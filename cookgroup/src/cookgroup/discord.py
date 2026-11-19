"""Embeds Discord y envío por webhook con control de 429."""
from __future__ import annotations

import time
from urllib.parse import quote_plus

import requests

from .models import Event, EventType, Opportunity

COLORS = {EventType.RESTOCK: 0x2ECC71, EventType.NEW_PRODUCT: 0x3498DB, EventType.NEW_SIZE: 0xF1C40F,
          EventType.PRICE_DROP: 0xE67E22, EventType.SOLD_OUT: 0x95A5A6, EventType.PRICE_ERROR: 0xE74C3C}
TITLES = {EventType.RESTOCK: "RESTOCK DETECTADO", EventType.NEW_PRODUCT: "NUEVO PRODUCTO",
          EventType.NEW_SIZE: "NUEVAS TALLAS", EventType.PRICE_DROP: "BAJADA DE PRECIO",
          EventType.SOLD_OUT: "AGOTADO", EventType.PRICE_ERROR: "POSIBLE PRICE ERROR"}


def eur(cents: int | None) -> str:
    return "N/D" if cents is None else f"{cents/100:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def build_embed(ev: Event, opp: Opportunity | None = None, market_note: str | None = None, *, buttons: bool = False) -> dict:
    p = ev.product
    sizes = ", ".join(v.title for v in ev.variants if v.title != "Oferta")
    price = ev.new_price_cents or p.min_price_cents
    fields = [
        {"name": "Tienda", "value": p.store, "inline": True},
        {"name": "Precio", "value": eur(price) if price else "No indicado", "inline": True},
    ]
    if ev.type in (EventType.PRICE_DROP, EventType.PRICE_ERROR):
        label = "Referencia (mediana propia)" if ev.type == EventType.PRICE_ERROR else "Antes"
        fields.append({"name": label, "value": eur(ev.old_price_cents), "inline": True})
    else:
        cmp_at = max((v.compare_at_cents or 0 for v in ev.variants), default=0)
        if cmp_at and price and cmp_at > price:
            fields.append({"name": "Descuento tienda", "value": f"~~{eur(cmp_at)}~~ (-{round((cmp_at-price)*100/cmp_at)} %)", "inline": True})
    skus = sorted({v.sku for v in ev.variants if v.sku})
    if skus:
        fields.append({"name": "SKU", "value": f"`{skus[0]}`" + (f" (+{len(skus)-1})" if len(skus) > 1 else ""), "inline": True})
    if sizes:
        fields.append({"name": "Tallas disponibles", "value": sizes[:1000], "inline": False})
    if opp is not None:
        fields.append({"name": "Precio de mercado", "value": eur(opp.resale_price_cents) + (f" ({market_note})" if market_note else ""), "inline": True})
        fields.append({"name": "Beneficio neto estimado", "value": eur(opp.net_profit_cents), "inline": True})
        fields.append({"name": "Score", "value": f"{opp.score}/100", "inline": True})
        if opp.notes:
            fields.append({"name": "⚠ Incertidumbre", "value": "\n".join(f"• {n}" for n in opp.notes)[:1000], "inline": False})
    q = quote_plus(skus[0] if skus else p.title)
    fields.append({"name": "Enlaces", "value": f"[Producto]({p.url}) | [StockX](https://stockx.com/search?s={q}) | "
                   f"[eBay](https://www.ebay.es/sch/i.html?_nkw={q})", "inline": False})
    embed = {
        "title": f"{TITLES[ev.type]} — {p.vendor or p.store}",
        "description": f"**[{p.title}]({p.url})**",
        "url": p.url, "color": COLORS[ev.type], "fields": fields,
        "timestamp": ev.detected_at,
        "footer": {"text": "Datos de la tienda; estimaciones no garantizadas"},
    }
    if p.image_url:
        embed["thumbnail"] = {"url": p.image_url}
    payload = {"embeds": [embed]}
    if buttons:  # solo válido con bot propio / webhook de aplicación; un webhook normal lo rechaza
        payload["components"] = [{"type": 1, "components": [{"type": 2, "style": 5, "label": "COMPRAR", "url": p.url}]}]
    return payload


class WebhookSender:
    def __init__(self, url: str, session: requests.Session | None = None, max_retries: int = 3):
        self.url, self.session, self.max_retries = url, session or requests.Session(), max_retries

    def send(self, payload: dict) -> str | None:
        for attempt in range(self.max_retries):
            r = self.session.post(self.url, params={"wait": "true"}, json=payload, timeout=15)
            if r.status_code == 429:
                time.sleep(float(r.json().get("retry_after", 1)) if r.content else 1)
                continue
            if r.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return str(r.json().get("id"))
        raise RuntimeError("Discord: reintentos agotados")
