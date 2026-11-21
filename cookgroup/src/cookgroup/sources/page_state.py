"""v1.6 · adaptadores de TALLA a partir del estado público que la propia ficha incrusta en su HTML.

Se usan cuando el JSON-LD no basta (Foot Locker ES/FR: una sola oferta por ficha; ASICS: talla «N/A»).
Cada ficha corresponde a UN color: el identificador del producto es el del color y el enlace va a esa ficha.

Estados de una talla (Variant.stock_scope):
  "online"       se puede pedir online (es lo único que dispara un aviso de reposición)
  "solo_tienda"  la ficha la marca disponible solo en tienda física → NO se anuncia como disponible online
  "agotada"      sin stock en ningún canal
  "desconocido"  la ficha no publica el dato → no cuenta ni como disponible ni como agotada (known=False)

Fuentes verificadas el 21-nov-2026 desde el navegador del dueño (solo lectura):
  Foot Locker (ES, FR, DE): window.footlocker.STATE_FROM_SERVER → api.productDetails.getDetails.data.sizes[*]
      sizeVariants {eu, uk, us} · inventory.warehouseInventoryAvailable (online) / storeInventoryAvailable (tienda)
      · price.salePrice. El selector visible marca como elegible una talla con stock solo en tienda, por eso
      NO se usa el selector como prueba de stock online.
  ASICS (ES): <script id="mobify-data"> → producto con masterId · attributes.size.values[*] {value: US, name: EU,
      orderable} del color seleccionado (attributes.color.values[selected]) · price.model.sales.value.
"""
from __future__ import annotations

import json
import re

from ..models import Product, Variant
from .jsonld import _cents


def _balanced_json(text: str, start: int) -> dict | None:
    i = text.find("{", start)
    if i < 0:
        return None
    depth, in_str, esc = 0, False, False
    for j in range(i, len(text)):
        c = text[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[i:j + 1])
                except ValueError:
                    return None
    return None


def _alt(uk=None, us=None) -> str | None:
    """Equivalencias que publica la tienda (UK «6 (EU 40)» se queda en «UK 6»)."""
    parts = [f"UK {str(uk).split(' (')[0]}" if uk else "", f"US {us}" if us else ""]
    return " · ".join(x for x in parts if x) or None


def parse_footlocker_state(html: str, *, url: str, store: str, default_currency: str = "EUR") -> Product | None:
    k = html.find("STATE_FROM_SERVER")
    if k < 0:
        return None
    state = _balanced_json(html, k)
    try:
        d = state["api"]["productDetails"]["getDetails"]["data"]
        sizes = d["sizes"]
    except (TypeError, KeyError):
        return None
    if not sizes:
        return None
    style, model = d.get("style") or {}, d.get("model") or {}
    color = (style.get("color") or "").strip()
    pid = str(style.get("sku") or "") or None
    variants, currency = [], default_currency
    for z in sizes:  # noqa: B007
        sv = z.get("sizeVariants") or {}
        eu = sv.get("eu") or z.get("size")
        inv = z.get("inventory") or {}
        online, shop = inv.get("warehouseInventoryAvailable"), inv.get("storeInventoryAvailable")
        if online is True:
            scope = "online"
        elif online is False and shop is True:
            scope = "solo_tienda"
        elif online is False and shop is False and inv.get("inventoryAvailable") is False:
            scope = "agotada"
        else:
            scope = "desconocido"                      # p. ej. inventoryAvailable sin canal, o campos ausentes
        pr = z.get("price") or {}
        currency = pr.get("currencyIso") or currency
        variants.append(Variant(str(z.get("productNumber") or z.get("id") or eu), f"EU {eu}",
                                _cents(pr.get("salePrice") or pr.get("listPrice")) or 0, scope == "online",
                                pid, known=scope != "desconocido",      # SKU del color (no el de la talla)
                                alt_sizes=_alt(sv.get("uk"), sv.get("us")), stock_scope=scope))
    name = (model.get("name") or "").strip() or pid or url
    return Product(store=store, product_id=pid or url, title=f"{name} · {color}" if color else name, url=url,
                   currency=currency, variants=tuple(variants), vendor=(model.get("brand") or None))


