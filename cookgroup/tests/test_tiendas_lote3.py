"""v1.6 · lote 3: ASOS ES y About You ES con capturas REALES del 21-nov-2026, por el punto de entrada del bot."""
import copy
import json
from pathlib import Path

from test_tallas_por_color import CFG, Site, mon

from cookgroup.market import FileMarketProvider
from cookgroup.pipeline import run_cycle
from cookgroup.runner import make_source
from cookgroup.sources.jsonld import parse_product_page
from cookgroup.store import Store

FIX = Path(__file__).parent / "fixtures"
ASOS = json.loads((FIX / "asos_es_REAL_2026-11-21.json").read_text(encoding="utf-8"))
AY = json.loads((FIX / "aboutyou_es_REAL_2026-11-21.json").read_text(encoding="utf-8"))


def asos_html(d):
    stock = [{"productId": d["productId"], "productPrice": {"current": {"value": d["base"]}, "currency": d["currency"]},
              "variants": [{"id": v["id"], "isInStock": v["inStock"], "isLowInStock": False,
                            "price": {"current": {"value": v["price"]}}} for v in d["variants"]]}]
    sizes = ",".join(f'{{"variantId":{v["id"]},"size":"{v["size"]}","brandSize":"{v["size"]}","hasIngredients":false,'
                     f'"colour":"{d["colour"]}","colourWayId":{d["colourWayId"]},"isPrimary":true}}' for v in d["variants"])
    lit = json.dumps(stock).replace('"', '\\"')
    ld = json.dumps({"@context": "https://schema.org", "@graph": [{"@type": "ProductGroup", "name": d["name"], "hasVariant": [{"url": "x"}]}]})
    return (f'<script type="application/ld+json">{ld}</script><script>window.asos.pdp.config.stockPriceResponse = \'{lit}\';'
            f'</script><script>window.asos.pdp.config.product = {{"variants":[{sizes}]}};</script>')


def ay_html(d):
    own = [{"@type": "Product", "color": d["color"], "size": z["size"],
            "offers": {"@type": "Offer", "price": z.get("price", d["price"]), "priceCurrency": "EUR",
                       "availability": z.get("av", "https://schema.org/InStock"), "sku": f'{d["group"]}-{z["size"]}'}} for z in d["sizes"]]
    other = [{"@type": "Product", "name": "otro color"} for _ in range(d["other_color_variants_without_offer"])]
    ld = {"@context": "https://schema.org", "@type": "ProductGroup", "productGroupID": d["group"], "name": d["name"],
          "brand": {"name": d["brand"]}, "hasVariant": own + other}
    return f'<script type="application/ld+json">{json.dumps(ld)}</script>'


def run(cfg, site, tmp_path):
    got = []
    src = make_source(cfg)
    src.session, src.products_per_cycle = site, 10
    st, mk = Store(tmp_path / "s.db"), FileMarketProvider(tmp_path / "m.json")
    return (lambda: run_cycle(cfg, CFG.defaults, src, st, mk, lambda p: got.append(p) or "1")), got


def test_asos_single_size_restock_and_per_size_price(tmp_path):
    cfg = mon("asos-es")
    d = copy.deepcopy(ASOS)
    site = Site("https://www.asos.com", cfg.listing_urls[0].split("?")[0], {d["url"]: d}, asos_html)
    cycle, got = run(cfg, site, tmp_path)
    cycle()
    assert got == []
    next(v for v in d["variants"] if v["size"] == "EU 49 1/3")["inStock"] = True    # SIMULACIÓN: vuelve la 49 1/3
    cycle()
    assert len(got) == 1
    blob = json.dumps(got[0], ensure_ascii=False)
    assert "EU 49 1/3" in blob and "prd/205774480" in blob and "Handball Spezial" in blob
    cycle()
    assert len(got) == 1


def test_asos_real_capture_has_two_prices():
    p = __import__("cookgroup.sources.page_state", fromlist=["x"]).parse_asos_state(
        asos_html(ASOS), url="https://www.asos.com" + ASOS["url"], store="ASOS")
    assert {v.price_cents for v in p.variants} == {8999, 11000}
    assert [v.title for v in p.variants if not v.available] == ["EU 49 1/3"]


def test_aboutyou_color_pages_do_not_collide_and_restock_once(tmp_path):
    d = copy.deepcopy(AY)
    url2 = d["url"].replace("32191359", "32191360")                         # SIMULACIÓN: otra ficha de color, mismo grupo
    d2 = copy.deepcopy(d)
    d2["color"] = "blanco"
    p1 = parse_product_page(ay_html(d), url="https://www.aboutyou.es" + d["url"], store="About You")
    p2 = parse_product_page(ay_html(d2), url="https://www.aboutyou.es" + url2, store="About You")
    assert p1.product_id != p2.product_id and len(p1.variants) == 12          # solo las tallas del color de la ficha
    cfg = mon("aboutyou-es")
    site = Site("https://www.aboutyou.es", cfg.listing_urls[0], {d["url"]: d, url2: d2}, ay_html)
    cycle, got = run(cfg, site, tmp_path)
    d["sizes"][0]["av"] = "https://schema.org/OutOfStock"
    cycle()
    assert got == []
    del d["sizes"][0]["av"]                                                   # vuelve la 35,5 en rosa
    cycle()
    assert len(got) == 1 and "35,5" in json.dumps(got[0], ensure_ascii=False)
    cycle()
    assert len(got) == 1


TRU = json.loads((FIX / "toysrus_es_REAL_2026-11-21.json").read_text(encoding="utf-8"))


def tru_html(d):
    return (f'<h1 class="name">{d["name"]}</h1><meta itemprop="price" content="{d["price"]}"/>'
            f'<meta itemprop="priceCurrency" content="EUR"/><input type="hidden" id="stockLevelStatus" name="stockLevelStatus" '
            f'value="{d["stock"]}"/>')


def test_toysrus_hybris_stock_and_price_drop(tmp_path):
    cfg = mon("toysrus-pokemon")
    prods = copy.deepcopy(TRU["products"])
    site = Site("https://www.toysrus.es", cfg.listing_urls[0], {p["url"]: p for p in prods}, tru_html)
    cycle, got = run(cfg, site, tmp_path)
    prods[0]["stock"] = "outOfStock"                                          # SIMULACIÓN (valor estándar de Hybris)
    cycle()
    assert got == []
    prods[0]["stock"] = "inStock"
    cycle()
    assert len(got) == 1 and "Eevee" in json.dumps(got[0], ensure_ascii=False)
    prods[1]["price"] = 149.99                                                # SIMULACIÓN: bajada de precio
    cycle()
    assert len(got) == 2
    prods[2]["stock"] = "algoRaro"                                            # valor no reconocido → desconocido
    cycle()
    assert len(got) == 2
