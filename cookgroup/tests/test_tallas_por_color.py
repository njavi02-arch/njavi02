"""v1.6 · lote 1: tallas por COLOR en Foot Locker ES y ASICS ES.

Datos: capturas REALES del 21-nov-2026 (tests/fixtures/footlocker_es_REAL_2026-11-21.json y asics_es_REAL_…json),
envueltas en el mismo HTML que publica cada tienda (estado público incrustado en la ficha). Punto de entrada: el del
bot (load_config → runner.make_source → pipeline.run_cycle) con la configuración de producción config/monitors.toml.
SIMULACIÓN IDENTIFICADA: el «ayer» de la prueba de aceptación es la captura real con la EU 44.5 puesta como
agotada; el «hoy» es la captura real sin tocar (la 44.5 de las AF1 White-White está online)."""
import copy
import json
from pathlib import Path

import pytest

from cookgroup.config import load_config
from cookgroup.market import FileMarketProvider
from cookgroup.pipeline import run_cycle
from cookgroup.runner import make_source
from cookgroup.sources.page_state import parse_asics_state, parse_footlocker_state
from cookgroup.store import Store

ROOT = Path(__file__).parents[1]
FL = json.loads((ROOT / "tests/fixtures/footlocker_es_REAL_2026-11-21.json").read_text(encoding="utf-8"))
AS = json.loads((ROOT / "tests/fixtures/asics_es_REAL_2026-11-21.json").read_text(encoding="utf-8"))
CFG = load_config(ROOT / "config/monitors.toml")


def mon(name):
    return next(m for m in CFG.monitors if m.name == name)


def fl_html(p):
    sizes = [{"productNumber": p["sku"] + (z["suf"] or z["eu"].replace(".", "")), "size": z["eu"],
              "sizeVariants": {"eu": z["eu"], "uk": z["uk"], "us": z["us"]},
              "inventory": {"inventoryAvailable": z["any"], "warehouseInventoryAvailable": z["online"],
                            "storeInventoryAvailable": z["store"]},
              "price": {"currencyIso": "EUR", "salePrice": p["price"], "listPrice": p["price"]}} for z in p["sizes"]]
    state = {"api": {"productDetails": {"getDetails": {"data": {"model": {"name": p["model"]},
                                                               "style": {"sku": p["sku"], "color": p["color"]}, "sizes": sizes}}}}}
    return f"<html><script>window.footlocker = {{\n STATE_FROM_SERVER: {json.dumps(state)},\n}}</script></html>"


def asics_html(p):
    prod = {"masterId": p["master"], "seo": {"title": p["title"]},
            "price": {"currency": "EUR", "model": {"sales": {"value": p["price"]}, "list": {"value": p["list"]}}},
            "attributes": {"color": {"values": [{"value": p["color"], "name": p["colorName"], "selected": True, "orderable": True}]},
                           "size": {"values": [{"value": s["us"], "name": s["eu"], "orderable": s["orderable"]} for s in p["sizes"]]}}}
    return f'<html><script id="mobify-data" type="application/json">{json.dumps({"page": {"product": prod}})}</script></html>'


class Site:
    def __init__(self, base, listing, pages, render):
        self.base, self.listing, self.pages, self.render, self.fail = base, listing, pages, render, set()

    def get(self, url, **kw):
        u = url.split("?")[0]
        path = u.replace(self.base, "")
        if path in self.fail:
            import requests
            raise requests.ConnectionError("caída simulada")
        body = (self.render(self.pages[path]) if path in self.pages else
                "".join(f'<a href="{k}?utm_source=x">x</a>' for k in self.pages) if u == self.listing else "")

        class R:
            status_code, headers, text, content = 200, {}, body, body.encode()
        return R()


def fl_site(products):
    return Site("https://www.footlocker.es", mon("footlocker-es").listing_urls[0], {p["url"]: p for p in products}, fl_html)


# ------------------------------------------------------------------ adaptadores sobre datos reales
def test_footlocker_state_separates_online_store_and_sold_out():
    mind, jordan, af1 = (parse_footlocker_state(fl_html(p), url="https://www.footlocker.es" + p["url"], store="Foot Locker")
                         for p in FL["products"])
    st = {v.title: v.stock_scope for v in jordan.variants}
    assert st["EU 40"] == "online" and st["EU 44.5"] == "solo_tienda" and st["EU 47.5"] == "agotada"
    assert [v.title for v in jordan.available_variants] == ["EU 40"]          # solo lo pedible online cuenta
    assert {v.title for v in mind.variants if v.stock_scope == "agotada"} == {"EU 45", "EU 46", "EU 47.5"}
    assert mind.product_id == "314627099204" and "Work Blue" in mind.title
    v = next(v for v in mind.variants if v.title == "EU 40")
    assert v.alt_sizes == "UK 6 · US 7" and v.price_cents == 8999
    a47 = next(v for v in af1.variants if v.title == "EU 47")                 # inventoryAvailable sin canal
    assert a47.stock_scope == "desconocido" and not a47.known and not a47.available


def test_asics_state_is_per_color_with_us_and_eu():
    black, blue = (parse_asics_state(asics_html(p), url="https://www.asics.com" + p["url"], store="ASICS") for p in AS["products"])
    assert black.product_id == "1011C052.001" and blue.product_id == "1011C052.404"
    b = {v.title: v for v in black.variants}
    assert not b["EU 39"].available and b["EU 44.5"].available and b["EU 44.5"].alt_sizes == "US 10.5"
    assert {v.title for v in blue.available_variants} >= {"EU 39", "EU 46"} and black.variants[0].price_cents == 14000


