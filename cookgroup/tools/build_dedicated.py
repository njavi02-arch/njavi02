"""Equivalentes DEDICADOS (v1.0): un canal propio por cada canal de la referencia que deja seguir por separado una
tienda, región, tema o expansión. Genera config/canales_dedicados.toml (lo lee el instalador) y
docs/v10/EQUIVALENTES.csv (una fila por canal de la referencia: los 339).

Tipos de equivalente:
  tienda    → #<tienda>: lo alimentan los monitores de esa tienda; la misma señal sale también en el agregado y
              al miembro solo se le menciona una vez.
  agregado  → el mismo concepto (muchas tiendas en un canal): #sneakers-eu, #sneakers-mundo, #pokémon-tcg…
  región    → #reino-unido, #pokémon-uk: tiendas de ese país.
  tema      → #ugg, #yeezy, #pokémon-prismatic: cualquier tienda, filtrado por palabras clave.
  foro      → hilos por expansión o set (editorial + avisos).
  editorial → lo publica una persona; se deja plantilla y flujo.
  sin-fuente → el canal se puede crear, pero falta una fuente autorizada o un acuerdo (no supera su prueba).
"""
from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

AGG = {"aio-custom": "sneakers-eu", "aio-custom-2": "sneakers-eu", "aio-eu": "sneakers-eu", "aio-eu-2": "sneakers-eu",
       "shopify-eu": "sneakers-eu", "shopify-eu-unfiltered": "sneakers-eu", "mesh-frontend": "sneakers-eu",
       "mesh-backend": "sneakers-eu", "aio-world": "sneakers-mundo", "shopify-all": "sneakers-mundo",
       "basket-shops": "baloncesto", "skateshops": "skate", "pokemon-aio": "pokémon-tcg", "pokemon-custom-aio": "pokémon-tcg",
       "pokemon-custom-shopify": "pokémon-tcg", "aio-random": "otros-artículos"}
REGION = {"uk": ("reino-unido", "GB"), "pokemon-aio-uk": ("pokémon-uk", "GB")}
TOPIC = {"ugg-all-special": ("ugg", ["ugg"]), "yeezy-especial-monitor": ("yeezy", ["yeezy"]),
         "pokemon-prismatic": ("pokémon-prismatic", ["prismatic", "prismátic", "prismatische"]),
         "timberland": ("timberland", ["timberland"]), "vans": ("vans", ["vans"])}
FORUM = {"📆important-releases": "lanzamientos", "📯calls-pokemon": "pokémon-expansiones", "📯calls-tcg": "tcg-expansiones",
         "📯calls-lego": "lego", "📯calls-invest": "lanzamientos-otros", "📯calls-funko": "funko", "📯calls-mattel": "mattel"}
NO_SOURCE_HINT = {"adidas": "adidas.es/.eu sin API pública de stock (probar JSON-LD de fichas)",
                  "asics": "asics.com: probar JSON-LD", "new-balance": "newbalance.com: probar JSON-LD",
                  "web-naranja": "Zalando: programa de afiliados/partner", "aboutyou": "About You: afiliados",
                  "asos": "ASOS: afiliados", "sports-direct": "sportsdirect: probar JSON-LD", "luisaviaroma": "probar JSON-LD",
                  "game": "GAME España: probar JSON-LD", "carrefour": "Carrefour: probar JSON-LD", "alcampo": "Alcampo: probar JSON-LD",
                  "toysrus": "Toys R Us España: probar JSON-LD", "drim": "Drim: probar JSON-LD", "amazon": "Amazon: programa de afiliados (PA-API)",
                  "footlocker": "Foot Locker: JSON-LD sin tallas", "sivasdescalzo": "SVD: permiso de lectura en Chrome pendiente",
                  "basketballemotion": "listado cargado con JavaScript", "kickz": "probar JSON-LD", "footshop": "probar JSON-LD",
                  "43einhalb": "probar JSON-LD", "skatedeluxe": "probar JSON-LD", "basket4ballers": "probar JSON-LD",
                  "dsml": "DSML: bloqueado", "end": "END: colección launches"}


def keyname(n: str) -> str:
    import unicodedata
    a = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", a.lower()).strip("_")


