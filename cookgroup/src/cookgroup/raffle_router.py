"""Reparto de raffles a varios canales (v1.1): #raffles-<tienda>, #<tienda> (etiqueta RAFFLE) y el agregado #raffles.

· Cada canal recibe su ficha; los avisos posteriores (cambio de plazo, cierre) EDITAN esa ficha y además dejan una línea
  corta, para que el móvil reciba la notificación.
· Mención: a cada miembro se le menciona UNA vez por raffle y evento en todo el servidor (registro `mentions`).
· Tiempos: se guardan por mensaje la hora de publicación de la tienda (solo si la fuente la da), la de detección, la de
  envío y la que marca Discord, más el enlace directo al mensaje.
"""
from __future__ import annotations

import copy
import time
from dataclasses import dataclass
from datetime import datetime

from .store import now_iso

LABEL = "RAFFLE"
SCHEMA = """CREATE TABLE IF NOT EXISTS delivery_times (
  id INTEGER PRIMARY KEY AUTOINCREMENT, raffle_key TEXT, kind TEXT, channel TEXT, store TEXT,
  published_ts REAL, detected_ts REAL, sent_ts REAL, discord_ts REAL,
  message_id TEXT, channel_id TEXT, guild_id TEXT, prueba INTEGER DEFAULT 0)"""


@dataclass
class Target:
    channel: str                  # nombre lógico: raffles_bstn, tienda_bstn, raffles, pruebas
    sender: object                # WebhookSender (send_full / edit) o un doble de prueba
    labelled: bool = False        # True en el canal de la tienda: el título lleva «RAFFLE ·»


def keyname(n: str) -> str:
    """Nombre ASCII para claves de .env: «Sivasdescalzo España» → sivasdescalzo_espana."""
    import re
    import unicodedata
    a = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", a.lower()).strip("_")


def jump_url(guild_id, channel_id, message_id) -> str | None:
    if guild_id and channel_id and message_id:
        return f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
    return None


def _discord_ts(m: dict) -> float | None:
    t = m.get("timestamp") if isinstance(m, dict) else None
    try:
        return datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp() if t else None
    except ValueError:
        return None


def _label(payload: dict, prefix: str) -> dict:
    p = copy.deepcopy(payload)
    for e in p.get("embeds", []):
        if e.get("title"):
            e["title"] = f"{prefix} · {e['title']}"
    if p.get("content") and not p.get("embeds"):
        p["content"] = f"**{prefix}** · {p['content']}"
    return p


