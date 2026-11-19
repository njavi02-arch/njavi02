"""Fuente genérica para tiendas Shopify vía su endpoint público /products.json.

Es un endpoint público de catálogo (no requiere autenticación). Se consulta con
User-Agent identificable, intervalos conservadores, ETag y respeto de 429/Retry-After.
No se elude ningún antibot/CAPTCHA: si la tienda responde 401/403/429 se registra y se espera.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from ..models import Product, Variant

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
    store: str
    base_url: str
    currency: str = "EUR"
    pages: int = 1
    page_size: int = 250
    collection: str | None = None     # p. ej. "launches": /collections/launches/products.json
    timeout: float = 15.0
    session: requests.Session | None = None

    def __post_init__(self):
        self.session = self.session or requests.Session()
        self._etags: dict[int, str] = {}

    def fetch(self) -> list[Product]:
        products: list[Product] = []
        for page in range(1, self.pages + 1):
            url = (f"{self.base_url.rstrip('/')}/collections/{self.collection}/products.json" if self.collection
                   else f"{self.base_url.rstrip('/')}/products.json")
            headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
            if page in self._etags:
                headers["If-None-Match"] = self._etags[page]
            try:
                r = self.session.get(url, params={"limit": self.page_size, "page": page},
                                     headers=headers, timeout=self.timeout)
            except requests.RequestException as e:
                raise SourceError(f"{self.store}: connection error: {e}") from e
            if r.status_code == 429:
                raise RateLimited(float(r.headers.get("Retry-After", 60)))
            if r.status_code == 304:
                raise SourceError("not-modified")  # el runner lo trata como 'sin cambios'
            if r.status_code in (401, 403):
                raise SourceError(f"{self.store}: acceso denegado ({r.status_code}); no se intenta eludir")
            if r.status_code != 200:
                raise SourceError(f"{self.store}: HTTP {r.status_code}")
            if (etag := r.headers.get("ETag")):
                self._etags[page] = etag
            try:
                payload = r.json()
            except ValueError as e:
                raise SourceError(f"{self.store}: respuesta no JSON") from e
            batch = parse_products(payload, store=self.store, base_url=self.base_url, currency=self.currency)
            products.extend(batch)
            if len(batch) < self.page_size:
                break
            time.sleep(1.0)
        return products
