# BULLET OPS — ÍNDICE MAESTRO DE DESARROLLO

Documento vivo de gestión autónoma del proyecto. Se actualiza en cada ciclo de trabajo (`ANALIZAR → PLANIFICAR → IMPLEMENTAR → PROBAR → CORREGIR → PULIR → ACTUALIZAR ÍNDICE → SIGUIENTE TAREA`). El detalle técnico de cada cambio (qué se hizo, por qué, cómo se probó) vive en `BULLET_OPS_PROGRESS.md` — este índice es el mapa de qué falta y en qué orden, no el changelog.

**Leyenda de estado:** 🔴 Pendiente · 🟡 En progreso · 🟢 Completado · 🔧 Funciona pero necesita mejora · 🔒 Bloqueado (requiere intervención del usuario) · ⚠️ Tiene errores conocidos
**Leyenda de prioridad:** P0 Crítico · P1 Muy importante · P2 Importante · P3 Pulido · P4 Opcional

Última actualización: sesión autónoma en curso (sistema de armas como prioridad principal; roster 45/82, ver `BULLET_OPS_PROGRESS.md`).

---

## FASE 1 — BASE DEL PROYECTO

| Tarea | Estado | Prioridad | Notas |
|---|---|---|---|
| Arquitectura de archivo único (sin build step, compatible con Artifact) | 🟢 | — | Decisión técnica estable, no revisar sin motivo de peso |
| `WEAPON_CONFIGS` como fuente única de datos de armas | 🟢 | — | 45 armas (objetivo 82), escalable por config |
| `WeaponController` (estado IDLE/RELOADING/SWITCHING/INSPECTING) | 🟢 | — | |
| `SoundSynth` (audio 100% sintetizado, sin assets externos) | 🟢 | — | |
| `SKIN_REGISTRY` / sistema de camuflajes | 🟢 | — | Solo 1 skin real + 1 patrón de prueba, ver FASE 4 |
| Gestión de memoria (fuga de materiales por disparo) | 🟢 | — | Corregido, materiales compartidos |
| Auditoría general de rendimiento (draw calls, mallas huérfanas) | 🟢 | — | Sin fugas tras la expansión a 35 armas; mallas/materiales/texturas planos en una partida real de 15s con disparo+cambio de arma continuos; ver `BULLET_OPS_PROGRESS.md` |
| Organización del código (comentarios, nomenclatura) | 🟢 | — | Mantenido consistente durante toda la sesión |

## FASE 2 — JUGADOR

| Tarea | Estado | Prioridad | Notas |
|---|---|---|---|
| Movimiento base (WASD, aceleración/deceleración arcade) | 🟢 | — | |
| Sprint | 🟢 | — | |
| Agacharse (crouch) | 🟢 | — | Altura de cámara + colisión |
| Slide (sprint→crouch→slide→recuperación) | 🟢 | — | Probado con Playwright |
| Salto | 🟢 | — | Con sonido propio |
| Cámara: altura al agacharse | 🟢 | — | Antes no existía |
| Cámara: head bob | 🟢 | — | Amortiguado en ADS |
| FOV (normal / ADS / slide) | 🟢 | — | |
| Transiciones (crouch↔stand, sprint↔slide) | 🟢 | — | |
| Animación de arma durante sprint (pose) | 🟢 | — | |
| Colisiones jugador-mundo | 🟢 | — | |

## FASE 3 — COMBATE

