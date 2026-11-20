"""Diagnóstico por fuente (v0.7). Solo LEE: nunca envía nada a Discord.

Estados (uno por fuente y comprobación):
  ÚTIL              lectura correcta con productos que pasan los filtros del monitor
  SIN COINCIDENCIAS lectura correcta y con productos, pero ninguno pasa los filtros (marcas/palabras)
  VACÍA             la fuente respondió bien pero sin elementos (en un feed puede ser normal; en una tienda, sospechoso)
  SIN CAMBIOS       304 Not Modified: la fuente confirma que no hay novedades (es correcto)
  LIMITADA          429 / bloqueo temporal / anti-bot: se reintenta más tarde, no es un fallo del monitor
  FALLO             error de red, HTML inesperado, dominio caído…
"""
from __future__ import annotations

import csv
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")
OK_STATES = {"ÚTIL", "SIN COINCIDENCIAS", "VACÍA", "SIN CAMBIOS"}
STATE_FILE = Path("logs/probe_lote.json")


@dataclass
class ProbeRow:
    monitor: str
    domain: str
    type: str
    status: str
    checked_madrid: str
    read: int | None
    valid: int | None
    with_stock: int | None
    sample: str
    last_delivery: str
    error: str
    next_step: str


def madrid_now() -> str:
    return datetime.now(MADRID).strftime("%d/%m/%Y %H:%M")


def _domain(m) -> str:
    u = m.base_url or (m.listing_urls[0] if getattr(m, "listing_urls", None) else "")
    return urlparse(u).netloc.removeprefix("www.") if u else (m.store or m.name)


def sample_variant(products) -> str:
    """Ejemplo legible: «Título — talla EU 43 — 129,99 EUR — con stock»."""
    for p in products:
        for v in p.variants:
            price = f"{v.price_cents / 100:.2f} {p.currency}" if v.price_cents is not None else "sin precio"
            stock = "con stock" if v.available else "sin stock"
            return f"{p.title[:60]} — talla {v.title or '?'} — {price} — {stock}"
        return f"{p.title[:60]} — (sin variantes)"
    return ""


def classify_error(e: Exception) -> tuple[str, str]:
    name, msg = type(e).__name__, str(e)
    low = msg.lower()
    if msg == "not-modified":
        return "SIN CAMBIOS", ""
    if name == "RateLimited" or any(k in low for k in ("429", "rate", "captcha", "anti-bot", "antibot", "403", "cloudflare",
                                                        "access denied", "challenge")):
        return "LIMITADA", f"{name}: {msg}"[:300]
    return "FALLO", f"{name}: {msg}"[:300]


NEXT = {
    "ÚTIL": "nada: listo para el piloto",
    "SIN COINCIDENCIAS": "revisar filtros (include_vendors / palabras) o la colección",
    "VACÍA": "normal en feeds sin novedades; en tienda, revisar URL/colección",
    "SIN CAMBIOS": "nada (la fuente confirma que no hay novedades)",
    "LIMITADA": "reintentar más tarde con intervalo mayor; si persiste, fuente no apta",
    "FALLO": "revisar el error; si el dominio cambió, actualizar config",
}


def probe_one(m, make_source, prepare, store=None) -> ProbeRow:
    from .sources.shopify import SourceError
    read = valid = stock = None
    sample = err = ""
    try:
        if m.type == "bstn":
            items = make_source(m).fetch_launches(datetime.now(timezone.utc))
            read = valid = len(items)
            stock = sum(1 for i in items if i.raffle_active)
            status = "ÚTIL" if items else "VACÍA"
            if items:
                i = items[0]
                sample = f"{getattr(i, 'name', '')[:60]} — raffle {'abierto' if i.raffle_active else 'no'}"
        else:
            raw = make_source(m).fetch()
            ok, _dropped = prepare(raw, m)
            read, valid = len(raw), len(ok)
            stock = sum(1 for p in ok if p.available_variants)
            status = "VACÍA" if not raw else "SIN COINCIDENCIAS" if not ok else "ÚTIL"
            sample = sample_variant(ok or raw)
    except SourceError as e:
        status, err = classify_error(e)
    except Exception as e:  # noqa: BLE001 — una fuente rota no para el lote
        status, err = classify_error(e)
    last = ""
    if store is not None:
        d = store.last_delivery().get(m.store)
        if d:
            last = datetime.fromisoformat(d[0]).astimezone(MADRID).strftime("%d/%m %H:%M") + f" (id {d[1]})"
        store.record_probe(m.name, _domain(m), status, read, valid, sample, err)
    return ProbeRow(m.name, _domain(m), m.type, status, madrid_now(), read, valid, stock, sample, last or "ninguno",
                    err, NEXT[status])


