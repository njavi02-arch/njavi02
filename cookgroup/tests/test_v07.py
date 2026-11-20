"""v0.7 — entrega fiable (bandeja de salida) y beneficio solo verificado. Datos CONTROLADOS, sin webhook real."""
import copy
from datetime import date

from cookgroup.config import MonitorConfig
from cookgroup.market import FileMarketProvider
from cookgroup.models import MarketData
from cookgroup.pipeline import run_cycle
from cookgroup.profit import DEFAULT_PLATFORMS, compute_profit
from cookgroup.store import Store
from test_core import FIX, FakeSource, with_available

MCFG = MonitorConfig("t", "shopify", "TestShop", "https://shop.invalid")


class FlakyDiscord:
    """Discord falso: se puede 'tirar' y 'levantar'. Guarda lo recibido con su id."""
    def __init__(self):
        self.down, self.got, self.n = False, [], 0

    def __call__(self, payload):
        if self.down:
            raise RuntimeError("Discord 503 (simulado)")
        self.n += 1
        self.got.append(payload)
        return f"msg{self.n}"


def test_v06_bug_snapshot_before_send_no_longer_loses_alerts(tmp_path):
    """v0.6: si Discord fallaba, la instantánea ya estaba guardada → el restock se perdía para siempre."""
    db = tmp_path / "s.db"
    d = FlakyDiscord()
    src = FakeSource([FIX, with_available({1}), with_available({1}), with_available({1})])
    st = Store(db)
    run_cycle(MCFG, {}, src, st, FileMarketProvider(tmp_path / "none.json"), d)        # base
    d.down = True
    r = run_cycle(MCFG, {}, src, st, FileMarketProvider(tmp_path / "none.json"), d)    # restock + Discord caído
    assert r["sent"] == 0 and r["pending"] >= 1 and r["delivery_error"]
    st.close() if hasattr(st, "close") else None
    # reinicio del proceso con Discord aún caído
    st = Store(db)
    run_cycle(MCFG, {}, src, st, FileMarketProvider(tmp_path / "none.json"), d)
    assert d.got == []
    # Discord vuelve
    d.down = False
    r = run_cycle(MCFG, {}, src, st, FileMarketProvider(tmp_path / "none.json"), d)
    assert r["sent"] >= 1 and r["pending"] == 0
    n = len(d.got)
    # otro ciclo / otro reinicio: no hay duplicados
    st = Store(db)
    run_cycle(MCFG, {}, FakeSource([with_available({1})]), st, FileMarketProvider(tmp_path / "none.json"), d)
    assert len(d.got) == n
    assert st.last_delivery() is not None


def test_pending_delivered_even_when_source_not_modified(tmp_path):
    from cookgroup.sources.shopify import SourceError
    d = FlakyDiscord()
    st = Store(tmp_path / "s.db")
    mk = FileMarketProvider(tmp_path / "none.json")
    run_cycle(MCFG, {}, FakeSource([FIX]), st, mk, d)
    d.down = True
    run_cycle(MCFG, {}, FakeSource([with_available({1})]), st, mk, d)
    d.down = False
    r = run_cycle(MCFG, {}, FakeSource([SourceError("not-modified")]), st, mk, d)
    assert r["sent"] >= 1 and r["pending"] == 0


def _md(**kw):
    base = dict(source="export", kind="sold", price_cents=20000, sample_size=5, as_of="2026-11-18", size="42",
                condition="new", market="stockx", currency="EUR", verified_sales=True)
    base.update(kw)
    return MarketData(**base)


def test_profit_verified_only_with_full_conditions():
    pf = DEFAULT_PLATFORMS["stockx"]
    ok = compute_profit(12000, _md(), pf, size="42", ships_es="sí", require_verified=True)
    assert ok.verified and ok.net_profit_cents is not None
    assert ok.margin_pct is not None and ok.roi_pct is not None and ok.roi_pct > ok.margin_pct  # ROI s/compra > margen s/venta
    assert "5 ventas cerradas" in ok.basis
    for bad, why in [(_md(sample_size=2), "solo 2"), (_md(kind="listing", verified_sales=False), "anuncios"),
                     (_md(size="43"), "misma talla"), (_md(currency="USD"), "monedas"), (_md(market="varios"), "mercados")]:
        r = compute_profit(12000, bad, pf, size="42", ships_es="sí", require_verified=True)
        assert not r.verified and r.net_profit_cents is None and any(why in n for n in r.notes), (why, r.notes)
    r = compute_profit(12000, _md(), pf, size="42", ships_es="por confirmar", require_verified=True)
    assert not r.verified and any("España" in n for n in r.notes)
    r = compute_profit(12000, None, pf, size="42", require_verified=True)
    assert not r.verified and r.net_profit_cents is None


def test_market_sales_file_window_and_size(tmp_path):
    import json
    f = tmp_path / "m.json"
    sales = [{"sku": "HQ4307-001", "size": "42", "condition": "new", "market": "stockx", "price": p, "currency": "EUR",
              "date": d, "source": "prueba"} for p, d in [(150, "2026-11-10"), (160, "2026-11-12"), (170, "2026-11-15"),
                                                          (400, "2026-08-01")]]
    sales.append({"sku": "HQ4307-001", "size": "43", "condition": "new", "market": "stockx", "price": 999,
                  "currency": "EUR", "date": "2026-11-15", "source": "prueba"})
    f.write_text(json.dumps({"sales": sales}))
    m = FileMarketProvider(f, today=date(2026, 11, 20)).lookup("HQ4307-001", "x", "42")
    assert m.verified_sales and m.sample_size == 3 and m.price_cents == 16000 and m.size == "42"


