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


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cookgroup")
    ap.add_argument("--config", default="config/monitors.toml")
    ap.add_argument("--db", default=os.environ.get("COOKGROUP_DB", "cookgroup.db"))
    ap.add_argument("command", choices=["run", "check-config", "check-releases"])
    a = ap.parse_args(argv)
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(_JsonFmt())
    logging.basicConfig(level=logging.INFO, handlers=[h])
    cfg = load_config(a.config)
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