| Tarea | Estado | Prioridad | Notas |
|---|---|---|---|
| Disparo (hitscan tipo proyectil con velocidad real) | 🟢 | — | |
| Daño + multiplicador de headshot por arma | 🟢 | — | Corregido de un valor fijo a per-arma |
| Hit detection (segmento vs. cápsula) | 🟢 | — | |
| Retroceso (patrón + kick visual + bloom) | 🟢 | — | |
| Munición / recarga (normal y desde vacío) | 🟢 | — | |
| Cambio de arma | 🟢 | — | Con sonido de equipar |
| Alcance real por arma | 🟢 | — | Corregido, antes ignorado |
| `sprintToFireDelay` | 🟢 | — | Corregido, antes ignorado |
| Feedback visual (hitmarker, headshot, killfeed) | 🟢 | — | |
| Feedback sonoro (impacto, headshot, kill confirm) | 🟢 | — | |
| Daño en área / explosiones (splash) | 🟢 | — | Con caída por distancia, sin auto-daño |
| Combate cuerpo a cuerpo | 🟢 | — | Reutiliza el pipeline de balas |
| IA de bots: usa el roster completo (incl. melee/explosivo) | 🟢 | — | |

## FASE 4 — ARMAS (SISTEMA PRINCIPAL DEL PROYECTO)

Redirección explícita del usuario: el sistema de armas pasa a ser uno de los pilares del proyecto, con Battlefield 4/V/2042 como referencia de **estructura, variedad y cantidad** — nunca de assets. Ningún modelo, textura, sonido ni animación se copia de ningún juego; solo se estudia su organización de categorías para diseñar la nuestra propia.

### Investigación: categorías por entrega (BF4 / BFV / BF2042)

| Entrega | Categorías de armas |
|---|---|
| Battlefield 4 | Fusil de asalto, **Carabina** (propia, todas las clases), SMG, LMG, **DMR** (propia, todas las clases), Francotirador, Escopeta, Pistola (all-kit), Lanzadores, Cuchillo |
| Battlefield V | Fusil de asalto, Fusil semiautomático, Fusil de cerrojo (sniper), **Fusil autocargante**, SMG, LMG, **Ametralladora media** (propia, más pesada que LMG), Escopeta, Arma secundaria (pistola) |
| Battlefield 2042 | Fusil de asalto, SMG, LMG, **Fusil de marcador/DMR** ("Marksman"), Francotirador, Utilidad (escopetas), Pistola |

Ningún juego usa exactamente la misma lista. El hilo común a las tres entregas — y el motivo de las decisiones de taxonomía de abajo — es que **AR, SMG, LMG, DMR, Sniper, Shotgun y Pistol/Sidearm aparecen siempre**, mientras que Carabina (BF4), Fusil autocargante/Ametralladora media (BFV) y la fusión Utilidad=Escopeta (BF2042) son variaciones de una misma entrega, no un consenso.

### Tabla maestra: categoría → BF4 → BFV → BF2042 → objetivo del proyecto

Cifras de BF4/BFV/BF2042 son aproximadas (rosters base, sin DLC/temporadas — varían por fuente y expansión; ver fuentes en `BULLET_OPS_PROGRESS.md`). La columna "objetivo" no es una copia de ninguna cifra: es una cantidad ambiciosa pero realista para una arquitectura escalable, priorizando variedad de gameplay por categoría sobre un número arbitrario.

| Categoría (nuestra) | BF4 | BFV | BF2042 | Objetivo del proyecto | Estado actual |
|---|---|---|---|---|---|
| Fusiles de asalto (AR) | ~10 | ~8 | 2 (base) | 12 | 🟡 5/12 |
| Subfusiles (SMG) | ~9 | ~6 | 4 | 10 | 🟡 5/10 |
| LMG | ~6 | ~5 | 2 | 8 | 🟡 4/8 |
| DMR (fusil de marcador) | ~5 | ~4 (autocargante) | 3 | 8 | 🟡 3/8 |
| Francotiradores (Sniper, cerrojo) | ~6 | ~6 (cerrojo) | 3 | 8 | 🟡 3/8 |
| Escopetas | ~5 | ~4 | 2 | 8 | 🟡 4/8 |
| Pistolas | ~8 | ~6 | 3 | 6 | 🟡 4/6 |
| Revólveres | (dentro de Pistolas en BF4/BFV) | (íd.) | (íd.) | 4 | 🟡 3/4 |
| Lanzadores | ~4 | ~3 | ~3 | 6 | 🟡 4/6 |
| Especiales/balísticos | — (no existe como categoría en ninguna entrega — decisión propia para armas futuristas/no convencionales) | — | — | 6 | 🟡 5/6 |
| Cuerpo a cuerpo (cuchillos + contundentes) | 1 (cuchillo genérico) | 1 | 1 | 6 | 🟡 5/6 |
| **Total** | ~65 (sin melee/gadgets) | ~48 | ~23 (base) | **82** | **45/82 (55%)** |

