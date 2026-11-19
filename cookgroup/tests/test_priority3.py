"""Calendario del staff, enrutado por tramo de descuento y unificación de dominios. Datos SIMULADOS."""
import copy
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from cookgroup.config import MonitorConfig, load_config
from cookgroup.market import FileMarketProvider
from cookgroup.models import Event, EventType, Product, Variant
from cookgroup.pipeline import discount_pct, pick_discount_route, run_cycle
from cookgroup.releases import (build_digest, build_reminder, calendar_tick, digest_due, due_reminders,
                                load_calendar)
from cookgroup.sources.shopify import parse_products
from cookgroup.store import Store

MAD = ZoneInfo("Europe/Madrid")
FIX = json.loads((Path(__file__).parent / "fixtures/shopify_SIMULATED.json").read_text())

CAL = """
[calendar]
channel = "releases"
timezone = "Europe/Madrid"
reminders_minutes = [60, 1440, 10]
digest_time = "08:00"

[[release]]
id = "sim-dunk"
name = "Dunk SIMULADA"
release_at = "2030-01-10T09:00"
method = "leo"
verdict = "cop"
sku = "SIM-001"
retail_price = 119.99
stores = [{ name = "Tienda", url = "https://shop.invalid/p" }]

[[release]]
id = "sim-allday"
name = "Lanzamiento sin hora"
release_at = 2030-01-10
verdict = "drop"
"""


@pytest.fixture
def cal(tmp_path):
    f = tmp_path / "r.toml"
    f.write_text(CAL)
    return load_calendar(f)


def at(h, m=0, d=10):
    return datetime(2030, 1, d, h, m, tzinfo=MAD)


def test_load_calendar_normalises(cal):
    assert cal.reminders_minutes == [1440, 60, 10]
    dunk = next(r for r in cal.releases if r.id == "sim-dunk")
    assert dunk.method == "LEO" and dunk.release_at.tzinfo is not None
    allday = next(r for r in cal.releases if r.id == "sim-allday")
    assert allday.all_day


@pytest.mark.parametrize("bad", [
    'id = "Mal ID"', 'method = "BOT"', 'verdict = "yes"', 'stores = [{ name = "x", url = "http://inseguro" }]',
])
def test_calendar_rejects_bad_entries(tmp_path, bad):
    f = tmp_path / "r.toml"
    base = 'id = "ok-id"\nname = "x"\nrelease_at = "2030-01-01T10:00"\n'
    key = bad.split(" = ")[0]
    lines = [l for l in base.splitlines() if not l.startswith(key + " ")]
    f.write_text("[[release]]\n" + "\n".join(lines + [bad]) + "\n")
    with pytest.raises(ValueError):
        load_calendar(f)


def test_due_reminders_windows(cal):
    ids = lambda now: sorted((r.id, m) for r, m in due_reminders(cal, now))
    assert ids(at(8, 0)) == [("sim-dunk", 60)]
    assert ids(at(8, 50)) == [("sim-dunk", 10)]
    assert ids(at(9, 0, d=9)) == [("sim-dunk", 1440)]
    assert ids(at(0, 5, d=9)) == [("sim-allday", 1440)]   # todo el día: solo aviso de 1 día
    assert ids(at(8, 30)) == []                             # fuera de ventana de gracia
    assert ids(at(9, 5)) == []                              # ya ha salido


def test_reminder_and_digest_format(cal):
    dunk = next(r for r in cal.releases if r.id == "sim-dunk")
    e = build_reminder(dunk, 60)["embeds"][0]
    assert e["title"] == "⏰ En 1 hora: Dunk SIMULADA"
    vals = {f["name"]: f["value"] for f in e["fields"]}
    assert vals["Método"] == "LEO" and vals["Valoración staff"] == "🟢 Cop" and vals["SKU"] == "`SIM-001`"
    assert "<t:" in vals["Cuándo"] and vals["Precio retail"] == "119,99 €"
    d = build_digest(cal, date(2030, 1, 10))["embeds"][0]["description"]
    assert d.index("09:00") < d.index("Durante el día")
    assert build_digest(cal, date(2030, 1, 11)) is None


