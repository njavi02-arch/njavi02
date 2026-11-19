# Pendiente / limitaciones conocidas

1. **Verificación real (19-nov-2026, desde navegador)**: 12 tiendas Shopify responden a `/products.json` y su robots.txt no
   lo prohíbe; DSML descartada. El bot aún no ha corrido 24 h seguidas contra ellas: vigilar 429/403 en los logs.
   Condiciones de uso de cada tienda: no revisadas legalmente.
2. **Datos de mercado**: sin API autorizada integrada. `FileMarketProvider` lee un JSON manual. Investigar APIs/partners
   oficiales (eBay Browse/Marketplace Insights, afiliados, etc.) antes de automatizar; no se hace scraping de StockX/GOAT.
3. **Comisiones** en `profit.py`: valores orientativos; verificarlos y moverlos a config.
4. **Botón COMPRAR**: requiere bot propio; con webhook normal solo hay enlace en el embed.
5. **Estado de alertas** (marcar agotado al editar el mensaje): no implementado (SOLD_OUT no se publica).
6. **Monitores** de raffles (entrada automática) y diferencias entre tiendas: no implementados. Price errors y feeds RSS: implementados
   y probados solo con datos simulados; ningún feed RSS real verificado todavía (revisar condiciones de cada web).
7. **PostgreSQL/Redis**: la v1 usa SQLite (suficiente para un proceso). Migrar al crecer; `migrations/` ya es SQL simple.
8. **Panel web, roles, suscripciones/Stripe, bot Discord, capa IA, métricas**: no implementados.
9. Marcar `enabled = true` solo tras verificar cada tienda; el monitor de ejemplo usa un dominio `.invalid`.
10. **Price error**: necesita histórico propio (por defecto 5 observaciones) → los primeros días no etiqueta nada como error.
11. **Stock por talla**: el `/products.json` público de Shopify no da unidades; solo disponible/no disponible.
12. **Misma tienda con varios dominios** (.fr/.eu, observado en la referencia): no se unifica aún.
13. **Pings**: requieren rol con ID real en `[[ping_rule]]` y `DISCORD_WEBHOOK_PINGS`; un webhook solo menciona roles mencionables.
14. **Calendario**: el ejemplo trae 2 lanzamientos anotados en la auditoría (Mind 001, AF1 x Travis Scott x GTA 6) con enlace
    genérico a Nike Launch y valoración "unknown": verificar fecha/hora/enlaces antes de activar `DISCORD_WEBHOOK_RELEASES`.
    Si el bot está parado en el momento de un recordatorio, ese aviso se pierde (ventana de gracia 15 min).
15. **Tramos de descuento**: solo copian alertas de los monitores propios; no hay monitor de Amazon (sin API autorizada integrada).
16. **SQLite compartido entre hilos** (monitores + calendario): válido para pocos monitores; migrar a PostgreSQL al crecer.
17. **Catálogo parcial**: se lee la 1ª página (250 productos) por tienda; restocks de productos antiguos fuera de esa página
    no se ven. Subir `pages` (máx. 4) en tiendas grandes si hace falta.
18. **Moneda**: Sneakersnstuff y Naked marcadas EUR sin confirmar; Goodhood en GBP (sin cálculo de beneficio).
19. **Reglas de ping** de ejemplo con `role_id` de ceros: poner IDs reales.
20. **Ningún monitor está ejecutándose** en un equipo persistente: esta sesión es temporal. Se activa en tu PC con `INSTALAR_AUTOARRANQUE.bat`.
21. **Entrega real a Discord sin confirmar**: falta un webhook. `PROBAR.bat` envía una única alerta de prueba identificada.
22. **Lectura desde Python** de BSTN y de las tiendas nuevas: verificada solo desde el navegador del mismo PC. `cookgroup probe` lo confirma.
23. **BSTN**: la fecha de salida de los productos con raffle solo está en raffle.bstn.com (excluido por robots.txt): no se lee.
    La cancelación no se publica: un producto que desaparece del calendario no genera alerta.
24. **SVD, Courir, EQL, marcas y Asia**: ver `docs/STORES.md` («Próximas oleadas»).
25. **Discord del grupo de referencia**: la sesión del navegador caducó. Volver a iniciarla para la segunda pasada.