def select(monitors, *, only: str | None = None, match: str | None = None, limit: int | None = None,
           resume: bool = False):
    ms = [m for m in monitors if m.enabled]
    if only:
        wanted = {x.strip().lower() for x in only.split(",") if x.strip()}
        ms = [m for m in ms if m.name.lower() in wanted or _domain(m).lower() in wanted]
    if match:
        k = match.lower()
        ms = [m for m in ms if k in m.name.lower() or k in _domain(m).lower() or k in (m.store or "").lower()]
    if resume and STATE_FILE.exists():
        done = set(json.loads(STATE_FILE.read_text(encoding="utf-8")).get("done", []))
        ms = [m for m in ms if m.name not in done]
    if limit:
        ms = ms[:limit]
    return ms


def run_probe(monitors, make_source, prepare, store=None, *, resume=False, out_dir="logs", printer=print) -> list[ProbeRow]:
    os.makedirs(out_dir, exist_ok=True)
    state = {"started": madrid_now(), "done": []}
    if resume and STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    rows = []
    printer(f"{'estado':<18} {'monitor':<24} {'leídos':>6} {'válidos':>7} {'stock':>5}  ejemplo / causa")
    for m in monitors:
        t0 = time.monotonic()
        r = probe_one(m, make_source, prepare, store)
        rows.append(r)
        state["done"].append(m.name)
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")  # se puede reanudar si se corta
        n = lambda x: "-" if x is None else str(x)
        printer(f"{r.status:<18} {r.monitor[:24]:<24} {n(r.read):>6} {n(r.valid):>7} {n(r.with_stock):>5}  "
                f"{(r.sample or r.error)[:90]}  ({time.monotonic() - t0:.1f}s)")
    stamp = datetime.now(MADRID).strftime("%Y%m%d_%H%M")
    path = Path(out_dir) / f"comprobacion_{stamp}.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig: Excel lo abre bien
        w = csv.writer(f, delimiter=";")
        w.writerow(["monitor", "dominio", "tipo", "estado", "comprobado (Madrid)", "leídos", "válidos", "con stock",
                    "ejemplo de variante", "último envío confirmado", "causa del fallo", "siguiente paso"])
        for r in rows:
            w.writerow([r.monitor, r.domain, r.type, r.status, r.checked_madrid, r.read, r.valid, r.with_stock, r.sample,
                        r.last_delivery, r.error, r.next_step])
    from collections import Counter
    c = Counter(r.status for r in rows)
    printer("\nResumen: " + " · ".join(f"{k} {v}" for k, v in c.most_common()) + f"\nInforme: {path.resolve()}")
    return rows


def finish_batch():
    """El lote terminó entero: la próxima --reanudar empieza de cero."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


# ---------- estado del proceso (latido) ----------
HEARTBEAT = Path("logs/heartbeat.json")


def write_heartbeat(n_threads: int, alive: int, path: Path = HEARTBEAT):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"pid": os.getpid(), "ts": datetime.now(timezone.utc).isoformat(), "threads": n_threads,
                               "alive": alive}), encoding="utf-8")
    os.replace(tmp, path)


def process_state(path: Path = HEARTBEAT, max_age_s: int = 120) -> tuple[str, str]:
    if not path.exists():
        return "PARADO", "no hay latido: el bot no se ha arrancado nunca en esta carpeta"
    d = json.loads(path.read_text(encoding="utf-8"))
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(d["ts"])).total_seconds()
    when = datetime.fromisoformat(d["ts"]).astimezone(MADRID).strftime("%d/%m %H:%M:%S")
    if age <= max_age_s:
        return "EN MARCHA", f"último latido {when} (hace {int(age)} s) · {d['alive']}/{d['threads']} hilos vivos · pid {d['pid']}"
    return "PARADO", f"último latido {when} (hace {int(age // 60)} min): el proceso no está corriendo"


def lag_label(last_ok_iso: str | None, interval_s: int, now: datetime | None = None) -> str:
    """Retraso de una fuente respecto a SU propio intervalo (con margen para escalonado y reintentos)."""
    if not last_ok_iso:
        return "SIN LECTURA"
    now = now or datetime.now(timezone.utc)
    age = (now - datetime.fromisoformat(last_ok_iso)).total_seconds()
    ratio = age / max(interval_s, 1)
    if age <= interval_s * 2 + 150:
        return "AL DÍA"
    return f"RETRASADA ×{ratio:.0f}"
