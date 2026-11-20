# Cifras de cookgroup (generadas 20/11/2026 12:17, Madrid)

Generado por `python tools/stats.py`. No editar a mano.

## Monitores

| Concepto | Cifra |
|---|---:|
| Monitores en `config/monitors.toml` | 30 |
| Filas en `config/shopify_stores.csv` | 231 (activas: 230) |
| **Monitores activos** (`cookgroup check-config`) | **260** |
| **Fuentes únicas activas** (dominios distintos; incluye 5 webs de chollos) | **260** |

Por tipo: bstn 1 · jsonld 2 · rss 5 · shopify 252

## Inventario (tiendas conocidas, no todas monitorizadas)

422 filas = 412 dominios vistos en el cookgroup de referencia + 10 de investigación propia.

Cobertura: bloqueada 13 · completa 17 · descartada 1 · parcial 243 · pendiente 148

## Cobertura por tipo de aviso (monitores activos)

| Aviso | Completa | Parcial |
|---|---:|---:|
| bajada de precio | 0 | 254 |
| chollo nuevo | 5 | 0 |
| fecha cambiada | 1 | 0 |
| lanzamiento anunciado | 1 | 0 |
| price error | 0 | 252 |
| producto nuevo | 252 | 2 |
| raffle abierto/cierre | 1 | 0 |
| talla nueva | 0 | 252 |
| vuelta a stock | 0 | 254 |
| vuelve talla | 0 | 1 |

*Completa*: el adaptador ve todo lo que publica la fuente. *Parcial*: solo una parte (página 1 + rotación de páginas profundas, fichas vigiladas o listados concretos); un cambio fuera de esa parte puede tardar o no verse.

## Actividad medida

Base de datos: `piloto.db` — **PILOTO LOCAL con Discord SIMULADO** (no son envíos a un Discord real)

| Concepto | Cifra |
|---|---:|
| Fuentes con lectura útil | 1 |
| Eventos detectados | 3 |
| **Envíos confirmados por Discord** (con id de mensaje) | **3** |
| Envíos pendientes en bandeja | 0 |
