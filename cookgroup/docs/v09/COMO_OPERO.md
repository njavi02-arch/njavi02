# Cómo opero el cookgroup como dueño

## Cada día (5 minutos)
1. Abre **PANEL_DUENO.bat**. Se abre la página de venta y, con tu `PANEL_PIN`, el **panel del dueño**.
2. Bloque **«Accesos que no cuadran»**: tiene que decir «todo cuadra». Si sale algo, mira «Un cliente ha pagado y no
   puede entrar».
3. Bloque **«Requiere atención»**: tickets abiertos, cobros fallidos, sincronizaciones pendientes y tareas editoriales.
4. Doble clic en **ESTADO.bat**: «PROCESO: EN MARCHA» y ninguna fuente «RETRASADA».

## Un cliente ha pagado y no puede entrar
1. Pídele por #soporte (ticket privado) su usuario de Discord. Nunca le pidas datos de la tarjeta.
2. En el panel, en **Fichas de miembro**, busca su ID:
   - **Derecho ✅ y Rol —**: Discord no aplicó el rol (estaba caído o el bot no tenía permiso). Pulsa
     **«Reintentar sincronización»**. Queda anotado en «Registro de acciones» como «dueño (panel)». Si vuelve a fallar,
     el error dice por qué: el bot sin «Gestionar roles» o el rol del bot por debajo de «Suscriptor activo».
   - **No aparece**: pagó con otra cuenta de Discord o no completó la vinculación. Que entre en la página de venta → «Darme
     de alta» con la cuenta correcta. En Stripe busca el pago por su email y comprueba `client_reference_id`.
   - **Derecho — («sin suscripción» o «impagada»)**: el pago no llegó o falló. Revísalo en Stripe → Pagos.
3. Sin hacer nada, la pasada automática reintenta cada 5 minutos.
4. Cierra el ticket con lo que se hizo.

## Detectar un monitor caído
- **ESTADO.bat** muestra el proceso (latido), «RETRASADA ×N» por fuente y el último error.
- **COMPROBAR.bat** dice por qué: VACÍA, LIMITADA (429 o anti-bot, se reintenta solo) o FALLO (URL cambiada, dominio
  caído). El CSV de `logs\` se abre con Excel. Ejemplo real: la URL de Snipes daba 404 y se corrigió así.
- **Si el proceso está PARADO**: ejecuta ARRANCAR.bat (o el autoarranque, cuando lo decidas).
- En el panel del dueño, «Alertas y fuentes» muestra la última entrega por tienda y las fuentes retrasadas.

## Comprobar que una baja se ha aplicado
1. Ficha del miembro: «cancela» en Vigencia significa que **conserva el acceso hasta la fecha que se muestra** (es
   lo correcto).
2. Pasada esa fecha: **Derecho —**, **Rol —** y en el registro «rol retirado» con el motivo «cancelada y vencida».
3. «Acceso sin derecho» tiene que estar vacío. Si aparece alguien, pulsa «Reintentar sincronización»: retira el rol.
4. Sus preferencias (marcas, tallas) se conservan, pero no recibe menciones ni ve canales de pago (probado:
   «ex-suscriptor» en la matriz de permisos).

## Cobros
- Pago fallido: el acceso sigue durante 3 días de gracia (`config/planes.toml`) mientras Stripe reintenta. Después se
  retira solo.
- Las cifras **REALES** y las **DE PRUEBA** salen en bloques separados. El «estimado» nunca es dinero cobrado.
- Cobrar de verdad exige `STRIPE_SECRET_KEY=sk_live_…` **y** `COBROS_REALES=si`. Sin las dos cosas, nunca se cobra.
