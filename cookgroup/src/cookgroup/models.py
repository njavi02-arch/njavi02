"""Modelos de dominio. Todos los importes en céntimos (int) para evitar errores de coma flotante."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EventType(str, Enum):
    NEW_PRODUCT = "new_product"
    RESTOCK = "restock"
    SOLD_OUT = "sold_out"
    NEW_SIZE = "new_size"
    PRICE_DROP = "price_drop"
    PRICE_ERROR = "price_error"  # bajada anómala frente al histórico PROPIO (no al "precio anterior" de la ficha)


@dataclass(frozen=True)
class Variant:
    variant_id: str
    title: str  # talla/variante tal cual la publica la tienda
    price_cents: int
    available: bool
    sku: str | None = None
    compare_at_cents: int | None = None  # precio tachado que publica la tienda (no se usa como referencia fiable)


@dataclass(frozen=True)
class Product:
    store: str
    product_id: str
    title: str
    url: str
    currency: str
    variants: tuple[Variant, ...]
    vendor: str | None = None
    product_type: str | None = None
    tags: tuple[str, ...] = ()
    image_url: str | None = None

    @property
    def key(self) -> str:
        return f"{self.store}:{self.product_id}"

    @property
    def available_variants(self) -> tuple[Variant, ...]:
        return tuple(v for v in self.variants if v.available)

    @property
    def min_price_cents(self) -> int | None:
        prices = [v.price_cents for v in self.variants]
        return min(prices) if prices else None


@dataclass(frozen=True)
class Event:
    type: EventType
    product: Product
    variants: tuple[Variant, ...] = ()  # variantes implicadas (tallas nuevas, repuestas...)
    old_price_cents: int | None = None
    new_price_cents: int | None = None
    detected_at: str = ""  # ISO-8601 UTC

    @property
    def dedupe_key(self) -> str:
        vids = ",".join(sorted(v.variant_id for v in self.variants))
        price = self.new_price_cents if self.type in (EventType.PRICE_DROP, EventType.PRICE_ERROR) else ""
        return f"{self.type.value}|{self.product.key}|{vids}|{price}"


@dataclass(frozen=True)
class MarketData:
    """Dato de mercado secundario aportado por una fuente AUTORIZADA.

    `kind` distingue ventas realizadas de anuncios: nunca se mezclan.
    """
    source: str
    kind: str  # "sold" | "listing"
    price_cents: int
    sample_size: int
    as_of: str
    url: str | None = None
    size: str | None = None          # talla de las ventas (None = sin talla → no verificable)
    condition: str | None = None     # "new" / "used"…
    market: str | None = None        # plataforma de las ventas (stockx, goat, ebay, vinted…)
    currency: str = "EUR"
    verified_sales: bool = False     # True solo si son ventas individuales con fecha y fuente


@dataclass
class Opportunity:
    event: Event
    buy_price_cents: int
    resale_price_cents: int | None
    net_profit_cents: int | None
    roi_pct: float | None
    score: int
    score_breakdown: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)  # incertidumbres explícitas
    margin_pct: float | None = None      # beneficio neto / precio de reventa
    verified: bool = False               # beneficio publicable (ventas recientes de la misma ref/talla/estado/mercado)
    basis: str | None = None             # texto de la base del cálculo (n ventas, mercado, fechas, fuente)
    buy_size: str | None = None          # talla concreta que se puede comprar y a la que corresponden las ventas
