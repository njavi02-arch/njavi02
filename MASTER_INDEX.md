# BULLET OPS — ÍNDICE MAESTRO DE DESARROLLO

Documento vivo de gestión autónoma del proyecto. Se actualiza en cada ciclo de trabajo (`ANALIZAR → PLANIFICAR → IMPLEMENTAR → PROBAR → CORREGIR → PULIR → ACTUALIZAR ÍNDICE → SIGUIENTE TAREA`). El detalle técnico de cada cambio (qué se hizo, por qué, cómo se probó) vive en `BULLET_OPS_PROGRESS.md` — este índice es el mapa de qué falta y en qué orden, no el changelog.

**Leyenda de estado:** 🔴 Pendiente · 🟡 En progreso · 🟢 Completado · 🔧 Funciona pero necesita mejora · 🔒 Bloqueado (requiere intervención del usuario) · ⚠️ Tiene errores conocidos
**Leyenda de prioridad:** P0 Crítico · P1 Muy importante · P2 Importante · P3 Pulido · P4 Opcional

Última actualización: sesión autónoma en curso (roster de armas 68/82; prioridad actual: directiva del usuario sobre edificios/paredes/colisiones/balística, ver `BULLET_OPS_PROGRESS.md`).

---

## FASE 1 — BASE DEL PROYECTO

| Tarea | Estado | Prioridad | Notas |
|---|---|---|---|
| Arquitectura de archivo único (sin build step, compatible con Artifact) | 🟢 | — | Decisión técnica estable, no revisar sin motivo de peso |
| `WEAPON_CONFIGS` como fuente única de datos de armas | 🟢 | — | 64 armas (objetivo 82), escalable por config |
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
| Fusiles de asalto (AR) | ~10 | ~8 | 2 (base) | 12 | 🟡 11/12 |
| Subfusiles (SMG) | ~9 | ~6 | 4 | 10 | 🟡 9/10 |
| LMG | ~6 | ~5 | 2 | 8 | 🟡 6/8 |
| DMR (fusil de marcador) | ~5 | ~4 (autocargante) | 3 | 8 | 🟡 5/8 |
| Francotiradores (Sniper, cerrojo) | ~6 | ~6 (cerrojo) | 3 | 8 | 🟡 5/8 |
| Escopetas | ~5 | ~4 | 2 | 8 | 🟡 6/8 |
| Pistolas | ~8 | ~6 | 3 | 6 | 🟢 6/6 |
| Revólveres | (dentro de Pistolas en BF4/BFV) | (íd.) | (íd.) | 4 | 🟢 4/4 |
| Lanzadores | ~4 | ~3 | ~3 | 6 | 🟢 6/6 |
| Especiales/balísticos | — (no existe como categoría en ninguna entrega — decisión propia para armas futuristas/no convencionales) | — | — | 6 | 🟡 5/6 |
| Cuerpo a cuerpo (cuchillos + contundentes) | 1 (cuchillo genérico) | 1 | 1 | 6 | 🟡 5/6 |
| **Total** | ~65 (sin melee/gadgets) | ~48 | ~23 (base) | **82** | **68/82 (83%)** |

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

### Roster actual por categoría (64 armas · 11 categorías)

- **AR** (11/12): BO-01 VANGUARD, BO-02 PREDATOR, BO-03 STORMCALLER, BO-04 SENTINEL, BO-05 OUTLAW, BO-06 LANCER, BO-07 SKIRMISH, BO-08 TRIBURST, BO-09 DUALSTRIKE, BO-94 HAILSTORM, BO-95 JUDGMENT
- **SMG** (9/10): BO-11 RAZORBACK, BO-12 WHISPER, BO-13 ENFORCER, BO-14 VIPERBITE, BO-15 UNDERTOW, BO-16 PDW-9, BO-17 HUSH, BO-18 THREEPOINT, BO-19 DELUGE
- **Shotgun** (6/8): BO-21 BREACHER, BO-22 SCATTERGUN, BO-23 WIDOWMAKER, BO-24 SLUGSTORM, BO-25 RIOT-12, BO-26 SAWTOOTH
- **Sniper** (5/8): BO-31 LONGSHOT, BO-33 WRAITHFANG, BO-34 DEADEYE, BO-91 WHISPER-9, BO-92 COLOSSUS
- **DMR** (5/8): BO-32 PHANTOM, BO-35 RIDGELINE, BO-36 QUICKSILVER, BO-37 FALCONER, BO-38 IRONCLAD
- **LMG** (6/8): BO-41 JUGGERNAUT, BO-42 RAMPART, BO-43 OVERLORD, BO-44 VANDAL, BO-45 SIEGEBREAKER, BO-46 WHIRLWIND
- **Pistol** (6/6): BO-51 SIDEARM, BO-53 VIPER, BO-54 ECHO, BO-55 DUELIST, BO-58 TEMPEST, BO-59 GHOSTGRIP
- **Revolver** (4/4): BO-52 MAGNUM, BO-56 PEACEMAKER, BO-57 SNAKEEYE, BO-93 WILDCARD
- **Rocket** (6/6): BO-61 DEVASTATOR, BO-62 SKYFALL, BO-63 BREACHPOINT, BO-64 LONGARM, BO-65 STINGRAY, BO-66 CATACLYSM
- **Melee** (5/6): BO-71 FANG, BO-72 KARAMBIT, BO-73 CLEAVER, BO-74 WRECKER, BO-75 TALONS
- **Special** (5/6): BO-81 SILENTBOLT, BO-82 THUMPER, BO-83 HORNET, BO-84 RAILDRIVER, BO-85 WASP

| Tarea transversal | Estado | Prioridad |
|---|---|---|
| Attachments (arquitectura lista, sin poblar) | 🔒 | P3 — bloqueado en modelos reales |
| Camuflajes reales (solo 1 skin + 1 patrón de prueba) | 🔴 | P3 |
| Sonido de casquillos | 🔴 | P4 |
| Sonido de disparo con variación por distancia | 🔴 | P4 |
| Backfill subcategory/ammoType/fireMode en las 35 armas restantes | 🔴 | P3 |
| Ampliación de roster hacia el objetivo de 82 (ver tabla maestra) | 🟡 68/82 (83%) — en pausa mientras la directiva P0 de edificios/balística esté activa | |
| Burst fire / modos de disparo múltiples por arma | 🟢 | — | Mecánica real implementada (no solo metadato), ver sección siguiente |

