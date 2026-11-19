"""Puntuación 0-100 con pesos ajustables y desglose explicable. Determinista: sin IA aquí."""
from __future__ import annotations

from dataclasses import dataclass

from .models import MarketData
from .profit import ProfitResult


@dataclass(frozen=True)
class Weights:
    margin: float = 0.35
    confidence: float = 0.20
    demand: float = 0.15
    liquidity: float = 0.10
    risk: float = 0.10     # factor de seguridad (más alto = menos riesgo)
    urgency: float = 0.10

    def normalized(self) -> "Weights":
        t = self.margin + self.confidence + self.demand + self.liquidity + self.risk + self.urgency
        return Weights(*(x / t for x in (self.margin, self.confidence, self.demand, self.liquidity, self.risk, self.urgency)))


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def score_opportunity(profit: ProfitResult, market: MarketData | None, *, urgency: float = 0.5,
                      weights: Weights = Weights(), min_net_cents: int = 1500) -> tuple[int, dict[str, float]]:
    """Devuelve (score, desglose 0-1 por factor). Sin dato de mercado => score acotado y bajo."""
    w = weights.normalized()
    if profit.net_profit_cents is None or market is None:
        return 0, {"margin": 0, "confidence": 0, "demand": 0, "liquidity": 0, "risk": 0, "urgency": urgency}
    margin = _clamp(profit.net_profit_cents / (min_net_cents * 4))  # 4x el umbral => 100%
    confidence = _clamp(0.5 * (1.0 if market.kind == "sold" else 0.4) + 0.5 * _clamp(market.sample_size / 20))
    demand = _clamp(market.sample_size / 30) if market.kind == "sold" else 0.2
    liquidity = _clamp(market.sample_size / 15) if market.kind == "sold" else 0.2
    risk = _clamp(1.0 - (0.0 if profit.roi_pct is None else 0.0) - 0.15 * len(profit.notes))
    parts = {"margin": margin, "confidence": confidence, "demand": demand,
             "liquidity": liquidity, "risk": risk, "urgency": _clamp(urgency)}
    total = (w.margin * margin + w.confidence * confidence + w.demand * demand +
             w.liquidity * liquidity + w.risk * risk + w.urgency * urgency)
    if profit.net_profit_cents < min_net_cents:
        total = min(total, 0.39)  # por debajo del umbral nunca es 'alerta'
    return round(total * 100), parts
