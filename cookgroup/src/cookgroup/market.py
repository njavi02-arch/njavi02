"""Datos de mercado secundario.

IMPORTANTE: no se hace scraping de StockX/GOAT/eBay saltando sus condiciones. La v1 lee un
fichero JSON mantenido por el operador (datos que haya verificado o exportado de una fuente a
la que tenga acceso legítimo: API oficial, programa de afiliados, partner...). Cada entrada
declara si es 'sold' (venta realizada) o 'listing' (anuncio). Sin entrada => sin beneficio.
Para añadir una API autorizada, implementar `MarketProvider.lookup`.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Protocol

from .models import MarketData


class MarketProvider(Protocol):
    def lookup(self, sku: str | None, title: str, size: str | None) -> MarketData | None: ...


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


class FileMarketProvider:
    """Formato: {"entries":[{"sku":"DD1391-100","size":"42","source":"manual","kind":"sold",
    "price_eur":210.0,"sample_size":12,"as_of":"2026-11-18","url":"..."}]}"""

    def __init__(self, path: str | Path):
        p = Path(path)
        self.entries = json.loads(p.read_text()).get("entries", []) if p.exists() else []

    def lookup(self, sku, title, size):
        best = None
        for e in self.entries:
            if sku and _norm(e.get("sku", "")) == _norm(sku) and e.get("size") in (None, size):
                if best is None or e.get("size") == size:  # prioriza coincidencia exacta de talla
                    best = e
        if not best:
            return None
        return MarketData(best["source"], best["kind"], round(best["price_eur"] * 100),
                          int(best.get("sample_size", 0)), best["as_of"], best.get("url"))
