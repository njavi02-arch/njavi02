"""Prioridad 2: normalización, price error validado, pings por regla y fuente RSS.
Datos SIMULADOS; los casos negativos reproducen fallos observados en la referencia (docs/REFERENCE_AUDIT.md)."""
import copy
import json
from pathlib import Path

import pytest

from cookgroup.config import MonitorConfig, load_config
from cookgroup.discord import build_embed
from cookgroup.market import FileMarketProvider
from cookgroup.models import Event, EventType, Product, Variant
from cookgroup.normalize import clean_variants, is_kids_size, normalize_size, validate_product
from cookgroup.pipeline import run_cycle
from cookgroup.price_error import check_price_error
from cookgroup.rules import PingRule, build_ping, rule_matches
from cookgroup.sources.rss import parse_feed, parse_price_cents
from cookgroup.sources.shopify import parse_products
from cookgroup.store import Store

FIX = json.loads((Path(__file__).parent / "fixtures/shopify_SIMULATED.json").read_text())
RSS = (Path(__file__).parent / "fixtures/rss_SIMULATED.xml").read_text()


def prod(title="Nike Dunk Low", price=10000, sizes=("42",), store="S", url="https://s.invalid/p", sku="DD1391-100"):
    vs = tuple(Variant(str(i), s, price, True, sku) for i, s in enumerate(sizes))
    return Product(store, "1", title, url, "EUR", vs)


# --- normalización (§2.4, §2.5) ---
@pytest.mark.parametrize("raw,exp", [
    ("42", "42"), ("42,5", "42.5"), ("EU 44", "44"), ("36 2/3", "36 2/3"), ("36⅔", "36 2/3"),
    ("uk 6", "UK 6"), ("US 9.5", "US 9.5"), ("4Y", "4Y"), ("42 / Black", "42"), ("M", "M"),
    ("Default Title", "Única"), ("375", None), ("36666", None), ("", None), ("99", None),
])
def test_normalize_size(raw, exp):
    assert normalize_size(raw) == exp


def test_kids_sizes_filtered_only_when_requested():
    p = prod(sizes=("4Y", "5.5Y", "42"))
    assert is_kids_size("5.5Y")
    assert [v.title for v in clean_variants(p).variants] == ["4Y", "5.5Y", "42"]
    assert [v.title for v in clean_variants(p, skip_kids=True).variants] == ["42"]


def test_unparseable_sizes_are_dropped_not_guessed():
    p = clean_variants(prod(sizes=("375", "36666", "38")))
    assert [v.title for v in p.variants] == ["38"]


# --- validación (§2.6, §2.9) ---
def test_validation_rejects_empty_and_numeric_titles():
    assert "sin título" in validate_product(prod(title="(Sin título)"))
    assert "título solo numérico/código" in validate_product(prod(title="1913086250"))
    assert "precio desconocido o 0" in validate_product(prod(price=0))
    assert validate_product(prod(price=0), allow_unknown_price=True) == []
    assert "sin URL válida" in validate_product(prod(url=""))
    assert validate_product(prod()) == []


# --- price error (§2.10) ---
def test_price_error_needs_history():
    c = check_price_error(1000, [10000, 10000])
    assert not c.is_error and "Histórico insuficiente" in c.notes[0]


def test_price_error_uses_own_median_and_ignores_absurd_compare_at():
    c = check_price_error(3582, [9000, 9500, 10000, 10000, 11000], compare_at_cents=3_988_333)
    assert c.is_error and c.reference_cents == 10000 and c.drop_pct == pytest.approx(64.2)
    assert any("no creíble" in n for n in c.notes)


def test_normal_drop_is_not_price_error():
    assert not check_price_error(8000, [10000] * 6).is_error


# --- reglas de ping (§2.13) ---
def ev_for(p, t=EventType.RESTOCK):
    return Event(t, p, p.variants, detected_at="2026-11-19T12:00:00+00:00")


def test_ping_rule_keywords_price_and_exclusions():
    r = PingRule.from_dict({"name": "dunk", "keywords": ["dunk", "low"], "max_price": 120,
                            "channel": "pings", "role_id": "123", "exclude_keywords": ["gs"]})
    assert rule_matches(r, ev_for(prod()))
    assert not rule_matches(r, ev_for(prod(price=15000)))
    assert not rule_matches(r, ev_for(prod(title="Nike Dunk Low GS")))
    assert not rule_matches(r, ev_for(prod(title="Nike Dunk High")))
    assert not rule_matches(r, ev_for(prod(), EventType.SOLD_OUT))


