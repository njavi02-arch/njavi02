# GAME · seguimiento de Pokémon TCG (v1.6, 21-nov-2026)

Qué vigila el monitor `game-es` (canal #game, cada 300 s):
1. **Lista fija** (`watch_urls` en `config/monitors.toml`): se lee en CADA ciclo, aunque no aparezca en ningún listado.
   - Sobre M2 Mega Inferno X (japonés) · 252158 · 9,99 € · agotado el 21-nov
   - Sobre Stellar Miracle (japonés) · 251944 · 7,99 € · agotado el 21-nov
   - Sobre SV9 Juntos de Aventuras (castellano) · 241279 · 5,99 € · agotado el 21-nov
2. **Descubrimiento**: la página pública https://www.game.es/pokemon (sin cookies enlaza ~14 productos Pokémon). Solo
   entran las fichas cuyo enlace contiene «pokemon» y una palabra de TCG (sobre, caja, tin, booster, blister, élite,
   entrenador, cartas…). Videojuegos, figuras, lámparas, vasos, etc. no.

Avisos que recibe un miembro: **vuelta a stock** (cuando GAME pasa la ficha de agotado a disponible), **producto nuevo**
en /pokemon y **bajada de precio**. GAME no publica tallas (no aplica) ni unidades.

## Añadir otra ficha
1. Abre la ficha en game.es y copia la dirección (termina en un número de 5-6 cifras, p. ej. `/…/252158`).
2. En `config/monitors.toml`, dentro de `[[monitor]] name = "game-es"`, añade la URL a `watch_urls` entre comillas y con
   coma al final.
3. Reinicia el bot (o espera al autoarranque). La primera lectura es línea base: no avisa; avisará del siguiente cambio.
4. Comprobación: `pytest tests/test_tiendas_fase2.py -k game` (usa las capturas reales).
