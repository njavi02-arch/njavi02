"""Pings por palabra clave + precio máximo → mención a un rol en un canal.

Equivalente propio de lo observado en `#pings-automaticos` (docs/REFERENCE_AUDIT.md §2.13):
regla "palabras ≤ precio", rol, canal de origen y motivo del aviso.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .models import Event, EventType

_LAUNCH_TYPES = ["announced", "date_confirmed", "date_changed", "raffle_open", "raffle_link_changed",
                 "raffle_closing", "live", "size_restock", "launch_price_drop", "cancelled"]
_ALL_TYPES = [e.value for e in EventType if e != EventType.SOLD_OUT] + _LAUNCH_TYPES


@dataclass
class PingRule:
    name: str
    keywords: list[str]                 # TODAS deben aparecer (insensible a mayúsculas/acentos); "*" = cualquiera
    channel: str                        # DISCORD_WEBHOOK_<CHANNEL>
    role_id: str | None = None          # ID numérico del rol a mencionar
    max_price_cents: int | None = None
    exclude_keywords: list[str] = field(default_factory=list)
    event_types: list[str] = field(default_factory=lambda: _ALL_TYPES)
    stores: list[str] = field(default_factory=list)   # vacío = todas
    brands: list[str] = field(default_factory=list)   # vacío = todas (palabra completa: "On" ≠ "Converse")
    sizes: list[str] = field(default_factory=list)    # tallas EU ("43", "42.5"); solo filtra eventos con tallas
    regions: list[str] = field(default_factory=list)  # p. ej. ["eu", "uk"] (prefijo de la región de la tienda)

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


def _match(rule: PingRule, *, type_value: str, text: str, brand: str, store: str, region: str | None,
           price: int | None, sizes: list[str] | None) -> bool:
    if type_value not in rule.event_types:
        return False
    if rule.stores and store not in rule.stores:
        return False
    if rule.regions and not (region and any(region.lower().startswith(r.lower()) for r in rule.regions)):
        return False
    if rule.brands and not any(re.search(rf"(?<!\w){re.escape(_norm(b))}(?!\w)", _norm(brand + " " + text)) for b in rule.brands):
        return False
    t = _norm(text)
    if not all(k == "*" or _norm(k) in t for k in rule.keywords):
        return False
    if any(_norm(k) in t for k in rule.exclude_keywords):
        return False
    if rule.max_price_cents is not None and (not price or price > rule.max_price_cents):
        return False
    if rule.sizes and sizes is not None:
        want = {s.replace(",", ".") for s in rule.sizes}
        if not want & {s.replace(",", ".") for s in sizes}:
            return False
    return True


def rule_matches(rule: PingRule, ev: Event) -> bool:
    p = ev.product
    text = f"{p.title} {p.vendor or ''} {' '.join(p.tags)} {' '.join(v.sku or '' for v in p.variants)}"
    sizes = [v.title.replace("EU ", "") for v in ev.variants] if rule.sizes else None
    return _match(rule, type_value=ev.type.value, text=text, brand=p.vendor or "", store=p.store, region=None,
                  price=_price(ev), sizes=sizes)


def rule_matches_launch(rule: PingRule, ev) -> bool:
    it = ev.launch
    sizes = [s.eu for s in ev.sizes] if ev.sizes else None   # anuncios/raffles no traen stock: no filtran por talla
    return _match(rule, type_value=ev.type.value, text=f"{it.brand} {it.name} {it.key}", brand=it.brand,
                  store=it.store, region=it.region, price=ev.new_price_cents or it.price_cents, sizes=sizes)


def build_ping(rule: PingRule, ev: Event | None, embed_payload: dict, title: str | None = None) -> dict:
    """Mensaje de ping: mención de rol (solo ese rol) + el mismo embed de la alerta."""
    mention = f"<@&{rule.role_id}> " if rule.role_id else ""
    what = f"{ev.type.value} en {ev.product.store}" if ev is not None else (title or "")
    payload = {
        "content": f"{mention}Regla **{rule.describe()}** · {what}",
        "embeds": embed_payload.get("embeds", []),
        "allowed_mentions": {"parse": [], "roles": [rule.role_id] if rule.role_id else []},
    }
    return payload
