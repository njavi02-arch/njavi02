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

Ya no quedan tareas P0/P1/P2 abiertas en el índice en este momento. Todo lo restante es P3/P4 o está bloqueado en assets reales (🔒).

**Siguiente**: segundo pase de props/detalle ambiental por mapa (FASE 6, P3) — los 3 mapas tienen cobertura básica pero podrían beneficiarse de más variedad de props dispersos (no solo cajas/barriles repetidos) para romper la monotonía visual. Después: revisar candidatos P4 restantes (pantalla de carga con barra real, configuración gráfica, 4º mapa).
