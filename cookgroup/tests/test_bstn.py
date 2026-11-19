"""BSTN con muestras REALES del 19-nov-2026 (tests/fixtures/bstn_*_REAL_*). Las transiciones (raffle que abre,
fecha que cambia, talla que vuelve…) se fabrican modificando esas muestras y están marcadas como simuladas."""
import copy
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cookgroup.config import MonitorConfig
from cookgroup.launches import (LaunchEventType, apply_product, build_launch_digest, build_launch_embed, diff_launches,
                                madrid, run_launch_cycle)
from cookgroup.rules import PingRule, rule_matches_launch
from cookgroup.sources.bstn import BstnSource, extract_next_data, parse_listing, parse_product, parse_store_date
from cookgroup.sources.shopify import SourceError
from cookgroup.store import Store

F = Path(__file__).parent / "fixtures"
LIST = json.loads((F / "bstn_upcoming_eu_es_REAL_2026-11-19.json").read_text())
P992 = json.loads((F / "bstn_product_u992lb_REAL_2026-11-19.json").read_text())
PCAR = json.loads((F / "bstn_product_iw6306-001_REAL_2026-11-19.json").read_text())
NOW = datetime(2026, 11, 19, 13, 20, tzinfo=timezone.utc)   # momento de la captura (14:20 Madrid)


def hits(nd):
    return nd["props"]["pageProps"]["serverState"]["initialResults"]["magento2_eu_products"]["results"][0]["hits"]


def listing(nd=LIST, now=NOW):
    return parse_listing(nd, region="eu_es", now=now)


# ------------------------------------------------------------------ parsing real
def test_parse_real_listing():
    items = {i.key: i for i in listing()}
    assert len(items) == 5
    car = items["IW6306-001"]
    assert car.url == "https://www.bstn.com/eu_es/r/nike-x-carhartt-wip-air-max-goadome-low-iw6306-001-0365606"
    assert car.release_ts == 1795161600 and madrid(car.release_ts) == "vie 20 nov · 09:00"
    assert car.price_cents == 18999 and car.currency == "EUR" and car.coming_soon and not car.raffle
    tj = items["JJ7604-001"]
    assert tj.raffle and tj.raffle_active and not tj.raffle_expired and tj.url is None and tj.release_ts is None
    assert tj.raffle_url == "https://raffle.bstn.com/eu_es/nike-x-cactus-jack-x-gta-vi-air-force-1-black-jj7604-001-0368004"
    assert madrid(tj.raffle_ends_ts) == "vie 20 nov · 15:00" and tj.raffle_ends_text == "20. Nov | 15:00 CET"
    assert tj.image_url.startswith("https://img.bstn.com/card-default/nike/")


@pytest.mark.parametrize("txt,iso", [
    ("20. Nov | 15:00 CET", "2026-11-20T14:00:00+00:00"), ("20. Nov | 14:00 GMT", "2026-11-20T14:00:00+00:00"),
    ("2. Jan | 9:00 CET", "2027-01-02T08:00:00+00:00"), ("27. Nov", "2026-11-26T23:00:00+00:00"),
])
def test_store_dates_keep_origin_timezone(txt, iso):
    assert datetime.fromtimestamp(parse_store_date(txt, NOW), timezone.utc).isoformat() == iso
    assert parse_store_date("mañana", NOW) is None


def test_parse_real_product_sizes_and_equivalences():
    p = parse_product(P992)
    assert p.key == "U992LB" and p.final_cents == 22999 and p.currency == "EUR"
    s43 = next(s for s in p.sizes if s.eu == "43")
    assert (s43.uk, s43.us, s43.qty) == ("9", "9.5", 10) and s43.label() == "EU 43 (UK 9 / US 9.5)"
    assert "41" not in [s.eu for s in p.sizes]          # agotada: BSTN no la lista
    car = parse_product(PCAR)
    assert car.release_ts == 1795161600 and car.hot
    assert all(s.us is None for s in car.sizes)          # US real tiene 12 tallas frente a 14 EU: no se emparejan
    assert car.sizes[0].uk == "6"                        # "6,0-EU40" -> "6"


def test_missing_next_data_is_an_error_not_an_empty_list():
    with pytest.raises(SourceError):
        extract_next_data("<html><body>Access denied</body></html>")


def test_robots_excluded_urls_are_never_fetched():
    with pytest.raises(SourceError):
        BstnSource(["eu_es"], ["men/upcoming"])._get("https://raffle.bstn.com/eu_es/x")


