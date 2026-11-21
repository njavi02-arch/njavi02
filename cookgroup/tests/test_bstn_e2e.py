"""v1.1 — recorrido BSTN completo: reparto a #raffles-bstn / #bstn / #raffles, lista «cierran hoy», una mención,
primer arranque silencioso, reinicio sin repetir, tiempos medidos y enlace directo al mensaje."""
from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from cookgroup.members import Profile
from cookgroup.raffle_router import RaffleRouter, Target, latest, raffle_wants
from cookgroup.raffles import Raffle, RaffleBoard
from cookgroup.runner import next_wait
from cookgroup.store import Store

MAD = ZoneInfo("Europe/Madrid")
NOW = int(datetime(2026, 11, 21, 10, 0, tzinfo=MAD).timestamp())


class FakeChannel:
    def __init__(self, cid):
        self.cid, self.sent, self.edits, self.n = cid, [], [], 0

    def send_full(self, p):
        self.n += 1
        self.sent.append(p)
        return {"id": f"{self.cid}{self.n:03d}", "channel_id": self.cid, "timestamp": "2026-11-21T09:00:00.250000+00:00"}

    def send(self, p):
        return self.send_full(p)["id"]

    def edit(self, mid, p):
        self.edits.append((mid, p))


def raffle(closes=NOW + 6 * 3600, status="abierto", key="BSTN|eu_es|DZ5485-612"):
    return Raffle(key, "BSTN", "Nike Air Jordan 1 High OG", "DZ5485-612", "https://www.bstn.com/eu_es/p/x",
                  "derecho de compra", 18999, "EUR", eligible_es=True, eligible_source="región eu_es", closes_ts=closes,
                  verified_ts=NOW, status=status)


def setup(tmp_path, wants=None, clock=None):
    st = Store(str(tmp_path / "c.db"))
    chans = {"raffles_bstn": FakeChannel("111"), "tienda_bstn": FakeChannel("222"), "raffles": FakeChannel("333")}
    targets = [Target("raffles_bstn", chans["raffles_bstn"]), Target("tienda_bstn", chans["tienda_bstn"], True),
               Target("raffles", chans["raffles"])]
    today = []
    router = RaffleRouter(st, targets, guild_id="999", wants=wants, clock=clock or (lambda: 1000.0))
    board = RaffleBoard(st, router=router, edit_today=today.append, clock=clock or (lambda: 1000.0))
    return st, chans, board, today


def test_first_run_registers_silently_then_new_raffle_goes_to_three_channels(tmp_path):
    st, ch, b, today = setup(tmp_path)
    assert b.ingest(raffle(key="BSTN|eu_es|OLD"), NOW, baseline=True) == ["registrado"]
    assert sum(c.n for c in ch.values()) == 0                       # catálogo existente: sin avisos
    assert "apertura" in b.ingest(raffle(), NOW)
    assert [c.n for c in ch.values()] == [1, 1, 1]
    store_title = ch["tienda_bstn"].sent[0]["embeds"][0]["title"]
    assert store_title.startswith("RAFFLE · ") and not ch["raffles_bstn"].sent[0]["embeds"][0]["title"].startswith("RAFFLE")
    f = {x["name"]: x["value"] for x in ch["raffles_bstn"].sent[0]["embeds"][0]["fields"]}
    assert "DZ5485-612" in f["SKU"] and "bstn.com" in f["Inscripción"] and "sí" in f["Desde España"]
    assert "Madrid" in f["Cierre"] or ":" in f["Cierre"]
    assert today and "HOY (2)" in today[-1]["embeds"][0]["title"]   # cierra hoy (16:00 Madrid)


def test_one_mention_per_member_across_channels(tmp_path):
    prof = [Profile("555", "ana", families={"Raffles"}), Profile("666", "luis", families={"Pokémon-TCG"})]
    st, ch, b, _ = setup(tmp_path, wants=raffle_wants(prof))
    b.ingest(raffle(), NOW)
    contents = [c.sent[0].get("content", "") for c in ch.values()]
    assert contents[0].startswith("<@555>") and all("<@" not in x for x in contents[1:])
    assert ch["raffles_bstn"].sent[0]["allowed_mentions"] == {"parse": [], "users": ["555"]}
    assert all("666" not in x for x in contents)


def test_restart_does_not_repeat_and_deadline_change_edits_card(tmp_path):
    st, ch, b, _ = setup(tmp_path)
    b.ingest(raffle(), NOW)
    st2, ch2, b2, _ = setup(tmp_path)                                # «reinicio»: misma base de datos
    assert b2.ingest(raffle(), NOW + 60) == [] and sum(c.n for c in ch2.values()) == 0
    done = b2.ingest(raffle(closes=NOW + 9 * 3600), NOW + 120)
    assert "cambio de plazo" in done and all(c.n == 1 for c in ch2.values())
    assert ch2["raffles_bstn"].edits and ch2["raffles_bstn"].edits[0][0] == "111001"   # la ficha original se edita
    assert ch2["tienda_bstn"].edits[0][1]["embeds"][0]["title"].startswith("RAFFLE · ")
    b2.ingest(raffle(closes=NOW + 9 * 3600, status="cerrado"), NOW + 180)
    assert "CERRADO" in ch2["raffles"].edits[-1][1]["embeds"][0]["title"]


