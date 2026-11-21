# Punto de reanudación — sesión de 5 h (inicio 03:01, límite 08:01 Madrid)

## 03:50 · lote D (tiendas) + auditoría #snipes
- Último canal auditado en ZESTY CREW: #snipes (966055358328107078); antes, #snipes-custom (1171109774738337802).
- Hallazgo: #snipes = Restock (monitor «zesty x Yeet»), #snipes-custom = Price Change + SKU/PID (otro monitor). Nuestro #snipes los une con etiqueta RESTOCK / REBAJA (test_snipes_v11).
- Validación EN VIVO desde el Chrome del dueño: 252 dominios Shopify · 244 con fuente operativa · 187 envían a España (docs/v11/validacion_shopify_2026-11-21.txt).
- Lote 2: 90 muestras reales fechadas; 89 pasan restock + rebaja + sin repetir; 88 tiendas nuevas con canal (una reutiliza canal); yellowshop.es pendiente de otra muestra.
- Fallo real corregido: productos sin tallas (TCG «Default Title» con idioma, colores) se descartaban enteros → ahora se publican sin decir talla.
- Pruebas: 368 pasan, 1 saltada (yellowshop).
- Próxima tarea exacta: reconstruir panel/directorio con 98 tiendas, recalcular cifras, commit; después shopify-eu (41) y los 47/28/112 en Discord.