El objetivo de 82 no es un techo — es la primera meta ambiciosa de una arquitectura ya probada para escalar a "cientos de armas" (cada arma nueva es una entrada de datos en `WEAPON_CONFIGS`, sin tocar `WeaponController`/`Bot`/HUD/crosshair). Cuando 82 esté cerca, se revisará si ampliar más aporta valor real de gameplay o solo relleno.

### Taxonomía definitiva del proyecto (11 categorías)

No es una copia de ninguna entrega — es la síntesis tras comparar las tres (ver tabla de investigación arriba). `WEAPON_CATEGORY` en `bullet-ops-game.html` es la fuente de verdad en código:

1. **AR** — Fusil de asalto, todoterreno.
2. **SMG** — Subfusil, movilidad alta, corto alcance.
3. **LMG** — Ametralladora ligera, cargador grande, movilidad reducida.
4. **DMR** — *(nueva)* Fusil semiautomático de precisión — daño/zoom intermedios entre AR y Sniper, sin la penalización de recuperación lenta del cerrojo. Sembrada con BO-32 PHANTOM (reclasificada desde SNIPER: su cadencia de 2.2 disp/s siempre desentonó con el resto de francotiradores de cerrojo lento).
5. **Sniper** — Cerrojo, daño altísimo, cadencia muy lenta, recuperación de retroceso lenta.
6. **Shotgun** — Corto alcance, daño de área por perdigones.
7. **Pistol** — Semiautomática, cargador medio, arma secundaria estándar.
8. **Revolver** — *(nueva)* Cargador pequeño, daño por disparo muy alto, recarga lenta. Sembrada con BO-52 MAGNUM (reclasificada desde PISTOL: 6 balas y 65 de daño ya la distinguían del resto de pistolas semiautomáticas).
9. **Rocket/Launcher** — Explosivos de área, daño en salpicadura.
10. **Special** — Armas balísticas/futuristas no convencionales — categoría sin equivalente directo en ninguna entrega de Battlefield, decisión propia del proyecto.
11. **Melee** — Cuerpo a cuerpo; subcategoría `subcategory` distingue cuchillos (`'Knife'`) de armas contundentes cuando se puebla (ver esquema de datos).

### Esquema de datos por arma (arquitectura escalable)

`WEAPON_CONFIGS[id]` ya cubre: `id, name, category, damage, headshotMul, fireRate, mag, reserve, reloadTime, reloadTimeEmpty, spread{hip/ads/moving}, range, bulletSpeed, ads{time/fovMul/sensitivityMul}, movement{hipMul/adsMul}, sprintToFireDelay, recoil{vertical/horizontal/cameraKick/recoverySpeed}, sway{amount/speed/bobAmount/bobSpeed}, soundProfile, defaultSkin, attachmentSlots, projectileType` (+ `meleeRange/meleeSpeed` o `splashRadius` según el tipo). Nuevos campos añadidos esta sesión, empezando por BO-32/BO-52 como ejemplo concreto: `subcategory` (string libre, p. ej. `'Marksman Rifle'`), `ammoType` (string descriptivo, p. ej. `'7.62mm'`), `fireMode` (`'semi-auto'` / `'single-action'` / futuro `'burst'`/`'full-auto'`). Backfill de estos 3 campos al resto de las 33 armas existentes es tarea pendiente (no bloqueante — ningún código de gameplay los lee todavía; son metadatos de catalogación).

