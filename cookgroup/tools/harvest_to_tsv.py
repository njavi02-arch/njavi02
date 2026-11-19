"""Convierte el volcado del muestreador de canales (JSON del navegador) en docs/reference_harvest.tsv.

Entrada (stdin o fichero): {"<channel_id>": {"name", "msgs", "oldest", "newest", "stores": [[author, domain, n, events, last], ...]}}
Solo se guardan nombres de tiendas (autor del webhook), dominios, recuentos y tipos de evento: nada de miembros.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"


def main(src: str | None = None) -> None:
    data = json.loads(Path(src).read_text() if src else sys.stdin.read())
    out = DOCS / "reference_harvest.tsv"
    chans = DOCS / "reference_channels.tsv"
    with out.open("w", newline="", encoding="utf-8") as f, chans.open("w", newline="", encoding="utf-8") as g:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["channel", "author", "domain", "count", "events", "last"])
        c = csv.writer(g, delimiter="\t")
        c.writerow(["channel_id", "channel", "messages_sampled", "oldest_reached", "newest", "stores", "resume_hint"])
        for cid, r in sorted(data.items(), key=lambda x: x[1]["name"]):
            for a, d, n, ev, last in r["stores"]:
                w.writerow([r["name"], a or "", d or "", n, ev or "", last or ""])
            c.writerow([cid, r["name"], r["msgs"], r["oldest"], r["newest"], len(r["stores"]),
                        f"continuar antes de {r['oldest']} (jump por snowflake de esa fecha)"])
    print(f"{out} y {chans} escritos", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
