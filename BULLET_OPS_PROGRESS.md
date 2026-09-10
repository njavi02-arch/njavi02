# BULLET OPS — Progress Tracker

Sesión autónoma en curso (trabajo continuo hasta revisión a las 19:00). Este archivo se actualiza durante el desarrollo, no solo al final.

---

## ✅ COMPLETADO

### FASE 0 — Estabilidad
- Bug prioritario (click PLAY requería ESC + reinteracción para responder): causa real era que el pointer lock se pedía desde un listener global de `mousedown` en `document` apuntando a `document.documentElement`, disparándose con cualquier click (incluido el propio botón PLAY) en carrera con el momento de ocultar el menú. Corregido con una máquina de estados única (`MENU/PLAYING/PAUSED/ENDED`) que pide el lock explícitamente sobre `canvas` al arrancar la partida.
- Menú de pausa real: ESC ahora pausa de verdad (libera cursor, congela lógica), Resume vuelve a capturar el cursor y da control inmediato.
- Colisiones con paredes/obstáculos: `scene.collisionsEnabled=true` no tenía efecto porque ningún mesh tenía `checkCollisions` y el movimiento usaba `position.addInPlace()` en vez de `moveWithCollisions()`. Jugador y bots atravesaban todo; corregido.
- Munición no se reseteaba al cambiar de arma (bug del prototipo original) — corregido, y luego sustituido por completo por munición persistente por arma en el nuevo `WeaponController`.
- Hit detection con "tunneling": balas rápidas (hasta 900 u/s) podían saltar por encima de un objetivo en un solo frame sin registrar impacto. Corregido comprobando el punto más cercano en todo el segmento recorrido ese frame, no solo la posición final.
- Salto de cámara al respawnear: el movimiento del mouse durante los 2-3s de espera de muerte se acumulaba sin consumirse. Corregido consumiendo el delta una vez por frame de forma incondicional.
- Space hacía scroll de página — `preventDefault()` en teclas de juego.
- Crouch no existía pese a estar en el checklist — implementado (agachado, -50% velocidad, sin sprint, transición suave).
- **Eje vertical del ratón invertido** (reportado explícitamente): confirmado empíricamente que `camera.rotation.x` en Babylon.js usa el convenio opuesto ("positivo = mirar abajo") al que usa el resto del código (`sin(pitch)` en disparo/recoil, "positivo = mirar arriba"). Corregido negando el pitch SOLO en la asignación final a `camera.rotation.x`, sin tocar el resto del sistema (verificado explícitamente que el eje horizontal ya era correcto y que el comportamiento se mantiene igual tras ESC→Resume).
- Listeners `keydown` duplicados — consolidados en uno.

### FASE 1 — FPS Core
Movimiento, sprint, salto, agachado, cámara/mouse look, cursor, vida, daño, muerte, respawn — verificado con pruebas Playwright reales contra el juego ejecutándose (no solo lectura de código).

### FASE 2 — Sistema de Armas (arma patrón funcionando de extremo a extremo)
Arquitectura completa y funcional, construida y probada en este orden:

1. **`WEAPON_CONFIGS`** — estructura de datos única por arma (daño, headshotMul, fireRate, mag/reserve, reloadTime/reloadTimeEmpty, spread{hip,ads,moving}, range, bulletSpeed, ads{time,fovMul,sensitivityMul}, movement{hipMul,adsMul}, sprintToFireDelay, recoil{vertical,horizontal,cameraKick,recoverySpeed}, sway{amount,speed,bobAmount,bobSpeed}, soundProfile, defaultSkin, attachmentSlots). Ningún valor de arma queda suelto por el código.
2. **Nomenclatura de armas** (investigado y decidido, ver "Decisiones técnicas"): códigos ficticios `BO-XX` por categoría, sin copiar nombres/marcas reales.
3. **`SoundSynth`** — disparo, recarga (mag-out/mag-in), vacío, equipar, hitmarker, headshot, kill confirm. Todo sintetizado en runtime con Web Audio API (osciladores + ruido filtrado), cero archivos externos.
4. **`SKIN_REGISTRY` + `applySkin()`** — sistema de camuflajes data-driven, incluye un patrón "digital" generado por código con `DynamicTexture`.
5. **`buildWeaponViewmodel()`** — arma en primera persona procedural (siluetas distintas por categoría: AR/SMG/Pistol/Shotgun/Sniper/LMG), renderizada con `renderingGroupId=1` + auto-clear de profundidad para no atravesar paredes cercanas.
6. **`WeaponController`** — máquina de estados IDLE/RELOADING/SWITCHING por jugador: disparo, recoil (patrón + kick visual + bloom de precisión, separados), ADS (FOV/sensibilidad/posición suavizados), reload (normal vs. desde vacío), weapon switching (con bloqueo de disparo durante la transición, verificado). Munición ahora persiste POR ARMA al cambiar (antes se reseteaba).
7. **Muzzle flash / impactos** — partículas con una textura compartida generada en runtime (sin asset externo), headshot visual y sonoramente distinto.
8. **`ATTACHMENT_SLOTS` + `getEffectiveWeaponStats()`** — arquitectura de attachments lista (identidad hasta que se añadan attachments reales), sin implementarlos todavía (según instrucción explícita).
9. Botón derecho = ADS (antes sin uso), menú contextual del navegador suprimido en el canvas.
10. Bots migrados a la nueva estructura de datos (siguen usando disparo simple, sin ADS/viewmodel, comparten `WEAPON_CONFIGS` para que el daño/cadencia sea consistente con el jugador).

