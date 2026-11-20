# Lote 1 — bienvenida, roles y notificaciones (ejecutado 20/11/2026 13:12, Madrid)

**Datos:** CAPTURA REAL de Footdistrict (20-nov 12:39) + cambios CONTROLADOS + Discord SIMULADO. Perfil de prueba: EU 44,5 · ASICS y New Balance · envío a España.

Resultado: **TODO OK**

| Paso | Resultado | Detalle |
|---|---|---|
| 0. Bienvenida → perfil | OK | roles elegidos: Sneakers, Rebajas, Lanzamientos, Raffles · ASICS, New Balance · Envío a España · EU 44,5 |
| 1. Base (estado real de la tienda) | OK | 2 productos reales; NB 990v7: 44,5 agotada; ASICS Kayano 14: solo 42,5 y 43,5 |
| 2. ✅ Vuelve la EU 44,5 de New Balance → te menciona | OK | aviso en #sneakers-eu con «<@tu-id> · EU 44,5»; solo se notifica a tu usuario (allowed_mentions) |
| 3. 🔕 Vuelve la EU 44 de ASICS (no es tu talla) → se publica, pero sin mencionarte | OK | motivo registrado: su talla no está disponible (disponibles: EU 44) |
| 4. 🔕 La misma señal en el canal agregado (#restocks) → sin segunda mención | OK | ya se le mencionó por esta misma señal en otro canal |
| 5. 🔕 Otra marca (adidas) en tu talla | OK | la marca no está entre las suyas (ASICS, New Balance) |
| 6. 🔕 Tienda que solo da stock general: no puede decir «vuelve la 44,5» | OK | la tienda solo da stock general: no se puede confirmar su talla |
| 7. 🔕 Tienda sin envío a España confirmado | OK | la tienda no tiene confirmado el envío a España |
| 8. 🔕 Avisos en pausa | OK | avisos en pausa |
| 9. Producto nuevo de tu marca en tienda sin tallas → aviso de producto, avisando de que la talla no está confirmada | OK | producto de interés; la tienda no da stock por talla (talla sin confirmar) |

Repetir: `python tools/lote1.py`