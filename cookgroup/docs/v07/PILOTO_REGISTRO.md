# Registro del piloto local (ejecutado 20/11/2026 13:12, Madrid)

**Tipo de datos:** CAPTURA REAL (footdistrict.com, 20-nov-2026 12:08 Madrid) + cambios CONTROLADOS aplicados en un servidor local + Discord SIMULADO. No se envió nada a un Discord real.

Resultado global: **TODO OK**

| Paso | Resultado | Detalle |
|---|---|---|
| 1. Captura y normalización (base) | OK | 3 productos reales leídos por HTTP, 0 eventos (la base no avisa) |
| 2. Vuelve una talla (cambio controlado: Oregon Ultra Tech talla 44) | OK | 1 evento(s), 1 aviso confirmado (id PILOTO-0001) |
| 3. Bajada de precio (cambio controlado: Dr. Martens 280 → 224 €, −20 %) | OK | 1 evento(s), 1 aviso; historial de precio guardado |
| 4. Discord caído al detectar (Autry talla 39 vuelve) | OK | aviso guardado en bandeja (pendientes: 1); error: RuntimeError: Discord: reintentos agotados |
| 5. Reinicio con Discord aún caído | OK | tras reiniciar no se re-detecta ni se pierde: sigue 1 pendiente |
| 6. Discord vuelve: se entrega lo pendiente | OK | entregado 1 aviso (id PILOTO-0003); bandeja vacía |
| 7. Otro reinicio + 2 ciclos: sin duplicados | OK | mensajes totales recibidos: 3 |
| 8. Último mensaje confirmado registrado | OK | ('2026-11-20T12:12:54+00:00', 'PILOTO-0003') |
| 9. Ningún aviso publica beneficio sin ventas verificadas | OK | market_data vacío → sin cifras de beneficio |

## Avisos recibidos por el Discord simulado

- **🔄 VUELVE LA EU 44 — FOOTDISTRICT** — Tienda: FOOTDISTRICT · 🇪🇸 ES · región EU; Precio: 110,00 €; SKU: `KZ8462-44`; Tallas: EU 44
- **BAJADA DE PRECIO — Dr. Martens** — Tienda: FOOTDISTRICT · 🇪🇸 ES · región EU; Ahora: 224,00 €
*origen: ficha de la tienda al detectar*; Antes: 280,00 €
*origen: nuestra lectura anterior de la ficha de la tienda*; SKU: `43651200`
- **🔄 VUELVE LA EU 39 — FOOTDISTRICT** — Tienda: FOOTDISTRICT · 🇪🇸 ES · región EU; Precio: 129,00 €; Descuento tienda: ~~215,00 €~~ (-40 %)
*origen: precio tachado que publica la tienda*; SKU: `AULMGG04-39`

Repetir: `python tools/piloto.py` (o `VER_PANEL.bat`, que lo ejecuta antes de abrir el panel).