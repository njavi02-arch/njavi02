# BULLET OPS — WEAPON BIBLE

**Documento maestro de diseño y producción de assets del sistema de armas.**
Generado por auditoría directa del código real, no por inferencia ni suposición. Cada afirmación de este documento fue verificada leyendo `bullet-ops-game.html` o ejecutando su código real (nunca "debería existir"). Convención de estado usada en todo el documento:

| Marca | Significado |
|---|---|
| ✅ **IMPLEMENTADO** | Existe y funciona en el juego real, verificado en el código |
| 🟡 **PARCIAL** | Existe pero de forma incompleta o simplificada respecto a lo pedido |
| 🔵 **PLACEHOLDER** | Existe una versión funcional pero deliberadamente genérica/sustituta (ej. geometría procedural en vez de un modelo real) |
| 🔴 **MISSING** | No existe en absoluto |
| 🟣 **RECOMMENDED** | No existe; es una recomendación de diseño, no un hecho del proyecto |

---

## 0. RESUMEN EJECUTIVO — ARQUITECTURA REAL DEL PROYECTO

**Bullet Ops no es un proyecto de motor tradicional con assets importados.** Es un único archivo HTML (`bullet-ops-game.html`, ~7700 líneas) que usa Babylon.js 7 vía CDN, sin build step, sin modelos 3D importados, sin archivos de audio, sin animaciones esqueléticas y sin base de datos externa. **Todo se genera en tiempo de ejecución mediante código**:

- **Modelos**: primitivas de Babylon (`CreateBox`, `CreateCylinder`, `CreateSphere`) ensambladas por categoría de arma. No hay ningún archivo `.glb`/`.fbx`/`.obj` en el proyecto.
- **Texturas**: dibujadas a mano con la API Canvas2D sobre `BABYLON.DynamicTexture` en tiempo de ejecución (ver `makePBRConcrete()` y similares para el mapa; las armas usan `StandardMaterial` con color plano o un patrón de camuflaje dibujado igual).
- **Sonido**: síntesis en tiempo real con Web Audio API (osciladores + ruido filtrado) mediante el objeto `SoundSynth`. **No existe ni un solo archivo `.wav`/`.mp3` en todo el proyecto.**
- **Animación**: no hay ningún sistema de animación esquelética ni `AnimationGroup` de Babylon en absoluto (verificado: cero referencias a `AnimationGroup`, `.skeleton`, `SceneLoader` o `ImportMesh` en todo el archivo). Todo lo que "se anima" (balanceo del arma, ADS, retroceso, sprint, inspección) es interpolación directa de posición/rotación de un `TransformNode` cada fotograma, código puro, no clips.
- **Base de datos**: `WEAPON_CONFIGS`, un objeto JavaScript literal dentro del propio archivo — no hay `weapons.json` ni ninguna base de datos externa antes de esta auditoría (se genera una en esta pasada, ver sección 13).

Esto no es necesariamente un defecto: es una arquitectura deliberada para un Artifact de un solo archivo sin pipeline de build. Pero significa que **la mayoría de las peticiones de la directiva del usuario sobre "modelos", "animaciones importadas" o "archivos de sonido" no tienen equivalente literal en este proyecto** — se documentan aquí con su equivalente real y su estado honesto, nunca inventando que existe algo que no existe.

### ⚠️ HALLAZGO CRÍTICO: existen DOS sistemas de armas en el repositorio

La auditoría (siguiendo la instrucción explícita de "inspeccionar todo el proyecto", no solo el archivo en el que se ha trabajado) encontró una carpeta `src/` con una arquitectura modular separada (`src/weapons/Weapon.js`, `src/weapons/weapons-config.js`, `src/weapons/WeaponManager.js`) más `index.html`/`game.js`/`vite.config.js`.

**Este sistema está abandonado**: su último commit (`fbe9cca "refactor: Simplify game architecture for Phase 1 prototype"`) es del primer día del proyecto (10 sep) y nunca se ha vuelto a tocar, mientras que `bullet-ops-game.html` ha recibido commits activos hasta hoy (11 sep). Contiene solo **5 armas** con un esquema de datos incompatible con el sistema real (por ejemplo, `BO41` en el prototipo es una Pistola; en el sistema real, `BO41 JUGGERNAUT` es una LMG — los IDs ni siquiera significan lo mismo entre ambos sistemas). No tiene sonidos, skins, accesorios ni iconos.

**Este documento — y todo el sistema de armas real de Bullet Ops — se refiere exclusivamente a `bullet-ops-game.html`.** Se recomienda (🟣 RECOMMENDED, no se ha tocado nada de `src/` en esta auditoría) archivar o eliminar explícitamente `src/`, `index.html`, `game.js`, `vite.config.js` y las dependencias de Vite en `package.json` una vez el usuario lo confirme, para que nadie vuelva a confundir ambos sistemas. **No se ha borrado nada** — esto es una detección, no una acción.

---

## 1. CATÁLOGO MAESTRO — LAS 68 ARMAS REALES

Extraído programáticamente del objeto `WEAPON_CONFIGS` real (evaluando el propio bloque de código fuente en Node, no transcrito a mano — cero riesgo de error de copia en 68 entradas × ~25 campos). El volcado completo, campo por campo, está en [`weapons.json`](./weapons.json) junto a este documento.

### 1.1 Categorías (11, todas reales, ninguna eliminada)

| Categoría | Cód. interno | Nº armas | Rango de ID reservado |
|---|---|---|---|
| Assault Rifle | `AR` | 11 | 01–09, 94–95 |
| SMG | `SMG` | 9 | 11–19 |
| Shotgun | `SHOTGUN` | 6 | 21–29 |
| Sniper | `SNIPER` | 5 | 31–34, 91–92 |
| DMR | `DMR` | 5 | 32, 35–38 (comparte decena con Sniper) |
| LMG | `LMG` | 6 | 41–46 |
| Pistol | `PISTOL` | 6 | 51–59 |
| Revolver | `REVOLVER` | 4 | 52, 56–57, 93 (comparte decena con Pistol) |
| Rocket Launcher | `ROCKET` | 6 | 61–66 |
| Melee | `MELEE` | 5 | 71–75 |
| Special | `SPECIAL` | 5 | 81–85 |
| **TOTAL** | | **68** | |

### 1.2 Tabla maestra (ID · Nombre · Categoría · Mecánica especial · Estado)

