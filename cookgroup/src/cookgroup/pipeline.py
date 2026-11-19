"""Un ciclo de monitor: fetch -> filtro -> diff -> oportunidad -> dedupe -> alerta."""
from __future__ import annotations

import logging
from typing import Callable

from .config import MonitorConfig
from .diff import diff_products
from .discord import build_embed
from .filters import product_passes
from .market import MarketProvider
from .models import Event, EventType, Opportunity
from .profit import DEFAULT_PLATFORMS, compute_profit
from .scoring import score_opportunity
from .sources.shopify import RateLimited, SourceError
from .store import Store

log = logging.getLogger("cookgroup")


def evaluate(ev: Event, market: MarketProvider, platform_name: str, store: Store) -> Opportunity | None:
    if not ev.variants or ev.type == EventType.SOLD_OUT:
        return None
    # Usa la variante disponible más barata; la talla se usa para buscar dato de mercado.
    v = min(ev.variants, key=lambda x: x.price_cents)
    md = market.lookup(v.sku, ev.product.title, v.title)
    pr = compute_profit(v.price_cents, md, DEFAULT_PLATFORMS[platform_name])
    urgency = 0.9 if ev.type in (EventType.RESTOCK, EventType.NEW_PRODUCT) else 0.6
    score, parts = score_opportunity(pr, md, urgency=urgency)
    notes = list(pr.notes)
    hist = store.historical_min(ev.product.key)
    if ev.type == EventType.PRICE_DROP and hist and ev.new_price_cents and ev.new_price_cents <= hist:
        notes.append("Mínimo del histórico propio (solo desde que este sistema monitoriza)")
    return Opportunity(ev, v.price_cents, pr.resale_cents, pr.net_profit_cents, pr.roi_pct, score, parts, notes)


def run_cycle(cfg: MonitorConfig, defaults: dict, source, store: Store, market: MarketProvider,
              send: Callable[[dict], str | None]) -> dict:
    """Devuelve un resumen; nunca lanza por errores de la fuente (se registran)."""
    try:
        products = [p for p in source.fetch() if product_passes(p, cfg)]
    except RateLimited as e:
        store.record_run(cfg.name, False, error=str(e))
        return {"ok": False, "backoff": e.retry_after, "error": str(e)}
    except SourceError as e:
        if str(e) == "not-modified":
            store.record_run(cfg.name, True)
            return {"ok": True, "products": 0, "events": 0, "sent": 0}
        store.record_run(cfg.name, False, error=str(e))
        return {"ok": False, "error": str(e)}

    old = store.load_snapshot(cfg.store)
    events = diff_products(old, products, min_drop_pct=defaults.get("min_drop_pct", 10))
    store.save_snapshot(cfg.store, products)
    sent = 0
    for ev in events:
        if ev.type == EventType.SOLD_OUT:
            continue  # el estado de alertas previas se actualiza en una fase futura
        if store.seen_recently(ev.dedupe_key, defaults.get("cooldown_seconds", 3600)):
            continue
        opp = evaluate(ev, market, defaults.get("platform", "stockx"), store)
        mid = send(build_embed(ev, opp))
        store.record_alert(ev.dedupe_key, ev.type.value, cfg.store, ev.product.key, mid)
        sent += 1
    store.record_run(cfg.name, True, len(products), len(events))
    return {"ok": True, "products": len(products), "events": len(events), "sent": sent}