# ------------------------------------------------------------------ transiciones
def states_after(items, prev=None, now=NOW):
    return diff_launches(prev or {}, items, now)


def test_first_run_is_baseline_and_digest_lists_raffle_and_week():
    ev, st = states_after(listing())
    assert ev == []
    dg = build_launch_digest(st, NOW, title="Resumen")["embeds"][0]["description"]
    assert "Raffles abiertos ahora" in dg and "CACTUS JACK" in dg and "cierra vie 20 nov · 15:00" in dg
    assert "Próximos 7 días" in dg and "vie 20 nov · 09:00 — Nike x Carhartt" in dg


def test_announced_date_changed_raffle_open_and_no_duplicates():
    _, st = states_after(listing())
    nd = copy.deepcopy(LIST)
    hs = hits(nd)
    hs.append(dict(hs[0], article_number="TEST-NEW-1", name="NUEVO SIMULADO", url="p/x-test-new-1"))
    hs[1]["release_date_row"] = 1795248000; hs[1]["release_date"] = "21. Nov | 9:00 CET"     # Carhartt cambia de fecha
    hs[3].update(raffle="Yes", raffle_is_active="Yes", raffle_url="jordan-aj3-raffle", raffleends="20. Nov | 20:00 CET")
    ev, st2 = states_after(listing(nd), st)
    kinds = sorted(e.type.value for e in ev)
    assert kinds == ["announced", "date_changed", "raffle_open"]
    dc = next(e for e in ev if e.type == LaunchEventType.DATE_CHANGED)
    assert dc.old_ts == 1795161600
    # mismo listado otra vez: sin eventos nuevos
    ev2, _ = states_after(listing(nd), st2)
    assert ev2 == []


def test_date_confirmed_from_no_date():
    nd = copy.deepcopy(LIST)
    hits(nd)[0].update(release_date_row=0, release_date="")
    _, st = states_after(listing(nd))
    ev, _ = states_after(listing(), st)
    assert [e.type for e in ev] == [LaunchEventType.DATE_CONFIRMED]


def test_disappearing_items_are_not_cancellations_and_empty_listing_is_rejected():
    _, st = states_after(listing())
    ev, st2 = states_after(listing()[:4], st)
    assert ev == [] and sum(d["present"] for d in st2.values()) == 4
    with pytest.raises(SourceError):
        states_after([], st)          # 0 de 5 → lectura sospechosa, no "todo cancelado"


def test_raffle_closing_reminder_once():
    from cookgroup.launches import timed_events
    _, st = states_after(listing())
    assert timed_events(st, NOW) == []
    near = datetime(2026, 11, 20, 12, 30, tzinfo=timezone.utc)   # 13:30 Madrid, cierra 15:00
    ev = timed_events(st, near)
    assert len(ev) == 1 and ev[0].type == LaunchEventType.RAFFLE_CLOSING
    e = build_launch_embed(ev[0], near)["embeds"][0]
    assert e["title"].startswith("⏳ El raffle cierra en 1 h 30 min")


def test_live_then_size_restock_then_real_restock_later():
    car_launch = next(i for i in listing() if i.key == "IW6306-001")
    _, st = states_after([car_launch])
    uid = car_launch.uid
    at_release = datetime.fromtimestamp(1795161600 + 40, timezone.utc)
    page = parse_product(PCAR)
    ev = apply_product(uid, st[uid], page, at_release, live_check=True)
    assert [e.type for e in ev] == [LaunchEventType.LIVE] and ev[0].delay_s == 40
    # la EU 43 se agota…
    p2 = copy.deepcopy(PCAR)
    eu = p2["props"]["pageProps"]["productDetails"]["configurable_options"][0]["values"]
    eu[:] = [v for v in eu if v["label"] != "43"]
    t2 = at_release + timedelta(hours=2)
    assert apply_product(uid, st[uid], parse_product(p2), t2, live_check=False) == []
    # …y vuelve
    t3 = at_release + timedelta(hours=5)
    ev3 = apply_product(uid, st[uid], page, t3, live_check=False)
    assert len(ev3) == 1 and ev3[0].type == LaunchEventType.SIZE_RESTOCK and [s.eu for s in ev3[0].sizes] == ["43"]
    title = build_launch_embed(ev3[0], t3)["embeds"][0]["title"]
    assert title == "🔄 Ha vuelto la EU 43 (UK 8.5) — BSTN"
    # misma ficha otra vez: sin evento
    assert apply_product(uid, st[uid], page, t3 + timedelta(minutes=5), live_check=False) == []
    # se agota y vuelve otra vez más tarde: evento NUEVO con otra clave
    apply_product(uid, st[uid], parse_product(p2), t3 + timedelta(hours=1), live_check=False)
    ev4 = apply_product(uid, st[uid], page, t3 + timedelta(hours=3), live_check=False)
    assert len(ev4) == 1 and ev4[0].key != ev3[0].key