def test_latency_and_jump_link_recorded(tmp_path):
    t = iter([1000.0, 1000.0004, 1000.0008, 1000.0012])
    st, ch, b, _ = setup(tmp_path, clock=lambda: next(t))
    b.ingest(raffle(), NOW)
    rows = latest(st)
    assert len(rows) == 3
    r = [x for x in rows if x["channel"] == "raffles_bstn"][0]
    assert r["jump_url"] == "https://discord.com/channels/999/111/111001"
    assert r["detect_to_send_ms"] is not None and r["detect_to_send_ms"] < 1000
    assert r["published_ts"] is None                                 # BSTN no publica la hora de apertura: no se inventa


def test_jittered_wait_and_store_backoff():
    m = SimpleNamespace(interval_seconds=60)
    assert next_wait(m, {"ok": True}, 0, 3600, rnd=lambda: 0.0)[0] == 54
    assert next_wait(m, {"ok": True}, 0, 3600, rnd=lambda: 1.0)[0] == 66
    w, why = next_wait(m, {"ok": False, "backoff": 900}, 1, 3600, rnd=lambda: 0.5)
    assert w == 900 and "pidió esperar" in why


def test_bstn_conditional_get_reuses_body_on_304():
    from cookgroup.sources.bstn import BstnSource

    class R:
        def __init__(self, code, text="", headers=None):
            self.status_code, self.text, self.content, self.headers = code, text, text.encode(), headers or {}

    class S:
        def __init__(self):
            self.h = []

        def get(self, url, headers=None, timeout=None):
            self.h.append(headers)
            return R(200, "<html>v1</html>", {"ETag": '"a"'}) if len(self.h) == 1 else R(304)

    s = S()
    src = BstnSource(["eu_es"], ["men/upcoming"], session=s, pause_s=0)
    assert src._get("https://www.bstn.com/eu_es/men/upcoming") == "<html>v1</html>"
    assert src._get("https://www.bstn.com/eu_es/men/upcoming") == "<html>v1</html>"
    assert s.h[1]["If-None-Match"] == '"a"' and src.not_modified == 1


def test_store_channel_only_publishes_tested_signals_with_label(tmp_path):
    from cookgroup.dedicated import labelled, load_dedicated
    d = load_dedicated("config/canales_dedicados.toml")
    assert d.allows("tienda_bstn", "RAFFLE") and d.allows("tienda_footdistrict", "REBAJA")
    assert d.allows("tienda_snipes", "REBAJA") and d.allows("tienda_snipes", "RESTOCK")      # v1.1: probado (#snipes-custom)
    assert not d.allows("tienda_solebox", "REBAJA")                                          # sin captura real: no sale
    assert "tienda_flatspot" in d.by_monitor["shop:flatspot.com"]
    p = labelled({"embeds": [{"title": "VUELVE LA EU 44"}]}, "RESTOCK")
    assert p["embeds"][0]["title"] == "RESTOCK · VUELVE LA EU 44"


def test_panel_tells_bot_down_from_source_down_from_no_news():
    from cookgroup.store_panel import state_of
    now = 10_000.0
    iso = lambda t: datetime.fromtimestamp(t, ZoneInfo("UTC")).isoformat()
    assert state_of(False, ("bstn-eu", iso(now - 10), 0), 60, now, 0)[0] == "BOT PARADO"
    assert state_of(True, ("bstn-eu", iso(now - 10), 0), 60, now, 0)[0] == "AL DÍA · sin novedades"
    assert state_of(True, ("bstn-eu", iso(now - 10), 0), 60, now, 2)[0] == "AL DÍA · con avisos"
    assert state_of(True, ("bstn-eu", iso(now - 3 * 3600), 0), 60, now, 0)[0] == "FUENTE CAÍDA"
    assert state_of(True, ("bstn-eu", iso(now - 10), 4), 60, now, 0)[0] == "FUENTE CAÍDA"


def test_store_panel_renders_counts_filters_and_message_link(tmp_path):
    from cookgroup.config import load_config
    from cookgroup.store_panel import collect, render
    st, ch, b, _ = setup(tmp_path)
    b.ingest(raffle(), NOW)
    st.record_health("bstn-eu", True, items=40)
    st.set_schedule("bstn-eu", 60, 57, "normal")
    hb = tmp_path / "hb.json"
    hb.write_text('{"ts": "%s", "alive": 3, "threads": 3, "pid": 1}' % datetime.now(ZoneInfo("UTC")).isoformat())
    d = collect(st, load_config("config/monitors.toml"), heartbeat=hb, env={})
    bstn = d["stores"][0]
    assert bstn["nombre"] == "BSTN" and bstn["estado"].startswith("AL DÍA") and bstn["intervalo_s"] == 60
    assert bstn["ultimo_raffle"]["jump_url"].endswith("/111/111001")
    assert d["counts"]["descubiertas"] > 300 and d["counts"]["fuente_validada"] >= 8
    h = render(d)
    assert "Ver mensaje" in h and "http-equiv=refresh" in h and "id=fp" in h and "RAFFLE" in h and "BOT EN MARCHA" in h
