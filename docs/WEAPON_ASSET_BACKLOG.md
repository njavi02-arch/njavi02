# BULLET OPS — WEAPON ASSET PRODUCTION BACKLOG

**Tickets de producción de assets, derivados directamente de los huecos documentados en [`WEAPON_BIBLE.md`](./WEAPON_BIBLE.md).**
Ningún ticket de este documento implica que el asset ya exista — todos parten de 🔴 MISSING / 🔵 PLACEHOLDER / 🟡 PARCIAL, tal como se documentó en la Weapon Bible. Este backlog no modifica `bullet-ops-game.html`; es una lista de trabajo para producción futura, pendiente de aprobación explícita del usuario (Fase 20).

Convención de estado idéntica a `WEAPON_BIBLE.md`: ✅ IMPLEMENTADO / 🟡 PARCIAL / 🔵 PLACEHOLDER / 🔴 MISSING / 🟣 RECOMMENDED.

---

## Decisión de alcance (léase antes de los tickets)

La Weapon Bible estableció, categoría tras categoría, que **casi toda la capa de producción (modelo, textura, sonido, VFX, icono) es compartida por CATEGORÍA (11), no única por ARMA (68)**. Generar 68 tickets casi idénticos por tipo de asset (uno por arma) inflaría este documento sin aportar información nueva y contradiría la Fase 17 ("no inventar" — aquí, no inventar granularidad que el proyecto no tiene todavía).

Por eso, este backlog crea:
- **1 ticket por CATEGORÍA (11) por tipo de asset**, para todo lo que hoy es realmente compartido (modelo/silueta, textura/material base, set de sonido, VFX de disparo/impacto, icono).
- **Tickets individuales SOLO donde el proyecto ya diferencia de verdad** (ej. armas con mecánica especial: ráfaga, perdigones, explosivo, cuerpo a cuerpo), porque esas sí necesitan un asset con requisitos distintos al resto de su categoría.
- **1 ticket único, no por categoría**, para sistemas que son transversales a las 68 armas por diseño (Weapon Inspect, skins, accesorios, audio espacial).

Si en el futuro se decide dar identidad única a las 68 armas individualmente (backlog P1 de la Weapon Bible), este documento se expandirá entonces — no antes, para no fabricar 68 fichas idénticas hoy.

---

## 1. TICKETS DE MODELO / SILUETA (por categoría, 11 tickets)

