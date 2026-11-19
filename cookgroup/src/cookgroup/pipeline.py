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


def evaluate(ev: Event, market: MarketProvider, platform_name: str, store: Store) -> Opportunity | None:
    if not ev.variants or ev.type == EventType.SOLD_OUT:
        return None
    v = min(ev.variants, key=lambda x: x.price_cents)
    if v.price_cents <= 0:
        return None  # sin precio no se calcula beneficio (p. ej. chollos RSS sin importe)
    md = market.lookup(v.sku, ev.product.title, v.title)
    pr = compute_profit(v.price_cents, md, DEFAULT_PLATFORMS[platform_name])
    urgency = 0.95 if ev.type == EventType.PRICE_ERROR else 0.9 if ev.type in (EventType.RESTOCK, EventType.NEW_PRODUCT) else 0.6
    score, parts = score_opportunity(pr, md, urgency=urgency)
    notes = list(pr.notes)
    hist = store.historical_min(ev.product.key)
    if ev.type in (EventType.PRICE_DROP, EventType.PRICE_ERROR) and hist and ev.new_price_cents and ev.new_price_cents <= hist:
        notes.append("Mínimo del histórico propio (solo desde que este sistema monitoriza)")
    return Opportunity(ev, v.price_cents, pr.resale_cents, pr.net_profit_cents, pr.roi_pct, score, parts, notes)


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


def run_cycle(cfg: MonitorConfig, defaults: dict, source, store: Store, market: MarketProvider,
              send: Callable[[dict], str | None], *, ping_rules: list[PingRule] | None = None,
              ping_senders: dict[str, Callable[[dict], str | None]] | None = None) -> dict:
    """Devuelve un resumen; nunca lanza por errores de la fuente (se registran)."""
    try:
        raw = source.fetch()
    except RateLimited as e:
        store.record_run(cfg.name, False, error=str(e))
        return {"ok": False, "backoff": e.retry_after, "error": str(e)}
    except SourceError as e:
        if str(e) == "not-modified":
            store.record_run(cfg.name, True)
            return {"ok": True, "products": 0, "events": 0, "sent": 0, "dropped": 0, "pings": 0}
        store.record_run(cfg.name, False, error=str(e))
        return {"ok": False, "error": str(e)}

    products, dropped = _prepare(raw, cfg)
    old = store.load_snapshot(cfg.store)
    events = diff_products(old, products, min_drop_pct=defaults.get("min_drop_pct", 10))
    events, pe_notes = _upgrade_price_errors(events, store, defaults)
    store.save_snapshot(cfg.store, products)

    sent = pings = 0
    cooldown = defaults.get("cooldown_seconds", 3600)
    for ev in events:
        if ev.type == EventType.SOLD_OUT:
            continue  # el estado de alertas previas se actualiza en una fase futura
        if store.seen_recently(ev.dedupe_key, cooldown):
            continue
        opp = evaluate(ev, market, defaults.get("platform", "stockx"), store)
        if opp is not None and pe_notes.get(ev.dedupe_key):
            opp.notes.extend(pe_notes[ev.dedupe_key])
        payload = build_embed(ev, opp)
        mid = send(payload)
        store.record_alert(ev.dedupe_key, ev.type.value, cfg.store, ev.product.key, mid)
        sent += 1
        for rule in ping_rules or []:
            sender = (ping_senders or {}).get(rule.channel)
            pkey = f"ping|{rule.name}|{ev.dedupe_key}"
            if sender and rule_matches(rule, ev) and not store.seen_recently(pkey, cooldown):
                pid = sender(build_ping(rule, ev, payload))
                store.record_alert(pkey, "ping", cfg.store, ev.product.key, pid)
                pings += 1
    store.record_run(cfg.name, True, len(products), len(events))
    return {"ok": True, "products": len(products), "events": len(events), "sent": sent,
            "dropped": dropped, "pings": pings}
