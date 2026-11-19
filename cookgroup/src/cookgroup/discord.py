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


_SYM = {"EUR": "€", "GBP": "£", "USD": "$", "SEK": "kr", "DKK": "kr", "CHF": "CHF"}


def eur(cents: int | None, currency: str = "EUR") -> str:
    if cents is None:
        return "N/D"
    n = f"{cents/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    sym = _SYM.get(currency.upper(), currency.upper())
    return f"£{n}" if sym == "£" else f"{sym}{n}" if sym == "$" else f"{n} {sym}"


def base_sku(skus: list[str]) -> str | None:
    """SKU de modelo: muchas tiendas añaden la talla ("HQ4307-001-42,5"). Prefijo común sin separador final."""
    if not skus:
        return None
    if len(skus) == 1:
        return skus[0]
    pre = skus[0]
    for s in skus[1:]:
        while not s.startswith(pre):
            pre = pre[:-1]
    seps = "-_ /."
    # si el prefijo corta a mitad de un segmento (p. ej. "…-4" de "…-40"/"…-41"), retrocede al último separador
    if any(len(s) > len(pre) and s[len(pre)] not in seps for s in skus) and pre and pre[-1] not in seps:
        cut = max(pre.rfind(c) for c in seps)
        pre = pre[:cut] if cut > 0 else pre
    pre = pre.rstrip(seps)
    return pre if len(pre) >= 5 else None


def build_embed(ev: Event, opp: Opportunity | None = None, market_note: str | None = None, *, buttons: bool = False,
                launch_collection: bool = False, region: str | None = None) -> dict:
    p = ev.product
    is_deal = bool(p.variants) and all(v.title == "Oferta" for v in p.variants) and ev.type == EventType.NEW_PRODUCT
    sizes = ", ".join(v.title for v in ev.variants if v.title != "Oferta")
    price = ev.new_price_cents or p.min_price_cents
    fields = [
        {"name": "Tienda", "value": p.store + (f" · {region.upper()}" if region else ""), "inline": True},
        {"name": "Precio", "value": eur(price, p.currency) if price else "No indicado", "inline": True},
    ]
    if ev.type in (EventType.PRICE_DROP, EventType.PRICE_ERROR):
        label = "Referencia (mediana propia)" if ev.type == EventType.PRICE_ERROR else "Antes"
        fields.append({"name": label, "value": eur(ev.old_price_cents, p.currency), "inline": True})
    else:
        cmp_at = max((v.compare_at_cents or 0 for v in ev.variants), default=0)
        if cmp_at and price and cmp_at > price:
            fields.append({"name": "Descuento tienda", "value": f"~~{eur(cmp_at, p.currency)}~~ (-{round((cmp_at-price)*100/cmp_at)} %)", "inline": True})
    skus = sorted({v.sku for v in ev.variants if v.sku})
    if (base := base_sku(skus)):
        fields.append({"name": "SKU", "value": f"`{base}`", "inline": True})
    if p.product_type and sizes == "":
        fields.append({"name": "Categoría", "value": p.product_type, "inline": True})
    temp = next((t[5:] for t in p.tags if t.startswith("temp:")), None)
    if temp:
        fields.append({"name": "Temperatura", "value": f"{temp}°", "inline": True})
    if sizes:
        fields.append({"name": "Tallas disponibles", "value": sizes[:1000], "inline": False})
    if launch_collection:
        fields.append({"name": "Fecha", "value": "La tienda no la publica en su catálogo: consúltala en el enlace", "inline": False})
    if opp is not None:
        fields.append({"name": "Precio de mercado", "value": eur(opp.resale_price_cents) + (f" ({market_note})" if market_note else ""), "inline": True})
        fields.append({"name": "Beneficio neto estimado", "value": eur(opp.net_profit_cents), "inline": True})
        fields.append({"name": "Score", "value": f"{opp.score}/100", "inline": True})
        if opp.notes:
            fields.append({"name": "⚠ Incertidumbre", "value": "\n".join(f"• {n}" for n in opp.notes)[:1000], "inline": False})
    q = quote_plus(base or p.title)
    links = f"[Ver chollo]({p.url})" if is_deal else (
        f"[Producto]({p.url}) | [StockX](https://stockx.com/search?s={q}) | [eBay](https://www.ebay.es/sch/i.html?_nkw={q})")
    fields.append({"name": "Enlaces", "value": links, "inline": False})
    embed = {
        "title": (f"📢 NUEVO EN LANZAMIENTOS — {p.store}" if launch_collection and ev.type == EventType.NEW_PRODUCT else
                  f"🟢 TALLAS DISPONIBLES (lanzamiento) — {p.store}" if launch_collection and ev.type in (EventType.RESTOCK, EventType.NEW_SIZE) else
                  f"NUEVO CHOLLO — {p.vendor} vía {p.store}" if is_deal and p.vendor else
                  f"NUEVO CHOLLO — {p.store}" if is_deal else f"{TITLES[ev.type]} — {p.vendor or p.store}"),
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
            try:
                r = self.session.post(self.url, params={"wait": "true"}, json=payload, timeout=15)
            except requests.RequestException as e:   # el mensaje de requests incluye la URL (con token): no se propaga
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Discord: error de conexión ({type(e).__name__})") from None
                time.sleep(2 ** attempt)
                continue
            if r.status_code == 429:
                time.sleep(float(r.json().get("retry_after", 1)) if r.content else 1)
                continue
            if r.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            if r.status_code >= 400:
                raise RuntimeError(f"Discord rechazó el mensaje: HTTP {r.status_code} {r.text[:200]}")
            return str(r.json().get("id"))
        raise RuntimeError("Discord: reintentos agotados")
