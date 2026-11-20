"""Perfiles de miembro y menciones personalizadas (v0.8, lote 1).

Cómo llega un miembro a recibir un aviso:
  1. En la bienvenida elige familias, marcas, región y tallas (preguntas nativas de Discord → roles).
  2. `cookgroup miembros --sincronizar` (con el token del bot) convierte esos roles en perfiles (config/miembros.toml).
     También se pueden añadir a mano palabras clave, negativas, precio máximo, canales excluidos y pausa.
  3. Cada aviso que publica el bot se cruza con los perfiles: solo se menciona a quien cumple TODO.
  4. Una misma señal (mismo producto, mismo tipo, mismas tallas) solo menciona una vez a cada miembro, aunque se
     publique en el canal de la tienda y en el agregado.

Reglas de talla (lo importante):
  · «Vuelve tu talla» solo si la tienda da stock POR TALLA y esa talla está disponible.
  · Si la tienda solo da stock general (sin tallas), puede avisar de un producto nuevo o de una bajada, nunca de
    «vuelve la 44,5».
"""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .models import Event, EventType
from .normalize import normalize_size

SIZE_EVENTS = {EventType.RESTOCK, EventType.NEW_SIZE}
FAMILY_BY_CHANNEL = {"sneakers": "Sneakers", "sneakers_world": "Sneakers", "baloncesto": "Sneakers", "skate": "Sneakers",
                     "restocks": "Sneakers", "lanzamientos": "Lanzamientos", "raffles": "Raffles", "rebajas_30": "Rebajas",
                     "rebajas_60": "Rebajas", "chollos": "Rebajas", "outlet": "Rebajas", "streetwear": "Streetwear",
                     "coleccionables": "Pokémon-TCG", "lego": "LEGO", "electronica": "Electrónica",
                     "madrid": "Tiendas Madrid", "reventa": "Reventa", "pruebas": "Sneakers"}


def eu_size(raw: str | None) -> str | None:
    """'44,5' / 'EU 44.5' / '44½' → '44.5'. Otros sistemas (US/UK) y tallas de ropa → None."""
    if raw is None:
        return None
    s = str(raw).strip().replace(",", ".")
    n = normalize_size(s)
    if not n or not re.fullmatch(r"\d{2}(\.5| 1/3| 2/3)?", n):
        return None
    return n


def size_label_es(s: str) -> str:
    return "EU " + s.replace(".", ",")


@dataclass
class Profile:
    member_id: str                       # id de usuario de Discord (snowflake) — se usa para <@id>
    name: str                            # apodo visible para el staff (no se publica)
    families: set[str] = field(default_factory=set)
    brands: set[str] = field(default_factory=set)
    sizes: set[str] = field(default_factory=set)       # canónicas: "44.5"
    regions: set[str] = field(default_factory=set)
    keywords: list[str] = field(default_factory=list)  # todas deben aparecer (si hay)
    negatives: list[str] = field(default_factory=list)
    max_price_eur: float | None = None
    excluded_channels: set[str] = field(default_factory=set)
    paused: bool = False
    destination: str = "canal"           # "canal" (mención en el canal) | "md" (mensaje privado, requiere bot)

    @classmethod
    def from_dict(cls, d: dict) -> "Profile":
        sizes = {x for x in (eu_size(s) for s in d.get("tallas", [])) if x}
        return cls(str(d["id"]), d.get("nombre", ""), set(d.get("familias", [])), set(d.get("marcas", [])), sizes,
                   set(d.get("regiones", [])), list(d.get("palabras", [])), list(d.get("negativas", [])),
                   d.get("precio_max_eur"), set(d.get("excluir_canales", [])), bool(d.get("pausa", False)),
                   d.get("destino", "canal"))

    @classmethod
    def from_roles(cls, member_id: str, name: str, role_names: list[str], design: dict) -> "Profile":
        r = design.get("roles", {})
        roles = set(role_names)
        sizes = {eu_size(x[3:]) for x in roles if x.startswith("EU ")}
        return cls(member_id, name, roles & set(r.get("familias", [])), roles & set(r.get("marcas", [])),
                   {s for s in sizes if s}, roles & set(r.get("regiones", [])))


def load_profiles(path: str | Path) -> list[Profile]:
    p = Path(path)
    if not p.exists():
        return []
    return [Profile.from_dict(d) for d in tomllib.loads(p.read_text(encoding="utf-8")).get("miembro", [])]


@dataclass
class Decision:
    notify: bool
    reason: str
    sizes: tuple[str, ...] = ()          # tallas del perfil que están disponibles en esta señal


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower())