### Alineación con la directiva de escala BF4 (redirección del usuario, sesión actual)

El usuario pidió convertir el sistema de armas en un shooter completo/profesional al estilo BF4 (escala, variedad, arquitectura), NO copiar ningún asset de Battlefield. Balance de lo pedido vs. lo ya resuelto:

**Ya satisfecho:**
- Arquitectura 100% data-driven (`WEAPON_CONFIGS`), cero duplicación de código por arma.
- Taxonomía de 11 categorías (AR/SMG/Shotgun/Sniper/DMR/LMG/Pistol/Revolver/Rocket/Melee/Special), con convención de rangos de id documentada.
- Tabla de escala referenciada en BF4/BFV/BF2042 (objetivo 82 armas), roster actual 68/82 (83%).
- Menú de armas moderno (nombre/categoría/imagen/daño/precisión/cadencia/movilidad/control/cargador/descripción).
- Slots de attachment (arquitectura declarada en `attachmentSlots`, sin poblar — bloqueado en modelos reales, correcto dejarlo así).
- Testing por Playwright contra el juego real tras cada bloque de armas, con dos lecciones de metodología documentadas (parenting de viewmodel, drift de IA de bots).
- **Modos de disparo reales, no solo descriptivos**: `fireMode` ahora tiene mecánica real de backing para full-auto/semi-auto/bolt-action/single-shot/break-action/double-action/single-action, y ráfaga real (`burstCount`/`burstInterval`, BO-08 TRIBURST 3 tiros, BO-09 DUALSTRIKE 2 tiros, verificado por Playwright).
- **Perdigones reales para shotguns**: `pelletCount`/`pelletDamage`/`pelletSpread` en las 5 shotguns de buckshot (BO-21/22/23/25/26), cada perdigón una bala independiente que reutiliza el sistema de colisión/headshot existente; BO-24 SLUGSTORM se mantiene como excepción deliberada de un solo slug. Verificado por Playwright (conteo de balas = `pelletCount` exacto en las 5, daño a bocajarro dentro de la banda esperada con headshot mezclado). Encontrado y corregido de paso un bug preexistente de rango (una bala podía impactar más allá de su `range` configurado en un fotograma de `deltaTime` grande) — ver `BULLET_OPS_PROGRESS.md`.
- **Caída de daño real por distancia**: `damageFalloff: {start, end, minMul}` aplicado a 3 armas representativas (BO-01 AR, BO-31 Sniper, BO-21 Shotgun), calculado sobre la distancia real en el punto de impacto (no la distancia total del fotograma — ver hallazgo de precisión en `BULLET_OPS_PROGRESS.md`). El mismo rediseño corrigió el corte de alcance para que ya no dependa de la distancia total del fotograma, más preciso a cualquier framerate.
- Armas de la misma categoría con arquetipos de juego genuinamente distintos (alto daño/baja cadencia vs. balanceado vs. alta precisión/cargador pequeño, etc.) — aplicado en cada ampliación de roster de esta sesión.

**Genuinamente pendiente (gaps reales, no solo más filas de datos):**
- ~~Número de perdigones + dispersión de perdigones para shotguns~~ 🟢 completado (`pelletCount`/`pelletDamage`/`pelletSpread`, ver sección siguiente). BO-24 SLUGSTORM se mantiene deliberadamente como excepción de un solo slug.
- ~~Caída de daño por distancia (damage falloff curve)~~ 🟡 mecánica implementada y probada en 3 armas representativas (AR/Sniper/Shotgun), pendiente de backfill al resto del roster — ver sección siguiente.
- Draw time / weapon-switch time por arma — actualmente `switchDuration` es global, no por arma.
- Distinción de recarga táctica vs. recarga por cargador vacío — actualmente `reloadTime`/`reloadTimeEmpty` ya distinguen tiempo, pero no hay diferencia de animación/comportamiento más allá del tiempo.
- Loadout con slots tipados PRIMARY/SECONDARY/LAUNCHER/MELEE — actualmente el loadout es "3 armas cualesquiera" sin restricción de slot.
- Pickup de armas en el mundo — no implementado (fuera de alcance por ahora, no bloqueante).
- Gravedad de proyectil (`projectileType` existe pero sin física de caída real para proyectiles no-hitscan salvo cohetes).

**Decisión de arquitectura de archivos (reafirmada):** el usuario pidió una estructura de carpetas `/assets/weapons/<categoría>/<arma>/{model,textures,animations,sounds,effects,data}/`. **No se implementa** porque el juego es un Artifact de un solo archivo HTML publicado vía Claude Artifacts — introducir carga de assets externos por carpeta rompería el flujo de publicación (`bullet-ops-game.html`, `favicon 🎯`, URL estable). La organización equivalente se mantiene dentro del archivo único vía agrupación por categoría en `WEAPON_CONFIGS`, comentarios de sección, y este mismo índice como catálogo de estado de producción por arma.

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
| BACKLOT-7 | 🟢 blockout | 🟢 propia | 🟢 propio (viento abierto, filtro 550Hz) | 🟢 PBR real (hormigón/ladrillo/madera/metal, ver PROGRESS) | 🟢 torre central con interior real, puerta real y rampa real al tejado (1/N edificios) | 🔴 sin LOD/oclusión |
| INDUSTRIAL-5 | 🟢 blockout | 🟢 propia | 🟢 propio (viento sordo 260Hz + zumbido de maquinaria) | 🟢 PBR real (hormigón/metal/metal oxidado) | 🟡 rampa real al walkway elevado | 🔴 |
| OUTPOST-9 | 🟢 blockout (3 carriles) | 🟢 propia | 🟢 propio (viento silbante 750Hz) | 🟢 PBR real (hormigón/madera/tierra) | 🟡 rampa real a centerPlatform (torre central/watchtower siguen sin rampa, ver PROGRESS) | 🔴 |
| KRYPTOS-URBAN | 🟢 construido desde plano táctico + vídeo de referencia del usuario (3 rutas + 2 respawns + 3 balizas de Hardpoint posicionadas, lógica de modo pendiente) | 🟢 propia (luz rasante cálida) | 🟢 propio | 🟡 PBR real (concreto/ladrillo/metal/asfalto/madera/cristal, ver PROGRESS) pero sin interiores reales todavía | 🟡 rampas reales a Control Tower/Warehouse (reemplazan escaleras que nunca funcionaron, ver PROGRESS) | 🔴 |

