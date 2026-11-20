from __future__ import annotations

import argparse
import json
import logging
import os
import sys

from .config import load_config
from .runner import run_all


import re
from logging.handlers import RotatingFileHandler

_SECRET = re.compile(r"https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/\S+")


class _JsonFmt(logging.Formatter):
    def format(self, r):
        msg = r.getMessage() + (("\n" + self.formatException(r.exc_info)) if r.exc_info else "")
        return json.dumps({"ts": self.formatTime(r), "level": r.levelname, "thread": r.threadName,
                           "msg": _SECRET.sub("[webhook oculto]", msg)}, ensure_ascii=False)


def load_dotenv(path: str = ".env") -> None:
    """Carga KEY=VALUE de .env sin dependencias; las variables ya definidas en el entorno mandan."""
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            if v.strip():
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cookgroup")
    ap.add_argument("--config", default="config/monitors.toml")
    ap.add_argument("--db", default=os.environ.get("COOKGROUP_DB", "cookgroup.db"))
    ap.add_argument("command", choices=["run", "check-config", "check-releases", "probe", "test-webhook", "preview", "status"])
    ap.add_argument("--channel", default="default", help="test-webhook: canal cuyo webhook probar")
    ap.add_argument("--out", default="preview.html", help="preview: fichero HTML de salida")
    a = ap.parse_args(argv)
    load_dotenv()
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(_JsonFmt())
    handlers = [h]
    if a.command == "run":   # log persistente con rotación (5 × 5 MB) en logs/cookgroup.log
        os.makedirs("logs", exist_ok=True)
        fh = RotatingFileHandler("logs/cookgroup.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8")
        fh.setFormatter(_JsonFmt())
        handlers.append(fh)
    logging.basicConfig(level=logging.INFO, handlers=handlers)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    cfg = load_config(a.config)
    if a.command == "status":
        from datetime import datetime, timezone
        from .store import Store
        rows = Store(a.db).health()
        if not rows:
            print("Sin datos todavía: arranca con 'run' y vuelve a mirar en unos minutos.")
            return 0
        now = datetime.now(timezone.utc)
        mins = lambda iso: int((now - datetime.fromisoformat(iso)).total_seconds() // 60) if iso else None
        def ago(m):
            return "nunca" if m is None else f"hace {m} min" if m < 120 else f"hace {m // 60} h" if m < 2880 else f"hace {m // 1440} d"
        ok = att = bad = 0
        print(f"{'fuente':<22} {'estado':<10} {'último OK':<13} {'desde (Madrid)':<16} {'ciclos':>6}  detalle")
        for src, last_ok, errs, last_err, err_at, items, ms, delay, first_ok, cycles in rows:
            age = mins(last_ok)
            if errs == 0 and last_ok and age is not None and age <= 60:
                st, ok = "OK", ok + 1
            elif errs >= 3 or not last_ok or (age or 0) > 60:
                st, bad = "ATENCIÓN", bad + 1
            else:
                st, att = "AVISO", att + 1
            from zoneinfo import ZoneInfo
            since = datetime.fromisoformat(first_ok).astimezone(ZoneInfo("Europe/Madrid")).strftime("%d-%m %H:%M") if first_ok else "-"
            det = (last_err or "")[:70] if errs else (f"{items} productos" if items is not None else "")
            if delay is not None:
                det += f" · retraso medido {delay}s"
            print(f"{src:<22} {st:<10} {ago(age):<13} {since:<16} {cycles or 0:>6}  {det}")
        print(f"\nResumen: {ok} OK · {att} con aviso · {bad} necesitan atención (sin ciclo correcto en la última hora o ≥3 errores seguidos)")
        return 0
    if a.command == "preview":
        from .preview import write_preview
        print(f"Vista previa escrita en {write_preview(a.out).resolve()}")
        return 0
    if a.command == "test-webhook":
        from .discord import WebhookSender
        from .preview import test_payload
        url = cfg.webhook_for(a.channel)
        if not url:
            print("Falta el webhook: pon DISCORD_WEBHOOK_DEFAULT=<url> en el fichero .env")
            return 1
        mid = WebhookSender(url).send(test_payload())
        print(f"OK: mensaje de prueba enviado (id {mid}). Míralo en tu canal de Discord.")
        return 0
    if a.command == "probe":
        from .pipeline import _prepare
        from .runner import make_source
        bad = 0
        for m in cfg.monitors:
            if not m.enabled:
                continue
            try:
                if m.type == "bstn":
                    from datetime import datetime, timezone
                    t0 = datetime.now(timezone.utc)
                    items = make_source(m).fetch_launches(t0)
                    raffles = sum(1 for i in items if i.raffle_active)
                    dated = sum(1 for i in items if i.release_ts)
                    print(f"OK    {m.name:<18} {len(items):>4} lanzamientos · {raffles} raffles abiertos · {dated} con fecha")
                    continue
                raw = make_source(m).fetch()
                ok, dropped = _prepare(raw, m)
                avail = sum(1 for p in ok if p.available_variants)
                print(f"OK    {m.name:<18} {len(raw):>4} leídos · {len(ok):>4} pasan filtros · {avail:>4} con stock · {dropped} descartados")
            except Exception as e:
                bad += 1
                print(f"ERROR {m.name:<18} {e}")
        print("Todo correcto: puedes arrancar con 'run'." if not bad else f"{bad} fuentes con error (el resto funciona).")
        return 0 if not bad else 2
    if a.command == "check-releases":
        from .releases import load_calendar
        cal = load_calendar(cfg.defaults.get("releases_file", "config/releases.toml"))
        for r in cal.releases:
            print(f"{r.release_at.isoformat()}  {r.method:<11} {r.verdict:<7} {r.name}")
        print(f"OK: {len(cal.releases)} lanzamientos, canal '{cal.channel}', recordatorios {cal.reminders_minutes} min")
        return 0
    if a.command == "check-config":
        print(f"OK: {len(cfg.monitors)} monitores, {sum(m.enabled for m in cfg.monitors)} activos")
        return 0
    run_all(cfg, a.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