| # | ASSET | ESTADO | NECESIDAD | ESPECIFICACIÓN | PROMPT DE GENERACIÓN | FORMATO | DURACIÓN |
|---|---|---|---|---|---|---|---|
| M-AR | Modelo/silueta única — Assault Rifle (11 armas) | 🔵 PLACEHOLDER (geometría compartida real, ver `buildWeaponViewmodel`) | Dar identidad visual propia a las 11 ARs, hoy clones geométricos | Rifle de asalto militar moderno, cañón medio, cajón recto, cargador curvo, culata plegable u opcional, riel superior | "Modern tactical assault rifle, military bullpup or standard configuration, matte finish, top picatinny rail, curved magazine, orthographic side view, neutral studio background, no branding" | Referencia: imagen 2D (luego evaluar si se importa como `.glb` vía `SceneLoader`, hoy no usado) | N/A (asset estático) |
| M-SMG | Modelo/silueta única — SMG (9 armas) | 🔵 PLACEHOLDER | Igual que arriba, categoría SMG | Perfil compacto, cañón corto, culata retráctil, cajón cerrado | "Compact submachine gun, retractable stock, short barrel, tactical, orthographic side view, neutral background" | Imagen de referencia | N/A |
| M-SHOTGUN | Modelo/silueta única — Shotgun (6 armas) | 🔵 PLACEHOLDER | Diferenciar de pistola/AR en silueta (cañón ancho, guardamano de bombeo) | Cañón corto y ancho, guardamano estriado, sin mira de precisión | "Pump-action or semi-auto tactical shotgun, wide barrel, ribbed forend, orthographic side view" | Imagen de referencia | N/A |
| M-SNIPER | Modelo/silueta única — Sniper (5 armas) | 🔵 PLACEHOLDER | Cañón largo, bípode, mira de precisión propia | Rifle de cerrojo o semiautomático, cañón largo con freno de boca, bípode plegado, mira de largo alcance | "Bolt-action sniper rifle, long barrel with muzzle brake, folded bipod, long-range scope, orthographic side view" | Imagen de referencia | N/A |
| M-DMR | Modelo/silueta única — DMR (5 armas) | 🔵 PLACEHOLDER — hoy comparte silueta con Sniper/AR indistintamente | Intermedio real entre AR y Sniper, no un clon de ninguno | Rifle semiautomático de precisión, cañón medio-largo, mira media, cargador recto | "Designated marksman rifle, semi-automatic, medium-long barrel, mid-range scope, orthographic side view" | Imagen de referencia | N/A |
| M-LMG | Modelo/silueta única — LMG (6 armas) | 🔵 PLACEHOLDER | Cajón de munición visible, bípode integrado, cañón pesado | Ametralladora ligera con caja de munición o tambor, bípode fijo, cañón grueso | "Light machine gun, belt-fed ammo box, integrated bipod, heavy barrel, orthographic side view" | Imagen de referencia | N/A |
| M-PISTOL | Modelo/silueta única — Pistol (6 armas) | 🔵 PLACEHOLDER | Silueta compacta de pistola semiautomática | Pistola semiautomática estándar, corredera visible, cargador en la empuñadura | "Semi-automatic service pistol, visible slide, grip magazine, orthographic side view" | Imagen de referencia | N/A |
| M-REVOLVER | Modelo/silueta única — Revolver (4 armas) | 🔵 PLACEHOLDER — hoy comparte silueta con Pistol | Tambor giratorio visible, cañón expuesto | Revólver de tambor visible, cañón corto o medio expuesto | "Revolver handgun, visible cylinder, exposed barrel, orthographic side view" | Imagen de referencia | N/A |
| M-ROCKET | Modelo/silueta única — Rocket Launcher (6 armas) | 🔵 PLACEHOLDER | Tubo de lanzamiento, mira óptica simple, culata de hombro | Lanzacohetes de hombro, tubo cilíndrico ancho, mira reflex simple | "Shoulder-fired rocket launcher, wide cylindrical tube, simple reflex sight, orthographic side view" | Imagen de referencia | N/A |
| M-MELEE | Modelo/silueta única — Melee (5 armas) | 🔵 PLACEHOLDER | Arma blanca, sin cargador/cañón, forma de hoja/mango | Cuchillo táctico o herramienta de combate cuerpo a cuerpo, hoja fija | "Tactical combat knife, fixed blade, ergonomic grip, orthographic side view" | Imagen de referencia | N/A |
| M-SPECIAL | Modelo/silueta única — Special (5 armas) | 🔵 PLACEHOLDER | Silueta distintiva "experimental/no convencional" | Arma futurista/experimental balística, detalles tecnológicos, sin encajar en categorías clásicas | "Experimental futuristic firearm, unconventional silhouette, tactical sci-fi accents, orthographic side view" | Imagen de referencia | N/A |

### Sub-tickets individuales por mecánica especial (requieren geometría/animación distinta dentro de su categoría)

| # | ASSET | ESTADO | NECESIDAD | ESPECIFICACIÓN |
|---|---|---|---|---|
| M-BURST | Pieza de selector de ráfaga visible (BO08, BO09, BO18) | 🔴 MISSING | Indicador físico de modo ráfaga en el modelo | Pequeño selector/palanca visible cerca del cajón, distinto de posición semi/auto |
| M-SLUG | Cañón de slug diferenciado (BO24, única shotgun sin perdigones) | 🔴 MISSING | Debe leerse visualmente distinta de las otras 5 shotguns (cañón más liso/largo, mira añadida) | Cañón rayado visible, posible mira abatible — la única shotgun "de precisión" |
| M-EXPLOSIVE | Cabeza de proyectil visible en lanzacohetes/BO82 (7 armas con `projectileType:'explosive'`) | 🔴 MISSING | El proyectil cargado debe leerse como explosivo, no bala estándar | Ojiva visible sobresaliendo del tubo antes de disparar |
| M-MELEE-VARIANT | 5 siluetas de melee realmente distintas entre sí (hoy comparten 1 sola silueta de categoría) | 🔴 MISSING | FANG (rápido/pequeño) vs CLEAVER/WRECKER (alcance mayor) deben leerse como objetos físicamente distintos, no la misma hoja reescalada | Cuchillo pequeño / machete / hacha de combate / garras, según el nombre de cada arma |

