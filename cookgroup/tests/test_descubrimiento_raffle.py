"""v1.3 · descubrimiento de un raffle NUEVO en BSTN, por el mismo punto de entrada que en producción (run_launch_cycle).

Página vigilada: https://www.bstn.com/eu_es/men/upcoming (listado público; el bot NO conoce la URL de inscripción).
Capturas reales fechadas:
  · 19-nov-2026 14:20 → «Cactus Jack x GTA VI AF1 Black»: raffle ABIERTO, cierra «20. Nov | 15:00 CET»
  · 21-nov-2026 18:15 → el mismo raffle CERRADO (raffle_is_expired = Yes)
Paso 0 (SIMULACIÓN identificada): el listado del 19-nov SIN esa ficha = «antes de que BSTN la publicara».
"""
import copy
import json
from datetime import datetime, timezone
from pathlib import Path

from cookgroup.config import MonitorConfig
from cookgroup.launches import run_launch_cycle
from cookgroup.raffle_router import DeliveryPending, RaffleRouter, Target, latest, pending
from cookgroup.raffles import RaffleBoard
from cookgroup.sources.bstn import BstnSource
from cookgroup.store import Store

FIX = Path(__file__).parent / "fixtures"
D19 = json.loads((FIX / "bstn_upcoming_eu_es_REAL_2026-11-19.json").read_text(encoding="utf-8"))
D21 = json.loads((FIX / "bstn_upcoming_eu_es_REAL_2026-11-21.json").read_text(encoding="utf-8"))
T19 = datetime(2026, 11, 19, 13, 20, tzinfo=timezone.utc)
T21 = datetime(2026, 11, 21, 17, 15, tzinfo=timezone.utc)


def hits(nd):
    r = nd["props"]["pageProps"]["serverState"]["initialResults"]
    return r[next(k for k in r if k.startswith("magento2"))]["results"][0]["hits"]


class Page:
    def __init__(self, nd):
        self.nd = nd

    def get(self, url, **kw):
        body = f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(self.nd)}</script>'

        class R:
            status_code, headers, text, content = 200, {}, body, body.encode()
        return R()


class Chan:
    def __init__(self, cid, fail=False):
        self.cid, self.fail, self.sent, self.edits = cid, fail, [], []

    def send_full(self, p):
        if self.fail:
            raise RuntimeError("Discord 503 (simulado)")
        self.sent.append(p)
        return {"id": f"{self.cid}{len(self.sent):02d}", "channel_id": self.cid, "timestamp": "2026-11-19T13:20:01+00:00"}

    def send(self, p):
        return self.send_full(p)["id"]

    def edit(self, mid, p):
        self.edits.append((mid, p))


def setup(tmp_path, fail_store_channel=False):
    st = Store(str(tmp_path / "c.db"))
    ch = {"raffles_bstn": Chan("111"), "tienda_bstn": Chan("222", fail_store_channel), "raffles": Chan("333")}
    router = RaffleRouter(st, [Target("raffles_bstn", ch["raffles_bstn"]), Target("tienda_bstn", ch["tienda_bstn"], True),
                               Target("raffles", ch["raffles"])], guild_id="1572928642999255120")
    board = RaffleBoard(st, router=router)
    cfg = MonitorConfig("bstn-eu", "bstn", "BSTN", "https://www.bstn.com", channel="lanzamientos")
    cfg.regions, cfg.listings, cfg.product_checks_per_cycle = ["eu_es"], ["men/upcoming"], 0
    return st, ch, board, cfg


def cycle(cfg, st, board, nd, now):
    src = BstnSource(["eu_es"], ["men/upcoming"], session=Page(nd), pause_s=0)
    return run_launch_cycle(cfg, {}, src, st, {"launch": lambda p: "x", "raffle": lambda p: "x", "restock": lambda p: "x",
                                               "digest": lambda p: "x"}, now, raffle_board=board)


