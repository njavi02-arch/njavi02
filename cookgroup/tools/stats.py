"""Cifras de cookgroup generadas desde la configuración, el inventario y (si existe) la base de datos.

Uso:  python tools/stats.py [--db cookgroup.db] [--out docs/CIFRAS.md] [--json docs/v07/cifras.json]
Nada se escribe a mano: si una cifra cambia, se vuelve a ejecutar.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cookgroup.config import load_config  # noqa: E402

# Cobertura por tipo de aviso SEGÚN EL DISEÑO DEL ADAPTADOR (completa = ve todo el universo de la fuente;
# parcial = solo una parte: página 1 + rotación, fichas vigiladas, listados concretos).
CAPS = {
    "shopify": {"producto nuevo": "completa", "vuelta a stock": "parcial", "talla nueva": "parcial",
                "bajada de precio": "parcial", "price error": "parcial"},
    "rss": {"chollo nuevo": "completa"},
    "bstn": {"lanzamiento anunciado": "completa", "raffle abierto/cierre": "completa", "fecha cambiada": "completa",
             "vuelve talla": "parcial"},
    "jsonld": {"producto nuevo": "parcial", "vuelta a stock": "parcial", "bajada de precio": "parcial"},
}


def dom(m) -> str:
    u = m.base_url or (m.listing_urls[0] if m.listing_urls else "")
    return urlparse(u).netloc.lower().removeprefix("www.") if u else m.store.lower()


def compute(config: str, db: str | None, inventory: Path) -> dict:
    cfg = load_config(ROOT / config if not Path(config).is_absolute() else config)
    import tomllib
    toml_mons = tomllib.loads((ROOT / config).read_text())["monitor"]
    csv_rows = list(csv.DictReader(open(ROOT / cfg.defaults["shopify_stores_file"], encoding="utf-8")))
    en = [m for m in cfg.monitors if m.enabled]
    out = {
        "generado": datetime.now(ZoneInfo("Europe/Madrid")).strftime("%d/%m/%Y %H:%M"),
        "monitores_toml": len(toml_mons),
        "filas_csv": len(csv_rows),
        "filas_csv_activas": sum(r.get("enabled", "1") not in ("0", "false", "no") for r in csv_rows),
        "monitores_cargados": len(cfg.monitors),
        "monitores_activos": len(en),
        "activos_por_tipo": dict(collections.Counter(m.type for m in en)),
        "tiendas_unicas_activas": len({dom(m) for m in en}),
    }
    inv = list(csv.DictReader(open(inventory, encoding="utf-8")))
    out["inventario_filas"] = len(inv)
    out["inventario_referencia"] = sum(r["en_referencia"] == "sí" for r in inv)
    out["inventario_propias"] = len(inv) - out["inventario_referencia"]
    out["inventario_cobertura"] = dict(collections.Counter(r["cobertura"] for r in inv))
    cov = collections.defaultdict(lambda: collections.Counter())
    for m in en:
        for ev, level in CAPS.get(m.type, {}).items():
            cov[ev][level] += 1
    out["cobertura_por_aviso"] = {k: dict(v) for k, v in cov.items()}
    if db and Path(db).exists():
        c = sqlite3.connect(db)
        q = lambda s: c.execute(s).fetchone()[0]
        out["bd"] = db
        out["lecturas_utiles"] = q("SELECT COUNT(DISTINCT source) FROM probe_results WHERE status='ÚTIL'") \
            + q("SELECT COUNT(*) FROM source_health WHERE last_ok IS NOT NULL AND COALESCE(last_items,0)>0 "
                "AND source NOT IN (SELECT source FROM probe_results WHERE status='ÚTIL')")
        out["eventos_detectados"] = q("SELECT COALESCE(SUM(events),0) FROM monitor_runs")
        out["envios_confirmados"] = q("SELECT COUNT(*) FROM alerts WHERE message_id IS NOT NULL AND message_id NOT IN ('','None')")
        out["envios_pendientes"] = q("SELECT COUNT(*) FROM outbox")
        out["comprobaciones_por_estado"] = dict(c.execute(
            "SELECT status, COUNT(*) FROM (SELECT source, status, MAX(checked_at) FROM probe_results GROUP BY source) GROUP BY status"
        ).fetchall())
    return out


def render(d: dict) -> str:
    L = [f"# Cifras de cookgroup (generadas {d['generado']}, Madrid)", "",
         "Generado por `python tools/stats.py`. No editar a mano.", "",
         "## Monitores", "",
         f"| Concepto | Cifra |", "|---|---:|",
         f"| Monitores en `config/monitors.toml` | {d['monitores_toml']} |",
         f"| Filas en `config/shopify_stores.csv` | {d['filas_csv']} (activas: {d['filas_csv_activas']}) |",
         f"| **Monitores activos** (`cookgroup check-config`) | **{d['monitores_activos']}** |",
         f"| **Fuentes únicas activas** (dominios distintos; incluye 5 webs de chollos) | **{d['tiendas_unicas_activas']}** |", ""]
    L += ["Por tipo: " + " · ".join(f"{k} {v}" for k, v in sorted(d["activos_por_tipo"].items())), ""]
    L += ["## Inventario (tiendas conocidas, no todas monitorizadas)", "",
          f"{d['inventario_filas']} filas = {d['inventario_referencia']} dominios vistos en el cookgroup de referencia + "
          f"{d['inventario_propias']} de investigación propia.", "",
          "Cobertura: " + " · ".join(f"{k} {v}" for k, v in sorted(d["inventario_cobertura"].items())), ""]
    L += ["## Cobertura por tipo de aviso (monitores activos)", "",
          "| Aviso | Completa | Parcial |", "|---|---:|---:|"]
    for ev, c in sorted(d["cobertura_por_aviso"].items()):
        L.append(f"| {ev} | {c.get('completa', 0)} | {c.get('parcial', 0)} |")
    L += ["", "*Completa*: el adaptador ve todo lo que publica la fuente. *Parcial*: solo una parte (página 1 + rotación de "
          "páginas profundas, fichas vigiladas o listados concretos); un cambio fuera de esa parte puede tardar o no verse.", ""]
    L += ["## Actividad medida", ""]
    if "bd" in d:
        sim = "piloto" in Path(d["bd"]).name
        L += [f"Base de datos: `{Path(d['bd']).name}`" + (" — **PILOTO LOCAL con Discord SIMULADO** (no son envíos a un Discord real)" if sim else ""), "",
              f"| Concepto | Cifra |", "|---|---:|",
              f"| Fuentes con lectura útil | {d['lecturas_utiles']} |",
              f"| Eventos detectados | {d['eventos_detectados']} |",
              f"| **Envíos confirmados por Discord** (con id de mensaje) | **{d['envios_confirmados']}** |",
              f"| Envíos pendientes en bandeja | {d['envios_pendientes']} |", ""]
        if d.get("comprobaciones_por_estado"):
            L += ["Última comprobación por fuente: " + " · ".join(f"{k} {v}" for k, v in d["comprobaciones_por_estado"].items()), ""]
    else:
        L += ["Sin base de datos: aún no hay actividad real registrada.", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/monitors.toml")
    ap.add_argument("--db")
    ap.add_argument("--out", default=str(ROOT / "docs/CIFRAS.md"))
    ap.add_argument("--json")
    a = ap.parse_args()
    d = compute(a.config, a.db, ROOT / "docs/inventory.csv")
    Path(a.out).write_text(render(d), encoding="utf-8")
    if a.json:
        Path(a.json).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(render(d))


if __name__ == "__main__":
    main()
