from __future__ import annotations

import functools
import json
import sqlite3
import threading
from pathlib import Path

from .diff import now_iso
from .models import Product, Variant

MIGRATIONS = Path(__file__).resolve().parent / "migrations"


def _enc(p: Product) -> str:
    return json.dumps({**p.__dict__, "variants": [v.__dict__ for v in p.variants], "tags": list(p.tags)})


def _dec(s: str) -> Product:
    d = json.loads(s)
    d["variants"] = tuple(Variant(**v) for v in d["variants"])
    d["tags"] = tuple(d["tags"])
    return Product(**d)


def _locked(fn):
    """Una sola conexión SQLite compartida por todos los hilos de monitores: acceso serializado."""
    @functools.wraps(fn)
    def wrapper(self, *a, **kw):
        with self._lock:
            return fn(self, *a, **kw)
    return wrapper


class Store:
    def __init__(self, path: str = "cookgroup.db"):
        self._lock = threading.RLock()
        self.db = sqlite3.connect(path, check_same_thread=False, timeout=30)
        self.db.execute("PRAGMA journal_mode=WAL") if path != ":memory:" else None
        for f in sorted(MIGRATIONS.glob("*.sql")):
            for stmt in filter(str.strip, f.read_text().split(";")):
                try:
                    self.db.execute(stmt)
                except sqlite3.OperationalError as e:
                    if "duplicate column" not in str(e):
                        raise

    @_locked
    def load_snapshot(self, store: str) -> dict[str, Product] | None:
        rows = self.db.execute("SELECT product_key, data FROM snapshots WHERE store=?", (store,)).fetchall()
        return {k: _dec(d) for k, d in rows} if rows else None

    @_locked
    def save_snapshot(self, store: str, products: list[Product]) -> None:
        ts = now_iso()
        with self.db:
            # fusión: una lectura parcial (paginación rotatoria) no borra lo que no se ha leído este ciclo
            self.db.executemany("INSERT OR REPLACE INTO snapshots VALUES (?,?,?,?)",
                                [(store, p.key, _enc(p), ts) for p in products])
            self.db.executemany("INSERT INTO price_history VALUES (?,?,?)",
                                [(p.key, ts, p.min_price_cents) for p in products if p.min_price_cents])

    @_locked
    def historical_min(self, product_key: str) -> int | None:
        r = self.db.execute("SELECT MIN(min_price_cents) FROM price_history WHERE product_key=?", (product_key,)).fetchone()
        return r[0]

    @_locked
    def price_samples(self, product_key: str, limit: int = 50) -> list[int]:
        rows = self.db.execute("SELECT min_price_cents FROM price_history WHERE product_key=? "
                               "ORDER BY ts DESC LIMIT ?", (product_key, limit)).fetchall()
        return [r[0] for r in rows if r[0]]

    @_locked
    def seen_recently(self, dedupe_key: str, cooldown_s: int) -> bool:
        if self.db.execute("SELECT 1 FROM outbox WHERE dedupe_key=?", (dedupe_key,)).fetchone():
            return True   # pendiente de entrega: no se vuelve a encolar
        r = self.db.execute("SELECT sent_at FROM alerts WHERE dedupe_key=?", (dedupe_key,)).fetchone()
        if not r:
            return False
        from datetime import datetime, timezone
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(r[0])).total_seconds()
        return age < cooldown_s

    # ------------------------------------------------------------ bandeja de salida
    @_locked
    def outbox_add(self, key: str, event_type: str, store: str, product_key: str, channel: str, payload: dict) -> bool:
        """Encola un aviso. False si ya estaba encolado o enviado (deduplicación)."""
        if self.db.execute("SELECT 1 FROM alerts WHERE dedupe_key=?", (key,)).fetchone():
            return False
        cur = self.db.execute("INSERT OR IGNORE INTO outbox(dedupe_key, event_type, store, product_key, channel, payload, created_at) "
                              "VALUES (?,?,?,?,?,?,?)", (key, event_type, store, product_key, channel,
                                                        json.dumps(payload, ensure_ascii=False), now_iso()))
        self.db.commit()
        return cur.rowcount == 1

    @_locked
    def outbox_pending(self, store: str | None = None, limit: int = 50) -> list[tuple]:
        q = "SELECT dedupe_key, event_type, store, product_key, channel, payload, attempts FROM outbox"
        args: tuple = ()
        if store is not None:
            q += " WHERE store=?"
            args = (store,)
        return self.db.execute(q + " ORDER BY created_at LIMIT ?", args + (limit,)).fetchall()

    @_locked
    def outbox_done(self, key: str, message_id: str | None) -> None:
        row = self.db.execute("SELECT event_type, store, product_key FROM outbox WHERE dedupe_key=?", (key,)).fetchone()
        if not row:
            return
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO alerts(dedupe_key, event_type, store, product_key, sent_at, message_id) "
                            "VALUES (?,?,?,?,?,?)", (key, row[0], row[1], row[2], now_iso(), message_id))
            self.db.execute("DELETE FROM outbox WHERE dedupe_key=?", (key,))

    @_locked
    def outbox_fail(self, key: str, error: str) -> None:
        self.db.execute("UPDATE outbox SET attempts=attempts+1, last_error=?, last_attempt_at=? WHERE dedupe_key=?",
                        (error[:300], now_iso(), key))
        self.db.commit()

    @_locked
    def in_outbox(self, key: str) -> bool:
        return self.db.execute("SELECT 1 FROM outbox WHERE dedupe_key=?", (key,)).fetchone() is not None

    @_locked
    def record_probe(self, source: str, domain: str | None, status: str, read: int | None, valid: int | None,
                     sample: str | None, error: str | None) -> None:
        self.db.execute("INSERT OR REPLACE INTO probe_results VALUES (?,?,?,?,?,?,?,?)",
                        (source, domain, now_iso(), status, read, valid, (sample or "")[:200], (error or "")[:300]))
        self.db.commit()

    @_locked
    def last_probes(self) -> dict[str, tuple]:
        rows = self.db.execute("SELECT source, domain, checked_at, status, items_read, items_valid, sample, error FROM probe_results "
                               "ORDER BY checked_at").fetchall()
        return {r[0]: r for r in rows}

    @_locked
    def last_delivery(self) -> dict[str, tuple]:
        """store -> (último mensaje confirmado: fecha, id). Solo cuenta mensajes con id devuelto por Discord."""
        rows = self.db.execute("SELECT store, MAX(sent_at), message_id FROM alerts WHERE message_id IS NOT NULL "
                               "AND message_id NOT IN ('', 'None') GROUP BY store").fetchall()
        return {r[0]: (r[1], r[2]) for r in rows}

    @_locked
    def claim_mention(self, member_id: str, signal_key: str, channel: str) -> bool:
        """True la primera vez que se menciona a este miembro por esta señal; False si ya se hizo (en cualquier canal)."""
        cur = self.db.execute("INSERT OR IGNORE INTO mentions VALUES (?,?,?,?)", (member_id, signal_key, channel, now_iso()))
        self.db.commit()
        return cur.rowcount == 1

    @_locked
    def has_alert(self, dedupe_key: str) -> bool:
        return self.db.execute("SELECT 1 FROM alerts WHERE dedupe_key=?", (dedupe_key,)).fetchone() is not None

    @_locked
    def record_alert(self, dedupe_key: str, event_type: str, store: str, product_key: str, message_id: str | None) -> None:
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO alerts VALUES (?,?,?,?,?,?)",
                            (dedupe_key, event_type, store, product_key, now_iso(), message_id))

    # ------------------------------------------------------------ lanzamientos
    @_locked
    def load_launch_states(self, store: str) -> dict[str, dict]:
        """uid -> {"launch": {...}, "state": {...}, "present": bool}. Vacío si es la primera vez."""
        rows = self.db.execute("SELECT uid, data, present FROM launches WHERE store=?", (store,)).fetchall()
        out = {}
        for uid, data, present in rows:
            d = json.loads(data)
            d["present"] = bool(present)
            out[uid] = d
        return out

    @_locked
    def save_launch_states(self, store: str, states: dict[str, dict]) -> None:
        ts = now_iso()
        with self.db:
            for uid, d in states.items():
                data = json.dumps({"launch": d["launch"], "state": d.get("state", {})}, ensure_ascii=False)
                self.db.execute(
                    "INSERT INTO launches(uid, store, data, present, first_seen, updated_at) VALUES (?,?,?,?,?,?) "
                    "ON CONFLICT(uid) DO UPDATE SET data=excluded.data, present=excluded.present, updated_at=excluded.updated_at",
                    (uid, store, data, int(d.get("present", True)), ts, ts))

    @_locked
    def record_health(self, source: str, ok: bool, *, items: int | None = None, duration_ms: int | None = None,
                      error: str | None = None, delay_s: int | None = None) -> None:
        ts = now_iso()
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO source_health(source, consecutive_errors) VALUES (?, 0)", (source,))
            if ok:
                self.db.execute("UPDATE source_health SET last_ok=?, first_ok=COALESCE(first_ok, ?), ok_cycles=ok_cycles+1, "
                                "consecutive_errors=0, last_items=?, last_duration_ms=?, last_delay_s=COALESCE(?, last_delay_s) "
                                "WHERE source=?", (ts, ts, items, duration_ms, delay_s, source))
            else:
                self.db.execute("UPDATE source_health SET last_error=?, last_error_at=?, consecutive_errors=consecutive_errors+1 "
                                "WHERE source=?", ((error or "")[:300], ts, source))

    @_locked
    def health(self) -> list[tuple]:
        return self.db.execute("SELECT source, last_ok, consecutive_errors, last_error, last_error_at, last_items, "
                               "last_duration_ms, last_delay_s, first_ok, ok_cycles FROM source_health ORDER BY source").fetchall()

    @_locked
    def record_run(self, monitor: str, ok: bool, products: int = 0, events: int = 0, error: str | None = None) -> None:
        with self.db:
            self.db.execute("INSERT INTO monitor_runs VALUES (?,?,?,?,?,?)",
                            (monitor, now_iso(), int(ok), products, events, error))