def before_publication():
    nd = copy.deepcopy(D19)                                    # SIMULACIÓN: aún no existe la ficha del raffle
    hs = hits(nd)
    hs[:] = [h for h in hs if h.get("article_number") != "JJ7604-001"]
    return nd


def test_discovery_open_then_close_from_real_captures(tmp_path):
    st, ch, board, cfg = setup(tmp_path)
    assert cycle(cfg, st, board, before_publication(), T19)["ok"]          # 1) primera lectura: catálogo en silencio
    assert all(not c.sent for c in ch.values())
    assert cycle(cfg, st, board, D19, T19)["ok"]                          # 2) DESCUBRE el raffle (URL nunca introducida)
    card = ch["raffles_bstn"].sent[0]["embeds"][0]
    f = {x["name"]: x["value"] for x in card["fields"]}
    assert "ABIERTO" in card["title"] and "CACTUS JACK" in card["title"].upper() or "CACTUS JACK" in card.get("description", "").upper()
    assert "bstn.com/eu_es/" in f["Inscripción"] and "jj7604-001" in f["Inscripción"].lower()
    assert "20/11" in f["Cierre"] and "15:00" in f["Cierre"]                # 15:00 CET = 15:00 Madrid
    assert "sí" in f["Desde España"]
    assert ch["tienda_bstn"].sent[0]["embeds"][0]["title"].startswith("RAFFLE · ")
    row = [r for r in latest(st) if r["channel"] == "raffles_bstn"][0]
    assert row["jump_url"] == "https://discord.com/channels/1572928642999255120/111/11101"
    assert cycle(cfg, st, board, D21, T21)["ok"]                          # 3) captura real del 21-nov: CERRADO
    assert any("cerrado" in (p.get("content") or "").lower() for p in ch["raffles_bstn"].sent)
    assert ch["raffles_bstn"].edits and "CERRADO" in ch["raffles_bstn"].edits[-1][1]["embeds"][0]["title"]
    n = sum(len(c.sent) for c in ch.values())
    assert cycle(cfg, st, board, D21, T21)["ok"] and sum(len(c.sent) for c in ch.values()) == n   # sin repetir


def test_discord_fails_mid_send_notice_stays_pending_and_retries_only_missing_channel(tmp_path):
    st, ch, board, cfg = setup(tmp_path, fail_store_channel=True)
    cycle(cfg, st, board, before_publication(), T19)
    assert cycle(cfg, st, board, D19, T19)["ok"]                          # el ciclo NO se da por fallido
    assert len(ch["raffles_bstn"].sent) == 1 and len(ch["raffles"].sent) == 1 and not ch["tienda_bstn"].sent
    assert [p["channel"] for p in pending(st)] == ["tienda_bstn"]         # estado consultable
    ch["tienda_bstn"].fail = False                                        # Discord vuelve
    cycle(cfg, st, board, D19, T19)
    assert len(ch["tienda_bstn"].sent) == 1                               # se envía lo que faltaba…
    assert len(ch["raffles_bstn"].sent) == 1 and len(ch["raffles"].sent) == 1   # …sin repetir en los otros
    assert pending(st) == []


def test_announced_is_not_an_open_raffle():
    from cookgroup.raffles import from_bstn
    src = BstnSource(["eu_es"], ["men/upcoming"], session=Page(D19), pause_s=0)
    items = {i.key: i for i in src.fetch_launches(T19)}
    nd = copy.deepcopy(D19)
    h = next(x for x in hits(nd) if x["article_number"] == "JJ7604-001")
    h.update(raffle_is_active="No", raffle_is_expired="No")              # anunciado, inscripción aún no abierta
    ann = {i.key: i for i in BstnSource(["eu_es"], ["men/upcoming"], session=Page(nd), pause_s=0).fetch_launches(T19)}
    ts = int(T19.timestamp())
    assert from_bstn(items["JJ7604-001"], ts).status == "abierto"
    assert from_bstn(ann["JJ7604-001"], ts).status != "abierto"
