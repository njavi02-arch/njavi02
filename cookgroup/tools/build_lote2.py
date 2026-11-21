"""Lote 2 (v1.1): tiendas Shopify europeas con envío a España, validadas EN VIVO el 21-nov-2026 y con muestra real
fechada. Genera config/lote2_tiendas.toml (lo leen el directorio, el panel y el generador de canales dedicados).

Una tienda entra solo si:
  · /meta.json dice que envía a España y /products.json responde con disponibilidad por variante
    (docs/v11/validacion_shopify_2026-11-21.txt), y
  · su muestra real (tests/fixtures/muestras_shopify_REAL_2026-11-21.txt) pasa tests/test_tiendas_lote2.py
    (restock, bajada de precio y sin repetir). Las que el test salta quedan como candidatas.
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cookgroup.config import load_config  # noqa: E402
from cookgroup.store_directory import merchant_key  # noqa: E402


def main():
    val = {}
    for tok in (ROOT / "docs/v11/validacion_shopify_2026-11-21.txt").read_text(encoding="utf-8").splitlines()[-1].split():
        d, c, es, cmp_ = tok.split(":")
        val[d] = (c, es, cmp_)
    samples = [ln.split("|")[0] for ln in (ROOT / "tests/fixtures/muestras_shopify_REAL_2026-11-21.txt").read_text(encoding="utf-8").splitlines()
               if ln and not ln.startswith("#")]
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-rs", "tests/test_tiendas_lote2.py"], cwd=ROOT,
                       capture_output=True, text=True, env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"})
    skipped = set(re.findall(r"SKIPPED.*?: ([\w.\-]+): el producto", r.stdout))
    print(r.stdout.strip().splitlines()[-1])
    failed = set(re.findall(r"FAILED .*?\[([\w.\-]+)\]", r.stdout))
    names = {}
    for x in csv.DictReader(open(ROOT / "docs/inventory.csv", encoding="utf-8")):
        names.setdefault(merchant_key(x["dominio"]), x["tienda"])
    mons, siblings = {}, {}
    for m in load_config(ROOT / "config/monitors.toml").monitors:
        dom = urlparse(m.base_url).netloc.removeprefix("www.")
        mons.setdefault(dom, m.name)
        siblings.setdefault(merchant_key(dom), []).append(m.name)   # versiones regionales del mismo comercio
    import tomllib
    existing = {}                                   # monitor → canal de tienda que ya existe como equivalente de la referencia
    for cat in tomllib.loads((ROOT / "config/canales_dedicados.toml").read_text(encoding="utf-8")).get("categoria", []):
        for c in cat["canal"]:
            if c.get("clase") == "tienda" and "lote" not in c.get("equivalente_de", ""):
                for m in c.get("monitores", []):
                    existing.setdefault(m, c["nombre"])
    used, out, cand = set(), ["# GENERADO por tools/build_lote2.py — no editar a mano. Fuente: validación en vivo y muestras del 21-nov-2026.", ""], []
    for d in samples:
        k = merchant_key(d)
        c, es, _ = val.get(d, ("", "?", "0"))
        if d in skipped or d in failed:
            cand.append(d)
            continue
        mon = mons.get(d) or f"shop:{d}"
        canal = existing.get(mon) or re.sub(r"[^a-z0-9-]+", "-", k.lower()).strip("-")
        if canal in used:
            continue
        used.add(canal)
        nombre = names.get(k) or k.replace("-", " ").title()
        if nombre.isupper() and len(nombre) > 4:
            nombre = nombre.title()
        out += ["[[tienda]]", f'nombre = "{nombre}"', f'canal = "{canal}"', f'pais = "{c}"', f'web = "https://{d}/"',
                f'envio_es = "{"sí" if es == "s" else "no" if es == "n" else "por confirmar"} (ships_to_countries, 21-nov)"',
                'raffle_es = "—"', "monitores = [" + ", ".join(f'"{x}"' for x in dict.fromkeys([mon] + siblings.get(k, []))) + "]", 'raffle = "sin-fuente"', 'lanzamiento = "por-probar"',
                'restock = "probado"', 'rebaja = "probado"',
                f'prueba_restock = "test_tiendas_lote2[{d}] · muestra real 21-nov"',
                f'prueba_rebaja = "test_tiendas_lote2[{d}] · muestra real 21-nov"', 'lote = 2', ""]
    out += [f"# Candidatas pendientes de otra muestra: {' '.join(cand) or '—'}"]
    (ROOT / "config/lote2_tiendas.toml").write_text("\n".join(out), encoding="utf-8")
    print(f"lote 2: {len(used)} tiendas con canal · candidatas pendientes: {cand}")


if __name__ == "__main__":
    main()