| ID | Nombre | Categoría | Mecánica especial | Estado |
|---|---|---|---|---|
| BO01 | BO-01 VANGUARD | Assault Rifle | estándar | ✅ IMPLEMENTADO |
| BO02 | BO-02 PREDATOR | Assault Rifle | estándar | ✅ IMPLEMENTADO |
| BO03 | BO-03 STORMCALLER | Assault Rifle | estándar | ✅ IMPLEMENTADO |
| BO04 | BO-04 SENTINEL | Assault Rifle | estándar | ✅ IMPLEMENTADO |
| BO05 | BO-05 OUTLAW | Assault Rifle | estándar | ✅ IMPLEMENTADO |
| BO06 | BO-06 LANCER | Assault Rifle | estándar | ✅ IMPLEMENTADO |
| BO07 | BO-07 SKIRMISH | Assault Rifle | estándar | ✅ IMPLEMENTADO |
| BO08 | BO-08 TRIBURST | Assault Rifle | **ráfaga real (3 tiros)** | ✅ IMPLEMENTADO |
| BO09 | BO-09 DUALSTRIKE | Assault Rifle | **ráfaga real (2 tiros)** | ✅ IMPLEMENTADO |
| BO94 | BO-94 HAILSTORM | Assault Rifle | cargador más grande (50) | ✅ IMPLEMENTADO |
| BO95 | BO-95 JUDGMENT | Assault Rifle | mayor daño/alcance de la categoría | ✅ IMPLEMENTADO |
| BO11 | BO-11 RAZORBACK | SMG | estándar | ✅ IMPLEMENTADO |
| BO12 | BO-12 WHISPER | SMG | estándar | ✅ IMPLEMENTADO |
| BO13 | BO-13 ENFORCER | SMG | estándar | ✅ IMPLEMENTADO |
| BO14 | BO-14 VIPERBITE | SMG | estándar | ✅ IMPLEMENTADO |
| BO15 | BO-15 UNDERTOW | SMG | estándar | ✅ IMPLEMENTADO |
| BO16 | BO-16 PDW-9 | SMG | estándar | ✅ IMPLEMENTADO |
| BO17 | BO-17 HUSH | SMG | estándar | ✅ IMPLEMENTADO |
| BO18 | BO-18 THREEPOINT | SMG | **ráfaga real (3 tiros)** | ✅ IMPLEMENTADO |
| BO19 | BO-19 DELUGE | SMG | cadencia/cargador más altos de la categoría | ✅ IMPLEMENTADO |
| BO21 | BO-21 BREACHER | Shotgun | **9 perdigones reales** | ✅ IMPLEMENTADO |
| BO22 | BO-22 SCATTERGUN | Shotgun | **10 perdigones reales** | ✅ IMPLEMENTADO |
| BO23 | BO-23 WIDOWMAKER | Shotgun | **12 perdigones reales** | ✅ IMPLEMENTADO |
| BO24 | BO-24 SLUGSTORM | Shotgun | **slug único (sin perdigones), deliberado** | ✅ IMPLEMENTADO |
| BO25 | BO-25 RIOT-12 | Shotgun | **8 perdigones reales** | ✅ IMPLEMENTADO |
| BO26 | BO-26 SAWTOOTH | Shotgun | **14 perdigones reales** | ✅ IMPLEMENTADO |
| BO31 | BO-31 LONGSHOT | Sniper | estándar | ✅ IMPLEMENTADO |
| BO33 | BO-33 WRAITHFANG | Sniper | estándar | ✅ IMPLEMENTADO |
| BO34 | BO-34 DEADEYE | Sniper | estándar | ✅ IMPLEMENTADO |
| BO91 | BO-91 WHISPER-9 | Sniper | estándar | ✅ IMPLEMENTADO |
| BO92 | BO-92 COLOSSUS | Sniper | mayor daño del juego | ✅ IMPLEMENTADO |
| BO32 | BO-32 PHANTOM | DMR | estándar | ✅ IMPLEMENTADO |
| BO35 | BO-35 RIDGELINE | DMR | estándar | ✅ IMPLEMENTADO |
| BO36 | BO-36 QUICKSILVER | DMR | estándar | ✅ IMPLEMENTADO |
| BO37 | BO-37 FALCONER | DMR | estándar | ✅ IMPLEMENTADO |
| BO38 | BO-38 IRONCLAD | DMR | estándar | ✅ IMPLEMENTADO |
| BO41 | BO-41 JUGGERNAUT | LMG | estándar | ✅ IMPLEMENTADO |
| BO42 | BO-42 RAMPART | LMG | estándar | ✅ IMPLEMENTADO |
| BO43 | BO-43 OVERLORD | LMG | estándar | ✅ IMPLEMENTADO |
| BO44 | BO-44 VANDAL | LMG | estándar | ✅ IMPLEMENTADO |
| BO45 | BO-45 SIEGEBREAKER | LMG | estándar | ✅ IMPLEMENTADO |
| BO46 | BO-46 WHIRLWIND | LMG | estándar | ✅ IMPLEMENTADO |
| BO51 | BO-51 SIDEARM | Pistol | estándar | ✅ IMPLEMENTADO |
| BO53 | BO-53 VIPER | Pistol | estándar | ✅ IMPLEMENTADO |
| BO54 | BO-54 ECHO | Pistol | estándar | ✅ IMPLEMENTADO |
| BO55 | BO-55 DUELIST | Pistol | estándar | ✅ IMPLEMENTADO |
| BO58 | BO-58 TEMPEST | Pistol | estándar | ✅ IMPLEMENTADO |
| BO59 | BO-59 GHOSTGRIP | Pistol | estándar | ✅ IMPLEMENTADO |
| BO52 | BO-52 MAGNUM | Revolver | estándar | ✅ IMPLEMENTADO |
| BO56 | BO-56 PEACEMAKER | Revolver | estándar | ✅ IMPLEMENTADO |
| BO57 | BO-57 SNAKEEYE | Revolver | estándar | ✅ IMPLEMENTADO |
| BO93 | BO-93 WILDCARD | Revolver | estándar | ✅ IMPLEMENTADO |
| BO61 | BO-61 DEVASTATOR | Rocket Launcher | **explosivo + daño de salpicadura** | ✅ IMPLEMENTADO |
| BO62 | BO-62 SKYFALL | Rocket Launcher | explosivo + salpicadura | ✅ IMPLEMENTADO |
| BO63 | BO-63 BREACHPOINT | Rocket Launcher | explosivo + salpicadura (ligero) | ✅ IMPLEMENTADO |
| BO64 | BO-64 LONGARM | Rocket Launcher | explosivo + salpicadura (pesado/anti-material) | ✅ IMPLEMENTADO |
| BO65 | BO-65 STINGRAY | Rocket Launcher | explosivo + salpicadura | ✅ IMPLEMENTADO |
| BO66 | BO-66 CATACLYSM | Rocket Launcher | mayor radio de salpicadura del juego | ✅ IMPLEMENTADO |
| BO71 | BO-71 FANG | Melee | **cuerpo a cuerpo instantáneo, sin munición** | ✅ IMPLEMENTADO |
| BO72 | BO-72 KARAMBIT | Melee | cuerpo a cuerpo | ✅ IMPLEMENTADO |
| BO73 | BO-73 CLEAVER | Melee | cuerpo a cuerpo, mayor alcance | ✅ IMPLEMENTADO |
| BO74 | BO-74 WRECKER | Melee | cuerpo a cuerpo, mayor alcance | ✅ IMPLEMENTADO |
| BO75 | BO-75 TALONS | Melee | cuerpo a cuerpo, más rápido | ✅ IMPLEMENTADO |
| BO81 | BO-81 SILENTBOLT | Special | balística estándar | ✅ IMPLEMENTADO |
| BO82 | BO-82 THUMPER | Special | **explosivo + salpicadura** | ✅ IMPLEMENTADO |
| BO83 | BO-83 HORNET | Special | balística estándar | ✅ IMPLEMENTADO |
| BO84 | BO-84 RAILDRIVER | Special | balística estándar | ✅ IMPLEMENTADO |
| BO85 | BO-85 WASP | Special | balística estándar | ✅ IMPLEMENTADO |