---

## 2. TICKETS DE TEXTURA / MATERIAL (por categoría, 11 tickets)

Todos comparten la misma necesidad base: reemplazar el `StandardMaterial` gris plano (`tempMat`, 0.15/0.15/0.17) por materiales reales diferenciados por parte (metal de cañón, polímero de cajón, goma de empuñadura), siguiendo el mismo enfoque PBR-procedural ya validado en el mapa (`makePBRConcrete`, `makePBRMetal`, etc. — ver `MASTER_INDEX.md`).

| # | ASSET | ESTADO | NECESIDAD | ESPECIFICACIÓN | FORMATO | DURACIÓN |
|---|---|---|---|---|---|---|
| T-AR | Set de materiales — Assault Rifle | 🔴 MISSING | Metal oscurecido en cañón/corredera + polímero mate en cajón/culata + desgaste ligero | Base Color + Roughness + Normal (reutilizar `makeNormalNoise`), sin Metallic map dedicado todavía | `DynamicTexture` procedural (igual que el mapa) | N/A |
| T-SMG | Set de materiales — SMG | 🔴 MISSING | Igual enfoque, tonos más oscuros/tácticos | Base Color + Roughness + Normal | `DynamicTexture` procedural | N/A |
| T-SHOTGUN | Set de materiales — Shotgun | 🔴 MISSING | Madera opcional en guardamano (si el diseño final la incluye) + metal en cañón | Base Color + Roughness + Normal, reutilizar `makePBRWood` como referencia de enfoque | `DynamicTexture` procedural | N/A |
| T-SNIPER | Set de materiales — Sniper | 🔴 MISSING | Acabado mate anti-reflejo (relevante para sigilo temático), metal en cañón largo | Base Color + Roughness + Normal | `DynamicTexture` procedural | N/A |
| T-DMR | Set de materiales — DMR | 🔴 MISSING | Intermedio entre AR y Sniper | Base Color + Roughness + Normal | `DynamicTexture` procedural | N/A |
| T-LMG | Set de materiales — LMG | 🔴 MISSING | Metal grueso/pesado, marcas de uso más intensas (arma de soporte) | Base Color + Roughness + Normal + manchas de desgaste (igual enfoque que `makePBRConcrete`) | `DynamicTexture` procedural | N/A |
| T-PISTOL | Set de materiales — Pistol | 🔴 MISSING | Metal/polímero estándar, acabado más limpio | Base Color + Roughness + Normal | `DynamicTexture` procedural | N/A |
| T-REVOLVER | Set de materiales — Revolver | 🔴 MISSING | Acabado metálico más brillante (tambor pulido) | Base Color + Roughness + Normal + Metallic más alto que el resto | `DynamicTexture` procedural | N/A |
| T-ROCKET | Set de materiales — Rocket Launcher | 🔴 MISSING | Tubo con textura de fibra/metal industrial, marcas de advertencia pintadas | Base Color + Roughness + Normal | `DynamicTexture` procedural | N/A |
| T-MELEE | Set de materiales — Melee | 🔴 MISSING | Hoja metálica reflectante + mango de goma/cuero | Base Color + Roughness + Normal, Metallic alto solo en la hoja | `DynamicTexture` procedural | N/A |
| T-SPECIAL | Set de materiales — Special | 🔴 MISSING | Acentos tecnológicos (franjas de color/emisivas sutiles) | Base Color + Roughness + Normal + Emissive puntual | `DynamicTexture` procedural | N/A |

---

## 3. TICKETS DE SONIDO (por categoría existente + gaps transversales)

