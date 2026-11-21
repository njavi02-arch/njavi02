"""Prueba visible de un raffle de BSTN (v1.1).

Simula la apertura de un raffle y lo publica UNA vez, marcado «PRUEBA», SOLO en #pruebas-bot (mismas comprobaciones que
la primera entrega real: servidor y canal correctos antes de enviar; relectura del mensaje después). Mide:
  · detección → envío      (lo que tarda el bot desde que «ve» el raffle hasta que lo manda)
  · detección → Discord    (hasta la hora que Discord pone al mensaje)
Después simula un reinicio con la misma base de datos y comprueba que NO se repite el aviso.

Sin .env (modo --simulado) hace lo mismo contra un Discord falso, para verlo funcionar en local.
"""
from __future__ import annotations

import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path

LOG = Path("docs/v11/PRUEBAS_RAFFLE.csv")


class _LocalChannel:
    """Discord falso (modo --simulado): devuelve id, canal y hora como lo haría Discord."""
    def __init__(self):
        self.sent, self.edits, self.n = [], [], 0

    def send_full(self, p):
        self.n += 1
        self.sent.append(p)
        return {"id": f"local{int(time.time() * 1000)}{self.n}", "channel_id": "pruebas-bot-local",
                "timestamp": datetime.now(timezone.utc).isoformat()}

    def edit(self, mid, p):
        self.edits.append((mid, p))


def simulated_raffle(now: int):
    from .raffles import Raffle
    return Raffle(f"PRUEBA|BSTN|{now}", "BSTN", "PRUEBA — Nike Dunk Low (raffle simulado)", "PRUEBA-0001",
                  "https://www.bstn.com/eu_es/", "derecho de compra (si te toca, pagas el precio indicado)", 11999, "EUR",
                  ["Esto es una PRUEBA: no hay raffle real"], "envío", True, "región eu_es de la tienda",
                  now + 4 * 3600, now, "abierto")


def run(store, env=os.environ, *, simulated: bool = False, http=None, log_path: Path = LOG) -> dict:
    from .raffle_router import RaffleRouter, Target, latest
    from .raffles import RaffleBoard
    target = None
    if simulated:
        chan = _LocalChannel()
    else:
        from .discord import WebhookSender
        from .real_delivery import Refused, preflight
        import requests
        http = http or requests
        url = env.get("DISCORD_WEBHOOK_PRUEBAS")
        if not url:
            raise Refused("falta DISCORD_WEBHOOK_PRUEBAS en .env (la prueba nunca usa otro canal)")
        target = preflight(url, guild_id=env.get("DISCORD_GUILD_ID"), bot_token=env.get("DISCORD_BOT_TOKEN"),
                           channel_id=env.get("DISCORD_PRUEBAS_CHANNEL_ID"), http=http)
        chan = WebhookSender(url, session=http if hasattr(http, "post") else None)
    now = int(time.time())
    r = simulated_raffle(now)
    guild = env.get("DISCORD_GUILD_ID") or (target or {}).get("guild_id")
    board = RaffleBoard(store, router=RaffleRouter(store, [Target("pruebas", chan, True)], guild_id=guild, prueba=True))
    board.ingest(r, now)
    row = latest(store, prueba=True, limit=1)[0]
    confirmed = None
    if not simulated and row["message_id"]:
        from .real_delivery import confirm
        confirmed = confirm(env["DISCORD_WEBHOOK_PRUEBAS"], row["message_id"], target, http=http)
    # reinicio: tablón y repartidor nuevos sobre la MISMA base de datos → no debe salir nada
    before = len(latest(store, prueba=True, limit=1000))
    RaffleBoard(store, router=RaffleRouter(store, [Target("pruebas", chan, True)], guild_id=guild, prueba=True)).ingest(r, now + 60)
    repeated = len(latest(store, prueba=True, limit=1000)) - before
    out = {"fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "modo": "simulado" if simulated else "Discord real",
           "message_id": row["message_id"], "enlace": row["jump_url"] or "", "deteccion_a_envio_ms": row["detect_to_send_ms"],
           "deteccion_a_discord_ms": row["detect_to_discord_ms"], "confirmado_en_pruebas_bot": confirmed,
           "repetidos_tras_reinicio": repeated}
    log_path.parent.mkdir(parents=True, exist_ok=True)
    new = not log_path.exists()
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out))
        if new:
            w.writeheader()
        w.writerow(out)
    return out
