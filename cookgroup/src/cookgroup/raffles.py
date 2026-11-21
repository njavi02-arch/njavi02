"""Raffles (v0.9): ficha completa, apertura → recordatorio → cambio de plazo → cierre, y lista de abiertos sin vencidos.

Cada ficha indica: qué se sortea, si es un derecho de compra, dónde inscribirse, precio, requisitos, envío o recogida,
elegibilidad desde España (con su fuente), cierre en hora de Madrid y última verificación.
No se inventa nada: si la fuente no da un dato, la ficha dice «según la tienda» y enlaza la página oficial.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

from .forum import eur, mad

REMINDER_BEFORE = 3 * 3600


@dataclass
class Raffle:
    key: str                      # tienda|región|sku
    store: str
    product: str
    sku: str
    link: str | None              # inscripción (página oficial del raffle)
    prize: str                    # «derecho de compra» / «compra directa al ganar»
    price_cents: int | None
    currency: str
    requirements: list = field(default_factory=list)
    fulfilment: str = "envío"     # «envío» / «recogida en tienda (ciudad)»
    eligible_es: bool | None = None
    eligible_source: str = ""
    closes_ts: int | None = None
    verified_ts: int | None = None
    status: str = "abierto"       # abierto / cerrado
    reminded: bool = False
    published_ts: float | None = None   # hora de publicación según la tienda (solo si la fuente la da)


def from_bstn(l, now: int) -> Raffle:
    es = l.region in ("eu_es", "es")
    return Raffle(f"{l.store}|{l.region}|{l.key}", l.store, f"{l.brand} {l.name}", l.key, l.raffle_url,
                  "derecho de compra (si te toca, pagas el precio indicado)", l.price_cents, l.currency,
                  ["Cuenta en la tienda", "Requisitos exactos: según la página del raffle"],
                  "solo en tienda" if l.instore_only else "envío", True if es else None,
                  f"región «{l.region}» de la tienda" if es else "no indicado por la tienda", l.raffle_ends_ts, now,
                  "cerrado" if (l.raffle_expired or not l.raffle_active) else "abierto")


def card(r: Raffle, title: str) -> dict:
    el = {True: "✅ sí", False: "❌ no", None: "❓ sin confirmar"}[r.eligible_es]
    return {"embeds": [{"title": f"{title} — {r.store}", "url": r.link or None, "description": f"**{r.product}**", "color": 0xEB459E, "fields": [
        {"name": "Qué se sortea", "value": r.prize, "inline": False},
        {"name": "Precio", "value": eur(r.price_cents, r.currency), "inline": True},
        {"name": "Cierre", "value": mad(r.closes_ts), "inline": True},
        {"name": "Desde España", "value": f"{el} · fuente: {r.eligible_source}", "inline": True},
        {"name": "Entrega", "value": r.fulfilment, "inline": True},
        {"name": "Requisitos", "value": "\n".join(f"• {x}" for x in r.requirements) or "según la tienda", "inline": False},
        {"name": "Inscripción", "value": f"[Página oficial del raffle]({r.link})" if r.link else "según la tienda", "inline": False},
        {"name": "SKU", "value": f"`{r.sku}`", "inline": True},
        {"name": "Última verificación", "value": mad(r.verified_ts), "inline": True},
    ]}], "allowed_mentions": {"parse": []}}


class RaffleBoard:
    def __init__(self, store, send=None, edit_list=None, *, router=None, edit_today=None, clock=None):
        """send(payload) publica en #raffles; edit_list(payload) actualiza el mensaje fijado «Raffles abiertos».
        router (RaffleRouter) reparte cada aviso a varios canales y mide tiempos; edit_today(payload) mantiene la lista
        fijada de #raffles-cierran-hoy."""
        import time as _t
        self.s, self.send, self.edit_list = store, send, edit_list or (lambda p: None)
        self.router, self.edit_today, self.clock = router, edit_today or (lambda p: None), clock or _t.time
        with store._lock:
            store.db.execute("CREATE TABLE IF NOT EXISTS raffles (key TEXT PRIMARY KEY, data TEXT)")
            store.db.execute("CREATE TABLE IF NOT EXISTS raffle_baseline (store TEXT PRIMARY KEY, at INTEGER)")
            store.db.commit()

    # --- primer arranque: el catálogo existente se registra sin avisar
    def baselined(self, store_name: str) -> bool:
        with self.s._lock:
            return self.s.db.execute("SELECT 1 FROM raffle_baseline WHERE store=?", (store_name,)).fetchone() is not None

    def mark_baselined(self, store_name: str, now: int) -> None:
        with self.s._lock:
            self.s.db.execute("INSERT OR IGNORE INTO raffle_baseline VALUES (?,?)", (store_name, now))
            self.s.db.commit()

    def _emit(self, kind: str, r: Raffle, payload: dict) -> None:
        if self.router is not None:
            self.router.emit(kind, r, payload)
        elif self.send is not None:
            self.send(payload)

    def today_list(self, now: int) -> list[Raffle]:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        d = datetime.fromtimestamp(now, ZoneInfo("Europe/Madrid")).date()
        return [r for r in self.open_list(now) if r.closes_ts and datetime.fromtimestamp(r.closes_ts, ZoneInfo("Europe/Madrid")).date() == d]

    def today_payload(self, now: int) -> dict:
        rs = self.today_list(now)
        lines = [f"• **{mad(r.closes_ts)}** · {r.store} — {r.product} · " + (f"[inscribirse]({r.link})" if r.link else "según la tienda")
                 for r in rs] or ["Hoy no cierra ningún raffle abierto."]
        return {"embeds": [{"title": f"⏰ Raffles que cierran HOY ({len(rs)}) — hora de Madrid", "description": "\n".join(lines)[:4000],
                            "color": 0xE67E22, "footer": {"text": f"Actualizado {mad(now)}"}}], "allowed_mentions": {"parse": []}}

    def _lists(self, now: int) -> None:
        self._today_sig = tuple(r.key for r in self.today_list(now))
        self.edit_list(self.list_payload(now))
        self.edit_today(self.today_payload(now))

    def _get(self, key):
        with self.s._lock:
            r = self.s.db.execute("SELECT data FROM raffles WHERE key=?", (key,)).fetchone()
        return Raffle(**json.loads(r[0])) if r else None

    def _save(self, r: Raffle):
        with self.s._lock:
            self.s.db.execute("INSERT OR REPLACE INTO raffles VALUES (?,?)", (r.key, json.dumps(asdict(r))))
            self.s.db.commit()

    def open_list(self, now: int) -> list[Raffle]:
        with self.s._lock:
            rows = self.s.db.execute("SELECT data FROM raffles").fetchall()
        rs = [Raffle(**json.loads(x[0])) for x in rows]
        return sorted((r for r in rs if r.status == "abierto" and (not r.closes_ts or r.closes_ts > now)), key=lambda r: r.closes_ts or 9e12)

    def list_payload(self, now: int) -> dict:
        rs = self.open_list(now)
        es = {True: "España: sí", False: "España: no", None: "España sin confirmar"}
        lines = [f"• **{r.store}** — {r.product} · cierra {mad(r.closes_ts)} · {es[r.eligible_es]} · "
                 + (f"[inscribirse]({r.link})" if r.link else "según la tienda") for r in rs] or [
            "No hay raffles abiertos ahora mismo.",
            "Cuando abra uno, aparecerá aquí y en #raffles con su enlace y la hora de cierre (hora de Madrid).",
            "Para que te avisen: #elige-tus-avisos."]
        return {"embeds": [{"title": f"🎟️ Raffles abiertos ({len(rs)}) — hora de Madrid", "description": "\n".join(lines)[:4000],
                            "color": 0xEB459E, "footer": {"text": f"Actualizado {mad(now)} · se edita sola, sin repetir avisos"}}],
                "allowed_mentions": {"parse": []}}

    def refresh_lists(self, now: int) -> None:
        """v1.6: rehace las listas fijadas (abiertos / cierran hoy). Se llama tras la línea base del primer arranque,
        para que un miembro nuevo vea los raffles que ya estaban abiertos sin que se envíe el histórico como avisos."""
        self._lists(now)

    def ingest(self, r: Raffle, now: int, *, baseline: bool = False) -> list[str]:
        """baseline=True: primer arranque, se guarda sin avisar (no se inunda el canal con el catálogo existente)."""
        if self.router is not None:
            self.router.detected_ts = self.clock()
        old, done = self._get(r.key), []
        if old is None and baseline:
            self._save(r)
            return ["registrado"]
        if old is None:
            if r.status != "abierto":
                return []                               # silencio: raffle ya cerrado cuando lo vemos por primera vez
            r._card_payload = card(r, "🎟️ RAFFLE ABIERTO")
            self._emit("apertura", r, r._card_payload)
            done.append("apertura")
        else:
            r.reminded = old.reminded
            if old.status == "cerrado":
                return []                               # silencio: un raffle cerrado no vuelve a avisar
            if r.closes_ts and old.closes_ts and r.closes_ts != old.closes_ts:
                r._card_payload = card(r, "🎟️ RAFFLE ABIERTO")
                self._emit("cambio de plazo", r, {"content": f"⏰ **Cambio de plazo en {r.store}** ({r.product}): {mad(old.closes_ts)} → **{mad(r.closes_ts)}**",
                           "allowed_mentions": {"parse": []}})
                r.reminded = False
                done.append("cambio de plazo")
            if r.status == "cerrado":
                r._card_payload = card(r, "🔒 RAFFLE CERRADO")
                self._emit("cierre", r, {"content": f"🔒 **Raffle cerrado** en {r.store}: {r.product}", "allowed_mentions": {"parse": []}})
                done.append("cierre")
        self._save(r)
        done += self.tick(now, only=r.key)
        if done:
            self._lists(now)
        return done

    def tick(self, now: int, only: str | None = None) -> list[str]:
        """Recordatorios (3 h antes) y cierres por vencimiento. Se llama periódicamente."""
        done = []
        with self.s._lock:
            rows = self.s.db.execute("SELECT data FROM raffles" + (" WHERE key=?" if only else ""), ((only,) if only else ())).fetchall()
        for x in rows:
            r = Raffle(**json.loads(x[0]))
            if r.status != "abierto" or not r.closes_ts:
                continue
            if now >= r.closes_ts:
                r.status = "cerrado"
                r._card_payload = card(r, "🔒 RAFFLE CERRADO")
                self._emit("cierre por plazo", r, {"content": f"🔒 **Raffle cerrado** en {r.store}: {r.product} (plazo vencido)", "allowed_mentions": {"parse": []}})
                done.append("cierre por plazo")
            elif not r.reminded and now >= r.closes_ts - REMINDER_BEFORE:
                r.reminded = True
                self._emit("recordatorio", r, card(r, "⏳ CIERRA EN MENOS DE 3 H"))
                done.append("recordatorio")
            else:
                continue
            self._save(r)
        if done and not only:
            self._lists(now)
        elif not only:                                   # cambio de día: la lista de «cierran hoy» se renueva sola
            sig = tuple(r.key for r in self.today_list(now))
            if sig != getattr(self, "_today_sig", None):
                self._today_sig = sig
                self.edit_today(self.today_payload(now))
        return done
