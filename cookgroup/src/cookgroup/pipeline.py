"""Un ciclo de monitor: fetch -> normalizar/validar -> filtro -> diff -> price error -> oportunidad
-> dedupe -> alerta -> pings por regla."""
from __future__ import annotations

import logging
from dataclasses import replace
from typing import Callable

from .config import MonitorConfig
from .diff import diff_products
from .discord import build_embed
from .filters import product_passes
from .market import MarketProvider
from .models import Event, EventType, Opportunity
from .normalize import clean_variants, validate_product
from .price_error import check_price_error
from .profit import DEFAULT_PLATFORMS, compute_profit
from .rules import PingRule, build_ping, rule_matches
from .scoring import score_opportunity
from .sources.shopify import RateLimited, SourceError
from .store import Store

log = logging.getLogger("cookgroup")


def evaluate(ev: Event, market: MarketProvider, platform_name: str, store: Store, cfg=None) -> Opportunity | None:
    """Calcula el beneficio TALLA A TALLA sobre las tallas disponibles del aviso: solo se verifica con ventas de esa
    misma talla. Se elige la talla comprable con mayor beneficio verificado; si ninguna se verifica, se usa la más
    barata y el aviso dice «beneficio sin verificar» con el motivo."""
    if not ev.variants or ev.type == EventType.SOLD_OUT:
        return None
    cands = [v for v in ev.variants if v.available and v.price_cents > 0] or [v for v in ev.variants if v.price_cents > 0]
    if not cands:
        return None  # sin precio no se calcula beneficio (p. ej. chollos RSS sin importe)
    best = None
    for v in sorted(cands, key=lambda x: x.price_cents):
        md = market.lookup(v.sku, ev.product.title, v.title)
        pr = compute_profit(v.price_cents, md, DEFAULT_PLATFORMS[platform_name], size=v.title,
                            buy_currency=ev.product.currency, ships_es=getattr(cfg, "ships_es", None), require_verified=True)
        key = (pr.verified, pr.net_profit_cents or 0)
        if best is None or key > best[0]:
            best = (key, v, md, pr)
    _, v, md, pr = best
    urgency = 0.95 if ev.type == EventType.PRICE_ERROR else 0.9 if ev.type in (EventType.RESTOCK, EventType.NEW_PRODUCT) else 0.6
    score, parts = score_opportunity(pr, md, urgency=urgency)
    notes = list(pr.notes)
    hist = store.historical_min(ev.product.key)
    if ev.type in (EventType.PRICE_DROP, EventType.PRICE_ERROR) and hist and ev.new_price_cents and ev.new_price_cents <= hist:
        notes.append("Mínimo del histórico propio (solo desde que este sistema monitoriza)")
    return Opportunity(ev, v.price_cents, pr.resale_cents, pr.net_profit_cents, pr.roi_pct, score, parts, notes,
                       margin_pct=pr.margin_pct, verified=pr.verified, basis=pr.basis, buy_size=v.title if v.available else None)


def _prepare(products, cfg: MonitorConfig):
    """Normaliza tallas y descarta lo no publicable. Devuelve (válidos, descartados)."""
    ok, dropped = [], 0
    for p in products:
        p = clean_variants(p, skip_kids=cfg.skip_kids_sizes, require_size=(cfg.type == "shopify"))
        issues = validate_product(p, allow_unknown_price=cfg.allow_unknown_price)
        if issues:
            dropped += 1
            log.debug("monitor=%s descartado %s: %s", cfg.name, p.key, ", ".join(issues))
            continue
        if product_passes(p, cfg):
            ok.append(p)
    return ok, dropped


def _upgrade_price_errors(events: list[Event], store: Store, defaults: dict) -> tuple[list[Event], dict[str, list[str]]]:
    """Convierte PRICE_DROP en PRICE_ERROR si el histórico propio lo respalda. Debe llamarse ANTES de
    guardar el snapshot nuevo (para que el precio actual no contamine la referencia)."""
    out, notes = [], {}
    for ev in events:
        if ev.type != EventType.PRICE_DROP or not ev.new_price_cents:
            out.append(ev)
            continue
        cmp_at = max((v.compare_at_cents or 0 for v in ev.variants), default=0) or None
        chk = check_price_error(ev.new_price_cents, store.price_samples(ev.product.key),
                                compare_at_cents=cmp_at,
                                threshold_pct=defaults.get("price_error_pct", 50),
                                min_observations=defaults.get("price_error_min_obs", 5))
        if chk.is_error:
            ev = replace(ev, type=EventType.PRICE_ERROR, old_price_cents=chk.reference_cents)
        if chk.notes:
            notes[ev.dedupe_key] = chk.notes
        out.append(ev)
    return out, notes


