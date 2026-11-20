"""Canales dedicados (v1.0): qué canales extra recibe cada señal. Fuente: config/canales_dedicados.toml (generado)."""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


def key_of(fuente: str) -> str:
    return fuente.split(":", 1)[1] if fuente.startswith("bot:") else ""


@dataclass
class Dedicated:
    by_monitor: dict[str, list[str]] = field(default_factory=dict)   # monitor → claves de canal de tienda
    by_country: dict[str, list[str]] = field(default_factory=dict)   # país → claves de canal de región
    topics: list[tuple[str, list[str]]] = field(default_factory=list)  # (clave, palabras)

    def channels_for(self, monitor_name: str, country: str | None, text: str) -> list[str]:
        out = list(self.by_monitor.get(monitor_name, []))
        out += self.by_country.get((country or "").upper(), [])
        low = text.lower()
        out += [k for k, kws in self.topics if any(re.search(r"(?<![a-z0-9])" + re.escape(w), low) for w in kws)]
        return list(dict.fromkeys(out))


def load_dedicated(path: str | Path = "config/canales_dedicados.toml") -> Dedicated:
    p = Path(path)
    d = Dedicated()
    if not p.exists():
        return d
    for cat in tomllib.loads(p.read_text(encoding="utf-8")).get("categoria", []):
        for c in cat.get("canal", []):
            k = key_of(c.get("fuente", ""))
            if not k or c.get("estado") != "construido":
                continue
            if c.get("clase") == "tienda":
                for m in c.get("monitores", []):
                    d.by_monitor.setdefault(m, []).append(k)
            elif c.get("clase") == "región" and c.get("pais"):
                d.by_country.setdefault(c["pais"].upper(), []).append(k)
            elif c.get("clase") == "tema" and c.get("palabras"):
                d.topics.append((k, [w.lower() for w in c["palabras"]]))
    return d
