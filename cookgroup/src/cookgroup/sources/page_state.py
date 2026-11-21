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


ADAPTERS = {"footlocker": parse_footlocker_state, "asics": parse_asics_state}