**Decisión deliberada de diseño:** el checklist detallado por arma que pide el usuario (modelo/escala/piezas/cargador/miras/accesorios; texturas base-color/normal/roughness/metallic/desgaste; animaciones idle/equipar/disparo/recarga/ADS/inspección; audio disparo/recarga/casquillo/impacto; VFX muzzle/humo/casquillos/tracer) **vive aquí en el índice, no como campos de `WEAPON_CONFIGS`** — son estados de producción de assets (bloqueados en modelos 3D reales para casi todo), no datos que el motor de juego necesite leer en tiempo de ejecución. Meterlos en el objeto de config bloatearía los datos con docenas de campos que ningún código consulta. El resumen compacto de abajo es ese checklist, ya aplicado a las 35 armas actuales.

Por arma: modelo(🔒 real / 🟢 placeholder) → textura(🔒) → materiales(🟢 código) → animaciones(🟢 procedurales: equipar/disparo/recarga/ADS/sprint/inspección) → disparo(🟢) → recarga(🟢) → sonidos(🟢 sintetizados) → retroceso(🟢) → ADS(🟢) → estadísticas(🟢) → efectos(🟢) → testing(🟢) → subcategory/ammoType/fireMode(🟡 2/35, resto pendiente de backfill). **Ninguna arma nueva necesita trabajo de gameplay** — lo único pendiente en las 35 (salvo el backfill de metadatos) es el mismo bloqueo de siempre: modelos 3D/texturas reales.

### Roster actual por categoría (45 armas · 11 categorías)

- **AR** (5/12): BO-01 VANGUARD, BO-02 PREDATOR, BO-03 STORMCALLER, BO-04 SENTINEL, BO-05 OUTLAW
- **SMG** (5/10): BO-11 RAZORBACK, BO-12 WHISPER, BO-13 ENFORCER, BO-14 VIPERBITE, BO-15 UNDERTOW
- **Shotgun** (4/8): BO-21 BREACHER, BO-22 SCATTERGUN, BO-23 WIDOWMAKER, BO-24 SLUGSTORM
- **Sniper** (3/8): BO-31 LONGSHOT, BO-33 WRAITHFANG, BO-34 DEADEYE
- **DMR** (3/8): BO-32 PHANTOM, BO-35 RIDGELINE, BO-36 QUICKSILVER
- **LMG** (4/8): BO-41 JUGGERNAUT, BO-42 RAMPART, BO-43 OVERLORD, BO-44 VANDAL
- **Pistol** (4/6): BO-51 SIDEARM, BO-53 VIPER, BO-54 ECHO, BO-55 DUELIST
- **Revolver** (3/4): BO-52 MAGNUM, BO-56 PEACEMAKER, BO-57 SNAKEEYE
- **Rocket** (4/6): BO-61 DEVASTATOR, BO-62 SKYFALL, BO-63 BREACHPOINT, BO-64 LONGARM
- **Melee** (5/6): BO-71 FANG, BO-72 KARAMBIT, BO-73 CLEAVER, BO-74 WRECKER, BO-75 TALONS
- **Special** (5/6): BO-81 SILENTBOLT, BO-82 THUMPER, BO-83 HORNET, BO-84 RAILDRIVER, BO-85 WASP

| Tarea transversal | Estado | Prioridad |
|---|---|---|
| Attachments (arquitectura lista, sin poblar) | 🔒 | P3 — bloqueado en modelos reales |
| Camuflajes reales (solo 1 skin + 1 patrón de prueba) | 🔴 | P3 |
| Sonido de casquillos | 🔴 | P4 |
| Sonido de disparo con variación por distancia | 🔴 | P4 |
| Backfill subcategory/ammoType/fireMode en las 35 armas restantes | 🔴 | P3 |
| Ampliación de roster hacia el objetivo de 82 (ver tabla maestra) | 🔴 | P2 — prioridad principal actual, ver PRÓXIMA TAREA |
| Burst fire / modos de disparo múltiples por arma | 🔴 | P3 — depende de que `fireMode` tenga backfill primero |