| Tarea transversal de mapas | Estado | Prioridad |
|---|---|---|
| Texturas de superficie reales (`BABYLON.PBRMaterial` con albedo real, no color plano) | 🟢 completado en los 4 mapas — ver `BULLET_OPS_PROGRESS.md`. Pendiente aparte: decals/grafitis/desgaste localizado (manchas, grietas puntuales) más allá de la variación ya dibujada en la propia textura procedural | P3 |
| Interiores reales en edificios accesibles | 🔴 P0 — directiva activa del usuario, ver PRÓXIMA TAREA | |
| Colisiones: auditoría completa pared/edificio/puerta/vehículo | 🟢 completado (jugador-vs-pared en los 3 mapas originales, ver `BULLET_OPS_PROGRESS.md`) — sin bugs encontrados, el sistema `moveWithCollisions`/`checkCollisions` ya funcionaba correctamente; puertas/vehículos no auditados por separado porque no existen como objetos interactivos todavía (hueco real, no bug) | |
| Balística: las balas NO deben atravesar paredes sólidas | 🟢 completado — bug real corregido y verificado (ver `BULLET_OPS_PROGRESS.md`): el raycast de entorno ahora se calcula antes del bucle de personajes y bloquea cualquier impacto cuya pared quede más cerca del tirador que el propio objetivo | |
| Penetración de balas por material (cristal fácil, madera con pérdida de daño, hormigón/metal grueso detienen la bala) | 🟢 completado — `PENETRATION_PROFILES` (hormigón/metal/tierra bloquean, cristal/madera penetran con pérdida de daño), `bullet.penetrationsLeft` evita que una bala atraviese infinitamente. Dos bugs reales encontrados y corregidos durante la implementación (auto-intersección tras penetrar, expiración de alcance justo tras penetrar), ver `BULLET_OPS_PROGRESS.md` | |
| Sombras dinámicas | 🟢 | — | Implementado con `ShadowGenerator` por mapa; ver `BULLET_OPS_PROGRESS.md` para el hallazgo de rendimiento en el entorno de pruebas (SwiftShader/software) y por qué no bloqueó la función |
| Sonido ambiente diferenciado por mapa | 🟢 | — | `MAP_AMBIENCE`, análogo a `MAP_LIGHTING` |
| Segundo pase de props/detalle ambiental | 🟢 | — | Ver `BULLET_OPS_PROGRESS.md`: dumpsters/palés/farolas, tanques/contenedores/tuberías, sacos de arena/rocas/antena por mapa |
| Un cuarto mapa / más contenido | 🟢 | — | KRYPTOS-URBAN, ver fila de arriba y `BULLET_OPS_PROGRESS.md` |

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
| Selector de arma / Loadout (68 armas) | 🟢 | — | Ahora visual (tarjetas + icono por categoría/nivel), no texto — ver FASE 14 |
| Catálogo de armas (WEAPONS) | 🟢 | — | Cuadrícula visual + detalle con previsualización 3D en vivo — ver FASE 14 |
| TIENDA (economía de skins) | 🟢 | — | Antes bloqueada tras "Próximamente"; ahora funcional (monedas ganadas jugando, compra/equipa skins reales) — ver FASE 14 |
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

## FASE 13 — SISTEMA VISUAL: PERSONAJES, EQUIPOS Y HUD (nueva prioridad del usuario, sesión actual)

El usuario pidió ampliar el desarrollo más allá del sistema de armas: personajes humanos 3D, dos equipos claramente diferenciados (Militar vs SWAT), sistema de skins BASE→EQUIPO→SKIN→VARIANTE, animaciones, separación primera/tercera persona, minimapa, crosshair clásico, impactos por material, sangre/feedback moderado, hitmarker, feedback de daño, HUD moderno, sistema de muerte/ragdoll, y optimización (LOD/pooling/instancing) — con una hoja de ruta explícita de 18 secciones/15 fases. Poco después llegó una segunda directiva pidiendo profundizar ADS/miras/accesorios/movimiento realista (mensaje cortado a mitad de frase en la transcripción — pendiente de releer completo cuando continúe).

Dado el tamaño real de esta petición (equivalente a varias sesiones de trabajo), este índice trackea el progreso fase a fase según el propio orden que pidió el usuario, sin intentar completarlo todo de una vez ni pedir permiso entre fases.

