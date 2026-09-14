# BULLET OPS

Shooter arcade competitivo en primera persona, construido íntegramente en
Babylon.js 7.x como **un único archivo HTML autocontenido**: sin build,
sin dependencias locales, sin assets externos (modelos, texturas y sonido
son 100% procedurales/sintetizados en tiempo real).

## Jugar

Abrí `bullet-ops-game.html` en un navegador. Las dependencias (Babylon.js)
se cargan desde CDN; no requiere instalación ni servidor.

## Documentación

- `MASTER_INDEX.md` — índice maestro de progreso y próximas tareas.
- `BULLET_OPS_PROGRESS.md` — historial técnico detallado de cada cambio.
- `docs/WEAPON_BIBLE.md` — auditoría maestra del sistema de armas (68 armas).
- `docs/WEAPON_ASSET_BACKLOG.md` — backlog de tickets de assets/VFX por arma.
- `docs/WEAPON_ASSET_MAP.md` — mapa de nomenclatura y organización interna
  del sistema de armas (convención de nombres, categorías, dónde vive cada
  pieza dentro del archivo).
- `docs/weapons.json` — espejo de datos de `WEAPON_CONFIGS` para consulta.

## Arquitectura

Todo el juego vive en `bullet-ops-game.html`. Esto es una decisión
deliberada (permite publicarlo como Claude Artifact de un solo archivo) y
se mantiene así intencionalmente: no se reestructura a multi-archivo.

`_archive/` contiene un prototipo Vite temprano y abandonado, sin
relación con el juego actual (ver `_archive/legacy-prototype/README.md`).
