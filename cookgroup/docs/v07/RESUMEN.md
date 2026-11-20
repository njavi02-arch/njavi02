# cookgroup v0.7 — resumen corto

## Funciona hoy
- **260 monitores** cargan sin errores (`cookgroup check-config`): 30 a mano + 230 del CSV. El README de v0.6 decía 262 por un error de suma; corregido.
- **Lectura real el 20-nov (12:08–12:10, Madrid)** de 6 fuentes del piloto: Footdistrict y Asphaltgold (250 productos cada una), BSTN (17 lanzamientos, 2 raffles abiertos), Solebox (44 fichas), Chollometro (30 chollos) y Snipes, que tenía la URL rota (404) y ya está corregida.
- **Los avisos no se pierden si Discord cae.** En v0.6 se guardaba la instantánea antes de enviar y un fallo de Discord borraba el aviso para siempre (reproducido con `tools/repro_v06_perdida.py`). Ahora el aviso se guarda primero en una bandeja, solo se marca como enviado cuando Discord devuelve el id, y sobrevive a reinicios sin duplicarse.
- **El diagnóstico ya no dice «OK» con 0 productos.** Distingue ÚTIL, SIN COINCIDENCIAS, VACÍA, SIN CAMBIOS, LIMITADA y FALLO; anota por fuente la hora de Madrid, los leídos, los válidos, una variante de ejemplo, el último envío y la causa del fallo; saca un CSV para Excel; permite probar unas pocas fuentes y reanudar el lote.
- **PROBAR.bat se ha dividido en tres:** COMPROBAR.bat (solo lee), ENVIAR_PRUEBA.bat (1 mensaje de PRUEBA) y VER_PANEL.bat (este panel). ESTADO.bat dice si el proceso está vivo y si cada fuente va retrasada respecto a su propio intervalo.
- **El beneficio solo se publica verificado:** hacen falta 3 o más ventas cerradas en 30 días de la misma referencia, talla, estado (nuevo) y mercado, en EUR, con envío a España confirmado. Si no, el aviso dice «beneficio sin verificar» y el motivo. El margen sobre la venta y el ROI sobre la compra se muestran por separado.
- **Los 2 lanzamientos del calendario quedan fuera de los avisos automáticos** hasta tener una fuente oficial. Nike Mind 001 HQ4307-001 ya salió en 2026 y la fecha del 20-nov parece un error. El AF1 Travis × GTA VI tiene un raffle abierto en BSTN, que ya se vigila, pero Nike no lo publica todavía.

## Solo probado con muestras
- El piloto completo, de la captura al aviso, pasa los 9 pasos, pero con el catálogo real de Footdistrict servido en local, cambios aplicados a propósito (vuelve la talla 44 y el precio baja de 280 a 224 €) y un **Discord simulado** que se tumba y se levanta.
- Los ejemplos de BSTN y Chollometro del panel son capturas del 19-nov; los de raffle que cierra, fecha cambiada, price error y beneficio verificado son simulaciones.
- Los 122 tests se ejecutan sin webhook.

## Falta
- **Ningún mensaje confirmado en un Discord real** (no hay webhook de pruebas configurado).
- Una lectura del bot en marcha en tu PC durante horas, con el registro de ESTADO.
- Datos de ventas cerradas en `config/market_data.json`: sin ellos todos los avisos dicen «beneficio sin verificar».
- Lote 1 de expansión: SVD (Chrome no dio permiso para leerla), Basketballemotion (el listado se carga con JavaScript) y AW LAB (sin datos estructurados). 24Segons está lista para añadir, con cobertura parcial y sin tallas.
- Siguientes lotes: streetwear, TCG, LEGO, electrónica, distribuidores de colaboraciones y tiendas físicas de Madrid; retomar el historial de la referencia.

## Qué necesito hacer yo
- **Una sola acción para el mensaje real:** crea un webhook en un canal **privado** de pruebas de tu servidor de Discord, pégalo en el fichero `.env` como `DISCORD_WEBHOOK_DEFAULT=...` (solo en tu PC, nunca en el chat) y haz doble clic en `ENVIAR_PRUEBA.bat`. Te devolverá el id del mensaje.
- Opcional: `COMPROBAR.bat piloto` para que el propio bot repita en tu PC la lectura de las 6 fuentes.
- Autoarranque, hosting de pago y apertura a clientes: lo decidimos después de ver el piloto.
