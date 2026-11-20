"""Panel v0.9: añade al panel v0.8 las pestañas de negocio (cifras, panel del dueño, alta y baja, permisos, mis canales).
Uso: python tools/build_panel_v09.py → docs/v09/PANEL.html (lo abre VER_PANEL.bat)
"""
from __future__ import annotations

import csv
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
E = html.escape


def table(rows, cols, cls=""):
    return (f"<div class=scroll><table class='{cls}'><thead><tr>" + "".join(f"<th>{E(c)}</th>" for c in cols) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{E(str(r.get(c, '')))}</td>" for c in cols) + "</tr>" for r in rows) + "</tbody></table></div>")


def md_table(path):
    rows = [l for l in Path(path).read_text(encoding="utf-8").splitlines() if l.startswith("|")]
    if not rows:
        return ""
    cell = lambda c: re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", E(c.strip()))
    head = [cell(c) for c in rows[0].strip("|").split("|")]
    return ("<div class=scroll><table><tr>" + "".join(f"<th>{h}</th>" for h in head) + "</tr>"
            + "".join("<tr>" + "".join(f"<td>{cell(c)}</td>" for c in r.strip("|").split("|")) + "</tr>" for r in rows[2:]) + "</table></div>")


def md(text):
    out = []
    for l in text.splitlines():
        if l.startswith("# ") or l.startswith("|"):
            continue
        x = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", E(l.lstrip("-0123456789. ").strip()))
        x = re.sub(r"`(.+?)`", r"<code>\1</code>", x)
        if l.startswith("## "):
            out.append(f"<h3>{x[3:] if x.startswith('## ') else E(l[3:])}</h3>")
        elif l.strip():
            out.append(f"<p>{'• ' if l.lstrip().startswith(('-', '1', '2', '3', '4', '5', '6')) else ''}{x}</p>")
    return "".join(out)


def main():
    import build_channel_map
    import build_channel_status
    import build_panel_v08
    import lote2
    import membresias_demo
    build_channel_map.main()
    build_channel_status.main()
    build_panel_v08.main()
    base = (ROOT / "docs/v08/PANEL.html").read_text(encoding="utf-8")
    m = membresias_demo.run(log=lambda *_: None)
    membresias_demo.write_log(m)
    l2 = lote2.run(log=lambda *_: None)
    lote2.write_log(l2)
    from cookgroup.access import matrix
    from cookgroup.preview import _embed_html
    from cookgroup.server_setup import load_design
    mx = matrix(load_design(ROOT / "config/servidor.toml"))
    mine = list(csv.DictReader(open(ROOT / "docs/v09/CANALES_MI_SERVIDOR.csv", encoding="utf-8")))
    ref = list(csv.DictReader(open(ROOT / "docs/v08/canales.csv", encoding="utf-8")))
    comprob = sum(1 for r in ref if r["nivel_evidencia"].startswith("función comprobada"))
    probados = sum(1 for r in mine if r["estado"] == "probado localmente")
    desarr = probados + sum(1 for r in mine if r["estado"].startswith("implementado"))
    real = sum(1 for r in mine if r["estado"] == "entrega real confirmada")
    owner = (ROOT / "docs/v09/PANEL_DUENO_demo.html").read_text(encoding="utf-8")
    owner_body = owner[owner.index("<h1>Panel del dueño</h1>"):owner.rindex("</div></body>")]
    owner_css = """#t-dueno .k{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px}#t-dueno .k div{background:var(--panel);border-radius:8px;padding:10px}
#t-dueno .k b{display:block;font-size:22px;color:#fff}#t-dueno .card{background:var(--panel);border-radius:8px;padding:10px;margin:6px 0}
#t-dueno .tag{background:#fee75c;color:#111}#t-dueno .tag.ok{background:#57f287}#t-dueno .tag.bad{background:#ed4245;color:#fff}"""

    kpis = f"""<div class=kpis>
<div class=kpi><b>{comprob}</b><span>funciones de la referencia comprobadas (de 339 canales vistos)</span></div>
<div class=kpi><b>{desarr}</b><span>equivalentes desarrollados en mi servidor ({probados} probados localmente, de 33 canales)</span></div>
<div class=kpi><b>0</b><span>canales operativos en mi Discord (falta el token del bot para instalar)</span></div>
<div class=kpi><b>{real}</b><span>canales con entrega real confirmada</span></div></div>"""
    plan = (ROOT / "PLAN_MAESTRO.md").read_text(encoding="utf-8")
    t_neg = f"""<h2>Negocio v0.9</h2>{kpis}<h3>Plan maestro</h3>{md_table(ROOT / 'PLAN_MAESTRO.md')}
<h3>Apertura: oferta, costes y pendientes</h3>{md((ROOT / 'docs/v09/APERTURA.md').read_text(encoding='utf-8'))}{md_table(ROOT / 'docs/v09/APERTURA.md')}
<h3>Cómo opero el cookgroup como dueño</h3>{md((ROOT / 'docs/v09/COMO_OPERO.md').read_text(encoding='utf-8'))}"""
    steps = "".join(f"<tr><td>{E(a)}</td><td class='{'ok' if b == 'OK' else 'bad'}'>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in m["steps"])
    t_alta = f"""<h2>Alta y baja en PRUEBA LOCAL</h2><div class=note>Web local real + simulador de Stripe (mismos eventos y firma) + Discord simulado.
No se cobra nada. Con tus claves de prueba de Stripe se usa el mismo código contra Stripe en modo prueba.</div>
<table><tr><th>Paso</th><th>Resultado</th><th>Detalle</th></tr>{steps}</table>"""
    who = ["visitante", "suscriptor", "ex-suscriptor", "moderador", "staff", "propietario"]
    t_perm = f"""<h2>Matriz de permisos (calculada con el algoritmo de Discord y probada con 6 identidades)</h2>
<div class=note>Visitante: presentación, planes, muestra y soporte. Suscriptor: lo contratado. Ex-suscriptor: igual que un visitante,
aunque conserve sus preferencias o un enlace antiguo. Los tickets son hilos privados: solo el cliente y el equipo.</div>
{table(mx, ['categoria', 'canal', 'audiencia'] + who)}"""
    ex = []
    for ch, pl in l2["examples"].items():
        ex.append(f"<h3>#{E(ch)} <span class='tag ctrl'>CAPTURA REAL + CAMBIO CONTROLADO</span></h3><div class=msg><div class=avatar>CG</div>"
                  f"<div class=body><div class=author>Cookgroup <span class=app>APP</span></div>{''.join(_embed_html(e) for e in pl.get('embeds', []))}</div></div>")
    st2 = "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td><td class='{'ok' if c == 'OK' else 'bad'}'>{E(c)}</td><td>{E(d)}</td></tr>" for a, b, c, d in l2["steps"])
    t_can = f"""<h2>Mis canales: ficha de cierre</h2><div class=note>Un canal solo queda «probado localmente» con ejemplo, prueba positiva y caso de silencio.
Ninguno está instalado todavía en tu Discord.</div>
{table(mine, ['categoria', 'canal', 'estado', 'finalidad', 'fuente_o_responsable', 'regla', 'visitante', 'suscriptor', 'ejemplo', 'prueba_positiva', 'caso_silencio'])}
<h3>Pruebas de los canales prioritarios</h3><table><tr><th>Canal</th><th>Prueba</th><th>Resultado</th><th>Detalle</th></tr>{st2}</table>{''.join(ex)}"""
    css = """.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}.kpi{background:var(--panel);border-radius:8px;padding:12px}
.kpi b{display:block;font-size:30px;color:#fff}.kpi span{color:var(--muted);font-size:13px}"""
    page = base.replace("</style>", css + owner_css + "</style>", 1)
    page = page.replace("<h1>Cookgroup v0.8 — panel</h1>", "<h1>Cookgroup v0.9 — panel</h1>")
    page = page.replace('<div class="tabs"><button data-t="resumen" class="on">Resumen v0.8</button>',
                        '<div class="tabs"><button data-t="negocio" class="on">Negocio</button><button data-t="dueno">Panel del dueño (demo)</button>'
                        '<button data-t="alta">Alta y baja</button><button data-t="permisos">Permisos</button><button data-t="canales">Mis canales</button>'
                        '<button data-t="resumen">Resumen v0.8</button>')
    page = page.replace('<div class="tab on" id="t-resumen">', f'''<div class="tab on" id="t-negocio">{t_neg}</div>
<div class="tab" id="t-dueno"><div class=note>DEMO: datos del recorrido de prueba (no son clientes). En tu PC, el panel en vivo con botón «Reintentar» se abre con PANEL_DUENO.bat.</div>{owner_body}</div>
<div class="tab" id="t-alta">{t_alta}</div><div class="tab" id="t-permisos">{t_perm}</div><div class="tab" id="t-canales">{t_can}</div>
<div class="tab" id="t-resumen">''', 1)
    out = ROOT / "docs/v09/PANEL.html"
    out.write_text(page, encoding="utf-8")
    print(out, len(page), comprob, desarr, probados, real)


if __name__ == "__main__":
    main()