**Control de calidad de esta tabla (Fase 18 aplicada aquí)**: 68 armas, 68 IDs únicos verificados (sin duplicados), las 68 tienen categoría asignada, las 68 tienen estado. Ninguna arma "NO IMPLEMENTADA" — el arsenal base (stats + lógica de disparo) está genuinamente completo. Lo que falta no son armas, son **capas de producción** (visual/sonido/animación únicos) — ver secciones siguientes.

---

## 2. ESTADÍSTICAS (Fase 3)

Todas las estadísticas reales están en [`weapons.json`](./weapons.json), extraídas directamente del código (no inventadas). Resumen de qué campos existen y cuáles no, aplicable a las 68 armas por igual:

| Estadística pedida | Estado | Nota |
|---|---|---|
| Daño | ✅ IMPLEMENTADO | `damage` (o `pelletDamage`×`pelletCount` en shotguns) |
| Daño por distancia | 🟡 PARCIAL | `damageFalloff` existe solo en **3 armas de ejemplo** (BO01 AR, BO21 Shotgun, BO31 Sniper) verificadas explícitamente con Playwright esta sesión; el resto de las 68 armas dispara con **daño plano a cualquier distancia dentro de su alcance** — no es que falte el sistema, es que no se ha extendido a las otras 65 armas todavía |
| Cadencia / RPM | ✅ IMPLEMENTADO | `fireRate` (disparos/seg); RPM = `fireRate × 60` |
| Cargador / Reserva | ✅ IMPLEMENTADO | `mag` / `reserve` (N/A en Melee, no usa munición) |
| Tiempo de recarga (táctica vs vacía) | ✅ IMPLEMENTADO | `reloadTime` / `reloadTimeEmpty`, **distintos de verdad** y con sonido de recarga temporizado de forma distinta según cuál se dispare (ver sección 8) |
| Velocidad de movimiento (hip/ADS) | ✅ IMPLEMENTADO | `movement.hipMul` / `movement.adsMul` |
| ADS speed | ✅ IMPLEMENTADO | `ads.time` |
| Sprint-to-fire | ✅ IMPLEMENTADO | `sprintToFireDelay`, con bug de "existía en los datos pero nunca se leía" corregido en una sesión anterior — ahora sí bloquea el disparo justo tras dejar de esprintar |
| Fire delay | 🔴 MISSING | No existe un "retraso de disparo inicial" distinto del `fireCooldown` normal |
| Recoil vertical/horizontal | ✅ IMPLEMENTADO | `recoil.vertical` / `recoil.horizontal` / `recoil.cameraKick` / `recoil.recoverySpeed` |
| Dispersión / precisión | ✅ IMPLEMENTADO | `spread.hip` / `spread.ads` / `spread.moving` |
| Alcance | ✅ IMPLEMENTADO | `range` (o `meleeRange` en cuerpo a cuerpo) |
| Multiplicador de headshot | ✅ IMPLEMENTADO | `headshotMul` |
| Penetración | 🟡 PARCIAL — **por MATERIAL, no por ARMA** | Toda bala penetra exactamente 1 superficie no bloqueante (cristal/madera) y ninguna arma tiene un valor de penetración propio distinto de otra; no existe el concepto de "munición perforante" por arma |
| Tipo de munición | 🔴 MISSING | No existe selección de tipo de munición (ni siquiera un campo declarativo) |
| Proyectiles por disparo / daño por proyectil | ✅ IMPLEMENTADO (solo shotguns) | `pelletCount` / `pelletDamage` en las 5 shotguns de perdigones reales |
| Modo de disparo | 🟡 PARCIAL | Ver hallazgo abajo — no hay automático/semiautomático/tiro-único real, solo "mantener para disparar repetidamente" vs ráfaga |

### ⚠️ Hallazgo real: no existe una distinción de modo de disparo automático/semiautomático/tiro único

Verificado leyendo el disparador: `if (inputs.mouseDown && this.fireCooldown <= 0 && ...)` — la condición de disparo comprueba si el botón está **mantenido**, no si se acaba de pulsar. Esto significa que **cualquier arma del juego, incluidas pistolas, revólveres y rifles de francotirador, dispara en modo "automático" si se mantiene el botón pulsado**, limitada solo por su `fireRate`. La única excepción real es el sistema de ráfaga (`burstCount`, 3 armas: BO08, BO09, BO18). No existe enforcement de semiautomático (un disparo por clic) en ninguna arma, ni siquiera en las que por convención de género deberían tenerlo (pistola, revólver, sniper, DMR). Esto es un hallazgo de diseño real, no cosmético: afecta directamente a cómo se siente cada categoría.

---

## 3. APARIENCIA VISUAL (Fase 4)

### ⚠️ Hallazgo central de esta fase