Los 8 perfiles de disparo (`GUNSHOT_PROFILES`) YA existen y están ✅ IMPLEMENTADO — no se listan como ticket. Los tickets aquí cubren exactamente los gaps documentados en la Weapon Bible sección 7.

| # | ASSET | ESTADO | NECESIDAD | ESPECIFICACIÓN | PROMPT / MÉTODO | FORMATO | DURACIÓN |
|---|---|---|---|---|---|---|---|
| S-SPATIAL | Audio espacial/posicional (`PannerNode`) | 🔴 MISSING | Que un disparo lejano/en otra zona del mapa suene distinto en volumen/paneo | Envolver las llamadas de `SoundSynth` existentes en un `PannerNode` con posición 3D del emisor respecto al listener (cámara) — Web Audio API, ya disponible, sin librería nueva | Código (no archivo de audio) | Tiempo real |
| S-DISTANT | Variante "disparo lejano" por perfil (8 perfiles × 1 variante = 8 tickets) | 🔴 MISSING | Atenuación de agudos + reverb ligero cuando la distancia supera un umbral | Filtro paso-bajo aplicado dinámicamente sobre el `tone()`/`noiseBurst()` existente según distancia real | Código (síntesis, no archivo) | ~0.3–0.6s por disparo |
| S-INDOOR | Variante "interior" (reverb) | 🔴 MISSING | Disparos dentro de edificios deben sonar con reflexión de sala | `ConvolverNode` con impulso corto sintético o `BiquadFilterNode` en cascada como aproximación barata | Código | Tiempo real |
| S-SUPPRESSED | Sonido de disparo silenciado | 🔴 MISSING (no hay concepto de silenciador todavía — depende de Accesorios, ticket A-MUZZLE) | Solo relevante una vez exista el accesorio de silenciador | Perfil `tone()` de baja amplitud + `noiseBurst()` recortado, sin el "crack" agudo actual | Código | ~0.1–0.2s |
| S-MECHANICAL | Sonidos mecánicos ampliados: Bolt/Slide/Chamber/Safety (por categoría, 11) | 🟡 PARCIAL (hoy solo genéricos Equip/MagOut/MagIn/Click/Empty) | Sonido distinto de "cerrojo" según si la categoría tiene corredera (Pistol/SMG/AR) o cerrojo manual (Sniper) o tambor (Revolver) | `noiseBurst()` corto y metálico, timbre distinto por categoría | Código | ~0.05–0.15s cada uno |
| S-INSPECT | Sonido mecánico de inspección (Weapon Inspect) | 🔴 MISSING | Pequeño clic/manipulación al iniciar el envelope de inspect ya existente | `tone()` corto + `noiseBurst()` sutil, disparado en el mismo punto donde hoy se activa `INSPECTING` | Código | ~0.1–0.2s |
| S-BODY-IMPACT | Sonido de impacto contra personaje ("Bullet Impact Body") | 🔴 MISSING | Hoy el impacto en jugador solo dispara el hitmarker visual, sin sonido de impacto propio | `noiseBurst()` corto y sordo, distinto del impacto contra material inerte | Código | ~0.1s |
| S-AMMOTYPE | Sonido por tipo de munición | 🟣 RECOMMENDED — depende de que exista el concepto de tipo de munición (hoy 🔴 MISSING, ver Weapon Bible sección 2) | No implementar antes de que exista el sistema de tipos de munición | N/A todavía | N/A |

---

## 4. TICKETS DE VFX / MUZZLE FLASH (por categoría, 11 tickets + transversales)

