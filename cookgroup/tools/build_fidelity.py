"""Fidelidad canal a canal (v1.1): cada canal de la referencia (339) → nuestro canal, fuente o responsable, permisos,
prueba y estado. Resuelve UNO A UNO los 47 que iban a #sneakers-eu, los 28 de #pokémon-tcg y los 112 sin equivalente.

Estados (de menos a más):
  investigado        → sabemos qué hace el canal de la referencia (recorrido / muestreo)
  desarrollado       → nuestro canal existe en el diseño y tiene fuente o responsable
  probado en local   → su fuente/función pasa una prueba con datos reales en local
  instalado          → el canal existe en tu Discord (un canal vacío cuenta como instalado)
  verificado         → se ha comprobado en Discord que cumple su función (entrega confirmada en ESE canal)

Salidas: docs/v11/FIDELIDAD.csv · docs/v11/FIDELIDAD.html (panel por categoría) · docs/v11/PARES.md
"""
from __future__ import annotations

import csv
import html
import json
import re
import sqlite3
import sys
import tomllib
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from cookgroup.access import matrix  # noqa: E402
from cookgroup.server_setup import load_design  # noqa: E402
from cookgroup.store_directory import load_lote, merchant_key, tested  # noqa: E402

E = html.escape
LEVELS = ["investigado", "desarrollado", "probado en local", "instalado", "verificado"]
# canales base con prueba automática propia (nombre de la prueba)
BASE_TESTS = {
    "raffles": "test_bstn_e2e (reparto y lista)", "raffles-bstn": "test_bstn_e2e", "raffles-cierran-hoy": "test_bstn_e2e (lista de hoy)",
    "alertas-personales": "test_bstn_e2e::one_mention · test_access", "lanzamientos": "test_e2e_runner (foro por SKU)",
    "próximos-7-días": "test_e2e_runner (resumen diario)", "soporte": "test_access::tickets_private", "elige-tus-avisos": "test_access (roles sin permisos)",
    "sneakers-eu": "test_familias / test_real_samples", "sneakers-mundo": "test_familias::undefeated", "baloncesto": "test_familias::baskets",
    "skate": "test_familias::flatspot", "outlet": "test_familias::asos_sample", "streetwear": "test_familias::goodhood",
    "pokémon-tcg": "test_familias::redgoblin", "rebajas-30": "test_core (rutas por descuento)", "rebajas-60": "test_core (rutas por descuento)",
    "chollos": "test_real_samples::chollometro", "muestra-gratis": "test_pilot (muestra con retraso)", "Miembros": "test_membresias (contador)",
    "planes": "test_membresias", "reventa": "test_core (beneficio verificado)",
}


MANUAL = {"📩tickets": ["soporte"], "🤖auto-pinger": ["alertas-personales", "elige-tus-avisos"]}


def our_channels():
    d = load_design(ROOT / "config/servidor.toml")
    chans = {}
    for cat in d["categoria"]:
        for c in cat["canal"]:
            chans[c["nombre"]] = {**c, "categoria_nuestra": cat["nombre"]}
    perms = {r["canal"]: r for r in matrix(d)}
    return chans, perms


def ref_channel_index(chans):
    idx = defaultdict(list)
    for n, c in chans.items():
        for r in (c.get("equivalente_de") or "").split(","):
            if r.strip():
                idx[r.strip()].append(n)
    return idx


