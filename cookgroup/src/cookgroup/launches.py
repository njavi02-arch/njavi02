"""Lanzamientos de tiendas: anuncio, fecha confirmada/cambiada, raffle abierto/enlace nuevo/cierre próximo,
salida a la venta, vuelta de tallas y bajada de precio — con estado persistente y sin duplicados tras reinicios.

Principios:
- Primer arranque: se guarda todo como línea base y se envía UN resumen (raffles abiertos + próximos 7 días).
- Un fallo de lectura (403/429/HTML raro/listado parcial) no produce eventos: ni cierres, ni restocks masivos.
- Un producto que desaparece del listado NO se anuncia como cancelado (la tienda no lo confirma).
- Cada alerta tiene una clave estable; una reposición real posterior (tras volver a agotarse) tiene clave nueva.
"""
from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Callable
from zoneinfo import ZoneInfo

from .discord import eur
from .sources.bstn import Launch, ProductPage, SizeStock
from .sources.shopify import RateLimited, SourceError

log = logging.getLogger("cookgroup")
MADRID = ZoneInfo("Europe/Madrid")
_DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
_MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
REGION_NAMES = {"eu": "Europa", "uk": "Reino Unido", "us": "EE. UU.", "ch": "Suiza", "dk": "Dinamarca", "se": "Suecia",
                "pl": "Polonia", "cz": "Chequia", "no": "Noruega", "ca": "Canadá"}


class LaunchEventType(str, Enum):
    ANNOUNCED = "announced"
    DATE_CONFIRMED = "date_confirmed"
    DATE_CHANGED = "date_changed"
    RAFFLE_OPEN = "raffle_open"
    RAFFLE_LINK_CHANGED = "raffle_link_changed"
    RAFFLE_CLOSING = "raffle_closing"
    LIVE = "live"
    SIZE_RESTOCK = "size_restock"
    LAUNCH_PRICE_DROP = "launch_price_drop"
    CANCELLED = "cancelled"   # solo si una fuente lo confirma explícitamente (BSTN no lo publica)


KIND = {  # a qué tipo de canal va cada evento
    LaunchEventType.ANNOUNCED: "launch", LaunchEventType.DATE_CONFIRMED: "launch", LaunchEventType.DATE_CHANGED: "launch",
    LaunchEventType.LIVE: "launch", LaunchEventType.CANCELLED: "launch",
    LaunchEventType.RAFFLE_OPEN: "raffle", LaunchEventType.RAFFLE_LINK_CHANGED: "raffle", LaunchEventType.RAFFLE_CLOSING: "raffle",
    LaunchEventType.SIZE_RESTOCK: "restock", LaunchEventType.LAUNCH_PRICE_DROP: "restock",
}


@dataclass
class LaunchEvent:
    type: LaunchEventType
    launch: Launch
    key: str                                   # clave de deduplicación estable
    sizes: list[SizeStock] = field(default_factory=list)
    old_ts: int | None = None
    old_price_cents: int | None = None
    new_price_cents: int | None = None
    delay_s: int | None = None                 # retraso medido frente a la hora publicada por la tienda
    simulated: bool = False


# ------------------------------------------------------------------ helpers
def launch_from_dict(d: dict) -> Launch:
    names = {f.name for f in fields(Launch)}
    return Launch(**{k: v for k, v in d.items() if k in names})


def madrid(ts: int | None, *, with_time: bool = True) -> str:
    if not ts:
        return "sin fecha"
    d = datetime.fromtimestamp(ts, MADRID)
    base = f"{_DIAS[d.weekday()]} {d.day} {_MESES[d.month - 1]}"
    return f"{base} · {d:%H:%M}" if with_time else base


def region_label(region: str) -> str:
    cc = region.split("_")[0].lower()
    return f"{REGION_NAMES.get(cc, cc.upper())} ({region})"


