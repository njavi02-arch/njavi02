"""Inventario maestro (v1.3): UNA fila por cada uno de los 339 canales de la referencia, con identificador estable,
más un listado aparte de tiendas monitorizadas (ampliación europea, fuera del total de referencia).

Estados técnicos comprobables:
  investigado         → sabemos qué hace el canal de la referencia
  construido          → hay implementación (código, canal diseñado, contenido o flujo editorial redactado)
  probado localmente  → una prueba automática con datos reales pasa
Estados en Discord:
  no instalado · instalado · entrega probada (mensaje de prueba recibido) · verificado con evento real

Salidas: docs/v12/INVENTARIO_MAESTRO.csv · docs/v12/INVENTARIO_MAESTRO.html (filtros) · docs/v12/TIENDAS_MONITORIZADAS.csv
"""
from __future__ import annotations

import csv
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cookgroup.config import load_config  # noqa: E402
from cookgroup.store_directory import load_lote  # noqa: E402

# --- trabajo de la sesión v1.3 que cambia el estado de canales concretos de la referencia
FASE2 = {  # canal de referencia → (nuestro canal, monitor, prueba)
    "kickz": ("#kickz", "kickz-releases", "test_tiendas_fase2[www.kickz.com]"),
    "43einhalb": ("#43einhalb", "43einhalb", "test_tiendas_fase2[www.43einhalb.com]"),
    "skatedeluxe": ("#skatedeluxe", "skatedeluxe", "test_tiendas_fase2[www.skatedeluxe.com]"),
    "basket4ballers": ("#basket4ballers", "basket4ballers", "test_tiendas_fase2[www.basket4ballers.com]"),
    "new-balance": ("#new-balance", "newbalance-es", "test_tiendas_fase2[www.newbalance.es]"),
    "web-naranja-españa": ("#zalando-es", "zalando-es", "test_tiendas_fase2[www.zalando.es]"),
    "adidas-es": ("#adidas-es", "adidas-es", "test_tiendas_fase2[www.adidas.es]"),
    "footlocker-es": ("#footlocker-es", "footlocker-es", "test_tiendas_fase2[www.footlocker.es]"),
}
PENDIENTE_TIENDA = {  # solo lo que sigue sin integrar a 23-nov (lo integrado sale de config/lote*_tiendas.toml)
    "luisaviaroma": "desafío Cloudflare sin cookies (23-nov) → feed de afiliados o permiso de la tienda",
    "aboutyou-yoox": "About You integrada (#aboutyou-es); YOOX: desafío Akamai sin cookies (23-nov) → feed de afiliados",
    "sivasdescalzo-raffles": "raffles solo en su app (sin fuente web pública)",
    "adidas-eu": "adidas DE/FR: JSON-LD con colores sin precio ni stock (21-nov) → no integrable por esta vía; adidas IT sin muestra agotada",
    "canary-yellow": "canary---yellow.com: /products.json responde pero el 23-nov solo había ropa infantil agotada; falta una muestra útil",
    "corteiz": "crtz.xyz: /products.json responde 401 (tienda cerrada con contraseña entre drops) → solo en drop abierto",
    "zara": "Zara ES: el catálogo sin cookies es una página vacía de ~2 KB (23-nov) → sin fuente pública legible",
    "zara-instore": "stock en tienda física de Zara: sin fuente pública",
    "uniqlo": "Uniqlo ES: web que monta el catálogo en el navegador; sin cookies, página vacía de 2,7 KB (23-nov)",
    "hym": "H&M ES: listado de novedades legible (49 fichas) pero la ficha devuelve desafío anti-bot (23-nov) → solo descubrimiento; adaptador de listado pendiente",
    "sephora": "Sephora ES: listado legible pero la ficha devuelve desafío anti-bot (23-nov) → solo descubrimiento; adaptador de listado pendiente",
    "aliexpress-labubu": "Pop Mart ES: la extensión no tiene permiso en popmart.com → dar permiso al sitio para comprobarlo; AliExpress: sin fuente pública",
    "steiff": "steiff.com/es-es responde 404: sin tienda española; mercados DE/EN sin comprobar",
    "asos": "ASOS ES integrada en #asos-es; otros mercados de ASOS sin auditar",
}
GUIAS = {"💰neobancos": "06-pagos-y-neobancos.md", "📊excel-inventario": "01-inventario-y-margen.md + inventario_margen.csv",
         "🛠zesty-tools": "07-herramientas-del-servidor.md", "👟cuentas-nike": "05-early-access-y-cuentas.md",
         "🛠️early-access-checker": "05-early-access-y-cuentas.md", "📒guía-ebay": "02-vender-en-ebay.md",
         "📚guía-vinted": "03-vender-en-vinted.md"}
