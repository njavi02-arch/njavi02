# BULLET OPS — Progress Tracker

Sesión autónoma extendida, modo agente completo. 24 commits en `claude/bullet-ops-fps-game-jizk2k`, artifact republicado en cada hito con build funcionando. Nada quedó "en progreso" a medio hacer — cada bloque se cerró probado con el juego real (Playwright) antes de pasar al siguiente. Los 3 puntos del "siguiente paso" de la revisión anterior (cobertura de bots, arsenal completo, selección de loadout) están terminados y probados.

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

### Arsenal — plantilla validada en las 6 categorías
Añadidas `BO-21 BREACHER` (Shotgun), `BO-31 LONGSHOT` (Sniper), `BO-41 JUGGERNAUT` (LMG) a `WEAPON_CONFIGS`, cada una con personalidad propia (Shotgun: alto daño/corto alcance/spread amplio; Sniper: casi un solo tiro, ADS lentísimo con FOV muy reducido, **recoil fuerte pero lento** tal como se pidió explícitamente — recoverySpeed 2.5 vs. 7 del AR; LMG: cargador de 75, movilidad reducida). Probado con un `WeaponController` temporal equipando las 6 armas a la vez: todas disparan, generan su propio viewmodel (con nº de meshes distinto por categoría), consumen su propia munición y aplican su propio recoil sin ningún cambio de código adicional — confirma que la arquitectura escala. Aún no forman parte del loadout de 3 armas por defecto (eso es Fase 9, selección de loadout).

### FASE 4 — Mapas (arrancada)
`OUTPOST-9`: mapa original de filosofía competitiva (bases enfrentadas simétricas, 3 carriles — centro con torre de control/atalaya, dos flancos — con huecos para rutas alternativas entre carriles). Blockout con las mismas primitivas/`checkCollisions` ya probadas. Tercer botón de mapa en el menú. Probado: colisión exacta contra la pared de la base, navegación libre por el carril central, bots activos sin errores durante 6s, captura de pantalla verificada visualmente.

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
| **Disparos nivelados a un objetivo estático a la misma altura fallaban** (a veces) | El cañón dispara desde Y≈1.5 (altura de cámara), pero el chequeo de impacto comparaba contra `entity.mesh.position` (Y=1, un único punto) con radio fijo 0.5 — la distancia real era 0.5006, justo por encima del umbral. El chequeo nunca modelaba la extensión vertical real de la cápsula (0.1 a 1.9) | Comparar el segmento recorrido por la bala contra el **segmento vertical (núcleo) de la cápsula del objetivo**, no contra un punto único — arreglo correcto (no solo agrandar el radio), también mejora headshots y objetivos agachados |

**Nota sobre el bug de hit detection**: no fue introducido por el nuevo sistema de armas — el mismo hueco vertical (origen de bala ~0.7 por encima del punto de referencia) ya existía en el `fire()` original, simplemente ninguna prueba anterior había disparado un tiro nivelado de verdad contra un objetivo inmóvil a distancia normal para revelarlo. Se encontró en una pasada de regresión amplia sobre TODO el juego (no solo lo nuevo de esta sesión), siguiendo la regla de "corrige antes de añadir".

---

### FASE 7 — Menús (en curso: LOADOUT, WEAPONS y OPERATORS funcionales; quedan CUSTOMIZE/SETTINGS)
Menú principal ampliado con las 5 secciones del roadmap (LOADOUT/WEAPONS/OPERATORS/CUSTOMIZE/SETTINGS) como botones **genuinamente deshabilitados** (atributo `disabled`, no solo con estilo de bloqueado), marcados "🔒 Próximamente" — un click no hace absolutamente nada, no aparentan funcionar. Verificado que no interfieren con PLAY ni con el resto del menú. Desde entonces LOADOUT, WEAPONS y OPERATORS se fueron habilitando uno a uno (ver más abajo); CUSTOMIZE y SETTINGS siguen bloqueados.

### FASE 7 — Pantalla WEAPONS (catálogo de las 15 armas, completa)
Botón WEAPONS (antes bloqueado) ahora abre un catálogo con scroll: `renderWeaponsScreen()` agrupa `WEAPON_CONFIGS` por categoría en orden fijo (AR/SMG/Shotgun/Sniper/LMG/Pistol), con cabecera por categoría y una fila por arma mostrando DMG/RoF/MAG/RNG leídos directamente de la config — cero datos duplicados a mano. Probado con Playwright: las 15 armas aparecen, agrupadas correctamente, y los valores mostrados coinciden con `WEAPON_CONFIGS`.

### FASE 7 — Pantalla OPERATORS (identidad de jugador, completa)
Sin modelos 3D de personajes disponibles todavía, OPERATORS se implementó como sistema de identidad **funcional**, no cosmético falso: `OPERATOR_REGISTRY` (6 operadores, cada uno con `callsign` + color propio), pantalla con selector ◀/▶, swatch de color y nombre, elección persistida en `localStorage` (`bulletOpsOperator`) igual que el loadout. El callsign se usa en el killfeed de FFA; el color se aplica al material de la cápsula del jugador **solo en FFA/sin equipo** — en TDM el color de equipo (azul/rojo) sigue teniendo prioridad absoluta por legibilidad, tal como ya ocurría antes.

