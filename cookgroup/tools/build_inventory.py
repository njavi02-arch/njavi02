"""Genera el inventario de tiendas (CSV + HTML filtrable) a partir de:
- docs/reference_harvest.tsv : lo observado en el cookgroup de referencia (canal → tienda → dominio → eventos)
- docs/store_registry.json   : nuestra investigación por dominio (país, regiones, fuente, estado, monitor…)
- config/monitors.toml       : qué monitores existen de verdad

Uso:  python tools/build_inventory.py   → docs/inventory.csv y docs/inventory.html
"""
from __future__ import annotations

import csv
import html
import json
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
STATES = ["identificada", "fuente localizada", "lectura verificada", "evento probado", "ejecutándose", "entrega confirmada"]


def load_harvest() -> dict[str, dict]:
    by_dom: dict[str, dict] = {}
    f = DOCS / "reference_harvest.tsv"
    if not f.exists():
        return by_dom
    for row in csv.DictReader(f.open(encoding="utf-8"), delimiter="\t"):
        dom = (row["domain"] or "?").lower()
        d = by_dom.setdefault(dom, {"names": set(), "channels": set(), "events": defaultdict(int), "count": 0, "last": ""})
        d["names"].add(row["author"])
        d["channels"].add(row["channel"])
        d["count"] += int(row["count"] or 0)
        for e in filter(None, (row["events"] or "").split(",")):
            k, _, v = e.partition(":")
            d["events"][k] += int(v or 1)
        d["last"] = max(d["last"], row["last"] or "")
    return by_dom


def monitors_by_domain() -> dict[str, list[str]]:
    cfg = tomllib.loads((ROOT / "config" / "monitors.toml").read_text())
    out: dict[str, list[str]] = defaultdict(list)
    for m in cfg.get("monitor", []):
        from urllib.parse import urlparse
        dom = (urlparse(m["base_url"]).hostname or "").removeprefix("www.")
        out[dom].append(f"{m['name']} ({m['type']}{', ' + m['collection'] if m.get('collection') else ''})")
    return out


def build() -> list[dict]:
    harvest = load_harvest()
    reg = json.loads((DOCS / "store_registry.json").read_text(encoding="utf-8"))
    mons = monitors_by_domain()
    rows = []
    doms = sorted(set(harvest) | set(reg), key=lambda d: (-(harvest.get(d, {}).get("count", 0)), d))
    for dom in doms:
        if dom in ("?", ""):
            continue
        h, r = harvest.get(dom), reg.get(dom, {})
        monitor = "; ".join(mons.get(dom, [])) or r.get("monitor", "")
        rows.append({
            "tienda": r.get("name") or (sorted(h["names"])[0] if h else dom),
            "dominio": dom,
            "en_referencia": "sí" if h else "no (investigación propia)",
            "canales_referencia": ", ".join(sorted(h["channels"])) if h else "",
            "alertas_observadas": h["count"] if h else 0,
            "eventos_referencia": ", ".join(f"{k}:{v}" for k, v in sorted(h["events"].items(), key=lambda x: -x[1])) if h else "",
            "ultima_vista": h["last"] if h else "",
            "pais": r.get("country", ""),
            "region": r.get("region", ""),
            "categoria": r.get("category", ""),
            "moneda": r.get("currency", ""),
            "envio_es": r.get("ships_es", "por confirmar"),
            "plataforma": r.get("platform", ""),
            "fuente": r.get("source", ""),
            "eventos_propios": r.get("events", ""),
            "monitor": monitor,
            "estado": r.get("status", "identificada" if h else "fuente localizada"),
            "cobertura": r.get("coverage", "pendiente"),
            "motivo_o_nota": r.get("note", ""),
            "ultima_prueba": r.get("checked", ""),
        })
    return rows


def write(rows: list[dict]) -> None:
    with (DOCS / "inventory.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    cols = list(rows[0])
    filt = ["pais", "categoria", "estado", "cobertura", "en_referencia", "plataforma"]
    opts = {c: sorted({str(r[c]) for r in rows if r[c]}) for c in filt}
    head = "".join(f"<th>{html.escape(c.replace('_', ' '))}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f'<td data-c="{c}">{html.escape(str(r[c]))}</td>' for c in cols) + "</tr>" for r in rows)
    selects = "".join(
        f'<label>{c.replace("_", " ")}<select data-f="{c}"><option value="">(todos)</option>'
        + "".join(f"<option>{html.escape(o)}</option>" for o in opts[c]) + "</select></label>" for c in filt)
    summary = defaultdict(int)
    for r in rows:
        summary[r["cobertura"]] += 1
    page = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cookgroup — inventario de tiendas</title><style>
body{{font:13px/1.4 system-ui,sans-serif;margin:0;background:#f6f7f9;color:#1d1f23}}header{{padding:16px 20px;background:#fff;border-bottom:1px solid #e3e5e8;position:sticky;top:0;z-index:2}}
h1{{font-size:18px;margin:0 0 6px}}.f{{display:flex;flex-wrap:wrap;gap:10px;align-items:end}}label{{display:flex;flex-direction:column;font-size:11px;color:#5c626b;text-transform:uppercase;letter-spacing:.02em}}
select,input{{font:13px system-ui;padding:5px 7px;border:1px solid #cfd3d8;border-radius:6px;min-width:130px;background:#fff}}
.wrap{{overflow:auto;padding:0 20px 30px}}table{{border-collapse:collapse;background:#fff;margin-top:12px;min-width:1400px}}th,td{{border-bottom:1px solid #eceef1;padding:6px 8px;text-align:left;vertical-align:top;max-width:280px}}
th{{position:sticky;top:0;background:#fafbfc;font-size:11px;text-transform:uppercase;color:#5c626b}}tr:hover td{{background:#f9fafb}}.n{{color:#5c626b;font-size:12px;margin-top:6px}}
</style></head><body><header><h1>Inventario de tiendas del cookgroup</h1>
<div class="f"><label>buscar<input id="q" placeholder="tienda, dominio, canal…"></label>{selects}</div>
<div class="n" id="count"></div><div class="n">Cobertura: {html.escape(", ".join(f"{k} {v}" for k, v in sorted(summary.items())))} · Estados: {" → ".join(STATES)}</div></header>
<div class="wrap"><table><thead><tr>{head}</tr></thead><tbody id="b">{body}</tbody></table></div>
<script>
const rows=[...document.querySelectorAll('#b tr')], sels=[...document.querySelectorAll('select')], q=document.getElementById('q');
function apply(){{const t=q.value.toLowerCase();let n=0;for(const r of rows){{let ok=!t||r.textContent.toLowerCase().includes(t);
for(const s of sels){{if(s.value&&r.querySelector(`[data-c="${{s.dataset.f}}"]`).textContent!==s.value)ok=false}}r.style.display=ok?'':'none';if(ok)n++}}
document.getElementById('count').textContent=n+' de '+rows.length+' tiendas'}}
q.addEventListener('input',apply);sels.forEach(s=>s.addEventListener('change',apply));apply();
</script></body></html>"""
    (DOCS / "inventory.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    rows = build()
    write(rows)
    print(f"{len(rows)} tiendas → docs/inventory.csv, docs/inventory.html", file=sys.stderr)
