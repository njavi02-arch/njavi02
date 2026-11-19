"""Cálculo de beneficio neto.

Beneficio = reventa estimada - compra - envío compra - comisión plataforma - envío venta - otros.
Si no hay dato de mercado verificado el beneficio es None (nunca se inventa).
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import MarketData


@dataclass(frozen=True)
class Platform:
    name: str
    fee_pct: float          # comisión sobre precio de venta
    fixed_fee_cents: int = 0
    seller_shipping_cents: int = 0


# Valores POR DEFECTO ORIENTATIVOS y editables en config/fees.toml. Verificar contra las
# tarifas vigentes de cada plataforma antes de usarlos para decisiones reales.
DEFAULT_PLATFORMS: dict[str, Platform] = {
    "stockx": Platform("stockx", 9.0, 0, 1000),
    "goat": Platform("goat", 9.5, 500, 0),
    "ebay": Platform("ebay", 12.8, 30, 600),
    "vinted": Platform("vinted", 0.0, 0, 400),  # comisión la paga el comprador
}


@dataclass(frozen=True)
class ProfitResult:
    resale_cents: int | None
    net_profit_cents: int | None
    roi_pct: float | None
    notes: tuple[str, ...]


def compute_profit(buy_cents: int, market: MarketData | None, platform: Platform, *,
                   buy_shipping_cents: int = 0, other_costs_cents: int = 0) -> ProfitResult:
    notes: list[str] = []
    if market is None:
        return ProfitResult(None, None, None, ("Sin dato de mercado verificado: beneficio no calculable",))
    if market.kind != "sold":
        notes.append("Precio de mercado basado en ANUNCIOS, no en ventas realizadas: sobreestima")
    if market.sample_size < 5:
        notes.append(f"Muestra pequeña ({market.sample_size} operaciones)")
    resale = market.price_cents
    fee = round(resale * platform.fee_pct / 100) + platform.fixed_fee_cents
    cost = buy_cents + buy_shipping_cents + fee + platform.seller_shipping_cents + other_costs_cents
    net = resale - cost
    roi = net * 100 / (buy_cents + buy_shipping_cents) if (buy_cents + buy_shipping_cents) > 0 else None
    return ProfitResult(resale, net, roi, tuple(notes))
