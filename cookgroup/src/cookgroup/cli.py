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
    ap.add_argument("command", choices=["run", "check-config", "check-releases", "probe", "test-webhook", "preview", "status", "servidor", "miembros", "web", "cuenta"])
    ap.add_argument("--channel", default="default", help="test-webhook: canal cuyo webhook probar")
    ap.add_argument("--out", default="preview.html", help="preview: fichero HTML de salida")
    ap.add_argument("--solo", help="probe: monitores o dominios separados por comas")
    ap.add_argument("--buscar", help="probe: solo los que contengan este texto (nombre, tienda o dominio)")
    ap.add_argument("--limite", type=int, help="probe: como mucho N fuentes")
    ap.add_argument("--reanudar", action="store_true", help="probe: continuar el último lote donde se cortó")
    ap.add_argument("--reintentar", help="cuenta: reintentar la sincronización del rol de este miembro (id de Discord)")
    ap.add_argument("--puerto", type=int, default=8765, help="web: puerto local")
    ap.add_argument("--aplicar", action="store_true", help="servidor: crear en Discord lo que falte (si no, solo muestra el plan)")
    ap.add_argument("--sincronizar", action="store_true", help="miembros: leer los roles elegidos y escribir config/miembros.toml")
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
        from .diagnostics import lag_label, process_state
        pst, pdet = process_state()
        print(f"PROCESO: {pst} — {pdet}\n")
        intervals = {m.name: m.interval_seconds for m in cfg.monitors}
        rows = Store(a.db).health()
        if not rows:
            print("Sin datos todavía: arranca con 'run' y vuelve a mirar en unos minutos.")
            return 0
        now = datetime.now(timezone.utc)
        mins = lambda iso: int((now - datetime.fromisoformat(iso)).total_seconds() // 60) if iso else None
        def ago(m):
            return "nunca" if m is None else f"hace {m} min" if m < 120 else f"hace {m // 60} h" if m < 2880 else f"hace {m // 1440} d"
        ok = att = bad = 0
        print(f"{'fuente':<22} {'estado':<10} {'ritmo':<14} {'último OK':<13} {'desde (Madrid)':<16} {'ciclos':>6}  detalle")
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
            det = (last_err or "")[:70] if errs else ("respuesta VACÍA (0 elementos)" if items == 0 else f"{items} elementos leídos" if items is not None else "")
            lag = lag_label(last_ok, intervals.get(src, 600))
            if delay is not None:
                det += f" · retraso medido {delay}s"
            print(f"{src:<22} {st:<10} {lag:<14} {ago(age):<13} {since:<16} {cycles or 0:>6}  {det}")
        print(f"\nResumen: {ok} OK · {att} con aviso · {bad} necesitan atención (sin ciclo correcto en la última hora o ≥3 errores seguidos)")
        return 0
    if a.command == "preview":
        from .preview import write_preview
        print(f"Vista previa escrita en {write_preview(a.out).resolve()}")
        return 0
    if a.command == "test-webhook":
        # v0.9: la prueba SOLO puede ir a #pruebas-bot (DISCORD_WEBHOOK_PRUEBAS); nunca al webhook general
        from .real_delivery import Refused, send_first_real
        from .store import Store
        try:
            row = send_first_real(store=Store(a.db))
        except Refused as e:
            print(f"NO SE HA ENVIADO NADA: {e}")
            return 1
        print(f"{row['estado'].upper()}: mensaje {row['message_id']} en #{row['canal']} (canal {row['channel_id']}, "
              f"servidor {row['guild_id']}). Registrado en docs/v09/ENTREGAS_REALES.csv")
        return 0 if row["estado"] == "entrega real confirmada" else 2
    if a.command == "probe":
        from .diagnostics import finish_batch, run_probe, select
        from .pipeline import _prepare
        from .runner import make_source
        from .store import Store
        ms = select(cfg.monitors, only=a.solo, match=a.buscar, limit=a.limite, resume=a.reanudar)
        if not ms:
            print("No hay fuentes que comprobar con ese filtro (o el lote ya estaba terminado).")
            return 0
        print(f"Comprobando {len(ms)} fuentes (solo lectura, no se envía nada a Discord)…")
        rows = run_probe(ms, make_source, _prepare, Store(a.db), resume=a.reanudar)
        if not a.limite and not a.solo and not a.buscar:
            finish_batch()
        return 0 if not any(r.status == "FALLO" for r in rows) else 2
    if a.command == "check-releases":
        from .releases import load_calendar
        cal = load_calendar(cfg.defaults.get("releases_file", "config/releases.toml"))
        for r in cal.releases:
            print(f"{r.release_at.isoformat()}  {r.method:<11} {r.verdict:<7} {r.status.upper():<10} {r.name}")
        n_ok = sum(r.status == "confirmado" for r in cal.releases)
        print(f"OK: {len(cal.releases)} lanzamientos ({n_ok} confirmados con fuente oficial; los pendientes NO se avisan), canal '{cal.channel}', recordatorios {cal.reminders_minutes} min")
        return 0
    if a.command in ("web", "cuenta"):
        from .billing import Billing, DiscordRoles, load_plans
        from .store import Store
        from .web import App, LocalRoles, auto_reconcile_once, serve, start_auto_reconcile
        b = Billing(Store(a.db), load_plans())
        tok, gid, rid = (os.environ.get(k) for k in ("DISCORD_BOT_TOKEN", "DISCORD_GUILD_ID", "DISCORD_ROL_SUSCRIPTOR_ID"))
        roles = DiscordRoles(tok, gid, rid) if (tok and gid and rid) else LocalRoles()
        app = App(b, roles)
        if a.command == "cuenta":
            if not a.reintentar:
                print("Uso: cookgroup cuenta --reintentar <id de Discord>")
                return 1
            print(b.reconcile(roles, only=a.reintentar, actor="dueño (consola)"))
            return 0
        pin = os.environ.get("PANEL_PIN") or __import__("secrets").token_hex(3)
        start_auto_reconcile(app)
        srv = serve(app, pin, a.puerto)
        print(f"Modo: {app.mode} · Discord: {'bot real' if isinstance(roles, DiscordRoles) else 'SIMULADO (sin DISCORD_BOT_TOKEN/ROL)'}")
        print(f"Página de venta:   http://127.0.0.1:{a.puerto}/")
        print(f"Panel del dueño:   http://127.0.0.1:{a.puerto}/admin?pin={pin}")
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
        return 0
    if a.command == "servidor":
        from pathlib import Path
        from .server_setup import DiscordAPI, apply, load_design, make_plan, read_env_keys, render_plan
        d = load_design()
        tok, gid = os.environ.get("DISCORD_BOT_TOKEN"), os.environ.get("DISCORD_GUILD_ID")
        if not a.aplicar or not (tok and gid):
            print(render_plan(make_plan(d, [], [], read_env_keys(Path(".env")))))
            if a.aplicar:
                print("\nFalta DISCORD_BOT_TOKEN y/o DISCORD_GUILD_ID en .env: no se ha creado nada.")
                return 1
            print("\n(Vista previa sobre un servidor vacío. Con --aplicar y el token del bot se crea lo que falte.)")
            return 0
        apply(d, DiscordAPI(tok, gid), Path(".env"))
        return 0
    if a.command == "miembros":
        from .members import load_profiles
        if a.sincronizar:
            print("La sincronización lee los roles con el bot (DISCORD_BOT_TOKEN) y requiere activar «Server Members Intent» "
                  "en el portal de desarrolladores. Pendiente de tu token; mientras, se usa config/miembros.toml.")
        for pr in load_profiles(cfg.defaults.get("members_file", "config/miembros.toml")):
            print(f"{pr.name}: familias={sorted(pr.families)} marcas={sorted(pr.brands)} regiones={sorted(pr.regions)} "
                  f"tallas={sorted(pr.sizes)} pausa={pr.paused}")
        return 0
    if a.command == "check-config":
        print(f"OK: {len(cfg.monitors)} monitores, {sum(m.enabled for m in cfg.monitors)} activos")
        return 0
    run_all(cfg, a.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
