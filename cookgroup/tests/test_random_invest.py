"""v1.6 · «Random invest» (23-nov-2026): Supreme EU por el punto de entrada del bot (run_cycle + make_source).
El objeto de la ficha es el REAL leído el 23-nov (FW26J79-BLK-S, 598 €, available=false); el resto es simulación."""
import copy
import json

from test_tallas_por_color import Site, mon

from cookgroup.market import FileMarketProvider
from cookgroup.pipeline import run_cycle
from cookgroup.runner import make_source
from cookgroup.sources.page_state import parse_supreme_page
from cookgroup.store import Store

REAL = {"name": "Supreme®/Dickies® Leather Hood", "variant": "Small", "sku": "FW26J79-BLK-S", "price": "598.00",
        "currency": "EUR", "brand": "Supreme", "category": "", "remote": False, "available": False}
BASE = "https://eu.supreme.com"


def html(o):
    return f"<html><script>window.dataLayer=[]; var p = {json.dumps(o)};</script></html>"


def test_supreme_object_means_any_size_left():
    p = parse_supreme_page(html(REAL), url=BASE + "/products/ue9bfelvscm-x1-n", store="Supreme")
    assert p.product_id == "FW26J79-BLK" and p.variants[0].title == "stock general (alguna talla)"
    assert not p.variants[0].available and p.variants[0].price_cents == 59800
    assert parse_supreme_page("<html>sin datos</html>", url="x", store="Supreme") is None


def test_supreme_new_drop_and_back_in_stock(tmp_path):
    m = mon("supreme-eu")
    pages = {"/products/ue9bfelvscm-x1-n": copy.deepcopy(REAL)}
    site = Site(BASE, m.listing_urls[0], pages, html)
    src = make_source(m)
    src.session = site
    st, mk, got = Store(tmp_path / "s.db"), FileMarketProvider(tmp_path / "m.json"), []
    send = lambda p: got.append(p) or f"m{len(got)}"                                    # noqa: E731
    run_cycle(m, {}, src, st, mk, send)
    assert got == []                                                                    # línea base: silencio
    pages["/products/ue9bfelvscm-x1-n"]["available"] = True                            # vuelve alguna talla
    run_cycle(m, {}, src, st, mk, send)
    assert len(got) == 1 and "stock general" in json.dumps(got[0], ensure_ascii=False)
    nuevo = dict(REAL, name="Supreme® Box Logo Hooded Sweatshirt", sku="FW26SW1-RED-M", price="178.00", available=True)
    pages["/products/fw26-box-logo-hooded"] = nuevo                                     # drop nuevo en /collections/new
    run_cycle(m, {}, src, st, mk, send)
    run_cycle(m, {}, src, st, mk, send)
    assert len(got) == 2 and "Box Logo" in json.dumps(got[1], ensure_ascii=False)
