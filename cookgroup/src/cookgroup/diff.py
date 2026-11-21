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

        # v1.6: bajada de precio POR VARIANTE (talla/color) frente a su propio precio anterior. Antes se comparaba el
        # mínimo de todo el producto: si el color barato volvía a stock, el mínimo bajaba sin que nada se abaratara.
        prev_price = {v.variant_id: v.price_cents for v in prev.variants if v.price_cents}
        cheaper = tuple(v for v in p.variants if v.available and v.price_cents and v.variant_id in prev_price
                        and (prev_price[v.variant_id] - v.price_cents) * 100 / prev_price[v.variant_id] >= min_drop_pct)
        if cheaper:
            old_min = min(prev_price[v.variant_id] for v in cheaper)
            new_min = min(v.price_cents for v in cheaper)
            if new_min < old_min:
                events.append(Event(EventType.PRICE_DROP, p, cheaper,
                                    old_price_cents=old_min, new_price_cents=new_min, detected_at=ts))
    return events