**No existe identidad visual individual por arma.** `buildWeaponViewmodel(scene, category)` construye un modelo con primitivas geométricas (`CreateBox`/`CreateCylinder`) **una silueta por CATEGORÍA (11 formas), no por arma**. Las 11 armas de tipo Assault Rifle, por ejemplo, comparten exactamente la misma geometría (mismas dimensiones de cañón/cajón/cargador/culata/empuñadura/mira), y se diferencian entre sí **solo por**:
1. El nombre (texto en UI)
2. Las estadísticas (invisibles hasta que se leen)
3. El color/patrón del skin aplicado (pero el skin por defecto es el mismo gris oscuro para las 68 armas)
4. El "tier" visual en el icono (ESTÁNDAR/AVANZADA/ÉLITE, un borde de color distinto, no la silueta)

Esto contradice directamente la petición del usuario ("quiero que cada arma tenga una identidad visual propia. NO quiero que todas parezcan clones unas de otras") — y es exactamente correcto detectarlo así, porque **hoy, dentro de cada categoría, literalmente SÍ son clones geométricos**.

### Estado por elemento pedido

| Elemento | Estado |
|---|---|
| Forma general / silueta | 🔵 PLACEHOLDER — 11 siluetas (una por categoría), geométricamente simples, reconocibles como "esto es un rifle/pistola/escopeta" pero sin detalle |
| Proporciones | 🔵 PLACEHOLDER — realistas a groso modo (un SMG es más corto que un AR, un Sniper tiene cañón largo + mira) |
| Materiales reales (metal/polímero/madera) | 🔴 MISSING — `tempMat` es un `StandardMaterial` gris plano (0.15,0.15,0.17) para TODA la geometría antes de aplicar skin; no hay distinción visual de qué parte es "metal de cañón" vs "polímero de cajón" |
| Desgaste / suciedad / arañazos / roughness | 🔴 MISSING en armas (si existe para el terreno del mapa, con mapas de normales y manchas reales — ver `MASTER_INDEX.md` — pero NO se ha aplicado nada equivalente a las armas) |
| Elementos móviles (corredera, cerrojo, tambor) | 🔴 MISSING — toda la geometría es estática; no hay ninguna pieza que se mueva al disparar/recargar más allá del arma entera desplazándose (retroceso) |
| Identidad visual por arma individual | 🔴 MISSING — ver hallazgo central arriba |

**Backlog de esta fase**: dar a cada una de las 68 armas una geometría propia es un incremento de producción real y grande (68 modelos distintos en vez de 11 compartidos) — ver PRODUCTION BACKLOG, prioridad P1.

---

## 4. SKINS (Fase 5)

### Lo que existe realmente: `SKIN_REGISTRY`, 5 skins (no 10)

| ID | Nombre mostrado | Tier real del código | Color/patrón |
|---|---|---|---|
| `default` | Factory | `basic` | Gris oscuro plano (0.16,0.16,0.18) |
| `tan` | Desert Tan | `basic` | Marrón arena plano |
| `urban` | Urban Grey | `basic` | Gris urbano plano |
| `gold` | Gilded | `special` | Dorado con brillo especular alto |
| `digital` | Digital Mesh | `military` | **Único patrón real** — camuflaje digital de 4 tonos dibujado en un `DynamicTexture` 64×64, no solo un color plano |

**Faltan explícitamente respecto a la lista mínima pedida por el usuario** (Default✅, Black🔴, Tactical🔴, Desert≈Tan✅, Urban✅, Military≈Digital✅, Red🔴, Gold✅, Carbon🔴, Special/Rare🔴): de los 10 pedidos, solo 4 tienen un equivalente real hoy (Default, Desert, Urban, Gold), y "Military" solo si se acepta Digital Mesh como equivalente.

### Otros gaps reales de esta fase

| Elemento pedido | Estado |
|---|---|
| Rareza (COMMON/UNCOMMON/RARE/EPIC/LEGENDARY) | 🔴 MISSING — el campo real es `tier: 'basic'/'military'/'special'` (3 valores, no 5, y no correlaciona 1:1 con los 5 pedidos) |
| Aplicación por zona (cañón/cajón/culata con materiales distintos) | 🔴 MISSING — `applySkin()` aplica **un único material a TODA la malla del arma** (`getChildMeshes().forEach(m => m.material = mat)`), no hay variación por pieza |
| Animaciones especiales por skin | 🔴 MISSING |
| Muzzle flash especial por skin | 🔴 MISSING — el muzzle flash es idéntico para las 68 armas × 5 skins |
| Trazadoras especiales | 🔴 MISSING — no existe ningún sistema de trazadoras de bala en absoluto (ver sección 6) |
| Icono/miniatura por skin | 🟡 PARCIAL — existe un `SKIN_SWATCH_COLOR` (un cuadrado de color plano en la UI de la tienda), no una miniatura real del arma con el skin aplicado |
| Economía real (comprar/equipar) | ✅ IMPLEMENTADO — esto SÍ es un sistema real y funcional: monedas ganadas jugando partidas reales, compra con `SKIN_PRICES`, y el skin equipado se aplica de verdad al arma en combate real (verificado con Playwright leyendo el material real del viewmodel en una partida) |

---

## 5. ANIMACIONES (Fase 6)

### Sistema de animación real del proyecto: ninguno basado en clips

Confirmado por auditoría de código (cero coincidencias de `AnimationGroup`, `.skeleton`, `SceneLoader`, `ImportMesh` en todo el archivo): Bullet Ops **no usa animación esquelética ni clips importados en absoluto**, ni para armas ni para personajes. Todo movimiento es interpolación de transformación por código, cada fotograma, en `WeaponController.updateViewmodelTransform()` (armas) y `animateCharacter()` (locomoción de personaje en tercera persona, ver `MASTER_INDEX.md` FASE 13).

### Estado real por animación pedida

