"""v1.3 · fase 2: tiendas sin Shopify auditadas el 21-nov-2026 desde el navegador del dueño (solo lectura).
Por tienda, el JSON-LD REAL de una ficha (docs/v12/capturas_tiendas_2026-11-21.jsonl) pasa por el lector JSON-LD
de producción y se comprueba: primera lectura en silencio, reposición, bajada de precio, sin repetir tras otro ciclo
y que un fallo de lectura NO convierte las tallas en «agotadas»."""
import copy
import json
from pathlib import Path

import pytest

from cookgroup.config import MonitorConfig
from cookgroup.market import FileMarketProvider
from cookgroup.pipeline import run_cycle
from cookgroup.sources.jsonld import JsonLdSource
from cookgroup.store import Store

CAP = Path(__file__).parents[1] / "docs/v12/capturas_tiendas_2026-11-21.jsonl"
PATTERN = {"www.kickz.com": "/p/", "www.43einhalb.com": "/en/p/", "www.skatedeluxe.com": "/es/p/",
           "www.basket4ballers.com": "/es/novedades/", "www.newbalance.es": "/es/pd/", "www.zalando.es": ".html", "www.zalando.fr": ".html", "www.zalando.it": ".html",
           "www.footlocker.de": "/de/product/", "www.sivasdescalzo.com": "re:^/es/p/[a-z0-9-]+$",
           "www.elcorteingles.es": r"re:^/juguetes/A\d{9}-[a-z0-9-]*pokemon[a-z0-9-]*/$", "www.footlocker.it": "/it/product/",
           "www.adidas.es": ".html", "www.footlocker.es": "/es/product/", "www.game.es": None}


def caps():
    return [r for r in map(json.loads, CAP.read_text(encoding="utf-8").splitlines()) if r.get("ld") and r["h"] in PATTERN]


def offers(ld):
    if ld["@type"] == "ProductGroup":
        return [v["offers"] for v in ld["hasVariant"]]
    return ld["offers"]


class Site:
    def __init__(self, cap):
        self.base = "https://" + cap["h"]
        self.url = self.base + cap["L"][0]
        self.ld = copy.deepcopy(cap["ld"])
        self.ld.setdefault("url", self.url)
        self.fail = False

    def get(self, url, **kw):
        if self.fail:
            import requests
            raise requests.ConnectionError("caída simulada")
        if url.split("?")[0] == self.url:
            body = f'<html><script type="application/ld+json">{json.dumps(self.ld)}</script></html>'
        else:
            body = f'<a href="{self.url.replace(self.base, "")}">x</a>'

        class R:
            status_code, headers, text, content = 200, {}, body, body.encode()
        return R()


@pytest.mark.parametrize("cap", caps(), ids=[c["h"] for c in caps()])
def test_real_jsonld_store_events(cap, tmp_path):
    site = Site(cap)
    if PATTERN[cap["h"]] is None:                       # lista de seguimiento (GAME): fichas concretas, sin listado
        src = JsonLdSource(cap["h"], site.base, watch_urls=[site.url], session=site)
    else:
        src = JsonLdSource(cap["h"], site.base, listing_urls=[site.base + cap.get("listing", "/")],
                           product_link_pattern=PATTERN[cap["h"]], session=site)
    cfg = MonitorConfig(cap["h"], "jsonld", cap["h"], site.base, channel="sneakers", skip_kids_sizes=True)
    st, mk, got = Store(tmp_path / "s.db"), FileMarketProvider(tmp_path / "m.json"), []
    send = lambda p: got.append(p) or f"m{len(got)}"                                   # noqa: E731
    of = offers(site.ld)
    of[0]["availability"] = "https://schema.org/OutOfStock"                             # partimos con una talla agotada
    run_cycle(cfg, {}, src, st, mk, send)
    assert got == [], "la primera lectura no debe publicar el catálogo"
    site.fail = True                                                                    # fallo de lectura
    res = run_cycle(cfg, {}, src, st, mk, send)
    assert not res.get("ok") and got == []
    site.fail = False
    run_cycle(cfg, {}, src, st, mk, send)                                               # vuelve a leer: sin falsas bajas
    assert got == [], "tras un fallo no debe haber avisos falsos"
    of[0]["availability"] = "https://schema.org/InStock"                                # REPOSICIÓN
    run_cycle(cfg, {}, src, st, mk, send)
    assert len(got) == 1, f"{cap['h']}: reposición no detectada"
    for o in of:                                                                        # BAJADA DE PRECIO
        o["price"] = round(float(o["price"]) * 0.8, 2)
    run_cycle(cfg, {"min_drop_pct": 5}, src, st, mk, send)
    assert len(got) == 2, f"{cap['h']}: bajada de precio no detectada"
    run_cycle(cfg, {"min_drop_pct": 5}, src, st, mk, send)                              # sin repetir
    assert len(got) == 2


@pytest.mark.parametrize("cap", [c for c in caps() if PATTERN[c["h"]]], ids=[c["h"] for c in caps() if PATTERN[c["h"]]])
def test_listing_discovers_new_product_url(cap, tmp_path):
    """v1.5 · descubrimiento: tras la línea base, una ficha NUEVA que aparece en el listado se anuncia una vez."""
    site = Site(cap)
    new_url = site.url.replace(".html", "-nuevo.html") if site.url.endswith(".html") else (site.url.rstrip("/") + "-nuevo/" if site.url.endswith("/") else site.url + "-nuevo")
    new_ld = copy.deepcopy(site.ld)
    new_ld["url"] = new_url
    for k in ("sku", "productGroupID"):
        if k in new_ld:
            new_ld[k] = str(new_ld[k]) + "-N"
    for v in new_ld.get("hasVariant", []):
        v["sku"] = str(v.get("sku", "")) + "-N"
    for o in offers(new_ld):                       # la ficha nueva sale con stock (una ficha agotada no se anuncia)
        o["availability"] = "https://schema.org/InStock"
    pages = {site.url: site.ld}

    def get(url, **kw):
        u = url.split("?")[0]
        if u in pages:
            body = f'<html><script type="application/ld+json">{json.dumps(pages[u])}</script></html>'
        else:
            body = "".join(f'<a href="{p.replace(site.base, "")}">x</a>' for p in pages)

        class R:
            status_code, headers, text, content = 200, {}, body, body.encode()
        return R()
    site.get = get
    src = JsonLdSource(cap["h"], site.base, listing_urls=[site.base + cap.get("listing", "/")],
                       product_link_pattern=PATTERN[cap["h"]], session=site)
    cfg = MonitorConfig(cap["h"], "jsonld", cap["h"], site.base, channel="sneakers", skip_kids_sizes=True)
    st, mk, got = Store(tmp_path / "s.db"), FileMarketProvider(tmp_path / "m.json"), []
    send = lambda p: got.append(p) or f"m{len(got)}"                                   # noqa: E731
    run_cycle(cfg, {}, src, st, mk, send)
    assert got == []
    pages[new_url] = new_ld                                                             # aparece en el listado
    run_cycle(cfg, {}, src, st, mk, send)
    assert len(got) == 1, f"{cap['h']}: ficha nueva no descubierta"
    assert new_url in json.dumps(got[0])
    run_cycle(cfg, {}, src, st, mk, send)
    assert len(got) == 1
