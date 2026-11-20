"""Tabla canal a canal: referencia observada (20-nov) × v0.7/v0.8 × mi servidor.

Entrada: docs/v08/reference_sidebar_2026-11-20.txt, docs/reference_channels.tsv, docs/inventory.csv,
         config/servidor.toml, config/monitors.toml (+ CSV de tiendas).
Salida:  docs/v08/canales.csv (buscable en el panel, pestaña «Mi Discord»).
"""
from __future__ import annotations

import csv
import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# (categoría regex, nombre regex) → (para qué lo usa el miembro, qué publica, quién lo alimenta, equivalente, qué falta, cómo se prueba)
RULES = [
    (r"^\(arriba\)$", r".", ("Contador público de miembros", "—", "Discord", "—", "no aplica", "—")),
    (r"IMPORTANT", r"sugerencias", ("Proponer mejoras", "Sugerencias", "miembros", "#sugerencias (foro)", "", "Abrir un hilo")),
    (r"EMPEZAR", r"bienvenido", ("Primer contacto", "Bienvenida y pasos", "staff", "#bienvenida", "textos propios (hecho) e instalar", "Abrirlo como miembro nuevo")),
    (r"EMPEZAR", r"roles", ("Elegir qué pings recibe", "Mensajes de roles por reacción (tipos, marcas, región)", "staff + bot de roles", "#elige-tus-avisos (preguntas de bienvenida)", "token de bot para instalar; añade TALLAS", "tools/lote1.py paso 0")),
    (r"EMPEZAR", r"auto-pinger|notificaciones|comandos", ("Configurar avisos personales", "Guía del autopinger por MD (palabras, negativas, precio, excluir canal, pausa, destino)", "staff + bot propio", "perfil del miembro (config/miembros.toml)", "comandos por MD necesitan bot en marcha; hoy perfil por roles + fichero", "tools/lote1.py pasos 5–8")),
    (r"EMPEZAR", r"guías|vídeo|checklist|posts|zestyapp", ("Aprender a usar el servidor", "Guías y vídeos", "staff", "#guía-de-avisos", "contenido editorial propio", "Revisión por el staff")),
    (r"Recompensas", r".", ("Normas y sanciones", "Reglas, faltas, recompensas", "staff", "#normas", "flujo de moderación humano", "Revisión por el staff")),
    (r"extension", r".", ("Extensión de navegador de la referencia", "Novedades y chat de su extensión", "proveedor de la referencia", "—", "no aplica (producto ajeno)", "—")),
    (r"IMPORTANT", r"pings", ("Recibir menciones de oportunidades", "Pings manuales y automáticos", "staff + bot", "menciones personalizadas en cada canal", "token para perfiles reales", "tools/lote1.py paso 2")),
    (r"IMPORTANT", r"anuncios|importante|updates", ("Enterarse de novedades", "Anuncios del servidor", "staff", "#anuncios", "", "Publicación del staff")),
    (r"IMPORTANT", r"releases|weekly|monthly", ("Ver qué sale", "Calendario semanal/mensual", "staff", "#próximos-7-días", "lote 2 (foro de lanzamientos)", "Siguiente lote")),
    (r"IMPORTANT", r"links|brick", ("Enlaces directos de compra", "Enlaces de tiendas autorizadas", "staff", "enlaces oficiales en el hilo del lanzamiento", "lote 2", "Siguiente lote")),
    (r"IMPORTANT", r"steals|risky", ("Oportunidades señaladas por el staff", "Calls del staff", "staff", "#reventa (solo verificadas)", "criterio humano + ventas cerradas", "tests/test_v07 (beneficio verificado)")),
    (r"IMPORTANT", r"instore", ("Saber qué hay en tienda física", "Info de lanzamientos en tienda", "staff", "#madrid-tiendas", "fuente autorizada por tienda (ampliación)", "Pendiente de fuente")),
    (r"IMPORTANT", r"success", ("Compartir resultados", "Capturas de compras/ventas de miembros", "miembros", "#resultados", "moderación humana", "Revisión por el staff")),
    (r"IMPORTANT", r"sugerencias", ("Proponer mejoras", "Sugerencias", "miembros", "#sugerencias (foro)", "", "Abrir un hilo")),
    (r"IMPORTANT", r"giveaways|groupbuys", ("Sorteos internos y compras en grupo", "Sorteos/compras conjuntas", "staff", "—", "decisión del staff (no se construye)", "—")),
    (r"IMPORTANT", r"leaks", ("Rumores de lanzamientos", "Filtraciones", "staff", "hilo de lanzamiento en estado «pendiente»", "fuente oficial obligatoria para avisar", "tests (releases pendientes)")),
    (r"IMPORTANT", r"tickets", ("Pedir ayuda privada", "Apertura de tickets", "staff", "#tickets", "moderación humana", "Abrir un ticket")),
    (r"Releases", r"important", ("Seguir un lanzamiento importante", "Foro: un hilo por lanzamiento con fecha, mercado, tiendas y keywords", "staff", "#lanzamientos (foro)", "lote 2", "Siguiente lote")),
    (r"Releases", r"cop-or-drop", ("Votar si merece la pena", "Encuestas cop/drop", "staff + miembros", "veredicto en el hilo del lanzamiento", "lote 2", "Siguiente lote")),
    (r"Releases", r".", ("Calendario por marca", "Lanzamientos de la marca", "staff", "#lanzamientos (etiqueta por marca)", "lote 2", "Siguiente lote")),
    (r"Stocks", r".", ("Ver cuánto stock hubo", "Cargas de stock por lanzamiento", "bot de la referencia", "—", "sin fuente autorizada de stock total", "—")),
    (r"^🤖Monitores|^Shopify monitors|^Demandware", r"aio|unfiltered|shopify-eu|shopify-all|mesh|uk$", ("Ver avisos de muchas tiendas juntas", "Agregado de restocks/novedades", "bot (monitores)", "#sneakers-eu / #sneakers-mundo", "", "piloto v0.7 + tools/lote1.py paso 4 (sin doble mención)")),
    (r"Shopify clothes", r".", ("Ropa de marcas hype", "Restocks de ropa", "bot (monitores)", "#streetwear", "", "COMPROBAR.bat buscar <tienda>")),
    (r"Nike monitors", r".", ("Nike/SNKRS", "Lanzamientos y restocks de Nike", "bot de la referencia", "—", "Nike SNKRS: sin fuente autorizada", "—")),
    (r"instore monitors", r".", ("Stock en tiendas físicas", "Disponibilidad por tienda física", "bot de la referencia", "#madrid-tiendas", "fuente autorizada (Nike/JD/adidas no la ofrecen)", "Pendiente")),
    (r"^🤖Monitores|^Shopify monitors|^Demandware", r".", ("Avisos de una tienda concreta", "Restocks/novedades de esa tienda", "bot (monitores)", "#sneakers-eu (+ menciones por talla)", "", "COMPROBAR.bat buscar <tienda>")),
    (r"rebajas", r"30|60|rebajas", ("Encontrar descuentos fuertes", "Bajadas de precio por tramo", "bot (monitores)", "#rebajas-30 / #rebajas-60", "lote 5", "tests (rutas de descuento)")),
    (r"rebajas", r"chollometro|dealabs|mydealz|pepper|hotukdeals", ("Chollos de comunidad", "Chollos calientes", "bot (feeds)", "#chollos", "", "piloto v0.7 (Chollometro real)")),
    (r"rebajas", r"privalia|zalando|miravia|amazon|lidl|pccomponentes|jd|asos", ("Descuentos de grandes tiendas", "Campañas y productos rebajados", "bot de la referencia", "#rebajas-30", "acceso comercial (afiliados/API)", "Bloqueado")),
    (r"Amazon", r".", ("Rebajas de Amazon por tramo", "Ofertas de Amazon", "bot de la referencia", "—", "programa de afiliados de Amazon", "Bloqueado")),
    (r"bots checkouts", r".", ("Monitores de bots de compra", "Avisos de herramientas de terceros", "proveedores de bots", "—", "no aplica (automatización de compra)", "—")),
    (r"General", r"ayuda", ("Resolver dudas", "Chat de ayuda", "miembros + staff", "#ayuda (foro)", "", "Abrir un hilo")),
    (r"General", r".", ("Hablar con la comunidad", "Conversación", "miembros", "#chat", "moderación humana", "—")),
    (r"Privados", r".", ("Canal privado del miembro", "—", "—", "—", "no se recorre", "—")),
    (r"Outlets", r".", ("Comprar en outlets y revender", "Guías, avisos, rangos de compraventa", "staff + scraper", "#outlet", "rangos de precio: requieren ventas cerradas", "Siguiente lote")),
    (r"Pokemon", r"aio|custom|amazon|prismatic|game|carrefour|drim|toysrus|alcampo|darizard|twitter|esa", ("Avisos de Pokémon/TCG", "Restocks de tiendas TCG", "bot", "#pokémon-tcg", "tiendas físicas: sin fuente", "COMPROBAR.bat buscar pokemon")),
    (r"Pokemon", r".", ("Comunidad Pokémon", "Calls, guías, compraventa", "staff + miembros", "#pokémon-tcg", "contenido editorial", "—")),
    (r"Random invest", r"lego", ("LEGO", "Calls de LEGO", "staff", "#lego", "ampliación: fuente autorizada", "Siguiente lote")),
    (r"Random invest", r"componentes|ram|playstation|finalmouse", ("Electrónica", "Calls y monitores de componentes", "staff + bot", "#electrónica", "ampliación", "Siguiente lote")),
    (r"Random invest", r".", ("Inversión variada", "Calls y monitores de otras categorías", "staff + bot", "—", "fuera del alcance actual", "—")),
    (r"Raffles", r".", ("Apuntarse a sorteos", "Fichas de raffles", "bot", "#raffles", "lote 3", "Siguiente lote")),
    (r"Cashbacks|Herramientas|Monkey|Partners", r".", ("Herramientas y acuerdos", "Guías y partners", "staff/partners", "—", "no se construye", "—")),
    (r"Market", r".", ("Comprar y vender entre miembros", "WTB/WTS, feedback, legit-check", "miembros", "—", "moderación humana (no se construye en v0.8)", "—")),
    (r"Old-releases", r".", ("Archivo de lanzamientos", "Hilos antiguos", "staff", "hilos cerrados del foro #lanzamientos", "lote 2", "—")),
    (r".", r".", ("—", "—", "—", "—", "pendiente de clasificar", "—")),
]