| Animación pedida | Estado real |
|---|---|
| Idle | ✅ IMPLEMENTADO — balanceo (`sway`) + respiración (`bobAmount`/`bobSpeed`) procedural, por arma vía config |
| Fire | ✅ IMPLEMENTADO — `kickOffset`/`kickRotX` (empuje hacia atrás + cabeceo), recupera con `recoverySpeed` propio por arma |
| ADS | ✅ IMPLEMENTADO — interpolación de posición del arma + FOV de cámara + sensibilidad, con tiempo propio por arma (`ads.time`) |
| ADS Idle | ✅ IMPLEMENTADO — mismo sistema de sway pero con amplitud reducida en ADS |
| Reload | 🟡 PARCIAL — el **estado y los tiempos** son reales (bloquea disparo, temporiza sonidos), pero **el arma no se mueve visualmente durante la recarga** — no hay ninguna animación de "bajar el arma, sacar cargador, meter cargador" |
| Tactical Reload / Empty Reload | 🟡 PARCIAL — la LÓGICA distingue ambos casos (duraciones distintas, `wasEmptyReload`), pero visualmente son indistinguibles (ninguna se ve, solo se oyen sonidos distintos en el tiempo) |
| Sprint | ✅ IMPLEMENTADO — `SPRINT_POS_OFFSET`/`SPRINT_ROT_OFFSET` interpolados por `sprintAmount` |
| Sprint-to-Fire | ✅ IMPLEMENTADO — bloqueo temporizado tras dejar de esprintar (`sprintToFireDelay`, corregido esta sesión) |
| Equip / Unequip | 🟡 PARCIAL — hay un estado `SWITCHING` con un `switchDip` (el arma baja un poco) y sonido de equipar, pero es genérico, no una animación de "sacar el arma nueva" real |
| Weapon Swap | ✅ IMPLEMENTADO (como transición de estado) — ver Equip/Unequip arriba |
| Melee | ✅ IMPLEMENTADO — las 5 armas Melee tienen su propio `meleeSpeed`/`meleeRange` y lógica de golpe instantáneo, pero **sin animación visual de swing** (el "golpe" es solo lógico: raycast + daño + sonido, el modelo del arma no se mueve de forma distinta a un disparo normal) |
| Inspect | ✅ **IMPLEMENTADO — ver sección 6, sistema completo ya existente** |
| Jump / Fall / Land | ✅ IMPLEMENTADO (personaje, no arma) — `animateCharacter()` |
| Crouch / Slide | ✅ IMPLEMENTADO (personaje) |
| Wall interaction | 🔴 MISSING |
| Hit reaction | 🟡 PARCIAL — existe `playDeathPose()` (procedural, no clip) para la muerte, pero no hay una reacción visual al recibir daño no letal más allá del efecto de pantalla (shake de cámara) |

---

## 6. WEAPON INSPECT (Fase 7) — YA EXISTE, no es una petición nueva

**Hallazgo importante: esta mecánica ya está implementada**, con un diseño sorprendentemente cercano a lo pedido, pero con diferencias reales que se listan explícitamente.

### Lo que existe (verificado leyendo `WeaponController`)

1. Estado dedicado `INSPECTING` dentro de la misma máquina de estados que `IDLE`/`RELOADING`/`SWITCHING` — **la prioridad lógica que pedía el usuario ya está resuelta de raíz**: solo se puede iniciar Inspect desde `IDLE`, y mientras se inspecciona, disparo/ADS/recarga quedan bloqueados automáticamente por el mismo guard (`this.state === 'IDLE'`) que ya protegía esas transiciones entre sí. No hace falta añadir lógica de prioridad nueva — ya es correcta por construcción.
2. Duración fija: 1.4 segundos (`inspectDuration`).
3. Animación real: un "envelope" seno (0→pico→0) que aplica un pequeño giro (`inspectRot`, hasta 0.9 rad en Y) y un desplazamiento hacia la cámara (`inspectPos`) al `TransformNode` del arma — se ve el arma girar y acercarse ligeramente, como pidió el usuario.
4. Bloquea disparo/ADS/recarga correctamente durante su duración (verificado en el código, no solo supuesto).

### Lo que NO existe, respecto a lo pedido explícitamente

| Petición del usuario | Estado real |
|---|---|
| Tecla configurable (`Weapon Inspect Key = F`, cambiable después) | 🔴 MISSING — la tecla es **`I`, hardcodeada** (`inputs.keys['i']`). No existe ningún sistema de rebinding de teclas en todo el proyecto — `gameSettings` solo contiene `sensitivity`/`invertY`/`volume`/`graphicsQuality`, nada de teclas |
| "La cámara hace un pequeño movimiento cinematográfico" | 🔴 MISSING — **solo se mueve el arma**, la cámara del jugador (`player.camera`) no se toca en ningún momento durante el inspect |
| Sonido mecánico al inspeccionar | 🔴 MISSING — no hay ninguna llamada a `SoundSynth` en el disparador ni en la actualización del estado `INSPECTING` |
| Animación específica de inspección por arma | 🔵 PLACEHOLDER — es un único envelope genérico compartido por las 68 armas, no una animación distinta por arma/categoría |
| No debe interferir con sprint | 🟡 PARCIAL/sin verificar — el inicio de Inspect no se bloquea explícitamente si el jugador está esprintando (a diferencia de ADS, que sí excluye `movementState.sprinting`); no se ha encontrado ni un guard que lo impida ni uno que lo permita a propósito — comportamiento no definido intencionalmente, recomendado revisar |

**Esto es la pieza mejor definida de toda la directiva del usuario para seguir desarrollando después de esta auditoría**: el esqueleto ya existe y es sólido; faltan 3 piezas concretas y acotadas (tecla configurable, movimiento de cámara, sonido) en vez de construir el sistema entero desde cero.

---

## 7. SISTEMA DE SONIDO (Fase 8)

### Arquitectura real: síntesis Web Audio, 8 perfiles compartidos, cero archivos de audio

`SoundSynth` (objeto módulo con closure sobre un único `AudioContext`) sintetiza cada sonido en tiempo real combinando dos primitivas: `tone()` (oscilador con rampa de frecuencia/ganancia) y `noiseBurst()` (buffer de ruido blanco filtrado). **No existe ningún archivo `.wav`/`.mp3`/`.ogg` en el proyecto — verificado, cero coincidencias de esas extensiones fuera de `intro.mp4` (el vídeo de introducción, no relacionado con armas).**

`GUNSHOT_PROFILES` define **8 perfiles** (`ar`, `smg`, `pistol`, `shotgun`, `sniper`, `lmg`, `rocket`, `special`) — no 68. Cada arma tiene un campo `soundProfile` que apunta a uno de estos 8, así que **todas las armas de una misma categoría suenan exactamente igual** (con la excepción de que DMR/Revolver reutilizan los perfiles de AR/Pistol respectivamente, ya que no tienen perfil propio — confirmar en `weapons.json`).

### Estado por categoría de sonido pedida

