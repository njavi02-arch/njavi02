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
    ships_es: str = "por confirmar"      # "sí" / "no" / "por confirmar": sin "sí" no se publica beneficio
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
    page_adapter: str = ""           # v1.6: "footlocker" | "asics" (tallas desde el estado público de la ficha)


@dataclass
class Config:
    defaults: dict
    monitors: list[MonitorConfig]
    ping_rules: list[PingRule] = field(default_factory=list)

    def webhook_for(self, channel: str) -> str | None:
        """Webhook del canal; si no hay, DISCORD_WEBHOOK_DEFAULT (útil para probar todo en un solo canal)."""
        key = "DISCORD_WEBHOOK_" + "".join(c if c.isalnum() else "_" for c in channel.upper())
        return os.environ.get(key) or os.environ.get("DISCORD_WEBHOOK_DEFAULT")


SNEAKER_BRANDS = ["Nike", "Jordan", "Air Jordan", "adidas", "New Balance", "ASICS", "Salomon", "On", "Hoka", "Puma",
                  "Converse", "Vans", "Saucony", "Onitsuka", "Mizuno", "Reebok", "Merrell", "Clarks", "UGG", "Timberland"]
CATEGORY_PRESETS = {
    # categoría → filtros y frecuencia para tiendas cargadas en bloque (config/shopify_stores.csv)
    "sneakers/deporte": {"include_vendors": SNEAKER_BRANDS, "interval_seconds": 600},
    "baloncesto": {"include_vendors": SNEAKER_BRANDS, "interval_seconds": 600},
    "skate": {"include_vendors": SNEAKER_BRANDS + ["Nike SB", "Last Resort", "Emerica", "DC Shoes", "Etnies", "New Balance Numeric"],
              "interval_seconds": 900},
    "streetwear": {"include_vendors": [], "interval_seconds": 900},
    "moda/lujo": {"include_vendors": SNEAKER_BRANDS, "interval_seconds": 900},
    "outlet/retail": {"include_vendors": [], "interval_seconds": 900},
    "coleccionables/TCG": {"include_keywords": ["pokemon", "pokémon", "one piece", "lorcana", "yu-gi-oh", "yugioh", "magic",
                                                "dragon ball", "booster", "display", "etb", "elite trainer", "lego"],
                           "include_vendors": [], "interval_seconds": 900},
}
EU = {"ES", "FR", "DE", "IT", "NL", "BE", "AT", "DK", "SE", "PL", "CZ", "SK", "RO", "GR", "LU", "IE", "PT", "FI", "HU", "NO", "CH"}


def load_store_list(defaults: dict, *, base_dir: Path, existing: set[str]) -> list[MonitorConfig]:
    """Tiendas Shopify en bloque desde un CSV (domain,name,country,category,channel,enabled). Cada fila = un monitor."""
    import csv
    f = defaults.get("shopify_stores_file")
    if not f:
        return []
    path = Path(f) if Path(f).is_absolute() else base_dir.parent / f
    if not path.exists():
        return []
    out = []
    for r in csv.DictReader(path.open(encoding="utf-8")):
        dom = r["domain"].strip().lower()
        name = f"shop:{dom}"
        if not dom or r.get("enabled", "1").strip() in ("0", "no", "false") or name in existing:
            continue
        preset = CATEGORY_PRESETS.get(r.get("category", ""), CATEGORY_PRESETS["sneakers/deporte"])
        cc = (r.get("country") or "").upper() or None
        region = "eu" if cc in EU else ("uk" if cc == "GB" else (cc.lower() if cc else None))
        out.append(MonitorConfig(
            name=name, type="shopify", store=r.get("name") or dom, base_url=f"https://{dom}", currency="auto",
            interval_seconds=int(r.get("interval_seconds") or preset["interval_seconds"]),
            channel=r.get("channel") or "sneakers", country=cc, region=region,
            include_vendors=list(preset.get("include_vendors", [])), include_keywords=list(preset.get("include_keywords", [])),
            exclude_keywords=["gift card", "geschenkkarte", "carte cadeau", "tarjeta regalo"], skip_kids_sizes=True,
            deep_pages=int(defaults.get("bulk_deep_pages", 4))))
    return out


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
        # v1.1: BSTN a 60 s (lectura condicional ETag/304, compresión, espera de 2 s entre páginas, respeta 429)
        min_iv = 60 if m.type == "bstn" else 300 if m.type in ("rss", "jsonld") else 30
        if m.interval_seconds < min_iv:
            raise ValueError(f"{m.name}: interval_seconds < {min_iv} no permitido para {m.type} (respeto a la fuente)")
    for r in raw.get("defaults", {}).get("discount_routes", []):
        if not (0 < float(r.get("min_pct", 0)) < 100) or not r.get("channel"):
            raise ValueError("discount_routes: cada ruta necesita min_pct (0-100) y channel")
    mons += load_store_list(raw.get("defaults", {}), base_dir=Path(path).parent, existing={m.name for m in mons})
    # v1.1: las tiendas del lote con canal propio se leen cada `intervalo_lote_s` (Shopify y BSTN; JSON-LD mantiene su mínimo)
    lp = Path(path).parent / "lote_tiendas.toml"
    if lp.exists():
        lote = tomllib.loads(lp.read_text(encoding="utf-8"))
        iv = int(lote.get("intervalo_lote_s", 0))
        names_lote = {n for f in [lp] + sorted(lp.parent.glob("lote[0-9]*_tiendas.toml"))
                      for t in tomllib.loads(f.read_text(encoding="utf-8")).get("tienda", []) for n in t.get("monitores", [])}
        for m in mons:
            if iv and m.name in names_lote and m.type in ("shopify", "bstn"):
                m.interval_seconds = max(iv, 60 if m.type == "bstn" else 30)
    rules = [PingRule.from_dict(r) for r in raw.get("ping_rule", [])]
    if len({r.name for r in rules}) != len(rules):
        raise ValueError("Nombres de ping_rule duplicados")
    return Config(raw.get("defaults", {}), mons, rules)
