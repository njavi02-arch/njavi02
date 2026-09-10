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

### Mecánica: alcance real por arma (completa)
`range` era otro campo definido en las 15 configs (y mostrado en la pantalla WEAPONS) que nunca se aplicaba de verdad — toda bala vivía hasta su `life = 10` segundos sin importar el arma, así que un Sniper (rango 200) y una SMG (rango 55) alcanzaban exactamente igual de lejos en la práctica. Cada bala ahora guarda `maxRange` (del arma que la disparó) y acumula `distanceTraveled` cada frame; al superar `maxRange` expira en silencio (sin efecto de impacto, sin daño) igual que si hubiera salido del mapa. Aplicado tanto a balas del jugador como de bots. Probado con Playwright: con los bots teleportados lejos (para aislar el comportamiento de cualquier posible impacto), una bala de BO-01 (rango 100) recorrió 97.47 unidades y desapareció del array de balas en el siguiente muestreo — justo en el borde de su rango configurado, no a los miles de unidades que hubiera recorrido antes en sus 10s de vida. Cero errores de consola.

### Mecánica: multiplicador de headshot por arma (completa)
El daño de headshot usaba un `2.0` fijo para las 15 armas, ignorando el `headshotMul` propio de cada una (definido desde el principio con valores intencionalmente distintos: 1.2 para Shotguns hasta 2.2 para Sniper/Magnum). Cada bala ahora guarda `headshotMul` (del arma que la disparó) y la fórmula de daño lo usa en vez del valor fijo. Probado con Playwright inyectando una bala sintética directamente sobre la zona de headshot de un bot (congelando el `update()` propio del bot ese frame para aislar el cálculo de daño de cualquier movimiento de IA): BO-01 (dmg 28 × mul 1.5) dio exactamente 42 de daño, BO-31 Sniper (dmg 95 × mul 2.2) dio exactamente 209 — coincide con la fórmula esperada en ambos casos, ya no con el 2.0 fijo anterior.

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

### FASE FINAL: Movimiento — SLIDE (Sprint → Crouch → Slide → Recovery, completo)
Redirección explícita de prioridad a mitad de sesión: pasar a una fase de "base visual y jugable sólida" con el movimiento como prioridad máxima tras las armas. El slide no existía en absoluto. Implementado en `Player`: pulsar Crouch (C) recién (flanco, no mantenido) mientras se está esprintando, en el suelo y moviéndose dispara un slide — un impulso de velocidad (16 u/s, por encima de los 14 u/s del sprint) fijado a la dirección de movimiento en el instante de activación (no dirigible con WASD durante el slide, para que se sienta como un movimiento comprometido y no un "crouch-walk rápido"), que decae por fricción (`slideFriction=3.2`) hacia un suelo de 5 u/s; el slide termina quien llegue primero entre el timer (`slideDuration=0.55s`) o tocar ese suelo, y a partir de ahí el jugador queda agachado (si sigue pulsando C) o se levanta (si lo soltó) con la desaceleración normal ya existente. Reutiliza la altura de cápsula/elipsoide de crouch ya existente (sin geometría de colisión nueva). Aplica un ligero ensanchamiento de FOV (×1.06) mientras dura el slide para dar sensación de velocidad, aplicado después del FOV que ya controla `WeaponController` por ADS para no pelearse con el zoom de apuntado.

Probado con Playwright llamando directamente a `player.update()` con inputs controlados: tras 3 frames de sprint (`velLen=14`, `wasSprinting=true`), pulsar C dispara el slide con `slideSpeed` decayendo exactamente según la fórmula de fricción esperada dentro del mismo frame (16 → 14.976, coincide con el cálculo exacto), `isCrouching=true`, elipsoide ya en altura de crouch, y FOV en `0.8 × 1.06 = 0.848` (coincide exacto con `baseFov`). Pasos siguientes muestran la velocidad decayendo suavemente frame a frame hasta tocar el suelo de 5 u/s, momento en el que `isSliding` pasa a `false` y el jugador queda agachado (C seguía pulsada) con la desaceleración normal tomando el relevo. Cero errores de consola.

