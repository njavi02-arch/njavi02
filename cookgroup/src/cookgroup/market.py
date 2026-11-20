"""Datos de mercado secundario (reventa).

No se hace scraping de StockX/GOAT/eBay saltando sus condiciones. config/market_data.json lo mantiene el operador con
VENTAS CERRADAS individuales obtenidas de una fuente legítima (API oficial, exportación propia, programa de partners):

  {"sales": [{"sku": "HQ4307-001", "size": "42", "condition": "new", "market": "stockx", "price": 135.0,
              "currency": "EUR", "date": "2026-11-18", "source": "export StockX vendedor", "url": "…"}]}

El formato antiguo {"entries": [...]} (agregados o anuncios) se sigue leyendo, pero NUNCA verifica un beneficio.
"""
from __future__ import annotations

import json
import re
import statistics
from datetime import date, timedelta
from pathlib import Path
from typing import Protocol

from .models import MarketData


class MarketProvider(Protocol):
    def lookup(self, sku: str | None, title: str, size: str | None) -> MarketData | None: ...


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def _size(s) -> str:
    return str(s or "").upper().replace("EU", "").replace(",", ".").strip()


class FileMarketProvider:
    def __init__(self, path: str | Path, *, market: str | None = None, condition: str = "new", window_days: int = 30,
                 today: date | None = None):
        p = Path(path)
        data = json.loads(p.read_text()) if p.exists() else {}
        self.sales = data.get("sales", [])
        self.entries = data.get("entries", [])
        self.market, self.condition, self.window_days = market, condition, window_days
        self.today = today

    def lookup(self, sku, title, size):
        if not sku:
            return None
        today = self.today or date.today()
        since = today - timedelta(days=self.window_days)
        ref = _norm(sku)
        cands = [s for s in self.sales if _norm(s.get("sku")) and (ref.startswith(_norm(s.get("sku"))) or _norm(s.get("sku")).startswith(ref))]
        if cands:
            same = [s for s in cands if _size(s.get("size")) == _size(size) and s.get("condition", "new") == self.condition
                    and (self.market is None or s.get("market") == self.market)]
            recent = [s for s in same if s.get("date") and date.fromisoformat(s["date"]) >= since]
            pool = recent or same
            if pool:
                markets = {s.get("market") for s in pool}
                currencies = {s.get("currency", "EUR") for s in pool}
                return MarketData(
                    source=", ".join(sorted({s.get("source", "?") for s in pool}))[:120], kind="sold",
                    price_cents=round(statistics.median(float(s["price"]) for s in pool) * 100), sample_size=len(recent),
                    as_of=max(s.get("date", "") for s in pool), url=pool[-1].get("url"), size=_size(size),
                    condition=self.condition, market=markets.pop() if len(markets) == 1 else "varios",
                    currency=currencies.pop() if len(currencies) == 1 else "mezcla", verified_sales=True)
        # formato antiguo: agregado/anuncio sin ventas individuales → nunca verificado
        best = None
        for e in self.entries:
            if _norm(e.get("sku")) == ref and e.get("size") in (None, size):
                if best is None or e.get("size") == size:
                    best = e
        if not best:
            return None
        return MarketData(best["source"], best["kind"], round(best["price_eur"] * 100), int(best.get("sample_size", 0)),
                          best["as_of"], best.get("url"), size=best.get("size"), verified_sales=False)
