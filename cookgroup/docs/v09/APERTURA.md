# Apertura comercial: oferta, costes y qué falta

**No soy asesor legal ni fiscal.** Revisa las condiciones y la fiscalidad (IVA en servicios digitales) con un
profesional antes de cobrar.

## Oferta propuesta (configurable en config/planes.toml)
- **Suscripción mensual: 19,99 €/mes, IVA incluido.** Es una propuesta, no está validada con el mercado. Sin permanencia;
  si cancelas, el acceso sigue hasta el fin del periodo; 3 días de gracia si falla un cobro.

## Costes previstos por suscriptor y mes (estimación)
| Concepto | Importe | Fuente |
|---|---:|---|
| IVA 21 % incluido en el precio | 3,47 € | cálculo (19,99 − 19,99/1,21) |
| Stripe, tarjeta europea estándar (1,5 % + 0,25 €) | 0,55 € | tarifa pública de Stripe España (ver Fuentes) |
| Stripe Billing (suscripciones) | ~0,14 € | **verificar**: Billing tiene coste aparte; confirmar el % en stripe.com/es/pricing |
| **Neto aproximado por suscriptor** | **~15,8 €** | |

Costes fijos estimados (sin verificar precios): servidor VPS para 24/7, unos 5–10 €/mes; dominio, unos 10 €/año.
Discord es gratis.

## Qué se puede anunciar con evidencia (hoy)
- Avisos de **260 fuentes** configuradas, con 6 leídas en real el 20-nov (Footdistrict, Asphaltgold, BSTN, Solebox,
  Snipes y Chollometro).
- **Menciones por tu talla y tus marcas**, una sola vez por señal (probado localmente con datos reales de Footdistrict).
- **Foro de lanzamientos** con hora de Madrid y **raffles** con cierre y recordatorio (probado con la captura real de
  BSTN).
- Hora de Madrid, origen de los precios en las rebajas y beneficio **solo verificado** con ventas de la misma talla.
- **No anunciar todavía:** «verificado en Discord», número de entregas reales, LEGO, electrónica, tiendas físicas de
  Madrid, Nike SNKRS, Zalando o Amazon, ni market de compraventa.

## Pendiente antes de aceptar clientes
1. **Token del bot + INSTALAR_SERVIDOR.bat** y una **entrega real confirmada** en #pruebas-bot. Después, verificar en
   Discord la vista de visitante y la de suscriptor con dos cuentas tuyas.
2. **Stripe en modo prueba** con tus claves: un alta y una baja completas con tarjeta de prueba; el webhook, con
   `stripe listen` o con la URL pública del servidor.
3. **Hosting 24/7** (decisión tuya) y que el bot lleve 72 h en marcha sin fuentes caídas.
4. **Condiciones de venta, política de privacidad y textos legales** de la página de venta. Fiscalidad del IVA.
5. **Responsable humano** de #soporte y de la moderación de la comunidad, con tiempos de respuesta.
6. Las tareas editoriales del panel (textos fijados, calendario confirmado).