| # | ASSET | ESTADO | NECESIDAD | ESPECIFICACIÓN | FORMATO | DURACIÓN |
|---|---|---|---|---|---|---|
| V-AR | Muzzle flash propio — AR | 🔵 PLACEHOLDER (hoy `spawnMuzzleFlash()` genérico) | Tamaño/duración medio, sin exagerar | Sprite + partículas, radio medio (~0.35), 14→18 partículas, 0.08s | Código (partículas Babylon existentes) | ~0.08s |
| V-SMG | Muzzle flash propio — SMG | 🔵 PLACEHOLDER | Más pequeño y rápido que AR (cadencia alta) | Radio ~0.25, 10 partículas, 0.06s | Código | ~0.06s |
| V-SHOTGUN | Muzzle flash propio — Shotgun | 🔵 PLACEHOLDER | Grande, ancho, corto (disparo contundente) | Radio ~0.5 ancho, 20 partículas dispersas, 0.1s | Código | ~0.1s |
| V-SNIPER | Muzzle flash propio — Sniper | 🔵 PLACEHOLDER | Grande y alargado (cañón largo, mucha pólvora) + onda de choque sutil | Radio ~0.45 alargado en eje del cañón, 16 partículas, 0.12s | Código | ~0.12s |
| V-DMR | Muzzle flash propio — DMR | 🔵 PLACEHOLDER | Intermedio AR/Sniper | Radio ~0.38, 15 partículas, 0.09s | Código | ~0.09s |
| V-LMG | Muzzle flash propio — LMG | 🔵 PLACEHOLDER | El más grande y sostenido (cadencia alta + calibre pesado) | Radio ~0.45, 20 partículas, 0.1s, ligera vibración de humo residual | Código | ~0.1s |
| V-PISTOL | Muzzle flash propio — Pistol | 🔵 PLACEHOLDER | Pequeño, seco | Radio ~0.22, 8 partículas, 0.05s | Código | ~0.05s |
| V-REVOLVER | Muzzle flash propio — Revolver | 🔵 PLACEHOLDER | Más grande que pistola semiauto (calibre mayor, cañón expuesto) | Radio ~0.3, 12 partículas, 0.07s | Código | ~0.07s |
| V-ROCKET | VFX propio de disparo + explosión — Rocket Launcher | 🟡 PARCIAL (la explosión de impacto YA es distinta; falta el VFX de LANZAMIENTO) | Estela de humo al salir del tubo, distinta de un muzzle flash de bala | Cono de humo trasero + destello frontal grande | Código | ~0.3s |
| V-MELEE | VFX de golpe — Melee | 🔴 MISSING (hoy sin VFX propio, ver Weapon Bible sección 8) | Marca de impacto/chispa al conectar el golpe, sin necesidad de muzzle flash | Chispa pequeña en el punto de impacto del raycast de melee | Código | ~0.05s |
| V-SPECIAL | Muzzle flash propio — Special | 🔵 PLACEHOLDER | Acento visual distintivo (color no estándar, ej. azulado) para reforzar identidad "experimental" | Radio ~0.35, color de partícula distinto al resto (no naranja estándar) | Código | ~0.08s |

### Transversales

| # | ASSET | ESTADO | NECESIDAD |
|---|---|---|---|
| V-SMOKE | Humo post-disparo | 🔴 MISSING | Partícula de humo residual tras el muzzle flash, por categoría (reutilizar sistema de partículas existente) |
| V-SHELL | Eyección de casquillos | 🔴 MISSING | Pequeño cilindro/`CreateCylinder` expulsado lateralmente al disparar, con física simple o animación corta |
| V-TRACER | Trazadora de bala | 🔴 MISSING | Línea/`CreateLines` o cilindro delgado siguiendo la trayectoria del proyectil existente |
| V-CAMSHAKE-FIRE | Camera shake al disparar (distinto del de recibir daño) | 🔴 MISSING | Reutilizar el mecanismo ya existente en `Player.takeDamage()`, aplicado también en el disparo, con magnitud por categoría (LMG/Shotgun más que Pistol/SMG) |
| V-BULLETTRAIL | Estela visual tras el proyectil en vuelo | 🔴 MISSING | Sistema de partículas ligero siguiendo la esfera de bala ya existente |

---

## 5. TICKETS DE ANIMACIÓN (transversales, no por categoría — el sistema procedural ya es compartido por diseño)

