# Punto de reanudación — sesión de 5 h (inicio 03:01, límite 08:01 Madrid)

## 03:50 · lote D (tiendas) + auditoría #snipes
- Último canal auditado en ZESTY CREW: #snipes (966055358328107078); antes, #snipes-custom (1171109774738337802).
- Hallazgo: #snipes = Restock (monitor «zesty x Yeet»), #snipes-custom = Price Change + SKU/PID (otro monitor). Nuestro #snipes los une con etiqueta RESTOCK / REBAJA (test_snipes_v11).
- Validación EN VIVO desde el Chrome del dueño: 252 dominios Shopify · 244 con fuente operativa · 187 envían a España (docs/v11/validacion_shopify_2026-11-21.txt).
- Lote 2: 90 muestras reales fechadas; 89 pasan restock + rebaja + sin repetir; 88 tiendas nuevas con canal (una reutiliza canal); yellowshop.es pendiente de otra muestra.
- Fallo real corregido: productos sin tallas (TCG «Default Title» con idioma, colores) se descartaban enteros → ahora se publican sin decir talla.
- Pruebas: 368 pasan, 1 saltada (yellowshop).
- Próxima tarea exacta: reconstruir panel/directorio con 98 tiendas, recalcular cifras, commit; después shopify-eu (41) y los 47/28/112 en Discord.

## 03:45 · auditoría de los 47/28/112 + lote 3
- Recorrido de solo lectura de 180 canales en ZESTY (los 47, 28 y 112): docs/v11/auditoria_187_2026-11-21.txt; último canal: #accesorios-sneakers. Fusionado en FIDELIDAD.csv (columna observado_21nov).
- Diferencias convertidas en tareas: «New add» → LANZAMIENTO probado por tienda (test_tiendas_lote2); «Price Change» → REBAJA; «[stock]» por talla → la fuente pública de Shopify no da unidades (no se replica); QT/enlaces de bots → no (terceros), sí StockX/eBay.
- Lote 3: 58 tiendas más → 156 tiendas con canal y tarjeta (146 de los lotes 2-3 con lanzamiento/restock/rebaja probados).
- Próxima tarea exacta: Excel actualizado, panel publicado, informe final; con token: INSTALAR_SERVIDOR + PRUEBA_RAFFLE + ARRANCAR en el PC.
