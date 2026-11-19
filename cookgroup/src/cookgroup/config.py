from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .rules import PingRule

SOURCE_TYPES = {"shopify", "rss"}


@dataclass
class MonitorConfig:
    name: str
    type: str
    store: str
    base_url: str
    currency: str = "EUR"
    interval_seconds: int = 120
    channel: str = "restocks"
    enabled: bool = True
    include_vendors: list[str] = field(default_factory=list)
    include_keywords: list[str] = field(default_factory=list)
    exclude_keywords: list[str] = field(default_factory=list)
    skip_kids_sizes: bool = False        # ruido observado en la referencia (tallas Y/C/GS)
    allow_unknown_price: bool = False    # feeds RSS de chollos pueden no traer precio
    dedupe_group: str | None = None      # misma tienda con varios dominios (.fr/.eu) → una sola alerta


@dataclass
class Config:
    defaults: dict
    monitors: list[MonitorConfig]
    ping_rules: list[PingRule] = field(default_factory=list)

    def webhook_for(self, channel: str) -> str | None:
        return os.environ.get(f"DISCORD_WEBHOOK_{channel.upper()}")


def load_config(path: str | Path) -> Config:
    raw = tomllib.loads(Path(path).read_text())
    mons = [MonitorConfig(**m) for m in raw.get("monitor", [])]
    names = [m.name for m in mons]
    if len(names) != len(set(names)):
        raise ValueError("Nombres de monitor duplicados")
    for m in mons:
        if m.type not in SOURCE_TYPES:
            raise ValueError(f"{m.name}: tipo '{m.type}' no soportado ({sorted(SOURCE_TYPES)})")
        min_iv = 300 if m.type == "rss" else 30
        if m.interval_seconds < min_iv:
            raise ValueError(f"{m.name}: interval_seconds < {min_iv} no permitido para {m.type} (respeto a la fuente)")
    for r in raw.get("defaults", {}).get("discount_routes", []):
        if not (0 < float(r.get("min_pct", 0)) < 100) or not r.get("channel"):
            raise ValueError("discount_routes: cada ruta necesita min_pct (0-100) y channel")
    rules = [PingRule.from_dict(r) for r in raw.get("ping_rule", [])]
    if len({r.name for r in rules}) != len(rules):
        raise ValueError("Nombres de ping_rule duplicados")
    return Config(raw.get("defaults", {}), mons, rules)
