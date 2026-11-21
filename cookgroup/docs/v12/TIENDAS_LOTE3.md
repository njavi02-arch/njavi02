# Lote 3 · tiendas pendientes y Pokémon (21-nov-2026)

Leído desde el navegador del dueño, sin cookies, como lo recibiría el bot. Solo lectura.

## Integradas en este lote (config/monitors.toml, cada 300 s)
| Tienda | Monitor | Aviso útil | Fuente | Prueba |
|---|---|---|---|---|
| ASOS ES | asos-es | reposición por talla y color, precio por talla, producto nuevo | estado público de la ficha (adaptador `asos`) | test_tiendas_lote3 (captura real) |
| About You ES | aboutyou-es | reposición por talla del color de la ficha, bajada de precio | JSON-LD (colores ya no se pisan) | test_tiendas_lote3 |
| Sivasdescalzo | sivasdescalzo-es | reposición por talla, novedades, limited edition | JSON-LD | test_tiendas_fase2 |
| GAME | game-es | vuelta a stock de 3 fichas fijas + Pokémon TCG nuevo en /pokemon | JSON-LD | test_tiendas_fase2 (3 capturas agotadas) |
| El Corte Inglés | elcorteingles-pokemon | vuelta a stock / nuevo / precio de JCC | JSON-LD | test_tiendas_fase2 (2 agotadas reales) |
| DRIM | drim-pokemon | nuevo / stock / precio de TCG | JSON-LD (VTEX) | test_tiendas_fase2 |
| Toys"R"Us | toysrus-pokemon | stock / precio (LEGO Pokémon, juegos) | microdatos + stockLevelStatus (adaptador `hybris`) | test_tiendas_lote3 · sin muestra agotada real |

## Bloqueadas o sin terminar (qué falta para desbloquear)
| Tienda | Mercado | Fuentes comprobadas | Qué falta |
|---|---|---|---|
| Sivasdescalzo raffles | ES | /es/lanzamientos dice que los sorteos van por la app | No hay fuente web pública; solo la app |
| YOOX | ES | /es/hombre/zapatos/zapatillas → 404; la portada no enlaza fichas en el HTML | Encontrar el listado actual de la tienda (URL) y repetir la sonda |
| Basketball Emotion | ES | /zapatillas-baloncesto → 404; Shopify sin /products.json (404/500) | URL de su colección actual; luego JSON-LD de la ficha |
| LuisaViaRoma | ES | La página redirige al cargar; no se pudo leer | Repetir desde el PC (ciclo real) |
| Footshop | ES | La extensión no tiene permiso de JS en footshop.es | Permiso de sitio en Chrome **o** ciclo real desde el PC |
| UGG | ES/EU | Sin comprobar en esta sesión | Comprobar el mercado efectivo (ugg.com/es-es) |
| Sports Direct | UK/ES | Sin comprobar en esta sesión | Confirmar si hay tienda ES y envío a España |
| Carrefour | ES | La búsqueda redirige; sin listado estable comprobado | URL de categoría Pokémon y sonda de la ficha |
| Fnac | ES | La búsqueda redirige al cargar | URL de categoría y sonda |
| Alcampo | ES | Sin comprobar | URL de categoría |
| Darizard | ES | darizard.com no resuelve desde el navegador | Dominio correcto de la tienda |
| adidas ES (ficha) | ES | Listado sí; ficha = desafío anti-bot sin cookies | Ciclo real desde el PC; si persiste, solo descubrimiento |
| New Balance ES | ES | Listado = desafío anti-bot sin cookies | Ciclo real desde el PC |