## FASE 5 — APUNTADO Y HUD

| Tarea | Estado | Prioridad | Notas |
|---|---|---|---|
| ADS (transición FOV/posición/sensibilidad) | 🟢 | — | |
| ADS "a través de la mira" real | 🟢 | — | Sin modelo 3D real: resuelto vía overlay de pantalla — círculo de mira + retícula mil-dot para SNIPER, viñeta sutil para el resto; sincronizado con `adsAmount` real. Ver `BULLET_OPS_PROGRESS.md` |
| Retícula reactiva a movimiento/disparo/ADS | 🟢 | — | Corregido bug: no reaccionaba a movimiento |
| Retículas diferentes por arma/categoría | 🟢 | — | Círculo/cuadrado/diamante/solo-punto según categoría, tamaño sigue siendo reactivo al spread real |
| Sensibilidad configurable | 🟢 | — | |
| Invertir eje Y | 🟢 | — | |
| Volumen general | 🟢 | — | |
| HUD: vida, munición, killfeed, hitmarker, streak | 🟢 | — | |
| HUD: indicador de arma cuerpo a cuerpo (sin munición) | 🟢 | — | |
| Pantalla de resultados | 🟢 | — | |

## FASE 6 — MAPAS

| Mapa | Geometría | Iluminación | Sonido ambiente | Props/cobertura | Puertas/ventanas | Optimización |
|---|---|---|---|---|---|---|
| BACKLOT-7 | 🟢 blockout | 🟢 propia | 🟢 propio (viento abierto, filtro 550Hz) | 🟢 básico | 🔴 no existen | 🔴 sin LOD/oclusión |
| INDUSTRIAL-5 | 🟢 blockout | 🟢 propia | 🟢 propio (viento sordo 260Hz + zumbido de maquinaria) | 🟢 básico | 🔴 | 🔴 |
| OUTPOST-9 | 🟢 blockout (3 carriles) | 🟢 propia | 🟢 propio (viento silbante 750Hz) | 🟢 básico | 🔴 | 🔴 |

| Tarea transversal de mapas | Estado | Prioridad |
|---|---|---|
| Texturas de superficie reales (ahora color plano) | 🔒 | P3 — bloqueado en assets |
| Sombras dinámicas | 🟢 | — | Implementado con `ShadowGenerator` por mapa; ver `BULLET_OPS_PROGRESS.md` para el hallazgo de rendimiento en el entorno de pruebas (SwiftShader/software) y por qué no bloqueó la función |
| Sonido ambiente diferenciado por mapa | 🟢 | — | `MAP_AMBIENCE`, análogo a `MAP_LIGHTING` |
| Segundo pase de props/detalle ambiental | 🟢 | — | Ver `BULLET_OPS_PROGRESS.md`: dumpsters/palés/farolas, tanques/contenedores/tuberías, sacos de arena/rocas/antena por mapa |
| Un cuarto mapa / más contenido | 🔴 | P4 |

## FASE 7 — AUDIO

| Tarea | Estado | Prioridad |
|---|---|---|
| Disparo (por categoría, incl. rocket/special nuevos) | 🟢 | — |
| Recarga (mag-out/mag-in/click) | 🟢 | — |
| Cambio de arma / equipar | 🟢 | — |
| Pasos (andar/esprintar/agachado) | 🟢 | — |
| Salto / aterrizaje | 🟢 | — |
| Impactos (normal/headshot/explosión) | 🟢 | — |
| Ambiente de mapa | 🟢 | — |
| Sonido dedicado de slide | 🟢 | — | Barrido de ruido descendente + golpe grave, disparado una vez al iniciar el slide |
| Sonido de la UI/menús (click, hover, back) | 🟢 | — | Listener delegado, cubre las 7 pantallas de menú incl. botones dinámicos |
| Música de menú/partida | 🔴 | P4 |

