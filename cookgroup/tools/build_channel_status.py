"""Ficha de cierre de cada canal de MI servidor (v0.9) → docs/v09/CANALES_MI_SERVIDOR.csv

Un canal solo cuenta como «probado localmente» si tiene ejemplo, prueba positiva y caso de silencio con evidencia.
«Operativo en mi servidor» exige que esté instalado en Discord, y «entrega real confirmada», un mensaje comprobado
(docs/v09/ENTREGAS_REALES.csv). Un canal creado pero vacío queda pendiente.
"""
from __future__ import annotations

import csv
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cookgroup.access import matrix  # noqa: E402

# canal → (responsable editorial / fuente, ejemplo, prueba positiva, caso de silencio)
EV = {
    "bienvenida": ("Javier (texto propio)", "docs/v08/TEXTOS_SERVIDOR.md", "visible para visitantes (tests/test_access)", "nadie escribe salvo el equipo (matriz)"),
    "normas": ("Javier (texto propio)", "docs/v08/TEXTOS_SERVIDOR.md", "visible para visitantes (tests/test_access)", "nadie escribe salvo el equipo (matriz)"),
    "elige-tus-avisos": ("Javier + preguntas de bienvenida", "roles de talla/marca/región", "lote1 paso 0: roles → perfil", "preferencias sin suscripción no mencionan (tests/test_access)"),
    "guía-de-avisos": ("Javier (texto propio)", "docs/v08/TEXTOS_SERVIDOR.md", "visible para visitantes", "nadie escribe salvo el equipo"),
    "anuncios": ("Javier", "", "", ""),
    "planes": ("Javier + web local", "página de venta (/)", "membresías paso 1", "visitante no ve canales de pago (paso 2)"),
    "muestra-gratis": ("bot (avisos ya entregados)", "aviso con pie «MUESTRA con 60 min de retraso»", "tests/test_lote2: retraso y sin menciones", "4.º aviso del día: no se publica"),
    "soporte": ("Staff/Moderador (humano)", "hilo privado de ticket", "tests/test_access: cliente y equipo lo ven", "otro cliente no ve el ticket"),
    "lanzamientos": ("bot (BSTN, tiendas Shopify launches) + staff", "hilo con SKU, fecha Madrid, retail, tiendas", "lote2 pasos 1, 3, 4", "lote2 paso 2: releer sin cambios = silencio"),
    "próximos-7-días": ("bot", "resumen con enlaces a hilos", "lote2 paso 5", "sin lanzamientos en 7 días: no publica"),
    "raffles": ("bot (BSTN) + staff", "ficha completa de raffle", "lote2 pasos 6, 8, 9, 11", "lote2 pasos 7, 10, 12"),
    "restocks": ("bot (monitores)", "«VUELVE LA EU 44»", "lote2 paso 13 + lote1 paso 2", "lote2 paso 14 y lote1 paso 3 (otra talla)"),
    "sneakers-eu": ("bot (132 tiendas)", "aviso Footdistrict real con mención", "piloto v0.7 + lote1 paso 2", "lote1 pasos 3–8"),
    "sneakers-mundo": ("bot (7 tiendas)", "Undefeated real: vuelve la talla M", "tests/test_familias::sneakers_mundo", "sin cambios = silencio; talla de zapatilla no aplica a ropa"),
    "baloncesto": ("bot", "Baskèts real: vuelve la «44 1/2»", "tests/test_familias::baloncesto", "el miembro de la 43 no recibe mención"),
    "skate": ("bot", "Flatspot real: vuelve la UK 9,5", "tests/test_familias::skate", "miembro solo con talla EU: no se le menciona (tienda en UK)"),
    "rebajas-30": ("bot (rutas de descuento)", "bajada 280→224 con origen de precios", "lote2 paso 15", "una sola mención aunque salga en dos canales (lote1 paso 4)"),
    "rebajas-60": ("bot (rutas de descuento)", "igual que rebajas-30", "tests de rutas de descuento", "una sola mención (lote1 paso 4)"),
    "chollos": ("bot (feeds Pepper)", "chollo real de Chollometro", "piloto v0.7 (lectura real)", "feed sin novedades = silencio (diagnóstico)"),
    "outlet": ("bot", "ASOS Sample Sale real: talla de ropa XXL", "tests/test_familias::outlet", "«EU 44» de ropa no menciona a quien eligió EU 44 de zapatilla"),
    "streetwear": ("bot (32 tiendas)", "Goodhood real en GBP", "tests/test_familias::streetwear", "nunca presenta libras como euros"),
    "pokémon-tcg": ("bot (65 tiendas)", "Red Goblin real: Ditto vuelve a stock (RON)", "tests/test_familias::pokemon", "el miembro solo de sneakers no recibe mención; sin talla inventada"),
    "Miembros": ("bot (contador)", "«Miembros: N»", "tests/test_membresias::counter + test_access (voz)", "nadie puede entrar ni hablar"),
    "charla": ("comunidad (Moderador modera)", "canal de voz", "tests/test_access::voice: suscriptor entra y habla", "visitante y ex-suscriptor no lo ven"),
    "alertas-personales": ("bot (perfil de cada miembro)", "mención solo a quien encaja", "tests/test_e2e_runner + lote1", "una mención por señal; ex-suscriptor no recibe"),
    "lego": ("pendiente de fuente autorizada", "", "", ""),
    "electrónica": ("pendiente de fuente autorizada", "", "", ""),
    "madrid-tiendas": ("pendiente de fuente autorizada", "", "", ""),
    "reventa": ("bot + ventas cerradas (config/market_data.json)", "beneficio verificado por talla (simulación)", "tests/test_v07 talla comprable", "ventas de otra talla → «sin verificar»"),
    "chat": ("Moderador", "", "", ""),
    "ayuda": ("Staff", "", "", ""),
    "sugerencias": ("Staff", "", "", ""),
    "resultados": ("Moderador", "", "", ""),
    "pruebas-bot": ("Javier", "mensaje de PRUEBA", "tests/test_real_delivery", "otro canal/servidor: no envía"),
    "registro-bot": ("bot", "", "", ""),
    "moderación": ("Staff", "", "", ""),
}
SAME_ENGINE: set = set()