def main():
    chans, perms = our_channels()
    by_ref = ref_channel_index(chans)
    lote = load_lote(ROOT / "config/lote_tiendas.toml")
    lot_by_merchant = {merchant_key(t["web"].split("//")[1]): t for t in lote}
    tested_store_ch = {t["canal"]: "lote 1: " + ", ".join(tested(t)) for t in lote if tested(t)}
    store_ch_by_merchant = {}
    for n, c in chans.items():
        if c.get("clase") == "tienda":
            store_ch_by_merchant[merchant_key(n + ".com")] = n
    for k, t in lot_by_merchant.items():
        store_ch_by_merchant[k] = t["canal"]
    huecos = {r["canal"]: r for r in csv.DictReader(open(ROOT / "docs/v10/HUECOS.csv", encoding="utf-8"))}
    ids = {}
    p = ROOT / "data/canales_ids.json"
    if p.exists():
        ids = json.loads(p.read_text(encoding="utf-8"))
    guild, ch_ids = ids.get("guild_id"), ids.get("canales", {})
    delivered = set()
    db = ROOT / "cookgroup.db"
    if db.exists():
        try:
            delivered = {r[0] for r in sqlite3.connect(db).execute(
                "SELECT DISTINCT channel FROM alerts WHERE message_id IS NOT NULL AND channel IS NOT NULL")}
        except sqlite3.Error:
            pass

    rows = []
    for r in csv.DictReader(open(ROOT / "docs/v08/canales.csv", encoding="utf-8")):
        plain = re.sub(r"^[^\w]+", "", r["canal"])
        doms = r["tiendas"].replace("…", "").split() if r["tiendas"] else []
        eq = r["equivalente"]
        nuestros, fuente, nota = [], "", ""
        from build_dedicated import AGG
        own = sorted({store_ch_by_merchant[merchant_key(d)] for d in doms if merchant_key(d) in store_ch_by_merchant})
        if r["canal"] in MANUAL:
            nuestros = MANUAL[r["canal"]]
            fuente = r["quien_alimenta"]
        elif plain in AGG or r["canal"] in AGG:                  # agregados: su canal agregado + canales propios de sus tiendas
            nuestros = [AGG.get(plain) or AGG[r["canal"]]] + own
            fuente = f"{len(doms)} tiendas en la referencia; {len(own)} con canal propio aquí"
        elif by_ref.get(r["canal"]) or by_ref.get(plain):
            nuestros = by_ref.get(r["canal"]) or by_ref.get(plain)
            fuente = ", ".join(chans[nuestros[0]].get("monitores", [])[:6]) or chans[nuestros[0]].get("fuente", "")
        elif eq.startswith("#sneakers-eu"):                       # los 47: tienda por tienda
            nuestros = own + ["sneakers-eu"]
            fuente = f"{len(doms)} tiendas en la referencia; {len(own)} con canal propio aquí"
            nota = "una sola tienda → canal propio pendiente de fuente" if len(doms) == 1 and not own else ""
        elif eq.startswith("#pokémon-tcg"):                       # los 28
            nuestros = ["pokémon-tcg"]
            fuente = "monitores TCG (Red Goblin…)" if "bot" in r["quien_alimenta"] else "staff (editorial)"
            nota = "comunidad/calls → editorial" if "staff" in r["quien_alimenta"] else ""
        elif eq in ("—", ""):                                     # los 112
            h = huecos.get(r["canal"], {})
            prop = h.get("equivalente_propuesto", "")
            m = re.findall(r"#([\w\-áéíóúñü]+)", prop)
            nuestros = [x for x in m if x in chans]
            fuente = h.get("falta_para_activar", "") or "sin fuente"
            nota = (h.get("decision_del_dueño") or "") + ((" · propuesto: " + prop) if prop and not nuestros else "")
        else:
            nuestros = [x for x in re.findall(r"#([\w\-áéíóúñü]+)", eq) if x in chans]
            fuente = r["quien_alimenta"]
        main_ch = nuestros[0] if nuestros else ""
        c = chans.get(main_ch, {})
        pm = perms.get(main_ch, {})
        permisos = f"suscriptor: {pm.get('suscriptor', '—')} · visitante: {pm.get('visitante', '—')}" if pm else "—"
        lot_channels = {t["canal"] for t in lote}
        prueba = tested_store_ch.get(main_ch) or BASE_TESTS.get(main_ch, "")
        weak = ""
        if not prueba and main_ch not in lot_channels and "probado localmente" in r["nivel_evidencia"]:
            weak = "solo comprobación de lectura (" + r["como_se_prueba"][:50] + "); falta prueba con captura real"
        level = "investigado"
        if main_ch and c.get("estado", "construido") in ("construido", "moderacion-humana", "editorial") and (c.get("fuente") or c.get("acceso")):
            level = "desarrollado"
        if level == "desarrollado" and prueba:
            level = "probado en local"
        if main_ch and main_ch in ch_ids:
            level = "instalado"
            key = (c.get("fuente") or "").removeprefix("bot:")
            if key and key in delivered:
                level = "verificado"
        rows.append({"categoria": r["categoria"], "canal_referencia": r["canal"], "que_hace": r["para_que"],
                     "evidencia_referencia": r["nivel_evidencia"], "nuestro_canal": " ".join("#" + x for x in nuestros) or "—",
                     "fuente_o_responsable": fuente, "permisos": permisos, "prueba": prueba or weak, "estado": level, "nota": nota,
                     "enlace": f"https://discord.com/channels/{guild}/{ch_ids[main_ch]}" if guild and main_ch in ch_ids else ""})
    out = ROOT / "docs/v11"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "FIDELIDAD.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out / "FIDELIDAD.html").write_text(render(rows), encoding="utf-8")
    cnt = Counter(r["estado"] for r in rows)
    print(f"{len(rows)} canales: " + " · ".join(f"{k}: {cnt.get(k, 0)}" for k in LEVELS))
    ref = list(csv.DictReader(open(ROOT / "docs/v08/canales.csv", encoding="utf-8")))
    groups = {"47 → #sneakers-eu": {x["canal"] for x in ref if x["equivalente"] == "#sneakers-eu (+ menciones por talla)"},
              "28 → #pokémon-tcg": {x["canal"] for x in ref if x["equivalente"] == "#pokémon-tcg"},
              "112 sin equivalente": {x["canal"] for x in ref if x["equivalente"] in ("—", "")}}
    summary = {}
    for grp, names in groups.items():
        sel = [r for r in rows if r["canal_referencia"] in names]
        summary[grp] = {"total": len(sel), **Counter(r["estado"] for r in sel),
                        "resueltos_con_canal": sum(1 for r in sel if r["nuestro_canal"] != "—")}
        print(grp, summary[grp])
    (out / "FIDELIDAD_resumen.json").write_text(json.dumps({"total": dict(cnt), "grupos": summary}, ensure_ascii=False, indent=1),
                                                 encoding="utf-8")
    return rows