| Fase (según numeración del usuario) | Estado | Notas |
|---|---|---|
| 1 — Personaje humano base | 🟢 completado | `buildHumanoidCharacter()`: ~21 partes (cabeza/casco/torso/chaleco/mochila/brazos/antebrazos/guantes/muslos/gemelos/botas), proporciones humanas (no bloque robótico) en blockout de primitivas — mismo patrón "placeholder ahora, modelo real después" ya usado en armas/mapas |
| 2 — Sistema de equipos | 🟢 completado | `paletteForTeam()`: BLUE→SWAT, RED→MILITARY, sin equipo→paleta neutral + acento de color de operador (FFA) |
| 3 — Modelo militar | 🟢 completado | Paleta `CHARACTER_PALETTES.MILITARY` (oliva/tostado/táctico), aplicada a uniforme/chaleco/casco/mochila |
| 4 — Modelo SWAT | 🟢 completado | Paleta `CHARACTER_PALETTES.SWAT` (azul marino/negro táctico oscuro) |
| 5 — Sistema de skins | 🟢 completado | `CHARACTER_SKINS`: 10 variantes (5 Militar: Estándar/Desierto/Bosque/Urbano/Nocturno; 5 SWAT: Estándar/Urbano/Pesado/Táctico/Nocturno), mismo rig compartido, seleccionables y persistidas desde la pantalla OPERATORS. "SWAT Pesado" además escala el chaleco (`vestScale`), demostrando que una variante puede ir más allá del color sin tocar el rig |
| 6 — Animaciones | 🟡 parcial | `animateCharacter()`: locomoción real (idle/caminar/correr/agachado/salto-caída) en jugador y bots, mezclable entre capas. Disparo/recarga/melee/reacción-a-impacto/muerte quedan como siguiente incremento explícito (requieren alinear brazos con la dirección real de disparo, no un ciclo periódico) |
| 7 — Integración con armas | 🟡 parcial | El viewmodel de primera persona (brazos+arma) ya existe y es independiente del cuerpo en tercera persona (nunca se mezclaron) — falta sincronizar animaciones de tercera persona con el estado real del arma |
| 8 — HUD | 🟡 parcial | Vida/munición/arma/cargador ya existían; ahora suma minimapa + crosshair clásico + hitmarker mejorado + feedback de daño direccional (ver fases 9/10/13 y sección siguiente) — sigue faltando la parte de "objetivos" (no aplica, no hay modo con objetivos todavía) |
| 9 — Crosshair | 🟢 completado | Crosshair clásico de 4 líneas como base para AR/SMG/LMG/Sniper/DMR/Special, reactivo a spread real (idle/movimiento/disparo ya incluidos vía `getEffectiveSpread`/`spreadBloom`) y a ADS (desvanece). Shotgun/Rocket usan un anillo distinto; Pistola/Revólver/Melee solo punto central |
| 10 — Minimapa | 🟢 completado | Esquina inferior izquierda, tiempo real, jugador centrado y siempre "hacia arriba" (el mapa gira, no la flecha), compañeros de equipo visibles en TDM. Enemigos y objetivos deliberadamente no se muestran todavía (no existe mecánica de radar/objetivos en el proyecto) — tamaño/transparencia/zoom/posición configurables quedan para una fase posterior, tal y como pidió el usuario |
| 11 — Impactos | 🟢 completado | `spawnMaterialImpactEffect()` con 5 perfiles (metal/madera/hormigón/tierra/vidrio), aplicado a una muestra representativa de las 3 mapas (paredes/bases/torres/suelos=hormigón, cajas=madera, contenedores/fábrica=metal). `dirt`/`glass` funcionan pero no tienen superficie real todavía en ningún mapa (hueco documentado, no bug). Ver sección siguiente — de paso se implementó la primera colisión real bala-vs-entorno del juego |
| 12 — Sangre y feedback de impactos | 🔴 pendiente | Impacto en personaje actualmente reutiliza el efecto genérico de FASE 11, sin sangre/reacción física dedicada |
| 13 — Hitmarker | 🟡 parcial | `showHitmarker(isHeadshot)` ahora tiene una variante visual real de headshot (marca X más grande, rojo-naranja, más duración) además del sonido diferenciado ya existente — falta exponer tamaño/duración/color como opciones configurables por el usuario |
| 14 — Sistema de muerte/ragdoll | 🟢 completado | `playDeathPose()`/`resetDeathPose()`: caída procedural (no física real, no hay motor de físicas cargado) con variación aleatoria, en jugador y bots. Limpieza automática del cadáver reutiliza el temporizador de respawn ya existente (teleporta la cápsula, el cuerpo parentado va con ella) — ningún objeto de cadáver nuevo que gestionar |
| 15 — Optimización | 🟡 en progreso | Ya aplicado: caché de materiales por personaje (`characterMaterialCache`, evita 1 material nuevo por parte por personaje), subconjunto reducido de shadow casters por personaje (torso/cabeza/muslos, no las 21 partes) en vez de cada extremidad — LOD/instancing reales siguen pendientes hasta que el conteo de personajes lo justifique |

**Decisión de arquitectura clave**: el cuerpo humano se parenta a la cápsula de colisión ya existente (`entity.mesh`), que se vuelve invisible pero sigue siendo exactamente lo que usa todo el código de hit-detection/colisión/`moveWithCollisions` — cero cambios en esa lógica, capa puramente visual añadida encima. Esto preserva la regla de "no romper sistemas existentes" mientras se construye el sistema nuevo.

**Segunda directiva del usuario (ADS/miras/accesorios/movimiento realista)**: llegó truncada a mitad de frase ("...la cámara se alinee con el centro de la cámara, se" — corte de transcripción). El ADS ya existe (`isADS`/`adsAmount`, transición de posición/FOV/sensibilidad, overlay de mira/retícula para simular mirar a través de una mira sin modelo 3D real, ver FASE 5 más arriba) — la nueva petición parece pedir profundizarlo (alineación real del arma con el centro de cámara, preparación para accesorios/miras reales). Pendiente releer el mensaje completo cuando el usuario continúe para no malinterpretar el resto de la petición.

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

~~P2 — Ampliación DMR/Sniper (3/8→5/8 cada una)~~ 🟢 completado. BO-37 FALCONER + BO-38 IRONCLAD (DMR), BO-91 WHISPER-9 + BO-92 COLOSSUS (Sniper, nuevo techo de daño del juego). Segunda lección de metodología en la misma sesión: un bot sin IA congelada puede alejarse de la línea de tiro durante la rampa de ADS del test — reposicionar justo antes de disparar lo evita.

~~P2 — Ampliación LMG/Shotgun (4/8→6/8 cada una)~~ 🟢 completado. BO-45 SIEGEBREAKER + BO-46 WHIRLWIND (LMG), BO-25 RIOT-12 + BO-26 SAWTOOTH (Shotgun).

~~P2 — Ampliación Pistola/Rocket (4/6→6/6 cada una)~~ 🟢 completado. BO-58 TEMPEST + BO-59 GHOSTGRIP (Pistola), BO-65 STINGRAY + BO-66 CATACLYSM (Rocket). **Pistola y Rocket alcanzan su objetivo de 6/6 — completas.**

~~P2 — Roster de Revólveres (3/4→4/4)~~ 🟢 completado. BO-93 WILDCARD. **Pistola, Revolver y Rocket ya están completas (6/6, 4/4, 6/6)**; roster global en 58/82 (71%).