def _has_word(text: str, word: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(_norm(word)) + r"(?![a-z0-9])", _norm(text)) is not None


def decide(p: Profile, ev: Event, *, channel: str, family: str, ships_es: str | None, size_stock: bool = True) -> Decision:
    """¿Hay que mencionar a este miembro por esta señal? Devuelve el motivo en ambos casos (sirve para pruebas y panel)."""
    if p.paused:
        return Decision(False, "avisos en pausa")
    if channel in p.excluded_channels:
        return Decision(False, f"ha excluido el canal #{channel}")
    if p.families and family not in p.families:
        return Decision(False, f"no sigue la familia «{family}»")
    text = f"{ev.product.vendor or ''} {ev.product.title}"
    if p.brands and not any(_has_word(text, b) for b in p.brands):
        return Decision(False, f"la marca no está entre las suyas ({', '.join(sorted(p.brands))})")
    if "Envío a España" in p.regions and (ships_es or "").lower() not in ("sí", "si", "yes"):
        return Decision(False, "la tienda no tiene confirmado el envío a España")
    if any(not _has_word(text, k) for k in p.keywords):
        return Decision(False, "no contiene sus palabras clave")
    if any(_has_word(text, n) for n in p.negatives):
        return Decision(False, "contiene una palabra negativa suya")
    avail = [v for v in (ev.variants or ev.product.available_variants) if v.available]
    if p.max_price_eur is not None:
        prices = [v.price_cents for v in avail if v.price_cents]
        if ev.product.currency.upper() != "EUR" or not prices or min(prices) > p.max_price_eur * 100:
            return Decision(False, f"supera su precio máximo ({p.max_price_eur:.0f} €) o no está en euros")
    if not p.sizes:
        return Decision(True, "cumple familia, marca y región (no ha elegido talla)")
    sized = {eu_size(v.title): v for v in avail}
    sized.pop(None, None)
    if not size_stock or not sized:
        if ev.type in SIZE_EVENTS:
            return Decision(False, "la tienda solo da stock general: no se puede confirmar su talla")
        return Decision(True, "producto de interés; la tienda no da stock por talla (talla sin confirmar)")
    mine = tuple(sorted(s for s in sized if s in p.sizes))
    if not mine:
        have = ", ".join(size_label_es(s) for s in sorted(sized)) or "ninguna"
        return Decision(False, f"su talla no está disponible (disponibles: {have})")
    return Decision(True, "su talla está disponible: " + ", ".join(size_label_es(s) for s in mine), mine)


def signal_key(ev: Event, sizes: tuple[str, ...]) -> str:
    """Identidad de la señal para no repetir la mención aunque el aviso salga en dos canales."""
    price = ev.new_price_cents if ev.type in (EventType.PRICE_DROP, EventType.PRICE_ERROR) else ""
    kind = "stock" if ev.type in SIZE_EVENTS else ev.type.value     # «vuelve» y «talla nueva» son la misma señal
    return f"{kind}|{ev.product.key}|{','.join(sizes)}|{price}"


def personalize(payload: dict, ev: Event, profiles: list[Profile], store, *, channel: str, family: str,
                ships_es: str | None, size_stock: bool = True) -> tuple[dict, list[tuple[Profile, Decision]]]:
    """Añade las menciones que tocan al payload (sin romper el embed) y registra cada mención para no repetirla.
    Devuelve (payload, decisiones) — las decisiones incluyen a quien NO se menciona y por qué."""
    out = dict(payload)
    decisions, ids, lines = [], [], []
    for p in profiles:
        d = decide(p, ev, channel=channel, family=family, ships_es=ships_es, size_stock=size_stock)
        if d.notify and p.destination == "canal":
            key = signal_key(ev, d.sizes)
            if not store.claim_mention(p.member_id, key, channel):
                d = Decision(False, "ya se le mencionó por esta misma señal en otro canal", d.sizes)
            else:
                ids.append(p.member_id)
                lines.append(f"<@{p.member_id}>" + (f" · {', '.join(size_label_es(s) for s in d.sizes)}" if d.sizes else ""))
        decisions.append((p, d))
    if ids:
        out["content"] = ((payload.get("content") or "") + "\n" if payload.get("content") else "") + "🔔 " + " · ".join(lines)
        out["allowed_mentions"] = {"parse": [], "users": ids[:100]}    # solo se notifica a estos usuarios
    else:
        out.setdefault("allowed_mentions", {"parse": []})              # nunca @everyone ni roles por accidente
    return out, decisions
