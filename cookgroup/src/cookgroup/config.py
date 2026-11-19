from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


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


@dataclass
class Config:
    defaults: dict
    monitors: list[MonitorConfig]

    def webhook_for(self, channel: str) -> str | None:
        return os.environ.get(f"DISCORD_WEBHOOK_{channel.upper()}")


def load_config(path: str | Path) -> Config:
    raw = tomllib.loads(Path(path).read_text())
    mons = [MonitorConfig(**m) for m in raw.get("monitor", [])]
    names = [m.name for m in mons]
    if len(names) != len(set(names)):
        raise ValueError("Nombres de monitor duplicados")
    for m in mons:
        if m.interval_seconds < 30:
            raise ValueError(f"{m.name}: interval_seconds < 30 no permitido (respeto a la fuente)")
    return Config(raw.get("defaults", {}), mons)