**Pausa deliberada de la ampliación pura de cantidad.** Seis ciclos consecutivos se dedicaron solo a añadir armas nuevas (35→58). El propio mandato del usuario (secciones 5-7 de sus instrucciones de esta sesión) pide revisión periódica de armas/mapas/movimiento, no solo cantidad — "quiero que cada arma se sienta diferente" y "mejora continua de los mapas" son tareas transversales, no un backlog aparte. Antes de seguir ampliando AR/SMG (las categorías con más hueco absoluto, 5/12 y 5/10), toca una pasada de calidad: revisar si las 58 armas actuales realmente se sienten distintas en juego (no solo en la tabla de stats) y si los 3 mapas siguen teniendo huecos visuales/de cobertura tras el pase de props de la FASE 6.

~~P2 — Revisión de sensación de armas en partida real~~ 🟢 completado. Cadencia real y pico de retroceso medidos con Playwright en 5 armas extremas (VANGUARD/IRONCLAD/COLOSSUS/WHIRLWIND/PEACEMAKER) vía `inputs.mouseDown` real — ambos órdenes coinciden exactamente con la configuración, confirmando distinción real en juego, no solo en datos. Nada plano encontrado, sin cambios de código necesarios. Ver `BULLET_OPS_PROGRESS.md`.

~~P2 — Ampliación AR (7/12→9/12)~~ 🟢 completado. BO-08 TRIBURST + BO-09 DUALSTRIKE. Roster global 62/82 (76%)→64/82 (78%).

~~P2 — Ampliación AR/SMG (9/12→11/12 AR, 7/10→9/10 SMG)~~ 🟢 completado y probado. BO-94 HAILSTORM + BO-95 JUDGMENT (AR), BO-18 THREEPOINT (primera SMG con ráfaga real, 3 tiros) + BO-19 DELUGE (SMG). Roster global 64/82 (78%)→68/82 (83%). Ver `BULLET_OPS_PROGRESS.md` para la verificación por Playwright.

~~P1 — Redirección del usuario: sistema de armas a escala BF4 (mecánica real, no solo metadatos)~~ 🟢 Primera mecánica real implementada esta sesión: **ráfaga de disparo real** (`burstCount`/`burstInterval`, máquina de estados `burstRemaining`/`burstTimer` en `WeaponController`), estrenada en BO-08 (3 tiros) y BO-09 (2 tiros), verificado por Playwright sin afectar a las 62 armas preexistentes. Ver sección "Alineación con la directiva de escala BF4" arriba en FASE 4 para el balance completo de lo satisfecho vs. lo pendiente.

~~P1 — Perdigones reales para shotguns (segunda mecánica real de la directiva BF4)~~ 🟢 completado. `pelletCount`/`pelletDamage`/`pelletSpread` en las 5 shotguns de buckshot (BO-21/22/23/25/26); cada perdigón es una bala independiente que reutiliza el sistema de colisión/headshot ya existente, sin lógica de impacto duplicada. BO-24 SLUGSTORM se mantiene como excepción deliberada (un solo slug, no perdigones). Verificado por Playwright: conteo de balas por disparo = `pelletCount` exacto en las 5 shotguns (9/10/12/8/14), BO-24 sigue disparando exactamente 1 bala, daño a bocajarro de BO-21 dentro de la banda esperada (63-81.9 según mezcla de headshots). De paso se encontró y corrigió un bug preexistente **no relacionado con perdigones**: una bala podía registrar impacto más allá de su `range` configurado si expiraba y pasaba cerca de un objetivo en el mismo fotograma de `deltaTime` grande — corregido con un guardián `bullet.life > 0` antes del bucle de impacto; regresión confirmada en AR/Rocket/Melee normales. Ver `BULLET_OPS_PROGRESS.md` para el detalle completo.

~~P1 — Caída de daño real por distancia (tercera mecánica real de la directiva BF4)~~ 🟢 completado en 3 armas representativas (AR/Sniper/Shotgun). De paso corregido un bug de precisión más serio: tanto la caída de daño como el corte de alcance usaban la distancia total del fotograma en vez de la distancia real en el punto de impacto — podía perder impactos válidos dentro de rango en un fotograma de `deltaTime` grande. Rediseñado para decidir el corte de rango por objetivo dentro del propio bucle de impacto. Ver `BULLET_OPS_PROGRESS.md`.

**Redirección mayor del usuario (esta sesión): sistema visual de personajes/equipos/HUD.** El usuario pidió ampliar el desarrollo mucho más allá de las armas — personajes humanos 3D, equipos Militar/SWAT, skins, animaciones, minimapa, crosshair clásico, impactos por material, sangre moderada, hitmarker, HUD moderno, sistema de muerte/ragdoll, optimización — con una hoja de ruta de 15 fases explícita, más una segunda directiva (llegó truncada) pidiendo profundizar ADS/miras/accesorios. Ver FASE 13 (nueva, arriba) para el detalle completo y la tabla de progreso por fase.

~~FASE 13, fases 1-4 — Personaje humano base + equipos Militar/SWAT~~ 🟢 completado. `buildHumanoidCharacter()` construye un cuerpo humano de ~21 partes (cabeza/casco/torso/chaleco/mochila/brazos/manos/piernas/botas) parentado a la cápsula de colisión existente (ahora invisible, sin cambiar ninguna lógica de hit-detection). Dos paletas de equipo (Militar oliva/táctico, SWAT azul marino/táctico oscuro) más una paleta neutral con acento de color de operador en FFA. Verificado por Playwright: 21 partes por personaje en jugador y bots, captura de pantalla confirma una silueta humana real (no un bloque) con sombra proyectada, y una prueba de regresión confirma que el daño sigue aplicándose correctamente (42 de daño exacto en un headshot de prueba) — la capa visual nueva no afectó ninguna lógica de combate existente.

~~FASE 13, fases 8-10 — HUD/crosshair clásico/minimapa~~ 🟢 completado. Minimapa circular inferior izquierdo (jugador centrado, mapa gira bajo una flecha fija, compañeros de equipo en TDM), crosshair clásico de 4 líneas para la mayoría de categorías (anillo para armas de patrón ancho, punto para sidearms de precisión), hitmarker con variante visual real de headshot, y feedback de daño direccional (flash + flecha hacia el origen del daño). Bug real encontrado y corregido durante esta tarea: una multiplicación `px * px` inválida en el CSS `calc()` del crosshair colapsaba las 4 líneas en una esquina en vez de repartirlas alrededor del centro — detectado por captura de pantalla, corregido, re-verificado. También corregida una colisión de layout real entre `#health` y el nuevo minimapa. Ver `BULLET_OPS_PROGRESS.md`.

