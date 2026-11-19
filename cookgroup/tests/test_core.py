"""Tests con datos SIMULADOS (tests/fixtures/*_SIMULATED.json). No prueban integración real."""
import copy
import json
from pathlib import Path

import pytest
import requests

from cookgroup.config import MonitorConfig, load_config
from cookgroup.diff import diff_products
from cookgroup.discord import WebhookSender, build_embed
from cookgroup.market import FileMarketProvider
from cookgroup.models import EventType, MarketData
from cookgroup.pipeline import run_cycle
from cookgroup.profit import DEFAULT_PLATFORMS, compute_profit
from cookgroup.scoring import score_opportunity
from cookgroup.sources.shopify import ShopifySource, RateLimited, SourceError, parse_products, _to_cents
from cookgroup.store import Store

FIX = json.loads((Path(__file__).parent / "fixtures/shopify_SIMULATED.json").read_text())
MCFG = MonitorConfig("t", "shopify", "TestShop", "https://shop.invalid", exclude_keywords=["gift card"])


def products(payload=FIX):
    return parse_products(payload, store="TestShop", base_url="https://shop.invalid", currency="EUR")


def with_available(ids):
    d = copy.deepcopy(FIX)
    for v in d["products"][0]["variants"]:
        v["available"] = v["id"] in ids
    return d


class FakeSource:
    def __init__(self, payloads):
        self.payloads = list(payloads)

    def fetch(self):
        x = self.payloads.pop(0)
        if isinstance(x, Exception):
            raise x
        return products(x)


def test_parse_money_and_fields():
    assert _to_cents("109.99") == 10999 and _to_cents("5") == 500 and _to_cents("5,5") == 550
    p = products()[0]
    assert p.url == "https://shop.invalid/products/aj1-low-test"
    assert p.image_url and p.vendor == "Jordan" and p.tags == ("sneakers", "jordan")


def test_baseline_emits_nothing():
    assert diff_products(None, products()) == []


def test_restock_vs_new_size_vs_soldout():
    base = {p.key: p for p in products()}
    ev = diff_products(base, products(with_available({1})))
    assert [e.type for e in ev if "1001" in e.product.key] == [EventType.RESTOCK]
    one = {p.key: p for p in products(with_available({1}))}
    ev2 = diff_products(one, products(with_available({1, 2})))
    assert ev2[0].type == EventType.NEW_SIZE and [v.title for v in ev2[0].variants] == ["43"]
    ev3 = diff_products(one, products(with_available(set())))
    assert any(e.type == EventType.SOLD_OUT for e in ev3)


def test_price_drop_threshold():
    base = {p.key: p for p in products(with_available({1}))}
    d = with_available({1}); d["products"][0]["variants"][0]["price"] = "80.00"
    ev = diff_products(base, products(d), min_drop_pct=10)
    assert ev[0].type == EventType.PRICE_DROP and ev[0].old_price_cents == 10999
    d["products"][0]["variants"][0]["price"] = "105.00"
    assert diff_products(base, products(d), min_drop_pct=10) == []


def test_profit_never_invented_without_market():
    r = compute_profit(10999, None, DEFAULT_PLATFORMS["stockx"])
    assert r.net_profit_cents is None and r.notes


def test_profit_math_and_listing_warning():
    md = MarketData("manual", "listing", 20000, 3, "2026-11-18")
    r = compute_profit(10000, md, DEFAULT_PLATFORMS["stockx"])
    # 20000 - 10000 - 9% (1800) - 1000 envío = 7200
    assert r.net_profit_cents == 7200
    assert any("ANUNCIOS" in n for n in r.notes) and any("Muestra pequeña" in n for n in r.notes)


def test_score_bounds_and_no_market():
    pr = compute_profit(10000, None, DEFAULT_PLATFORMS["stockx"])
    assert score_opportunity(pr, None)[0] == 0
    sold = MarketData("manual", "sold", 25000, 30, "2026-11-18")
    s, parts = score_opportunity(compute_profit(10000, sold, DEFAULT_PLATFORMS["stockx"]), sold)
    assert 70 <= s <= 100 and set(parts) == {"margin", "confidence", "demand", "liquidity", "risk", "urgency"}
    listing = MarketData("manual", "listing", 25000, 2, "2026-11-18")
    s2, _ = score_opportunity(compute_profit(10000, listing, DEFAULT_PLATFORMS["stockx"]), listing)
    assert s2 < s  # anuncio puntúa menos que ventas reales


