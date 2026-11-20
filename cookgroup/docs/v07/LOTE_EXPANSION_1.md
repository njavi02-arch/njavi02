# Lote de expansión 1 — España, tiendas de alto valor (20-nov-2026)

Medido desde tu navegador (solo lectura). «Siguiente paso» es lo único que falta para activarla.
Solo se guardan tallas, enlaces, moneda y fechas cuando la fuente las da.

| Tienda | Plataforma (observado) | Resultado medido | Evidencia | Siguiente paso |
|---|---|---|---|---|
| FOOTDISTRICT | Shopify | ÚTIL: 250 productos, EUR, tallas y stock por talla | `footdistrict.com/products.json` | ya activa (piloto) |
| BSTN | Next.js propio | ÚTIL: 17 lanzamientos, 2 raffles abiertos | `bstn.com/eu_es/men/upcoming` | ya activa (piloto) |
| Solebox | SFCC (igual que Snipes) | ÚTIL: 44 fichas, precio EUR y disponibilidad en JSON-LD; **sin tallas** | `solebox.com/en-eu/c/footwear-2777` | activar tras el piloto (está en `config/piloto.toml`) |
| 24Segons | PrestaShop | PARCIAL: listado con 32 fichas `/es/product/…`; JSON-LD con precio EUR (1 oferta agregada); 17 tallas US **solo en el HTML**, sin stock por talla | `24segons.es/es/zapatillas-baloncesto/` | añadir con `type = "jsonld"`, `product_link_pattern = "/es/product/"` (avisos: producto nuevo y bajada de precio; tallas no) |
| SVD (Sivasdescalzo) | Next.js | **BLOQUEADO por permiso**: Chrome no permitió leer la página con script en este dominio | — | dar permiso a Claude en Chrome para `sivasdescalzo.com` (o abrirla tú y decírmelo) y repetir |
| Basketballemotion | propia (render en cliente) | SIN DATOS: el listado `/es/zapatillas` no trae fichas en el HTML (se cargan con JavaScript) | `basketballemotion.com/es/zapatillas` | localizar la API pública del listado; si no hay, descartar |
| AW LAB | SFCC | SIN DATOS: 15 enlaces en `/es-es/hombre/zapatillas`, pero las fichas probadas no traen JSON-LD de producto | `aw-lab.com/es-es/hombre/zapatillas` | probar otra categoría / ficha; si sigue sin JSON-LD, descartar adaptador estructurado |

Dependencias de acceso comercial ya identificadas (sin cambios): Zalando, Privalia y Amazon (afiliados/API comercial),
Nike SNKRS e instore (sin fuente autorizada), JD Sports (anti-bot).

Pendiente para lotes siguientes: streetwear, Pokémon/TCG, LEGO, electrónica y descuentos; listas oficiales de
distribuidores de colaboraciones; tiendas físicas de Madrid. Se retoma el historial de la referencia y los hilos
visibles después de que veas el piloto.