| # | ASSET | ESTADO | NECESIDAD | ESPECIFICACIÓN |
|---|---|---|---|---|
| A-RELOAD-VISUAL | Animación visual de recarga (hoy solo temporización + sonido, sin movimiento) | 🔴 MISSING | Interpolación de posición del `TransformNode` del arma: bajar el arma, pausa, volver a subir — sincronizada con `playMagOut()`/`playMagIn()` ya existentes | Extensión del mismo sistema procedural de `updateViewmodelTransform()`, sin necesidad de clips |
| A-EQUIP-VISUAL | Animación real de "sacar arma nueva" (hoy solo `switchDip` genérico) | 🔴 MISSING | Movimiento de entrada desde fuera de cámara o desde abajo, distinto de solo bajar/subir | Igual enfoque procedural |
| A-MELEE-SWING | Animación de swing visual en golpe cuerpo a cuerpo (hoy el golpe es solo lógico) | 🔴 MISSING | Arco de rotación del `TransformNode` del arma sincronizado con el raycast de daño existente | Igual enfoque procedural, por variante de melee (ver M-MELEE-VARIANT) |
| A-HITREACTION | Reacción visual no letal a recibir daño (hoy solo shake de cámara) | 🔴 MISSING | Pequeño flinch de la vista/arma al recibir daño sin morir | Igual enfoque procedural |
| A-WALLINTERACTION | Interacción con paredes (lean/mantling visual) | 🔴 MISSING | Fuera de alcance salvo que el usuario confirme que quiere mecánica de "lean" — hoy no existe ni la mecánica base, no solo la animación | 🟣 RECOMMENDED evaluar primero si la mecánica de movimiento la soporta antes de animar algo que no tiene lógica |

---

## 6. WEAPON INSPECT — los 3 gaps concretos (Fase 7, no un sistema nuevo)

| # | ASSET | ESTADO | NECESIDAD | ESPECIFICACIÓN |
|---|---|---|---|---|
| I-KEYBIND | Tecla configurable para Inspect | 🔴 MISSING | Añadir `inspectKey` a `gameSettings` (hoy solo `sensitivity`/`invertY`/`volume`/`graphicsQuality`) + UI de rebinding | Requiere primero un sistema mínimo de rebinding de teclas (hoy no existe ninguno en absoluto) — este ticket es más grande de lo que parece a primera vista |
| I-CAMERA | Movimiento de cámara durante inspect | 🔴 MISSING | Pequeño desplazamiento/rotación de `player.camera` sincronizado con el envelope seno ya existente en `inspectRot`/`inspectPos` | Extensión directa del sistema procedural ya presente |
| I-SOUND | Sonido mecánico al inspeccionar | 🔴 MISSING | Ver ticket S-INSPECT arriba (mismo ticket, listado también aquí por completitud) | — |

---

## 7. SKINS (Fase 5) — sistema transversal, no por categoría

| # | ASSET | ESTADO | NECESIDAD | ESPECIFICACIÓN |
|---|---|---|---|---|
| K-COUNT | Ampliar de 5 a 10 skins mínimas | 🔴 MISSING (faltan Black/Tactical/Red/Carbon/una 5ª "Special/Rare" distinta de Gold) | Diseñar 5 skins nuevas siguiendo el mismo patrón que `digital` (patrón real dibujado en `DynamicTexture`, no solo color plano) | Black (negro mate), Tactical (verde oliva + parches), Red (rojo con acentos negros), Carbon (patrón de fibra de carbono dibujado, no plano), 5ª Rare (patrón único, no reusar Gold) |
| K-RARITY | Sistema de rareza real (5 tiers) | 🔴 MISSING (hoy `tier` tiene 3 valores: basic/military/special) | Extender el campo a COMMON/UNCOMMON/RARE/EPIC/LEGENDARY, remapeando las 5+5=10 skins finales | Cambio de dato + UI de color de borde por rareza (ya existe un patrón similar en el "tier" de icono `weaponTier()`) |
| K-PERZONE | Materiales por zona (cañón/cajón/culata distintos) | 🔴 MISSING | Sustituir `applySkin()` (un material para toda la malla) por asignación por submalla | Depende de que existan submallas nombradas por parte — hoy la geometría es plana por categoría, ver sección 1 |
| K-ICON | Miniatura real por skin (hoy solo un cuadrado de color `SKIN_SWATCH_COLOR`) | 🟡 PARCIAL | Render pequeño del arma con el skin aplicado, no solo un swatch | Reutilizar `getWeaponIconDataURL()` pero coloreado según el skin real, en vez de un cuadrado separado |

