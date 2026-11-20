"""Fuente genérica para tiendas Shopify vía su endpoint público /products.json.

Es un endpoint público de catálogo (no requiere autenticación). Se consulta con
User-Agent identificable, intervalos conservadores, ETag y respeto de 429/Retry-After.
No se elude ningún antibot/CAPTCHA: si la tienda responde 401/403/429 se registra y se espera.
"""
from __future__ import annotations

from dataclasses import dataclass

import requests

from ..models import Product, Variant
from ..ratelimit import wait_turn

USER_AGENT = "CookgroupMonitor/0.1 (+contact: configure CONTACT_URL)"


class SourceError(Exception):
    pass


class RateLimited(SourceError):
    def __init__(self, retry_after: float):
        super().__init__(f"rate limited, retry after {retry_after}s")
        self.retry_after = retry_after


def _to_cents(value: str | int | float | None) -> int:
    if value is None or value == "":
        return 0
    s = str(value).replace(",", ".")
    whole, _, frac = s.partition(".")
    frac = (frac + "00")[:2]
    return int(whole or 0) * 100 + int(frac)


def parse_products(payload: dict, *, store: str, base_url: str, currency: str) -> list[Product]:
    """Convierte la respuesta JSON de /products.json en Product. Función pura (testeable)."""
    out: list[Product] = []
    for p in payload.get("products", []):
        variants = tuple(
            Variant(
                variant_id=str(v["id"]),
                title=str(v.get("title") or v.get("option1") or "Default"),
                price_cents=_to_cents(v.get("price")),
                available=bool(v.get("available", False)),
                sku=v.get("sku") or None,
                compare_at_cents=_to_cents(v.get("compare_at_price")) or None,
            )
            for v in p.get("variants", [])
        )
        images = p.get("images") or []
        tags = p.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        out.append(
            Product(
                store=store,
                product_id=str(p["id"]),
                title=p.get("title", "").strip(),
                url=f"{base_url.rstrip('/')}/products/{p['handle']}",
                currency=currency,
                variants=variants,
                vendor=p.get("vendor") or None,
                product_type=p.get("product_type") or None,
                tags=tuple(tags),
                image_url=(images[0].get("src") if images else None),
            )
        )
    return out


@dataclass
class ShopifySource:
    """Catálogo Shopify con tres capas por ciclo:
    1. página 1 (novedades) siempre;
    2. paginación rotatoria: una página más del catálogo por ciclo (2, 3, … hasta `deep_pages`), así un restock de un
       modelo antiguo se ve como mucho en `deep_pages` ciclos;
    3. seguimiento selectivo: hasta `watch_per_cycle` fichas /products/<handle>.json de modelos vigilados por ciclo.
    El resultado es PARCIAL: el pipeline fusiona con la instantánea guardada en vez de reemplazarla.
    """
    store: str
    base_url: str
    currency: str = "EUR"
    pages: int = 1                    # páginas fijas por ciclo (compatibilidad)
    page_size: int = 250
    timeout: float = 15.0
    session: requests.Session | None = None
    collection: str | None = None     # p. ej. "launches": /collections/launches/products.json
    deep_pages: int = 1               # >1 activa la paginación rotatoria
    watch_per_cycle: int = 3

    def __post_init__(self):
        self.session = self.session or requests.Session()
        self._etags: dict[int, str] = {}
        self._rot = 2
        self._last_p1: int | None = None
        self.watch: list[str] = []      # handles vigilados (lo rellena el pipeline)
        self._watch_pos = 0
        self.partial = True

    def _url(self, page: int) -> str:
        base = self.base_url.rstrip("/")
        return f"{base}/collections/{self.collection}/products.json" if self.collection else f"{base}/products.json"

    def _get(self, url: str, params: dict | None = None, etag_key: int | None = None):
        wait_turn(url)
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if etag_key is not None and etag_key in self._etags:
            headers["If-None-Match"] = self._etags[etag_key]
        try:
            r = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        except requests.RequestException as e:
            raise SourceError(f"{self.store}: connection error: {type(e).__name__}") from e
        if r.status_code == 429:
            raise RateLimited(float(r.headers.get("Retry-After", 60)))
        if r.status_code == 304:
            return None
        if r.status_code in (401, 403):
            raise SourceError(f"{self.store}: acceso denegado ({r.status_code}); no se intenta eludir")
        if r.status_code != 200:
            raise SourceError(f"{self.store}: HTTP {r.status_code}")
        if etag_key is not None and (etag := r.headers.get("ETag")):
            self._etags[etag_key] = etag
        try:
            return r.json()
        except ValueError as e:
            raise SourceError(f"{self.store}: respuesta no JSON") from e

    def _resolve_currency(self) -> None:
        """currency = "auto": la moneda que Shopify devuelve a este visitante (/cart.js). Si falla, "N/D" (no se inventa)."""
        if self.currency != "auto":
            return
        try:
            data = self._get(f"{self.base_url.rstrip('/')}/cart.js")
            self.currency = (data or {}).get("currency") or "N/D"
        except (SourceError, RateLimited):
            self.currency = "N/D"

    def _page(self, page: int) -> list[Product] | None:
        payload = self._get(self._url(page), {"limit": self.page_size, "page": page}, etag_key=page)
        if payload is None:
            return None
        return parse_products(payload, store=self.store, base_url=self.base_url, currency=self.currency)

    def fetch(self) -> list[Product]:
        self._resolve_currency()
        products: list[Product] = []
        first = self._page(1)
        if first is None and self.pages == 1 and self.deep_pages <= 1 and not self.watch:
            raise SourceError("not-modified")  # el runner lo trata como 'sin cambios'
        if first is not None:
            if not first and (self._last_p1 or 0) >= 5:
                raise SourceError(f"{self.store}: la página 1 llega vacía (antes {self._last_p1}); lectura sospechosa, se ignora")
            self._last_p1 = len(first)
            products.extend(first)
        for page in range(2, self.pages + 1):           # páginas fijas
            batch = self._page(page) or []
            products.extend(batch)
            if len(batch) < self.page_size:
                break
        if self.deep_pages > 1 and first is not None and len(first) >= self.page_size:   # rotatoria
            page = max(self._rot, self.pages + 1)
            batch = self._page(page) or []
            products.extend(batch)
            self._rot = 2 if (len(batch) < self.page_size or page >= self.deep_pages) else page + 1
        if self.watch:                                    # seguimiento selectivo
            n = min(self.watch_per_cycle, len(self.watch))
            for i in range(n):
                handle = self.watch[(self._watch_pos + i) % len(self.watch)]
                try:
                    one = self._get(f"{self.base_url.rstrip('/')}/products/{handle}.json")
                except SourceError:
                    continue   # una ficha retirada no invalida el ciclo
                if one and one.get("product"):
                    products.extend(parse_products({"products": [one["product"]]}, store=self.store,
                                                   base_url=self.base_url, currency=self.currency))
            self._watch_pos = (self._watch_pos + n) % max(len(self.watch), 1)
        seen, out = set(), []
        for p in products:
            if p.key not in seen:
                seen.add(p.key)
                out.append(p)
        return out