### FASE FINAL: Sonido ambiente de mapa (completo, procedural)
Primer elemento del checklist "sonido de mapas" del usuario: ambiente/viento. Añadido `SoundSynth.startAmbient()/stopAmbient()` — ruido filtrado en bucle (paso-bajo, ganancia baja) enrutado por el mismo `masterGain` que ya controla el volumen general, sin ningún archivo de audio externo (mismo enfoque que el resto de `SoundSynth`). Se inicia al empezar una partida (`initGame`) y se detiene al terminarla (`endGame`), para no sonar bajo la pantalla de resultados ni duplicarse en una repetición. Probado con Playwright: el contexto de audio queda en estado `running` durante la partida, y llamadas repetidas de start/stop/start/stop (incluida una llamada duplicada a `startAmbient()` ya en marcha) no lanzan ningún error — confirma que es seguro invocarlo desde cualquier punto del ciclo de vida de la partida.

### FASE FINAL: Bug de retícula — no reaccionaba al movimiento (corregido)
`updateCrosshairSize()` pasaba `moving: false` **fijo** a `getEffectiveSpread()`, a pesar de que el comentario junto a esa línea afirmaba lo contrario — la retícula nunca se ensanchaba al caminar/esprintar/deslizarse, solo reaccionaba a ADS/agachado/bloom de disparo. Corregido exponiendo `player.isMoving` (ya calculado internamente en `Player.update()`, simplemente no se guardaba) y usándolo en la llamada. Probado con Playwright: en reposo la retícula midió 31.8px, moviéndose hacia delante (`W`) midió 37.4px — confirma que ahora sí responde al estado de movimiento real, no solo a un valor congelado.

### FASE FINAL: Sonidos de jugador — pasos, salto, aterrizaje (completo, procedural)
El checklist de sonido del usuario pedía explícitamente "Pasos/Saltos/Aterrizajes" para el jugador, que no existían en absoluto. Añadido a `SoundSynth`: `playFootstep(crouched)` (ruido filtrado, más suave si está agachado), `playJump()`, `playLand()` — mismo enfoque 100% sintetizado que el resto del sistema de sonido. `Player` ahora dispara `playJump()` en el frame exacto en que se inicia un salto, `playLand()` en el frame exacto en que aterriza tras estar en el aire (detectado comparando `isGrounded` antes/después del chequeo de suelo del frame), y un temporizador de pasos mientras está en el suelo y moviéndose (cadencia distinta para andar/esprintar/agachado: 0.38s/0.28s/0.5s), pausado durante el slide. Probado con Playwright interceptando las tres funciones: 2s de caminar hacia delante disparó 6 pasos (coincide con la cadencia esperada de ~0.38s), pulsar salto disparó exactamente 1 sonido de salto y puso `isGrounded=false`, y forzar una caída seguida de aterrizaje disparó exactamente 1 sonido de aterrizaje y puso `isGrounded=true`. Cero errores de consola.

---

### FASE FINAL: Iluminación diferenciada por mapa (completa)
Los 3 mapas compartían exactamente la misma configuración de luz (misma intensidad, mismo color blanco, misma dirección) — el inventario de arriba lo señalaba como pendiente. Añadido `MAP_LIGHTING`, sin ningún asset nuevo: BACKLOT-7 mantiene una luz de día neutra y brillante (como antes), INDUSTRIAL-5 pasa a una luz más tenue y fría (tono azulado, sensación de nave industrial cubierta), OUTPOST-9 pasa a una luz cálida de atardecer (tono ámbar/naranja, ángulo más bajo). Probado con Playwright: los 3 mapas tienen valores de luz numéricamente distintos entre sí (confirmado por código) y capturas de pantalla confirman la diferencia visualmente perceptible — OUTPOST-9 se ve claramente ambarino/cálido frente al gris neutro de BACKLOT-7. Cero errores de consola.

### FASE FINAL: Pose de arma al esprintar (completa)
El inventario de arriba señalaba "Anim. sprint con arma" como ausente — el arma solo aceleraba el bob al esprintar, sin ninguna pose distinta. Añadido `sprintAmount` (blend 0-1 suavizado, no un salto instantáneo) que interpola el viewmodel hacia una pose de sprint (bajada/metida hacia dentro y ladeada) por encima de la posición base HIP/ADS ya existente — compatible sin conflicto porque ADS ya es mutuamente excluyente con esprintar en `WeaponController.isADS`. Probado con Playwright: andando `sprintAmount=0` (pose normal); esprintando `sprintAmount≈0.97` con un desplazamiento de posición claramente perceptible (`≈0.178` unidades) y rotación coincidente con el offset configurado; al dejar de esprintar (pero seguir moviéndose) `sprintAmount` vuelve a `≈0.005` — confirma la transición suave de entrada y salida. Cero errores de consola.

