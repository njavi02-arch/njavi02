"""Normalización de tallas y validación de productos antes de alertar.

Motivación (docs/REFERENCE_AUDIT.md §2.5, §2.6, §2.9): la referencia publica tallas mal parseadas
("375", "36666"), títulos que son solo un código y mensajes vacíos "(Sin título)". Aquí nada se
"adivina": lo que no se puede interpretar con seguridad se marca como inválido y no se publica.
"""
from __future__ import annotations

import re
from dataclasses import replace

from .models import Product, Variant

_FRACTIONS = {"⅓": " 1/3", "⅔": " 2/3", "½": ".5", " 1/2": ".5"}   # " 1/2": visto en baskets-store.com (20-nov)
_PREFIX = re.compile(r"^(EU|EUR)\s*", re.I)
_REGIONAL = re.compile(r"^(UK|US|USM|USW|JP|CM)\s*(\d{1,2}(?:\.5)?)$", re.I)
_EU = re.compile(r"^(\d{2})(?:\.5| 1/3| 2/3)?$")
_KIDS = re.compile(r"^\d{1,2}(?:\.5)?\s*(Y|C|K|T)$|\b(GS|PS|TD)\b", re.I)
_US = re.compile(r"^(\d{1,2})(?:\.5)?$")                       # tiendas con talla US sin prefijo (p. ej. 4.5, 10)
_MW = re.compile(r"^M\s?(\d{1,2}(?:\.5)?)\s?/\s?W\s?(\d{1,2}(?:\.5)?)$", re.I)  # "M5.5/W6.5" (unisex US)
_ALPHA = {"XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL", "2XL", "3XL", "OS", "O/S", "ONE SIZE", "TALLA ÚNICA", "DEFAULT TITLE"}
_WORDS = {"X-SMALL": "XS", "SMALL": "S", "MEDIUM": "M", "LARGE": "L", "X-LARGE": "XL", "XX-LARGE": "XXL",
          "XXX-LARGE": "XXXL", "EXTRA SMALL": "XS", "EXTRA LARGE": "XL"}
_KIDS_TITLE = re.compile(r"\b(GS|PS|TD|toddler|little kids|big kids|infant|baby|kids|niño|niña|junior|enfant)\b|\((GS|PS|TD)\)", re.I)


def normalize_size(raw: str) -> str | None:
    """Devuelve la talla canónica o None si no es interpretable sin adivinar.

    Shopify suele publicar "42 / Black": se toma el primer segmento.
    """
    if raw is None:
        return None
    parts = [x.strip() for x in str(raw).split(" / ")]
    if len(parts) > 1:  # "42 / Black" o "- / 5": el primer segmento que sea una talla
        for part in parts:
            if part and part != "-" and (n := normalize_size(part)) is not None:
                return n
        return None
    s = parts[0]
    if (m := re.match(r"^(XXS|XS|S|M|L|XL|XXL|XXXL|\dXL)\s*-\s*EU\s*\d+$", s.strip(), re.I)):
        return m.group(1).upper()          # ropa «XXL - EU 44» (ASOS Sample Sale): la talla es XXL, no un 44 de calzado
    for k, v in _FRACTIONS.items():
        s = s.replace(k, v)
    s = re.sub(r"\s+", " ", s).replace(",", ".")
    s = _PREFIX.sub("", s).strip()
    if not s:
        return None
    if s.upper() in _WORDS:
        return _WORDS[s.upper()]
    if s.upper() in _ALPHA:
        return "Única" if s.upper() in {"OS", "O/S", "ONE SIZE", "TALLA ÚNICA", "DEFAULT TITLE"} else s.upper()
    if m := _MW.match(s):
        return f"M{m.group(1)}/W{m.group(2)}"
    if m := _REGIONAL.match(s):
        return f"{m.group(1).upper()} {m.group(2)}"
    if _KIDS.search(s):
        return s.upper().replace(" ", "")
    if (m := _EU.match(s)) and 15 <= int(m.group(1)) <= 52:
        return s
    if (m := _US.match(s)) and 1 <= int(m.group(1)) <= 18:
        return s
    return None  # p. ej. "375", "36666": no se corrige por intuición


def is_kids_size(size: str) -> bool:
    return bool(_KIDS.search(size or ""))


def is_kids_product(title: str) -> bool:
    """Marcas de producto infantil en el título (p. ej. "Air Jordan 4 Retro OG GS", "Toddler (TD)")."""
    return bool(_KIDS_TITLE.search(title or ""))


def clean_variants(p: Product, *, skip_kids: bool = False, require_size: bool = True) -> Product:
    """Sustituye títulos de variante por la talla normalizada y elimina las no interpretables."""
    if skip_kids and is_kids_product(p.title):
        return replace(p, variants=())
    out: list[Variant] = []
    for v in p.variants:
        n = normalize_size(v.title)
        if n is None:
            if require_size:
                continue
            n = v.title
        if skip_kids and is_kids_size(n):
            continue
        out.append(replace(v, title=n))
    return replace(p, variants=tuple(out))


def validate_product(p: Product, *, allow_unknown_price: bool = False) -> list[str]:
    """Lista de problemas; vacía = publicable."""
    issues: list[str] = []
    title = (p.title or "").strip()
    if not title or title.lower() in {"(sin título)", "sin título", "untitled", "null", "none"}:
        issues.append("sin título")
    elif re.fullmatch(r"[\W\d_]+", title):
        issues.append("título solo numérico/código")
    if not p.url or not p.url.startswith(("http://", "https://")):
        issues.append("sin URL válida")
    if not p.variants:
        issues.append("sin variantes publicables")
    elif not allow_unknown_price and (p.min_price_cents or 0) <= 0:
        issues.append("precio desconocido o 0")
    return issues