def watch_handles(snapshot: dict, cfg, defaults: dict, limit: int = 40) -> list[str]:
    """Modelos a vigilar ficha a ficha: los que encajan con `watch_keywords` (monitor o defaults) y con las
    palabras de las reglas de ping. Prioriza los agotados (son los que pueden volver)."""
    kws = [k.lower() for k in (cfg.watch_keywords or defaults.get("watch_keywords", [])) if k.strip()]
    if not kws:
        return []
    cand = []
    for p in snapshot.values():
        t = f"{p.title} {p.vendor or ''}".lower()
        if any(k in t for k in kws) and "/products/" in p.url:
            cand.append((bool(p.available_variants), p.url.rsplit("/products/", 1)[1]))
    return [h for _, h in sorted(cand)][:limit]


def discount_pct(ev: Event) -> float | None:
    """% de descuento del evento: bajada observada, o precio tachado de la tienda si es creíble (≤5×)."""
    if ev.type in (EventType.PRICE_DROP, EventType.PRICE_ERROR) and ev.old_price_cents and ev.new_price_cents:
        return (ev.old_price_cents - ev.new_price_cents) * 100 / ev.old_price_cents
    best = None
    for v in ev.variants:
        if v.compare_at_cents and 0 < v.price_cents < v.compare_at_cents <= v.price_cents * 5:
            pct = (v.compare_at_cents - v.price_cents) * 100 / v.compare_at_cents
            best = pct if best is None else max(best, pct)
    return best


def pick_discount_route(pct: float | None, routes: list[dict]) -> str | None:
    """Ruta del tramo más alto alcanzado (p. ej. 60 % antes que 30 %), como los canales por tramo observados."""
    if pct is None:
        return None
    ok = [r for r in routes if pct >= float(r["min_pct"])]
    return max(ok, key=lambda r: float(r["min_pct"]))["channel"] if ok else None


def _alert_key(ev: Event, group: str | None) -> str:
    if not group:
        return ev.dedupe_key
    return ev.dedupe_key.replace(ev.product.key, f"group={group}:{ev.product.product_id}", 1)


def deliver_outbox(store: Store, senders: dict[str, Callable[[dict], str | None]], *, store_name: str | None = None) -> dict:
    """Envía lo pendiente en orden. Al primer fallo de Discord se para (se reintenta en el siguiente ciclo)."""
    import json as _json
    by_type: dict[str, int] = {}
    err = None
    for key, etype, _st, _pk, channel, payload, _att in store.outbox_pending(store_name):
        snd = senders.get(channel)
        if not snd:
            continue
        try:
            mid = snd(_json.loads(payload))
        except Exception as e:   # Discord caído, 429 persistente, red…
            err = f"{type(e).__name__}: {e}"[:200]
            store.outbox_fail(key, err)
            log.warning("entrega pendiente (%s): %s", key[:60], err)
            break
        store.outbox_done(key, mid)
        k = "route" if etype == "route" else "ping" if etype == "ping" else "tienda" if etype == "tienda" else "main"
        by_type[k] = by_type.get(k, 0) + 1
    return {"by_type": by_type, "error": err, "pending": len(store.outbox_pending(store_name, limit=1000))}