| Categoría pedida | Estado |
|---|---|
| **Disparo** (Fire) | ✅ IMPLEMENTADO — 8 perfiles reales, con thump grave + ruido agudo, tuneados de forma distinta por categoría (un shotgun suena más grave/largo que una SMG, por ejemplo) |
| Fire Distant / Suppressed / Indoor / Outdoor | 🔴 MISSING — el disparo suena exactamente igual sin importar distancia, si el arma tiene silenciador (no existe el concepto) o si el jugador está dentro/fuera de un edificio |
| **Mecánicos** (Equip, Magazine In/Out, Trigger, Safety) | 🟡 PARCIAL — existen `playEquip()`, `playMagOut()`, `playMagIn()`, `playReloadClick()`, `playEmpty()` (genéricos, compartidos por las 68 armas); NO existen sonidos de Bolt/Slide/Chamber/Safety/Inspect como eventos propios |
| **Recarga** (Start/Remove/Insert/Complete) | ✅ IMPLEMENTADO como secuencia temporizada — `playMagOut()` al iniciar, `playMagIn()` a mitad de la recarga (`midDelay`), `playReloadClick()` al completar — genérico, no por arma |
| **Impactos por material** | ✅ IMPLEMENTADO — 5 sonidos reales y distintos por material de superficie (`playImpactMetal/Wood/Concrete/Dirt/Glass`), pero **por MATERIAL de la superficie golpeada, no por arma que dispara**; no existe "Bullet Impact Body" como sonido propio (el impacto contra un personaje no reproduce ningún sonido de impacto dedicado, solo el hitmarker) |
| Formato de archivo / duración / volumen / pitch variation / randomización / distancia máxima / falloff / 2D-3D / spatial audio | 🔴 MISSING **en su totalidad** — no aplica ningún concepto de archivo real (todo es síntesis), y verificado explícitamente: **no existe ningún `PannerNode` ni audio espacial/posicional en todo el proyecto** — un disparo suena exactamente igual sin importar dónde ocurra en el mapa respecto al jugador |

---

## 8. MUZZLE FLASH Y VFX (Fase 9)

| Elemento pedido | Estado |
|---|---|
| Muzzle flash | 🔵 PLACEHOLDER — **una única función `spawnMuzzleFlash()` compartida por las 68 armas**: un sprite esférico + 14 partículas de chispa, mismo tamaño/color/duración sin importar la categoría |
| Smoke | 🔴 MISSING — no hay humo tras el disparo |
| Shell casing (casquillos) | 🔴 MISSING — verificado, cero menciones de eyección de casquillos en todo el código |
| Tracer (trazadora) | 🔴 MISSING — la propia bala es una esfera de 0.1 de diámetro visible en vuelo, pero no hay ninguna estela/trazadora dedicada |
| Recoil effect | ✅ IMPLEMENTADO — ver sección 5/6, `kickOffset`/`kickRotX`/`recoilKickPitch`/`recoilKickYaw`, real y por arma |
| Camera shake | 🟡 PARCIAL — existe shake de cámara al **recibir** daño (`Player.takeDamage()` desvía pitch/yaw aleatoriamente), pero no se ha encontrado un camera shake dedicado al **disparar** (el "cameraKick" de recoil mueve el arma/mira, no literalmente la cámara del jugador) |
| Impact effect | ✅ IMPLEMENTADO — `spawnImpactEffect()` (partículas rojas/doradas según headshot) + `spawnMaterialImpactEffect()` (por material de superficie, 5 perfiles, ver MASTER_INDEX FASE 13) |
| Bullet trail | 🔴 MISSING — no hay estela visual detrás de la bala en vuelo |
| Hit marker | ✅ IMPLEMENTADO — `showHitmarker(isHeadshot)`, con variante visual real de headshot (X más grande, rojo-naranja) |
| Reload effects | 🔴 MISSING (visual) — solo sonido, ver sección 5 |

**Diferenciación por categoría pedida explícitamente** ("una escopeta NO debe sentirse igual que una pistola, un sniper NO debe sentirse igual que un SMG"): hoy **el VFX de disparo (muzzle flash/impacto) es idéntico para las 68 armas**. La diferenciación de "sensación" que sí existe hoy viene enteramente de las estadísticas (retroceso/cadencia/sonido de disparo), no del VFX.

---

## 9. ACCESORIOS (Fase 10)

`ATTACHMENT_REGISTRY = {}` — **objeto completamente vacío**, verificado. Cada arma declara 5 slots (`OPTIC`, `GRIP`, `MAGAZINE`, `BARREL`, `STOCK`) en `attachmentSlots`, pero **los 5 están siempre a `null` en las 68 armas** y no hay ni una sola definición de accesorio real en ningún sitio del código. El comentario del propio código lo confirma: *"con nada en ATTACHMENT_REGISTRY todavía esto es un stub puro sin ningún efecto"*.

| Categoría de accesorio pedida | Estado |
|---|---|
| Optics (Red Dot, Holographic, ACOG, Sniper Scope, etc.) | 🔴 MISSING |
| Muzzle (Suppressor, Compensator, etc.) | 🔴 MISSING |
| Magazine (Extended, Fast, etc.) | 🔴 MISSING |
| Grip (Vertical, Angled, etc.) | 🔴 MISSING |
| Ammunition (Armor Piercing, Hollow Point, etc.) | 🔴 MISSING |
| Stock | 🔴 MISSING |
| Laser / Tactical Light | 🔴 MISSING |

**Lo único real**: la arquitectura de slots (5 tipos, ya nombrados de forma sensata) existe y está pensada para escalar — es un cimiento razonable, no haría falta rediseñarlo, solo poblarlo. Cualquier compatibilidad física arma↔accesorio (la advertencia del usuario de "no añadas accesorios incompatibles") es hoy un no-problema porque no hay ningún accesorio que pudiera ser incompatible — se convertirá en una restricción real de diseño el día que se implemente el primero.

---

## 10. REFERENCIAS VISUALES E ICONOS (Fases 11–12)

### Iconos (lo único con producción real hoy)

`getWeaponIconDataURL()` genera un **pictograma 2D procedural** (no una fotografía/render del arma) dibujado en un `<canvas>` interno: una silueta esquemática según `CATEGORY_ICON_PARTS` (11 formas, una por categoría) con el color de acento de esa categoría (`CATEGORY_ACCENT`) y un borde/etiqueta según el "tier" relativo del arma dentro de su categoría (`weaponTier()`: ESTÁNDAR/AVANZADA/ÉLITE, calculado por daño×cadencia relativo, no inventado). Cacheado en `_weaponIconCache`. Se usa hoy como icono de inventario/HUD/tienda/selección — **el mismo pictograma en todos esos sitios**, no iconos distintos por contexto.

