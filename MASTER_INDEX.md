# BULLET OPS — ÍNDICE MAESTRO DE DESARROLLO

Documento vivo de gestión autónoma del proyecto. Se actualiza en cada ciclo de trabajo (`ANALIZAR → PLANIFICAR → IMPLEMENTAR → PROBAR → CORREGIR → PULIR → ACTUALIZAR ÍNDICE → SIGUIENTE TAREA`). El detalle técnico de cada cambio (qué se hizo, por qué, cómo se probó) vive en `BULLET_OPS_PROGRESS.md` — este índice es el mapa de qué falta y en qué orden, no el changelog.

**Leyenda de estado:** 🔴 Pendiente · 🟡 En progreso · 🟢 Completado · 🔧 Funciona pero necesita mejora · 🔒 Bloqueado (requiere intervención del usuario) · ⚠️ Tiene errores conocidos
**Leyenda de prioridad:** P0 Crítico · P1 Muy importante · P2 Importante · P3 Pulido · P4 Opcional

Última actualización: sesión autónoma en curso (expansión de armas 15→35 completada, ver `BULLET_OPS_PROGRESS.md`).

---

## FASE 1 — BASE DEL PROYECTO

| Tarea | Estado | Prioridad | Notas |
|---|---|---|---|
| Arquitectura de archivo único (sin build step, compatible con Artifact) | 🟢 | — | Decisión técnica estable, no revisar sin motivo de peso |
| `WEAPON_CONFIGS` como fuente única de datos de armas | 🟢 | — | 35 armas, escalable por config |
| `WeaponController` (estado IDLE/RELOADING/SWITCHING/INSPECTING) | 🟢 | — | |
| `SoundSynth` (audio 100% sintetizado, sin assets externos) | 🟢 | — | |
| `SKIN_REGISTRY` / sistema de camuflajes | 🟢 | — | Solo 1 skin real + 1 patrón de prueba, ver FASE 4 |
| Gestión de memoria (fuga de materiales por disparo) | 🟢 | — | Corregido, materiales compartidos |
| Auditoría general de rendimiento (draw calls, mallas huérfanas) | 🔴 | P2 | No se ha hecho una pasada dedicada desde la expansión a 35 armas |
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
| IA de bots: usa las 35 armas (incl. melee/explosivo) | 🟢 | — | |

## FASE 4 — ARMAS (35 armas · 9 categorías)

| Categoría | Cantidad | Estado gameplay | Estado modelo/textura real |
|---|---|---|---|
| Fusiles de asalto | 5 | 🟢 | 🔒 placeholder procedural, sin GLB real |
| Subfusiles | 5 | 🟢 | 🔒 |
| Escopetas | 4 | 🟢 | 🔒 |
| Ametralladoras ligeras | 4 | 🟢 | 🔒 |
| Fusiles de francotirador | 4 | 🟢 | 🔒 (sin mira real modelada, ver FASE 5) |
| Pistolas | 5 | 🟢 | 🔒 |
| Lanzacohetes | 2 | 🟢 | 🔒 |
| Cuchillos / melee | 3 | 🟢 | 🔒 |
| Armas balísticas/especiales | 3 | 🟢 | 🔒 |

Por arma: modelo(🔒 real / 🟢 placeholder) → textura(🔒) → materiales(🟢 código) → animaciones(🟢 procedurales: equipar/disparo/recarga/ADS/sprint/inspección) → disparo(🟢) → recarga(🟢) → sonidos(🟢 sintetizados) → retroceso(🟢) → ADS(🟢) → estadísticas(🟢) → efectos(🟢) → testing(🟢). **Ningún arma nueva necesita trabajo de gameplay** — lo único pendiente en las 35 es el mismo bloqueo de siempre: modelos 3D/texturas reales.

| Tarea transversal | Estado | Prioridad |
|---|---|---|
| Attachments (arquitectura lista, sin poblar) | 🔒 | P3 — bloqueado en modelos reales |
| Camuflajes reales (solo 1 skin + 1 patrón de prueba) | 🔴 | P3 |
| Sonido de casquillos | 🔴 | P4 |
| Sonido de disparo con variación por distancia | 🔴 | P4 |

## FASE 5 — APUNTADO Y HUD