Probado de extremo a extremo con Playwright, verificando el criterio explícito de "cambiar de operador cambia de verdad el color en partida":
- Ciclar con ◀/▶ actualiza nombre y swatch en pantalla, y persiste en `localStorage` (confirmado tras recargar la página, el operador elegido se recarga correctamente al arrancar).
- Iniciando una partida FFA real, `player.mesh.material.diffuseColor` coincide exactamente con el color del operador elegido (antes todos los jugadores FFA eran del mismo amarillo plano) y `player.callsign` coincide con el nombre del operador.
- Regresión TDM: con el mismo operador elegido, una partida TDM sigue asignando el color de equipo (azul/rojo) al material, no el color del operador — confirma que la prioridad de equipo no se rompió.
- Cero errores de consola durante todo el flujo.

### FASE 7 — Pantalla SETTINGS (sensibilidad, volumen, invertir eje Y — completa)
Última sección de Fase 7 que no dependía de ningún asset. `gameSettings` (`sensitivity`, `invertY`, `volume`) persistido en `localStorage` (`bulletOpsSettings`) igual que loadout/operador, con botón de reset a valores por defecto. Tres efectos reales, no solo UI decorativa:
- **Sensibilidad**: multiplica directamente la fórmula de mouse-look ya existente (`0.001 * gameSettings.sensitivity * getSensitivityMultiplier()`), así que sigue respetando la reducción de sensibilidad al hacer ADS por arma.
- **Invertir eje Y**: se añadió como un flip de signo condicional sobre la MISMA línea que ya tenía el fix explícito de inversión del pitch de esta sesión (`this.pitch += (gameSettings.invertY ? 1 : -1) * inputs.mouseY * sensitivity`) — no se tocó el convenio de signos ya corregido, solo se hizo el signo opcional.
- **Volumen**: `SoundSynth` ahora enruta todos los sonidos por un `GainNode` maestro (antes cada sonido conectaba directo a `ctx.destination`); el volumen guardado se aplica como valor inicial al crear el contexto de audio y `SoundSynth.setVolume()` lo actualiza en caliente si el jugador cambia el slider durante la sesión.

Probado con Playwright: mover los sliders actualiza el estado y `localStorage` en vivo; tras recargar la página los tres valores se mantienen; con `invertY=true` y sensibilidad `2.5x`, una llamada directa a `player.update()` con `mouseY=10` produce un delta de pitch de exactamente `+0.025` (signo invertido respecto al comportamiento normal, y magnitud que coincide con la sensibilidad configurada) — confirma matemáticamente que ambos ajustes se aplican correctamente, no solo visualmente. Cero errores de consola.

### Mecánica: retraso de disparo al salir de sprint (completa)
`sprintToFireDelay` existía como campo en las 15 configs de `WEAPON_CONFIGS` desde el principio (parte del diseño original del sistema de armas), pero nunca se leía en ningún sitio — dato muerto, la mecánica no tenía ningún efecto real. Implementado en `WeaponController`: mientras se está esprintando, `sprintRecoveryTimer` se mantiene fijado al valor completo del arma; al dejar de esprintar empieza a bajar, y el disparo (tanto tiro real como click en vacío) queda bloqueado hasta que llega a 0 — un arma más pesada (LMG/Shotgun) tarda más en "recuperarse" que una SMG/Pistola, respetando el valor ya configurado por arma. Probado con Playwright llamando directamente a `WeaponController.update()`: al esprintar se arma el temporizador exactamente al `sprintToFireDelay` del arma (BO-01: 0.15s), un intento de disparo inmediato tras dejar de esprintar queda bloqueado (munición sin cambios), y el disparo se desbloquea correctamente pasado ese tiempo (disparo real confirmado a los 0.16s, prácticamente exacto). Cero errores de consola.

### IA de bots — variedad de armamento (completa)
Cada bot llevaba siempre el mismo trío fijo (`BO01`/`BO51`/`BO11`), sin importar que el arsenal completo tuviera 15 armas — un vestigio del prototipo original de antes del sistema de armas completo. Corregido con `pickRandomBotLoadout()` (Fisher-Yates parcial sobre `WEAPON_CONFIGS`): cada bot recibe ahora 3 armas distintas elegidas al azar de las 15, con las mismas probabilidades para todas. Probado con Playwright en una partida FFA real: los 3 bots spawneados llevaban loadouts distintos entre sí y ninguno coincidía con el trío fijo anterior (ej. un bot con Shotgun+AR+Pistol, otro con Sniper+AR+SMG), combate de 8s sin errores de consola y con bajas reales (2/3 bots sobrevivientes) — confirma que el sistema de disparo de bots funciona igual de bien con cualquiera de las 6 categorías de arma, no solo con las 3 originales.

