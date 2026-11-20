"""v1.0: recorrido COMPLETO desde el programa que arranca el dueño (runner._loop) hasta el canal de destino.

Tienda local con la CAPTURA REAL de Footdistrict (20-nov) → CAMBIO SIMULADO (vuelve la EU 44,5 de las New Balance)
→ el monitor lo detecta → lo publica en #footdistrict (canal dedicado) y en #sneakers-eu (agregado) → menciona al
suscriptor UNA vez → tras reiniciar el programa no repite nada. Discord simulado que registra en qué webhook llega.
"""
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import cookgroup.runner as runner
from cookgroup.config import Config, MonitorConfig
from cookgroup.market import FileMarketProvider
from cookgroup.store import Store

FIX = Path(__file__).parent / "fixtures/footdistrict_nb_asics_REAL_2026-11-20.json"


def _servers(cat, got):
    class Shop(BaseHTTPRequestHandler):
        def do_GET(self):
            p = self.path.split("?")[0]
            body = {"currency": "EUR"} if p == "/cart.js" else {"products": cat["products"]} if p.endswith("products.json") else None
            if body is None:
                self.send_response(404); self.end_headers(); return
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps(body).encode())

        def log_message(self, *a):
            pass

    class Discord(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            got.append((self.path.split("?")[0].rsplit("/", 1)[-1], json.loads(self.rfile.read(n))))
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps({"id": f"m{len(got)}"}).encode())

        def log_message(self, *a):
            pass
    out = []
    for h in (Shop, Discord):
        s = ThreadingHTTPServer(("127.0.0.1", 0), h)
        threading.Thread(target=s.serve_forever, daemon=True).start()
        out.append(s)
    return out


def test_program_to_destination_with_restart(tmp_path, monkeypatch):
    cat, got = json.loads(FIX.read_text()), []
    shop, disc = _servers(cat, got)
    hook = f"http://127.0.0.1:{disc.server_port}/api/webhooks/1/"
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    monkeypatch.setenv("DISCORD_WEBHOOK_SNEAKERS", hook + "sneakers-eu")
    monkeypatch.setenv("DISCORD_WEBHOOK_TIENDA_FOOTDISTRICT", hook + "footdistrict")
    monkeypatch.delenv("DISCORD_WEBHOOK_DEFAULT", raising=False)
    (tmp_path / "m.toml").write_text('[[miembro]]\nid = "900"\nnombre = "s"\nmarcas = ["New Balance"]\nregiones = ["Envío a España"]\n'
                                     'tallas = ["44,5"]\nactivo = true\n[[miembro]]\nid = "901"\nnombre = "x"\nmarcas = ["Nike"]\ntallas = ["44,5"]\n')
    (tmp_path / "d.toml").write_text('[[categoria]]\nnombre = "T"\n[[categoria.canal]]\nnombre = "footdistrict"\nclase = "tienda"\n'
                                     'fuente = "bot:tienda_footdistrict"\nestado = "construido"\nmonitores = ["footdistrict"]\npalabras = []\n')
    m = MonitorConfig("footdistrict", "shopify", "FOOTDISTRICT", f"http://127.0.0.1:{shop.server_port}", channel="sneakers",
                      country="ES", ships_es="sí", interval_seconds=1)
    cfg = Config({"members_file": str(tmp_path / "m.toml"), "dedicated_file": str(tmp_path / "d.toml")}, [m])
    db = str(tmp_path / "c.db")

    def run_for(seconds, mutate=None):
        stop = threading.Event()
        t = threading.Thread(target=runner._loop, args=(m, cfg, Store(db), FileMarketProvider(tmp_path / "x.json"), stop))
        t.start()
        time.sleep(1.5)
        if mutate:
            mutate()
        time.sleep(seconds)
        stop.set()
        t.join(5)

    def nb_445_back():
        p = next(x for x in cat["products"] if "990v7" in x["title"])
        next(v for v in p["variants"] if v["title"] == "44.5")["available"] = True

    run_for(2.5, nb_445_back)
    chans = [c for c, _ in got]
    assert chans.count("footdistrict") == 1 and chans.count("sneakers-eu") == 1, chans
    mentions = [p.get("allowed_mentions", {}).get("users") for _, p in got]
    assert mentions.count(["900"]) == 1 and ["901"] not in mentions          # una mención, solo al que encaja
    assert dict(got)["footdistrict"]["allowed_mentions"]["users"] == ["900"]  # la mención va en el canal de la tienda
    n = len(got)
    run_for(2.5)                                                            # REINICIO del programa: nada se repite
    assert len(got) == n
    shop.shutdown(); disc.shutdown()
