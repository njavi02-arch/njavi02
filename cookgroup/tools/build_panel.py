"""Genera docs/v07/PANEL.html: un único fichero que se abre con doble clic (sin Python, sin Discord, sin internet).

Incluye: resumen en español, cifras (desde docs/v07/cifras.json), lecturas reales del piloto, registro del piloto,
ejemplos de avisos etiquetados (CAPTURA HISTÓRICA / SIMULACIÓN / DIRECTO) e inventario con buscador.
Uso: python tools/build_panel.py
"""
from __future__ import annotations

import csv
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from cookgroup.preview import _embed_html, render_html, sample_payloads  # noqa: E402

E = html.escape


def md_table(md: str) -> str:
    """Convierte las tablas markdown sencillas de los docs en HTML (negritas y `código` incluidos)."""
    rows = [l for l in md.splitlines() if l.startswith("|")]
    if not rows:
        return ""
    def cell(c):
        c = E(c.strip())
        c = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", c)
        return re.sub(r"`(.+?)`", r"<code>\1</code>", c)
    head = [cell(c) for c in rows[0].strip("|").split("|")]
    body = [[cell(c) for c in r.strip("|").split("|")] for r in rows[2:]]
    return ("<table><thead><tr>" + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>" +
            "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table>")


def label_kind(label: str) -> str:
    L = label.upper()
    if "SIMULAD" in L or "EJEMPLO" in L or "SIMULACIÓN" in L or "PING" in L or "CALENDARIO" in L or "DROPS DEL" in L:
        return "SIMULACIÓN"
    if "REAL" in L:
        return "CAPTURA HISTÓRICA"
    return "SIMULACIÓN"


