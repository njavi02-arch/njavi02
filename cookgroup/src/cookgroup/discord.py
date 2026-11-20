"""Embeds Discord y envío por webhook con control de 429."""
from __future__ import annotations

import time
from dataclasses import replace
from urllib.parse import quote_plus

import requests

from .models import Event, EventType, Opportunity
from .normalize import normalize_size

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


FLAGS = {"ES": "🇪🇸", "FR": "🇫🇷", "DE": "🇩🇪", "IT": "🇮🇹", "GB": "🇬🇧", "UK": "🇬🇧", "NL": "🇳🇱", "BE": "🇧🇪", "PT": "🇵🇹",
         "DK": "🇩🇰", "SE": "🇸🇪", "PL": "🇵🇱", "CZ": "🇨🇿", "AT": "🇦🇹", "CH": "🇨🇭", "US": "🇺🇸", "CA": "🇨🇦", "AU": "🇦🇺",
         "JP": "🇯🇵", "KR": "🇰🇷", "CN": "🇨🇳", "HK": "🇭🇰", "SG": "🇸🇬", "TH": "🇹🇭", "AE": "🇦🇪", "ZA": "🇿🇦", "MX": "🇲🇽",
         "BR": "🇧🇷", "AR": "🇦🇷", "CL": "🇨🇱", "CO": "🇨🇴", "IE": "🇮🇪", "FI": "🇫🇮", "NO": "🇳🇴", "GR": "🇬🇷", "HU": "🇭🇺"}


def size_label(s: str) -> str:
    """Talla legible con su sistema: "43" -> "EU 43", "US 9" se queda, "9" (sin sistema) -> "talla 9"."""
    s = str(s).strip()
    if s[:2].upper() in ("US", "UK", "EU", "JP", "CM") or s.startswith("M") and "/W" in s:
        return s
    try:
        n = float(s.split()[0])
        return f"EU {s}" if 15 <= n <= 52 else f"talla {s}"
    except ValueError:
        return s


def madrid_text(iso_ts: str | None) -> str:
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo
    try:
        d = datetime.fromisoformat(iso_ts) if iso_ts else datetime.now(timezone.utc)
    except ValueError:
        d = datetime.now(timezone.utc)
    d = d.astimezone(ZoneInfo("Europe/Madrid"))
    dias = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    return f"{dias[d.weekday()]} {d.day} {meses[d.month - 1]} · {d:%H:%M} (hora de Madrid)"