### FASE FINAL: Cámara — altura al agacharse + head bob (completo)
Pedido explícito del usuario bajo "Cámara y sensación de juego". La cámara del jugador nunca se movía verticalmente por sí sola: estaba fijada a una altura local (`0.6`) en el constructor y nunca se volvía a tocar — agacharse cambiaba la cápsula de colisión pero la vista permanecía exactamente a la misma altura, y no existía ningún bob de cámara (solo el arma en primera persona tenía su propio bob independiente). Implementado: altura de cámara suavizada por interpolación hacia un objetivo (`0.6` de pie / `0.35` agachado), y un bob de cámara (vertical + lateral sutil) activo solo mientras se está en el suelo, en movimiento y no deslizando, con cadencia distinta andar/esprintar/agachado — y amortiguado hasta un ~30% de su amplitud mientras se apunta (ADS), para que apuntar se sienta más estable, como se pidió explícitamente ("el movimiento debe cambiar ligeramente" durante ADS).

Probado con Playwright llamando a `player.update()` con inputs controlados: de pie la cámara se asienta exactamente en `0.6`; agachado se asienta en `≈0.35` (coincide con el objetivo); caminando 40 frames produce un rango de oscilación de `≈0.029`; manteniendo ADS (rampa real vía `adsDown`, no forzado) con `adsAmount≈0.999`, el mismo recorrido de 40 frames caminando produce un rango de solo `≈0.009` — una reducción de ~70%, coincide con la fórmula de amortiguación esperada. Cero errores de consola.

### FASE FINAL: Regresión combinada en los 3 mapas × 2 modos (completa)
Última pasada de verificación tras toda la tanda de cambios de esta fase (slide, cámara, pose de sprint, pasos/salto/aterrizaje, iluminación por mapa, sonido ambiente). Se ejecutó la secuencia combinada completa (esprintar→deslizar→ponerse de pie→disparar→recargar→saltar→moverse) sobre el jugador real en las 3 combinaciones `BACKLOT-7/TDM`, `INDUSTRIAL-5/FFA`, `OUTPOST-9/TDM`: el jugador terminó vivo y con salud completa en los 3 casos, la cámara volvió correctamente a su altura de pie (`0.6`) tras toda la secuencia, y cero errores de consola en total. Confirma que la combinación de todos los sistemas nuevos de esta fase no interfiere entre sí ni con ningún mapa/modo existente.

### FASE FINAL: Prueba de regresión de extremo a extremo (completa)
Tras la tanda de cambios de esta fase (slide, pasos/salto/aterrizaje, sonido ambiente, fix de retícula, fix de headshot, fix de alcance, fix de sprint-to-fire), se probó con Playwright la cadena completa que el usuario pidió poder validar al volver: **moverse → esprintar → agacharse → deslizarse → sacar arma → apuntar con la mira → disparar → recargar → cambiar de arma → moverse por el mapa**, todo en una sola secuencia continua sobre el jugador real:
1. Mover (W) → velocidad 8 (moveSpeed) ✓
2. Esprintar (W+Shift) → velocidad 14 (sprintSpeed), `wasSprinting=true` ✓
3. Agachar+deslizar (C recién pulsado en sprint) → `isSliding=true`, velocidad ~14.98 decayendo ✓
4. Fin del slide → sigue agachado (C mantenido) ✓
5. Soltar C → de pie ✓
6. Cambiar de arma (tecla 2) → arma correcta equipada, estado `IDLE` tras la transición ✓
7. Apuntar (ADS) → `isADS=true`, `adsAmount≈1.0`, FOV reducido correctamente ✓
8. Disparar → munición 25→24, bala creada ✓
9. Recargar (R) → estado `RELOADING`→`IDLE`, munición restaurada a 25 ✓
10. Cambiar de arma otra vez (tecla 3) → arma correcta, estado `IDLE` ✓
11. Moverse por el mapa → posición avanza con normalidad, jugador vivo ✓

Cero errores de consola en toda la cadena — confirma que ningún sistema se rompió con los cambios acumulados de esta fase.

---

## 🔧 SIGUIENTE PASO (para retomar la sesión)

