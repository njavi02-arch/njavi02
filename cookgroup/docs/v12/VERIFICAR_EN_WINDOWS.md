# Primera comprobación en tu PC con Windows (lote 5)

Todo con doble clic en la carpeta `cookgroup`. El token lo escribes tú en `.env`; nunca sale en pantalla ni en `logs\verificar.txt`.

| Orden | Qué haces | Qué comprueba | Si falla |
|---|---|---|---|
| 1 | `INSTALAR.bat` | Python 3.11+, entorno del bot, crea `.env` | el mensaje dice qué instalar |
| 2 | En `.env`: `DISCORD_BOT_TOKEN=…` y `DISCORD_GUILD_ID=1572928642999255120` | — | — |
| 3 | `VERIFICAR.bat tienda` | **Paso 1:** tu PC lee BSTN y FOOTDISTRICT (solo lectura; productos y milisegundos) | sin internet, antivirus que inspecciona HTTPS, 403/429 de la tienda: cada caso con su arreglo |
| 4 | `VERIFICAR.bat discord` | **Paso 2:** token válido (2.1), el bot está en TU servidor (2.2), existe #pruebas-bot con su webhook (2.3) | 2.1 token mal copiado · 2.2 invitar el bot (URL de OAuth2) · 2.3 ejecutar `INSTALAR_SERVIDOR.bat` |
| 5 | `INSTALAR_SERVIDOR.bat` (si el paso 2.3 lo pide) | crea canales, roles y webhooks que falten; no duplica ni borra | — |
| 6 | `VERIFICAR.bat alerta` | **Paso 3:** UN aviso marcado PRUEBA solo en #pruebas-bot, releído por su ID; imprime el **enlace directo** | no envía nada si falta algo del paso 2 |
| 7 | En el móvil | abre el enlace del paso 3 (o #pruebas-bot en la app de Discord) y mira el aviso de PRUEBA | — |
| 8 | `INSTALAR_AUTOARRANQUE.bat` y luego `VERIFICAR.bat arranque` | **Paso 4:** tarea «Cookgroup» instalada y estado de cada tienda | «BOT PARADO» → `ARRANCAR.bat` |

`VERIFICAR.bat` sin nada hace los pasos 0, 1 y 2 seguidos y pregunta (escribe SI) antes de enviar el aviso del paso 3.

## Qué se ha ejecutado aquí y qué falta en tu PC
| | Aquí (23-nov) | En tu PC |
|---|---|---|
| Paso 1 tienda | lógica probada con tienda simulada (OK y 403); contra tiendas reales este entorno recibe 403 de su propia red, y así lo informa | **pendiente**: lectura real |
| Paso 2 Discord | probado con un Discord simulado: OK y los 6 fallos posibles, sin que el token aparezca | **pendiente**: tu token y tu servidor |
| Paso 3 alerta | probado: enlace directo cuando se confirma; no envía nada si falta configuración | **pendiente**: el aviso real en #pruebas-bot |
| Reinicio y recuperación | probados en local (test_e2e_runner: tras reiniciar no repite avisos; destino pendiente se reintenta) | **pendiente**: reiniciar Windows y mirar `VERIFICAR.bat arranque` |
| Autoarranque | el .bat existe y registra la tarea al iniciar sesión | **pendiente**: instalarlo |
