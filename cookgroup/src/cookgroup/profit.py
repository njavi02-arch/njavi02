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
    roi_pct: float | None            # beneficio neto / coste de compra
    notes: tuple[str, ...]
    margin_pct: float | None = None  # beneficio neto / precio de venta
    verified: bool = False
    basis: str | None = None


MIN_SALES = 3          # ventas cerradas mínimas en la ventana
WINDOW_DAYS = 30


def verification_problems(market: MarketData | None, *, size: str | None, buy_currency: str, ships_es: str | None) -> list[str]:
    """Motivos por los que un beneficio NO es publicable. Lista vacía = verificable."""
    p = []
    if market is None:
        return ["sin ventas registradas de esta referencia"]
    if not market.verified_sales or market.kind != "sold":
        p.append("el dato no son ventas cerradas individuales (anuncios o agregado)")
    if market.sample_size < MIN_SALES:
        p.append(f"solo {market.sample_size} ventas en los últimos {WINDOW_DAYS} días (mínimo {MIN_SALES})")
    if not market.size or str(market.size).replace(",", ".") != str(size or "").replace("EU ", "").replace(",", "."):
        p.append("las ventas no son de la misma talla")
    if (market.condition or "") != "new":
        p.append("estado del producto no confirmado como nuevo")
    if not market.market or market.market == "varios":
        p.append("ventas de mercados distintos mezcladas")
    if (market.currency or "").upper() != "EUR" or buy_currency.upper() != "EUR":
        p.append("monedas distintas sin tipo de cambio verificado")
    if (ships_es or "").lower() not in ("sí", "si", "yes"):
        p.append("envío a España sin confirmar")
    return p


def compute_profit(buy_cents: int, market: MarketData | None, platform: Platform, *,
                   buy_shipping_cents: int = 0, other_costs_cents: int = 0, size: str | None = None,
                   buy_currency: str = "EUR", ships_es: str | None = "sí", require_verified: bool = False) -> ProfitResult:
    """Con require_verified=True (avisos reales) solo devuelve cifras si se cumplen TODAS las condiciones;
    si no, net=None y verified=False con los motivos en notes ("beneficio sin verificar")."""
    if require_verified:
        probs = verification_problems(market, size=size, buy_currency=buy_currency, ships_es=ships_es)
        if probs:
            return ProfitResult(None, None, None, tuple(probs), None, False, None)
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
    margin = net * 100 / resale if resale else None
    verified = require_verified   # aquí solo se llega verificado si se exigió
    basis = (f"{market.sample_size} ventas cerradas en {market.market}, talla {market.size}, nuevo, últimos {WINDOW_DAYS} días "
             f"(última {market.as_of}; fuente: {market.source}); comisión {platform.fee_pct:g} % + envío venta "
             f"{platform.seller_shipping_cents / 100:.2f} €") if verified else None
    return ProfitResult(resale, net, roi, tuple(notes), margin, verified, basis)