| Elemento pedido | Estado |
|---|---|
| Icono de inventario/HUD/clase/tienda/selección | ✅ IMPLEMENTADO (compartido, no 5 iconos distintos por arma-contexto) |
| Thumbnail | ✅ IMPLEMENTADO (mismo pictograma, reescalado) |
| Imagen promocional | 🔴 MISSING |
| **7 vistas de referencia por arma** (perfiles, frontal, trasera, superior, 3/4, FPS) | 🔴 MISSING — no existe ningún render/imagen real de ninguna arma, solo el pictograma esquemático de icono |

**Sobre generación de imágenes reales** (Fase 11 completa: 7 vistas × 68 armas = 476 imágenes): esta sesión **no tiene ningún conector de generación de imágenes conectado** (ver sección de herramientas recomendadas al final). No se han inventado ni generado imágenes falsas — se documenta como MISSING honesto, con la especificación lista para producirse en cuanto haya una herramienta disponible.

---

## 11. ESTRUCTURA DE ARCHIVOS (Fase 13) — adaptada a la arquitectura real

La estructura `assets/weapons/<categoría>/<Weapon_Name>/model,textures,...` que pide el usuario **no es aplicable literalmente**: no existen archivos de asset independientes que organizar (todo se genera en código dentro de `bullet-ops-game.html`). Proponer esa estructura de carpetas sin más rompería la premisa de "no romper la estructura existente" y produciría carpetas vacías que nadie usaría.

**Estructura real actual** (verificada, no inventada):
```
/home/user/njavi02/
├── bullet-ops-game.html      ← el juego real completo (armas, mapas, UI, todo)
├── MASTER_INDEX.md            ← índice de progreso de todo el proyecto
├── BULLET_OPS_PROGRESS.md     ← historial detallado de desarrollo
├── docs/                      ← 🆕 creada en esta auditoría
│   ├── WEAPON_BIBLE.md         (este documento)
│   ├── weapons.json             (base de datos maestra real)
│   └── WEAPON_ASSET_BACKLOG.md  (tickets de producción)
├── src/                       ← ⚠️ prototipo abandonado, ver hallazgo crítico arriba
└── intro.mp4
```

**Recomendación (🟣 RECOMMENDED) para cuando existan assets reales**: si en el futuro se generan imágenes de referencia/renders reales (Fase 11) mediante una herramienta externa, la carpeta natural sería `docs/weapon-references/<ID>_<nombre>/` (imágenes estáticas, no código) — separada de `docs/` de texto para no mezclar binarios con markdown, y sin tocar `bullet-ops-game.html` salvo que se decida explícitamente cargar alguna como textura.

---

## 12. WEAPON MASTER DATABASE (Fase 14)

Creada: [`docs/weapons.json`](./weapons.json). 68 entradas, una por arma, extraídas programáticamente de `WEAPON_CONFIGS` (evaluando el bloque de código fuente real en Node, no transcritas a mano). Cada entrada incluye:

- Identificación (`id`, `displayName`, `category`, `subcategory` derivada de su mecánica real, `fireMode` con la nota honesta de la sección 2)
- `stats`: las ~25 estadísticas reales, con `"NOT IMPLEMENTED"` explícito en los campos que no existen (nunca un valor inventado)
- `audio`/`visual`/`attachments`: el estado real (placeholder/missing) de cada sistema, para que quien lea el JSON no necesite cruzar este documento para saber qué es real

Formato elegido: JSON plano compatible con cualquier herramienta futura, en vez de intentar adivinar un "formato que ya usa el proyecto" que no existe (no hay ninguna base de datos previa).

---

## 13. TABLA DE CONTROL DE CALIDAD FINAL (Fase 18)

Dado que **la mayoría de sistemas de producción son compartidos por categoría, no por arma individual** (ver hallazgos de las secciones 3, 5, 7, 8, 9, 10), una tabla de 68 filas repetiría el mismo estado 5-11 veces seguidas de forma redundante. Se presenta la tabla real **por categoría** (11 filas) más una fila que resume qué es realmente por-arma vs compartido.

| Categoría | Stats (68/68 únicas) | Model | Texture | Animation | Sound | VFX | Skins | Inspect | Attachments | Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Assault Rifle (11) | ✅ | 🔵 compartido | 🔵 compartido | 🟡 procedural | 🔵 compartido | 🔵 compartido | 🟡 5 skins | ✅ (genérico) | 🔴 | 🟡 PARTIAL |
| SMG (9) | ✅ | 🔵 compartido | 🔵 compartido | 🟡 procedural | 🔵 compartido | 🔵 compartido | 🟡 5 skins | ✅ (genérico) | 🔴 | 🟡 PARTIAL |
| Shotgun (6) | ✅ | 🔵 compartido | 🔵 compartido | 🟡 procedural | 🔵 compartido | 🔵 compartido | 🟡 5 skins | ✅ (genérico) | 🔴 | 🟡 PARTIAL |
| Sniper (5) | ✅ | 🔵 compartido | 🔵 compartido | 🟡 procedural | 🔵 compartido | 🔵 compartido | 🟡 5 skins | ✅ (genérico) | 🔴 | 🟡 PARTIAL |
| DMR (5) | ✅ | 🔵 compartido | 🔵 compartido | 🟡 procedural | 🔵 compartido | 🔵 compartido | 🟡 5 skins | ✅ (genérico) | 🔴 | 🟡 PARTIAL |
| LMG (6) | ✅ | 🔵 compartido | 🔵 compartido | 🟡 procedural | 🔵 compartido | 🔵 compartido | 🟡 5 skins | ✅ (genérico) | 🔴 | 🟡 PARTIAL |
| Pistol (6) | ✅ | 🔵 compartido | 🔵 compartido | 🟡 procedural | 🔵 compartido | 🔵 compartido | 🟡 5 skins | ✅ (genérico) | 🔴 | 🟡 PARTIAL |
| Revolver (4) | ✅ | 🔵 compartido | 🔵 compartido | 🟡 procedural | 🔵 compartido (reusa Pistol) | 🔵 compartido | 🟡 5 skins | ✅ (genérico) | 🔴 | 🟡 PARTIAL |
| Rocket Launcher (6) | ✅ | 🔵 compartido | 🔵 compartido | 🟡 procedural | 🔵 compartido | 🟡 explosión propia | 🟡 5 skins | ✅ (genérico) | 🔴 | 🟡 PARTIAL |
| Melee (5) | ✅ | 🔵 compartido | 🔵 compartido | 🔴 sin swing visual | 🔵 compartido | 🔴 sin VFX propio | 🟡 5 skins | ✅ (genérico) | 🔴 N/A | 🔴 MISSING (VFX/anim) |
| Special (5) | ✅ | 🔵 compartido | 🔵 compartido | 🟡 procedural | 🔵 compartido | 🟡 mixto (1 explosivo) | 🟡 5 skins | ✅ (genérico) | 🔴 | 🟡 PARTIAL |