# Comprobado abriendo el canal (20-nov, solo lectura). Resumen propio, sin datos de miembros.
CHECKED = {
    "📆important-releases": "foro: 12 hilos (dic-2025→nov-2026), uno por lanzamiento, con veredicto, fecha, mercado, tiendas y keywords",
    "📯calls-pokemon": "foro: 12 hilos, uno por expansión de Pokémon TCG con veredicto 🟢🟠🔴",
    "📲-invitaciones-pokemon": "foro: 0 hilos visibles para esta cuenta (pendiente de verificar)",
    "📚guías-pokemon": "foro: 7 guías (introducción, dónde comprar/vender, tipos de producto, envío por Cardmarket, mercado)",
    "📯calls-invest": "foro: 30 hilos de lanzamientos variados (consolas, Finalmouse, colaboraciones Pokémon…)",
    "📯calls-mattel": "foro: 6 hilos (Hot Wheels por serie, Monster High, diecast, instore)",
    "📯calls-funko": "foro: 43 hilos, uno por Funko Pop con fecha y veredicto",
    "📯calls-tcg": "foro: 24 hilos (One Piece, Magic, Lorcana, Dragon Ball, Riftbound…)",
    "📯calls-lego": "foro: 6 hilos, uno por set con su número (#75192, #10335…)",
    "🌎roles": "4 mensajes de roles por reacción: tipos de aviso, marcas, otros, comunidad autónoma; sin tallas",
    "🤖auto-pinger": "bot por MD: palabras, negativas, precio máximo, excluir canal, pausa, destino, CSV",
    "raffles-europe": "fichas automáticas; última del 1-jul-2026 (inactivo)",
    "aio-eu": "avisos de restock con tallas, precio y enlaces de mercado",
    "📤wts": "market: miembros publican ventas con talla y precio (tema del canal: precio obligatorio); activo",
    "✅legit-check": "market: miembros suben fotos para que otros validen autenticidad; activo",
    "🚫black-list-scammers": "market: avisos de estafadores; moderado por el staff",
    "adonis-monitor": "bot de compra de terceros: publica checkouts (tienda, modo, pago, precio, talla, hora)",
    "🤝aycd-partnership": "partner de 2022: herramientas para generar cuentas y correos en masa",
}
DEPENDS = [(r"Market", "moderación humana + normas de compraventa + responsabilidad legal sobre transacciones entre miembros"),
           (r"bots checkouts", "proveedor de bot de compra (licencia de pago) y su webhook de éxitos"),
           (r"Partners", "acuerdo comercial con el proveedor (afiliación/descuento)"),
           (r"Amazon|privalia|zalando|miravia", "fuente comercial: programa de afiliados/API"),
           (r"Nike monitors|instore", "fuente autorizada inexistente hoy (SNKRS/tiendas físicas)"),
           (r"Cashbacks", "acuerdos de afiliación con plataformas de cashback"),
           (r"Monkey", "partner de consigna (acuerdo comercial)")]


