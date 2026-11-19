from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .diff import now_iso
from .models import Product, Variant

MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"


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

    def seen_recently(self, dedupe_key: str, cooldown_s: int) -> bool:
        r = self.db.execute("SELECT sent_at FROM alerts WHERE dedupe_key=?", (dedupe_key,)).fetchone()
        if not r:
            return False
        from datetime import datetime, timezone
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(r[0])).total_seconds()
        return age < cooldown_s

    def record_alert(self, dedupe_key: str, event_type: str, store: str, product_key: str, message_id: str | None) -> None:
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO alerts VALUES (?,?,?,?,?,?)",
                            (dedupe_key, event_type, store, product_key, now_iso(), message_id))

    def record_run(self, monitor: str, ok: bool, products: int = 0, events: int = 0, error: str | None = None) -> None:
        with self.db:
            self.db.execute("INSERT INTO monitor_runs VALUES (?,?,?,?,?,?)",
                            (monitor, now_iso(), int(ok), products, events, error))