def main():
    from cookgroup.server_setup import load_design
    design = load_design(ROOT / "config/servidor.toml")
    perms = {r["canal"]: r for r in matrix(design)}
    real = set()
    p = ROOT / "docs/v09/ENTREGAS_REALES.csv"
    if p.exists():
        real = {r["canal"] for r in csv.DictReader(open(p, encoding="utf-8")) if r["estado"] == "entrega real confirmada"}
    rows = []
    for cat in design["categoria"]:
        for ch in cat["canal"]:
            n = ch["nombre"]
            if ch.get("instalar") is False:
                continue                      # MARKET: pendiente de tu decisión (no cuenta en el total instalable)
            who, ex, pos, sil = EV.get(n, ("", "", "", ""))
            if ch.get("clase") in ("tienda", "región", "tema") and ch.get("estado") == "construido":
                who = ", ".join(ch.get("monitores", [])) or ("palabras: " + ", ".join(ch.get("palabras", [])) if ch.get("palabras") else f"país {ch.get('pais')}")
                ex, pos, sil = ("mismo aviso que el agregado, en el canal propio", "tests/test_dedicated (enrutado)",
                                "otra tienda/país/tema no entra; mención única (tests/test_e2e_runner)")
            elif ch.get("clase"):
                who = who or ch.get("falta", "")
            if n in real:
                st = "entrega real confirmada"
            elif ch.get("clase") in ("tienda", "región", "tema") and ch.get("estado") == "construido":
                st = "enrutado probado (lectura de la fuente en tu PC)" if n != "footdistrict" else "probado localmente"
            elif ch.get("clase") and ch.get("estado") != "construido":
                st = "pendiente: " + (ch.get("falta") or "fuente")
            elif pos and sil and ex and n not in SAME_ENGINE and ch["estado"] == "construido":
                st = "probado localmente"
            elif n in SAME_ENGINE:
                st = "implementado (mismo motor; falta prueba propia)"
            elif ch["estado"] == "moderacion-humana" or "Moderador" in who or who.startswith("Staff"):
                st = "pendiente: necesita responsable humano"
            else:
                st = "pendiente"
            if n == "reventa":
                st = "pendiente: vacío hasta cargar ventas cerradas"
            pm = perms[n]
            rows.append({"categoria": cat["nombre"], "canal": n, "finalidad": ch.get("finalidad") or f"Seguir por separado lo que en la referencia es {ch.get('equivalente_de', '')}", "fuente_o_responsable": who or ch["fuente"],
                         "regla": ch.get("regla") or "Misma señal que el agregado; mención única por miembro", "visitante": pm["visitante"], "suscriptor": pm["suscriptor"], "ex_suscriptor": pm["ex-suscriptor"],
                         "moderador": pm["moderador"], "ejemplo": ex, "prueba_positiva": pos, "caso_silencio": sil,
                         "estado": st, "instalado_en_mi_discord": "no (falta token del bot)",
                         "equivalente_de": ch.get("equivalente_de", "")})
    out = ROOT / "docs/v09/CANALES_MI_SERVIDOR.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(len(rows), Counter(r["estado"] for r in rows))


if __name__ == "__main__":
    main()