def test_digest_due_uses_local_time(cal):
    assert digest_due(cal, at(8, 10).astimezone(timezone.utc)) == date(2030, 1, 10)
    assert digest_due(cal, at(9, 0)) is None


def test_calendar_tick_never_repeats(cal, tmp_path):
    store, sent = Store(str(tmp_path / "db.sqlite")), []
    send = lambda p: sent.append(p) or str(len(sent))
    assert calendar_tick(cal, at(8, 0), store, send) == 2   # recordatorio 1 h + resumen del día
    assert calendar_tick(cal, at(8, 5), store, send) == 0
    assert len(sent) == 2


# --- tramos de descuento ---
def ev(t, price, old=None, cmp_at=None):
    p = Product("S", "1", "Zapa", "https://s.invalid/p", "EUR", (Variant("v", "42", price, True, None, cmp_at),))
    return Event(t, p, p.variants, old_price_cents=old, new_price_cents=price if old else None)


def test_discount_pct_and_routes():
    routes = [{"min_pct": 30, "channel": "r30"}, {"min_pct": 60, "channel": "r60"}]
    assert discount_pct(ev(EventType.PRICE_DROP, 6000, old=10000)) == 40
    assert pick_discount_route(40, routes) == "r30"
    assert pick_discount_route(65, routes) == "r60"
    assert pick_discount_route(10, routes) is None
    assert discount_pct(ev(EventType.RESTOCK, 7000, cmp_at=10000)) == 30
    assert discount_pct(ev(EventType.RESTOCK, 3582, cmp_at=3_988_333)) is None  # tachado absurdo (§2.10)


class FakeSource:
    def __init__(self, payloads):
        self.payloads = list(payloads)

    def fetch(self):
        return self.payloads.pop(0)


def avail(payload, price_factor=1.0):
    d = copy.deepcopy(payload)
    for v in d["products"][0]["variants"]:
        v["available"] = True
        v["price"] = str(round(float(v["price"]) * price_factor, 2))
    return d


def parse(d, store="TestShop"):
    return parse_products(d, store=store, base_url="https://shop.invalid", currency="EUR")


def test_cycle_copies_drop_to_tier_channel(tmp_path):
    store, main, tier = Store(str(tmp_path / "db.sqlite")), [], []
    cfg = MonitorConfig("t", "shopify", "TestShop", "https://shop.invalid")
    mk = FileMarketProvider(str(tmp_path / "none.json"))
    d = {"discount_routes": [{"min_pct": 30, "channel": "r30"}]}
    run_cycle(cfg, d, FakeSource([parse(avail(FIX))]), store, mk, lambda p: main.append(p) or "1")
    res = run_cycle(cfg, d, FakeSource([parse(avail(FIX, 0.6))]), store, mk, lambda p: main.append(p) or "2",
                    channel_senders={"r30": lambda p: tier.append(p) or "3"})
    assert res["routed"] == 1 and tier[0] == main[-1]


def test_dedupe_group_merges_two_domains(tmp_path):
    store, sent = Store(str(tmp_path / "db.sqlite")), []
    mk = FileMarketProvider(str(tmp_path / "none.json"))
    send = lambda p: sent.append(p) or "x"
    for name in ("Shop FR", "Shop EU"):
        cfg = MonitorConfig(name, "shopify", name, "https://shop.invalid", dedupe_group="shop")
        sold = copy.deepcopy(FIX)
        run_cycle(cfg, {}, FakeSource([parse(sold, name)]), store, mk, send)          # línea base
        run_cycle(cfg, {}, FakeSource([parse(avail(FIX), name)]), store, mk, send)    # restock
    restocks = [e for p in sent for e in p["embeds"] if e["title"].startswith("🔄")]
    assert len(restocks) == 1


def test_config_validates_discount_routes(tmp_path):
    f = tmp_path / "m.toml"
    f.write_text('[defaults]\ndiscount_routes = [{ min_pct = 150, channel = "x" }]\n')
    with pytest.raises(ValueError):
        load_config(f)