def render(rows) -> str:
    cats = defaultdict(list)
    for r in rows:
        cats[r["categoria"]].append(r)
    cls = {"investigado": "s0", "desarrollado": "s1", "probado en local": "s2", "instalado": "s3", "verificado": "s4"}
    o = ["<!doctype html><html lang=es><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
         "<title>Fidelidad por categoría · cookgroup</title><style>body{font-family:system-ui,sans-serif;margin:0;background:#0f1115;color:#e7e9ee}"
         "main{max-width:1200px;margin:auto;padding:16px}.cats{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.cats button{background:#181b22;color:#e7e9ee;"
         "border:1px solid #333;border-radius:8px;padding:6px 9px;cursor:pointer}.cats button.on{border-color:#8ab4ff}table{width:100%;border-collapse:collapse;font-size:13px}"
         "td,th{padding:6px;border-bottom:1px solid #262a33;text-align:left;vertical-align:top}.tag{padding:2px 7px;border-radius:6px;font-size:12px;font-weight:600}"
         ".s0{background:#2a2d35}.s1{background:#3a2e12;color:#ffd479}.s2{background:#14304a;color:#8ac7ff}.s3{background:#1f3a2a;color:#9be0b4}.s4{background:#12351f;color:#7ee2a0}"
         ".muted{color:#9aa3b2;font-size:12px}a{color:#8ab4ff}</style><main><h1>Fidelidad con la referencia, canal por canal</h1>"
         "<p class=muted>Pulsa una categoría. Un canal vacío cuenta como <b>instalado</b>; <b>verificado</b> exige una entrega confirmada en ese canal.</p>"]
    tot = Counter(r["estado"] for r in rows)
    o.append("<p>" + " · ".join(f"<span class='tag {cls[k]}'>{k}: {tot.get(k, 0)}</span>" for k in LEVELS) + f" de {len(rows)}</p>")
    o.append("<div class=cats><button class=on onclick=\"show('')\">Todas</button>" + "".join(
        f"<button onclick=\"show('{E(c)}')\">{E(c)} ({len(v)})</button>" for c, v in cats.items()) + "</div>")
    o.append("<table><tr><th>Referencia</th><th>Qué hace</th><th>Nuestro canal</th><th>Fuente o responsable</th><th>Permisos</th><th>Prueba</th><th>Estado</th></tr>")
    for r in rows:
        ch = f"<a href='{E(r['enlace'])}'>{E(r['nuestro_canal'])}</a>" if r["enlace"] else E(r["nuestro_canal"])
        o.append(f"<tr data-c='{E(r['categoria'])}'><td>{E(r['canal_referencia'])}<br><span class=muted>{E(r['categoria'])}</span></td>"
                 f"<td>{E(r['que_hace'])}</td><td>{ch}</td><td>{E(r['fuente_o_responsable'])}<br><span class=muted>{E(r['nota'])}</span></td>"
                 f"<td class=muted>{E(r['permisos'])}</td><td class=muted>{E(r['prueba'])}</td><td><span class='tag {cls[r['estado']]}'>{E(r['estado'])}</span></td></tr>")
    o.append("</table></main><script>function show(c){document.querySelectorAll('tr[data-c]').forEach(t=>t.style.display=(!c||t.dataset.c===c)?'':'none');"
             "document.querySelectorAll('.cats button').forEach(b=>b.classList.toggle('on',b.textContent.startsWith(c||'Todas')))}</script></html>")
    return "\n".join(o)


if __name__ == "__main__":
    main()
