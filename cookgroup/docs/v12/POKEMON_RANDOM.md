# Fase 4 · Pokémon/TCG (11) y «random invest» (34)

| Tienda | Fuente comprobada (21-nov) | Cómo se monitoriza | Estado |
|---|---|---|---|
| GAME | La ficha trae JSON-LD (Product: disponibilidad + precio). El buscador se carga por JS y su robots.txt bloquea /api | **Lista de seguimiento** por URL de ficha (watch_urls): el staff añade los productos Pokémon que interesan | Probado en local con una ficha real |
| Tiendas TCG con Shopify (Red Goblin, Pokemillon, Cardcosmos, TCG Dojo, Yonko TCG, Pokeprinz, Senpai Manga…) | /products.json | Monitor Shopify (producto nuevo, reposición, rebaja) | Probado en local (muestra real por tienda) |
| Carrefour, DRIM, Toys"R"Us, Alcampo, El Corte Inglés, Fnac | Sin auditar en esta sesión | Lista de seguimiento si su ficha trae JSON-LD | Pendiente |
| Amazon ES/EU | Requiere el programa de afiliados de Amazon | — | **Decisión tuya** (ver abajo) |

**Amazon**, condiciones vigentes comprobadas hoy en la documentación oficial:
- Para usar su API de productos (Creators API) hay que estar en Amazon Afiliados del país y tener **al menos 10 ventas válidas en los últimos 30 días**.
- Se pierde el acceso tras 30 días sin ventas referidas.

**Catálogos grandes**: siempre por lista de seguimiento (producto, referencia o colección), para no llenar Discord con artículos corrientes.

Las recomendaciones (#calls-pokemon) son editoriales y van aparte de los avisos automáticos. Plantilla en EDITORIAL.md.
