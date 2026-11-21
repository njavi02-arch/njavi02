"""v1.1 · #snipes reúne los dos canales de la referencia: #snipes (Restock) y #snipes-custom (Price Change).
Muestra real de snipes.com capturada el 20-nov-2026; la bajada de precio se simula sobre esa misma página."""
from pathlib import Path

from cookgroup.config import MonitorConfig
from cookgroup.dedicated import load_dedicated
from cookgroup.market import FileMarketProvider
from cookgroup.pipeline import run_cycle
from cookgroup.sources.jsonld import JsonLdSource
from cookgroup.store import Store

REAL = (Path(__file__).parent / "fixtures" / "snipes_es_product_REAL_2026-11-20.html").read_text()
URL = "https://www.snipes.com/es-es/p/nike-air-force-1-07-blanco-1727"
LIST = "https://www.snipes.com/es-es/c/novedades"


class Site:
    def __init__(self):
        self.pages = {LIST: '<a href="/es-es/p/nike-air-force-1-07-blanco-1727">x</a>', URL: REAL}

    def get(self, url, **kw):
        body = self.pages[url.split("?")[0]]

        class R:
            status_code, headers, text, content = 200, {}, body, body.encode()
        return R()


def test_snipes_price_change_goes_to_snipes_labelled_rebaja_once(tmp_path):
    site = Site()
    src = JsonLdSource("Snipes", "https://www.snipes.com", listing_urls=[LIST], product_link_pattern="/es-es/p/", session=site)
    cfg = MonitorConfig("snipes-es", "jsonld", "Snipes", "https://www.snipes.com", interval_seconds=900, channel="sneakers",
                        country="DE", ships_es="sí")
    st, mk = Store(str(tmp_path / "db.sqlite")), FileMarketProvider(str(tmp_path / "m.json"))
    out = {"sneakers": [], "tienda_snipes": []}
    send = lambda p: out["sneakers"].append(p) or "1"                       # noqa: E731
    chans = {"tienda_snipes": lambda p: out["tienda_snipes"].append(p) or "2"}
    ded = load_dedicated("config/canales_dedicados.toml")
    run_cycle(cfg, {}, src, st, mk, send, channel_senders=chans, dedicated=ded)          # línea base: silencio
    assert out == {"sneakers": [], "tienda_snipes": []}
    site.pages[URL] = REAL.replace('"price":95.99', '"price":69.99')
    run_cycle(cfg, {"min_drop_pct": 5}, src, st, mk, send, channel_senders=chans, dedicated=ded)
    t = out["tienda_snipes"][0]["embeds"][0]
    assert t["title"].startswith("REBAJA · ")
    txt = str(t)
    assert "95,99" in txt and "69,99" in txt                                # antes → ahora
    run_cycle(cfg, {"min_drop_pct": 5}, src, st, mk, send, channel_senders=chans, dedicated=ded)   # ciclo igual: sin repetir
    assert len(out["tienda_snipes"]) == 1
