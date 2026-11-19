from __future__ import annotations

from .config import MonitorConfig
from .models import Product


def product_passes(p: Product, cfg: MonitorConfig) -> bool:
    text = f"{p.title} {p.vendor or ''} {' '.join(p.tags)}".lower()
    if cfg.include_vendors and not any(v.lower() in text for v in cfg.include_vendors):
        return False
    if cfg.include_keywords and not any(k.lower() in text for k in cfg.include_keywords):
        return False
    if any(k.lower() in text for k in cfg.exclude_keywords):
        return False
    return True