### FASE 6 — Pantalla de resultados (pulido)
`endGame()` usaba `alert()` nativo (bloquea toda la página hasta que se cierra) para mostrar resultados. Sustituido por una pantalla `#resultsScreen` propia (mismo estilo visual que el menú de pausa): título con ganador/color de equipo o "VICTORY" en FFA, marcador final, kills/deaths/K/D/tiempo de partida, botón "Back to Menu". Cursor liberado al mostrarla. Empezado a usar `GameState.ENDED`, que existía en el enum pero nunca se usaba. Probado en TDM y FFA con captura de pantalla — sin diálogo bloqueante, formato correcto en ambos modos.

### FASE 5 — Cobertura de bots (completa)
`findCoverPosition()`: función genérica que busca el obstáculo más cercano y calcula un punto al otro lado respecto a la amenaza — funciona igual en los 3 mapas sin código específico por mapa (solo usa meshes con `checkCollisions`). Un bot con <40% de vida o recargando, con un objetivo a <40 unidades, se retira hacia ese punto en vez de avanzar en línea recta (sigue devolviendo fuego si no está recargando). Episodio de 3.5s o hasta llegar/curarse. Solo se calcula al iniciar el episodio, no cada frame. Probado: un bot herido cambia de rumbo medible hacia su punto de cobertura en vez de hacia el jugador; se cura y dejar de buscar cobertura; 3 bots heridos a la vez durante 8s sin errores.

### Arsenal completo — 15/15 armas (3 AR, 3 SMG, 3 Pistol, 2 Shotgun, 2 Sniper, 2 LMG)
Las 9 armas que faltaban añadidas a `WEAPON_CONFIGS`, cada una con rol distinto dentro de su categoría (ej. AR: VANGUARD equilibrado / PREDATOR preciso-lento / STORMCALLER rápido-impreciso). Cero cambios de arquitectura necesarios — se instanció un `WeaponController` con las 15 a la vez y las 15 disparan y gestionan su propia munición correctamente.

### FASE 9 — Selección de Loadout (completa)
El botón LOADOUT (antes bloqueado) ahora es funcional de verdad: pantalla con 3 slots, cada uno cicla entre las 15 armas del catálogo. Elección guardada en `localStorage`, sobrevive a recargar la página. `Player` ahora construye su `WeaponController` con `currentLoadout` en vez de un array fijo. Probado de extremo a extremo: elegir un Sniper en el slot 1 → recargar página → la elección persiste → empezar partida → el arma equipada en la ranura 1 es el Sniper elegido → pulsar "1" en partida efectivamente la equipa.

### Optimización — fuga de materiales por disparo (corregida)
Cada bala (jugador y bot) y cada muzzle flash creaba su propio `StandardMaterial` nuevo con `dispose()` del mesh al final de su vida — pero `mesh.dispose()` **no libera su material** por defecto, así que cada disparo dejaba uno o dos materiales huérfanos en memoria para siempre (crítico de cara a partidas largas o multijugador). Corregido con tres materiales compartidos y creados de forma perezosa (`getSharedBulletMaterial` para bala de jugador/bot, `getSharedMuzzleFlashMaterial`), reutilizados en cada disparo en vez de crear uno nuevo cada vez. Verificado contando materiales vivos en el motor con Playwright: antes del fix crecían sin límite disparo a disparo; después, el conteo se estabiliza tras la primera creación perezosa (14→17 en 20 disparos, atribuible solo a la creación única de los 3 compartidos; 14→15 tras 10s de combate continuo con varios bots). De paso se descartó una hipótesis alternativa (que `ParticleSystem.dispose()` pudiera liberar la textura compartida de partículas) tras confirmar empíricamente que la textura sigue siendo válida después de 15 ciclos de dispose.

---

## 🔧 SIGUIENTE PASO (para retomar la sesión)

Nada quedó a medias. LOADOUT, WEAPONS, OPERATORS y SETTINGS ya son funcionales. Por orden de prioridad según el roadmap original, lo que sigue:

1. **Fase 7 (Menús)**: solo queda 1 sección bloqueada (CUSTOMIZE) — tiene más sentido una vez haya más de un skin real por arma (combinar skin + operador visualmente todavía no aporta mucho con un único skin sólido por defecto y un patrón "digital" de prueba).
2. **Fase 10 (Multiplayer)**: explícitamente "solo cuando el prototipo offline sea estable" — dado que Fases 0-2, 4-9 están sólidas y probadas, es razonable empezar a planificar la arquitectura cliente/red sin tocar lo existente.
3. **Mapas**: un segundo mapa original si se prioriza más contenido, o pase de arte sobre los 3 existentes cuando haya assets reales.
4. **Attachments**: la arquitectura (`ATTACHMENT_SLOTS`, `getEffectiveWeaponStats()`) está lista pero vacía — implementarlos requiere decidir su representación visual, que a su vez depende de tener modelos 3D reales (no tiene sentido un attachment procedural sobre un arma procedural).

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
