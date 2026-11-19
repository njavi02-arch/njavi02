"""Fuente RSS 2.0 / Atom para webs de chollos y tiendas que OFRECEN un feed público.

Usar solo feeds que la propia web publica para ser consumidos (enlace RSS visible o documentado)
y revisar sus condiciones. Sin scraping de HTML, sin eludir antibot. Respeta 429/Retry-After y ETag.

Cada entrada se modela como un Product con una única variante "Oferta". Si el precio no aparece en
el título/descr. se deja a 0 y el monitor debe tener `allow_unknown_price = true`.
"""
from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

import requests

from ..models import Product, Variant
from .shopify import USER_AGENT, RateLimited, SourceError

MAX_BYTES = 2_000_000
_NS = {"atom": "http://www.w3.org/2005/Atom", "media": "http://search.yahoo.com/mrss/",
       "pepper": "http://www.pepper.com/rss"}  # Chollometro, Dealabs, mydealz, Pepper, hotukdeals (verificado 19-nov-2026)
_TEMP = re.compile(r"^\s*(-?\d{1,5})°\s*-\s*")
_PRICE = re.compile(r"(\d{1,6}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)\s?(?:€|EUR)|€\s?(\d{1,6}(?:[.,]\d{1,2})?)", re.I)
_TAG = re.compile(r"<[^>]+>")


def parse_price_cents(text: str) -> int:
    """Primer importe en euros del texto; 0 si no hay. "1.299,99 €" -> 129999."""
    m = _PRICE.search(text or "")
    if not m:
        return 0
    s = m.group(1) or m.group(2)
    if re.search(r"[.,]\d{1,2}$", s):
        whole, frac = re.split(r"[.,](?=\d{1,2}$)", s)
    else:
        whole, frac = s, "0"
    whole = re.sub(r"[.,]", "", whole)
    return int(whole) * 100 + int((frac + "0")[:2])


def _txt(el, path: str) -> str:
    x = el.find(path, _NS)
    return (x.text or "").strip() if x is not None and x.text else ""


def parse_feed(xml_text: str, *, store: str, currency: str = "EUR") -> list[Product]:
    """Función pura: XML -> Product. Entradas sin título o sin enlace se descartan."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise SourceError(f"{store}: feed no es XML válido") from e
    items = root.findall("./channel/item") or root.findall("atom:entry", _NS)
    out: list[Product] = []
    for it in items:
        title = _txt(it, "title") or _txt(it, "atom:title")
        link = _txt(it, "link")
        if not link:
            a = it.find("atom:link", _NS)
            link = (a.get("href") or "").strip() if a is not None else ""
        guid = _txt(it, "guid") or _txt(it, "atom:id") or link
        desc = _TAG.sub(" ", _txt(it, "description") or _txt(it, "atom:summary"))
        if not title or not link:
            continue
        tags: list[str] = []
        if (tm := _TEMP.match(title)):
            tags.append(f"temp:{tm.group(1)}")   # "temperatura" del chollo en webs Pepper (votos de la comunidad)
            title = title[tm.end():].strip()
        merchant = it.find("pepper:merchant", _NS)
        vendor = merchant.get("name") if merchant is not None else None
        category = _txt(it, "category") or None
        img = None
        for path, attr in (("enclosure", "url"), ("media:content", "url"), ("media:thumbnail", "url")):
            e = it.find(path, _NS)
            if e is not None and e.get(attr):
                img = e.get(attr)
                break
        pid = hashlib.sha1(guid.encode()).hexdigest()[:16]
        price = (parse_price_cents(merchant.get("price", "")) if merchant is not None else 0) \
            or parse_price_cents(title) or parse_price_cents(desc)
        out.append(Product(store=store, product_id=pid, title=title, url=link, currency=currency,
                           variants=(Variant(pid, "Oferta", price, True),), image_url=img,
                           vendor=vendor, product_type=category, tags=tuple(tags)))
    return out


@dataclass
class RssSource:
    store: str
    feed_url: str
    currency: str = "EUR"
    timeout: float = 15.0
    session: requests.Session | None = None
    _etag: str | None = field(default=None, init=False)

    def __post_init__(self):
        self.session = self.session or requests.Session()

    def fetch(self) -> list[Product]:
        headers = {"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml"}
        if self._etag:
            headers["If-None-Match"] = self._etag
        try:
            r = self.session.get(self.feed_url, headers=headers, timeout=self.timeout)
        except requests.RequestException as e:
            raise SourceError(f"{self.store}: connection error: {e}") from e
        if r.status_code == 429:
            raise RateLimited(float(r.headers.get("Retry-After", 300)))
        if r.status_code == 304:
            raise SourceError("not-modified")
        if r.status_code in (401, 403):
            raise SourceError(f"{self.store}: acceso denegado ({r.status_code}); no se intenta eludir")
        if r.status_code != 200:
            raise SourceError(f"{self.store}: HTTP {r.status_code}")
        if len(r.content) > MAX_BYTES:
            raise SourceError(f"{self.store}: feed demasiado grande")
        if (etag := r.headers.get("ETag")):
            self._etag = etag
        return parse_feed(r.text, store=self.store, currency=self.currency)