**Bug encontrado y corregido durante esta fase**: el viewmodel del arma no se veía en absoluto (pantalla vacía donde debería estar el arma). Diagnosticado con capturas de pantalla reales, no solo lectura de código: la cámara tenía `minZ=1` (plano de recorte cercano por defecto de Babylon) pero el arma estaba a ~0.3-0.5 unidades — se recortaba por completo. Corregido con `camera.minZ = 0.05`.

**Ajuste de diseño durante esta fase**: la posición de ADS inicial centraba completamente el arma frente a la cámara, y al ser geometría de bloques sin mira real, tapaba casi toda la pantalla (confirmado con captura: pantalla negra). Se ajustó para que quede ligeramente descentrada (como en la mayoría de shooters arcade) dejando que el zoom de FOV aporte la sensación de apuntado — es una limitación conocida del placeholder, se resolverá con un modelo real con mira modelada.

---

## 🐛 BUGS ENCONTRADOS Y SOLUCIONADOS (esta sesión completa)

| Bug | Causa | Fix |
|---|---|---|
| Click PLAY no respondía hasta ESC + reinteracción | Pointer lock pedido desde listener global de mousedown, mal targeteado | Máquina de estados única, lock explícito en canvas al iniciar partida |
| Jugador/bots atravesaban paredes | `checkCollisions` nunca activado en ningún mesh | `checkCollisions=true` en obstáculos + `moveWithCollisions()` |
| Munición no se reseteaba al cambiar de arma | Variable única no por arma | Ahora `WeaponController.ammo` por arma, persistente |
| Balas rápidas atravesaban objetivos sin dañar | Test de colisión solo en punto final del frame | Test contra el segmento completo recorrido |
| Salto de cámara al respawnear | Delta de mouse no se reseteaba durante la muerte | Reset incondicional una vez por frame en `updateGame()` |
| Space hacía scroll de página | Sin `preventDefault` | Añadido para teclas de juego |
| Eje vertical de ratón invertido | Convenio de signo opuesto entre `camera.rotation.x` (Babylon) y `pitch` (resto del código) | Negación aislada solo en la asignación final |
| Viewmodel del arma invisible | `camera.minZ=1` recortaba el arma (a 0.3-0.5u) | `camera.minZ=0.05` |
| ADS tapaba toda la pantalla (negro) | Arma centrada sin mira real, geometría de bloque | Posición ligeramente descentrada + más distancia |
| 2 listeners `keydown` duplicados | Redundancia de una corrección anterior | Consolidados en uno |

---

## 🔧 EN PROGRESO / SIGUIENTE PASO

Nada en progreso activo ahora mismo entre commits — cada bloque se cerró probado y funcionando antes de seguir. **Siguiente paso concreto**: duplicar la plantilla `WeaponController`/`WEAPON_CONFIGS` para poblar el resto del arsenal (2 AR más, 3 SMG total, 2 shotgun, 2 sniper, 2 LMG, 3 pistolas) usando BO-01 VANGUARD como plantilla ya validada, ajustando solo los números de stats y el perfil de sonido/recoil por categoría — la arquitectura ya soporta esto sin cambios estructurales.

---

## 📦 ASSETS NECESARIOS (nada de esto bloquea el desarrollo — placeholders funcionando mientras tanto)