def build_embed(ev: Event, opp: Opportunity | None = None, market_note: str | None = None, *, buttons: bool = False,
                launch_collection: bool = False, region: str | None = None, country: str | None = None) -> dict:
    p = ev.product
    is_deal = bool(p.variants) and all(v.title == "Oferta" for v in p.variants) and ev.type == EventType.NEW_PRODUCT
    sizes = ", ".join(v.title for v in ev.variants if v.title != "Oferta")
    price = ev.new_price_cents or p.min_price_cents
    fields = [
        {"name": "Tienda", "value": p.store + (f" · {FLAGS.get(country.upper(), '')} {country.upper()}".rstrip() if country else "")
                                   + (f" · región {region.upper()}" if region and (not country or region.upper() != country.upper()) else ""), "inline": True},
        {"name": "Precio", "value": eur(price, p.currency) if price else "No indicado", "inline": True},
    ]
    if ev.type in (EventType.PRICE_DROP, EventType.PRICE_ERROR):
        # v0.9: precio anterior y actual, cada uno con su origen
        if ev.type == EventType.PRICE_ERROR:
            fields.append({"name": "Referencia", "value": f"{eur(ev.old_price_cents, p.currency)}\n*origen: mediana de los precios que "
                                                          f"hemos leído en esta tienda*", "inline": True})
        else:
            fields.append({"name": "Antes", "value": f"{eur(ev.old_price_cents, p.currency)}\n*origen: nuestra lectura anterior de la "
                                                     f"ficha de la tienda*", "inline": True})
        fields[1] = {"name": "Ahora", "value": f"{eur(price, p.currency)}\n*origen: ficha de la tienda al detectar*", "inline": True}
    else:
        cmp_at = max((v.compare_at_cents or 0 for v in ev.variants), default=0)
        if cmp_at and price and cmp_at > price:
            fields.append({"name": "Descuento tienda", "value": f"~~{eur(cmp_at, p.currency)}~~ (-{round((cmp_at-price)*100/cmp_at)} %)"
                                                                f"\n*origen: precio tachado que publica la tienda*", "inline": True})
    skus = sorted({v.sku for v in ev.variants if v.sku})
    if (base := base_sku(skus)):
        fields.append({"name": "SKU", "value": f"`{base}`", "inline": True})
    if p.product_type and sizes == "":
        fields.append({"name": "Categoría", "value": p.product_type, "inline": True})
    temp = next((t[5:] for t in p.tags if t.startswith("temp:")), None)
    if temp:
        fields.append({"name": "Temperatura", "value": f"{temp}°", "inline": True})
    if sizes:
        fields.append({"name": "Tallas" if ev.type in (EventType.NEW_SIZE, EventType.RESTOCK) else "Tallas disponibles",
                       "value": ", ".join(size_label(v.title) for v in ev.variants if v.title != "Oferta")[:1000], "inline": False})
    if launch_collection:
        fields.append({"name": "Fecha", "value": "La tienda no la publica en su catálogo: consúltala en el enlace", "inline": False})
    buyable = {normalize_size(v.title) for v in ev.variants if v.available}
    if opp is not None and opp.verified and normalize_size(opp.buy_size or "") not in buyable:
        # Defensa: nunca presentar como comprable un beneficio calculado con ventas de una talla que no está a la venta
        opp = replace(opp, verified=False, notes=["las ventas son de una talla que no está disponible en este aviso"])
    if opp is not None and opp.verified and opp.net_profit_cents is not None:
        fields.append({"name": f"💶 Beneficio neto verificado · talla {size_label(opp.buy_size)}",
                       "value": f"**{eur(opp.net_profit_cents)}** comprando la {size_label(opp.buy_size)} a "
                                f"{eur(opp.buy_price_cents)} · margen {opp.margin_pct:.0f} % sobre venta · "
                                f"ROI {opp.roi_pct:.0f} % sobre compra", "inline": False})
        fields.append({"name": "Reventa (mediana)", "value": eur(opp.resale_price_cents), "inline": True})
        fields.append({"name": "Score", "value": f"{opp.score}/100", "inline": True})
        if opp.basis:
            fields.append({"name": "Base del cálculo", "value": opp.basis[:1000], "inline": False})
    elif opp is not None:
        fields.append({"name": "💶 Beneficio", "value": "**sin verificar** — " + "; ".join(opp.notes[:3])[:900], "inline": False})
    q = quote_plus(base or p.title)
    links = f"[Ver chollo]({p.url})" if is_deal else (
        f"[Producto]({p.url}) | [StockX](https://stockx.com/search?s={q}) | [eBay](https://www.ebay.es/sch/i.html?_nkw={q})")
    fields.append({"name": "Enlaces", "value": links, "inline": False})
    fields.append({"name": "Detectado", "value": madrid_text(ev.detected_at), "inline": False})
    one = [v for v in ev.variants if v.title != "Oferta"]
    size_title = None
    sized = [v for v in one if normalize_size(v.title) not in (None, "Única")]
    if ev.type in (EventType.NEW_SIZE, EventType.RESTOCK) and not is_deal and not sized:
        size_title = "🔄 VUELVE A STOCK (la tienda no indica tallas)"     # v0.9: sin stock por talla no se anuncia una talla
    elif ev.type in (EventType.NEW_SIZE, EventType.RESTOCK) and not is_deal:
        size_title = f"🔄 VUELVE LA {size_label(one[0].title).upper()}" if len(one) == 1 else (
            f"🔄 RESTOCK · {len(one)} tallas" if ev.type == EventType.RESTOCK else f"🔄 VUELVEN {len(one)} TALLAS")
    embed = {
        "title": (f"{size_title} — {p.store}" if size_title and not launch_collection else
                  f"📢 NUEVO EN LANZAMIENTOS — {p.store}" if launch_collection and ev.type == EventType.NEW_PRODUCT else
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
