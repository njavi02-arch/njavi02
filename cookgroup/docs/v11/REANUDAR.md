# Punto de reanudación — 21-nov-2026

Último lote cerrado: v1.5 lote 2a (commit 0aea1c5, rama claude/cookgroup-v1.0). Tests: 515 passed, 2 skipped.

## Lo hecho en el lote 2a
- Zalando FR (/baskets-homme/) e IT (/sneakers-uomo/): ProductGroup con una variante por talla, precio EUR y stock. Integrados (zalando-fr, zalando-it → canal zalando-eu).
- Foot Locker DE e IT: ProductGroup con variantes por COLOR que traen precio y stock propios (no hay tallas). Integrados (footlocker-de, footlocker-it → canal footlocker-eu). El lector JSON-LD usa ahora el color como etiqueta cuando falta la talla.
- zalando-es: patrón cambiado de "-a13.html" a ".html".
- adidas DE/FR: el JSON-LD es un ProductGroup con variantes de color pero sin offers, así que no da precio ni stock. No se integra. adidas IT no se comprobó.
- Foot Locker FR: el primer enlace del listado era una ficha "~" sin variantes. Queda pendiente de una segunda comprobación.
- Test nuevo: test_listing_discovers_new_product_url. Una ficha nueva que aparece en el listado se anuncia una sola vez en las 13 tiendas JSON-LD.

## Siguiente acción exacta
1. Foot Locker ES: adaptador de tallas. La ficha trae unas 53 claves "size" fuera del JSON-LD; buscar el bloque de estado embebido.
2. ASICS: adaptador de tallas (en el JSON-LD la talla sale N/A).
3. Lote 2b: About You, YOOX, Sports Direct, LuisaViaRoma, Basketball Emotion, UGG (mercado efectivo), Sivasdescalzo y ASOS.
   Footshop: el permiso de JS en Chrome está denegado; probar otra ruta pública.
4. Retail Pokémon: GAME (watchlist con URLs reales), Carrefour, DRIM, Toys"R"Us, Alcampo, Darizard, El Corte Inglés, Fnac.
5. Fase 4: decisiones, fiabilidad (campos del panel) y la secuencia única de Windows.