def test_price_drop_from_product_page():
    car_launch = next(i for i in listing() if i.key == "IW6306-001")
    _, st = states_after([car_launch])
    uid = car_launch.uid
    p = copy.deepcopy(P992)
    page = parse_product(p)
    apply_product(uid, st[uid], page, NOW, live_check=True)
    p["props"]["pageProps"]["productDetails"]["price_range"]["maximum_price"]["final_price"]["value"] = 159.99
    ev = apply_product(uid, st[uid], parse_product(p), NOW + timedelta(hours=1), live_check=False)
    assert [e.type for e in ev] == [LaunchEventType.LAUNCH_PRICE_DROP]
    assert "~~229,99 €~~ → **159,99 €**" in json.dumps(build_launch_embed(ev[0], NOW)["embeds"][0]["fields"], ensure_ascii=False)


def test_embed_mobile_order_and_madrid_time():
    tj = next(i for i in listing() if i.key == "JJ7604-001")
    from cookgroup.launches import LaunchEvent
    e = build_launch_embed(LaunchEvent(LaunchEventType.RAFFLE_OPEN, tj, "k"), NOW)["embeds"][0]
    assert e["title"] == "🎟️ Raffle abierto — BSTN"
    assert e["description"].splitlines()[1] == "Inscríbete antes del cierre."
    names = [f["name"] for f in e["fields"]]
    assert names[:3] == ["Tienda", "Precio", "SKU"] and "⏳ Cierre del raffle" in names
    vals = {f["name"]: f["value"] for f in e["fields"]}
    assert "vie 20 nov · 15:00" in vals["⏳ Cierre del raffle"] and "20. Nov | 15:00 CET" in vals["⏳ Cierre del raffle"]
    assert vals["Modalidad"] == "Online · requiere cuenta de la tienda"
    assert e["url"].startswith("https://raffle.bstn.com/")


def test_ping_rule_by_size_brand_region():
    car_launch = next(i for i in listing() if i.key == "IW6306-001")
    from cookgroup.launches import LaunchEvent
    from cookgroup.sources.bstn import SizeStock
    r = PingRule.from_dict({"name": "nike43", "keywords": ["*"], "brands": ["Nike"], "sizes": ["43"], "regions": ["eu"],
                            "channel": "pings", "role_id": "1", "max_price": 200})
    ok = LaunchEvent(LaunchEventType.SIZE_RESTOCK, car_launch, "k", sizes=[SizeStock("43", 2)])
    other = LaunchEvent(LaunchEventType.SIZE_RESTOCK, car_launch, "k", sizes=[SizeStock("44", 2)])
    assert rule_matches_launch(r, ok) and not rule_matches_launch(r, other)
    assert rule_matches_launch(r, LaunchEvent(LaunchEventType.ANNOUNCED, car_launch, "k"))   # sin tallas: no filtra
    r2 = PingRule.from_dict({"name": "uk", "keywords": ["*"], "regions": ["uk"], "channel": "pings"})
    assert not rule_matches_launch(r2, ok)


# ------------------------------------------------------------------ ciclo completo con fuente falsa
class FakeBstn:
    def __init__(self, listings, products=None, fail=False):
        self.listings, self.products, self.fail, self.calls = list(listings), products or {}, fail, []

    def fetch_launches(self, now):
        if self.fail:
            raise SourceError("BSTN: acceso denegado (403); no se intenta eludir")
        return self.listings.pop(0)

    def fetch_product(self, url):
        self.calls.append(url)
        if url not in self.products:
            raise SourceError("BSTN: 404")
        return self.products[url]


