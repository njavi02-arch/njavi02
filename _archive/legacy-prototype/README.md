# Prototipo Vite abandonado (Fase 1, 2026-09-10)

Este directorio contiene el primer intento de BULLET OPS: un scaffold
multi-archivo basado en Vite (`package.json`, `vite.config.js`) con
`index.html` / `play.html` como puntos de entrada y una mini-arquitectura
en `src/` (`ai/`, `core/`, `game/`, `map/`, `player/`, `ui/`, `weapons/`).

**Se abandonó el mismo día que se creó** (10 sept 2026) a favor de
`bullet-ops-game.html` en la raíz del repo: un único archivo HTML
autocontenido (Babylon.js 7.x, modelos procedurales, texturas Canvas2D,
audio sintetizado en tiempo real), publicado como Claude Artifact. Todo
el desarrollo real de BULLET OPS desde esa fecha vive exclusivamente en
ese archivo.

## Por qué sigue aquí

Auditado el 14 sept 2026: no hay ninguna referencia cruzada entre este
prototipo y `bullet-ops-game.html` en ninguna dirección. Se conserva por
historial en vez de borrarse, pero **no forma parte del juego actual y
no debe editarse** como parte del desarrollo activo.

- `game.js` solo define 2 armas de ejemplo (`BO01`, `BO41`) frente a las
  68 del juego real.
- `src/weapons/weapons-config.js` y `src/weapons/WeaponManager.js` son
  la versión temprana del sistema de armas, superada por
  `WEAPON_CONFIGS`/`WeaponController` en `bullet-ops-game.html`.
