"""Primera entrega REAL a Discord, con comprobaciones antes y después (v0.9).

Reglas:
  · SOLO usa DISCORD_WEBHOOK_PRUEBAS. Nunca recurre a DISCORD_WEBHOOK_DEFAULT ni a otro canal.
  · Antes de enviar consulta el webhook en Discord (GET, sin publicar nada) y exige:
      - que pertenezca a tu servidor (DISCORD_GUILD_ID), si lo has configurado;
      - que el canal se llame «pruebas-bot» (con el token del bot se lee el nombre real del canal) o, sin bot,
        que el webhook se llame «cookgroup · pruebas-bot» (lo crea así INSTALAR_SERVIDOR) o coincida
        DISCORD_PRUEBAS_CHANNEL_ID.
  · Después de enviar vuelve a leer el mensaje por su ID y confirma canal y servidor. Solo entonces se registra como
    «entrega real confirmada» (docs/v09/ENTREGAS_REALES.csv y tabla real_deliveries).
"""
from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

API = "https://discord.com/api/v10"
TEST_CHANNEL = "pruebas-bot"


class Refused(Exception):
    pass


def _webhook_parts(url: str) -> tuple[str, str]:
    p = url.rstrip("/").split("/")
    return p[-2], p[-1]


def preflight(url: str, *, guild_id: str | None, bot_token: str | None, channel_id: str | None,
              http=requests) -> dict:
    """Lee el webhook (no publica nada) y comprueba servidor y canal. Devuelve {guild_id, channel_id, channel_name}."""
    r = http.get(url, timeout=15)
    if r.status_code != 200:
        raise Refused(f"el webhook no responde correctamente (HTTP {r.status_code})")
    w = r.json()
    if guild_id and str(w.get("guild_id")) != str(guild_id):
        raise Refused(f"el webhook pertenece a OTRO servidor ({w.get('guild_id')}), no a DISCORD_GUILD_ID")
    name = None
    if bot_token:
        c = http.get(f"{API}/channels/{w['channel_id']}", headers={"Authorization": f"Bot {bot_token}"}, timeout=15)
        if c.status_code == 200:
            name = c.json().get("name")
    if name is not None:
        if name != TEST_CHANNEL:
            raise Refused(f"el webhook publica en #{name}, no en #{TEST_CHANNEL}")
    elif channel_id:
        if str(w.get("channel_id")) != str(channel_id):
            raise Refused("el canal del webhook no coincide con DISCORD_PRUEBAS_CHANNEL_ID")
    elif TEST_CHANNEL not in (w.get("name") or ""):
        raise Refused("no se puede confirmar que el canal sea #pruebas-bot: añade DISCORD_BOT_TOKEN o "
                      "DISCORD_PRUEBAS_CHANNEL_ID en .env (o usa el webhook que crea INSTALAR_SERVIDOR)")
    return {"guild_id": str(w.get("guild_id")), "channel_id": str(w.get("channel_id")), "channel_name": name or TEST_CHANNEL}


def confirm(url: str, message_id: str, expected: dict, http=requests) -> bool:
    wid, tok = _webhook_parts(url)
    r = http.get(f"{API}/webhooks/{wid}/{tok}/messages/{message_id}", timeout=15)
    return r.status_code == 200 and str(r.json().get("channel_id")) == expected["channel_id"]


def send_first_real(env=os.environ, *, http=requests, sender=None, store=None,
                    log_path: Path = Path("docs/v09/ENTREGAS_REALES.csv")) -> dict:
    url = env.get("DISCORD_WEBHOOK_PRUEBAS")
    if not url:
        raise Refused("falta DISCORD_WEBHOOK_PRUEBAS en .env (no se usa el webhook general a propósito)")
    target = preflight(url, guild_id=env.get("DISCORD_GUILD_ID"), bot_token=env.get("DISCORD_BOT_TOKEN"),
                       channel_id=env.get("DISCORD_PRUEBAS_CHANNEL_ID"), http=http)
    from .preview import test_payload
    if sender is None:
        from .discord import WebhookSender
        sender = WebhookSender(url, session=http if hasattr(http, "post") else None).send
    payload = test_payload()
    payload["allowed_mentions"] = {"parse": []}          # la prueba no menciona a nadie
    mid = sender(payload)
    ok = bool(mid) and confirm(url, mid, target, http=http)
    row = {"fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "message_id": mid,
           "guild_id": target["guild_id"], "channel_id": target["channel_id"], "canal": target["channel_name"],
           "estado": "entrega real confirmada" if ok else "enviado sin confirmar"}
    log_path.parent.mkdir(parents=True, exist_ok=True)
    new = not log_path.exists()
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)
    if store is not None and ok:
        store.record_alert(f"real|{mid}", "prueba-real", "PRUEBA", "-", mid)
    return row