---

## 8. ACCESORIOS (Fase 10) — sistema transversal, no por categoría

`ATTACHMENT_REGISTRY = {}` está vacío. Se lista un ticket por SLOT (5), no por arma ni por categoría, ya que los slots ya están definidos de forma genérica y razonable.

| # | ASSET | ESTADO | NECESIDAD | ESPECIFICACIÓN |
|---|---|---|---|---|
| A-OPTIC | Primer set de Optics (Red Dot, Holographic, ACOG mínimo) | 🔴 MISSING | Más visible de los 5 slots, empezar aquí | Geometría simple superpuesta en el riel superior + efecto de mira al hacer ADS |
| A-MUZZLE | Primer set de Muzzle (Suppressor, Compensator) | 🔴 MISSING | Habilita también el ticket S-SUPPRESSED de sonido | Geometría enroscada en la punta del cañón |
| A-MAGAZINE | Primer set de Magazine (Extended) | 🔴 MISSING | Modifica `mag` real en stats, no solo visual | Cargador visualmente más largo + valor de `mag` aumentado en la config |
| A-GRIP | Primer set de Grip (Vertical, Angled) | 🔴 MISSING | Geometría bajo el guardamano | Pieza añadida bajo el cañón |
| A-STOCK | Primer set de Stock (Lightweight, Heavy) | 🔴 MISSING | Modifica `movement`/`recoil` reales, no solo visual | Reemplazo de la culata trasera |

**Nota de compatibilidad (Fase 10 del usuario, "no añadir accesorios físicamente incompatibles")**: Melee (5 armas) y Rocket Launcher (6 armas, salvo quizá Optics) deberían quedar explícitamente excluidas de la mayoría de estos slots en `ATTACHMENT_REGISTRY` cuando se implementen — hoy no es un problema porque no hay ningún accesorio real todavía.

---

## 9. ICONOS Y REFERENCIAS VISUALES (Fases 11–12)

| # | ASSET | ESTADO | NECESIDAD | ESPECIFICACIÓN | PROMPT DE GENERACIÓN | FORMATO | DURACIÓN |
|---|---|---|---|---|---|---|---|
| R-VIEWS | 7 vistas de referencia por arma (perfil izq/der, frontal, trasera, superior, 3/4 cinemática, vista FPS) | 🔴 MISSING — bloqueado, ver sección 15 de `WEAPON_BIBLE.md` (ninguna herramienta de generación de imágenes conectada esta sesión) | Referencias de diseño para producción futura de modelos/texturas reales | 476 imágenes totales (68 armas × 7 vistas) si se hiciera por arma; **con el alcance actual (identidad por categoría), se reduce a 11×7 = 77 imágenes** hasta que se decida dar identidad única por arma | Ver prompts por categoría en sección 1 de este documento (M-AR..M-SPECIAL) como base, extendidos a 7 ángulos cada uno | PNG, fondo neutro | N/A |
| R-PROMO | Imagen promocional por arma/skin | 🔴 MISSING | Fuera de alcance hasta que existan modelos/skins reales que promocionar | — | — | PNG | N/A |

---

## RESUMEN DE CONTEO DE TICKETS

| Tipo | Tickets por categoría | Tickets transversales/especiales | Total |
|---|---|---|---|
| Modelo/silueta | 11 | 4 (mecánicas especiales) | 15 |
| Textura/material | 11 | 0 | 11 |
| Sonido | 0 (perfiles base ya ✅) | 8 | 8 |
| VFX/muzzle flash | 11 | 5 | 16 |
| Animación | 0 | 5 | 5 |
| Weapon Inspect | 0 | 3 | 3 |
| Skins | 0 | 4 | 4 |
| Accesorios | 0 | 5 | 5 |
| Iconos/referencias | 0 | 2 | 2 |
| **TOTAL** | | | **69 tickets** |

Ninguno de estos 69 tickets se ha empezado a implementar en esta pasada — este documento es el inventario de trabajo pendiente, tal como pidió el usuario en la Fase 16, a la espera de aprobación explícita antes de tocar `bullet-ops-game.html`.
