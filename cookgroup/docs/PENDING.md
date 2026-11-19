# Pendiente / limitaciones conocidas

1. **Sin verificación con red real**: el entorno de desarrollo bloqueó las tiendas (proxy). `ShopifySource` solo está
   probada con respuestas simuladas. Hay que probar cada tienda real y comprobar sus condiciones de uso/robots.
2. **Datos de mercado**: sin API autorizada integrada. `FileMarketProvider` lee un JSON manual. Investigar APIs/partners
   oficiales (eBay Browse/Marketplace Insights, afiliados, etc.) antes de automatizar; no se hace scraping de StockX/GOAT.
3. **Comisiones** en `profit.py`: valores orientativos; verificarlos y moverlos a config.
4. **Botón COMPRAR**: requiere bot propio; con webhook normal solo hay enlace en el embed.
5. **Estado de alertas** (marcar agotado al editar el mensaje): no implementado (SOLD_OUT no se publica).
6. **Monitores** de raffles, lanzamientos y diferencias entre tiendas: no implementados. Price errors y feeds RSS: implementados
   y probados solo con datos simulados; ningún feed RSS real verificado todavía (revisar condiciones de cada web).
7. **PostgreSQL/Redis**: la v1 usa SQLite (suficiente para un proceso). Migrar al crecer; `migrations/` ya es SQL simple.
8. **Panel web, roles, suscripciones/Stripe, bot Discord, capa IA, métricas**: no implementados.
9. Marcar `enabled = true` solo tras verificar cada tienda; el monitor de ejemplo usa un dominio `.invalid`.
10. **Price error**: necesita histórico propio (por defecto 5 observaciones) → los primeros días no etiqueta nada como error.
11. **Stock por talla**: el `/products.json` público de Shopify no da unidades; solo disponible/no disponible.
12. **Misma tienda con varios dominios** (.fr/.eu, observado en la referencia): no se unifica aún.
13. **Pings**: requieren rol con ID real en `[[ping_rule]]` y `DISCORD_WEBHOOK_PINGS`; un webhook solo menciona roles mencionables.