| Tarea | Estado | Prioridad | Notas |
|---|---|---|---|
| ADS (transición FOV/posición/sensibilidad) | 🟢 | — | |
| ADS "a través de la mira" real | 🔧 | P2 | Limitado por geometría placeholder sin mira modelada — documentado, requiere modelo real |
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
| BACKLOT-7 | 🟢 blockout | 🟢 propia | 🔧 mismo viento que los otros 2 | 🟢 básico | 🔴 no existen | 🔴 sin LOD/oclusión |
| INDUSTRIAL-5 | 🟢 blockout | 🟢 propia | 🔧 | 🟢 básico | 🔴 | 🔴 |
| OUTPOST-9 | 🟢 blockout (3 carriles) | 🟢 propia | 🔧 | 🟢 básico | 🔴 | 🔴 |

| Tarea transversal de mapas | Estado | Prioridad |
|---|---|---|
| Texturas de superficie reales (ahora color plano) | 🔒 | P3 — bloqueado en assets |
| Sombras dinámicas | 🟢 | — | Implementado con `ShadowGenerator` por mapa; ver `BULLET_OPS_PROGRESS.md` para el hallazgo de rendimiento en el entorno de pruebas (SwiftShader/software) y por qué no bloqueó la función |
| Sonido ambiente diferenciado por mapa | 🔴 | P2 |
| Segundo pase de props/detalle ambiental | 🔴 | P3 |
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
| Sonido dedicado de slide | 🔴 | P3 |
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
| Configuración gráfica (calidad, resolución) | 🔴 | P4 |
| Pantalla de carga | 🔧 | P4 — solo texto, sin barra de progreso ni animación |
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
| Auditoría de draw calls / mallas por partida larga | 🔴 | P2 | No hecha desde la expansión a 35 armas (más viewmodels precreados por loadout) |
| LOD | 🔴 | P4 | Geometría actual demasiado simple para necesitarlo aún |
| Oclusión / culling de mapas | 🔴 | P4 | Mapas pequeños, bajo impacto por ahora |

## FASE 12 — PULIDO FINAL

Revisión continua transversal. Elementos "de prototipo" detectados activamente y priorizados en las fases de arriba:
- ~~Sin sombras~~ — 🟢 corregido, ver FASE 6/8.
- ~~Brillo especular no deseado en superficies de mapa~~ — 🟢 corregido de paso al implementar sombras.
- ~~Sin sonido de UI~~ — 🟢 corregido, ver FASE 7/9.
- ~~Retícula única para 35 armas~~ — 🟢 corregido, ver FASE 5.
- ~~Sin postprocesado~~ — 🟢 corregido, ver FASE 8.
- **Retícula única para 35 armas** (FASE 5, P2).
- **Sin postprocesado** (FASE 8, P2).
- Resto de "prototipo" visual (texturas planas, modelos de bloques) está correctamente identificado como bloqueado en assets reales, no como negligencia — cada uno tiene ya su placeholder funcional documentado en `BULLET_OPS_PROGRESS.md`.

---

## 🎯 PRÓXIMA TAREA (según este índice, sin esperar instrucción)

~~P1 — Sombras dinámicas~~ 🟢 completado.
~~P1 — Sonido de UI~~ 🟢 completado.
~~P2 — Retículas por categoría de arma~~ 🟢 completado.
~~P2 — Postprocesado ligero~~ 🟢 completado.

Ya no quedan tareas P1 ni P2 abiertas de la lista original de esta fase. Auditoría de rendimiento (FASE 1/11) revisada de paso al investigar el coste de las sombras: `initGame()` solo puede ejecutarse una vez por carga de página (las dos rutas de "volver al menú" — resultados y pausa — hacen `location.reload()`), así que no existe riesgo de acumulación de escenas/mallas entre partidas; no se encontró ninguna fuga nueva. Sin más hallazgos de rendimiento que abordar por ahora.

**Siguiente**: sonido ambiente diferenciado por mapa (FASE 6/7, P2) — los 3 mapas usan exactamente el mismo bucle de viento. Se implementa a continuación en este mismo ciclo. Después: ADS real "a través de la mira" (bloqueado en modelo real — revisar si hay alguna mejora intermedia posible sin modelo, por ejemplo centrar mejor el placeholder).
