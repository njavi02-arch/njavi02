# Fiabilidad de los avisos y velocidad real (v1.6 · 21-nov-2026)

## Qué garantiza el sistema
| Caso | Comportamiento | Prueba |
|---|---|---|
| Falla 1 ficha de 10 | Se leen las otras 9; la que falla conserva su último estado (no hay falsa reposición ni falso agotado al volver) | test_fiabilidad::test_one_page_of_ten_fails… |
| Página incompleta (cortada) | Sin datos válidos → la ficha no se toca este ciclo | test_incomplete_page_keeps_last_valid_state |
| Fallan TODAS las fichas | El ciclo cuenta como error; nada se marca agotado | test_tiendas_fase2 (caída simulada) |
| El listado cambia de orden | No es novedad | test_listing_order_change_is_not_news |
| Dos colores con precios distintos | La bajada se calcula **por talla/color frente a su propio precio**: si vuelve el color barato no hay «rebaja» falsa; si baja de verdad un color, el aviso nombra ese color y su precio anterior | test_two_colors_different_prices_no_false_drop |
| Mismo código en dos países | El estado va **por monitor** y el código lleva el país (ES:…, FR:…): un mercado nuevo arranca en silencio y no pisa a otro | test_same_code_in_two_markets_does_not_collide |
| Estado desconocido de una talla | Ni disponible ni agotada: no genera avisos | test_tallas_por_color::test_unknown_state… |
| Desafío anti-bot | Se registra como fallo «anti-bot»; no se elude ni se toma por «sin productos» | test_descubrimiento_listados |
| 2 canales reciben y falla el 3.º; reinicio | El pendiente queda en la bandeja (SQLite); tras reiniciar se envía SOLO al canal que faltaba | test_two_channels_ok_third_fails_restart… |
| Envío de resultado incierto (se corta tras enviar) | Se marca «incierto» en la bandeja y se reenvía **una vez** en el siguiente ciclo | test_uncertain_send_is_marked_and_resent_once |

**Garantía de entrega: «al menos una vez».** Un aviso detectado nunca se pierde por un fallo de Discord o un reinicio:
queda en la bandeja hasta que Discord confirma el mensaje. Si la conexión se corta DESPUÉS de enviarlo, el sistema no
puede saber si llegó: lo reenvía una vez. En ese caso concreto el miembro puede ver **un duplicado** (nunca una ráfaga:
ya no se reintenta dentro del mismo envío). El panel muestra esos casos como «incierto».

## Velocidad
- Cada monitor tiene su propio hilo; el límite de 2 s entre peticiones es **por dominio**. Una tienda lenta o caída no
  retrasa a BSTN ni a otra tienda (comprobado en la simulación de abajo).
- v1.6: el intervalo configurado se cuenta **de inicio a inicio** de lectura. Antes, la espera empezaba al terminar
  el ciclo y BSTN «a 60 s» salía a unos 65 s.
- Las tiendas JSON-LD siguen a 300 s: cada ciclo son unas 5 peticiones (listado + 4 fichas). Bajarlas a 60 s sería
  multiplicar por 5 la carga sobre la tienda y el riesgo de bloqueo. Propuesta tras medir en el PC: 120 s solo para
  el listado de Foot Locker y Zalando (descubrimiento) si la medición real no muestra 429/bloqueos.

### Resultado · SIMULACIÓN local (no son tiendas reales)
Escala 1/60, 1 hilo por monitor, 38 monitores (8 + 30 Shopify de ruido), latencias variadas, una tienda que tarda
~45 s por petición y otra que falla siempre. Comando: `python tools/medir_intervalos.py --simulacion --segundos 60`
```

SIMULACIÓN local (escala 1/60, 60 s reales ≈ 60 min)
----------------------------------------------------
monitor                 config  lecturas  observado     máx   ciclo
bstn-eu                     60        60       61.6    65.9     3.5
footlocker-es              300        13      295.2   325.6    15.3
footlocker-fr              300        12      308.1   329.114.149999999999999
zalando-es                 300        13      293.5   327.2    10.6
zalando-fr                 300        13      289.3   322.5    10.5
tienda-lenta               300        12      304.0   329.6   216.0
tienda-caida               300         3      986.1  1346.6    93.4
asics-es                   300        12      314.3   323.1   13.65
```
«observado» = mediana de segundos entre el INICIO de dos lecturas seguidas. «ciclo» = lo que tarda una lectura.

### Medición real (pendiente en tu PC)
```
python tools/medir_intervalos.py --real --monitores bstn-eu,footlocker-es,zalando-es,asics-es --ciclos 3
```
Solo lectura, sin Discord; tarda unos 12 minutos (3 lecturas de las tiendas a 300 s). Deja `medicion_intervalos.csv`.

## Panel
Por tienda: **intervalo configurado**, **intervalo observado** (mediana real de monitor_runs), **última lectura buena**,
**próximo intento y por qué**, **última entrega confirmada** (con enlace al mensaje) y los avisos **pendientes / inciertos**.
El estado distingue «sin novedades» de «sin leer desde hace horas».