EDITORIAL = {"🔊-pings", "🔌links", "🧱brick-links", "✅brick-links-autorizados", "🏪instore-info", "🔜leaks", "✅❌cop-or-drop",
             "📯calls-pokemon", "📯calls-invest", "📯calls-mattel", "📯calls-funko", "📯calls-tcg", "📯calls-lego", "📯calls-componentes"}
ACUERDO_CATS = {"Cashbacks", "Monkey-Consign Partner", "Partners y descuentos"}


def responsable(r) -> str:
    c, f = r["categoria"], r["fuente_o_responsable"].lower()
    if r["canal_referencia"] in EDITORIAL or "staff" in f or "editorial" in f:
        return "staff (editorial)"
    if c in ACUERDO_CATS:
        return "acuerdo con tercero (decisión del dueño)"
    if c == "bots checkouts":
        return "webhook del bot de cada miembro (decisión del dueño)"
    if "miembro" in f or c == "🏦Market":
        return "miembros + moderación"
    return "bot"


ALIAS = {"#ugg-oficial": "#ugg"}
REF_CANAL = {"funko": "#funko-es", "mattel": "#mattel-creations", "milfshakes": "#milfshakes"}   # canales de referencia sin equivalente previo   # la web oficial de UGG es la misma fuente que el monitor ugg-es


def lote_probado() -> dict:
    """v1.6: canal propio → tienda de los lotes con alguna señal «probado» (misma fuente que el bot y las tarjetas)."""
    sig = ("restock", "rebaja", "lanzamiento", "raffle")
    return {"#" + t["canal"]: t for t in load_lote(ROOT / "config/lote_tiendas.toml") if any(t.get(k) == "probado" for k in sig)}


