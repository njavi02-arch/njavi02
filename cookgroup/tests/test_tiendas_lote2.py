"""v1.1 · lote 2 (90 tiendas europeas con envío a España): para CADA tienda, una muestra real fechada de su fuente
(tests/fixtures/muestras_shopify_REAL_2026-11-21.txt) pasa por el mismo pipeline que en producción y se comprueba:
  RESTOCK  → una talla agotada vuelve (o, si todas estaban disponibles, se agota una y vuelve)
  REBAJA   → el precio baja un 20 %
  y un ciclo idéntico no repite nada.
"""
from pathlib import Path

import pytest

from cookgroup.config import MonitorConfig
from cookgroup.market import FileMarketProvider
from cookgroup.pipeline import run_cycle
from cookgroup.sources.shopify import parse_products
from cookgroup.store import Store

FIX = Path(__file__).parent / "fixtures/muestras_shopify_REAL_2026-11-21.txt"


def samples():
    out = []
    for line in FIX.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        dom, title, updated, vs = line.split("|")
        variants = []
        for i, v in enumerate(vs.split(",")):
            t, price, cmp, av = v.split("~")
            variants.append({"id": i + 1, "title": t.strip() or "Default Title", "price": price,
                             "compare_at_price": cmp or None, "available": av == "1"})
        out.append((dom, {"products": [{"id": 1, "title": title.strip() or dom, "handle": "muestra", "vendor": dom,
                                        "product_type": "", "updated_at": updated, "tags": [], "images": [],
                                        "variants": variants}]}))
    return out


class Src:
    def __init__(self, dom, cat):
        self.dom, self.cat = dom, cat

    def fetch(self):
        return parse_products(self.cat, store=self.dom, base_url=f"https://{self.dom}", currency="EUR")


@pytest.mark.parametrize("dom,cat", samples(), ids=[s[0] for s in samples()])
def test_store_restock_and_price_drop_from_real_sample(dom, cat, tmp_path):
    cfg = MonitorConfig(f"shop:{dom}", "shopify", dom, f"https://{dom}", channel="sneakers", ships_es="sí",
                        skip_kids_sizes=True)                               # como en producción (tiendas en bloque)
    st, mk, got = Store(tmp_path / "s.db"), FileMarketProvider(tmp_path / "m.json"), []
    send = lambda p: got.append(p) or f"m{len(got)}"                       # noqa: E731
    src = Src(dom, cat)
    from cookgroup.normalize import clean_variants, validate_product
    if (bad := validate_product(src.fetch()[0])):
        pytest.skip(f"{dom}: el producto de la muestra no es publicable ({', '.join(bad)}); tienda pendiente de otra muestra")
    keep = {v.variant_id for v in clean_variants(src.fetch()[0], skip_kids=cfg.skip_kids_sizes).variants}
    vs = [v for v in src.cat["products"][0]["variants"] if str(v["id"]) in keep]   # las que el bot publicaría
    if not vs:
        pytest.skip(f"{dom}: el producto de la muestra no es publicable (solo tallas de niño o sin variantes); tienda pendiente de otra muestra")
    if all(v["available"] for v in vs):                                    # todas disponibles: se agota una antes
        vs[0]["available"] = False
    run_cycle(cfg, {}, src, st, mk, send)                                   # línea base: silencio
    assert got == []
    off = next(v for v in vs if not v["available"])
    off["available"] = True
    run_cycle(cfg, {}, src, st, mk, send)
    assert len(got) == 1, f"{dom}: restock no detectado"
    for v in src.cat["products"][0]["variants"]:
        v["price"] = f"{float(v['price']) * 0.8:.2f}"
    run_cycle(cfg, {"min_drop_pct": 5}, src, st, mk, send)
    titles = " ".join(e.get("title", "") for p in got for e in p.get("embeds", []))
    assert len(got) >= 2 and ("BAJA" in titles.upper() or "REBAJA" in titles.upper() or "PRECIO" in titles.upper()), titles
    n = len(got)
    run_cycle(cfg, {"min_drop_pct": 5}, src, st, mk, send)                  # ciclo idéntico: sin repetir
    assert len(got) == n