**Redirección de prioridad a mitad de sesión (instrucción explícita del usuario):** pasar a una "fase final de visual y gameplay" — base jugable sólida antes de más contenido. Nuevo orden de prioridad: 1) Mapas, 2) Movimiento del jugador, 3) Sprint, 4) Agacharse, 5) Slide, 6) ADS, 7) Retícula, 8) Cámara, 9) Armas/animaciones, 10) Sonidos, 11) Texturas/materiales, 12) Pulido visual, 13) Optimización, 14) Bugs/testing.

Ya cubierto dentro de esta nueva prioridad (ver secciones "FASE FINAL" arriba): Slide completo y probado, pasos/salto/aterrizaje, sonido ambiente de mapa, fix de retícula (no reaccionaba a movimiento), y una pasada de regresión de extremo a extremo confirmando el flujo completo mover→esprintar→agachar→deslizar→sacar arma→apuntar→disparar→recargar→cambiar→moverse. Lo que queda de esta lista, en orden:

1. **Mapas (prioridad máxima del usuario, aún pendiente en profundidad)**: el inventario de arriba ya identifica qué falta por elemento. Lo accionable sin assets externos: iluminación diferenciada por mapa (ahora mismo las 3 usan exactamente la misma luz plana), variación del sonido ambiente por mapa (interior/exterior), más props de cobertura procedurales para dar más textura visual sin necesitar modelos reales.
2. **ADS real "a través de la mira"**: el pedido explícito es que se apunte de verdad, no solo zoom de cámara — la limitación conocida (geometría de bloque sin mira real, documentada en el código y en Decisiones Técnicas) sigue sin resolverse porque depende de un modelo real con mira modelada.
3. **Cámara**: head bob ya existe (bob de viewmodel), pero no hay bob de cámara en sí (solo el arma se mueve) — revisar si el usuario lo espera en la cámara del jugador también.
4. **Fase 7 (Menús)**: solo queda CUSTOMIZE bloqueado — de prioridad baja en el nuevo orden.
5. **Fase 10 (Multiplayer)**: pausado — la redirección de prioridad no lo menciona, se retoma cuando la base visual/jugable esté más sólida.
6. **Attachments**: sigue bloqueado en modelos 3D reales, sin cambios.

---

## 📦 INVENTARIO DE ASSETS (nada de esto bloquea el desarrollo — placeholders funcionando mientras tanto)

### MAPAS — por elemento

Los 3 mapas (`BACKLOT-7`, `INDUSTRIAL-5`, `OUTPOST-9`) comparten exactamente la misma naturaleza: blockout geométrico con primitivas Babylon (cajas/cilindros/plano) y `StandardMaterial` de color plano, sin ningún asset externo. Todos los elementos de abajo aplican igual a los 3 — lo que cambia entre mapas es solo el layout (posiciones/tamaños), no el tipo de asset.

| Elemento | Estado actual | Tipo de asset que falta | Bloquea desarrollo |
|---|---|---|---|
| Suelo | ✅ Plano + color plano | Textura de superficie (PNG/JPG tileable) | No |
| Edificios/bases/torres | ✅ Cajas + color plano | Modelo 3D (GLB) + textura | No |
| Coberturas (crates, muros, barriles) | ✅ Primitivas + `checkCollisions` | Modelo 3D (GLB) de props | No |
| Puertas | ❌ No existen (todo son cajas sólidas fijas) | Modelo + animación de apertura | No — nada las requiere aún |
| Ventanas | ❌ No existen | Modelo/material transparente | No |
| Iluminación | ✅ **Nuevo esta sesión**: 1 luz hemisférica + 1 direccional, con intensidad/color/ángulo propios por mapa (`MAP_LIGHTING`) | — | — |
| Skybox | ❌ Color de fondo plano (`scene.clearColor`) | HDR o 6 caras JPG | No |
| Sonido ambiente | ✅ **Nuevo esta sesión**: viento sintetizado (ruido filtrado en bucle), igual en los 3 mapas | Variación por mapa (interior/exterior distinto) | No |
| Props ambientales (vegetación, señalética, escombros) | ❌ No existen | Modelos 3D variados (GLB) | No |
| Elementos interactivos | ❌ No existen (ninguna puerta/palanca/ascensor) | Diseño + modelo + lógica | No |
| Optimización (LOD/oclusión) | ❌ No implementada — geometría actual es lo bastante simple para no necesitarlo todavía | N/A por ahora | No |

### ARMAS — por arma y elemento (patrón idéntico en las 15)

