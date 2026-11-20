"""Adaptador JSON-LD (tiendas no Shopify). HTML SIMULADO con los formatos schema.org más comunes."""
import json

from cookgroup.config import MonitorConfig
from cookgroup.market import FileMarketProvider
from cookgroup.pipeline import run_cycle
from cookgroup.sources.jsonld import JsonLdSource, extract_links, parse_product_page
from cookgroup.store import Store

GROUP = {"@context": "https://schema.org", "@type": "ProductGroup", "name": "Air Jordan 4 Bred", "productGroupID": "FV5029-006",
         "brand": {"@type": "Brand", "name": "Jordan"}, "image": ["https://img.invalid/aj4.jpg"],
         "hasVariant": [{"@type": "Product", "sku": f"FV5029-006-{s}", "size": s,
                         "offers": {"@type": "Offer", "price": "215.00", "priceCurrency": "EUR",
                                    "availability": "https://schema.org/" + ("InStock" if s != "43" else "OutOfStock")}}
                        for s in ("42", "43", "44")]}
AGG = {"@type": "Product", "name": "Samba OG", "sku": "B75806", "brand": "adidas",
       "offers": {"@type": "AggregateOffer", "lowPrice": "120", "priceCurrency": "EUR",
                  "offers": [{"@type": "Offer", "name": "EU 40", "sku": "B75806-40", "price": "120", "availability": "InStock"},
                             {"@type": "Offer", "name": "EU 41", "sku": "B75806-41", "price": "120", "availability": "OutOfStock"}]}}
SIMPLE = {"@type": "Product", "name": "Gorra", "sku": "CAP1", "offers": {"price": "35,00", "priceCurrency": "GBP", "availability": "SoldOut"}}


def page(obj):
    return f'<html><head><script type="application/ld+json">{json.dumps(obj)}</script></head><body></body></html>'


def test_product_group_with_sizes():
    p = parse_product_page(page(GROUP), url="https://s.invalid/p/aj4", store="S")
    assert p.title == "Air Jordan 4 Bred" and p.vendor == "Jordan" and p.product_id == "FV5029-006"
    assert [(v.title, v.available, v.price_cents) for v in p.variants] == [("42", True, 21500), ("43", False, 21500), ("44", True, 21500)]


def test_aggregate_offer_and_simple():
    p = parse_product_page(page({"@graph": [AGG]}), url="https://s.invalid/p/samba", store="S")
    assert [(v.title, v.available) for v in p.variants] == [("EU 40", True), ("EU 41", False)]
    s = parse_product_page(page(SIMPLE), url="https://s.invalid/p/cap", store="S")
    assert s.currency == "GBP" and s.variants[0].price_cents == 3500 and not s.variants[0].available
    assert parse_product_page("<html>categoría</html>", url="u", store="S") is None


def test_listing_links_same_host_and_pattern():
    html = '<a href="/es/p/aj4?x=1">a</a><a href="https://otro.invalid/es/p/x">b</a><a href="/es/c/zapas">c</a><a href="/es/p/aj4">d</a>'
    assert extract_links(html, base_url="https://s.invalid", pattern="/es/p/") == ["https://s.invalid/es/p/aj4"]


class Site:
    def __init__(self):
        self.pages = {"https://s.invalid/es/novedades": '<a href="/es/p/aj4">x</a>', "https://s.invalid/es/p/aj4": page(GROUP)}

    def get(self, url, **kw):
        body = self.pages[url]

        class R:
            status_code, headers, text, content = 200, {}, body, body.encode()
        return R()


def test_cycle_size_comes_back_from_structured_data(tmp_path):
    site = Site()
    src = JsonLdSource("S", "https://s.invalid", listing_urls=["https://s.invalid/es/novedades"], product_link_pattern="/es/p/", session=site)
    cfg = MonitorConfig("s", "jsonld", "S", "https://s.invalid", interval_seconds=300)
    st, sent, mk = Store(str(tmp_path / "db.sqlite")), [], FileMarketProvider(str(tmp_path / "x.json"))
    run_cycle(cfg, {}, src, st, mk, lambda p: sent.append(p) or "1")       # línea base
    g = json.loads(json.dumps(GROUP))
    g["hasVariant"][1]["offers"]["availability"] = "https://schema.org/InStock"
    site.pages["https://s.invalid/es/p/aj4"] = page(g)
    run_cycle(cfg, {}, src, st, mk, lambda p: sent.append(p) or "1")
    assert [e["title"] for p in sent for e in p["embeds"]] == ["🔄 VUELVE LA EU 43 — S"]
    run_cycle(cfg, {}, src, st, mk, lambda p: sent.append(p) or "1")       # ciclo idéntico: sin duplicado
    assert len(sent) == 1


def test_antibot_page_is_an_error_not_an_empty_store():
    import pytest
    from cookgroup.sources.shopify import SourceError
    site = Site()
    site.pages["https://s.invalid/es/novedades"] = "<html><title>Just a moment...</title>cf-chl captcha</html>"
    src = JsonLdSource("S", "https://s.invalid", listing_urls=["https://s.invalid/es/novedades"], session=site)
    with pytest.raises(SourceError, match="anti-bot"):
        src.fetch()


def test_real_snipes_product_page():
    from pathlib import Path
    html = (Path(__file__).parent / "fixtures" / "snipes_es_product_REAL_2026-11-20.html").read_text()
    url = "https://www.snipes.com/es-es/p/nike-air-force-1-07-blanco-1727"
    p = parse_product_page(html, url=url, store="Snipes")
    assert p.title == "Air Force 1 '07" and p.currency == "EUR"
    assert [(v.title, v.available, v.price_cents) for v in p.variants] == [("Única", True, 9599)]   # isSimilarTo ignorado
