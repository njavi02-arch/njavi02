# cookgroup v0.8 — resumen corto

## Qué canales descubrí
- **Recorrido completo de la referencia el 20-nov:** 28 categorías y **339 canales** (326 de texto, 9 foros y 4 de voz). En v0.7 había muestreados 112. Tu cuenta puede leerlos todos, pero solo escribir en 9.
- **Nuevo respecto a v0.7:**
  - El foro **#important-releases**: un hilo por lanzamiento, con veredicto, fecha, enlaces de mercado y una respuesta por tienda con su método. Además sugiere palabras clave para el autopinger.
  - Los **roles por reacción**: tipos de aviso, marcas y comunidad autónoma, **sin tallas**.
  - El **autopinger personal** por mensaje privado: palabras, negativas, precio máximo, excluir canal, pausa y destino.
  - Categorías de Pokémon, outlets, market, inversión variada y comunidad.
- **#raffles-europe está inactivo**: su último aviso es del 1-jul-2026.
- La tabla de canales tiene **una fila por canal**, con finalidad, quién lo alimenta, equivalente, qué falta, cómo se prueba, estado y tiendas asociadas. Está en la pestaña «Canales de la referencia» y en `docs/v08/canales.csv`.
  - 217 canales tienen un equivalente en mi diseño.
  - 10 son funciones sin canal propio.
  - 112 no aplican: bots de compra, extensión ajena, market…

## Qué construí
- **Diseño de mi servidor** (`config/servidor.toml`): 8 categorías, 31 canales, permisos y **59 roles** (familias, marcas, regiones y **29 tallas EU**), más las preguntas de bienvenida y textos propios.
- **Instalador repetible** (`INSTALAR_SERVIDOR.bat`): primero enseña la vista previa. No duplica, no borra y no toca tus canales actuales (general, juegos, música). Crea los webhooks y los guarda en tu `.env` sin mostrarlos. Está probado contra un Discord simulado: la segunda ejecución no crea nada.
- **Lote 1 completo (bienvenida, roles y notificaciones):** los roles se convierten en tu perfil y cada aviso se cruza con él.
  - Solo te menciona si encajan familia, marca, envío a España y **tu talla con stock confirmado**.
  - **Una sola mención** aunque el aviso salga en el canal de la tienda y en el agregado.
  - La mención usa `allowed_mentions` con tu usuario: nadie más recibe la notificación.
- **Corrección de reventa:** el beneficio se calcula **talla a talla** sobre las tallas comprables. El aviso dice para qué talla es, con costes y antigüedad de las ventas. El ejemplo del panel que mezclaba ventas de la 43 con tallas disponibles 40, 41 y 42,5 queda corregido, y hay un test que impide repetirlo.

## Qué funciona con datos reales
- **Tu recorrido** usa el catálogo real de Footdistrict leído hoy a las 12:39 (750 productos):
  - Las New Balance 990v7 no tenían la 44,5. Con un cambio controlado vuelve la 44,5 y **recibes la mención**.
  - Vuelve la 44 de las ASICS: el aviso sale en el canal, **sin mencionarte**.
  - También se prueban los silencios: otra marca, tienda solo con stock general, tienda sin envío a España, avisos en pausa y la misma señal en el agregado.
- Las lecturas reales de v0.7 (Footdistrict, Asphaltgold, BSTN, Solebox, Snipes y Chollometro) alimentan los canales de mi servidor que equivalen a 132 canales de la referencia.
- **Ninguna entrega real a Discord todavía.** Los 128 tests y los recorridos usan un Discord simulado.

## Qué depende de una persona o de un permiso
- **Token del bot** (tuyo): hace falta para instalar el servidor, leer los roles de los miembros y crear el canal privado de pruebas con su webhook.
- **Activar «Comunidad»** en tu servidor: sin ella, los foros y las preguntas de bienvenida se crean como texto y queda anotado.
- **Moderación humana:** #tickets, #resultados y #moderación; el flujo está en la guía. El market de compraventa no se construye.
- **Siguientes lotes:** foro de lanzamientos → raffles → restocks por talla en lanzamientos → rebajas. Después LEGO, electrónica y tiendas de Madrid, que son ampliaciones propias sin fuente autorizada todavía.

## La única acción que necesito ahora de ti
- **Crea un bot en el portal de desarrolladores de Discord** e invítalo a «Mi servidor privado» con los permisos Gestionar canales, Gestionar roles y Gestionar webhooks. Activa también «Server Members Intent».
- Pega en el `.env` de tu PC `DISCORD_BOT_TOKEN=…` y `DISCORD_GUILD_ID=1572928642999255120`. Hazlo solo ahí, nunca en el chat.
- Haz doble clic en `INSTALAR_SERVIDOR.bat` y después en `ENVIAR_PRUEBA.bat`. El primer mensaje real irá a #pruebas-bot y te devolverá su ID.
