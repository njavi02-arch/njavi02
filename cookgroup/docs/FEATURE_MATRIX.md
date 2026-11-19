# Matriz de funcionalidades

**Estado del análisis del servidor de referencia: NO REALIZADO.** No se facilitó enlace, invitación ni
capturas, y el conector de Discord de esta sesión no conectó. Nada de lo siguiente describe el servidor
original; es la lista de capacidades *típicas* de un cookgroup, con su equivalente propio.
Cuando se aporte acceso legítimo (o capturas), se rellenará la columna "Observado".

| Capacidad típica | Observado en referencia | Equivalente propio | Estado |
|---|---|---|---|
| Restocks | pendiente | `diff.py` RESTOCK (todas las variantes agotadas → disponible) | ✅ probado (simulado) |
| Producto nuevo vs restock | pendiente | NEW_PRODUCT vs RESTOCK, línea base sin spam | ✅ probado (simulado) |
| Tallas | pendiente | NEW_SIZE por variante | ✅ probado (simulado) |
| Bajadas de precio | pendiente | PRICE_DROP con umbral % | ✅ probado (simulado) |
| Deduplicación | pendiente | clave `tipo|producto|variantes|precio` + cooldown en BD | ✅ probado (simulado) |
| Embeds Discord | pendiente | `discord.py` | ✅ formato probado; ❌ envío real no probado |
| Beneficio neto / score | pendiente | `profit.py`, `scoring.py` | ✅ probado; datos de mercado: manuales |
| Raffles, calendario lanzamientos | pendiente | — | ⬜ pendiente |
| Price errors | pendiente | — (solo bajada de precio; no se etiqueta "error") | ⬜ pendiente |
| Panel admin, suscripciones, bot | pendiente | — | ⬜ pendiente |
| Capa IA (Claude API) | pendiente | — (el score actual es determinista) | ⬜ pendiente |