## FASE 8 — GRÁFICOS Y VISUAL

| Tarea | Estado | Prioridad |
|---|---|---|
| Iluminación diferenciada por mapa | 🟢 | — | |
| Sombras dinámicas | 🟢 | — | Ver FASE 6 |
| Partículas (muzzle flash, impacto, explosión) | 🟢 | — | |
| Postprocesado (tone mapping, vignette) | 🟢 | — | Vía `imageProcessingConfiguration` (horneado en shader, sin coste de pase extra) en vez de `DefaultRenderingPipeline` con bloom |
| Texturas/materiales reales | 🔒 | P3 | Bloqueado en assets |
| Modelos 3D reales | 🔒 | P3 | Bloqueado en assets |
| Animaciones (viewmodel procedural) | 🟢 | — | |
| Cámara (bob, FOV, transiciones) | 🟢 | — | |

## FASE 9 — UI / MENÚS

| Tarea | Estado | Prioridad |
|---|---|---|
| Menú principal | 🟢 | — |
| HUD de partida | 🟢 | — |
| Selector de arma / Loadout (35 armas) | 🟢 | — |
| Catálogo de armas (WEAPONS) | 🟢 | — |
| Operadores (identidad visual) | 🟢 | — |
| Configuración (sensibilidad, volumen, invertir Y) | 🟢 | — |
| Configuración gráfica (calidad, resolución) | 🟢 | — | Toggle HIGH/LOW: LOW desactiva sombras + reduce resolución interna (`setHardwareScalingLevel`) — las dos palancas reales identificadas en la auditoría de rendimiento |
| Pantalla de carga | 🟢 | — | Barra de progreso real (no falsa) por etapa de `initGame()`; ver `BULLET_OPS_PROGRESS.md` |
| Pantalla de resultados | 🟢 | — |
| CUSTOMIZE (combinar skin + operador) | 🔒 | P4 — bloqueado en tener más de 1 skin real |
| Sonido de UI | 🟢 | — | Ver FASE 7 |

## FASE 10 — TESTING

| Área | Estado | Notas |
|---|---|---|
| Combate (armas, hit detection, splash, melee) | 🟢 | Probado exhaustivamente con Playwright esta sesión |
| Movimiento (sprint/crouch/slide/jump) | 🟢 | Probado |
| IA de bots (incl. las 35 armas) | 🟢 | Probado, incluida una partida real de 15s sin asistencia |
| Mapas (3 mapas × 2 modos) | 🟢 | Regresión combinada probada |
| UI/menús | 🟢 | Catálogo, loadout, operadores, settings probados |
| Auditoría de errores de consola | 🟢 | Cero errores en todas las pruebas de esta sesión |
| Pase de regresión tras cada cambio grande | 🟢 | Metodología ya establecida y seguida sistemáticamente |

Sin bugs críticos conocidos abiertos en este momento.

## FASE 11 — OPTIMIZACIÓN

| Tarea | Estado | Prioridad |
|---|---|---|
| Fuga de materiales por disparo | 🟢 | — | Corregido |
| Reutilización de texturas de partículas | 🟢 | — | |
| Límite de balas en vuelo (`maxBullets`) | 🟢 | — | Ya existía |
| Auditoría de draw calls / mallas por partida larga | 🟢 | — | Ver FASE 1 |
| LOD | 🔴 | P4 | Geometría actual demasiado simple para necesitarlo aún |
| Oclusión / culling de mapas | 🔴 | P4 | Mapas pequeños, bajo impacto por ahora |

## FASE 12 — PULIDO FINAL