~~FASE 13, fase 11 — Impactos por material~~ 🟢 completado. `spawnMaterialImpactEffect()` (5 perfiles) + primera colisión real bala-vs-entorno del juego (antes las balas atravesaban toda la geometría del mapa). Verificado con un raycast de control determinista (10/11 superficies etiquetadas acertadas exactamente, el único fallo un caso geométrico degenerado de la propia prueba) y una regresión completa de combate sin obstáculos (daño exacto, sin cambios). Ver `BULLET_OPS_PROGRESS.md`.

---

## FASE 14 — ARSENAL VISUAL: ARMAS/CREAR CLASE/TIENDA (directiva del usuario, sesión actual)

El usuario pidió que las pantallas de armas dejaran de mostrar texto plano y pasaran a ser un inventario visual real: tarjeta grande por arma (imagen→estado→info→nombre), previsualización/personalización, y una tienda funcional — con un registro central de armas que alimente todas las pantallas automáticamente, sin mantenimiento manual por pantalla, y sin usar ningún asset pirateado o copiado de otro juego.

| Tarea | Estado | Notas |
|---|---|---|
| Registro visual central (iconos por categoría/nivel, sin assets externos) | 🟢 completado | `CATEGORY_ICON_PARTS`/`CATEGORY_ACCENT`/`TIER_STYLE`/`weaponTier()`/`getWeaponIconDataURL()` — pictograma 2D procedural por categoría+nivel, cacheado, cero dependencia de imágenes reales de armas (que el proyecto no tiene y no puede generar sin herramienta de imágenes) |
| Previsualización 3D en vivo | 🟢 completado | Segundo motor Babylon ligado a `#weaponPreviewCanvas`, reutiliza el `buildWeaponViewmodel()`/`applySkin()` real del juego (no una maqueta aparte); rotación/zoom libres vía `ArcRotateCamera.attachControl()`; bucle de render se para al cerrar la pantalla |
| Pantalla ARMAS → cuadrícula visual | 🟢 completado | `#weaponsGrid`: 68 tarjetas agrupadas por categoría, cada una abre `#weaponDetailScreen` (preview 3D + stats + skins + equipar) |
| Pantalla CREAR CLASE → tarjetas visuales | 🟢 completado | `#loadoutSlots` visual, mecanismo prev/next ya existente conservado sin regresión |
| TIENDA funcional (economía de monedas + skins) | 🟢 completado | `playerCoins`/`ownedSkins`/`equippedSkins` persistentes, monedas ganadas jugando (no dinero real), `getEquippedSkin()` alimenta el arma real en combate — verificado que un skin comprado se ve de verdad en una partida real, no solo en el menú |
| Personalización real por punto de montaje (mira/cañón/cargador/etc. individuales) | 🔴 pendiente, hueco explícito | `ATTACHMENT_REGISTRY` sigue vacío/solo-arquitectura; no construido esta sesión |
| Animaciones idle/inspección en la previsualización 3D | 🔴 pendiente, hueco explícito | La preview solo rota libremente por arrastre, sin animación propia del arma |

**Decisión de alcance documentada**: la TIENDA vende camuflajes/skins cosméticos, no las 68 armas en sí — el loadout sigue siendo de acceso libre como ya lo era antes de esta sesión, para no introducir una regresión de una funcionalidad existente. Ver `BULLET_OPS_PROGRESS.md` para el detalle completo, incluida la evidencia de Playwright del flujo completo MENÚ→ARMAS→PREVIEW→CREAR CLASE→TIENDA→COMPRA→EQUIPAR→PARTIDA REAL.

~~Vídeo de introducción~~ 🟢 completado. `intro.mp4` (adjuntado por el usuario) se reproduce en una pantalla nueva antes del menú, con botones SKIP/UNMUTE y manejo defensivo de errores (nunca bloquea al jugador si el vídeo falla). Verificado con Playwright: el fallback de error se activó automáticamente ante un fallo real de decodificación H.264 en el Chromium de pruebas (sin decodificador H.264 en este sandbox — limitación del entorno de pruebas, no del código; el archivo es un MP4/H.264 estándar), y se confirmó el cableado de SKIP/`ended` por separado. El flujo PLAY tras la intro sigue funcionando con normalidad.

~~Rediseño del menú principal (estilo shooter AAA)~~ 🟡 completado en lo funcional, pendiente la imagen real. El usuario pidió (en 3 mensajes sucesivos, cada uno más detallado) un menú de nivel AAA: logo metálico, navegación lateral de 8 opciones (JUGAR/MULTIJUGADOR/PRÁCTICA/ARMAMENTO/OPERADORES/TIENDA/PASE DE BATALLA/AJUSTES), panel de jugador, tarjeta de novedades, indicador de servidores, atajos de teclado, todo sobre una foto de portada real que el usuario compartió dos veces en el chat. **Bloqueo real, no evitado por comodidad**: esa imagen llegó como contenido inline del chat, no como archivo adjunto — esta sesión solo puede leer bytes de archivos adjuntados explícitamente (como `intro.mp4`, que sí funcionó), no de imágenes pegadas en la conversación. Como el usuario pidió explícitamente no alterar ni sustituir la imagen, se dejó un fondo de marcador de posición (degradado oscuro) con el cambio de una línea ya preparado en el código, y se le explicó la limitación pidiéndole que la adjunte como archivo. El resto — estructura, navegación, las 8 opciones enrutadas honestamente (JUGAR/MULTIJUGADOR → panel de partida real; PRÁCTICA → FFA directo; ARMAMENTO/OPERADORES/AJUSTES → pantallas ya existentes; TIENDA/PASE DE BATALLA → bloqueadas de verdad, sin sistema de economía) — está completo y probado. Ver `BULLET_OPS_PROGRESS.md` para el detalle completo y la evidencia de pruebas.