def _human_delta(seconds: float) -> str:
    m = int(seconds // 60)
    if m < 60:
        return f"{m} min"
    h, m = divmod(m, 60)
    return f"{h} h {m:02d} min" if h < 48 else f"{h // 24} días"


# ------------------------------------------------------------------ transiciones del listado
def diff_launches(prev: dict[str, dict], new: list[Launch], now: datetime, *,
                  min_drop_pct: float = 5.0) -> tuple[list[LaunchEvent], dict[str, dict]]:
    """prev: estados guardados (uid -> {"launch","state","present"}). Devuelve eventos y estados nuevos.

    Línea base (prev vacío): sin eventos. Listado sospechosamente corto: SourceError (no se toca nada).
    """
    present_before = [u for u, d in prev.items() if d.get("present")]
    if len(present_before) >= 5 and len(new) < 0.3 * len(present_before):
        raise SourceError(f"listado sospechoso: {len(new)} productos frente a {len(present_before)} antes; se ignora")
    states = {u: {"launch": d["launch"], "state": dict(d.get("state", {})), "present": False} for u, d in prev.items()}
    events: list[LaunchEvent] = []
    baseline = not prev
    for item in new:
        st = states.get(item.uid)
        old = launch_from_dict(st["launch"]) if st else None
        state = st["state"] if st else {"first_seen": now.isoformat(timespec="seconds")}
        states[item.uid] = {"launch": asdict(item), "state": state, "present": True}
        if baseline:
            continue
        u = item.uid
        if old is None:
            if item.raffle_active:
                events.append(LaunchEvent(LaunchEventType.RAFFLE_OPEN, item, f"raffle_open|{u}|{item.raffle_url}"))
            else:
                events.append(LaunchEvent(LaunchEventType.ANNOUNCED, item, f"announced|{u}"))
            continue
        if item.release_ts and not old.release_ts:
            events.append(LaunchEvent(LaunchEventType.DATE_CONFIRMED, item, f"date|{u}|{item.release_ts}"))
        elif item.release_ts and old.release_ts and item.release_ts != old.release_ts:
            events.append(LaunchEvent(LaunchEventType.DATE_CHANGED, item, f"date|{u}|{item.release_ts}", old_ts=old.release_ts))
        if item.raffle_active and not old.raffle_active:
            events.append(LaunchEvent(LaunchEventType.RAFFLE_OPEN, item, f"raffle_open|{u}|{item.raffle_url}"))
        elif item.raffle_active and old.raffle_active and item.raffle_url and item.raffle_url != old.raffle_url:
            events.append(LaunchEvent(LaunchEventType.RAFFLE_LINK_CHANGED, item, f"raffle_link|{u}|{item.raffle_url}"))
        if item.price_cents and old.price_cents and item.price_cents < old.price_cents * (1 - min_drop_pct / 100):
            events.append(LaunchEvent(LaunchEventType.LAUNCH_PRICE_DROP, item, f"price|{u}|{item.price_cents}",
                                      old_price_cents=old.price_cents, new_price_cents=item.price_cents))
    return events, states


def timed_events(states: dict[str, dict], now: datetime, *, closing_window_h: float = 3.0) -> list[LaunchEvent]:
    """Recordatorio de cierre de raffle: una vez, cuando faltan ≤ closing_window_h horas."""
    out = []
    t = now.timestamp()
    for u, d in states.items():
        if not d.get("present"):
            continue
        item = launch_from_dict(d["launch"])
        if item.raffle_active and not item.raffle_expired and item.raffle_ends_ts and 0 < item.raffle_ends_ts - t <= closing_window_h * 3600:
            out.append(LaunchEvent(LaunchEventType.RAFFLE_CLOSING, item, f"raffle_closing|{u}|{item.raffle_ends_ts}"))
    return out


def due_live_checks(states: dict[str, dict], now: datetime, *, window_h: float = 12.0) -> list[str]:
    """Fichas a comprobar porque su hora de salida ya ha llegado y aún no se ha confirmado que estén a la venta."""
    t = now.timestamp()
    out = []
    for u, d in states.items():
        item, st = launch_from_dict(d["launch"]), d["state"]
        if item.url and item.release_ts and item.release_ts <= t < item.release_ts + window_h * 3600 and not st.get("live_done"):
            out.append(u)
    return sorted(out, key=lambda u: states[u]["launch"].get("release_ts") or 0)


def due_watch_checks(states: dict[str, dict], now: datetime, *, days: int = 14, limit: int = 4) -> list[str]:
    """Fichas ya lanzadas (≤ `days`) para vigilar tallas y precio, las menos recientes primero."""
    t = now.timestamp()
    cand = []
    for u, d in states.items():
        item, st = launch_from_dict(d["launch"]), d["state"]
        if item.url and st.get("live_done") and item.release_ts and t - item.release_ts <= days * 86400:
            cand.append((st.get("last_product_check") or "", u))
    return [u for _, u in sorted(cand)[:limit]]


def apply_product(uid: str, d: dict, page: ProductPage, now: datetime, *, live_check: bool,
                  min_drop_pct: float = 5.0) -> list[LaunchEvent]:
    """Actualiza el estado de tallas con una ficha leída correctamente y devuelve eventos."""
    item, st = launch_from_dict(d["launch"]), d["state"]
    ts_now = now.isoformat(timespec="seconds")
    st["last_product_check"] = ts_now
    events: list[LaunchEvent] = []
    prev_sizes: dict[str, int] | None = st.get("sizes")
    cur = {s.eu: s.qty for s in page.sizes if s.qty > 0}
    soldout_since: dict[str, str] = st.setdefault("soldout_since", {})
    if live_check and not st.get("live_done"):
        if page.in_stock:
            delay = int(now.timestamp() - item.release_ts) if item.release_ts else None
            events.append(LaunchEvent(LaunchEventType.LIVE, item, f"live|{uid}|{item.release_ts}", sizes=page.in_stock, delay_s=delay))
            st["live_done"] = True
        # sin stock en la hora de salida: no se afirma nada (puede no haber abierto aún o haberse agotado)
    elif prev_sizes is not None:
        back = [s for s in page.in_stock if prev_sizes.get(s.eu, 0) <= 0]
        if back:
            tag = ",".join(sorted(soldout_since.get(s.eu, "0") for s in back))
            events.append(LaunchEvent(LaunchEventType.SIZE_RESTOCK, item,
                                      f"restock|{uid}|{','.join(s.eu for s in back)}|{tag}", sizes=back))
        old_p, new_p = st.get("final_cents"), page.final_cents
        if old_p and new_p and new_p < old_p * (1 - min_drop_pct / 100):
            events.append(LaunchEvent(LaunchEventType.LAUNCH_PRICE_DROP, item, f"price|{uid}|{new_p}",
                                      sizes=page.in_stock, old_price_cents=old_p, new_price_cents=new_p))
    for eu, q in (prev_sizes or {}).items():   # tallas que se agotan ahora: se fecha para distinguir reposiciones
        if q > 0 and eu not in cur:
            soldout_since[eu] = ts_now
    for eu in cur:
        soldout_since.pop(eu, None)
    if page.in_stock or prev_sizes is not None or st.get("live_done"):
        st["sizes"] = cur
    if page.final_cents:
        st["final_cents"] = page.final_cents
    return events


# ------------------------------------------------------------------ Discord
TITLES = {
    LaunchEventType.ANNOUNCED: ("📢", "Nuevo lanzamiento anunciado", 0x3498DB),
    LaunchEventType.DATE_CONFIRMED: ("📅", "Fecha confirmada", 0x3498DB),
    LaunchEventType.DATE_CHANGED: ("🔁", "Fecha cambiada", 0xF1C40F),
    LaunchEventType.RAFFLE_OPEN: ("🎟️", "Raffle abierto", 0x9B59B6),
    LaunchEventType.RAFFLE_LINK_CHANGED: ("🔗", "Nuevo enlace de raffle", 0x9B59B6),
    LaunchEventType.RAFFLE_CLOSING: ("⏳", "El raffle cierra pronto", 0xE67E22),
    LaunchEventType.LIVE: ("🟢", "A la venta ahora", 0x2ECC71),
    LaunchEventType.SIZE_RESTOCK: ("🔄", "Restock", 0x2ECC71),
    LaunchEventType.LAUNCH_PRICE_DROP: ("💸", "Bajada de precio", 0xE67E22),
    LaunchEventType.CANCELLED: ("⛔", "Lanzamiento cancelado", 0x95A5A6),
}


def _mode(item: Launch) -> str:
    if item.instore_only:
        return "Solo en tienda física (recogida/compra en tienda)"
    if item.app_only:
        return "Solo en la app de la tienda"
    if item.raffle:
        return "Online · requiere cuenta de la tienda"
    return "Online"


def _money(cents: int | None, currency: str) -> str:
    return eur(cents, currency) if cents else "N/D"


def build_launch_embed(ev: LaunchEvent, now: datetime) -> dict:
    it = ev.launch
    emoji, label, color = TITLES[ev.type]
    t = now.timestamp()
    if ev.type == LaunchEventType.SIZE_RESTOCK:
        label = f"Vuelve la {ev.sizes[0].label()}" if len(ev.sizes) == 1 else f"Vuelven {len(ev.sizes)} tallas"
    if ev.type == LaunchEventType.RAFFLE_CLOSING and it.raffle_ends_ts:
        label = f"El raffle cierra en {_human_delta(it.raffle_ends_ts - t)}"
    action = {
        LaunchEventType.ANNOUNCED: "Apúntalo y activa avisos; aún no se puede comprar.",
        LaunchEventType.DATE_CONFIRMED: "Ya hay fecha: prepara cuenta, talla y pago.",
        LaunchEventType.DATE_CHANGED: "Revisa la nueva fecha.",
        LaunchEventType.RAFFLE_OPEN: "Inscríbete antes del cierre.",
        LaunchEventType.RAFFLE_LINK_CHANGED: "Usa el enlace nuevo para inscribirte.",
        LaunchEventType.RAFFLE_CLOSING: "Última oportunidad para inscribirte.",
        LaunchEventType.LIVE: "Entra ya: tallas disponibles abajo.",
        LaunchEventType.SIZE_RESTOCK: "Compra ya si es tu talla.",
        LaunchEventType.LAUNCH_PRICE_DROP: "Precio rebajado.",
        LaunchEventType.CANCELLED: "La tienda lo ha cancelado.",
    }[ev.type]
    f = []
    f.append({"name": "Tienda", "value": f"{it.store} · {region_label(it.region)}", "inline": True})
    if ev.type == LaunchEventType.LAUNCH_PRICE_DROP:
        f.append({"name": "Precio", "value": f"~~{_money(ev.old_price_cents, it.currency)}~~ → **{_money(ev.new_price_cents, it.currency)}**", "inline": True})
    else:
        f.append({"name": "Precio", "value": _money(it.price_cents, it.currency), "inline": True})
    f.append({"name": "SKU", "value": f"`{it.key}`", "inline": True})
    if it.raffle_active or ev.type in (LaunchEventType.RAFFLE_OPEN, LaunchEventType.RAFFLE_CLOSING, LaunchEventType.RAFFLE_LINK_CHANGED):
        val = f"**{madrid(it.raffle_ends_ts)}** (hora de Madrid)" if it.raffle_ends_ts else "No publicado"
        if it.raffle_ends_text:
            val += f"\nOrigen: {it.raffle_ends_text}"
        if it.raffle_ends_ts and it.raffle_ends_ts > t:
            val += f" · faltan {_human_delta(it.raffle_ends_ts - t)}"
        f.append({"name": "⏳ Cierre del raffle", "value": val, "inline": False})
    if it.release_ts:
        val = f"**{madrid(it.release_ts)}** (hora de Madrid)"
        if it.release_text:
            val += f"\nOrigen: {it.release_text}"
        if ev.type == LaunchEventType.DATE_CHANGED and ev.old_ts:
            val = f"~~{madrid(ev.old_ts)}~~ → " + val
        f.append({"name": "Lanzamiento", "value": val, "inline": False})
    elif ev.type not in (LaunchEventType.SIZE_RESTOCK, LaunchEventType.LIVE):
        f.append({"name": "Lanzamiento", "value": "Fecha aún no publicada por la tienda", "inline": False})
    f.append({"name": "Modalidad", "value": _mode(it), "inline": True})
    if ev.sizes:
        f.append({"name": "Tallas disponibles" if ev.type == LaunchEventType.LIVE else "Tallas",
                  "value": ", ".join(f"{s.label()} · {s.qty}{'+' if s.qty >= 10 else ''} uds" for s in ev.sizes)[:1000], "inline": False})
    link = it.raffle_url if ev.type in (LaunchEventType.RAFFLE_OPEN, LaunchEventType.RAFFLE_CLOSING, LaunchEventType.RAFFLE_LINK_CHANGED) else (it.url or it.raffle_url)
    if link:
        f.append({"name": "Enlace directo", "value": f"[{'Inscribirse en el raffle' if link == it.raffle_url and it.raffle_active else 'Abrir en ' + it.store}]({link})", "inline": False})
    foot = f"{'SIMULADO · ' if ev.simulated else ''}Fuente: calendario público de {it.store}"
    if ev.delay_s is not None:
        foot += f" · detectado {_human_delta(max(ev.delay_s, 0))} tras la hora publicada"
    embed = {"title": f"{emoji} {label} — {it.store}", "description": f"**{it.brand} {it.name}**\n{action}",
             "color": color, "fields": f, "footer": {"text": foot},
             "timestamp": now.astimezone(timezone.utc).isoformat(timespec="seconds")}
    if link:
        embed["url"] = link
    if it.image_url:
        embed["thumbnail"] = {"url": it.image_url}
    return {"embeds": [embed], "allowed_mentions": {"parse": []}}


def build_launch_digest(states: dict[str, dict], now: datetime, *, title: str, days: int = 7) -> dict | None:
    t = now.timestamp()
    items = [launch_from_dict(d["launch"]) for d in states.values() if d.get("present")]
    raffles = sorted((i for i in items if i.raffle_active and not i.raffle_expired and (not i.raffle_ends_ts or i.raffle_ends_ts > t)),
                     key=lambda i: i.raffle_ends_ts or 1e12)
    soon = sorted((i for i in items if i.release_ts and t <= i.release_ts <= t + days * 86400 and not i.raffle_active),
                  key=lambda i: i.release_ts)
    if not raffles and not soon:
        return None
    lines = ["**🎟️ Raffles abiertos ahora**"] if raffles else []
    for i in raffles:
        end = f"cierra {madrid(i.raffle_ends_ts)}" if i.raffle_ends_ts else "cierre no publicado"
        lines.append(f"• {i.brand} {i.name} — {end} · {_money(i.price_cents, i.currency)} · [inscribirse]({i.raffle_url})")
    if soon:
        lines += ["", f"**📅 Próximos {days} días** (hora de Madrid)"]
        for i in soon:
            mode = " · solo tienda" if i.instore_only else " · solo app" if i.app_only else ""
            link = f" · [ver]({i.url})" if i.url else ""
            lines.append(f"• {madrid(i.release_ts)} — {i.brand} {i.name} · {_money(i.price_cents, i.currency)}{mode}{link}")
    return {"embeds": [{"title": title, "description": "\n".join(lines)[:4000], "color": 0x5865F2,
                        "footer": {"text": "Solo fuentes verificadas · hora de Madrid"},
                        "timestamp": now.astimezone(timezone.utc).isoformat(timespec="seconds")}],
            "allowed_mentions": {"parse": []}}


# ------------------------------------------------------------------ ciclo
def run_launch_cycle(cfg, defaults: dict, source, store, senders: dict[str, Callable[[dict], str | None]],
                     now: datetime | None = None, *, ping_rules=None, forum=None, raffle_board=None) -> dict:
    """senders: {"launch"|"raffle"|"restock"|"digest"|<canal de ping>: send}. Nunca lanza por errores de la fuente."""
    from .rules import build_ping, rule_matches_launch  # evitar import circular
    now = now or datetime.now(timezone.utc)
    t0 = time.monotonic()
    src_name = f"{cfg.name}"
    try:
        items = source.fetch_launches(now)
        prev = store.load_launch_states(cfg.store)
        events, states = diff_launches(prev, items, now, min_drop_pct=defaults.get("min_drop_pct", 5))
    except RateLimited as e:
        store.record_health(src_name, False, error=str(e))
        return {"ok": False, "backoff": e.retry_after, "error": str(e)}
    except SourceError as e:
        store.record_health(src_name, False, error=str(e))
        return {"ok": False, "error": str(e)}
    first_run = not prev
    events += timed_events(states, now, closing_window_h=defaults.get("raffle_closing_hours", 3))

    product_errors, delays = 0, []
    if not first_run:
        checks = [(u, True) for u in due_live_checks(states, now)[:3]]
        checks += [(u, False) for u in due_watch_checks(states, now, limit=getattr(cfg, "product_checks_per_cycle", 4))
                   if u not in {c for c, _ in checks}]
        for u, live in checks:
            url = states[u]["launch"].get("url")
            try:
                page = source.fetch_product(url)
            except RateLimited as e:
                product_errors += 1
                log.warning("monitor=%s ficha %s: %s", cfg.name, url, e)
                break
            except SourceError as e:   # una ficha que falla no genera eventos
                product_errors += 1
                log.warning("monitor=%s ficha %s: %s", cfg.name, url, e)
                states[u]["state"]["last_product_check"] = now.isoformat(timespec="seconds")
                continue
            new_ev = apply_product(u, states[u], page, now, live_check=live)
            delays += [e.delay_s for e in new_ev if e.delay_s is not None]
            events += new_ev

    sent = pings = 0
    # v1.0: foro (un hilo por SKU, cambios dentro del hilo) y tablón de raffles (apertura/recordatorio/plazo/cierre)
    now_ts = int(now.timestamp())
    if forum is not None:
        for it in items:
            sent += len(forum.ingest(it))
    if raffle_board is not None:
        from .raffles import from_bstn
        for it in items:
            if it.raffle:
                sent += len(raffle_board.ingest(from_bstn(it, now_ts), now_ts))
        sent += len(raffle_board.tick(now_ts))
    if first_run:
        dg = build_launch_digest(states, now, title=f"Resumen inicial — {cfg.store}: raffles abiertos y próximos lanzamientos")
        send = senders.get("digest") or senders.get("launch")
        if dg and send and not store.has_alert(f"digest-first|{cfg.store}"):
            store.record_alert(f"digest-first|{cfg.store}", "launch_digest", cfg.store, "-", send(dg))
            sent += 1
    for ev in events:
        if store.has_alert(ev.key):
            continue
        kind = KIND[ev.type]
        payload = build_launch_embed(ev, now)
        if raffle_board is not None and kind == "raffle":
            store.record_alert(ev.key, ev.type.value, cfg.store, ev.launch.uid, None)   # lo publica el tablón de raffles
            continue
        if forum is not None and kind == "launch":
            if forum.post_update(ev.launch.key, payload):                             # dentro del hilo de ese SKU
                store.record_alert(ev.key, ev.type.value, cfg.store, ev.launch.uid, "hilo")
                sent += 1
            continue
        send = senders.get(kind) or (None if forum is not None else senders.get("launch"))
        if not send:
            continue
        store.record_alert(ev.key, ev.type.value, cfg.store, ev.launch.uid, send(payload))
        sent += 1
        for rule in ping_rules or []:
            snd = senders.get(rule.channel)
            pkey = f"ping|{rule.name}|{ev.key}"
            if snd and rule_matches_launch(rule, ev) and not store.has_alert(pkey):
                store.record_alert(pkey, "ping", cfg.store, ev.launch.uid, snd(build_ping(rule, None, payload, title=f"{ev.launch.brand} {ev.launch.name}")))
                pings += 1
    store.save_launch_states(cfg.store, states)
    store.record_health(src_name, True, items=len(items), duration_ms=int((time.monotonic() - t0) * 1000),
                        delay_s=max(delays) if delays else None)
    return {"ok": True, "items": len(items), "events": len(events), "sent": sent, "pings": pings,
            "first_run": first_run, "product_errors": product_errors}