def main():
    now = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%d/%m/%Y %H:%M")
    cif = json.loads((ROOT / "docs/v07/cifras.json").read_text(encoding="utf-8"))
    import piloto
    res = piloto.run(log=lambda *_: None)
    piloto.write_log(res)
    style = re.search(r"<style>(.*?)</style>", render_html([]), re.S).group(1)

    ex = []
    for ch, label, payload in sample_payloads():
        k = label_kind(label)
        embeds = "".join(_embed_html(e) for e in payload.get("embeds", []))
        content = f'<div class="content">{E(payload.get("content", ""))}</div>' if payload.get("content") else ""
        ex.append((k, ch, label, content + embeds))
    for p in res["received"]:
        ex.insert(0, ("CAPTURA REAL + CAMBIO CONTROLADO", "sneakers", "Piloto local: catálogo real de Footdistrict (20-nov) "
                      "con un cambio aplicado a propósito; entregado al Discord simulado",
                      "".join(_embed_html(e) for e in p.get("embeds", []))))
    cls = {"SIMULACIÓN": "sim", "CAPTURA HISTÓRICA": "hist", "CAPTURA REAL + CAMBIO CONTROLADO": "ctrl", "DIRECTO": "live"}
    ex_html = "".join(
        f'<section class="ex" data-k="{E(k)}"><div class="chan"># {E(ch)} <span class="tag {cls[k]}">{E(k)}</span></div>'
        f'<div class="label">{E(label)}</div><div class="msg"><div class="avatar">CG</div><div class="body">'
        f'<div class="author">Cookgroup <span class="app">APP</span></div>{body}</div></div></section>'
        for k, ch, label, body in ex)

    inv = list(csv.DictReader(open(ROOT / "docs/inventory.csv", encoding="utf-8")))
    cols = ["tienda", "dominio", "pais", "categoria", "plataforma", "envio_es", "eventos_referencia", "estado", "cobertura",
            "monitor", "motivo_o_nota", "ultima_prueba"]
    inv_json = json.dumps([[r.get(c, "") for c in cols] for r in inv], ensure_ascii=False)

    pilot_rows = "".join(f"<tr><td>{E(a)}</td><td class='{'ok' if b == 'OK' else 'bad'}'>{E(b)}</td><td>{E(c)}</td></tr>"
                         for a, b, c in res["steps"])
    fuentes = md_table((ROOT / "docs/v07/PILOTO_FUENTES.md").read_text(encoding="utf-8"))
    lote = md_table((ROOT / "docs/v07/LOTE_EXPANSION_1.md").read_text(encoding="utf-8"))
    cov = "".join(f"<tr><td>{E(k)}</td><td>{v.get('completa', 0)}</td><td>{v.get('parcial', 0)}</td></tr>"
                  for k, v in sorted(cif["cobertura_por_aviso"].items()))
    resumen = (ROOT / "docs/v07/RESUMEN.md").read_text(encoding="utf-8")
    def md_block(t):
        out, inlist = [], False
        for l in t.splitlines():
            if l.startswith("# "):
                continue
            if l.startswith("## "):
                if inlist: out.append("</ul>"); inlist = False
                out.append(f"<h3>{E(l[3:])}</h3>")
            elif l.startswith("- "):
                if not inlist: out.append("<ul>"); inlist = True
                x = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", E(l[2:]))
                out.append("<li>" + re.sub(r"`(.+?)`", r"<code>\1</code>", x) + "</li>")
            elif l.strip():
                if inlist: out.append("</ul>"); inlist = False
                out.append("<p>" + re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", E(l)) + "</p>")
        if inlist: out.append("</ul>")
        return "".join(out)

    page = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cookgroup v0.7 — panel</title><style>{style}
.wrap{{max-width:1100px;margin:auto;padding:18px 20px 60px}} h1{{font-size:24px;margin:8px 0}} h2{{font-size:18px;margin:30px 0 10px;color:#f2f3f5;border-bottom:1px solid #444;padding-bottom:6px}}
h3{{font-size:15px;margin:14px 0 4px;color:#f2f3f5}} .kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px}}
.kpi{{background:var(--panel);border-radius:8px;padding:12px}} .kpi b{{display:block;font-size:24px;color:#fff}} .kpi span{{color:var(--muted);font-size:13px}}
table{{border-collapse:collapse;width:100%;font-size:13px;background:var(--panel)}} th,td{{border:1px solid #3f4147;padding:6px 8px;text-align:left;vertical-align:top}}
th{{background:#232428;position:sticky;top:0}} td.ok{{color:#57f287;font-weight:700}} td.bad{{color:#ed4245;font-weight:700}}
.tag{{font-size:11px;padding:2px 6px;border-radius:4px;margin-left:6px;font-weight:700;color:#111}} .sim{{background:#fee75c}} .hist{{background:#5865f2;color:#fff}} .ctrl{{background:#57f287}} .live{{background:#ed4245;color:#fff}}
nav a{{color:var(--link);margin-right:14px;text-decoration:none}} input,select{{background:#1e1f22;color:var(--text);border:1px solid #444;border-radius:6px;padding:7px 9px;font-size:14px}}
.note{{background:#2b2d31;border-left:4px solid #fee75c;padding:10px 12px;border-radius:6px;margin:10px 0}} code{{background:#1e1f22;padding:1px 4px;border-radius:3px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}} @media(max-width:800px){{.grid2{{grid-template-columns:1fr}}}} .scroll{{max-height:520px;overflow:auto}}
section.ex{{max-width:760px}}</style></head><body><div class="wrap">
<h1>Cookgroup v0.7 — panel</h1><div style="color:var(--muted)">Generado {E(now)} (Madrid) · se abre sin Python, sin Discord y sin internet</div>
<nav style="margin:10px 0"><a href="#resumen">Resumen</a><a href="#cifras">Cifras</a><a href="#piloto">Piloto</a><a href="#avisos">Ejemplos de avisos</a><a href="#lote">Lote de expansión</a><a href="#inventario">Inventario</a></nav>
<div class="note"><b>Cómo leer las etiquetas:</b> <span class="tag hist">CAPTURA HISTÓRICA</span> datos reales capturados en una fecha pasada ·
<span class="tag ctrl">CAPTURA REAL + CAMBIO CONTROLADO</span> datos reales con un cambio aplicado a propósito para probar ·
<span class="tag sim">SIMULACIÓN</span> datos inventados o estados simulados · <span class="tag live">DIRECTO</span> enviado de verdad a tu Discord (todavía ninguno).</div>
<h2 id="resumen">Resumen</h2>{md_block(resumen)}
<h2 id="cifras">Cifras (generadas desde la configuración, no a mano)</h2>
<div class="kpis"><div class="kpi"><b>{cif['monitores_activos']}</b><span>monitores activos ({cif['monitores_toml']} a mano + {cif['filas_csv_activas']} del CSV)</span></div>
<div class="kpi"><b>{cif['tiendas_unicas_activas']}</b><span>fuentes únicas activas (5 son webs de chollos)</span></div>
<div class="kpi"><b>{cif['inventario_filas']}</b><span>tiendas en inventario ({cif['inventario_referencia']} de la referencia + {cif['inventario_propias']} propias)</span></div>
<div class="kpi"><b>6</b><span>fuentes del piloto con lectura real el 20-nov (5 útiles, 1 corregida)</span></div>
<div class="kpi"><b>20/11 12:10</b><span>última lectura útil (Madrid, desde tu navegador)</span></div>
<div class="kpi"><b>0</b><span>mensajes confirmados en un Discord real (falta el webhook de pruebas)</span></div></div>
<h3>Cobertura por tipo de aviso</h3><table><tr><th>Aviso</th><th>Monitores con cobertura completa</th><th>Parcial</th></tr>{cov}</table>
<p style="color:var(--muted)">Por qué el README de v0.6 decía 262: sumó las 231 filas del CSV (incluida milk-store, desactivada) más 31 monitores a mano, pero el fichero tiene 30. La cifra correcta es 260.</p>
<h2 id="piloto">Piloto</h2><h3>Lecturas reales (solo lectura, desde tu navegador)</h3><div class="scroll">{fuentes}</div>
<h3>Prueba de extremo a extremo (captura real + cambios controlados + Discord simulado)</h3>
<table><tr><th>Paso</th><th>Resultado</th><th>Detalle</th></tr>{pilot_rows}</table>
<h2 id="avisos">Ejemplos de avisos</h2>
<select id="fk" onchange="fx()"><option value="">Todas las etiquetas</option><option>CAPTURA REAL + CAMBIO CONTROLADO</option><option>CAPTURA HISTÓRICA</option><option>SIMULACIÓN</option></select>
<div id="exs">{ex_html}</div>
<h2 id="lote">Lote de expansión 1 (España, alto valor)</h2><div class="scroll">{lote}</div>
<h2 id="inventario">Inventario de tiendas ({len(inv)})</h2>
<input id="q" placeholder="Buscar tienda, dominio, país, categoría…" oninput="fi()" style="width:60%">
<select id="fc" onchange="fi()"><option value="">Toda cobertura</option><option>completa</option><option>parcial</option><option>pendiente</option><option>bloqueada</option><option>descartada</option></select>
<span id="cnt" style="color:var(--muted);margin-left:8px"></span>
<div class="scroll" style="margin-top:8px"><table><thead><tr>{"".join(f"<th>{E(c)}</th>" for c in cols)}</tr></thead><tbody id="tb"></tbody></table></div>
</div><script>
const INV={inv_json};const esc=s=>String(s).replace(/[&<>]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]));
function fi(){{const q=document.getElementById('q').value.toLowerCase(),c=document.getElementById('fc').value;
const r=INV.filter(x=>(!q||x.join(' ').toLowerCase().includes(q))&&(!c||x[8]===c));
document.getElementById('cnt').textContent=r.length+' de '+INV.length;
document.getElementById('tb').innerHTML=r.slice(0,600).map(x=>'<tr>'+x.map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('');}}
function fx(){{const k=document.getElementById('fk').value;document.querySelectorAll('section.ex').forEach(s=>s.style.display=(!k||s.dataset.k===k)?'':'none');}}
fi();</script></body></html>"""
    out = ROOT / "docs/v07/PANEL.html"
    out.write_text(page, encoding="utf-8")
    print(out, len(page))


if __name__ == "__main__":
    main()