def test_cycle_first_run_digest_then_events_restart_safe(tmp_path):
    db = str(tmp_path / "db.sqlite")
    cfg = MonitorConfig("bstn-eu", "bstn", "BSTN", "https://www.bstn.com")
    sent = []
    snd = {"launch": lambda p: sent.append(("launch", p)) or "1", "raffle": lambda p: sent.append(("raffle", p)) or "2",
           "restock": lambda p: sent.append(("restock", p)) or "3"}
    r1 = run_launch_cycle(cfg, {}, FakeBstn([listing()]), Store(db), snd, NOW)
    assert r1["first_run"] and r1["sent"] == 1 and "Resumen inicial" in sent[0][1]["embeds"][0]["title"]
    nd = copy.deepcopy(LIST)
    hits(nd).append(dict(hits(nd)[0], article_number="TEST-NEW-2", name="NUEVO SIMULADO 2", url="p/x-2"))
    r2 = run_launch_cycle(cfg, {}, FakeBstn([listing(nd)]), Store(db), snd, NOW + timedelta(minutes=10))
    assert r2["sent"] == 1 and sent[-1][1]["embeds"][0]["title"].startswith("📢 Nuevo lanzamiento anunciado")
    # "reinicio": nueva conexión a la misma BD y el mismo listado → nada nuevo
    r3 = run_launch_cycle(cfg, {}, FakeBstn([listing(nd)]), Store(db), snd, NOW + timedelta(minutes=20))
    assert r3["sent"] == 0
    # error de tienda → ningún evento, salud registrada
    r4 = run_launch_cycle(cfg, {}, FakeBstn([], fail=True), Store(db), snd, NOW + timedelta(minutes=30))
    assert not r4["ok"] and len(sent) == 2
    h = {row[0]: row for row in Store(db).health()}
    assert h["bstn-eu"][2] == 1 and "403" in h["bstn-eu"][3]
    # hora de salida de la Carhartt: comprueba la ficha y avisa A LA VENTA una sola vez
    car_url = "https://www.bstn.com/eu_es/r/nike-x-carhartt-wip-air-max-goadome-low-iw6306-001-0365606"
    at = datetime.fromtimestamp(1795161600 + 75, timezone.utc)
    fake = FakeBstn([listing(nd, at)], {car_url: parse_product(PCAR)})
    r5 = run_launch_cycle(cfg, {}, fake, Store(db), snd, at)
    assert car_url in fake.calls and any(p["embeds"][0]["title"].startswith("🟢 A la venta ahora") for _, p in sent)
    assert "1 min tras la hora publicada" in sent[-1][1]["embeds"][0]["footer"]["text"]
    n = len(sent)
    run_launch_cycle(cfg, {}, FakeBstn([listing(nd, at)], {car_url: parse_product(PCAR)}), Store(db), snd, at + timedelta(minutes=5))
    assert len(sent) == n


class _Resp:
    def __init__(self, status, text="", headers=None):
        self.status_code, self.text, self.headers = status, text, headers or {}
        self.content = text.encode()


class _Sess:
    def __init__(self, resp):
        self.resp, self.urls = resp, []

    def get(self, url, **kw):
        self.urls.append(url)
        assert "Mozilla" not in kw["headers"]["User-Agent"]          # identificado, sin hacerse pasar por navegador
        return self.resp


def _html(nd):
    return f'<html><script id="__NEXT_DATA__" type="application/json">{json.dumps(nd)}</script></html>'


def test_bstn_source_http_path_and_errors(monkeypatch):
    from cookgroup.sources.shopify import RateLimited
    s = _Sess(_Resp(200, _html(LIST)))
    src = BstnSource(["eu_es"], ["men/upcoming"], pause_s=0, session=s)
    items = src.fetch_launches(NOW)
    assert len(items) == 5 and s.urls == ["https://www.bstn.com/eu_es/men/upcoming"]
    s2 = _Sess(_Resp(200, _html(P992)))
    assert BstnSource(["eu_es"], [], session=s2).fetch_product("https://www.bstn.com/eu_es/p/x").key == "U992LB"
    with pytest.raises(SourceError, match="403"):
        BstnSource(["eu_es"], ["men/upcoming"], session=_Sess(_Resp(403))).fetch_launches(NOW)
    with pytest.raises(RateLimited):
        BstnSource(["eu_es"], ["men/upcoming"], session=_Sess(_Resp(429, headers={"Retry-After": "120"}))).fetch_launches(NOW)
    with pytest.raises(SourceError):
        BstnSource(["eu_es"], ["men/upcoming"], session=_Sess(_Resp(200, "<html>captcha</html>"))).fetch_launches(NOW)
