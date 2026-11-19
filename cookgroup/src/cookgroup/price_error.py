"""Detección de posibles price errors con precio de referencia validado.

Motivación (docs/REFERENCE_AUDIT.md §2.10): la referencia marca "-100 %" usando el "precio anterior"
que muestra la ficha, aunque sea de miles de euros. Aquí la referencia es la MEDIANA del histórico
propio de precios del producto, con un mínimo de observaciones; el precio tachado de la tienda solo
se usa como nota, y se descarta si no es creíble.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median


@dataclass
class PriceErrorCheck:
    is_error: bool
    reference_cents: int | None
    drop_pct: float | None
    notes: list[str] = field(default_factory=list)


def check_price_error(new_price_cents: int, history_cents: list[int], *, compare_at_cents: int | None = None,
                      threshold_pct: float = 50.0, min_observations: int = 5,
                      max_credible_ratio: float = 5.0) -> PriceErrorCheck:
    notes: list[str] = []
    if compare_at_cents and new_price_cents > 0 and compare_at_cents > new_price_cents * max_credible_ratio:
        notes.append(f"Precio tachado de la tienda no creíble (>{max_credible_ratio:.0f}× el actual); ignorado")
    hist = [h for h in history_cents if h and h > 0]
    if len(hist) < min_observations:
        notes.append(f"Histórico insuficiente ({len(hist)}/{min_observations} observaciones): no se etiqueta como price error")
        return PriceErrorCheck(False, None, None, notes)
    ref = int(median(hist))
    if ref <= 0 or new_price_cents <= 0:
        return PriceErrorCheck(False, ref or None, None, notes)
    drop = (ref - new_price_cents) * 100 / ref
    is_err = drop >= threshold_pct
    if is_err:
        notes.append(f"Referencia: mediana de {len(hist)} precios observados por este sistema")
        notes.append("Posible error de precio: la tienda puede cancelar el pedido")
    return PriceErrorCheck(is_err, ref, round(drop, 1), notes)