~~FASE 13, fase 5 — Sistema de skins/variantes~~ 🟢 completado. 10 variantes (5 Militar + 5 SWAT), seleccionables/persistidas desde OPERATORS, mismo rig compartido. Bug real de caché de materiales encontrado y corregido durante la implementación (la clave de caché no incluía la variante, así que cambiar de skin no habría cambiado nada visualmente). Ver `BULLET_OPS_PROGRESS.md`.

~~FASE 13, fase 6 — Animaciones (locomoción)~~ 🟡 completado en lo esencial. `animateCharacter()`: ciclo de marcha real, agachado, salto/caída, todo mezclable, en jugador y bots — los cuerpos en tercera persona ya no son estáticos. Disparo/recarga/melee/reacción-a-impacto/muerte quedan como siguiente incremento explícito (requieren alinear brazos con la dirección real de disparo, no un ciclo periódico simple). Ver `BULLET_OPS_PROGRESS.md`.

~~FASE 13, fase 14 — Muerte/ragdoll~~ 🟢 completado. `playDeathPose()`/`resetDeathPose()`, caída procedural con variación aleatoria en jugador y bots, limpieza automática reutilizando el temporizador de respawn ya existente. De paso cubre parte del hueco de "muerte" que quedaba abierto en la fase 6 (animaciones). Ver `BULLET_OPS_PROGRESS.md`.

**Balance de FASE 13 tras esta tanda**: fases 1-6, 8-11 y 14 completadas (algunas parciales pero funcionales); quedan abiertas: fase 5 sigue sin variantes de skin de armas (solo de personaje), fase 7 (integración de animación con el estado real del arma: disparo/recarga/melee reflejados en los brazos de tercera persona) y fase 13 (opciones de configuración del hitmarker) son huecos menores; fase 15 (LOD/instancing real) sigue en pausa hasta que el número de personajes lo justifique.

~~Cuarto mapa: KRYPTOS-URBAN~~ 🟢 completado (geometría/gameplay TDM-FFA/materiales PBR reales/luz/sonido/UI). Construido desde el plano táctico + vídeo de referencia que el usuario proporcionó, siguiendo su directiva de 9 fases: respawns oeste/este, 3 rutas (izquierda CQB/centro objetivo/derecha mixta) siguiendo exactamente el plano, 3 balizas de Hardpoint posicionadas (lógica de modo de captura deliberadamente diferida, documentada), y la primera generación real de `BABYLON.PBRMaterial` (no solo color plano) del proyecto vía 6 funciones `makePBR*()` reutilizables. Probado con Playwright: 12 spawns sin caída fuera del mundo, 3 rutas recorridas con colisión de edificio real (bloquea sin tunneling), regresión limpia. Ver `BULLET_OPS_PROGRESS.md` para el detalle completo, incluida la técnica de extracción de fotogramas de vídeo sin ffmpeg (OpenCV) y el hallazgo del bug de serialización de `Vector3` en las propias pruebas.

~~Balística: bloqueo real de paredes + penetración por material~~ 🟢 completado, la pieza más crítica de la directiva P0 del usuario sobre edificios/paredes/colisiones/balística. El bug real confirmado leyendo el código (el hit-test de personajes se resolvía ANTES de comprobar el entorno, así que "ARMA → PARED → JUGADOR" hacía daño igualmente) está corregido: `envHit` se calcula antes del bucle de personajes y bloquea cualquier impacto cuya pared quede más cerca del tirador que el objetivo. Penetración real por material (`PENETRATION_PROFILES`: hormigón/metal/tierra bloquean, cristal/madera penetran con pérdida de daño) con `bullet.penetrationsLeft` garantizando que una bala nunca atraviesa infinitamente. Dos bugs reales encontrados y corregidos durante la propia implementación de la penetración (auto-intersección con la malla ya penetrada, expiración de alcance justo tras penetrar por `distanceTraveled` sin truncar) — ver `BULLET_OPS_PROGRESS.md` para las 9 pruebas de Playwright que verifican cada caso (bloqueado/despejado/penetración reducida/doble penetración bloqueada/pared irrelevante/regresión melee+explosivo+mapa real).

~~Materiales PBR reales extendidos a los 4 mapas~~ 🟢 completado. Los 6 helpers `makePBR*()` (antes solo en KRYPTOS-URBAN) ahora cubren BACKLOT-7/INDUSTRIAL-5/OUTPOST-9 también — hormigón/ladrillo/madera/metal(+variante oxidada) según cada mapa, más varias estructuras grandes que no tenían ninguna etiqueta de impacto antes de esta pasada (ahora sí) y el primer uso real del perfil `dirt` en todo el proyecto (rocas de OUTPOST-9). Ver `BULLET_OPS_PROGRESS.md` para el detalle y la verificación por Playwright.

~~Primer interior real: torre central de BACKLOT-7~~ 🟢 completado (fase 1). La torre sólida de una pieza se sustituye por 4 paredes reales con un hueco de puerta de 3 unidades — el jugador entra caminando de verdad y la sala está delimitada por paredes que bloquean desde fuera, verificado por Playwright. **Hallazgo real de esta fase**: el sistema de movimiento no tiene ninguna tolerancia de pendiente/escalón (`moveWithCollisions()` puro, sin controlador de personaje dedicado) — tanto una escalera de peldaños como una rampa inclinada probadas para dar acceso a la azotea de la plataforma elevada dejaban al jugador bloqueado/oscilando sin poder subir; retirada la rampa no funcional en vez de dejarla a medias. Limitación real y preexistente de todo el sistema (ya afectaba a la plataforma de BACKLOT-7, el walkway de INDUSTRIAL-5 y las torres de OUTPOST-9 antes de esta sesión), documentada explícitamente, no oculta. Ver `BULLET_OPS_PROGRESS.md`.

