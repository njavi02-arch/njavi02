"""Foro de lanzamientos (v0.9): un hilo por lanzamiento (clave = SKU base), actualizaciones por tienda en el MISMO hilo.

Webhook a canal de foro (Discord): POST ?wait=true con `thread_name` crea la publicación (el hilo); después,
POST ?thread_id=… responde dentro, y PATCH /messages/{id}?thread_id=… actualiza el mensaje inicial.
Silencio: si nada cambia (misma tienda, misma fecha, mismo método) no se publica nada.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

MAD = ZoneInfo("Europe/Madrid")
DAY = 86400


def mad(ts: int | None, fmt="%a %d/%m · %H:%M") -> str:
    if not ts:
        return "fecha por confirmar"
    d = datetime.fromtimestamp(ts, MAD)
    dias = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
    return d.strftime(fmt).replace(d.strftime("%a"), dias[d.weekday()]) + " (Madrid)"


def base_sku(s: str) -> str:
    return (s or "").upper().strip()


@dataclass
class StoreEntry:
    store: str
    region: str
    method: str                  # «raffle (derecho de compra)», «venta directa (FCFS)», «app», «solo en tienda»
    url: str | None
    price_cents: int | None
    currency: str
    release_ts: int | None
    raffle_closes_ts: int | None = None


@dataclass
class ReleaseThread:
    sku: str
    name: str
    brand: str
    stores: dict = field(default_factory=dict)        # store → StoreEntry (dict)
    thread_id: str | None = None
    starter_id: str | None = None
    official_links: list = field(default_factory=list)

    @property
    def release_ts(self) -> int | None:
        ts = [s["release_ts"] for s in self.stores.values() if s.get("release_ts")]
        return min(ts) if ts else None

    def title(self) -> str:
        d = datetime.fromtimestamp(self.release_ts, MAD).strftime("%d/%m") if self.release_ts else "Por confirmar"
        return f"{d} · {self.brand} {self.name}"[:100]


def method_of(l) -> str:
    if l.instore_only:
        return "solo en tienda"
    if l.app_only:
        return "app de la tienda"
    if l.raffle:
        return "raffle (derecho de compra)"
    return "venta directa (FCFS)"


def entry_from_launch(l) -> StoreEntry:
    return StoreEntry(l.store, l.region, method_of(l), l.link, l.price_cents, l.currency, l.release_ts, l.raffle_ends_ts)


def eur(c, cur="EUR"):
    return "—" if c is None else f"{c / 100:.2f} {'€' if cur == 'EUR' else cur}".replace(".", ",")


def starter_payload(t: ReleaseThread) -> dict:
    lines = []
    for s in sorted(t.stores.values(), key=lambda x: (x["release_ts"] or 9e12, x["store"])):
        link = f"[enlace oficial]({s['url']})" if s.get("url") else "sin enlace"
        close = f" · cierra {mad(s['raffle_closes_ts'])}" if s.get("raffle_closes_ts") else ""
        lines.append(f"• **{s['store']}** ({s['region']}) — {s['method']} · {mad(s['release_ts'])} · {eur(s['price_cents'], s['currency'])}"
                     f"{close} · {link}")
    prices = [s["price_cents"] for s in t.stores.values() if s.get("price_cents")]
    return {"embeds": [{"title": f"{t.brand} {t.name}"[:250], "color": 0x5865F2, "fields": [
        {"name": "SKU", "value": f"`{t.sku}`", "inline": True},
        {"name": "Fecha y hora", "value": mad(t.release_ts), "inline": True},
        {"name": "Precio retail", "value": (eur(min(prices)) + " (precio publicado por la tienda)") if prices else "por confirmar", "inline": True},
        {"name": f"Tiendas participantes ({len(t.stores)})", "value": "\n".join(lines)[:1024] or "—", "inline": False},
    ], "footer": {"text": "Las actualizaciones de cada tienda se publican en este mismo hilo"}}], "allowed_mentions": {"parse": []}}


class Forum:
    def __init__(self, store, publisher):
        self.s, self.pub = store, publisher
        with store._lock:
            store.db.execute("CREATE TABLE IF NOT EXISTS forum_threads (sku TEXT PRIMARY KEY, data TEXT, updated_at TEXT)")
            store.db.commit()

    def get(self, sku) -> ReleaseThread | None:
        with self.s._lock:
            r = self.s.db.execute("SELECT data FROM forum_threads WHERE sku=?", (sku,)).fetchone()
        return ReleaseThread(**json.loads(r[0])) if r else None

    def save(self, t: ReleaseThread):
        with self.s._lock:
            self.s.db.execute("INSERT OR REPLACE INTO forum_threads VALUES (?,?,datetime('now'))", (t.sku, json.dumps(asdict(t))))
            self.s.db.commit()

    def all(self) -> list[ReleaseThread]:
        with self.s._lock:
            rows = self.s.db.execute("SELECT data FROM forum_threads").fetchall()
        return [ReleaseThread(**json.loads(r[0])) for r in rows]

    def ingest(self, l) -> list[str]:
        """Aplica un lanzamiento visto en una tienda. Devuelve lo publicado (vacío = silencio)."""
        sku = base_sku(l.key)
        e = asdict(entry_from_launch(l))
        t = self.get(sku)
        done = []
        if t is None:
            t = ReleaseThread(sku, l.name, l.brand, {l.store: e})
            t.thread_id, t.starter_id = self.pub.create(t.title(), starter_payload(t))
            done.append(f"hilo creado: «{t.title()}»")
        else:
            old = t.stores.get(l.store)
            if old is None:
                t.stores[l.store] = e
                self.pub.reply(t.thread_id, {"content": f"🏪 **Nueva tienda: {l.store}** ({l.region}) — {e['method']} · "
                                                        f"{mad(e['release_ts'])} · {eur(e['price_cents'], e['currency'])}"
                                                        + (f" · {e['url']}" if e["url"] else ""), "allowed_mentions": {"parse": []}})
                done.append(f"nueva tienda en el hilo: {l.store}")
            else:
                if old["release_ts"] != e["release_ts"] and e["release_ts"]:
                    self.pub.reply(t.thread_id, {"content": f"📅 **Cambio de fecha en {l.store}:** {mad(old['release_ts'])} → "
                                                            f"**{mad(e['release_ts'])}**", "allowed_mentions": {"parse": []}})
                    done.append(f"cambio de fecha en {l.store}")
                if old["method"] != e["method"]:
                    self.pub.reply(t.thread_id, {"content": f"🔁 **{l.store} cambia el método:** {old['method']} → **{e['method']}**"
                                                            + (f" · {e['url']}" if e["url"] else ""), "allowed_mentions": {"parse": []}})
                    done.append(f"cambio de método en {l.store}")
                if not done:
                    return []                                       # silencio: nada nuevo
                t.stores[l.store] = e
            self.pub.edit(t.thread_id, t.starter_id, starter_payload(t))
        self.save(t)
        return done

    def post_update(self, sku: str, payload: dict) -> bool:
        """Publica una actualización (p. ej. «a la venta») dentro del hilo de ese SKU. False si no hay hilo."""
        t = self.get(base_sku(sku))
        if not t or not t.thread_id:
            return False
        self.pub.reply(t.thread_id, payload)
        return True

    def next_7_days(self, now: float, guild_id: str = "TU_SERVIDOR") -> dict | None:
        soon = sorted((t for t in self.all() if t.release_ts and now <= t.release_ts <= now + 7 * DAY), key=lambda t: t.release_ts)
        if not soon:
            return None
        lines = [f"**{mad(t.release_ts)}** — {t.brand} {t.name} · {len(t.stores)} tienda(s) · "
                 f"[hilo](https://discord.com/channels/{guild_id}/{t.thread_id})" for t in soon]
        return {"embeds": [{"title": "📆 Próximos 7 días", "description": "\n".join(lines)[:4000], "color": 0x3498DB}],
                "allowed_mentions": {"parse": []}}


class WebhookForum:
    """Publicador real (webhook del canal de foro). Se usa con DISCORD_WEBHOOK_LANZAMIENTOS."""
    def __init__(self, url, http=None):
        import requests
        self.url, self.http = url.rstrip("/"), http or requests.Session()

    def create(self, title, payload):
        r = self.http.post(self.url, params={"wait": "true"}, json={**payload, "thread_name": title}, timeout=15)
        r.raise_for_status()
        m = r.json()
        return m["channel_id"], m["id"]

    def reply(self, thread_id, payload):
        self.http.post(self.url, params={"wait": "true", "thread_id": thread_id}, json=payload, timeout=15).raise_for_status()

    def edit(self, thread_id, msg_id, payload):
        self.http.patch(f"{self.url}/messages/{msg_id}", params={"thread_id": thread_id}, json=payload, timeout=15).raise_for_status()


class FakeForum:
    """Foro simulado para pruebas y panel: guarda hilos, respuestas y ediciones."""
    def __init__(self):
        self.threads: dict[str, dict] = {}
        self.n = 0

    def create(self, title, payload):
        self.n += 1
        tid, mid = f"hilo{self.n}", f"msg{self.n}"
        self.threads[tid] = {"title": title, "starter": payload, "replies": [], "edits": 0}
        return tid, mid

    def reply(self, tid, payload):
        self.threads[tid]["replies"].append(payload)

    def edit(self, tid, mid, payload):
        self.threads[tid]["starter"] = payload
        self.threads[tid]["edits"] += 1


def launch_from_product(p, region: str = "eu"):
    """Producto de una colección «launches» de Shopify → lanzamiento para el foro (sin fecha: la tienda no la publica)."""
    from .sources.bstn import Launch
    skus = sorted({v.sku for v in p.variants if v.sku})
    key = skus[0].rsplit("-", 1)[0] if skus and "-" in skus[0] else (skus[0] if skus else p.product_id)
    price = min((v.price_cents for v in p.variants if v.price_cents), default=None)
    return Launch(p.store, region, key, p.vendor or "", p.title, p.url, p.image_url, p.currency, price)
