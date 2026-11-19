"""BSTN (bstn.com) — lanzamientos, raffles, salida a la venta y stock por talla.

Fuentes (investigadas el 19-nov-2026 en navegador; ver docs/STORES.md):
- Listado «Coming Soon»  https://www.bstn.com/<región>/<men|women|kids>/upcoming[/footwear]
  HTML renderizado en servidor con <script id="__NEXT_DATA__">: índice magento2_<eu|uk|us>_products con, por
  producto, release_date ("20. Nov | 9:00 CET"), release_date_row (epoch), raffle / raffle_is_active /
  raffle_is_expired / raffleends ("20. Nov | 15:00 CET") / raffle_url, app_only, instore_only, precio, descuento.
- Ficha de producto  https://www.bstn.com/<región>/<p|r>/<slug>
  __NEXT_DATA__.props.pageProps.productDetails: release_date_raw, configurable_options (EU/UK/US con
  qty_in_stock por talla; las tallas agotadas NO aparecen), price_range (final/regular).
Política: robots.txt de bstn.com excluye /raffle/ y /api/ → el bot NO consulta las páginas de raffle
(raffle.bstn.com) ni APIs; solo enlaza a ellas. Listados y fichas sí están permitidos.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

from .shopify import USER_AGENT, RateLimited, SourceError

BASE = "https://www.bstn.com"
RAFFLE_BASE = "https://raffle.bstn.com"
IMG_BASE = "https://img.bstn.com/card-default/"
MAX_BYTES = 6_000_000
_NEXT = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
_TZ = {"CET": "Europe/Berlin", "CEST": "Europe/Berlin", "GMT": "Europe/London", "BST": "Europe/London",
       "EST": "America/New_York", "EDT": "America/New_York", "UTC": "UTC"}
_MONTHS = {m: i + 1 for i, names in enumerate([
    ("jan", "ene", "jän", "janv"), ("feb", "fév", "févr"), ("mar", "mär", "mars"), ("apr", "abr", "avr"),
    ("may", "mai", "mag"), ("jun", "juin", "giu"), ("jul", "juil", "lug"), ("aug", "ago", "août"),
    ("sep", "sept", "set"), ("oct", "okt", "ott"), ("nov",), ("dec", "dez", "dic", "déc")]) for m in names}
_DATE_TXT = re.compile(r"^\s*(\d{1,2})\.?\s*([A-Za-zäéû]{3,5})\.?\s*(?:\|\s*(\d{1,2}):(\d{2})\s*([A-Z]{2,4}))?\s*$")


@dataclass
class SizeStock:
    eu: str
    qty: int
    uk: str | None = None
    us: str | None = None

    def label(self) -> str:
        extra = " / ".join(x for x in (f"UK {self.uk}" if self.uk else "", f"US {self.us}" if self.us else "") if x)
        return f"EU {self.eu}" + (f" ({extra})" if extra else "")


@dataclass
class Launch:
    """Un artículo visto en un calendario/listado de lanzamientos de una tienda."""
    store: str
    region: str
    key: str                       # SKU de la tienda (article_number)
    brand: str
    name: str
    url: str | None                # ficha (p/ o r/); None si solo existe la página de raffle
    image_url: str | None
    currency: str
    price_cents: int | None
    discount_pct: float = 0.0
    release_ts: int | None = None  # epoch exacto publicado por la tienda
    release_text: str | None = None  # texto original con su zona horaria ("20. Nov | 9:00 CET")
    coming_soon: bool = False
    raffle: bool = False
    raffle_active: bool = False
    raffle_expired: bool = False
    raffle_url: str | None = None
    raffle_ends_ts: int | None = None
    raffle_ends_text: str | None = None
    app_only: bool = False
    instore_only: bool = False

    @property
    def uid(self) -> str:
        return f"{self.store}|{self.region}|{self.key}"

    @property
    def link(self) -> str | None:
        return self.raffle_url if self.raffle_active else (self.url or self.raffle_url)


@dataclass
class ProductPage:
    key: str
    name: str
    brand: str
    currency: str | None
    final_cents: int | None
    regular_cents: int | None
    release_ts: int | None
    release_text: str | None
    app_only: bool
    instore_only: bool
    hot: bool
    sizes: list[SizeStock] = field(default_factory=list)

    @property
    def in_stock(self) -> list[SizeStock]:
        return [s for s in self.sizes if s.qty > 0]


# ------------------------------------------------------------------ parsing (puro, testeable)
def extract_next_data(html: str) -> dict:
    m = _NEXT.search(html or "")
    if not m:
        raise SourceError("BSTN: la página no contiene __NEXT_DATA__ (¿bloqueo, mantenimiento o cambio de web?)")
    try:
        return json.loads(m.group(1))
    except ValueError as e:
        raise SourceError("BSTN: __NEXT_DATA__ ilegible") from e


def parse_store_date(text: str | None, now: datetime) -> int | None:
    """"20. Nov | 15:00 CET" -> epoch. Sin año en la web: se elige el más cercano a `now` (±6 meses)."""
    if not text:
        return None
    m = _DATE_TXT.match(text)
    if not m:
        return None
    day, mon = int(m.group(1)), _MONTHS.get(m.group(2).lower()[:4]) or _MONTHS.get(m.group(2).lower()[:3])
    if not mon:
        return None
    tz = ZoneInfo(_TZ.get((m.group(5) or "CET").upper(), "Europe/Berlin"))
    hh, mm = (int(m.group(3)), int(m.group(4))) if m.group(3) else (0, 0)
    best = None
    for y in (now.year - 1, now.year, now.year + 1):
        try:
            cand = datetime(y, mon, day, hh, mm, tzinfo=tz)
        except ValueError:
            continue
        if best is None or abs(cand - now) < abs(best - now):
            best = cand
    return int(best.timestamp()) if best and abs(best - now) <= timedelta(days=200) else None


def _yes(v) -> bool:
    return v is True or str(v).strip().lower() in {"yes", "1", "true"}


def _cents(v) -> int | None:
    try:
        return round(float(v) * 100) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def parse_listing(next_data: dict, *, region: str, now: datetime, store: str = "BSTN") -> list[Launch]:
    try:
        results = next_data["props"]["pageProps"]["serverState"]["initialResults"]
    except (KeyError, TypeError) as e:
        raise SourceError("BSTN: estructura del listado desconocida") from e
    idx = next((k for k in results if re.fullmatch(r"magento2_\w+_products", k)), None)
    if not idx:
        raise SourceError("BSTN: índice de productos no encontrado en el listado")
    hits = results[idx]["results"][0]["hits"]
    out: list[Launch] = []
    for h in hits:
        key = str(h.get("article_number") or "").strip()
        if not key or not h.get("name"):
            continue
        cur, price = next(((k.split(".")[1], _cents(v)) for k, v in h.items()
                           if re.fullmatch(r"price\.[A-Z]{3}\.default", k)), ("EUR", None))
        disc = next((float(v or 0) for k, v in h.items() if re.fullmatch(r"discount\.[A-Z]{3}\.default", k)), 0.0)
        url = (h.get("url") or "").split("?")[0]
        raffle_slug = (h.get("raffle_url") or "").split("?")[0]
        img = (h.get("image_url") or "").split("?")[0]
        row = int(h.get("release_date_row") or 0)
        ends_text = h.get("raffleends") or None
        out.append(Launch(
            store=store, region=region, key=key, brand=str(h.get("brand") or "").strip(), name=str(h["name"]).strip(),
            url=f"{BASE}/{region}/{url}" if url else None,
            image_url=img if img.startswith("http") else (IMG_BASE + img if img else None),
            currency=cur, price_cents=price, discount_pct=disc,
            release_ts=row if row > 0 else None, release_text=h.get("release_date") or None,
            coming_soon=_yes(h.get("coming_soon")), raffle=_yes(h.get("raffle")),
            raffle_active=_yes(h.get("raffle_is_active")), raffle_expired=_yes(h.get("raffle_is_expired")),
            raffle_url=(raffle_slug if raffle_slug.startswith("http") else f"{RAFFLE_BASE}/{region}/{raffle_slug}") if raffle_slug else None,
            raffle_ends_ts=parse_store_date(ends_text, now), raffle_ends_text=ends_text,
            app_only=_yes(h.get("app_only")), instore_only=_yes(h.get("instore_only")),
        ))
    return out


def _size_label(raw: str) -> str:
    s = str(raw).split("-")[0].strip().replace(",", ".")   # "6,0-EU40" -> "6.0"
    return s[:-2] if s.endswith(".0") else s


def parse_product(next_data: dict) -> ProductPage:
    p = next_data.get("props", {}).get("pageProps", {}).get("productDetails")
    while isinstance(p, dict) and "productDetails" in p:
        p = p["productDetails"]
    if isinstance(p, list):
        p = p[0] if p else None
    if isinstance(p, dict) and "items" in p:
        p = (p["items"] or [None])[0]
    if not isinstance(p, dict) or not p.get("article_number"):
        raise SourceError("BSTN: ficha sin datos de producto")
    opts = {o.get("label", "").upper(): o.get("values", []) for o in p.get("configurable_options") or []}
    eu = opts.get("EU", [])
    uk, us = opts.get("UK", []), opts.get("US", [])
    # Equivalencias UK/US solo si las listas están alineadas 1:1 (en la Carhartt real US tiene 12 y EU 14)
    uk_ok, us_ok = len(uk) == len(eu), len(us) == len(eu)
    sizes = []
    for i, v in enumerate(eu):
        qty = int(((v.get("stock") or {}).get("qty_in_stock")) or 0)
        sizes.append(SizeStock(_size_label(v.get("label", "")), qty,
                               _size_label(uk[i]["label"]) if uk_ok else None,
                               _size_label(us[i]["label"]) if us_ok else None))
    mp = ((p.get("price_range") or {}).get("maximum_price") or {})
    fin, reg = mp.get("final_price") or {}, mp.get("regular_price") or {}
    raw = p.get("release_date_raw")
    return ProductPage(
        key=str(p["article_number"]), name=str(p.get("name") or ""), brand=str(p.get("brand") or ""),
        currency=fin.get("currency"), final_cents=_cents(fin.get("value")), regular_cents=_cents(reg.get("value")),
        release_ts=int(raw) if raw and str(raw).isdigit() and int(raw) > 0 else None,
        release_text=p.get("release_date"), app_only=_yes(p.get("app_only")), instore_only=_yes(p.get("instore_only")),
        hot=bool(p.get("hot_release_message")), sizes=sizes,
    )


# ------------------------------------------------------------------ red
@dataclass
class BstnSource:
    regions: list[str]
    listings: list[str]               # p. ej. ["men/upcoming", "women/upcoming/footwear"]
    timeout: float = 20.0
    pause_s: float = 2.0
    session: requests.Session | None = None

    def __post_init__(self):
        self.session = self.session or requests.Session()

    def _get(self, url: str) -> str:
        if re.search(r"/(raffle|api)/|//raffle\.", url):
            raise SourceError(f"BSTN: {url} excluido por robots.txt; no se consulta")
        try:
            r = self.session.get(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"}, timeout=self.timeout)
        except requests.RequestException as e:
            raise SourceError(f"BSTN: error de conexión: {e}") from e
        if r.status_code == 429:
            raise RateLimited(float(r.headers.get("Retry-After", 300)))
        if r.status_code in (401, 403):
            raise SourceError(f"BSTN: acceso denegado ({r.status_code}); no se intenta eludir")
        if r.status_code == 404:
            raise SourceError("BSTN: 404")
        if r.status_code != 200:
            raise SourceError(f"BSTN: HTTP {r.status_code}")
        if len(r.content) > MAX_BYTES:
            raise SourceError("BSTN: respuesta demasiado grande")
        return r.text

    def fetch_launches(self, now: datetime) -> list[Launch]:
        """Todas las páginas configuradas. Si UNA falla, se lanza error: un listado parcial no debe parecer
        que han desaparecido productos."""
        seen: dict[str, Launch] = {}
        for i, (region, path) in enumerate((r, p) for r in self.regions for p in self.listings):
            if i:
                time.sleep(self.pause_s)
            nd = extract_next_data(self._get(f"{BASE}/{region}/{path}"))
            for item in parse_listing(nd, region=region, now=now):
                seen.setdefault(item.uid, item)
        return list(seen.values())

    def fetch_product(self, url: str) -> ProductPage:
        return parse_product(extract_next_data(self._get(url)))