def parse_asics_state(html: str, *, url: str, store: str, default_currency: str = "EUR") -> Product | None:
    m = re.search(r'<script[^>]+id=["\']mobify-data["\'][^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    try:
        root = json.loads(m.group(1))
    except ValueError:
        return None
    found = []

    def walk(o, depth=0):
        if found or depth > 16 or not isinstance(o, (dict, list)):
            return
        if isinstance(o, dict):
            if o.get("masterId") and isinstance(o.get("attributes"), dict) and "color" in o["attributes"]:
                found.append(o)
                return
            for v in o.values():
                walk(v, depth + 1)
        else:
            for v in o:
                walk(v, depth + 1)
    walk(root)
    if not found:
        return None
    p = found[0]
    attrs = p["attributes"]
    sel = next((c for c in (attrs.get("color") or {}).get("values", []) if c.get("selected")), None)
    if not sel:
        return None                                    # sin color seleccionado no se sabe a qué color van las tallas
    model = (p.get("price") or {}).get("model") or {}
    price = _cents(((model.get("sales") or {}).get("value"))) or 0
    currency = (p.get("price") or {}).get("currency") or default_currency
    variants = []
    for s in (attrs.get("size") or {}).get("values", []):
        orderable = s.get("orderable")
        scope = "online" if orderable is True else "agotada" if orderable is False else "desconocido"
        vid = f"{sel['value']}|{s.get('value')}"
        variants.append(Variant(vid, f"EU {s.get('name')}", price, scope == "online", vid,
                                known=scope != "desconocido", alt_sizes=_alt(None, s.get("value")), stock_scope=scope))
    if not variants:
        return None
    title = ((p.get("seo") or {}).get("title") or p.get("masterId")).strip()
    return Product(store=store, product_id=str(sel["value"]), title=f"{title} · {sel.get('name', '')}".strip(" ·"),
                   url=url, currency=currency, variants=tuple(variants), vendor="ASICS")


_ASOS_SIZE = re.compile(r'"variantId":(\d+),"size":"([^"]+)","brandSize":"([^"]*)"[^}]*?"colour":"([^"]*)","colourWayId":(\d+)')


def parse_asos_state(html: str, *, url: str, store: str, default_currency: str = "EUR") -> Product | None:
    """ASOS (ES), verificado el 21-nov-2026: `window.asos.pdp.config.stockPriceResponse = '[…]'` trae, por variante,
    isInStock y su precio (puede variar por talla); el mapa variantId → talla («EU 42 2/3») y color está en la
    definición del producto de la misma página. Cada ficha (/prd/<id>) es UN color."""
    k = html.find("window.asos.pdp.config.stockPriceResponse")
    if k < 0:
        return None
    a = html.find("'", k) + 1
    b = html.find("';", a)
    try:
        stock = json.loads(html[a:b].replace('\\"', '"').replace("\\\\", "\\"))
    except ValueError:
        return None
    sizes = {m.group(1): (m.group(2), m.group(4)) for m in _ASOS_SIZE.finditer(html)}
    name = None
    for raw in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            j = json.loads(raw)
        except ValueError:
            continue
        for n in (j.get("@graph") or [j]) if isinstance(j, dict) else []:
            if isinstance(n, dict) and n.get("@type") in ("ProductGroup", "Product"):
                name = name or n.get("name")
    if not stock:
        return None
    prod = stock[0]
    pr = prod.get("productPrice") or {}
    currency = pr.get("currency") or default_currency
    base = ((pr.get("current") or {}).get("value"))
    variants, color = [], ""
    for v in prod.get("variants") or []:
        vid = str(v.get("id"))
        size, color = sizes.get(vid, (None, color))
        ins = v.get("isInStock")
        scope = "online" if ins is True else "agotada" if ins is False else "desconocido"
        if size is None:
            scope = "desconocido"                       # sin talla publicada para esa variante: no se anuncia
        price = _cents(((v.get("price") or {}).get("current") or {}).get("value") or base) or 0
        variants.append(Variant(vid, size or f"variante {vid}", price, scope == "online", vid,
                                known=scope != "desconocido", stock_scope=scope))
    if not variants:
        return None
    title = (name or f"ASOS {prod.get('productId')}").strip()
    return Product(store=store, product_id=str(prod.get("productId")), title=f"{title} · {color}" if color else title,
                   url=url, currency=currency, variants=tuple(variants))


ADAPTERS = {"footlocker": parse_footlocker_state, "asics": parse_asics_state, "asos": parse_asos_state}
