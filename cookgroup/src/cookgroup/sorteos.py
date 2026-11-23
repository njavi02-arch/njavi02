"""v1.6 · sorteos internos del servidor (equivalente a «🎉giveaways» de la referencia).

Flujo: el staff crea el sorteo (premio + duración) → el bot publica el anuncio y añade 🎉 → los miembros reaccionan →
al cerrar, el bot lee quién reaccionó (sin bots), elige ganador(es) con una semilla que queda guardada (auditable) y
publica el resultado mencionando solo a los ganadores. Un sorteo se resuelve UNA vez (aunque el proceso se reinicie).
Solo usa la API REST de Discord con el token del bot; no hay cobros ni datos personales más allá del id de Discord.
"""
from __future__ import annotations

import json
import random
import sqlite3
import time
from urllib.parse import quote

EMOJI = "🎉"
API = "https://discord.com/api/v10"


class Sorteos:
    def __init__(self, db: str, http, token: str):
        self.db, self.http, self.h = db, http, {"Authorization": f"Bot {token}"}
        with sqlite3.connect(self.db) as c:
            c.execute("CREATE TABLE IF NOT EXISTS sorteos (id INTEGER PRIMARY KEY, channel_id TEXT, message_id TEXT, premio TEXT,"
                      " ganadores INTEGER, cierra REAL, estado TEXT, semilla TEXT, resultado TEXT)")

    def _ok(self, r):
        if r.status_code >= 400:
            raise RuntimeError(f"Discord respondió {r.status_code}")
        return r

    def crear(self, channel_id: str, premio: str, minutos: int, ganadores: int = 1, now: float | None = None) -> int:
        now = time.time() if now is None else now
        cierra = now + minutos * 60
        body = {"embeds": [{"title": f"{EMOJI} SORTEO · {premio}", "color": 0xF1C40F,
                            "description": f"Reacciona con {EMOJI} para participar.\nGanadores: **{ganadores}** · "
                                           f"Cierra <t:{int(cierra)}:R> (<t:{int(cierra)}:f>)"}],
                "allowed_mentions": {"parse": []}}
        msg = self._ok(self.http.post(f"{API}/channels/{channel_id}/messages", headers=self.h, json=body)).json()
        self._ok(self.http.put(f"{API}/channels/{channel_id}/messages/{msg['id']}/reactions/{quote(EMOJI)}/@me", headers=self.h))
        with sqlite3.connect(self.db) as c:
            cur = c.execute("INSERT INTO sorteos (channel_id, message_id, premio, ganadores, cierra, estado) VALUES (?,?,?,?,?, 'abierto')",
                            (channel_id, msg["id"], premio, ganadores, cierra))
            return cur.lastrowid

    def _participantes(self, channel_id: str, message_id: str) -> list[str]:
        out, after = [], None
        while True:
            params = {"limit": 100, **({"after": after} if after else {})}
            users = self._ok(self.http.get(f"{API}/channels/{channel_id}/messages/{message_id}/reactions/{quote(EMOJI)}",
                                           headers=self.h, params=params)).json()
            out += [u["id"] for u in users if not u.get("bot")]
            if len(users) < 100:
                return sorted(set(out))
            after = users[-1]["id"]

    def resolver_vencidos(self, now: float | None = None, rng=None) -> list[dict]:
        now = time.time() if now is None else now
        with sqlite3.connect(self.db) as c:
            rows = c.execute("SELECT id, channel_id, message_id, premio, ganadores FROM sorteos WHERE estado='abierto' AND cierra<=?",
                             (now,)).fetchall()
        hechos = []
        for sid, ch, mid, premio, n in rows:
            gente = self._participantes(ch, mid)
            semilla = f"{sid}-{mid}-{len(gente)}"
            ganadores = (rng or random.Random(semilla)).sample(gente, min(n, len(gente))) if gente else []
            if ganadores:
                txt = f"{EMOJI} **{premio}** · ganador{'es' if len(ganadores) > 1 else ''}: " + ", ".join(f"<@{g}>" for g in ganadores)
                txt += f"\nParticipantes: {len(gente)} · semilla del sorteo: `{semilla}`. El staff contactará por privado."
            else:
                txt = f"{EMOJI} **{premio}** · nadie participó: sorteo desierto."
            self._ok(self.http.post(f"{API}/channels/{ch}/messages", headers=self.h,
                                    json={"content": txt, "allowed_mentions": {"users": ganadores},
                                          "message_reference": {"message_id": mid}}))
            with sqlite3.connect(self.db) as c:      # se marca resuelto SOLO tras publicar: un fallo se reintenta
                c.execute("UPDATE sorteos SET estado='resuelto', semilla=?, resultado=? WHERE id=?",
                          (semilla, json.dumps({"participantes": len(gente), "ganadores": ganadores}), sid))
            hechos.append({"id": sid, "participantes": len(gente), "ganadores": ganadores, "semilla": semilla})
        return hechos
