"""Límite de peticiones por dominio, compartido por todos los monitores (hilos).

Cada monitor corre en su propio hilo, así que una tienda lenta no retrasa a las demás. Pero varios monitores pueden
apuntar al mismo dominio (p. ej. catálogo y colección «launches» de la misma tienda, o varias páginas de BSTN): aquí
se garantiza un intervalo mínimo entre peticiones a un mismo dominio.
"""
from __future__ import annotations

import threading
import time
from urllib.parse import urlparse

DEFAULT_MIN_INTERVAL = 2.0   # segundos entre peticiones al mismo dominio
_lock = threading.Lock()
_next_slot: dict[str, float] = {}
_overrides: dict[str, float] = {}


def set_interval(domain: str, seconds: float) -> None:
    _overrides[domain.lower().removeprefix("www.")] = seconds


def wait_turn(url: str, *, clock=time.monotonic, sleep=time.sleep) -> float:
    """Bloquea (solo a este hilo) hasta que toque turno para el dominio. Devuelve los segundos esperados."""
    dom = (urlparse(url).hostname or "").lower().removeprefix("www.")
    gap = _overrides.get(dom, DEFAULT_MIN_INTERVAL)
    with _lock:
        now = clock()
        slot = max(now, _next_slot.get(dom, 0.0))
        _next_slot[dom] = slot + gap
    wait = slot - now
    if wait > 0:
        sleep(wait)
    return wait
