"""Detección de eventos comparando snapshots. Distingue producto nuevo vs restock."""
from __future__ import annotations

from datetime import datetime, timezone

from .models import Event, EventType, Product


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def diff_products(old: dict[str, Product] | None, new: list[Product], *, min_drop_pct: float = 5.0) -> list[Event]:
    """Compara el snapshot previo con el actual.

    old=None => primera ejecución: se establece la línea base y NO se emiten eventos
    (evita inundar Discord con todo el catálogo como 'nuevo').
    """
    if old is None:
        return []
    ts = now_iso()
    events: list[Event] = []
    for p in new:
        prev = old.get(p.key)
        if prev is None:
            if p.available_variants:
                events.append(Event(EventType.NEW_PRODUCT, p, p.available_variants, detected_at=ts))
            continue
        prev_v = {v.variant_id: v for v in prev.variants if v.known}     # v1.6: lo «desconocido» no es referencia
        was_any_available = bool(prev.available_variants)

        back = tuple(v for v in p.variants if v.available and (v.variant_id in prev_v) and not prev_v[v.variant_id].available)
        known_before = {v.variant_id for v in prev.variants}
        added = tuple(v for v in p.variants if v.available and v.variant_id not in known_before)
        if back and not was_any_available:
            events.append(Event(EventType.RESTOCK, p, back, detected_at=ts))
        elif back or added:
            events.append(Event(EventType.NEW_SIZE, p, back + added, detected_at=ts))

        if was_any_available and not p.available_variants and all(v.known for v in p.variants):
            events.append(Event(EventType.SOLD_OUT, p, (), detected_at=ts))

        old_min, new_min = prev.min_price_cents, p.min_price_cents
        if old_min and new_min and new_min < old_min and p.available_variants:
            drop = (old_min - new_min) * 100 / old_min
            if drop >= min_drop_pct:
                events.append(Event(EventType.PRICE_DROP, p, p.available_variants,
                                    old_price_cents=old_min, new_price_cents=new_min, detected_at=ts))
    return events