def test_ping_payload_only_mentions_its_role():
    r = PingRule.from_dict({"name": "x", "keywords": ["dunk"], "channel": "pings", "role_id": 555})
    payload = build_ping(r, ev_for(prod()), build_embed(ev_for(prod())))
    assert payload["content"].startswith("<@&555>")
    assert payload["allowed_mentions"] == {"parse": [], "roles": ["555"]}
    assert payload["embeds"]


def test_ping_rule_rejects_bad_role():
    with pytest.raises(ValueError):
        PingRule.from_dict({"name": "x", "keywords": ["a"], "channel": "c", "role_id": "@everyone"})


# --- RSS (§2.9) ---
def test_parse_price_cents():
    assert parse_price_cents("Zapatillas por 49,99€") == 4999
    assert parse_price_cents("Portátil 1.299,99 €") == 129999
    assert parse_price_cents("€ 12.5 envío") == 1250
    assert parse_price_cents("sin precio") == 0


def test_parse_feed_rss_skips_untitled_entries():
    ps = parse_feed(RSS, store="FeedSim")
    assert [p.title for p in ps] == ["Mando DualSense blanco por 49,99€", "Auriculares inalámbricos"]
    assert ps[0].variants[0].price_cents == 4999 and ps[0].image_url
    assert ps[1].variants[0].price_cents == 0


class FakeSource:
    def __init__(self, payloads):
        self.payloads = list(payloads)

    def fetch(self):
        return self.payloads.pop(0)


def test_rss_cycle_publishes_new_deals_and_drops_invalid(tmp_path):
    store, sent = Store(str(tmp_path / "db.sqlite")), []
    cfg = MonitorConfig("feed", "rss", "FeedSim", "https://feed.invalid/rss", allow_unknown_price=True)
    first = parse_feed(RSS, store="FeedSim")[:1]
    both = parse_feed(RSS, store="FeedSim") + [prod(title="", store="FeedSim")]
    mk = FileMarketProvider(str(tmp_path / "none.json"))
    run_cycle(cfg, {}, FakeSource([first]), store, mk, lambda p: sent.append(p) or "1")
    res = run_cycle(cfg, {}, FakeSource([both]), store, mk, lambda p: sent.append(p) or "2")
    assert res["sent"] == 1 and res["dropped"] == 1
    assert "Auriculares" in sent[0]["embeds"][0]["description"]


# --- integración pipeline: price error + ping ---
def test_cycle_upgrades_drop_to_price_error_and_pings(tmp_path):
    store, sent, pinged = Store(str(tmp_path / "db.sqlite")), [], []
    base = copy.deepcopy(FIX)
    for v in base["products"][0]["variants"]:
        v["available"] = True
    cfg = MonitorConfig("t", "shopify", "TestShop", "https://shop.invalid")
    mk = FileMarketProvider(str(tmp_path / "none.json"))
    title = parse_products(base, store="TestShop", base_url="https://shop.invalid", currency="EUR")[0].title
    rule = PingRule.from_dict({"name": "pe", "keywords": [title.split()[0]], "channel": "pings",
                               "role_id": "1", "event_types": ["price_error"]})
    defaults = {"price_error_min_obs": 3, "price_error_pct": 50}
    for _ in range(4):  # construye histórico propio
        run_cycle(cfg, defaults, FakeSource([parse_products(base, store="TestShop", base_url="https://shop.invalid", currency="EUR")]),
                  store, mk, lambda p: sent.append(p) or "x")
    cheap = copy.deepcopy(base)
    for v in cheap["products"][0]["variants"]:
        v["price"] = str(round(float(v["price"]) * 0.3, 2))
    res = run_cycle(cfg, defaults, FakeSource([parse_products(cheap, store="TestShop", base_url="https://shop.invalid", currency="EUR")]),
                    store, mk, lambda p: sent.append(p) or "y", ping_rules=[rule],
                    ping_senders={"pings": lambda p: pinged.append(p) or "z"})
    titles = [e["title"] for p in sent for e in p["embeds"]]
    assert any(t.startswith("POSIBLE PRICE ERROR") for t in titles)
    assert res["pings"] == 1 and pinged[0]["content"].startswith("<@&1>")


def test_config_loads_ping_rules_and_rejects_fast_rss(tmp_path):
    f = tmp_path / "m.toml"
    f.write_text('[defaults]\n[[monitor]]\nname="r"\ntype="rss"\nstore="R"\nbase_url="https://x.invalid"\ninterval_seconds=60\n')
    with pytest.raises(ValueError):
        load_config(f)
    f.write_text('[defaults]\n[[ping_rule]]\nname="a"\nkeywords=["dunk"]\nmax_price=100\nchannel="pings"\nrole_id="1"\n')
    assert load_config(f).ping_rules[0].max_price_cents == 10000
