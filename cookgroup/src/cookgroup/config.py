from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .rules import PingRule

SOURCE_TYPES = {"shopify", "rss", "bstn", "jsonld"}
LAUNCH_TYPES = {"bstn"}   # fuentes de calendario de lanzamientos (ciclo propio)


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
    pages: int = 1                       # páginas de 250 productos por consulta
    collection: str | None = None        # Shopify: vigilar solo esta colección (p. ej. "launches")
    deep_pages: int = 6                  # Shopify: paginación rotatoria (1 página extra por ciclo, hasta esta)
    watch_keywords: list[str] = field(default_factory=list)  # Shopify: modelos a seguir ficha a ficha
    country: str | None = None           # país de la tienda (ISO-2) para la alerta y el inventario
    region: str | None = None            # etiqueta de región para alertas y filtros (p. ej. "eu", "uk", "us")
    min_temperature: int | None = None   # feeds Pepper: solo chollos con ≥ N° de la comunidad
    dedupe_group: str | None = None
    # --- fuentes de lanzamientos (type = "bstn")
    regions: list[str] = field(default_factory=lambda: ["eu_es"])
    listings: list[str] = field(default_factory=lambda: ["men/upcoming", "women/upcoming/footwear"])
    launch_channels: dict = field(default_factory=lambda: {"launch": "lanzamientos", "raffle": "raffles",
                                                          "restock": "restocks", "digest": "lanzamientos"})
    product_checks_per_cycle: int = 4
    # --- fichas con datos estructurados (type = "jsonld")
    listing_urls: list[str] = field(default_factory=list)
    product_link_pattern: str = "/p/"
    watch_urls: list[str] = field(default_factory=list)
    products_per_cycle: int = 6      # misma tienda con varios dominios (.fr/.eu) → una sola alerta


@dataclass
class Config:
    defaults: dict
    monitors: list[MonitorConfig]
    ping_rules: list[PingRule] = field(default_factory=list)

    def webhook_for(self, channel: str) -> str | None:
        """Webhook del canal; si no hay, DISCORD_WEBHOOK_DEFAULT (útil para probar todo en un solo canal)."""
        key = "DISCORD_WEBHOOK_" + "".join(c if c.isalnum() else "_" for c in channel.upper())
        return os.environ.get(key) or os.environ.get("DISCORD_WEBHOOK_DEFAULT")


def load_config(path: str | Path) -> Config:
    raw = tomllib.loads(Path(path).read_text())
    mons = [MonitorConfig(**m) for m in raw.get("monitor", [])]
    names = [m.name for m in mons]
    if len(names) != len(set(names)):
        raise ValueError("Nombres de monitor duplicados")
    for m in mons:
        if m.type not in SOURCE_TYPES:
            raise ValueError(f"{m.name}: tipo '{m.type}' no soportado ({sorted(SOURCE_TYPES)})")
        if not 1 <= m.deep_pages <= 40:
            raise ValueError(f"{m.name}: deep_pages debe estar entre 1 y 40")
        if not 1 <= m.pages <= 4:
            raise ValueError(f"{m.name}: pages debe estar entre 1 y 4")
        min_iv = 300 if m.type in ("rss", "bstn", "jsonld") else 30
        if m.interval_seconds < min_iv:
            raise ValueError(f"{m.name}: interval_seconds < {min_iv} no permitido para {m.type} (respeto a la fuente)")
    for r in raw.get("defaults", {}).get("discount_routes", []):
        if not (0 < float(r.get("min_pct", 0)) < 100) or not r.get("channel"):
            raise ValueError("discount_routes: cada ruta necesita min_pct (0-100) y channel")
    rules = [PingRule.from_dict(r) for r in raw.get("ping_rule", [])]
    if len({r.name for r in rules}) != len(rules):
        raise ValueError("Nombres de ping_rule duplicados")
    return Config(raw.get("defaults", {}), mons, rules)
