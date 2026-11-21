# Comprobación de la v0.9 (20-nov-2026, 13:30)

- **Punto de partida:** rama `claude/cookgroup-v0.9`, commit `c7738ba` (igual en local y en remoto, sin trabajo
  posterior). Pruebas: **142/142 en verde**.
- **Cifras recalculadas desde los archivos**: coinciden con el ZIP. 339 canales de referencia, 129 con función
  comprobada, 33 canales propios, 15 probados localmente y 0 entregas reales. En `canales.csv` hay 47 filas asignadas
  a #sneakers-eu, 28 a #pokémon-tcg y 112 sin equivalente.

## Qué decía el informe y qué hacía de verdad el programa
| Informe v0.9 | Realidad al arrancar el bot (`cookgroup run`) | Corregido en v1.0 |
|---|---|---|
| #lanzamientos (foro) «probado localmente» | El foro solo existía como módulo. El bot enviaba mensajes normales al webhook del foro, y Discord los rechaza sin `thread_name` | El bucle de lanzamientos y las colecciones «launches» publican en el foro: hilo por SKU y cambios dentro del hilo |
| #raffles con recordatorio, cambio de plazo y cierre | El bot usaba el aviso antiguo de raffles, sin lista de abiertos ni cierre por vencimiento | El tablón de raffles va dentro del bucle de lanzamientos; la lista fijada se edita en el mismo mensaje |
| Reglas de ping personales | El bot publicaba en «pings», un canal que el servidor no creaba (caía al webhook general o no salía) | Nuevo canal #alertas-personales |
| Calendario del staff | Publicaba en «releases», canal que tampoco existía | #próximos-7-días recibe el calendario y la vista de 7 días |
| #muestra-gratis «probado localmente» | El módulo existía, pero nada lo alimentaba | El bot pasa a la muestra lo entregado (máx. 3 al día, 60 min de retraso) |
| #registro-bot | Nada lo alimentaba | El bot avisa cuando una fuente falla 3 veces seguidas y cuando se recupera |
| 6 familias «mismo motor» | Sin prueba propia | Prueba propia con una captura real de cada familia (ver abajo) |

## Fallos reales encontrados al probar las 6 familias con datos reales
- **baskets-store.com** publica las medias tallas como «44 1/2»: no se reconocían, así que un miembro de la 44,5 nunca
  habría recibido la mención. Corregido.
- **flatspot.com y goodhoodstore.com** publican tallas **UK**: un miembro con talla EU no podía coincidir. Ahora el perfil
  admite tallas UK y el motivo del silencio lo explica.
- **ASOS Sample Sale** publica ropa como «XXL - EU 44»: se descartaba la variante. Corregido, y además ahora nunca se
  confunde con una talla 44 de zapatilla.
