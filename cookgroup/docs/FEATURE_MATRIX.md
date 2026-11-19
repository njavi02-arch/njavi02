# Matriz de funcionalidades

**Estado del análisis del servidor de referencia: REALIZADO (19-nov-2026, solo lectura).** Detalle por canal en
[`REFERENCE_AUDIT.md`](REFERENCE_AUDIT.md). En la columna "Observado": **[O]** = visto en pantalla, **[I]** = inferido.
No se conoce el código ni los proveedores internos de la referencia.

| Capacidad | Observado en referencia | Equivalente propio | Estado |
|---|---|---|---|
| Restocks | [O] Campo *Type/Reason: Restock* en Shopify, adidas, Zalando, Snipes, aio-world | `diff.py` RESTOCK | ✅ probado (simulado) |
| Producto nuevo vs restock | [O] "New" / "New add" / "Restock" / "Sale" explícito en el embed | NEW_PRODUCT vs RESTOCK, línea base sin spam | ✅ probado (simulado) |
| Tallas | [O] Por talla con stock ([n], LOW/MEDIUM/HIGH, 15+); EU con fracciones, UK, niño (Y). [O] Errores de parseo ("375", "36666") | `normalize.py`: tallas canónicas, descarta lo no interpretable, filtro opcional de tallas de niño | ✅ probado (simulado). Stock por talla: ❌ Shopify público no lo da |
| Bajadas de precio / rebajas | [O] Canales por tramo (30/60 %, Amazon 0-30/31-50/51-70/+70); tachado + % | PRICE_DROP con umbral %; `compare_at_price` como "Descuento tienda"; `discount_routes` copia la alerta al canal del tramo más alto | ✅ probado (simulado) |
| Price errors | [O] `#amazon-error` con "precio anterior" no creíble (miles de €) → falsos "-100 %" | `price_error.py`: referencia = mediana del histórico **propio**, mínimo de observaciones; tachado absurdo se ignora | ✅ probado (simulado) |
| Deduplicación | [O] Duplicados exactos (checkouts ×3; Shopify base + enriquecido; misma tienda .fr/.eu) | clave `tipo|producto|variantes|precio` + cooldown en BD; un único mensaje por evento | ✅ probado (simulado); `dedupe_group` unifica una tienda con varios dominios ✅ (simulado) |
| Validación del mensaje | [O] Mensajes vacíos "(Sin título)/—" en `#chollometro`; título = código en `#aio-world` | `validate_product`: no se publica sin título, con título numérico, sin URL o sin precio (salvo feeds marcados) | ✅ probado (simulado) |
| Embeds Discord | [O] Autor = nombre de tienda; SKU en bloque; región; enlaces por país; Links StockX/GOAT/eBay; imagen | `discord.py`: tipo, tienda, precio, antes/referencia, descuento, SKU, tallas, enlaces de búsqueda StockX/eBay | ✅ formato probado; ❌ envío real no probado |
| Beneficio neto / score | [O] Beneficio por talla "tras comisiones (12 % + 5 €)" + nº ventas 90 días + gráfico | `profit.py`, `scoring.py` (comisiones explícitas) | ✅ probado; datos de mercado: manuales (sin API autorizada) |
| Pings por palabra clave / rol | [O] `#pings-automaticos`: regla "palabras ≤ precio", rol, canal origen, motivo, botones "Ir al mensaje/producto" | `rules.py` + `[[ping_rule]]`: keywords (todas), exclusiones, precio máx., tipos de evento, solo menciona su rol | ✅ probado (simulado) |
| Chollos / retail / electrónica | [O] Chollometro, Dealabs, Pepper, mydealz, hotukdeals, PcComponentes, Lidl, Privalia, Zalando Privé | `sources/rss.py` (RSS/Atom públicos) | ✅ parser probado (simulado); ❌ ningún feed real verificado |
| Nike SNKRS / Nike instore | [O] Status, style code, exclusive, max qty, commerce date, stock por talla, tienda física y "last change" | — | ⬜ requiere fuente oficial/condiciones; no se implementa |
| adidas / Zalando / Demandware (Snipes, Solebox) | [O] Formatos con SKU, regiones, stock por talla | — | ⬜ solo con API/afiliado oficial |
| Raffles, calendario lanzamientos | [O] Sin canal de raffles; calendario **manual** del staff (foro por drop, horario, método LEO, semáforo 🔴🟠🟢) | `releases.py` + `config/releases.toml`: el staff edita; recordatorios (1 día/1 h/10 min), resumen "Drops del día" por hora, método, semáforo como opinión, sin repetir avisos | ✅ probado (simulado); raffles: solo como `method = "RAFFLE"` |
| Stock bajo demanda (comando) | [O] `/nike-stock` devuelve tallas/stock, fecha, método | — | ⬜ requiere bot propio |
| Redes sociales | [O] Posts de Instagram de tiendas con caption | — | ⬜ solo vía API oficial |
| Checkouts de bots / quicktask / ATC | [O] Feeds de bots de compra y enlaces ATC/QT | — | 🚫 fuera de alcance (compra automatizada de terceros) |
| Panel admin, suscripciones, bot | [O] Roles (Owner, Staff, Helper, Pinger, OG Chef…), tickets, app propia | — | ⬜ pendiente |
| Capa IA (Claude API) | [I] No se observa nada atribuible | — (score determinista) | ⬜ pendiente |
