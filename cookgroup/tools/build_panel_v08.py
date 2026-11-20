"""Panel v0.8: añade al panel de v0.7 las pestañas «Mi Discord», «Mi recorrido» y «Canales de la referencia».
Uso: python tools/build_panel_v08.py  → docs/v08/PANEL.html (lo abre VER_PANEL.bat)
"""
from __future__ import annotations

import csv
import html
import json
import re
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from cookgroup.preview import _embed_html, sample_payloads  # noqa: E402

E = html.escape
# Última lectura útil MEDIDA por canal de mi servidor (lecturas reales del 20-nov desde tu navegador, ver docs/v07/PILOTO_FUENTES.md)
LAST_READ = {"sneakers": "20/11 12:10 · Footdistrict, Asphaltgold, Solebox, Snipes (lectura real)",
             "chollos": "20/11 12:09 · Chollometro (lectura real)",
             "lanzamientos": "20/11 12:09 · BSTN, 17 lanzamientos (lectura real)",
             "raffles": "20/11 12:09 · BSTN, 2 raffles abiertos (lectura real)",
             "restocks": "20/11 12:39 · Footdistrict páginas 1-3, 750 productos (lectura real)"}


def main():
    import build_panel
    import lote1
    build_panel.main()                                   # regenera el panel v0.7 (piloto incluido)
    base = (ROOT / "docs/v07/PANEL.html").read_text(encoding="utf-8")
    head = base[:base.index('<div class="wrap">')]
    old_body = base[base.index('<h2 id="resumen">'):base.index("</div><script>")]
    old_script = base[base.index("</div><script>") + len("</div><script>"):base.index("</script></body>")]
    res = lote1.run(log=lambda *_: None)
    lote1.write_log(res)
    design = tomllib.loads((ROOT / "config/servidor.toml").read_text(encoding="utf-8"))
    samples = {}
    for ch, label, payload in sample_payloads():
        samples.setdefault(ch, (label, payload))
    samples["sneakers"] = ("CAPTURA REAL + CAMBIO CONTROLADO: vuelve la EU 44,5 (con tu mención)", res["received"])

    def msg(payload, label, kind):
        content = f'<div class="content">{E(payload.get("content", ""))}</div>' if payload.get("content") else ""
        cls = {"SIMULACIÓN": "sim", "CAPTURA HISTÓRICA": "hist", "CAPTURA REAL + CAMBIO CONTROLADO": "ctrl"}[kind]
        return (f'<div class="label"><span class="tag {cls}">{E(kind)}</span> {E(label)}</div><div class="msg"><div class="avatar">CG</div>'
                f'<div class="body"><div class="author">Cookgroup <span class="app">APP</span></div>{content}'
                + "".join(_embed_html(e) for e in payload.get("embeds", [])) + "</div></div>")

    texts = (ROOT / "docs/v08/TEXTOS_SERVIDOR.md").read_text(encoding="utf-8")
    sec = {m.group(1): m.group(2).strip() for m in re.finditer(r"^## #(\S+)\n(.*?)(?=^## |\Z)", texts, re.M | re.S)}
    tree = []
    for cat in design["categoria"]:
        items = []
        for ch in cat["canal"]:
            key = ch["fuente"].split(":", 1)[1] if ch["fuente"].startswith("bot:") else None
            if key and key in samples:
                lab, pl = samples[key]
                kind = "CAPTURA REAL + CAMBIO CONTROLADO" if "CAMBIO" in lab else "CAPTURA HISTÓRICA" if "real" in lab.lower() and "SIMUL" not in lab.upper() else "SIMULACIÓN"
                ex = msg(pl, lab, kind)
            elif ch["nombre"] in sec:
                ex = f'<div class="label"><span class="tag sim">TEXTO PROPIO</span></div><pre class="txt">{E(sec[ch["nombre"]])}</pre>'
            else:
                ex = '<div class="label">Sin ejemplo todavía: ' + E({"siguiente-lote": "siguiente lote", "ampliacion": "ampliación propia",
                                                                    "moderacion-humana": "depende de una persona (flujo en guía)"}.get(ch["estado"], "")) + "</div>"
            st = {"construido": "construido", "siguiente-lote": "siguiente lote", "ampliacion": "ampliación",
                  "moderacion-humana": "moderación humana"}[ch["estado"]]
            items.append(f'''<details class="ch"><summary><span class="hash">{"💬" if ch["tipo"] == "foro" else "📢" if ch["tipo"] == "anuncios" else "#"}</span>
{E(ch["nombre"])} <span class="st st-{ch["estado"]}">{st}</span> <span class="acc">{E(ch["acceso"])}</span></summary>
<div class="meta"><b>Finalidad:</b> {E(ch["finalidad"])}<br><b>Fuente u operador:</b> {E(ch["fuente"])}<br><b>Regla de publicación:</b> {E(ch["regla"])}
<br><b>Última lectura útil:</b> {E(LAST_READ.get(key or "", "sin lectura medida"))}<br><b>Última entrega confirmada:</b> ninguna (falta el webhook / bot)
<br><b>En mi servidor:</b> pendiente de instalar (INSTALAR_SERVIDOR.bat)</div>{ex}</details>''')
        tree.append(f'<div class="cat"><div class="catn">{E(cat["nombre"])}</div>{"".join(items)}</div>')
    roles = design["roles"]
    roles_html = "".join(f"<p><b>{E(k)}</b>: " + ", ".join(E(x) for x in (v if k != "tallas_eu" else [f"EU {t}" for t in v])) + "</p>"
                         for k, v in roles.items())

    steps = "".join(f"<tr><td>{E(a)}</td><td class='{'ok' if b == 'OK' else 'bad'}'>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in res["steps"])
    journey = f'''<h2>Mi recorrido: de elegir mi talla a recibir la alerta</h2>
<div class="note">Perfil de prueba: <b>EU 44,5 · ASICS y New Balance · envío a España</b>. Datos: <b>captura real de Footdistrict (20-nov 12:39)</b>
con el stock tal cual (las New Balance 990v7 no tenían la 44,5; las ASICS Kayano 14 solo la 42,5 y la 43,5) y <b>cambios controlados</b>.
Discord <b>simulado</b>: todavía no hay entrega real.</div>
<ol class="journey"><li><b>Entras al servidor</b> y en las preguntas de bienvenida marcas: Sneakers, Rebajas, Lanzamientos, Raffles · ASICS, New Balance · Envío a España · EU 44,5.</li>
<li><b>El bot convierte tus roles en tu perfil</b> (con el token del bot, `cookgroup miembros --sincronizar`).</li>
<li><b>Vuelve la EU 44,5 de las New Balance en Footdistrict</b> → aviso en #sneakers-eu y <b>mención solo para ti</b>:</li></ol>
{msg(res["received"], "Lo que recibirías", "CAPTURA REAL + CAMBIO CONTROLADO")}
<ol start="4" class="journey"><li><b>Vuelve la EU 44 de las ASICS</b> (no es tu talla) → el aviso se publica en el canal, <b>pero no te menciona</b>:</li></ol>
{msg(res["discarded"], "Lo que tus filtros descartan (sin mención)", "CAPTURA REAL + CAMBIO CONTROLADO")}
<h3>Todas las comprobaciones (incluidos los silencios)</h3><table><tr><th>Paso</th><th>Resultado</th><th>Detalle</th></tr>{steps}</table>'''

    ref = list(csv.DictReader(open(ROOT / "docs/v08/canales.csv", encoding="utf-8")))
    cols = ["categoria", "canal", "tipo", "para_que", "que_publica", "quien_alimenta", "equivalente", "que_falta", "como_se_prueba",
            "documentado", "existe_en_mi_servidor", "recibe_datos", "entrega_confirmada", "n_tiendas", "tiendas"]
    ref_json = json.dumps([[r[c] for c in cols] for r in ref], ensure_ascii=False)
    now = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%d/%m/%Y %H:%M")
    resumen = (ROOT / "docs/v08/RESUMEN.md").read_text(encoding="utf-8") if (ROOT / "docs/v08/RESUMEN.md").exists() else ""
    def md(t):
        out, inl = [], False
        for l in t.splitlines():
            if l.startswith("# "):
                continue
            if l.startswith("## "):
                out.append(("</ul>" if inl else "") + f"<h3>{E(l[3:])}</h3>"); inl = False
            elif l.lstrip().startswith("- "):
                sub = l.startswith("  ")
                x = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", E(l.lstrip()[2:]))
                out.append(("" if inl else "<ul>") + f"<li{' style=margin-left:22px;list-style:circle' if sub else ''}>"
                           + re.sub(r"`(.+?)`", r"<code>\1</code>", x) + "</li>"); inl = True
            elif l.strip():
                out.append(("</ul>" if inl else "") + "<p>" + re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", E(l)) + "</p>"); inl = False
        return "".join(out) + ("</ul>" if inl else "")
    css = """
.tabs{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0 4px}.tabs button{background:#2b2d31;color:var(--text);border:1px solid #444;border-radius:6px;padding:9px 14px;font-size:14px;cursor:pointer;min-height:40px}
.tabs button.on{background:#5865f2;color:#fff;border-color:#5865f2}.tab{display:none}.tab.on{display:block}
.cat{margin:14px 0}.catn{font-size:12px;font-weight:700;color:var(--muted);text-transform:uppercase;margin-bottom:4px}
details.ch{background:var(--panel);border-radius:6px;margin:4px 0;padding:6px 10px}details.ch summary{cursor:pointer;font-weight:600}
.hash{color:var(--muted);margin-right:4px}.st{font-size:11px;padding:1px 6px;border-radius:4px;margin-left:6px;color:#111;font-weight:700}
.st-construido{background:#57f287}.st-siguiente-lote{background:#fee75c}.st-ampliacion{background:#a8b0ff}.st-moderacion-humana{background:#f0b232}
.acc{font-size:11px;color:var(--muted);margin-left:6px}.meta{font-size:13px;color:#c9cdd3;margin:8px 0;line-height:1.6}pre.txt{white-space:pre-wrap;background:#1e1f22;padding:10px;border-radius:6px;font-size:13px}
ol.journey li{margin:6px 0}"""
    head = head.replace("</style>", css + "</style>")
    page = f'''{head}<div class="wrap"><h1>Cookgroup v0.8 — panel</h1><div style="color:var(--muted)">Generado {E(now)} (Madrid) · sin Python, sin Discord y sin internet</div>
<div class="tabs"><button data-t="resumen" class="on">Resumen v0.8</button><button data-t="midiscord">Mi Discord</button><button data-t="recorrido">Mi recorrido</button><button data-t="referencia">Canales de la referencia ({len(ref)})</button><button data-t="v07">Piloto, cifras e inventario</button></div>
<div class="tab on" id="t-resumen"><h2>Resumen v0.8</h2>{md(resumen)}</div>
<div class="tab" id="t-midiscord"><h2>Mi Discord (diseño que instala INSTALAR_SERVIDOR.bat)</h2>
<div class="note">Recorre categorías y canales: finalidad, fuente, regla de publicación, ejemplo, última lectura útil y última entrega confirmada. Hoy tu servidor tiene general, juegos, música y 2 canales de voz: <b>se conservan</b>. Nada de esto está creado todavía en Discord.</div>
{"".join(tree)}<h3>Roles que se crean (para las preguntas de bienvenida)</h3>{roles_html}</div>
<div class="tab" id="t-recorrido">{journey}</div>
<div class="tab" id="t-referencia"><h2>Canales de la referencia (recorrido del 20-nov) cruzados con mi proyecto</h2>
<input id="q2" placeholder="Buscar canal, categoría, tienda, equivalente…" oninput="fr()" style="width:60%">
<select id="f2" onchange="fr()"><option value="">Todo</option><option>no (instalador listo)</option><option>función, sin canal propio</option><option>no aplica</option></select>
<span id="c2" style="color:var(--muted);margin-left:8px"></span>
<div class="scroll" style="margin-top:8px"><table><thead><tr>{"".join(f"<th>{E(c)}</th>" for c in cols)}</tr></thead><tbody id="tb2"></tbody></table></div></div>
<div class="tab" id="t-v07">{old_body}</div>
</div><script>{old_script}
const REF={ref_json};
function fr(){{const q=document.getElementById('q2').value.toLowerCase(),f=document.getElementById('f2').value;
const r=REF.filter(x=>(!q||x.join(' ').toLowerCase().includes(q))&&(!f||x[10]===f));document.getElementById('c2').textContent=r.length+' de '+REF.length;
document.getElementById('tb2').innerHTML=r.map(x=>'<tr>'+x.map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('');}}
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x===b));
document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('on',t.id==='t-'+b.dataset.t));}});fr();</script></body></html>'''
    out = ROOT / "docs/v08/PANEL.html"
    out.write_text(page, encoding="utf-8")
    print(out, len(page))


if __name__ == "__main__":
    main()