**PARA ARMAS** (por cada una de las 15 del arsenal, empezando por BO-01 VANGUARD como prioridad):
- Modelo 3D en primera persona (viewmodel) — **formato GLB**, poli bajo/medio.
- Animaciones embebidas en el GLB: disparo (recoil del modelo), recarga (normal + desde vacío), equipar.
- Sonido de disparo real por arma — WAV.
- Sonido de recarga — WAV/MP3.
- Textura/material base — PNG.

**PARA MAPAS** (cuando se retome Fase 4):
- Concepto o plano 2D con spawns, chokepoints, verticalidad (blockout se construye sin más assets).
- Fase de pulido posterior: props 3D (GLB), texturas de superficies (PNG/JPG), skybox (HDR o 6 caras JPG).

**PARA CAMUFLAJES**:
- Solo necesarios para camuflajes con patrón: textura tileable PNG. Los sólidos/metálicos/especiales no necesitan ningún asset (son material/shader por código).

**Todo lo anterior tiene placeholder funcional ahora mismo** (viewmodel procedural, sonido sintetizado, skins de color sólido + un patrón generado por código) — nada de esto detiene el desarrollo.

---

## 🧠 DECISIONES TÉCNICAS IMPORTANTES

- **Arquitectura de archivo**: se mantiene un único `bullet-ops-game.html` (no módulos ES / múltiples archivos) porque es lo que el entorno de Artifact puede publicar y servir de forma fiable (ya probado extensamente en sesiones anteriores, incluyendo problemas previos con carga de módulos). La modularidad se consigue con clases/objetos bien encapsulados dentro del archivo (`WeaponController`, `SoundSynth`, `SKIN_REGISTRY`, etc.), no con separación física de archivos.
- **Nomenclatura de armas — investigación y decisión**: juegos con acuerdos de licencia (COD, Battlefield) usan nombres/marcas reales de fabricantes; juegos sin esos acuerdos (Valorant, Apex, Overwatch, Fortnite) usan nombres 100% ficticios con armas visualmente "inspiradas" en categorías reales sin copiar el diseño exacto de ningún fabricante — evita riesgo de marca registrada sin necesitar un acuerdo de licencia. BULLET OPS sigue este segundo enfoque: códigos `BO-XX` por rango de categoría (01-09 AR, 11-19 SMG, 21-29 Shotgun, 31-39 Sniper, 41-49 LMG, 51-59 Pistola).
- **Sonido**: sintetizado 100% por código vía Web Audio API (osciladores + ruido filtrado), sin descargar ningún archivo de audio externo — evita cualquier problema de copyright, cumple la instrucción explícita de no usar sonidos de licencia dudosa.
- **Viewmodel (brazos/arma en primera persona)**: geometría procedural (primitivas Babylon combinadas por categoría), sin modelo 3D todavía. Renderizado con `renderingGroupId=1` + auto-clear de profundidad para que nunca atraviese paredes cercanas, técnica equivalente a la cámara de arma dedicada de un FPS real. Munición/recoil/ADS ya funcionan de forma completamente independiente del modelo visual, así que sustituir esta geometría por un GLB real más adelante no debería requerir tocar `WeaponController`.
- **Munición por arma**: se cambió de "resetear al máximo al cambiar de arma" (comportamiento arcade simplificado del prototipo) a "persistente por arma, solo la recarga la cambia" — más correcto y más "serio", sin coste de complejidad relevante.
- **Camuflajes**: registro de skins data-driven; añadir uno nuevo = una entrada en `SKIN_REGISTRY`, cero cambios en el código del arma. Incluye un camuflaje "digital" generado por código con `DynamicTexture` (patrón dibujado, no descargado) como prueba de que el sistema soporta patrones, no solo colores sólidos.
- **Attachments**: arquitectura lista (`ATTACHMENT_SLOTS`, `getEffectiveWeaponStats()` como identidad) pero sin poblar — según instrucción explícita de no implementarlos todos ahora mismo.

---

## 🧪 METODOLOGÍA DE PRUEBAS

Todo lo anterior se verificó **ejecutando el juego real** (Babylon.js servido localmente vía `node_modules/babylonjs/babylon.js`, ya que el proxy de este entorno bloquea el CDN de cdnjs) con Playwright headless: simulando clicks/teclado/mouse reales, leyendo estado del motor en vivo, y tomando capturas de pantalla para verificar visualmente (así se encontraron los bugs de `minZ` y de ADS tapando la pantalla, que no eran detectables solo leyendo el código). No se marcó nada como "hecho" sin antes reproducirlo, corregirlo y volver a probarlo.
