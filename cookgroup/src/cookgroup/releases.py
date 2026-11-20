"""Calendario de lanzamientos mantenido por el staff (fichero TOML) + recordatorios y resumen diario.

Equivalente propio de lo observado en `#releases`, `#nike-releases` e `#important-releases`
(docs/REFERENCE_AUDIT.md §2.15): en la referencia el calendario es MANUAL (staff), con horario,
método de drop (LEO, FCFS, raffle…), enlaces a tienda y a mercado, y un semáforo de recomendación.
Aquí el staff edita `config/releases.toml`; el sistema solo programa y formatea los avisos.
No se consulta ninguna web.
"""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

VERDICTS = {"cop": ("🟢", "Cop", 0x2ECC71), "maybe": ("🟠", "Dudoso", 0xE67E22),
            "drop": ("🔴", "Drop", 0xE74C3C), "unknown": ("⚪", "Sin valorar", 0x95A5A6)}
METHODS = {"LEO", "FCFS", "DAN", "RAFFLE", "INSTORE", "APP", "DESCONOCIDO"}
_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,79}$")


@dataclass
class StoreLink:
    name: str
    url: str


@dataclass
class Release:
    id: str                       # slug estable: se usa para no repetir avisos
    name: str
    release_at: datetime          # con zona horaria
    method: str = "DESCONOCIDO"
    verdict: str = "unknown"
    sku: str | None = None
    retail_price: float | None = None
    stores: list[StoreLink] = field(default_factory=list)
    market_url: str | None = None
    image_url: str | None = None
    notes: str | None = None
    all_day: bool = False         # "Durante el día": hora no confirmada
    status: str = "pendiente"     # "confirmado" (fuente oficial anotada) | "pendiente" (no se avisa automáticamente)
    official_source: str | None = None


@dataclass
class Calendar:
    channel: str
    timezone: str
    reminders_minutes: list[int]
    digest_time: str | None
    releases: list[Release]


def _url(u: str | None, where: str) -> str | None:
    if u is None:
        return None
    if not str(u).startswith("https://"):
        raise ValueError(f"{where}: URL debe empezar por https:// ({u})")
    return str(u)


def _status(r: dict, rid: str) -> str:
    st = str(r.get("status", "pendiente")).lower()
    if st not in ("confirmado", "pendiente"):
        raise ValueError(f"release '{rid}': status debe ser 'confirmado' o 'pendiente'")
    if st == "confirmado" and not r.get("official_source"):
        raise ValueError(f"release '{rid}': 'confirmado' exige official_source (URL oficial de marca o tienda)")
    return st


def load_calendar(path: str | Path) -> Calendar:
    raw = tomllib.loads(Path(path).read_text())
    cal = raw.get("calendar", {})
    tz = ZoneInfo(cal.get("timezone", "Europe/Madrid"))
    rels, seen = [], set()
    for r in raw.get("release", []):
        rid = r.get("id", "")
        if not _ID.match(rid):
            raise ValueError(f"release '{rid}': id debe ser un slug (a-z, 0-9, guiones)")
        if rid in seen:
            raise ValueError(f"release '{rid}': id duplicado")
        seen.add(rid)
        when = r["release_at"]
        if isinstance(when, str):
            when = datetime.fromisoformat(when)
        elif isinstance(when, date) and not isinstance(when, datetime):
            when = datetime(when.year, when.month, when.day)
            r.setdefault("all_day", True)
        if when.tzinfo is None:
            when = when.replace(tzinfo=tz)
        method = str(r.get("method", "DESCONOCIDO")).upper()
        if method not in METHODS:
            raise ValueError(f"release '{rid}': method '{method}' no válido ({sorted(METHODS)})")
        verdict = r.get("verdict", "unknown")
        if verdict not in VERDICTS:
            raise ValueError(f"release '{rid}': verdict '{verdict}' no válido ({sorted(VERDICTS)})")
        rels.append(Release(
            id=rid, name=r["name"], release_at=when, method=method, verdict=verdict, sku=r.get("sku"),
            retail_price=r.get("retail_price"),
            stores=[StoreLink(s["name"], _url(s["url"], rid)) for s in r.get("stores", [])],
            market_url=_url(r.get("market_url"), rid), image_url=_url(r.get("image_url"), rid),
            notes=r.get("notes"), all_day=bool(r.get("all_day", False)),
            status=_status(r, rid), official_source=_url(r.get("official_source"), rid),
        ))
    rels.sort(key=lambda x: x.release_at)
    mins = sorted({int(m) for m in cal.get("reminders_minutes", [1440, 60, 10])}, reverse=True)
    if any(m <= 0 for m in mins):
        raise ValueError("reminders_minutes deben ser > 0")
    digest = cal.get("digest_time")
    if digest and not re.fullmatch(r"\d{2}:\d{2}", digest):
        raise ValueError("digest_time debe ser HH:MM")
    return Calendar(cal.get("channel", "releases"), str(tz), mins, digest, rels)


