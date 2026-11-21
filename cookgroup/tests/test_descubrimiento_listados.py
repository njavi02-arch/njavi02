"""v1.6 · lote 2: el listado real descubre fichas válidas y descarta ayuda, categorías, campañas y duplicados."""
import json
from pathlib import Path

import pytest

from cookgroup.config import load_config
from cookgroup.sources.jsonld import JsonLdSource, extract_links
from cookgroup.sources.shopify import SourceError

ROOT = Path(__file__).parents[1]
ZAL = json.loads((ROOT / "tests/fixtures/zalando_es_listado_REAL_2026-11-21.json").read_text(encoding="utf-8"))
MON = {m.name: m for m in load_config(ROOT / "config/monitors.toml").monitors}


def test_zalando_es_listing_keeps_only_real_product_pages():
    base = "https://www.zalando.es"
    hrefs = (ZAL["products"] + ZAL["faq"] + ZAL["categories"]
             + [p + "?utm_source=newsletter&amp;utm_medium=x" for p in ZAL["products"][:5]]   # duplicados con seguimiento
             + [p + "#reviews" for p in ZAL["products"][:3]] + ["https://www.zalando.de" + ZAL["products"][0]])
    html = "".join(f'<a href="{h}">x</a>' for h in hrefs)
    got = extract_links(html, base_url=base, pattern=MON["zalando-es"].product_link_pattern)
    assert got == [base + p for p in ZAL["products"]]
    assert not any("/faq/" in u for u in got)
    old = extract_links(html, base_url=base, pattern=".html")      # el patrón anterior (v1.5) cogía la ayuda
    assert sum("/faq/" in u for u in old) == 12


@pytest.mark.parametrize("name,good,bad", [
    ("asics-es", "/es/es-es/gel-kayano-32/p/1011C052-404.html", "/es/es-es/mens-running-shoes/c/as10201000/"),
    ("adidas-es", "/zapatilla-sl72-og/JR1639.html", "/ayuda/devoluciones.html"),
    ("footlocker-es", "/es/product/nike-mind-001-hombre-zapatillas/314627099204.html", "/es/product/~/311700000003.html"),
    ("basket4ballers", "/es/novedades/64198-nike-kd19-aunt-pearl-io8111-600.html", "/es/6-nouveautes"),
])
def test_patterns_from_live_check(name, good, bad):
    m = MON[name]
    html = f'<a href="{good}">a</a><a href="{bad}">b</a>'
    assert extract_links(html, base_url=m.base_url, pattern=m.product_link_pattern) == [m.base_url + good]


def test_js_challenge_is_reported_not_read_as_empty_listing():
    class S:
        def get(self, url, **kw):
            class R:
                status_code, headers = 200, {}
                text = "<html><body>Powered and protected by Privacy<script>var chlgeId = ''</script></body></html>"
                content = text.encode()
            return R()
    src = JsonLdSource("New Balance", "https://www.newbalance.es", listing_urls=["https://www.newbalance.es/es/hombre/zapatillas/"],
                       product_link_pattern="/es/pd/", session=S())
    with pytest.raises(SourceError, match="anti-bot"):
        src.fetch()