def test_embed_format_and_no_buttons_by_default():
    p = products(with_available({1}))[0]
    from cookgroup.models import Event
    e = Event(EventType.RESTOCK, p, p.available_variants, detected_at="2026-11-19T10:00:00+00:00")
    out = build_embed(e)
    emb = out["embeds"][0]
    assert emb["title"].startswith("RESTOCK DETECTADO") and emb["url"] == p.url
    assert "components" not in out and "components" in build_embed(e, buttons=True)
    assert any(f["value"] == "42" for f in emb["fields"])


def test_pipeline_dedupe_and_filter(tmp_path):
    store, sent = Store(str(tmp_path / "t.db")), []
    market = FileMarketProvider(tmp_path / "none.json")
    src = FakeSource([FIX, with_available({1}), with_available(set()), with_available({1})])
    send = lambda payload: sent.append(payload) or "m1"
    r1 = run_cycle(MCFG, {"cooldown_seconds": 3600}, src, store, market, send)
    assert r1["events"] == 0 and not sent                      # línea base
    r2 = run_cycle(MCFG, {"cooldown_seconds": 3600}, src, store, market, send)
    assert r2["sent"] == 1                                      # restock
    run_cycle(MCFG, {"cooldown_seconds": 3600}, src, store, market, send)  # agotado: no alerta
    r4 = run_cycle(MCFG, {"cooldown_seconds": 3600}, src, store, market, send)
    assert r4["events"] == 1 and r4["sent"] == 0 and len(sent) == 1  # mismo restock dentro de cooldown: dedupe
    assert all("Gift Card" not in json.dumps(s) for s in sent)  # filtro exclude_keywords


def test_pipeline_errors_do_not_raise(tmp_path):
    store, market = Store(str(tmp_path / "t.db")), FileMarketProvider(tmp_path / "x.json")
    r = run_cycle(MCFG, {}, FakeSource([SourceError("boom")]), store, market, lambda p: None)
    assert r["ok"] is False
    r = run_cycle(MCFG, {}, FakeSource([RateLimited(77)]), store, market, lambda p: None)
    assert r["backoff"] == 77


class Resp:
    def __init__(self, code, body=None, headers=None):
        self.status_code, self._b, self.headers, self.content = code, body, headers or {}, b"x"

    def json(self):
        return self._b

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


class Sess:
    def __init__(self, resps):
        self.resps, self.calls = list(resps), 0

    def get(self, *a, **k):
        self.calls += 1
        r = self.resps.pop(0)
        if isinstance(r, Exception):
            raise r
        return r

    post = get


def test_source_http_errors():
    mk = lambda r: ShopifySource("S", "https://s.invalid", session=Sess([r]))
    with pytest.raises(RateLimited) as e:
        mk(Resp(429, headers={"Retry-After": "30"})).fetch()
    assert e.value.retry_after == 30
    with pytest.raises(SourceError, match="no se intenta eludir"):
        mk(Resp(403)).fetch()
    with pytest.raises(SourceError, match="connection"):
        mk(requests.ConnectionError("down")).fetch()
    assert len(mk(Resp(200, FIX)).fetch()) == 2


def test_webhook_retries_on_429(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    s = Sess([Resp(429, {"retry_after": 0.1}), Resp(200, {"id": "42"})])
    assert WebhookSender("https://discord.invalid/hook", session=s).send({"content": "x"}) == "42"
    assert s.calls == 2


def test_config_rejects_aggressive_interval(tmp_path):
    f = tmp_path / "m.toml"
    f.write_text('[[monitor]]\nname="a"\ntype="shopify"\nstore="S"\nbase_url="https://x"\ninterval_seconds=5\n')
    with pytest.raises(ValueError):
        load_config(f)


def test_repo_config_loads_and_has_no_secrets():
    root = Path(__file__).parents[1]
    assert load_config(root / "config/monitors.toml").monitors
    for f in list(root.rglob("*.py")) + list(root.glob("config/*")) + [root / ".env.example"]:
        t = f.read_text()
        assert "discord.com/api/webhooks/" not in t or "REPLACE" in t, f
