"""Piloto de extremo a extremo SIN webhook real (v0.7).

Levanta en local dos servidores HTTP:
  · una «tienda» Shopify que sirve la CAPTURA REAL de footdistrict.com (20-nov-2026) y a la que se aplican cambios
    CONTROLADOS (vuelve una talla, baja un precio…);
  · un «Discord» falso que responde como un webhook (devuelve id de mensaje) y que se puede tumbar y levantar.
Recorre: captura → normalización → historial → detección → aviso, más reinicio del proceso y caída/recuperación de
Discord, comprobando que no se pierde ni se duplica nada. Escribe el registro en docs/v07/PILOTO_REGISTRO.md.

Uso:  python tools/piloto.py
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost"

import cookgroup.ratelimit as rl  # noqa: E402
from cookgroup.config import MonitorConfig  # noqa: E402
from cookgroup.discord import WebhookSender  # noqa: E402
from cookgroup.market import FileMarketProvider  # noqa: E402
from cookgroup.pipeline import run_cycle  # noqa: E402
from cookgroup.sources.shopify import ShopifySource  # noqa: E402
from cookgroup.store import Store  # noqa: E402

rl.DEFAULT_MIN_INTERVAL = 0
FIX = ROOT / "tests/fixtures/footdistrict_REAL_2026-11-20.json"


class State:
    def __init__(self):
        self.catalog = json.loads(FIX.read_text(encoding="utf-8"))
        self.discord_down = False
        self.received: list[dict] = []
        self.n = 0


def _servers(state: State):
    class Shop(BaseHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split("?")[0]
            if path == "/cart.js":
                body = {"currency": "EUR"}
            elif path.endswith("/products.json"):
                q = self.path.split("?")[1] if "?" in self.path else ""
                body = {"products": state.catalog["products"]} if "page=1" in q or "page" not in q else {"products": []}
            elif path.startswith("/products/") and path.endswith(".json"):
                h = path[len("/products/"):-5]
                p = next((x for x in state.catalog["products"] if x["handle"] == h), None)
                body = {"product": p} if p else None
            else:
                body = None
            if body is None:
                self.send_response(404); self.end_headers(); return
            raw = json.dumps(body).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(raw)

        def log_message(self, *a):
            pass

    class Discord(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or b"{}")
            if state.discord_down:
                self.send_response(503); self.end_headers(); self.wfile.write(b"caido (simulado)"); return
            state.n += 1
            state.received.append(payload)
            raw = json.dumps({"id": f"PILOTO-{state.n:04d}"}).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(raw)

        def log_message(self, *a):
            pass

    out = []
    for h in (Shop, Discord):
        s = ThreadingHTTPServer(("127.0.0.1", 0), h)
        threading.Thread(target=s.serve_forever, daemon=True).start()
        out.append(s)
    return out


def _variant(state, handle, size):
    p = next(x for x in state.catalog["products"] if x["handle"] == handle)
    return next(v for v in p["variants"] if v["title"] == size), p


def run(log=print, db_path: str | None = None) -> dict:
    state = State()
    shop, disc = _servers(state)
    shop_url = f"http://127.0.0.1:{shop.server_port}"
    hook = f"http://127.0.0.1:{disc.server_port}/api/webhooks/0/piloto"
    tmp = Path(tempfile.mkdtemp())
    db = Path(db_path) if db_path else tmp / "piloto.db"
    cfg = MonitorConfig("footdistrict-piloto", "shopify", "FOOTDISTRICT", shop_url, channel="sneakers", country="ES",
                        region="eu")
    market = FileMarketProvider(tmp / "sin_mercado.json")
    defaults = {"cooldown_seconds": 3600, "min_drop_pct": 10}
    steps, ok_all = [], True

    def cycle(store, src, label):
        res = run_cycle(cfg, defaults, src, store, market, WebhookSender(hook, max_retries=1).send)
        return res

    def check(name, cond, detail):
        nonlocal ok_all
        ok_all &= bool(cond)
        steps.append((name, "OK" if cond else "FALLA", detail))
        log(f"[{'OK' if cond else 'FALLA'}] {name}: {detail}")

    store, src = Store(db), ShopifySource("FOOTDISTRICT", shop_url, deep_pages=1)
    r = cycle(store, src, "base")
    check("1. Captura y normalización (base)", r["ok"] and r["products"] == 3 and r["sent"] == 0,
          f"{r['products']} productos reales leídos por HTTP, {r['events']} eventos (la base no avisa)")

    v, _ = _variant(state, "adidas-originals-oregon-ultra-tech-kz8462", "44")
    v["available"] = True
    r = cycle(store, src, "talla")
    msg = json.dumps(state.received[-1:], ensure_ascii=False)
    check("2. Vuelve una talla (cambio controlado: Oregon Ultra Tech talla 44)", r["sent"] == 1 and "44" in msg,
          f"{r['events']} evento(s), {r['sent']} aviso confirmado (id {state.received and 'PILOTO-%04d' % state.n})")

    for vv in next(x for x in state.catalog["products"] if x["handle"].startswith("dr-martens"))["variants"]:
        vv["price"] = "224.00"
    r = cycle(store, src, "precio")
    msg = json.dumps(state.received[-1:], ensure_ascii=False)
    check("3. Bajada de precio (cambio controlado: Dr. Martens 280 → 224 €, −20 %)", r["sent"] == 1 and "224" in msg,
          f"{r['events']} evento(s), {r['sent']} aviso; historial de precio guardado")

    state.discord_down = True
    v, _ = _variant(state, "autry-medalist-low-goatskin-aulmgg04", "39")
    v["available"] = True
    r = cycle(store, src, "caida")
    check("4. Discord caído al detectar (Autry talla 39 vuelve)", r["sent"] == 0 and r["pending"] == 1 and r["delivery_error"],
          f"aviso guardado en bandeja (pendientes: {r['pending']}); error: {str(r['delivery_error'])[:60]}")

    store, src = Store(db), ShopifySource("FOOTDISTRICT", shop_url, deep_pages=1)   # reinicio del proceso
    r = cycle(store, src, "reinicio")
    check("5. Reinicio con Discord aún caído", r["sent"] == 0 and r["pending"] == 1 and r["events"] == 0,
          "tras reiniciar no se re-detecta ni se pierde: sigue 1 pendiente")

    before = state.n
    state.discord_down = False
    r = cycle(store, src, "recuperacion")
    check("6. Discord vuelve: se entrega lo pendiente", r["sent"] == 1 and r["pending"] == 0 and state.n == before + 1,
          f"entregado 1 aviso (id PILOTO-{state.n:04d}); bandeja vacía")

    store, src = Store(db), ShopifySource("FOOTDISTRICT", shop_url, deep_pages=1)
    n = state.n
    r = cycle(store, src, "sin_dup")
    r = cycle(store, src, "sin_dup2")
    check("7. Otro reinicio + 2 ciclos: sin duplicados", state.n == n, f"mensajes totales recibidos: {state.n}")

    last = store.last_delivery().get("FOOTDISTRICT")
    check("8. Último mensaje confirmado registrado", last is not None, f"{last}")
    unverified = all("Beneficio neto" not in json.dumps(p, ensure_ascii=False) for p in state.received)
    check("9. Ningún aviso publica beneficio sin ventas verificadas", unverified, "market_data vacío → sin cifras de beneficio")
    shop.shutdown(); disc.shutdown()
    return {"ok": ok_all, "steps": steps, "received": state.received}


def write_log(res: dict, path: Path = ROOT / "docs/v07/PILOTO_REGISTRO.md"):
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%d/%m/%Y %H:%M")
    L = [f"# Registro del piloto local (ejecutado {now}, Madrid)", "",
         "**Tipo de datos:** CAPTURA REAL (footdistrict.com, 20-nov-2026 12:08 Madrid) + cambios CONTROLADOS aplicados "
         "en un servidor local + Discord SIMULADO. No se envió nada a un Discord real.", "",
         f"Resultado global: **{'TODO OK' if res['ok'] else 'HAY FALLOS'}**", "",
         "| Paso | Resultado | Detalle |", "|---|---|---|"]
    L += [f"| {a} | {b} | {c} |" for a, b, c in res["steps"]]
    L += ["", "## Avisos recibidos por el Discord simulado", ""]
    for p in res["received"]:
        e = (p.get("embeds") or [{}])[0]
        L.append(f"- **{e.get('title', '')}** — " + "; ".join(f"{f['name']}: {f['value']}" for f in e.get("fields", [])[:4])[:300])
    L += ["", "Repetir: `python tools/piloto.py` (o `VER_PANEL.bat`, que lo ejecuta antes de abrir el panel)."]
    path.write_text("\n".join(L), encoding="utf-8")
    return path


if __name__ == "__main__":
    res = run(db_path=sys.argv[1] if len(sys.argv) > 1 else None)
    print("Registro:", write_log(res))
    sys.exit(0 if res["ok"] else 1)