# ------------------------------------------------------------------ prueba de aceptación (punto de entrada del bot)
def test_acceptance_44_5_returns_for_one_color_once_and_survives_restart(tmp_path):
    cfg = mon("footlocker-es")
    assert cfg.page_adapter == "footlocker"
    ayer = copy.deepcopy(FL["products"])
    af1 = next(p for p in ayer if p["sku"] == "314101996404")
    z = next(z for z in af1["sizes"] if z["eu"] == "44.5")
    z.update(online=False, store=False, any=False)                            # SIMULACIÓN: ayer agotada
    site, got = fl_site(ayer), []
    send = lambda p: got.append(p) or f"m{len(got)}"                          # noqa: E731
    db = tmp_path / "bot.db"

    def cycle(site):
        src = make_source(cfg)
        src.session = site
        src.products_per_cycle = 10
        return run_cycle(cfg, CFG.defaults, src, Store(db), FileMarketProvider(tmp_path / "m.json"), send)
    cycle(site)
    assert got == [], "la primera lectura es la línea base"
    site.pages[af1["url"]] = next(p for p in FL["products"] if p["sku"] == "314101996404")   # hoy: captura real
    cycle(site)
    assert len(got) == 1, got
    emb = got[0]["embeds"][0]
    blob = json.dumps(emb, ensure_ascii=False)
    assert "EU 44.5" in emb["title"].upper().replace("EU 44,5", "EU 44.5") or "EU 44.5" in blob
    assert "White-White" in blob and "314101996404.html" in blob and "/jordan-" not in blob
    assert "UK 9.5 · US 10.5" in blob and "online" in blob
    cycle(site)                                                               # mismo estado: sin repetir
    cycle(site)                                                               # «reinicio»: proceso nuevo, misma base de datos
    assert len(got) == 1


def test_store_only_size_never_announced_as_online(tmp_path):
    cfg = mon("footlocker-es")
    prods = copy.deepcopy(FL["products"])
    jordan = next(p for p in prods if p["sku"] == "314110019404")
    z = next(z for z in jordan["sizes"] if z["eu"] == "44.5")
    z.update(online=False, store=False, any=False)
    site, got = fl_site(prods), []
    send = lambda p: got.append(p) or f"m{len(got)}"                          # noqa: E731
    src = make_source(cfg)
    src.session, src.products_per_cycle = site, 10
    st, mk = Store(tmp_path / "s.db"), FileMarketProvider(tmp_path / "m.json")
    run_cycle(cfg, CFG.defaults, src, st, mk, send)
    z.update(store=True, any=True)                                            # vuelve, pero SOLO en tienda física
    run_cycle(cfg, CFG.defaults, src, st, mk, send)
    assert got == [], "una talla solo en tienda no es una reposición online"


def test_unknown_state_is_not_a_sold_out(tmp_path):
    cfg = mon("footlocker-es")
    prods = copy.deepcopy(FL["products"])
    site, got = fl_site(prods), []
    send = lambda p: got.append(p) or f"m{len(got)}"                          # noqa: E731
    src = make_source(cfg)
    src.session, src.products_per_cycle = site, 10
    st, mk = Store(tmp_path / "s.db"), FileMarketProvider(tmp_path / "m.json")
    run_cycle(cfg, CFG.defaults, src, st, mk, send)
    for p in prods:                                                           # la ficha deja de publicar el inventario
        for z in p["sizes"]:
            z.update(online=None, store=None, any=None)
    run_cycle(cfg, CFG.defaults, src, st, mk, send)
    for p in FL["products"]:                                                  # vuelve el dato real
        site.pages[p["url"]] = p
    run_cycle(cfg, CFG.defaults, src, st, mk, send)
    assert got == [], [g["embeds"][0]["title"] for g in got]


def test_asics_restock_of_one_color_through_bot_entry_point(tmp_path):
    cfg = mon("asics-es")
    assert cfg.page_adapter == "asics"
    prods = copy.deepcopy(AS["products"])
    site = Site("https://www.asics.com", cfg.listing_urls[0], {p["url"]: p for p in prods}, asics_html)
    got = []
    send = lambda p: got.append(p) or f"m{len(got)}"                          # noqa: E731
    src = make_source(cfg)
    src.session, src.products_per_cycle = site, 10
    st, mk = Store(tmp_path / "s.db"), FileMarketProvider(tmp_path / "m.json")
    run_cycle(cfg, CFG.defaults, src, st, mk, send)
    black = site.pages["/es/es-es/gel-kayano-32/p/1011C052-001.html"]
    next(s for s in black["sizes"] if s["eu"] == "46")["orderable"] = True     # SIMULACIÓN: vuelve la 46 en negro
    run_cycle(cfg, CFG.defaults, src, st, mk, send)
    assert len(got) == 1
    blob = json.dumps(got[0], ensure_ascii=False)
    assert "Black/Graphite Grey" in blob and "1011C052-001.html" in blob and "EU 46" in blob and "US 11.5" in blob


def test_color_only_source_says_so():
    from cookgroup.discord import build_embed
    from cookgroup.models import Event, EventType
    from cookgroup.sources.jsonld import parse_product_page
    cap = [json.loads(l) for l in (ROOT / "docs/v12/capturas_tiendas_2026-11-21.jsonl").read_text().splitlines()]
    de = next(c for c in cap if c["h"] == "www.footlocker.it")
    html = f'<script type="application/ld+json">{json.dumps(de["ld"])}</script>'
    p = parse_product_page(html, url="https://www.footlocker.it" + de["L"][0], store="Foot Locker")
    ev = Event(EventType.NEW_SIZE, p, (p.variants[0],))
    emb = build_embed(ev)["embeds"][0]
    assert "COLOR" in emb["title"] and "sin dato de tallas" in emb["title"]
    assert any(f["name"] == "Disponibilidad" and "por color" in f["value"] for f in emb["fields"])
