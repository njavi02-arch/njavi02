"""v1.6 · Mide el intervalo REAL entre el inicio de dos lecturas de una misma tienda.

Dos modos:

  python tools/medir_intervalos.py --simulacion
      SIMULACIÓN LOCAL (sin red). Lanza un hilo por monitor, como el bot, con el mismo cálculo de espera (next_wait)
      y el mismo límite por dominio (ratelimit.wait_turn). Los tiempos van a escala 1/60 (60 s → 1 s) para que tarde
      poco. Incluye una tienda muy lenta y otra que falla, para ver si retrasan a BSTN o al resto.

  python tools/medir_intervalos.py --real --monitores bstn-eu,footlocker-es,zalando-es --ciclos 3
      MEDICIÓN REAL desde tu PC (solo lectura, sin Discord). Usa las fuentes de producción de config/monitors.toml y
      respeta el intervalo configurado de cada una (BSTN 60 s; JSON-LD 300 s). Escribe medicion_intervalos.csv.
"""
from __future__ import annotations

import argparse
import csv
import random
import statistics
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cookgroup import ratelimit  # noqa: E402
from cookgroup.runner import next_wait, start_to_start  # noqa: E402


class _Cfg:
    def __init__(self, name, interval):
        self.name, self.interval_seconds = name, interval


def _worker(name, interval, fetch, stop, starts, scale, results):
    cfg, failures = _Cfg(name, interval), 0
    while not stop.is_set():
        starts[name].append(time.monotonic())
        t0 = time.monotonic()
        try:
            fetch()
            res = {"ok": True}
            failures = 0
        except Exception as e:  # noqa: BLE001
            res = {"ok": False, "error": str(e)}
            failures += 1
        results[name].append(round((time.monotonic() - t0) / scale, 1))
        wait, _ = next_wait(cfg, res, failures, 1800)
        wait = start_to_start(wait, (time.monotonic() - t0) / scale, res["ok"])   # igual que el bot (v1.6)
        stop.wait(wait * scale)


def _report(starts, durs, intervals, scale, label):
    rows = []
    for name, st in starts.items():
        gaps = [(b - a) / scale for a, b in zip(st, st[1:])]
        rows.append({"monitor": name, "configurado_s": intervals[name], "lecturas": len(st),
                     "observado_mediana_s": round(statistics.median(gaps), 1) if gaps else None,
                     "observado_max_s": round(max(gaps), 1) if gaps else None,
                     "duracion_ciclo_mediana_s": statistics.median(durs[name]) if durs[name] else None})
    print(f"\n{label}\n" + "-" * len(label))
    print(f"{'monitor':<22}{'config':>8}{'lecturas':>10}{'observado':>11}{'máx':>8}{'ciclo':>8}")
    for r in rows:
        print(f"{r['monitor']:<22}{r['configurado_s']:>8}{r['lecturas']:>10}{str(r['observado_mediana_s']):>11}"
              f"{str(r['observado_max_s']):>8}{str(r['duracion_ciclo_mediana_s']):>8}")
    return rows


def simulacion(segundos_reales: float = 40.0, scale: float = 1 / 60) -> list[dict]:
    """Escala 1/60: 40 s reales ≈ 40 min simulados."""
    random.seed(7)
    ratelimit.DEFAULT_MIN_INTERVAL = 2.0 * scale
    monitors = {                                   # nombre: (intervalo s, dominio, latencia media s, falla)
        "bstn-eu": (60, "https://www.bstn.com", 1.5, False),
        "footlocker-es": (300, "https://www.footlocker.es", 3.0, False),
        "footlocker-fr": (300, "https://www.footlocker.fr", 3.0, False),
        "zalando-es": (300, "https://www.zalando.es", 2.0, False),
        "zalando-fr": (300, "https://www.zalando.fr", 2.0, False),
        "tienda-lenta": (300, "https://lenta.example", 45.0, False),    # responde en ~45 s
        "tienda-caida": (300, "https://caida.example", 20.0, True),     # agota el tiempo y falla
        "asics-es": (300, "https://www.asics.com", 2.5, False),
    }
    for i in range(30):                                                # ruido: 30 tiendas Shopify a 600 s
        monitors[f"shopify-{i:02d}"] = (600, f"https://s{i}.example", random.uniform(0.5, 4), False)

    def make_fetch(dom, lat, fails, pages):
        def fetch():
            for _ in range(pages):                 # listado + fichas: cada petición respeta el turno del dominio
                ratelimit.wait_turn(dom)
                time.sleep(random.uniform(0.6, 1.4) * lat * scale)
            if fails:
                raise TimeoutError("sin respuesta")
        return fetch
    stop = threading.Event()
    starts = {n: [] for n in monitors}
    durs = {n: [] for n in monitors}
    ths = []
    for n, (iv, dom, lat, fails) in monitors.items():
        pages = 2 if n == "bstn-eu" else 5 if not n.startswith("shopify") else 1
        th = threading.Thread(target=_worker, args=(n, iv, make_fetch(dom, lat, fails, pages), stop, starts, scale, durs),
                              daemon=True)
        th.start()
        ths.append(th)
    time.sleep(segundos_reales)
    stop.set()
    rows = _report({k: v for k, v in starts.items() if not k.startswith("shopify")},
                   durs, {k: v[0] for k, v in monitors.items()}, scale,
                   f"SIMULACIÓN local (escala 1/60, {segundos_reales:.0f} s reales ≈ {segundos_reales / scale / 60:.0f} min)")
    return rows


def real(nombres: list[str], ciclos: int, out: Path) -> list[dict]:
    from cookgroup.config import load_config
    from cookgroup.runner import make_source
    cfg = load_config(ROOT / "config/monitors.toml")
    mons = {m.name: m for m in cfg.monitors}
    stop, starts, durs, ths = threading.Event(), {}, {}, []
    for n in nombres:
        m = mons[n]
        src = make_source(m)
        starts[n], durs[n] = [], []
        th = threading.Thread(target=_worker, args=(n, m.interval_seconds, src.fetch, stop, starts, 1.0, durs), daemon=True)
        th.start()
        ths.append(th)
    longest = max(mons[n].interval_seconds for n in nombres)
    deadline = time.monotonic() + longest * (ciclos - 1) * 1.15 + 120
    while time.monotonic() < deadline and not all(len(starts[n]) >= ciclos for n in nombres):
        time.sleep(1)
    stop.set()
    rows = _report(starts, durs, {n: mons[n].interval_seconds for n in nombres}, 1.0, "MEDICIÓN REAL desde este equipo")
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\nGuardado: {out}")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulacion", action="store_true")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--monitores", default="bstn-eu,footlocker-es,zalando-es,asics-es")
    ap.add_argument("--ciclos", type=int, default=3)
    ap.add_argument("--segundos", type=float, default=40.0)
    a = ap.parse_args()
    if a.real:
        real(a.monitores.split(","), a.ciclos, ROOT / "medicion_intervalos.csv")
    else:
        simulacion(a.segundos)