Las 15 armas (`BO01-BO03` AR, `BO11-BO13` SMG, `BO21-BO22` Shotgun, `BO31-BO32` Sniper, `BO41-BO42` LMG, `BO51-BO53` Pistol) comparten el mismo estado porque usan la misma arquitectura (`WEAPON_CONFIGS` + `buildWeaponViewmodel` + `WeaponController`). Se muestra un resumen por categoría de elemento en vez de repetir 15 filas idénticas; **BO-01 VANGUARD es la prioridad de referencia si solo se puede producir un lote de assets a la vez.**

| Elemento | Estado actual | Asset que falta | Bloquea gameplay |
|---|---|---|---|
| Modelo 3D (viewmodel) | ✅ Placeholder procedural, silueta distinta por categoría | Modelo GLB real, poli bajo/medio | No |
| Material/textura | ✅ Color plano por skin (`SKIN_REGISTRY`) | Textura PNG (solo para skins con patrón) | No |
| Cargador visible | ✅ Geometría propia por categoría | Modelo detallado | No |
| Mira/accesorios | ⚠️ Sight solo en AR/Sniper (bloque simple), sin mira real que mirar a través | Mira modelada (red-dot/scope real) | No, pero limita la sensación de ADS (ver nota en Decisiones Técnicas) |
| Anim. equipar/desequipar | ✅ Transición de "dip" al cambiar de arma (`switchDip`) | Animación real de modelo | No |
| Anim. disparo (recoil visual) | ✅ Kick de cámara + arma por código | Animación de modelo | No |
| Anim. recarga (normal/vacía) | ✅ Timing correcto (`reloadTime`/`reloadTimeEmpty`) + sonido, sin animación visual del modelo (el arma no se mueve durante la recarga) | Animación de recarga en el modelo | No |
| Anim. apuntado/salir de apuntado | ✅ Transición de posición/FOV suavizada | Animación real si el modelo la necesita | No |
| Anim. sprint con arma | ✅ **Nuevo esta sesión**: pose de sprint (bajada/ladeada) con blend suavizado | — | — |
| Anim. inspección | ❌ No existe | Animación | No |
| Sonido disparo | ✅ Sintetizado, un perfil por categoría (`GUNSHOT_PROFILES`) | Audio real grabado por arma | No |
| Sonido disparo por distancia | ❌ No hay variación por distancia | Capas de audio (cerca/lejos) | No |
| Sonido recarga/cargador | ✅ Sintetizado (mag-out/mag-in/click) | Audio real | No |
| Sonido equipar/cambiar | ✅ Sintetizado (`playEquip`) | Audio real | No |
| Sonido impacto | ✅ Partícula + sonido de hitmarker/headshot | Sonido de impacto en superficie (madera/metal/etc.) | No |
| Sonido casquillos | ❌ No existe | Audio sintetizado o real | No |
| Daño/cadencia/retroceso/precisión/alcance/capacidad/recarga/movimiento | ✅ **Completo y verificado** — todo dato en `WEAPON_CONFIGS`, todo aplicado de verdad (ver bugs corregidos esta sesión: `headshotMul`, `range`, `sprintToFireDelay`) | — | — |
| Multiplicador headshot | ✅ **Corregido esta sesión** — antes fijo en 2.0, ahora usa el valor real por arma | — | — |

### JUGADOR — sonidos (elemento nuevo de esta sesión)

| Elemento | Estado |
|---|---|
| Pasos | ✅ **Nuevo esta sesión** — sintetizado, cadencia distinta andar/esprintar/agachado |
| Sprint (transición de sonido) | ✅ Cubierto por la cadencia de pasos más rápida |
| Agacharse | ⚠️ Sin sonido propio de transición (solo pasos más lentos mientras se mueve agachado) |
| Slide | ⚠️ Sin sonido propio (el mecanismo de movimiento sí está completo) |
| Saltos | ✅ **Nuevo esta sesión** |
| Aterrizajes | ✅ **Nuevo esta sesión** |

**Nada de lo marcado ❌/⚠️ arriba bloquea el desarrollo** — cada sistema tiene su placeholder funcional (geometría procedural, sonido sintetizado, o simplemente "no pasa nada visualmente pero el gameplay ya es correcto") y puede sustituirse por el asset real más adelante sin tocar la arquitectura que ya lo consume (`WeaponController`, `SoundSynth`, `buildWeaponViewmodel`).

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
