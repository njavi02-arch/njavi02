from __future__ import annotations

import json
import sqlite3
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


class Store:
    def __init__(self, path: str = "cookgroup.db"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        for f in sorted(MIGRATIONS.glob("*.sql")):
            self.db.executescript(f.read_text())

    def load_snapshot(self, store: str) -> dict[str, Product] | None:
        rows = self.db.execute("SELECT product_key, data FROM snapshots WHERE store=?", (store,)).fetchall()
        return {k: _dec(d) for k, d in rows} if rows else None

    def save_snapshot(self, store: str, products: list[Product]) -> None:
        ts = now_iso()
        with self.db:
            self.db.execute("DELETE FROM snapshots WHERE store=?", (store,))
            self.db.executemany("INSERT INTO snapshots VALUES (?,?,?,?)",
                                [(store, p.key, _enc(p), ts) for p in products])
            self.db.executemany("INSERT INTO price_history VALUES (?,?,?)",
                                [(p.key, ts, p.min_price_cents) for p in products if p.min_price_cents])

    def historical_min(self, product_key: str) -> int | None:
        r = self.db.execute("SELECT MIN(min_price_cents) FROM price_history WHERE product_key=?", (product_key,)).fetchone()
        return r[0]

    def price_samples(self, product_key: str, limit: int = 50) -> list[int]:
        rows = self.db.execute("SELECT min_price_cents FROM price_history WHERE product_key=? "
                               "ORDER BY ts DESC LIMIT ?", (product_key, limit)).fetchall()
        return [r[0] for r in rows if r[0]]

    def seen_recently(self, dedupe_key: str, cooldown_s: int) -> bool:
        r = self.db.execute("SELECT sent_at FROM alerts WHERE dedupe_key=?", (dedupe_key,)).fetchone()
        if not r:
            return False
        from datetime import datetime, timezone
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(r[0])).total_seconds()
        return age < cooldown_s

    def has_alert(self, dedupe_key: str) -> bool:
        return self.db.execute("SELECT 1 FROM alerts WHERE dedupe_key=?", (dedupe_key,)).fetchone() is not None

    def record_alert(self, dedupe_key: str, event_type: str, store: str, product_key: str, message_id: str | None) -> None:
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO alerts VALUES (?,?,?,?,?,?)",
                            (dedupe_key, event_type, store, product_key, now_iso(), message_id))

    # ------------------------------------------------------------ lanzamientos
    def load_launch_states(self, store: str) -> dict[str, dict]:
        """uid -> {"launch": {...}, "state": {...}, "present": bool}. Vacío si es la primera vez."""
        rows = self.db.execute("SELECT uid, data, present FROM launches WHERE store=?", (store,)).fetchall()
        out = {}
        for uid, data, present in rows:
            d = json.loads(data)
            d["present"] = bool(present)
            out[uid] = d
        return out

    def save_launch_states(self, store: str, states: dict[str, dict]) -> None:
        ts = now_iso()
        with self.db:
            for uid, d in states.items():
                data = json.dumps({"launch": d["launch"], "state": d.get("state", {})}, ensure_ascii=False)
                self.db.execute(
                    "INSERT INTO launches(uid, store, data, present, first_seen, updated_at) VALUES (?,?,?,?,?,?) "
                    "ON CONFLICT(uid) DO UPDATE SET data=excluded.data, present=excluded.present, updated_at=excluded.updated_at",
                    (uid, store, data, int(d.get("present", True)), ts, ts))

    def record_health(self, source: str, ok: bool, *, items: int | None = None, duration_ms: int | None = None,
                      error: str | None = None, delay_s: int | None = None) -> None:
        ts = now_iso()
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO source_health(source, consecutive_errors) VALUES (?, 0)", (source,))
            if ok:
                self.db.execute("UPDATE source_health SET last_ok=?, consecutive_errors=0, last_items=?, last_duration_ms=?, "
                                "last_delay_s=COALESCE(?, last_delay_s) WHERE source=?", (ts, items, duration_ms, delay_s, source))
            else:
                self.db.execute("UPDATE source_health SET last_error=?, last_error_at=?, consecutive_errors=consecutive_errors+1 "
                                "WHERE source=?", ((error or "")[:300], ts, source))

    def health(self) -> list[tuple]:
        return self.db.execute("SELECT source, last_ok, consecutive_errors, last_error, last_error_at, last_items, "
                               "last_duration_ms, last_delay_s FROM source_health ORDER BY source").fetchall()

    def record_run(self, monitor: str, ok: bool, products: int = 0, events: int = 0, error: str | None = None) -> None:
        with self.db:
            self.db.execute("INSERT INTO monitor_runs VALUES (?,?,?,?,?,?)",
                            (monitor, now_iso(), int(ok), products, events, error))
