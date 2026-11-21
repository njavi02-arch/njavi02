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
    signals: dict[str, set[str]] = field(default_factory=dict)       # v1.1: canal de tienda → señales PROBADAS

    def allows(self, channel_key: str, signal: str) -> bool:
        """Un canal de tienda del lote solo publica las señales probadas con datos reales (sin lista = todas)."""
        s = self.signals.get(channel_key)
        return s is None or signal in s

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
                if c.get("senales") is not None:
                    d.signals[k] = {x.strip() for x in c["senales"].split(",") if x.strip()}
                for m in c.get("monitores", []):
                    d.by_monitor.setdefault(m, []).append(k)
            elif c.get("clase") == "región" and c.get("pais"):
                d.by_country.setdefault(c["pais"].upper(), []).append(k)
            elif c.get("clase") == "tema" and c.get("palabras"):
                d.topics.append((k, [w.lower() for w in c["palabras"]]))
    return d


SIGNAL_OF = {"new_product": "LANZAMIENTO", "restock": "RESTOCK", "new_size": "RESTOCK", "price_drop": "REBAJA",
             "price_error": "REBAJA"}


def labelled(payload: dict, signal: str) -> dict:
    """Etiqueta visible en el canal de la tienda: «RESTOCK · …», «REBAJA · …», «LANZAMIENTO · …», «RAFFLE · …»."""
    import copy
    p = copy.deepcopy(payload)
    for e in p.get("embeds", [])[:1]:
        if e.get("title") and not e["title"].startswith(signal):
            e["title"] = f"{signal} · {e['title']}"[:256]
    return p
