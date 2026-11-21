"""Los 112 canales de la referencia sin equivalente (v0.8 «no aplica»): ninguno se da por resuelto.
Para cada uno: equivalente propuesto, qué se puede construir YA, qué falta para activarlo y qué decisión es tuya.
→ docs/v10/HUECOS.csv (se conservan dentro del total de 339).
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# categoría (o canal) → (equivalente propuesto, construible ya, falta para activar, decisión del dueño)
R = [
    (r"^\(arriba\)$", ("contador de miembros (canal de voz bloqueado con el nombre «Miembros: N»)", "sí: lo actualiza el bot cada hora",
                       "token del bot", "ninguna")),
    (r"extension", ("ninguno (es la extensión de navegador de la referencia)", "no", "producto propio de navegador",
                    "decidir si algún día ofreces una extensión propia")),
    (r"^Stocks$", ("#stock-lanzamientos: cuántas unidades se esperan (editorial)", "sí: canal editorial con plantilla",
                   "fuente: la referencia lo publica a mano; sin dato oficial", "quién lo redacta y con qué fuente")),
    (r"Nike monitors", ("#nike-snkrs (lanzamientos de Nike en el foro + calendario oficial)", "parcial: hilos del foro desde tiendas que venden Nike",
                        "Nike no ofrece una fuente autorizada de stock/SNKRS", "aceptar que Nike se cubra vía tiendas y calendario")),
    (r"bots checkouts", ("#exitos-bots: solo si un proveedor de bots te da su webhook de éxitos", "sí: canal y enrutado",
                         "acuerdo con el proveedor + licencias; uso de bots puede infringir condiciones de tiendas", "decidir si quieres ese tipo de cliente")),
    (r"Partners", ("#partners: descuentos de herramientas legítimas", "sí: canal editorial", "acuerdos comerciales firmados",
                   "con quién te asocias (evitar generadores de cuentas)")),
    (r"Herramientas", ("#guías-reventa: neobancos, inventario en hoja de cálculo, guías eBay/Vinted", "sí: plantillas y guías propias",
                       "redactar el contenido", "quién escribe y revisa")),
    (r"Cashbacks", ("#cashback: guía y enlaces de afiliado", "sí: canal editorial", "alta en programas de afiliados", "aceptar comisiones de afiliación")),
    (r"Monkey", ("#consigna: vender a través de un partner", "sí: canal y flujo", "acuerdo con un partner de consigna", "si te interesa ese acuerdo")),
    (r"Market", ("categoría MARKET: #vendo-compro, #legit-check, #valoraciones, #lista-negra", "sí: canales, normas, plantilla de anuncio y flujo de moderación",
                 "moderador diario + normas + revisión legal", "abrir o no el market y con qué normas")),
    (r"Random invest", ("#otros-artículos + foros por familia (Funko, Mattel, consolas…)", "sí: canales y foros; monitores Shopify/JSON-LD por tienda",
                        "fuentes por tienda (Amazon/AliExpress requieren afiliación)", "qué familias entran en el plan")),
    (r"IMPORTANT", ("#sorteos-internos y #compras-conjuntas (gestionados por el staff)", "sí: canales y plantillas", "responsable humano",
                    "si haces sorteos/compras conjuntas (bases legales)")),
    (r"Privados", ("canal privado por miembro = ticket privado de #soporte", "sí (hecho)", "—", "ninguna")),
]


def main():
    rows = []
    for r in csv.DictReader(open(ROOT / "docs/v08/canales.csv", encoding="utf-8")):
        if r["existe_en_mi_servidor"] != "no aplica":
            continue
        eq, ya, falta, dec = next(v for rx, v in R if re.search(rx, r["categoria"], re.I))
        rows.append({"categoria": r["categoria"], "canal": r["canal"], "para_que": r["para_que"], "equivalente_propuesto": eq,
                     "construible_ya": ya, "falta_para_activar": falta, "decision_del_dueño": dec})
    out = ROOT / "docs/v10/HUECOS.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows))


if __name__ == "__main__":
    main()
