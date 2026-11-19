from __future__ import annotations

import re

from .config import MonitorConfig
from .models import Product


def product_passes(p: Product, cfg: MonitorConfig) -> bool:
    text = f"{p.title} {p.vendor or ''} {' '.join(p.tags)}".lower()
    if cfg.include_vendors:
        # palabra completa en marca o título: "On" no debe coincidir con "Converse"
        hay = f"{p.vendor or ''} {p.title}"
        if not any(re.search(rf"(?<![\w]){re.escape(v)}(?![\w])", hay, re.I) for v in cfg.include_vendors):
            return False
    if cfg.include_keywords and not any(k.lower() in text for k in cfg.include_keywords):
        return False
    if any(k.lower() in text for k in cfg.exclude_keywords):
        return False
    if cfg.min_temperature is not None:
        temp = next((int(t[5:]) for t in p.tags if t.startswith("temp:")), None)
        if temp is None or temp < cfg.min_temperature:
            return False
    return True
