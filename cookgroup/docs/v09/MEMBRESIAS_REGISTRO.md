# Membresías en PRUEBA LOCAL (ejecutado 20/11/2026 13:12, Madrid)

Web local real (HTTP) + simulador de Stripe (eventos firmados como Stripe, livemode=false) + Discord simulado.
No se cobra nada y no se toca Discord.

Resultado: **TODO OK**

| Paso | Resultado | Detalle |
|---|---|---|
| 1. Visitante abre la página de venta | OK | ve el plan, el precio (19,99 €/mes), qué incluye y las condiciones |
| 2. Visitante sin pagar: solo zona pública | OK | ve bienvenida, planes, muestra y soporte; no ve los canales de pago |
| 3. Alta: vincula Discord → pago de prueba → rol | OK | pago simulado con firma de Stripe; rol «Suscriptor activo» concedido; vigente hasta 2026-12-20T12:12:55+00:00 |
| 4. Bienvenida enviada una sola vez | OK | mensaje privado de bienvenida |
| 5. Acceso a los canales contratados | OK | ahora ve #sneakers-eu, #lanzamientos, #raffles… |
| 6. El cliente ve su suscripción | OK | página /cuenta: estado, vigencia y botón de cancelar |
| 7. Cancela: mantiene el acceso hasta el fin del periodo | OK | activa (cancelada: acceso hasta el fin del periodo) |
| 8. Al vencer se retira el acceso | OK | rol retirado; conserva preferencias (Nike, EU 44,5) pero ya no ve los canales de pago |
| 9. Ha pagado pero Discord estaba caído → aparece en el panel | OK | «PAGADO SIN ACCESO» con el error; sincronización pendiente |
| 10. El dueño pulsa «Reintentar» → acceso recuperado y anotado | OK | rol concedido; queda en el registro como acción del dueño |
| 10b. …o se recupera solo en la siguiente pasada automática (cada 5 min) | OK | sin intervención: la pasada periódica concede el rol pendiente |
| 11. Panel protegido por PIN | OK | sin PIN: 403 |
| 12. Renovación: nuevo periodo y cobro de renovación | OK | acceso hasta el nuevo fin de periodo |
| 13. Evento duplicado: se ignora | OK | Stripe repite el mismo evento: no se cuenta dos veces |
| 14. Evento con firma falsa: rechazado | OK | {"error": "firma no v\u00e1lida"} |
| 15. Pago fallido: acceso durante la gracia | OK | pago pendiente: en periodo de gracia |
| 16. Gracia agotada: acceso retirado | OK | impagada: gracia agotada |
| 17. Al final, nada descuadrado | OK | panel: todo cuadra |

Cifras de prueba al terminar: {'miembros_de_pago': 0, 'altas': 0, 'renovaciones': 0, 'bajas': 0, 'cancelaciones_programadas': 0, 'cobrado_cents': 0, 'cobros_fallidos': 1, 'mrr_cents': 0}

Repetir: `python tools/membresias_demo.py`