# Inventario de tiendas y fuentes

> **Inventario completo y filtrable (20-nov-2026):** `docs/inventory.html` (abrir en el navegador) y `docs/inventory.csv`.
> Lo genera `tools/build_inventory.py` a partir de la referencia (`docs/reference_*.tsv`), del registro verificado
> (`docs/store_registry.json`) y de los monitores reales. Esta página resume lo verificado a mano en la v0.5.

Última comprobación de todas: **19-nov-2026** (desde Chrome en el PC del usuario, Windows, España).

**Estados**, de menos a más:
1. **Localizada**: se sabe dónde publica la tienda la información.
2. **Lectura verificada**: se ha leído la fuente real y el formato coincide con el adaptador. Hecho desde el navegador de tu PC, que es la misma red y el mismo equipo donde correrá el bot. Desde Python se confirma con `PROBAR.bat` → `cookgroup probe`.
3. **Ejecutándose**: el monitor está corriendo de forma continua. Hoy no lo está en ningún sitio: se activa con `ARRANCAR.bat` o `INSTALAR_AUTOARRANQUE.bat`.
4. **Entrega confirmada**: Discord ha aceptado una alerta real. Pendiente de tu webhook: `PROBAR.bat` envía una alerta de prueba.

Todas las tiendas con el estado 2 están activas en `config/monitors.toml`. Ninguna ha llegado aún a los estados 3 y 4.

## Lanzamientos y raffles (calendario de la tienda)

| Tienda | País · regiones | Moneda | Envío a ES | Fuente | Qué detecta de verdad | Estado |
|---|---|---|---|---|---|---|
| **BSTN** | DE · eu_es (también uk_en, us_en, ch, dk, se, pl, cz, no, ca) | EUR (UK: GBP) | Sí (web eu_es: envío gratis a España desde 100 €) | `bstn.com/eu_es/men/upcoming`, `/women/upcoming/footwear` (HTML con `__NEXT_DATA__`) + fichas `/p/` y `/r/` | Lanzamiento anunciado; fecha confirmada o cambiada (con hora y zona de origen); raffle abierto, enlace nuevo y aviso de cierre (`raffleends`); solo app o solo en tienda; a la venta (ficha con tallas tras la hora publicada, con el retraso medido); vuelta de talla EU con UK/US cuando están alineadas y unidades; bajada de precio | 2 · lectura verificada |
| END. Launches | UK · en-eu | EUR | Sí | `endclothing.com/en-eu/collections/launches/products.json` | Modelo nuevo en lanzamientos; apertura y vuelta de tallas. **Sin fecha** (no está en el catálogo) | 2 |
| size? | UK | GBP | Por confirmar | `size.co.uk/collections/launches/products.json` (etiqueta `eql-launch-checked` → raffles en EQL) | Igual que END. Raffles de EQL: **no cubiertos** (plataforma aparte) | 2 |
| Footpatrol | UK | GBP | Por confirmar | `footpatrol.com/collections/launches/products.json` | Igual que END | 2 |
| SVD (Sivasdescalzo) | ES | EUR | Sí | `sivasdescalzo.com/es/lanzamientos` (Next.js app-router; fecha solo como texto en la tarjeta, p. ej. «300 € 20 Noviembre») | — | 1 · adaptador pendiente: formato interno frágil, prioridad alta |
| Courir | FR · ES | EUR | Sí | courir.es (Salesforce Commerce) | — | 1 · pendiente |
| Nike SNKRS | Global | — | — | App/SNKRS web con sesión | — | Seguimiento manual (requiere sesión/app; sin feed oficial estable) |
| adidas CONFIRMED | Global | — | — | Solo app | — | Seguimiento manual (solo app) |
| New Balance, ASICS, Salomon | Marcas | — | — | Webs de marca | — | 1 · pendiente (revisar sus páginas de lanzamientos) |
| atmos | JP | JPY | — | atmos-tokyo.com (no es Shopify) | — | 1 · pendiente |
| Kasina | KR | KRW | — | kasina.co.kr (robots excluye `/pick-out-jordan`, su sección de sorteos) | — | 1 · no se automatiza la sección excluida |
| mita sneakers, INVINCIBLE | JP · TW | — | — | — | — | Sin investigar todavía (siguiente oleada Asia) |
| 24 Kilates | ES → TH | — | — | 24kilates.com está aparcado y en venta (GoDaddy). Según Overkill cerraron Barcelona y operan desde Bangkok | — | Excluida (sin web activa localizada) |

## Catálogo completo (restock, producto nuevo, tallas, precio)

| Tienda | País · región | Moneda | Fuente | Detecta | Estado |
|---|---|---|---|---|---|
| Footdistrict | ES · eu | EUR | `/products.json` | Producto nuevo, restock, tallas nuevas, bajada de precio, posible price error | 2 |
| Asphaltgold | DE · eu | EUR | ídem | ídem | 2 |
| Overkill | DE · eu | EUR | ídem | ídem | 2 |
| Sneakersnstuff | SE · eu | EUR (por confirmar) | ídem | ídem | 2 |
| Family 3.0 | FR · eu | EUR | ídem | ídem | 2 |
| Noirfonce | FR · eu | EUR | ídem | ídem | 2 |
| Naked | DK · eu | EUR (por confirmar) | ídem | ídem | 2 |
| Kith EU | eu | EUR | ídem | ídem (ropa) | 2 |
| Slam Jam | IT · eu | EUR | ídem | ídem (ropa) | 2 |
| Goodhood | UK | GBP | ídem | ídem (ropa) | 2 |
| Voo Store | DE · eu | EUR | ídem | ídem (ropa) | 2 |
| Starcow | FR · eu | EUR | ídem | ídem (ropa) | 2 |
| Concepts | US | USD | ídem | ídem | 2 |
| Undefeated | US | EUR (adaptada a España) | ídem | ídem | 2 |
| Social Status | US | USD | ídem | ídem | 2 |
| A Ma Maniére | US | USD | ídem | ídem | 2 |
| Extra Butter | US | EUR (adaptada) | ídem | ídem | 2 |
| Up There | AU | EUR (adaptada) | ídem | ídem | 2 |
| Supply Store | AU | AUD | ídem | ídem | 2 |
| Dover Street Market | — | — | — | — | Descartada (no permite la consulta) |

## Chollos

| Fuente | Región | Detecta | Estado |
|---|---|---|---|
| Chollometro `/rss/hot` | ES | Chollo nuevo con tienda, precio y temperatura (≥100°) | 2 |
| Dealabs `/rss/hot` | FR | Ídem (≥150°) | 2 |

## Marketplaces de reventa (no son tiendas retail)
StockX, GOAT, Hypeboost, Kaufland y similares **no se monitorizan como tiendas**: venden a precio de reventa.
Solo aparecen como enlaces de búsqueda en las alertas. Su precio no se usa sin una fuente autorizada (`config/market_data.json`).

## Próximas oleadas (por prioridad)
1. **SVD** (España, raffles propios): adaptador del listado `/es/lanzamientos`.
2. **Courir** y las webs de marca (New Balance, ASICS, Salomon): localizar sus calendarios.
3. **Asia**: atmos, mita, Kasina (solo las secciones permitidas), INVINCIBLE.
4. **Latinoamérica, Oriente Medio y África**: sin investigar todavía.
