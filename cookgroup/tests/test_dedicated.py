"""v1.0: cada canal dedicado CON fuente queda bien enrutado (prueba por canal, no «comparte motor»).
Positivo: su monitor (o su país / sus palabras) lo alimenta y el instalador crea el webhook con la clave que busca el bot.
Silencio: la señal de OTRA tienda no llega a ese canal.
"""
import tomllib
from pathlib import Path

import pytest

from cookgroup.config import load_config
from cookgroup.dedicated import load_dedicated
from cookgroup.server_setup import load_design, make_plan

ROOT = Path(__file__).resolve().parents[1]
DED = tomllib.loads((ROOT / "config/canales_dedicados.toml").read_text())
CH = [c for cat in DED["categoria"] for c in cat["canal"] if c["estado"] == "construido"]
CFG = load_config(ROOT / "config/monitors.toml")
NAMES = {m.name: m for m in CFG.monitors}
D = load_dedicated(ROOT / "config/canales_dedicados.toml")
PLAN = make_plan(load_design(ROOT / "config/servidor.toml"), [], [], set())
ENVKEYS = {k for _, k in PLAN.webhooks}


@pytest.mark.parametrize("c", CH, ids=[c["nombre"] for c in CH])
def test_dedicated_channel_routing(c):
    key = c["fuente"].split(":", 1)[1]
    assert f"DISCORD_WEBHOOK_{key.upper()}" in ENVKEYS                  # el instalador crea su webhook
    if c["clase"] == "tienda":
        assert c["monitores"] and all(m in NAMES for m in c["monitores"])
        for m in c["monitores"]:
            assert key in D.channels_for(m, NAMES[m].country, "")          # positivo
        other = next(n for n in NAMES if n not in c["monitores"])
        assert key not in D.channels_for(other, "XX", "")                  # silencio: otra tienda no entra
    elif c["clase"] == "región":
        assert key in D.channels_for("x", c["pais"], "") and key not in D.channels_for("x", "ES", "")
    elif c["clase"] == "tema":
        w = c["palabras"][0]
        assert key in D.channels_for("x", "ES", f"Producto {w.upper()} Classic") and key not in D.channels_for("x", "ES", "Nike Dunk")