**Resto de la directiva P0 (edificios/paredes/colisiones/balística)** — balística, colisión jugador-vs-pared, materiales/PBR, el primer interior real, y el controlador de movimiento con tolerancia de pendiente/escalón ya están resueltos y verificados, incluyendo rampas reales conectando el walkway de INDUSTRIAL-5 y la `centerPlatform` de OUTPOST-9. Queda como trabajo futuro explícito: interiores reales en más edificios (Control Tower/Warehouse/Office de KRYPTOS-URBAN, estructura de fábrica de INDUSTRIAL-5) y una rampa en zigzag/varios tramos para la torre central (10 unidades) y el `watchtower` (14 unidades) de OUTPOST-9 — demasiado altas para una rampa recta de un solo tramo con ángulo caminable dentro del espacio disponible del mapa.

~~Controlador de movimiento: tolerancia real de pendiente/escalón~~ 🟢 completado. Causa raíz real identificada (no una limitación de `moveWithCollisions()`, que sí desliza correctamente por superficies inclinadas, sino el paso siguiente: un `groundLevel` de altura fija que cancelaba cualquier elevación ganada por esa colisión, forzando al jugador de vuelta abajo cada fotograma). Corregido con un nuevo registro `WALKABLE_SURFACES` (mismo patrón opt-in que `IMPACT_SURFACES`) y un rayo hacia abajo que sigue la altura real de cualquier superficie etiquetada, con una tolerancia de 0.6 unidades por fotograma (subida y bajada) — el suelo plano base de cada mapa no cambia en absoluto, cero riesgo de regresión ahí. Probado primero en aislamiento (ascenso continuo sin oscilar, caída correcta al salir de una plataforma sin barandilla) y luego en la rampa real de BACKLOT-7, reconstruida y ahora funcional (antes retirada por no funcionar). Regresión de suelo plano/pared/salto/puerta-del-interior/68-armas confirmada limpia. Ver `BULLET_OPS_PROGRESS.md` para el detalle completo.

~~Rampas reales en INDUSTRIAL-5 (walkway) y OUTPOST-9 (centerPlatform)~~ 🟢 completado. Mismo patrón que BACKLOT-7, con el signo de rotación de la rampa verificado en aislamiento antes de aplicarlo a geometría real (la rampa de OUTPOST-9 necesitaba subir en dirección -z, opuesta a la de BACKLOT-7/INDUSTRIAL-5). Ambas probadas con Playwright: ascenso limpio hasta la altura exacta esperada en los dos mapas, sin oscilación real durante la subida (la caída posterior al cruzar cada plataforma sin barandilla es comportamiento físico esperado, no un bug). La torre central y el `watchtower` de OUTPOST-9 quedan deliberadamente fuera de esta pasada — su altura (10/14 unidades) necesitaría una rampa en zigzag, un incremento de diseño mayor, no forzado en el primer hueco disponible. Ver `BULLET_OPS_PROGRESS.md`.

~~Bug real corregido: las "escaleras" de KRYPTOS-URBAN (Control Tower/Warehouse) nunca funcionaron~~ 🟢 completado. `addStairs()` (peldaños discretos) llevaba desde la construcción del mapa afirmando sin verificar que funcionaba "igual que cualquier rampa" — probado ahora por primera vez, confirmado que el jugador apenas sube unos centímetros del primer peldaño (~1.22 unidades de subida por peldaño, muy por encima de cualquier tolerancia razonable) antes de deslizarse alrededor de toda la escalera. Reemplazadas ambas por rampas reales (`addRampZ()`, función reutilizable que generaliza el patrón ya probado 3 veces) — Control Tower desde el sur hasta la azotea, Warehouse desde el campo sur hasta el walkway elevado, ambos destinos ahora también etiquetados transitables. Probado con Playwright: ascenso limpio a la altura exacta esperada en ambos casos, 68 armas intactas, sin errores nuevos. Ver `BULLET_OPS_PROGRESS.md`.

**Pendiente aparte (menor prioridad)**: en cuanto el usuario adjunte la imagen de portada del menú como archivo, integrarla en `#menuBg`. Releer el mensaje truncado de ADS/miras cuando el usuario lo continúe, antes de tocar el ADS existente de `WeaponController`.

~~Arsenal visual: ARMAS/CREAR CLASE/TIENDA~~ 🟢 completado — ver FASE 14 (nueva, arriba) para el detalle completo. Registro visual central sin assets externos (iconos procedurales por categoría/nivel), previsualización 3D en vivo reutilizando el viewmodel real del juego, cuadrícula visual en ARMAS/CREAR CLASE, y una TIENDA funcional con economía de monedas ganadas jugando. Verificado end-to-end con Playwright (flujo completo MENÚ→ARMAS→PREVIEW→CREAR CLASE→TIENDA→COMPRA→EQUIPAR→PARTIDA REAL, incluida la confirmación de que un skin comprado se aplica de verdad al material del arma en combate real, no solo en el menú). Huecos explícitos que quedan abiertos: personalización real por punto de montaje (mira/cañón/cargador/etc., `ATTACHMENT_REGISTRY` sigue vacío) y animaciones idle/inspección en la previsualización 3D — ver `BULLET_OPS_PROGRESS.md` para el detalle honesto de ambos.

~~Controlador de movimiento con tolerancia de pendiente/escalón~~ 🟢 completado — ver FASE 6 arriba para el detalle y `BULLET_OPS_PROGRESS.md` para la causa raíz y las pruebas.

~~Rampas reales en INDUSTRIAL-5 y OUTPOST-9~~ 🟢 completado — ver FASE 6 arriba y `BULLET_OPS_PROGRESS.md`.

~~Bug real: escaleras de KRYPTOS-URBAN nunca funcionaron, reemplazadas por rampas reales~~ 🟢 completado — ver FASE 6 arriba y `BULLET_OPS_PROGRESS.md`.

**🎯 Próxima tarea real, sin esperar instrucción**: con los 4 mapas ya con al menos una superficie elevada realmente accesible caminando, el hueco de mayor prioridad que queda de la directiva P0 de edificios/paredes es dar interiores reales a más edificios (Office/Apartment Block de KRYPTOS-URBAN, estructura de fábrica de INDUSTRIAL-5), siguiendo el mismo patrón ya verificado en la torre de BACKLOT-7. La rampa en zigzag para la torre central/watchtower de OUTPOST-9 queda como alternativa de menor prioridad (afecta a un solo mapa, no a varios). Se abordará como siguiente incremento verificado de principio a fin, salvo que llegue una nueva directiva del usuario con prioridad distinta.
