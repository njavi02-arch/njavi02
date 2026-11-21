"""v1.6 · lote 2: un miembro que entra por primera vez ve los raffles que YA estaban abiertos antes de arrancar el bot.

Punto de entrada de producción: run_launch_cycle con la captura REAL de BSTN del 19-nov-2026 14:20 (raffle Cactus Jack
x GTA VI AF1 Black abierto, cierra «20. Nov | 15:00 CET»). El bot arranca con ese raffle ya publicado:
  · no se envía como aviso (no se vuelca el histórico) → 0 mensajes en #raffles / #raffles-bstn / #bstn
  · la lista fijada «Raffles abiertos» (mensaje que se edita) sí lo muestra, con cierre en hora de Madrid y enlace."""
import copy
from datetime import datetime, timezone

from test_descubrimiento_raffle import D19, D21, T19, T21, Chan, cycle, hits, setup

from cookgroup.raffles import Raffle, RaffleBoard
from cookgroup.store import Store


def board_with_list(tmp_path):
    st, ch, _, cfg = setup(tmp_path)
    from cookgroup.raffle_router import RaffleRouter, Target
    router = RaffleRouter(st, [Target("raffles_bstn", ch["raffles_bstn"]), Target("tienda_bstn", ch["tienda_bstn"], True),
                               Target("raffles", ch["raffles"])], guild_id="1572928642999255120")
    lists = []
    board = RaffleBoard(st, router=router, edit_list=lists.append)
    return st, ch, board, cfg, lists


def test_first_start_shows_already_open_raffle_in_pinned_list_without_flooding(tmp_path):
    st, ch, board, cfg, lists = board_with_list(tmp_path)
    cycle(cfg, st, board, D19, T19)                                   # primer arranque del bot: raffle ya publicado
    assert all(not c.sent for c in ch.values()), "no se envía el histórico como avisos"
    assert lists, "la lista fijada debe actualizarse tras la línea base"
    d = lists[-1]["embeds"][0]
    assert d["title"].startswith("🎟️ Raffles abiertos (1)") and "hora de Madrid" in d["title"]
    assert "vie 20/11 · 15:00 (Madrid)" in d["description"]
    assert "raffle.bstn.com/eu_es/nike-x-cactus-jack-x-gta-vi-air-force-1-black" in d["description"]
    assert "España: sí" in d["description"]                          # región eu_es publicada por la tienda
    cycle(cfg, st, board, D21, T21)                                   # 21-nov: ya cerrado → sale de la lista
    assert "No hay raffles abiertos ahora mismo." in lists[-1]["embeds"][0]["description"]


def test_store_without_eligibility_says_spain_unconfirmed(tmp_path):
    st = Store(str(tmp_path / "s.db"))
    lists = []
    b = RaffleBoard(st, edit_list=lists.append, send=lambda p: "1")
    now = int(datetime(2026, 11, 21, 18, 0, tzinfo=timezone.utc).timestamp())
    b.ingest(Raffle("X|eu|SKU1", "Tienda X", "Zapatilla prueba", "SKU1", "https://example.org/raffle", "derecho de compra",
                    15000, "EUR", closes_ts=now + 86400, verified_ts=now), now, baseline=True)
    b.refresh_lists(now)
    assert "España sin confirmar" in lists[-1]["embeds"][0]["description"]


def test_member_sees_explicit_empty_state(tmp_path):
    st = Store(str(tmp_path / "s.db"))
    lists = []
    b = RaffleBoard(st, edit_list=lists.append)
    b.refresh_lists(int(datetime(2026, 11, 21, 18, 0, tzinfo=timezone.utc).timestamp()))
    d = lists[-1]["embeds"][0]
    assert d["title"].startswith("🎟️ Raffles abiertos (0)")
    assert "No hay raffles abiertos ahora mismo." in d["description"] and "#elige-tus-avisos" in d["description"]
