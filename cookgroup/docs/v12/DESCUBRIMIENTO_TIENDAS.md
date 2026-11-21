# Dónde descubre novedades el bot sin que el dueño escriba URLs (comprobado el 21-nov-2026, ~19:30 Madrid)

Método «lee el listado / lee la ficha»: desde el navegador del dueño se descargó el HTML del listado configurado
**sin cookies** (`fetch(..., {credentials: "omit"})`, lo más parecido a lo que recibe el bot) y se aplicó la MISMA
regla de enlaces de `config/monitors.toml`. Después se descargó, también sin cookies, la primera ficha encontrada.
Es una aproximación: el bot corre en el PC del dueño con Python y su propia IP, y una tienda puede tratarlo distinto.
Por eso queda pendiente un ciclo real desde Windows (ver lote 5).

| Monitor | Lee el listado (fichas que encuentra la regla) | Lee la ficha (sin cookies) | Detecta un cambio simulado | Observó un cambio auténtico |
|---|---|---|---|---|
| footlocker-es | sí · 48 | sí · estado con tallas | sí · test_tallas_por_color (44.5 por color, reinicio) | no |
| footlocker-fr | sí · 48 | sí · estado con tallas | mismo adaptador que ES (sin fixture propio) | no |
| footlocker-de | sí · 49 | sí · estado con tallas | sí · test_tiendas_fase2 (JSON-LD por color) | no |
| footlocker-it | sí · 48 | sí · estado con tallas (3 fichas) | sí · test_tiendas_fase2 + test_tallas (aviso por color) | no |
| asics-es | sí · 24 | sí · estado con tallas | sí · test_tallas_por_color (EU 46 negro) | no |
| zalando-es | sí · 24 (antes .html cogía 12 /faq/) | sí · ProductGroup con tallas | sí · test_tiendas_fase2 + test_descubrimiento_listados | no |
| zalando-fr | sí · 24 | sí · ProductGroup con tallas | sí · test_tiendas_fase2 | no |
| zalando-it | sí · 24 | sí · ProductGroup con tallas | sí · test_tiendas_fase2 | no |
| kickz-releases | sí · 24 (calendario Releases) | sí · Product con oferta | sí · test_tiendas_fase2 | no |
| 43einhalb | sí · 45 | sí · ProductGroup con oferta | sí · test_tiendas_fase2 | no |
| skatedeluxe | sí · 60 | sí · Product con oferta | sí · test_tiendas_fase2 | no |
| solebox-eu | sí · 47 | sí · Product con oferta | sí · test_jsonld | no |
| basket4ballers | **corregido**: /es/novedades → 404; categorías → 403 sin cookies; la portada /es/ enlaza 14 novedades | sí · ProductGroup | sí · test_tiendas_fase2 | no |
| adidas-es | sí · 48 | **no** · desafío anti-bot sin cookies («Powered and protected by») | solo con captura del navegador | no |
| newbalance-es | **no** · desafío anti-bot sin cookies | — | solo con captura del navegador | no |
| snipes-es | sin comprobar hoy: la extensión no tiene permiso de JS en snipes.com | — | sí · test_snipes_v11 | no |

Cambios de este lote:
- `product_link_pattern` admite `re:` + expresión regular sobre la ruta. Zalando exige el código de artículo,
  adidas el código de 6 caracteres, ASICS `/p/<modelo>-<color>.html` y Foot Locker excluye la tarjeta regalo (`/product/~/`).
- Los enlaces se guardan sin `?…` ni `#…`, así que el mismo producto con parámetros de seguimiento no se duplica.
- Un desafío anti-bot ya no se toma por «listado sin productos»: se registra como fallo (`anti-bot`) y no se elude.
- «Observó un cambio auténtico» está en **no** en todas: el bot aún no ha corrido contra estas tiendas desde el PC
  del dueño. Las 13 pruebas de «cambio simulado» usan capturas reales en las que se cambia un dato.