def test_embed_says_unverified(tmp_path):
    import json
    st = Store(tmp_path / "s.db")
    d = FlakyDiscord()
    mk = FileMarketProvider(tmp_path / "none.json")
    run_cycle(MCFG, {}, FakeSource([FIX]), st, mk, d)
    run_cycle(MCFG, {}, FakeSource([with_available({1})]), st, mk, d)
    txt = json.dumps(d.got, ensure_ascii=False)
    assert "Beneficio neto estimado" not in txt


def test_probe_states_and_resume(tmp_path, monkeypatch):
    from cookgroup import diagnostics as dg
    from cookgroup.pipeline import _prepare
    from cookgroup.sources.shopify import RateLimited, SourceError, parse_products
    monkeypatch.setattr(dg, "STATE_FILE", tmp_path / "lote.json")

    class Src:
        def __init__(self, x): self.x = x
        def fetch(self):
            if isinstance(self.x, Exception): raise self.x
            return parse_products(self.x, store="T", base_url="https://t.invalid", currency="EUR")
    cases = {"util": FIX, "vacia": {"products": []}, "sin304": SourceError("not-modified"),
             "limit": RateLimited(60), "fallo": SourceError("T: HTTP 500")}
    ms = [MonitorConfig(n, "shopify", n, f"https://{n}.invalid") for n in cases]
    nomatch = MonitorConfig("nomatch", "shopify", "nomatch", "https://nm.invalid", include_vendors=["Nadie"])
    cases["nomatch"] = FIX
    rows = dg.run_probe(ms + [nomatch], lambda m: Src(cases[m.name]), _prepare, Store(tmp_path / "s.db"),
                        out_dir=str(tmp_path), printer=lambda *_: None)
    got = {r.monitor: r.status for r in rows}
    assert got == {"util": "ÚTIL", "vacia": "VACÍA", "sin304": "SIN CAMBIOS", "limit": "LIMITADA", "fallo": "FALLO",
                   "nomatch": "SIN COINCIDENCIAS"}
    assert rows[0].sample and "talla" in rows[0].sample
    assert list(tmp_path.glob("comprobacion_*.csv"))
    # reanudar: lo ya hecho no se repite
    assert dg.select(ms + [nomatch], resume=True) == []
    assert [m.name for m in dg.select(ms, match="lim")] == ["limit"]


def test_lag_and_heartbeat(tmp_path):
    from datetime import datetime, timedelta, timezone
    from cookgroup import diagnostics as dg
    now = datetime.now(timezone.utc)
    assert dg.lag_label((now - timedelta(seconds=500)).isoformat(), 600, now) == "AL DÍA"
    assert dg.lag_label((now - timedelta(hours=3)).isoformat(), 600, now).startswith("RETRASADA")
    assert dg.lag_label(None, 600) == "SIN LECTURA"
    hb = tmp_path / "hb.json"
    assert dg.process_state(hb)[0] == "PARADO"
    dg.write_heartbeat(5, 5, hb)
    assert dg.process_state(hb)[0] == "EN MARCHA"


def test_resale_size_must_be_buyable():
    """v0.8: el panel mostraba ventas de la talla 43 con tallas disponibles 40, 41 y 42,5. Prohibido."""
    import json as _j
    from cookgroup.discord import build_embed
    from cookgroup.models import Event, EventType, Opportunity
    from cookgroup.preview import _mind001
    p = _mind001()
    avail = [v.title for v in p.available_variants]
    ev = Event(EventType.NEW_PRODUCT, p, p.available_variants)
    bad = Opportunity(ev, 9000, 15500, 3440, 38.2, 71, margin_pct=22.2, verified=True, buy_size="43",
                      basis="5 ventas talla 43")
    assert "43" not in avail
    txt = _j.dumps(build_embed(ev, bad), ensure_ascii=False)
    assert "verificado" not in txt.lower() and "sin verificar" in txt
    good = Opportunity(ev, 9000, 15500, 3440, 38.2, 71, margin_pct=22.2, verified=True, buy_size=avail[0],
                       basis="5 ventas")
    txt = _j.dumps(build_embed(ev, good), ensure_ascii=False)
    assert "verificado" in txt.lower() and avail[0] in txt


def test_evaluate_picks_size_with_matching_sales(tmp_path):
    import json as _j
    from datetime import date
    from cookgroup.config import MonitorConfig
    from cookgroup.models import Event, EventType
    from cookgroup.pipeline import evaluate
    from cookgroup.preview import _mind001
    p = _mind001()
    sz = p.available_variants[-1].title
    sku = p.available_variants[-1].sku
    f = tmp_path / "m.json"
    f.write_text(_j.dumps({"sales": [{"sku": sku, "size": sz, "condition": "new", "market": "stockx", "price": 200,
                                       "currency": "EUR", "date": f"2026-11-1{i}", "source": "prueba"} for i in range(3)]}))
    opp = evaluate(Event(EventType.RESTOCK, p, p.available_variants), FileMarketProvider(f, today=date(2026, 11, 20)),
                   "stockx", Store(tmp_path / "s.db"), MonitorConfig("x", "shopify", "x", "https://x", ships_es="sí"))
    assert opp.verified and opp.buy_size == sz