class RaffleRouter:
    def __init__(self, store, targets: list[Target], *, guild_id: str | None = None, wants=None, prueba: bool = False,
                 clock=time.time):
        """wants(raffle) -> ids de Discord de los miembros a mencionar (filtros personales). None = no se menciona a nadie."""
        self.s, self.targets, self.guild, self.wants, self.prueba, self.clock = store, targets, guild_id, wants, prueba, clock
        self.detected_ts: float | None = None
        with store._lock:
            store.db.execute(SCHEMA)
            store.db.commit()

    # ------------------------------------------------------------------ envío
    def emit(self, kind: str, r, payload: dict) -> list[dict]:
        detected = self.detected_ts or self.clock()
        users = list(self.wants(r)) if (self.wants and kind in ("apertura", "recordatorio")) else []
        out = []
        for t in self.targets:
            p = _label(payload, LABEL) if t.labelled else copy.deepcopy(payload)
            if self.prueba:
                p = _label(p, "PRUEBA")
            mine = [u for u in users if self.s.claim_mention(u, f"raffle|{r.key}|{kind}", t.channel)]
            if mine:
                p["content"] = " ".join(f"<@{u}>" for u in mine) + ((" " + p["content"]) if p.get("content") else "")
                p["allowed_mentions"] = {"parse": [], "users": mine}
            else:
                p["allowed_mentions"] = {"parse": []}
            old = self._card(r.key, t.channel) if kind in ("cambio de plazo", "cierre", "cierre por plazo") else None
            sent = self.clock()
            m = t.sender.send_full(p) or {}
            if old and kind != "recordatorio" and getattr(r, "_card_payload", None):
                try:   # la ficha original refleja el nuevo plazo / el cierre
                    t.sender.edit(old, _label(r._card_payload, LABEL) if t.labelled else r._card_payload)
                except Exception:   # noqa: BLE001 — editar es una mejora; el aviso nuevo ya ha salido
                    pass
            row = self._record(r, kind, t.channel, detected, sent, m)
            out.append(row)
        return out

    # ------------------------------------------------------------------ registro
    def _record(self, r, kind, channel, detected, sent, m) -> dict:
        mid, cid = (str(m.get("id")) if m.get("id") else None), (str(m.get("channel_id")) if m.get("channel_id") else None)
        row = {"raffle_key": r.key, "kind": kind, "channel": channel, "store": r.store,
               "published_ts": getattr(r, "published_ts", None), "detected_ts": detected, "sent_ts": sent,
               "discord_ts": _discord_ts(m), "message_id": mid, "channel_id": cid, "guild_id": self.guild,
               "prueba": int(self.prueba)}
        with self.s._lock:
            self.s.db.execute("INSERT INTO delivery_times(raffle_key, kind, channel, store, published_ts, detected_ts, sent_ts, "
                              "discord_ts, message_id, channel_id, guild_id, prueba) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                              tuple(row.values()))
            if mid:   # también cuenta como entrega del canal (actividad, último mensaje)
                key = f"raffle|{channel}|{r.key}|{kind}|{sent:.3f}"
                self.s.db.execute("INSERT OR REPLACE INTO alerts(dedupe_key, event_type, store, product_key, sent_at, message_id, channel) "
                                  "VALUES (?,?,?,?,?,?,?)", (key, f"raffle_{kind}", r.store, r.sku, now_iso(), mid, channel))
            self.s.db.commit()
        row["jump_url"] = jump_url(self.guild, cid, mid)
        row["detect_to_send_ms"] = round((sent - detected) * 1000, 1)
        row["detect_to_discord_ms"] = round((row["discord_ts"] - detected) * 1000, 1) if row["discord_ts"] else None
        return row

    def _card(self, key, channel) -> str | None:
        with self.s._lock:
            x = self.s.db.execute("SELECT message_id FROM delivery_times WHERE raffle_key=? AND channel=? AND kind='apertura' "
                                  "AND message_id IS NOT NULL ORDER BY id LIMIT 1", (key, channel)).fetchone()
        return x[0] if x else None


def latest(store, *, prueba: bool | None = None, limit: int = 20) -> list[dict]:
    """Últimas entregas con tiempos (para el panel y la línea de comandos)."""
    q = "SELECT * FROM delivery_times" + ("" if prueba is None else f" WHERE prueba={int(prueba)}") + " ORDER BY id DESC LIMIT ?"
    with store._lock:
        try:
            cur = store.db.execute(q, (limit,))
        except Exception:   # noqa: BLE001 — tabla aún no creada
            return []
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, x)) for x in cur.fetchall()]
    for r in rows:
        r["jump_url"] = jump_url(r["guild_id"], r["channel_id"], r["message_id"])
        r["detect_to_send_ms"] = round((r["sent_ts"] - r["detected_ts"]) * 1000, 1) if r["sent_ts"] and r["detected_ts"] else None
        r["detect_to_discord_ms"] = round((r["discord_ts"] - r["detected_ts"]) * 1000, 1) if r["discord_ts"] and r["detected_ts"] else None
    return rows


def raffle_wants(profiles):
    """Miembros a mencionar en un raffle: con acceso, no en pausa, con la familia Raffles (o sin familias elegidas),
    la tienda permitida y, si eligieron marcas o palabras, que aparezcan en el modelo."""
    def f(r):
        text = f"{r.product} {r.sku}".lower()
        for p in profiles:
            fam = {x.lower() for x in p.families}
            if not p.entitled or p.paused or (fam and "raffles" not in fam):
                continue
            st = r.store.lower()
            if (p.stores and st not in {x.lower() for x in p.stores}) or st in {x.lower() for x in p.excluded_stores}:
                continue
            if p.brands and not any(b.lower() in text for b in p.brands):
                continue
            if any(k.lower() not in text for k in p.keywords) or any(n.lower() in text for n in p.negatives):
                continue
            yield p.member_id
    return f