def parse_sidebar(path: Path):
    cat, out = None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# ") or not line.strip():
            continue
        if line.startswith("## "):
            cat = line[3:]
            continue
        for item in line.split(";"):
            name, tf, cid = item.rsplit("|", 2)
            out.append({"categoria": cat, "canal": name, "tipo": {"t": "texto", "f": "foro", "v": "voz"}.get(tf[0], tf[0]),
                        "miembro_escribe": "sí" if tf[1] == "o" else "no", "id": cid})
    return out


def main():
    rows = parse_sidebar(ROOT / "docs/v08/reference_sidebar_2026-11-20.txt")
    sampled = {r["channel"]: r for r in csv.DictReader(open(ROOT / "docs/reference_channels.tsv", encoding="utf-8"), delimiter="\t")}
    stores_by = defaultdict(list)
    for r in csv.DictReader(open(ROOT / "docs/inventory.csv", encoding="utf-8")):
        for ch in (r["canales_referencia"] or "").split(","):
            if ch.strip():
                stores_by[ch.strip()].append(r["dominio"])
    design = tomllib.loads((ROOT / "config/servidor.toml").read_text(encoding="utf-8"))
    mine = {c["nombre"]: (cat["nombre"], c) for cat in design["categoria"] for c in cat["canal"]}
    from cookgroup.config import load_config
    cfg = load_config(ROOT / "config/monitors.toml")
    feeding = defaultdict(int)
    for m in cfg.monitors:
        feeding[m.channel] += 1
    out = []
    for r in rows:
        plain = re.sub(r"^[^\w]+", "", r["canal"]).strip()
        key = next(k for k in sampled if k == plain) if plain in sampled else None
        for cre, nre, info in RULES:
            if re.search(cre, r["categoria"] or "", re.I) and re.search(nre, plain, re.I):
                break
        para, publica, quien, equiv, falta, prueba = info
        eq_names = re.findall(r"#([\w\-áéíóúñ]+)", equiv)
        exists = [n for n in eq_names if n in mine]
        bot = [mine[n][1]["fuente"].split(":", 1)[1] for n in exists if mine[n][1]["fuente"].startswith("bot:")]
        recibe = "sí (" + ", ".join(f"{feeding[b]} monitores" for b in bot if feeding.get(b)) + ")" if any(feeding.get(b) for b in bot) else "no"
        st = sorted(set(stores_by.get(plain, [])))
        estado_eq = [mine[n][1]["estado"] for n in exists]
        if r["canal"] in CHECKED or plain in CHECKED:
            nivel = "función comprobada"
        elif key:
            nivel = "función comprobada (muestreo v0.6)"
        else:
            nivel = "visto en la barra lateral"
        if "construido" in estado_eq:
            nivel += " · equivalente implementado y probado localmente"
        dep = next((d for rx, d in DEPENDS if re.search(rx, (r["categoria"] or "") + " " + plain, re.I)), "")
        out.append({**r, "canal": r["canal"], "para_que": para, "que_publica": publica, "quien_alimenta": quien,
                    "equivalente": equiv, "que_falta": falta, "como_se_prueba": prueba,
                    "documentado": "sí (muestreado v0.6)" if key else "sí (recorrido 20-nov)",
                    "mensajes_muestreados": sampled[key]["messages_sampled"] if key else "",
                    "existe_en_mi_servidor": "no (instalador listo)" if exists else "no aplica" if equiv in ("—", "") else "función, sin canal propio",
                    "recibe_datos": recibe, "entrega_confirmada": "no (sin webhook)",
                    "nivel_evidencia": nivel, "comprobado_20nov": CHECKED.get(r["canal"], CHECKED.get(plain, "")),
                    "dependencia": dep, "tiendas": " ".join(st[:40]) + (f" … (+{len(st) - 40})" if len(st) > 40 else ""), "n_tiendas": len(st)})
    cols = list(out[0].keys())
    with open(ROOT / "docs/v08/canales.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    print(len(out), Counter(r["existe_en_mi_servidor"] for r in out), Counter(r["recibe_datos"] != "no" for r in out),
          sum(1 for r in out if r["que_falta"] == "pendiente de clasificar"))


if __name__ == "__main__":
    main()