Revisión continua transversal. Elementos "de prototipo" detectados activamente y priorizados en las fases de arriba:
- ~~Sin sombras~~ — 🟢 corregido, ver FASE 6/8.
- ~~Brillo especular no deseado en superficies de mapa~~ — 🟢 corregido de paso al implementar sombras.
- ~~Sin sonido de UI~~ — 🟢 corregido, ver FASE 7/9.
- ~~Retícula única para 35 armas~~ — 🟢 corregido, ver FASE 5.
- ~~Sin postprocesado~~ — 🟢 corregido, ver FASE 8.
- ~~Mismo sonido ambiente en los 3 mapas~~ — 🟢 corregido, ver FASE 6/7.
- Resto de "prototipo" visual (texturas planas, modelos de bloques) está correctamente identificado como bloqueado en assets reales, no como negligencia — cada uno tiene ya su placeholder funcional documentado en `BULLET_OPS_PROGRESS.md`.

---

## 🔌 HERRAMIENTAS Y CONECTORES

Sección permanente, actualizada cada vez que se evalúa o conecta una herramienta nueva. Formato: Nombre → función → coste → estado → permisos → utilidad → tareas dependientes.

**Estados:** 🟢 Conectado · 🟡 Recomendado · 🔴 No disponible · 🔒 Requiere autorización del usuario · ⚪ No necesario

| Herramienta | Función | Coste | Estado | Permisos | Utilidad | Tareas dependientes |
|---|---|---|---|---|---|---|
| Git (Bash) | Control de versiones, commit/push a `claude/bullet-ops-fps-game-jizk2k` | Gratis | 🟢 Conectado | Lectura/escritura del repo local, push al remoto | Imprescindible — único mecanismo de guardado/entrega del proyecto | Todas |
| TaskCreate/TaskUpdate/TaskList (nativo) | Seguimiento de tareas de esta sesión | Gratis | 🟢 Conectado | Ninguno (interno) | Organiza el ciclo autónomo, visible para el usuario | Todas |
| Playwright + Chromium local | Testing automatizado contra el juego real (no simulado) | Gratis | 🟢 Conectado | Ejecuta el juego en un navegador headless local | Único método de verificación usado toda la sesión — sin esto no se podría probar nada | Todas las que requieren verificación |
| Artifact (publish/read) | Despliega el juego jugable con link compartible | Gratis (incluido) | 🟢 Conectado | Publica el contenido de `bullet-ops-game.html` | Es cómo el usuario prueba el juego sin abrir el repo | Cada publicación de build |
| WebSearch / WebFetch (nativas) | Investigación externa (referencias de otros shooters, técnicas Babylon.js/WebGL, búsqueda de assets libres) | Gratis | 🟢 Conectado (disponibles, uso puntual según necesidad) | Solo lectura de la web pública | Puede acelerar decisiones de diseño de armas/gameplay y localizar assets CC0 reales | Mejora continua de armas/mapas; ver fila siguiente |
| Bibliotecas de assets CC0 (Kenney.nl, Poly Haven, itch.io CC0) | Modelos 3D / texturas / sonidos gratuitos y sin restricción de licencia | Gratis (CC0) | 🟡 Recomendado — se intentará vía WebFetch antes de pedir cualquier cosa de pago | Solo descarga de archivos públicos | Es el camino realista para desbloquear "modelos 3D reales" y "texturas reales" (hoy 🔒), sin depender de un conector de generación 3D que no existe en este entorno | Modelos de armas, texturas de mapas, skins reales |
| GitHub MCP (`mcp__github__*`) | Issues/PRs/CI en GitHub | Gratis (incluido) | ⚪ No necesario por ahora | Leer/escribir el repo vía API en vez de git directo | Git directo por Bash ya cubre todo lo que este proyecto necesita (no hay flujo de PR/review solicitado) | Ninguna actualmente |
| Adobe for Creativity / Canva | Edición de imágenes, generación de diseños gráficos | Gratis con límites / planes de pago | ⚪ No necesario — evaluado y descartado | — | Son herramientas de diseño gráfico/marketing, no de generación de texturas PBR tileable ni modelos 3D de juego — no resuelven el bloqueo real de assets | — |
| Generador de modelos 3D dedicado | Crear modelos GLB/OBJ reales para armas/personajes | Variable | 🔴 No disponible en este entorno | — | Ningún conector de los disponibles hace esto; sin él, "modelos 3D reales" sigue con placeholder procedural. Antes de recomendar algo de pago se agotará la vía CC0 gratuita de la fila de arriba | Modelos de las 35 armas |

