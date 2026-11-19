"""Pings por palabra clave + precio máximo → mención a un rol en un canal.

Equivalente propio de lo observado en `#pings-automaticos` (docs/REFERENCE_AUDIT.md §2.13):
regla "palabras ≤ precio", rol, canal de origen y motivo del aviso.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .models import Event, EventType


@dataclass
class PingRule:
    name: str
    keywords: list[str]                 # TODAS deben aparecer (insensible a mayúsculas/acentos); "*" = cualquiera
    channel: str                        # DISCORD_WEBHOOK_<CHANNEL>
    role_id: str | None = None          # ID numérico del rol a mencionar
    max_price_cents: int | None = None
    exclude_keywords: list[str] = field(default_factory=list)
    event_types: list[str] = field(default_factory=lambda: [e.value for e in EventType if e != EventType.SOLD_OUT])
    stores: list[str] = field(default_factory=list)  # vacío = todas

    @classmethod
    def from_dict(cls, d: dict) -> "PingRule":
        d = dict(d)
        if "max_price" in d:
            d["max_price_cents"] = round(float(d.pop("max_price")) * 100)
        if d.get("role_id") is not None:
            d["role_id"] = str(d["role_id"])
            if not d["role_id"].isdigit():
                raise ValueError(f"ping_rule {d.get('name')}: role_id debe ser numérico")
        if not d.get("keywords"):
            raise ValueError(f"ping_rule {d.get('name')}: keywords vacío")
        return cls(**d)

    def describe(self) -> str:
        kw = " ".join(self.keywords) if self.keywords != ["*"] else "cualquier producto"
        return f"{kw} ≤ {self.max_price_cents/100:g}" if self.max_price_cents else kw


_ACC = str.maketrans("áéíóúüñ", "aeiouun")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().translate(_ACC))


def _price(ev: Event) -> int | None:
    if ev.new_price_cents:
        return ev.new_price_cents
    prices = [v.price_cents for v in ev.variants if v.price_cents > 0]
    return min(prices) if prices else ev.product.min_price_cents


def rule_matches(rule: PingRule, ev: Event) -> bool:
    if ev.type.value not in rule.event_types:
        return False
    if rule.stores and ev.product.store not in rule.stores:
        return False
    p = ev.product
    text = _norm(f"{p.title} {p.vendor or ''} {' '.join(p.tags)} {' '.join(v.sku or '' for v in p.variants)}")
    if not all(k == "*" or _norm(k) in text for k in rule.keywords):
        return False
    if any(_norm(k) in text for k in rule.exclude_keywords):
        return False
    if rule.max_price_cents is not None:
        price = _price(ev)
        if not price or price > rule.max_price_cents:
            return False
    return True


def build_ping(rule: PingRule, ev: Event, embed_payload: dict) -> dict:
    """Mensaje de ping: mención de rol (solo ese rol) + el mismo embed de la alerta."""
    mention = f"<@&{rule.role_id}> " if rule.role_id else ""
    payload = {
        "content": f"{mention}Regla **{rule.describe()}** · {ev.type.value} en {ev.product.store}",
        "embeds": embed_payload.get("embeds", []),
        "allowed_mentions": {"parse": [], "roles": [rule.role_id] if rule.role_id else []},
    }
    return payload
