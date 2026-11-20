"""#muestra-gratis (v0.9): enseña el servicio a visitantes sin regalarlo.

Regla: como mucho N avisos al día, publicados con RETRASO (por defecto 60 min), sin menciones y con una nota que
invita a suscribirse. Solo se eligen avisos ya entregados a los suscriptores.
"""
from __future__ import annotations

import copy

DELAY = 3600
PER_DAY = 3


class SampleFeed:
    def __init__(self, per_day: int = PER_DAY, delay: int = DELAY):
        self.per_day, self.delay = per_day, delay
        self.queue: list[tuple[float, dict]] = []
        self.published: list[tuple[float, dict]] = []

    def offer(self, payload: dict, delivered_at: float) -> bool:
        day = int(delivered_at // 86400)
        taken = sum(1 for t, _ in self.queue + self.published if int(t // 86400) == day)
        if taken >= self.per_day:
            return False                                  # silencio: cupo diario lleno
        p = copy.deepcopy(payload)
        p.pop("content", None)                            # sin menciones de suscriptores
        p["allowed_mentions"] = {"parse": []}
        for e in p.get("embeds", []):
            e.setdefault("footer", {})["text"] = "MUESTRA con 60 min de retraso · los suscriptores lo recibieron al momento"
        self.queue.append((delivered_at, p))
        return True

    def due(self, now: float) -> list[dict]:
        ready = [(t, p) for t, p in self.queue if now >= t + self.delay]
        self.queue = [(t, p) for t, p in self.queue if now < t + self.delay]
        self.published += ready
        return [p for _, p in ready]