def due_reminders(cal: Calendar, now: datetime, *, grace_minutes: int = 15) -> list[tuple[Release, int]]:
    """Recordatorios cuyo momento ya llegó y no han caducado (ventana de gracia).

    Un lanzamiento "todo el día" solo recibe recordatorios de ≥ 1 día (la hora no es fiable).
    Devuelve (release, minutos_antes); la deduplicación la hace quien envía.
    """
    out = []
    for r in cal.releases:
        if r.status != "confirmado":
            continue   # pendiente de fuente oficial → nunca se avisa automáticamente
        for m in cal.reminders_minutes:
            if r.all_day and m < 1440:
                continue
            at = r.release_at - timedelta(minutes=m)
            if at <= now < at + timedelta(minutes=grace_minutes) and now < r.release_at:
                out.append((r, m))
    return out


def digest_due(cal: Calendar, now: datetime, *, grace_minutes: int = 30) -> date | None:
    """Fecha local del resumen si toca enviarlo ahora."""
    if not cal.digest_time:
        return None
    tz = ZoneInfo(cal.timezone)
    local = now.astimezone(tz)
    hh, mm = map(int, cal.digest_time.split(":"))
    at = local.replace(hour=hh, minute=mm, second=0, microsecond=0)
    return local.date() if at <= local < at + timedelta(minutes=grace_minutes) else None


def _human(minutes: int) -> str:
    if minutes % 1440 == 0:
        d = minutes // 1440
        return f"{d} día" + ("s" if d > 1 else "")
    if minutes % 60 == 0:
        h = minutes // 60
        return f"{h} hora" + ("s" if h > 1 else "")
    return f"{minutes} min"


def _links(r: Release) -> str:
    parts = [f"[{s.name}]({s.url})" for s in r.stores]
    if r.market_url:
        parts.append(f"[Mercado]({r.market_url})")
    return " | ".join(parts) or "—"


def build_reminder(r: Release, minutes_before: int) -> dict:
    emoji, label, color = VERDICTS[r.verdict]
    ts = int(r.release_at.timestamp())
    when = f"<t:{ts}:D> (hora sin confirmar)" if r.all_day else f"<t:{ts}:F> · <t:{ts}:R>"
    fields = [
        {"name": "Cuándo", "value": when, "inline": False},
        {"name": "Método", "value": r.method, "inline": True},
        {"name": "Valoración staff", "value": f"{emoji} {label}", "inline": True},
    ]
    if r.retail_price is not None:
        fields.append({"name": "Precio retail", "value": f"{r.retail_price:.2f} €".replace(".", ","), "inline": True})
    if r.sku:
        fields.append({"name": "SKU", "value": f"`{r.sku}`", "inline": True})
    fields.append({"name": "Enlaces", "value": _links(r)[:1000], "inline": False})
    if r.notes:
        fields.append({"name": "Notas", "value": r.notes[:1000], "inline": False})
    embed = {"title": f"⏰ En {_human(minutes_before)}: {r.name}", "color": color, "fields": fields,
             "footer": {"text": "Calendario del staff · la valoración es una opinión, no una garantía"}}
    if r.image_url:
        embed["thumbnail"] = {"url": r.image_url}
    return {"embeds": [embed]}


def build_digest(cal: Calendar, day: date) -> dict | None:
    """Resumen "drops del día" agrupado por hora (formato observado en `#releases`)."""
    tz = ZoneInfo(cal.timezone)
    todays = [r for r in cal.releases if r.release_at.astimezone(tz).date() == day and r.status == "confirmado"]
    if not todays:
        return None
    groups: dict[str, list[Release]] = {}
    for r in todays:
        key = "Durante el día" if r.all_day else r.release_at.astimezone(tz).strftime("%H:%M")
        groups.setdefault(key, []).append(r)
    order = sorted(groups, key=lambda k: (k == "Durante el día", k))
    lines = []
    for k in order:
        lines.append(f"**⏰ {k}**")
        for r in groups[k]:
            lines.append(f"• {VERDICTS[r.verdict][0]} {r.name} — {r.method} · {_links(r)}")
        lines.append("")
    return {"embeds": [{"title": f"Drops del día — {day.strftime('%d/%m/%Y')}", "description": "\n".join(lines)[:4000],
                        "color": 0x3498DB, "footer": {"text": "🟢 cop · 🟠 dudoso · 🔴 drop · ⚪ sin valorar (opinión del staff)"}}]}


def calendar_tick(cal: Calendar, now: datetime, store, send) -> int:
    """Envía lo que toque y lo registra para no repetirlo. Devuelve nº de mensajes enviados."""
    sent = 0
    for r, m in due_reminders(cal, now):
        key = f"release|{r.id}|{int(r.release_at.timestamp())}|{m}"
        if store.has_alert(key):
            continue
        mid = send(build_reminder(r, m))
        store.record_alert(key, "release_reminder", "calendar", r.id, mid)
        sent += 1
    if (day := digest_due(cal, now)) is not None:
        key = f"digest|{day.isoformat()}"
        if not store.has_alert(key) and (payload := build_digest(cal, day)):
            mid = send(payload)
            store.record_alert(key, "release_digest", "calendar", day.isoformat(), mid)
            sent += 1
    return sent