def main():
    fid = list(csv.DictReader(open(ROOT / "docs/v11/FIDELIDAD.csv", encoding="utf-8")))
    probadas = lote_probado()
    muestras = {l.split("|")[0] for l in (ROOT / "tests/fixtures/muestras_shopify_REAL_2026-11-21.txt").read_text(encoding="utf-8").splitlines()
                if l and not l.startswith("#")}
    rows = []
    for i, r in enumerate(fid, 1):
        ref = r["canal_referencia"]
        plain = re.sub(r"^[^\w]+", "", ref)
        tech = {"investigado": "investigado", "desarrollado": "construido", "probado en local": "probado localmente"}[r["estado"]]
        ours, fuente, evid, nxt = r["nuestro_canal"], r["fuente_o_responsable"], r["prueba"], ""
        if plain in REF_CANAL and ours in ("", "—"):
            ours = REF_CANAL[plain]
        if plain in FASE2:
            ours, mon, test = FASE2[plain]
            tech, fuente, evid = "probado localmente", f"monitor {mon} (JSON-LD público de la ficha)", test + " · captura 21-nov"
        elif ALIAS.get(ours, ours) in probadas and tech != "probado localmente":
            t = probadas[ALIAS.get(ours, ours)]
            tech, fuente = "probado localmente", f"monitor {', '.join(t['monitores'])}"
            evid = t.get("prueba_restock") or t.get("prueba_rebaja") or "lote de tiendas"
        elif tech == "construido" and (doms := [d for d in re.findall(r"shop:([a-z0-9.-]+)", fuente) if d in muestras]):
            tech, evid = "probado localmente", " + ".join(f"test_tiendas_lote2[{d}]" for d in doms) + " · muestra real /products.json"
        elif plain in PENDIENTE_TIENDA:
            nxt = PENDIENTE_TIENDA[plain]
        if ref in GUIAS:
            tech, evid = "construido", "contenido redactado: docs/v12/guias/" + GUIAS[ref]
            nxt = "revisión del dueño y publicación al instalar"
        if ref in EDITORIAL:
            tech = "construido" if tech == "investigado" else tech
            evid = (evid + " · " if evid else "") + "flujo editorial: docs/v12/EDITORIAL.md"
            nxt = nxt or "nombrar responsable (rol Pinger/Analista)"
        if r["categoria"] == "bots checkouts":
            nxt = "decidir si se activa (docs/v12/BOTS_CHECKOUT.md)"
        if r["categoria"] in ACUERDO_CATS:
            nxt = "acuerdo pendiente (docs/v12/ACUERDOS.md)"
        if r["categoria"] in ("the zesty chefs extension", "(arriba)"):
            nxt = "no se copia; alternativa propia en docs/v12/MARCA_ZESTY.md"
        if not nxt:
            nxt = {"investigado": "construir o decidir", "construido": "probar localmente",
                   "probado localmente": "instalar en Discord (falta token)"}[tech]
        rows.append({"id": f"Z-{i:03d}", "categoria": r["categoria"], "canal_referencia": ref, "id_discord_referencia": r["id_referencia"],
                     "funcion": r["que_hace"], "equivalente_propio": ours, "fuente": fuente, "pais": "ES/EU",
                     "responsable": responsable(r), "estado_tecnico": tech, "estado_discord": "no instalado",
                     "evidencia": evid, "observado_21nov": r.get("observado_21nov", ""), "siguiente_accion": nxt})
    out = ROOT / "docs/v12"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "INVENTARIO_MAESTRO.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    tot = Counter(r["estado_tecnico"] for r in rows)
    disc = Counter(r["estado_discord"] for r in rows)
    resumen = {"total": len(rows), "estado_tecnico": dict(tot), "estado_discord": dict(disc),
               "responsable": dict(Counter(r["responsable"] for r in rows))}
    (out / "INVENTARIO_MAESTRO_resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "INVENTARIO_MAESTRO.html").write_text(render(rows, resumen), encoding="utf-8")
    stores = tiendas()
    print(json.dumps(resumen, ensure_ascii=False))
    print(f"tiendas monitorizadas (fuera del total de referencia): {stores}")


def tiendas() -> int:
    cfg = load_config(ROOT / "config/monitors.toml")
    lote = {m: t for t in load_lote(ROOT / "config/lote_tiendas.toml") for m in t["monitores"]}
    caps = {json.loads(l)["h"] for l in (ROOT / "docs/v12/capturas_tiendas_2026-11-21.jsonl").read_text(encoding="utf-8").splitlines()}
    val = set()
    vp = ROOT / "docs/v11/validacion_shopify_2026-11-21.txt"
    if vp.exists():
        val = {t.split(":")[0] for t in vp.read_text(encoding="utf-8").splitlines()[-1].split()}
    rows = []
    for m in cfg.monitors:
        host = urlparse(m.base_url).netloc
        t = lote.get(m.name)
        if m.type == "shopify":
            det = "producto nuevo · reposición por talla · bajada de precio"
        elif m.type == "bstn":
            det = "raffle (apertura, cambio de plazo, cierre) · lanzamiento · reposición por talla · bajada de precio"
        elif m.type == "jsonld":
            det = "producto nuevo · reposición (por talla si la ficha la da) · bajada de precio"
        else:
            det = "lanzamientos (feed)"
        comprobada = "sí (21-nov)" if host.removeprefix("www.") in val or host in caps or (t and any(t.get(s) == "probado" for s in ("raffle", "restock", "rebaja"))) else "no"
        rows.append({"monitor": m.name, "tienda": m.store, "pais": m.country or "", "tipo_fuente": m.type,
                     "detecta": det, "frecuencia_s": m.interval_seconds, "canal_propio": ("#" + t["canal"]) if t else "",
                     "fuente_comprobada": comprobada, "estado": "probado localmente" if (t or host in caps) else "monitor configurado",
                     "primera_entrega_real": "no (falta token)"})
    with open(ROOT / "docs/v12/TIENDAS_MONITORIZADAS.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return {"monitores": len(rows), "con_canal_propio": sum(1 for r in rows if r["canal_propio"]),
            "fuente_comprobada": sum(1 for r in rows if r["fuente_comprobada"].startswith("sí"))}


def render(rows, res) -> str:
    E = html.escape
    sts = ["investigado", "construido", "probado localmente"]
    cats = sorted({r["categoria"] for r in rows})
    o = ["<!doctype html><html lang=es><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Inventario maestro</title>",
         "<style>body{font-family:system-ui,sans-serif;margin:0;background:#0f1115;color:#e7e9ee}main{max-width:1300px;margin:auto;padding:16px}"
         "table{width:100%;border-collapse:collapse;font-size:13px}td,th{padding:6px;border-bottom:1px solid #262a33;text-align:left;vertical-align:top}"
         "select,input{background:#181b22;color:#e7e9ee;border:1px solid #333;border-radius:8px;padding:6px;margin:4px}.m{color:#9aa3b2;font-size:12px}</style><main>",
         f"<h1>Inventario maestro · {res['total']} canales de la referencia</h1><p>" +
         " · ".join(f"<b>{k}</b>: {res['estado_tecnico'].get(k, 0)}" for k in sts) + " · en Discord: " +
         " · ".join(f"{k}: {v}" for k, v in res["estado_discord"].items()) + "</p>",
         "<select id=fe onchange=f()><option value=''>Todos los estados</option>" + "".join(f"<option>{s}</option>" for s in sts) +
         "</select><select id=fc onchange=f()><option value=''>Todas las categorías</option>" + "".join(f"<option>{E(c)}</option>" for c in cats) +
         "</select><input id=fq placeholder=Buscar oninput=f()>",
         "<table><tr><th>ID</th><th>Referencia</th><th>Equivalente propio</th><th>Responsable</th><th>Estado</th><th>Evidencia</th><th>Siguiente acción</th></tr>"]
    for r in rows:
        o.append(f"<tr data-e='{E(r['estado_tecnico'])}' data-c='{E(r['categoria'])}'><td>{r['id']}</td><td>{E(r['canal_referencia'])}<br><span class=m>{E(r['categoria'])} · {E(r['funcion'][:90])}</span></td>"
                 f"<td>{E(r['equivalente_propio'])}<br><span class=m>{E(r['fuente'][:80])}</span></td><td class=m>{E(r['responsable'])}</td>"
                 f"<td>{E(r['estado_tecnico'])}<br><span class=m>{E(r['estado_discord'])}</span></td><td class=m>{E(r['evidencia'][:120])}</td><td class=m>{E(r['siguiente_accion'])}</td></tr>")
    o.append("</table></main><script>function f(){const e=fe.value,c=fc.value,q=fq.value.toLowerCase();document.querySelectorAll('tr[data-e]').forEach(t=>t.style.display=((!e||t.dataset.e===e)&&(!c||t.dataset.c===c)&&(!q||t.textContent.toLowerCase().includes(q)))?'':'none')}</script></html>")
    return "\n".join(o)


if __name__ == "__main__":
    main()
