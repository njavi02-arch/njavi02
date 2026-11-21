# Estado v1.1 — 21-nov-2026

## Cifras (cada una con su total)

| Qué | Cifra |
|---|---|
| Tiendas descubiertas (comercios únicos; 422 filas del inventario, 31 con duplicados) | **359** |
| Tiendas con fuente validada (lectura buena o señal probada con datos reales) | **8** |
| Tiendas con canal propio diseñado (lote 1) | **10** |
| Tiendas instaladas en Discord | **0 / 10** (falta el token del bot) |
| Tiendas con entrega verificada en Discord | **0 / 10** |
| Canales de la referencia investigados | **339 / 339** |
| Canales de la referencia desarrollados | **81 / 339** |
| Canales de la referencia probados en local | **111 / 339** |
| Canales de la referencia instalados | **0 / 339** |
| Canales de la referencia verificados | **0 / 339** |
| Los 47 que iban a #sneakers-eu | 47/47 resueltos uno a uno · 9 probados · 18 desarrollados · 20 investigados |
| Los 28 de #pokémon-tcg | 28/28 resueltos · 15 probados · 2 desarrollados · 11 investigados |
| Los 112 sin equivalente | 31 con canal nuestro · 1 probado · 25 desarrollados · 86 investigados (de estos, la mayoría depende de un acuerdo con terceros o de una decisión tuya) |

## Criterio de los estados

**«Probado en local»** exige una prueba automática con una captura real de la tienda. Que el bot lea la tienda (COMPROBAR.bat) ya no basta: v1.0 sí lo contaba como prueba.

Por eso han bajado algunos canales que en v1.0 figuraban como probados: ahora solo cuentan los que de verdad tienen prueba.

## BSTN, de principio a fin

**Canales**
- #raffles-bstn, más la etiqueta RAFFLE en #bstn, el agregado #raffles y #raffles-cierran-hoy (hora de Madrid).

**Avisos**
- Una sola mención por miembro.
- En el primer arranque, el catálogo existente se registra en silencio.
- Tras un reinicio no se repite ningún aviso.
- Si el plazo cambia o el raffle cierra, se edita la ficha original.

**Lectura**
- BSTN se lee cada 60 s (±10 %, arranques escalonados).
- Usa lectura condicional (304), así que no se vuelve a descargar lo que no ha cambiado.
- Si BSTN pide esperar (429 / Retry-After), espera.

**Tiempos por mensaje**
- Detección, envío y hora de Discord, más el enlace directo al mensaje.
- La hora de publicación de BSTN no se guarda porque BSTN no la da.

**Fuente en tiempo real**
- BSTN solo ofrece notificaciones dentro de su app; no he encontrado ninguna vía «push» para terceros.

## Fase

**Pruebas internas.**

Para pasar a beta privada faltan:
1. El token del bot y la instalación del servidor.
2. La prueba real en #pruebas-bot.
3. Un primer raffle real entregado en #raffles-bstn.
4. Un ordenador encendido 24/7.

Los cobros reales y la apertura al público siguen pendientes de tu autorización.
