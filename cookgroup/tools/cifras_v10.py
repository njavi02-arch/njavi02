"""Las cinco cifras de avance (con denominador), calculadas desde los archivos, más tiendas y monitores aparte.
→ docs/v10/CIFRAS.json y docs/v10/CIFRAS.md
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main():
    ref = list(csv.DictReader(open(ROOT / "docs/v08/canales.csv", encoding="utf-8")))
    eqv = {r["canal"]: r for r in csv.DictReader(open(ROOT / "docs/v10/EQUIVALENTES.csv", encoding="utf-8"))}
    mine = {r["canal"]: r for r in csv.DictReader(open(ROOT / "docs/v09/CANALES_MI_SERVIDOR.csv", encoding="utf-8"))}
    real_path = ROOT / "docs/v09/ENTREGAS_REALES.csv"
    real = [r for r in csv.DictReader(open(real_path, encoding="utf-8"))] if real_path.exists() else []
    installed_path = ROOT / "docs/v10/INSTALADOS.txt"
    installed = set(installed_path.read_text().split()) if installed_path.exists() else set()

    comprob = sum(1 for r in ref if r["nivel_evidencia"].startswith("función comprobada"))
    full = routed = 0
    for r in ref:
        e = eqv.get(r["canal"], {})
        names = re.findall(r"#([\w\-áéíóúñü]+)", e.get("equivalente_dedicado", "") or r["equivalente"])
        sts = [mine[n]["estado"] for n in names if n in mine]
        if any(s == "probado localmente" or s == "entrega real confirmada" for s in sts):
            full += 1
        elif any(s.startswith("enrutado probado") for s in sts):
            routed += 1
    probados = sum(1 for r in mine.values() if r["estado"] in ("probado localmente", "entrega real confirmada"))
    verified = sum(1 for r in mine.values() if r["estado"] == "entrega real confirmada")
    from cookgroup.config import load_config
    cfg = load_config(ROOT / "config/monitors.toml")
    act = [m for m in cfg.monitors if m.enabled]
    doms = {urlparse(m.base_url).netloc.removeprefix("www.") for m in act}
    d = {"funciones_comprobadas": [comprob, len(ref)],
         "equivalente_supera_prueba": [full, len(ref)], "equivalente_solo_enrutado": [routed, len(ref)],
         "propios_probados_localmente": [probados, len(mine)],
         "propios_instalados": [len(installed & set(mine)), len(mine)],
         "propios_verificados_discord": [verified, len(mine)],
         "monitores_activos": len(act), "fuentes_unicas": len(doms),
         "entregas_reales_confirmadas": sum(1 for r in real if r["estado"] == "entrega real confirmada")}
    (ROOT / "docs/v10/CIFRAS.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# Cifras v1.0 (calculadas desde los archivos)", "",
         f"1. Canales de referencia con función comprobada: **{comprob} / {len(ref)}**",
         f"2. Canales de referencia con un equivalente que supera su prueba: **{full} / {len(ref)}** "
         f"(+{routed} con solo prueba de enrutado; la lectura de su fuente se comprueba en tu PC)",
         f"3. Canales propios probados localmente: **{probados} / {len(mine)}**",
         f"4. Canales propios instalados en tu Discord: **{len(installed & set(mine))} / {len(mine)}**",
         f"5. Canales propios verificados en Discord: **{verified} / {len(mine)}**", "",
         f"Aparte: {len(act)} monitores activos sobre {len(doms)} fuentes únicas; entregas reales confirmadas: {d['entregas_reales_confirmadas']}."]
    (ROOT / "docs/v10/CIFRAS.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