def run_cycle(cfg: MonitorConfig, defaults: dict, source, store: Store, market: MarketProvider,
              send: Callable[[dict], str | None], *, ping_rules: list[PingRule] | None = None,
              ping_senders: dict[str, Callable[[dict], str | None]] | None = None,
              channel_senders: dict[str, Callable[[dict], str | None]] | None = None,
              profiles: list | None = None, forum=None, extra_channels: tuple = (), dedicated=None) -> dict:
    """Devuelve un resumen; nunca lanza por errores de la fuente (se registran)."""
    senders = {**(channel_senders or {}), **(ping_senders or {}), cfg.channel: send}
    try:
        raw = source.fetch()
    except RateLimited as e:
        store.record_run(cfg.name, False, error=str(e))
        store.record_health(cfg.name, False, error=str(e))
        d = deliver_outbox(store, senders, store_name=cfg.store)   # lo pendiente no depende de la fuente
        return {"ok": False, "backoff": e.retry_after, "error": str(e), "sent": d["by_type"].get("main", 0), "pending": d["pending"]}
    except SourceError as e:
        d = deliver_outbox(store, senders, store_name=cfg.store)
        if str(e) == "not-modified":
            store.record_run(cfg.name, True)
            store.record_health(cfg.name, True, items=0)
            return {"ok": True, "products": 0, "events": 0, "sent": d["by_type"].get("main", 0), "dropped": 0, "pings": 0,
                    "routed": 0, "pending": d["pending"], "not_modified": True}
        store.record_run(cfg.name, False, error=str(e))
        store.record_health(cfg.name, False, error=str(e))
        return {"ok": False, "error": str(e), "sent": d["by_type"].get("main", 0), "pending": d["pending"]}

    products, dropped = _prepare(raw, cfg)
    old = store.load_snapshot(cfg.store)
    events = diff_products(old, products, min_drop_pct=defaults.get("min_drop_pct", 10))
    events, pe_notes = _upgrade_price_errors(events, store, defaults)
    routes = defaults.get("discount_routes", [])
    queued = 0
    cooldown = defaults.get("cooldown_seconds", 3600)
    # 1) ENCOLAR (persistente) todo lo detectado, ANTES de tocar la instantánea
    for ev in events:
        if ev.type == EventType.SOLD_OUT:
            continue  # el estado de alertas previas se actualiza en una fase futura
        akey = _alert_key(ev, cfg.dedupe_group)
        if store.seen_recently(akey, cooldown):
            continue
        opp = evaluate(ev, market, defaults.get("platform", "stockx"), store, cfg)
        if opp is not None and pe_notes.get(ev.dedupe_key):
            opp.notes.extend(pe_notes[ev.dedupe_key])
        if forum is not None and cfg.collection and ev.type == EventType.NEW_PRODUCT:
            from .forum import launch_from_product
            forum.ingest(launch_from_product(ev.product, cfg.region or "eu"))   # nuevo lanzamiento → su hilo del foro
            store.record_alert(akey, ev.type.value, cfg.store, ev.product.key, "hilo")
            continue
        payload = build_embed(ev, opp, launch_collection=bool(cfg.collection), region=cfg.region, country=cfg.country)
        main_payload = payload
        from .members import FAMILY_BY_CHANNEL, personalize
        fam = FAMILY_BY_CHANNEL.get(cfg.channel, "Sneakers")
        # canal dedicado de la tienda (si existe): misma señal, la mención se hace aquí y no se repite en el agregado
        extras = list(extra_channels)
        if dedicated is not None:
            extras += dedicated.channels_for(cfg.name, cfg.country, f"{ev.product.vendor or ''} {ev.product.title}")
        from .dedicated import SIGNAL_OF, labelled
        sig = SIGNAL_OF.get(ev.type.value, "")
        for ch in dict.fromkeys(extras):
            if dedicated is not None and not dedicated.allows(ch, sig):
                continue                                   # señal aún sin probar en esta tienda: no se publica
            if ch in senders:
                pl = labelled(payload, sig) if ch.startswith("tienda_") and sig else payload
                if profiles:
                    pl, _ = personalize(pl, ev, profiles, store, channel=ch, family=fam, ships_es=cfg.ships_es,
                                        size_stock=cfg.type != "jsonld")
                store.outbox_add(f"tienda|{ch}|{akey}", "tienda", cfg.store, ev.product.key, ch, pl)
        if profiles:
            main_payload, _ = personalize(payload, ev, profiles, store, channel=cfg.channel, family=fam,
                                          ships_es=cfg.ships_es, size_stock=cfg.type != "jsonld")
        queued += store.outbox_add(akey, ev.type.value, cfg.store, ev.product.key, cfg.channel, main_payload)
        if (ch := pick_discount_route(discount_pct(ev), routes)) and ch != cfg.channel and ch in senders:
            route_payload = payload
            if profiles:
                route_payload, _ = personalize(payload, ev, profiles, store, channel=ch, family="Rebajas",
                                               ships_es=cfg.ships_es, size_stock=cfg.type != "jsonld")
            store.outbox_add(f"route|{ch}|{akey}", "route", cfg.store, ev.product.key, ch, route_payload)
        for rule in ping_rules or []:
            if rule.channel in senders and rule_matches(rule, ev):
                store.outbox_add(f"ping|{rule.name}|{akey}", "ping", cfg.store, ev.product.key, rule.channel,
                                 build_ping(rule, ev, payload))
    # 2) solo ahora se guarda la instantánea (los avisos ya están a salvo en la bandeja)
    store.save_snapshot(cfg.store, products)
    if hasattr(source, "watch") and cfg.type == "shopify":
        source.watch = watch_handles({**(old or {}), **{p.key: p for p in products}}, cfg, defaults)
    # 3) ENTREGAR lo pendiente de esta tienda (incluidos fallos de ciclos anteriores)
    d = deliver_outbox(store, senders, store_name=cfg.store)
    sent, routed, pings = d["by_type"].get("main", 0), d["by_type"].get("route", 0), d["by_type"].get("ping", 0)
    store.record_run(cfg.name, True, len(products), len(events))
    store.record_health(cfg.name, True, items=len(raw))
    return {"ok": True, "products": len(products), "events": len(events), "sent": sent,
            "dropped": dropped, "pings": pings, "routed": routed, "queued": queued, "pending": d["pending"],
            "delivery_error": d["error"]}