def slug(n: str) -> str:
    return re.sub(r"[^\wáéíóúñü-]+", "", re.sub(r"^[^\w]+", "", n.lower())).strip("-")


def main():
    from cookgroup.config import load_config
    cfg = load_config(ROOT / "config/monitors.toml")
    by_dom = defaultdict(list)
    for m in cfg.monitors:
        d = urlparse(m.base_url).netloc.lower().removeprefix("www.")
        by_dom[d].append(m)
        by_dom[d.split(".", 1)[-1] if d.count(".") > 1 else d].append(m)
    gb = [m.name for m in cfg.monitors if (m.country or "").upper() == "GB"]
    rows, dedicated = [], defaultdict(list)
    for r in csv.DictReader(open(ROOT / "docs/v08/canales.csv", encoding="utf-8")):
        plain = re.sub(r"^[^\w]+", "", r["canal"])
        doms = r["tiendas"].replace("…", "").split() if r["tiendas"] else []
        feeds = sorted({m.name for d in doms for m in by_dom.get(d.lower(), [])})
        kind, eq, src, gap = None, "", "", ""
        if plain in AGG or r["canal"] in AGG:
            kind, eq = "agregado", AGG.get(plain) or AGG[r["canal"]]
            src = f"monitores de su familia ({len(feeds)} de sus {len(doms)} tiendas coinciden)"
            gap = "" if feeds or eq in ("pokémon-tcg",) else "ninguna de sus tiendas tiene monitor"
        elif plain in REGION:
            kind, (eq, cc) = "región", REGION[plain]
            feeds = gb if cc == "GB" and eq == "reino-unido" else feeds
            src = f"monitores con país {cc}: {len(gb)}"
            gap = "" if gb else "sin monitores del país"
        elif plain in TOPIC:
            kind, (eq, kws) = "tema", TOPIC[plain]
            src = "cualquier monitor, palabras clave: " + ", ".join(kws)
        elif r["canal"] in FORUM:
            kind, eq = "foro", FORUM[r["canal"]]
            src = "staff (hilo por artículo) + avisos automáticos en el hilo"
            gap = "" if eq == "lanzamientos" else "responsable editorial"
        elif r["categoria"] in ("🤖Monitores", "Shopify monitors", "Demandware monitors", "Shopify clothes") and int(r["n_tiendas"] or 0) <= 5 \
                and plain not in ("info", "socials-monitors"):
            kind, eq = "tienda", slug(plain).removesuffix("-custom")
            eq = "ugg-oficial" if eq == "ugg" else eq
            src = ", ".join(feeds) if feeds else ""
            if not feeds:
                gap = next((v for k, v in NO_SOURCE_HINT.items() if k in plain), "sin monitor para sus tiendas") + " → sin fuente aún"
        elif r["categoria"] == "Pokemon" and plain in ("game", "game-instore", "carrefour", "carrefour-instore", "drim", "toysrus",
                                                     "alcampo", "pokemon-amazon", "darizard", "twitter-pokemon"):
            kind, eq = "tienda", slug(plain)
            gap = next((v for k, v in NO_SOURCE_HINT.items() if k in plain), "fuente por localizar") + " → sin fuente aún"
            if "instore" in plain:
                gap = "disponibilidad en tienda física: sin fuente autorizada"
        if kind in ("tienda", "región", "tema", "foro") and eq not in ("lanzamientos",):
            cat = {"tienda": "🏪 TIENDAS" if r["categoria"] != "Pokemon" else "🃏 POKÉMON Y TCG", "región": "🌍 REGIONES",
                   "tema": "🏷️ TEMAS", "foro": "🃏 POKÉMON Y TCG" if "pok" in eq or "tcg" in eq else "🧩 OTRAS FAMILIAS"}[kind]
            prev = next((c for c in dedicated[cat] if c["nombre"] == eq), None)
            if prev is not None:
                prev["equivalente_de"] += f", {r['canal']}"
                prev["monitores"] = sorted(set(prev["monitores"]) | set(feeds))
            else:
                dedicated[cat].append({"nombre": eq, "clase": kind, "pais": REGION.get(plain, ("", ""))[1], "tipo": "foro" if kind == "foro" else "texto", "acceso": "lectura",
                                       "fuente": f"bot:{('tienda_' if kind == 'tienda' else '') + keyname(eq)}",
                                       "estado": "construido" if not gap else "pendiente", "equivalente_de": r["canal"],
                                       "monitores": feeds, "palabras": TOPIC.get(plain, ("", []))[1], "falta": gap})
        rows.append({**{k: r[k] for k in ("categoria", "canal", "tipo", "para_que", "quien_alimenta")},
                     "tipo_equivalente": kind or "ver tabla v0.9", "equivalente_dedicado": f"#{eq}" if eq else r["equivalente"],
                     "fuente_o_responsable": src, "hueco": gap, "tiendas_ref": r["n_tiendas"]})
    # v1.3: nombres claros en lugar de la jerga de la referencia («web naranja» = Zalando)
    RENAME = {"web-naranja-españa": "zalando-es", "web-naranja-eu": "zalando-eu"}
    for chans in dedicated.values():
        for c in chans:
            if c["nombre"] in RENAME:
                c["nombre"] = RENAME[c["nombre"]]
                c["fuente"] = "bot:tienda_" + keyname(c["nombre"])
    # v1.1: tiendas del lote (config/lote_tiendas.toml) que aún no tienen canal propio
    from cookgroup.store_directory import load_lote
    lote = load_lote(ROOT / "config/lote_tiendas.toml")
    have = {c["nombre"] for chans in dedicated.values() for c in chans}
    by_mon = {m: c["nombre"] for chans in dedicated.values() for c in chans if c["clase"] == "tienda" for m in c["monitores"]}
    for t in lote:
        sig = ", ".join(k.upper() for k in ("raffle", "lanzamiento", "restock", "rebaja") if t.get(k) == "probado")
        same = next((by_mon[m] for m in t["monitores"] if m in by_mon), None)
        if t["canal"] not in have and same:          # la tienda ya tiene canal (equivalente de la referencia): se reutiliza
            t["canal"] = same
        if t["canal"] in have:
            c = next(c for chans in dedicated.values() for c in chans if c["nombre"] == t["canal"])
            c["monitores"] = sorted(set(c["monitores"]) | set(t["monitores"]))
            c["pais"], c["senales"] = t["pais"], sig
            continue
        have.add(t["canal"])
        dedicated["🏪 TIENDAS"].append({"nombre": t["canal"], "clase": "tienda", "pais": t["pais"], "tipo": "texto", "acceso": "lectura",
                                       "fuente": f"bot:tienda_{keyname(t['canal'])}", "estado": "construido",
                                       "equivalente_de": "(lote 1 propio)", "monitores": t["monitores"], "palabras": [],
                                       "falta": "", "senales": sig})
    # TOML para el instalador (categorías extra, máximo 50 canales por categoría)
    out = ["# GENERADO por tools/build_dedicated.py — canales dedicados (tiendas, regiones, temas, foros). No editar a mano.", ""]
    for cat, chans in dedicated.items():
        for i in range(0, len(chans), 50):
            out += ["[[categoria]]", f'nombre = "{cat}{"" if i == 0 else f" ({i // 50 + 1})"}"', 'audiencia = "suscriptores"']
            for c in chans[i:i + 50]:
                out += ["[[categoria.canal]]"] + [f'{k} = "{v}"' for k, v in c.items() if isinstance(v, str)]
                out += [f"monitores = {list(c['monitores'])!r}".replace("'", '"'), f"palabras = {list(c['palabras'])!r}".replace("'", '"')]
            out.append("")
    (ROOT / "config/canales_dedicados.toml").write_text("\n".join(out), encoding="utf-8")
    (ROOT / "docs/v10").mkdir(parents=True, exist_ok=True)
    with open(ROOT / "docs/v10/EQUIVALENTES.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    n = sum(len(c) for c in dedicated.values())
    print(f"{len(rows)} filas; {n} canales dedicados ({sum(1 for c in dedicated.values() for x in c if not x['falta'])} con fuente)")
    for cat, chans in dedicated.items():
        print(cat, len(chans), [c["nombre"] for c in chans][:60])


if __name__ == "__main__":
    main()
