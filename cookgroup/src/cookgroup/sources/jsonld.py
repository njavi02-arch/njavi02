"""Adaptador compartido para tiendas NO Shopify: datos estructurados schema.org (JSON-LD) de las fichas.

Casi todas las plataformas (Magento, Salesforce Commerce, Shopware, PrestaShop, Next.js…) publican en cada ficha
un <script type="application/ld+json"> con Product → offers (precio, moneda, disponibilidad y, a veces, una
oferta por talla/SKU). Con eso se detecta: producto nuevo (vía listado), vuelta a stock, talla que vuelve (si hay
ofertas por talla) y bajada de precio.

Uso por tienda (config):
  type = "jsonld", base_url = "https://tienda.example"
  listing_urls = ["https://tienda.example/es/novedades"]      # páginas públicas con enlaces a fichas
  product_link_pattern = "/es/p/"                              # qué enlaces del listado son fichas
  watch_urls = [...]                                           # fichas concretas a vigilar siempre
Límites: si una tienda bloquea (403/CAPTCHA) se registra el fallo y no se elude nada.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import requests

from ..models import Product, Variant
from ..ratelimit import wait_turn
from .shopify import USER_AGENT, RateLimited, SourceError

_LD = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)
_HREF = re.compile(r'href=["\']([^"\'#]+)["\']', re.I)
MAX_BYTES = 5_000_000


def _iter_nodes(obj):
    if isinstance(obj, list):
        for x in obj:
            yield from _iter_nodes(x)
    elif isinstance(obj, dict):
        yield obj
        for k in ("@graph", "hasVariant", "itemListElement"):
            if k in obj:
                yield from _iter_nodes(obj[k])


def _types(node) -> set[str]:
    t = node.get("@type")
    return {x.lower() for x in (t if isinstance(t, list) else [t]) if isinstance(x, str)}


def _cents(v) -> int:
    try:
        return round(float(str(v).replace(",", ".")) * 100)
    except (TypeError, ValueError):
        return 0


def _available(av) -> bool | None:
    if av is None:
        return None
    s = str(av).lower()
    if any(k in s for k in ("instock", "in_stock", "limitedavailability", "onlineonly", "preorder", "presale")):
        return True
    if any(k in s for k in ("outofstock", "soldout", "discontinued", "out_of_stock", "instoreonly")):
        return False
    return None


def parse_product_page(html: str, *, url: str, store: str, default_currency: str = "EUR") -> Product | None:
    """Ficha → Product. None si la página no trae Product en JSON-LD (no es un error: puede ser una categoría)."""
    nodes = []
    for raw in _LD.findall(html or ""):
        try:
            nodes.extend(_iter_nodes(json.loads(raw.strip())))
        except ValueError:
            continue
    prods = [n for n in nodes if "product" in _types(n) or "productgroup" in _types(n)]
    if not prods:
        return None
    main = next((p for p in prods if "productgroup" in _types(p)), prods[0])
    name = str(main.get("name") or "").strip()
    brand = main.get("brand")
    vendor = (brand.get("name") if isinstance(brand, dict) else brand) or None
    image = main.get("image")
    if isinstance(image, list):
        image = image[0] if image else None
    if isinstance(image, dict):
        image = image.get("url")
    sku = str(main.get("sku") or main.get("mpn") or main.get("productGroupID") or "") or None
    variants: list[Variant] = []
    currency = default_currency
    # 1) variantes explícitas (ProductGroup.hasVariant) o varios Product con talla
    candidates = [p for p in prods if p is not main] or [main]
    for p in candidates:
        offers = p.get("offers")
        offers = offers if isinstance(offers, list) else [offers] if offers else []
        if offers and isinstance(offers[0], dict) and "offers" in offers[0]:      # AggregateOffer
            offers = offers[0]["offers"] if isinstance(offers[0]["offers"], list) else [offers[0]["offers"]]
        for i, o in enumerate(o for o in offers if isinstance(o, dict)):
            currency = o.get("priceCurrency") or currency
            size = (p.get("size") or o.get("name") or p.get("color")) if p is not main else (o.get("name") or o.get("size"))  # Foot Locker DE/IT: variantes por color
            vsku = str(o.get("sku") or p.get("sku") or "") or None
            vid = vsku or hashlib.sha1(f"{url}|{size}|{i}".encode()).hexdigest()[:12]
            av = _available(o.get("availability"))
            price = _cents(o.get("price") or o.get("lowPrice"))
            scope = "color" if (p is not main and not p.get("size") and not o.get("name") and p.get("color")) else None
            variants.append(Variant(vid, str(size or "Única"), price, bool(av), vsku, stock_scope=scope))
    if not variants:
        return None
    pid = sku or hashlib.sha1(url.encode()).hexdigest()[:16]
    return Product(store=store, product_id=pid, title=name or pid, url=url, currency=currency,
                   variants=tuple(variants), vendor=vendor, image_url=image if isinstance(image, str) else None)


def link_matcher(pattern: str):
    """v1.6: `pattern` es un fragmento del enlace o, con el prefijo «re:», una expresión regular sobre la RUTA.
    La regex permite exigir la forma exacta de una ficha (p. ej. el código de artículo) y descartar ayuda/FAQ,
    categorías y campañas que también terminan en .html."""
    if pattern.startswith("re:"):
        rx = re.compile(pattern[3:])
        return lambda u: bool(rx.search(urlparse(u).path))
    return lambda u: pattern in u


def extract_links(html: str, *, base_url: str, pattern: str) -> list[str]:
    host = urlparse(base_url).hostname
    ok = link_matcher(pattern)
    out, seen = [], set()
    for href in _HREF.findall(html or ""):
        u = urljoin(base_url + "/", href.replace("&amp;", "&")).split("?")[0].split("#")[0]   # sin parámetros de seguimiento
        if urlparse(u).hostname == host and ok(u) and u not in seen:
            seen.add(u)
            out.append(u)
    return out


@dataclass
class JsonLdSource:
    store: str
    base_url: str
    currency: str = "EUR"
    listing_urls: list[str] = field(default_factory=list)
    product_link_pattern: str = "/p/"
    watch_urls: list[str] = field(default_factory=list)
    products_per_cycle: int = 6
    timeout: float = 20.0
    session: requests.Session | None = None
    adapter: str = ""                    # v1.6: "footlocker" | "asics" → tallas desde el estado público de la ficha

    def __post_init__(self):
        self.session = self.session or requests.Session()
        self._known: list[str] = list(self.watch_urls)
        self._pos = 0
        self.watch: list[str] = []
        self.partial = True

    def _get(self, url: str) -> str:
        wait_turn(url)
        try:
            r = self.session.get(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"}, timeout=self.timeout)
        except requests.RequestException as e:
            raise SourceError(f"{self.store}: connection error: {type(e).__name__}") from e
        if r.status_code == 429:
            raise RateLimited(float(r.headers.get("Retry-After", 300)))
        if r.status_code in (401, 403):
            raise SourceError(f"{self.store}: acceso denegado ({r.status_code}); no se intenta eludir")
        if r.status_code != 200:
            raise SourceError(f"{self.store}: HTTP {r.status_code}")
        if len(r.content) > MAX_BYTES:
            raise SourceError(f"{self.store}: página demasiado grande")
        if re.search(r"captcha|cf-chl|px-captcha|access denied|powered and protected by", r.text[:5000], re.I):
            # v1.6: «Powered and protected by …» = desafío JS (adidas ES ficha, New Balance ES listado) sin cookies
            raise SourceError(f"{self.store}: la tienda pide verificación anti-bot; no se elude")
        return r.text

    def fetch(self) -> list[Product]:
        """Listados (descubre fichas nuevas) + rotación de fichas conocidas. Si un listado falla, el ciclo falla
        (no se interpreta como 'productos retirados')."""
        for lu in self.listing_urls:
            links = extract_links(self._get(lu), base_url=self.base_url, pattern=self.product_link_pattern)
            new = [u for u in links if u not in self._known]
            self._known = new + self._known      # las fichas recién vistas, primero
        targets = list(dict.fromkeys(self.watch + self.watch_urls))
        rest = [u for u in self._known if u not in targets]
        n = max(self.products_per_cycle - len(targets), 0)
        if rest and n:
            start = self._pos % len(rest)
            targets += (rest[start:] + rest[:start])[:n]
            self._pos += n
        out, errors = [], 0
        for u in targets:
            try:
                html = self._get(u)
                if self.adapter:
                    from .page_state import ADAPTERS
                    p = ADAPTERS[self.adapter](html, url=u, store=self.store, default_currency=self.currency)
                else:
                    p = parse_product_page(html, url=u, store=self.store, default_currency=self.currency)
            except SourceError as e:
                if "anti-bot" in str(e) or "denegado" in str(e):
                    raise
                errors += 1
                continue
            if p:
                out.append(p)
        if targets and errors == len(targets):
            # v1.3: si no se pudo leer NINGUNA ficha, el ciclo falla (no se interpreta como «todo agotado/retirado»)
            raise SourceError(f"{self.store}: no se pudo leer ninguna ficha ({errors})")
        return out
