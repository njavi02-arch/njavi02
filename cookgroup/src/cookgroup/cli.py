from __future__ import annotations

import argparse
import json
import logging
import os
import sys

from .config import load_config
from .runner import run_all


class _JsonFmt(logging.Formatter):
    def format(self, r):
        return json.dumps({"ts": self.formatTime(r), "level": r.levelname, "msg": r.getMessage()})


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
    logging.basicConfig(level=logging.INFO, handlers=[h])
    cfg = load_config(a.config)
    if a.command == "status":
        from datetime import datetime, timezone
        from .store import Store
        rows = Store(a.db).health()
        if not rows:
            print("Sin datos todavía: arranca con 'run' y vuelve a mirar en unos minutos.")
            return 0
        now = datetime.now(timezone.utc)
        print(f"{'fuente':<20} {'estado':<9} {'último ciclo OK':<22} {'errores seguidos':>16}  último error")
        for src, last_ok, errs, last_err, err_at, items, ms, delay in rows:
            age = f"hace {int((now - datetime.fromisoformat(last_ok)).total_seconds() // 60)} min" if last_ok else "nunca"
            st = "OK" if errs == 0 and last_ok else "FALLA" if errs >= 3 else "AVISO"
            extra = f" · retraso medido {delay}s" if delay is not None else ""
            print(f"{src:<20} {st:<9} {age:<22} {errs:>16}  {(last_err or '')[:60]}{extra}")
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
