"""Escala: paginación rotatoria, seguimiento selectivo, lecturas parciales, límite por dominio. Datos SIMULADOS."""
import copy
import json
from pathlib import Path

import pytest

from cookgroup import ratelimit
from cookgroup.config import MonitorConfig
from cookgroup.market import FileMarketProvider
from cookgroup.pipeline import run_cycle
from cookgroup.sources.shopify import ShopifySource, SourceError
from cookgroup.store import Store


def prod(i, avail=True, title=None):
    return {"id": i, "title": title or f"Zapatilla {i}", "handle": f"zapa-{i}", "vendor": "Nike",
            "variants": [{"id": i * 10 + 1, "title": "42", "price": "100.00", "available": avail}]}


class Catalog:
    """Tienda falsa paginada (page_size pequeño) con fichas /products/<handle>.json."""
    def __init__(self, n, page_size):
        self.items = {i: prod(i) for i in range(1, n + 1)}
        self.page_size, self.urls = page_size, []

    def get(self, url, params=None, headers=None, timeout=None):
        self.urls.append((url, (params or {}).get("page")))
        class R:
            status_code, headers = 200, {}
        r = R()
        if url.endswith("/products.json"):
            page = params["page"]
            ids = sorted(self.items)[(page - 1) * self.page_size: page * self.page_size]
            r.json = lambda: {"products": [self.items[i] for i in ids]}
        else:
            h = url.rsplit("/products/", 1)[1][:-5]
            i = int(h.split("-")[1])
            r.json = lambda: {"product": self.items[i]}
        return r


def src(cat, **kw):
    return ShopifySource("T", "https://t.invalid", page_size=cat.page_size, session=cat, **kw)


def test_rotation_visits_whole_catalog_and_wraps():
    cat = Catalog(10, 3)  # páginas: [1-3][4-6][7-9][10]
    s = src(cat, deep_pages=10)
    seen_pages = []
    for _ in range(5):
        s.fetch()
        seen_pages.append(sorted(p for u, p in cat.urls if p and p > 1)[-1])
        cat.urls.clear()
    assert seen_pages == [2, 3, 4, 2, 3]


def test_restock_of_old_model_on_page_3_is_detected_and_partial_reads_are_not_new(tmp_path):
    cat = Catalog(9, 3)
    for i in (7, 8, 9):
        cat.items[i]["variants"][0]["available"] = False
    st, sent = Store(str(tmp_path / "db.sqlite")), []
    cfg = MonitorConfig("t", "shopify", "T", "https://t.invalid")
    s, mk = src(cat, deep_pages=5), FileMarketProvider(str(tmp_path / "x.json"))
    for _ in range(3):   # línea base + recorrido de páginas 2 y 3
        run_cycle(cfg, {}, s, st, mk, lambda p: sent.append(p) or "1")
    assert sent == []    # leer páginas nuevas del catálogo NO es "producto nuevo"
    cat.items[8]["variants"][0]["available"] = True
    for _ in range(3):
        run_cycle(cfg, {}, s, st, mk, lambda p: sent.append(p) or "1")
    titles = [e["title"] for p in sent for e in p["embeds"]]
    assert titles == ["🔄 VUELVE LA EU 42 — T"] and "Zapatilla 8" in json.dumps(sent)


def test_selective_watch_fetches_product_json(tmp_path):
    cat = Catalog(9, 3)
    cat.items[9] = prod(9, avail=False, title="Air Jordan 4 Bred")
    st, sent = Store(str(tmp_path / "db.sqlite")), []
    cfg = MonitorConfig("t", "shopify", "T", "https://t.invalid", watch_keywords=["jordan 4"], deep_pages=1)
    s, mk = src(cat, deep_pages=1), FileMarketProvider(str(tmp_path / "x.json"))
    run_cycle(cfg, {}, s, st, mk, lambda p: sent.append(p) or "1")       # solo página 1: el AJ4 no se ve
    assert s.watch == []
    # el AJ4 aparece una vez (p. ej. vía rotación) y queda vigilado
    st.save_snapshot("T", __import__("cookgroup.sources.shopify", fromlist=["x"]).parse_products(
        {"products": [cat.items[9]]}, store="T", base_url="https://t.invalid", currency="EUR"))
    run_cycle(cfg, {}, s, st, mk, lambda p: sent.append(p) or "1")
    assert s.watch == ["zapa-9"]
    cat.items[9]["variants"][0]["available"] = True
    cat.urls.clear()
    run_cycle(cfg, {}, s, st, mk, lambda p: sent.append(p) or "1")
    assert ("https://t.invalid/products/zapa-9.json", None) in cat.urls
    assert any("Air Jordan 4 Bred" in json.dumps(p) and "VUELVE LA EU 42" in json.dumps(p, ensure_ascii=False) for p in sent)


def test_empty_first_page_after_full_one_is_suspicious():
    cat = Catalog(15, 5)
    s = src(cat)
    s.fetch()
    cat.items.clear()
    with pytest.raises(SourceError, match="sospechosa"):
        s.fetch()


def test_domain_limiter_spaces_requests_per_domain(monkeypatch):
    monkeypatch.setattr(ratelimit, "DEFAULT_MIN_INTERVAL", 2.0)
    t = [100.0]
    waits = []
    clock = lambda: t[0]
    sleep = lambda s: waits.append(s)
    ratelimit._next_slot.clear()
    ratelimit.wait_turn("https://a.example/x", clock=clock, sleep=sleep)
    ratelimit.wait_turn("https://www.a.example/y", clock=clock, sleep=sleep)   # mismo dominio → espera 2 s
    ratelimit.wait_turn("https://b.example/z", clock=clock, sleep=sleep)       # otro dominio → sin espera
    assert waits == [2.0]
