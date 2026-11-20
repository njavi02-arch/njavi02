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


EVN = {"N": "nuevo", "R": "restock", "P": "bajada de precio", "S": "rebajas", "F": "raffle", "L": "lanzamiento", "B": "vuelve stock"}


def load_harvest() -> dict[str, dict]:
    """docs/reference_classified.tsv (canal → tienda → dominio → eventos, clasificado)."""
    by_dom: dict[str, dict] = {}
    f = DOCS / "reference_classified.tsv"
    if not f.exists():
        return by_dom
    for row in csv.DictReader(f.open(encoding="utf-8"), delimiter="\t"):
        dom = row["domain"].lower().removeprefix("www.")
        ev = defaultdict(int)
        for e in filter(None, (row["events"] or "").split(",")):
            k = e.rstrip("0123456789")
            ev[EVN.get(k, k)] += int(e[len(k):] or 1)
        by_dom[dom] = {"names": {row["names"]}, "channels": set(row["channels"].split(",")), "events": ev,
                       "count": int(row["alerts_sampled"] or 0), "last": "2026-" + row["last_seen"] if row["last_seen"] else "",
                       "platform": row["platform"], "category": row["category"], "country": row["country"]}
    return by_dom


def monitors_by_domain() -> dict[str, list[str]]:
    sys.path.insert(0, str(ROOT / "src"))
    from urllib.parse import urlparse

    from cookgroup.config import load_config
    out: dict[str, list[str]] = defaultdict(list)
    for m in load_config(ROOT / "config" / "monitors.toml").monitors:
        dom = (urlparse(m.base_url).hostname or "").removeprefix("www.")
        out[dom].append(f"{m.name} ({m.type}{', ' + m.collection if m.collection else ''}{'' if m.enabled else ', desactivado'})")
    for f in ("bstn.com",):
        out.setdefault(f, [])
    return out


PENDING_REASON = {
    "mesh (grupo JD)": ("bloqueada", "JD Sports/size?/Footpatrol: la consulta automatizada de JD falla incluso en navegador; size? y Footpatrol cubiertos vía colección launches de Shopify"),
    "zalando": ("pendiente", "Zalando no ofrece catálogo público consultable; la referencia usa un proveedor externo (yeet). Buscar API de afiliados"),
    "marca (web propia)": ("pendiente", "web de marca con protección anti-bot o calendario solo en app (SNKRS/CONFIRMED); probar JSON-LD de fichas"),
    "propia/por confirmar": ("pendiente", "plataforma propia: probar adaptador JSON-LD (listado + fichas)"),
    "propia/por confirmar (skate/basket)": ("pendiente", "plataforma propia: probar adaptador JSON-LD"),
    "amazon": ("pendiente", "requiere API de afiliados de Amazon (acceso comercial autorizado)"),
    "retail/outlet propio": ("pendiente", "Privalia/Miravia/Lidl/PcComponentes: sin fuente pública estable localizada; Privalia exige sesión"),
    "rss pepper": ("completa", ""),
    "shopify": ("parcial", "monitor configurado; falta confirmar lectura desde el bot (PROBAR.bat)"),
}


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
        if h and h["platform"] == "no es tienda":
            continue
        monitor = "; ".join(mons.get(dom, [])) or r.get("monitor", "")
        plat = h["platform"] if h else r.get("platform", "")
        cov, why = PENDING_REASON.get(plat, ("pendiente", ""))
        if not monitor and cov in ("parcial", "completa") and plat == "shopify":
            cov, why = "pendiente", "Shopify duplicado de otra web de la misma tienda o desactivado"
        rows.append({
            "tienda": r.get("name") or (sorted(h["names"])[0] if h else dom),
            "dominio": dom,
            "en_referencia": "sí" if h else "no (investigación propia)",
            "canales_referencia": ", ".join(sorted(h["channels"])) if h else "",
            "alertas_observadas": h["count"] if h else 0,
            "eventos_referencia": ", ".join(f"{k}:{v}" for k, v in sorted(h["events"].items(), key=lambda x: -x[1])) if h else "",
            "ultima_vista": h["last"] if h else "",
            "pais": r.get("country") or (h or {}).get("country", ""),
            "region": r.get("region", ""),
            "categoria": r.get("category") or (h or {}).get("category", ""),
            "moneda": r.get("currency", ""),
            "envio_es": r.get("ships_es", "por confirmar"),
            "plataforma": r.get("platform") or plat,
            "fuente": r.get("source", ""),
            "eventos_propios": r.get("events", ""),
            "monitor": monitor,
            "estado": r.get("status") or ("fuente localizada" if monitor else "identificada en la referencia"),
            "cobertura": (r.get("coverage") or cov).split(" (")[0],
            "motivo_o_nota": r.get("note") or (r.get("coverage", "").partition(" (")[2].rstrip(")")) or why,
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