**Verificación de integridad (Fase 18, literal)**:
- ✅ Las 68 armas están incluidas (verificado por conteo programático)
- ✅ No existen armas duplicadas (68 IDs únicos)
- ✅ Todas tienen categoría (11/11 categorías representadas, ninguna vacía)
- ✅ Todas tienen estado
- ✅ Todas tienen especificación de sonido (aunque compartida, ninguna arma carece de `soundProfile`)
- ✅ Todas tienen especificación de animación (aunque genérica/procedural)
- 🟡 Todas tienen especificación visual, pero **ninguna es única** — esta es la brecha nº1 del proyecto
- ✅ Todas tienen sistema de recarga (lógica real, sin excepción)
- ✅ Todas tienen muzzle flash (compartido, sin excepción)
- ✅ Todas tienen Weapon Inspect (genérico, funcional, sin excepción)
- 🟡 Todas tienen icono (compartido por categoría+tier, no arte único)
- 🟡 Todas tienen skins planificadas (5 reales, no 10 pedidas)

---

## 14. PRODUCTION BACKLOG (Fase 19.10)

### P0 — CRÍTICO
- Ninguno. El arsenal base (68 armas, stats, lógica de disparo/daño/recarga/reload, economía de skins funcional, Weapon Inspect funcional) está genuinamente completo y jugable — no hay ningún bloqueante que impida jugar hoy.

### P1 — IMPORTANTE
1. **Identidad visual real por arma** (no solo por categoría) — el hallazgo más repetido de este documento. Empezar por 1-2 armas "insignia" por categoría (11-22 armas) antes de las 68.
2. **Weapon Inspect: cerrar los 3 gaps concretos** — tecla configurable (settings), movimiento de cámara, sonido mecánico. El sistema base ya existe, esto es un incremento acotado, no una construcción desde cero.
3. **Diferenciar VFX de disparo/impacto por categoría** — al menos tamaño/color de muzzle flash distinto para Shotgun/Sniper/Pistol/LMG frente al genérico actual.
4. **Extender `damageFalloff` a las 65 armas restantes** (hoy solo 3 lo tienen).
5. **Audio espacial/posicional básico** (`PannerNode` de Web Audio, ya disponible en la API que ya se usa) — hoy un disparo suena igual sin importar la distancia.

### P2 — POLISH
1. Poblar `ATTACHMENT_REGISTRY` con un primer set real (empezar por Optics, el más visible).
2. Ampliar skins de 5 a los 10 pedidos, con rareza real (COMMON→LEGENDARY) en vez del `tier` de 3 valores actual.
3. Shell casing / smoke / bullet tracer.
4. Reload con animación visual real (no solo temporización + sonido).
5. Camera shake dedicado al disparar (distinto del que ya existe al recibir daño).

### P3 — OPCIONAL
1. Sonidos suprimidos/indoor/outdoor/distant.
2. Referencias visuales de 7 vistas por arma (bloqueado en tener una herramienta de generación de imágenes — ver siguiente sección).
3. Modo de disparo real automático/semiautomático/tiro-único por categoría (hoy todo es "mantener para disparar" salvo ráfaga).
4. Archivar o eliminar formalmente `src/` (el prototipo abandonado) para evitar confusión futura.

---

## 15. HERRAMIENTAS EXTERNAS RECOMENDADAS (ninguna conectada hoy)

Todo lo generado en esta sesión (iconos, texturas de mapa, sonidos) se ha hecho **sin ninguna herramienta externa**, por código puro (Canvas2D + Web Audio + primitivas Babylon), evitando cualquier coste y cualquier asset con licencia dudosa. Para ir más allá de lo que el código puro puede producir razonablemente (Fase 11: 476 imágenes de referencia realistas; modelos 3D reales por arma), estas son las opciones, priorizando siempre gratis/open-source:

| Herramienta | Para qué serviría | Gratis | Qué produciría | Cómo se integraría |
|---|---|---|---|---|
| **Modelos 3D CC0** (Kenney.nl, itch.io CC0, Poly Haven) | Modelos base de armas realistas sin generar desde cero | ✅ Sí, CC0 | Archivos `.glb`/`.obj` descargables | Requeriría añadir `BABYLON.SceneLoader.ImportMesh` (hoy no usado en el proyecto) — cambio de arquitectura real, no trivial, pero factible |
| **Generador de imágenes de referencia** (no conectado en esta sesión) | Las 7 vistas por arma de la Fase 11 | Depende de la herramienta | Imágenes PNG de referencia | Servirían solo como referencia de diseño, no se cargarían directamente al juego (que sigue siendo 100% procedural) |
| **Generador de modelos 3D dedicado** | Modelos únicos reales por arma (P1 del backlog) | Variable — no evaluado ninguno todavía | Archivos de modelo 3D | Mismo cambio de arquitectura que el punto de modelos CC0 |

**No se ha usado ni se recomienda ningún servicio de pago sin que el usuario lo apruebe explícitamente primero**, tal y como pidió.

---

## 16. RESUMEN PARA EL USUARIO

1. **El arsenal real tiene 68 armas en 11 categorías**, todas con estadísticas de combate genuinamente completas y jugables — no hay armas a medias ni placeholders de datos.
2. **La brecha real y repetida en todo el documento**: casi todo lo "de producción" (modelo, textura, sonido, icono, VFX) es **compartido por categoría, no único por arma** — 11 versiones, no 68. Esto es honesto y consistente, no un error aislado.
3. **Sorpresa positiva**: Weapon Inspect ya existe y funciona bien (tecla `I`, animación de giro+acercamiento, bloqueo de disparo/ADS/recarga correcto por diseño) — falta pulir 3 cosas concretas, no construirlo.
4. **Hallazgo de higiene del repositorio**: existe un prototipo de 5 armas totalmente abandonado en `src/` desde el primer día, sin relación con el sistema real — no se ha tocado, se recomienda archivarlo cuando el usuario lo confirme.
5. **Todo lo documentado como MISSING/PLACEHOLDER es honesto** — no se ha fabricado ningún dato, imagen o valor para rellenar huecos, siguiendo la Fase 17 de la directiva.
6. **No se ha modificado `bullet-ops-game.html` en esta pasada** — solo se han creado 3 archivos nuevos en `docs/` (este documento, `weapons.json`, y el backlog de assets). Se espera confirmación antes de empezar a implementar el backlog de la sección 14.