**Nota:** ningún conector nuevo es necesario en este momento para continuar el desarrollo — todo lo disponible (git, testing, tareas, Artifact, búsqueda web) ya está conectado y en uso. Si en algún ciclo futuro se detecta que una tarea concreta realmente lo requiere, se documentará aquí con la recomendación específica (gratuita primero) antes de pedir nada al usuario.

---

## 🎯 PRÓXIMA TAREA (según este índice, sin esperar instrucción)

~~P1 — Sombras dinámicas~~ 🟢 completado.
~~P1 — Sonido de UI~~ 🟢 completado.
~~P2 — Retículas por categoría de arma~~ 🟢 completado.
~~P2 — Postprocesado ligero~~ 🟢 completado.
~~P2 — Sonido ambiente diferenciado por mapa~~ 🟢 completado.
~~P2 — Auditoría de rendimiento (draw calls, mallas huérfanas)~~ 🟢 completado. Sin fugas encontradas; ver `BULLET_OPS_PROGRESS.md`.
~~P2 — ADS "a través de la mira" (mejora sin modelo real)~~ 🟢 completado. Overlay de círculo de mira + retícula para SNIPER, viñeta para el resto.
~~P3 — Sonido dedicado de slide~~ 🟢 completado.
~~P3 — Segundo pase de props/detalle por mapa~~ 🟢 completado.
~~P4 — Barra de progreso de carga real~~ 🟢 completado.
~~P4 — Configuración gráfica (calidad/resolución)~~ 🟢 completado.

**Redirección de prioridad del usuario (esta sesión):** el sistema de armas pasa a ser prioridad P2 principal — ver FASE 4 reescrita arriba con tabla comparativa BF4/BFV/BF2042, taxonomía de 11 categorías y objetivo de roster. Completado en este ciclo: investigación + taxonomía + arquitectura de datos (`subcategory`/`ammoType`/`fireMode`) + 2 categorías nuevas sembradas y ampliadas (DMR 1→3/8 con BO-32/35/36, Revolver 1→3/4 con BO-52/56/57), roster total 35→41/82.

~~P2 — Ampliación Rocket/Launcher (2/6→4/6)~~ 🟢 completado. BO-63 BREACHPOINT (lanzagranadas ligero) + BO-64 LONGARM (anti-materiel pesado).

~~P2 — Ampliación Melee/Special (3/6→5/6 cada una)~~ 🟢 completado. BO-74 WRECKER + BO-75 TALONS, BO-84 RAILDRIVER + BO-85 WASP. Lección de metodología: viewmodel de prueba sin `parent = player.camera` da un falso negativo en el hit de melee — corregido y re-verificado, ver `BULLET_OPS_PROGRESS.md`.

**Siguiente**: seguir la ampliación de roster (FASE 4, P2) por la categoría más vacía en cada ciclo — tras este pase, DMR/Sniper (3/8 cada una) son las más cortas, seguidas de LMG/Escopetas (4/8). Reutilizar la plantilla ya validada (config +, si la categoría lo necesita, una rama de viewmodel nueva). El resto de items P4 (4º mapa, música de menú/partida, CUSTOMIZE bloqueado en skins) y Fase 10 multijugador siguen en pausa mientras dure esta prioridad.
