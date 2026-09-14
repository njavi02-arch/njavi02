# WEAPON_ASSET_MAP — Mapa de nomenclatura y organización del sistema de armas

> Complementa `WEAPON_BIBLE.md` (auditoría de diseño/balance) y
> `WEAPON_ASSET_BACKLOG.md` (tickets pendientes). Este documento resuelve
> específicamente la petición de estructura profesional de carpetas
> `Weapons/[Categoria]/[Arma]/Models/Textures/.../` sobre la arquitectura
> real del proyecto.

## 0. Por qué esto es un mapa "virtual" y no carpetas reales

`bullet-ops-game.html` es un único archivo HTML autocontenido: sin build,
sin loader de assets, sin `.glb`/`.fbx`/`.png`/`.wav` en disco. Cada modelo
es geometría Babylon procedural, cada textura es un `DynamicTexture`
dibujado con Canvas2D en tiempo de carga, cada sonido es síntesis Web
Audio en tiempo real. Es una decisión deliberada y se mantiene así (se
publica como Claude Artifact de un solo archivo).

Por eso una estructura `Weapons/AssaultRifles/M4A1/M4A1_Model.fbx` no
puede existir de verdad sin romper esa arquitectura. Lo que sí se puede
—y es lo que hace este documento— es dar la **misma claridad de
localización** que esa estructura busca, pero apuntando a la función/línea
real del código donde vive cada pieza de cada arma, en vez de a un
archivo separado. Ninguna carpeta ni archivo de esta lista existe
físicamente; son rutas conceptuales de navegación.

## 1. Sistema de nombres (ya vigente, documentado aquí por primera vez)

Cada arma tiene dos identidades separadas y consistentes:

- **ID interno** (`WEAPON_CONFIGS` key, p. ej. `BO01`): sigue un esquema
  de decenas por categoría, ya vigente desde que se diseñó el roster:

  | Rango ID | Categoría | Rango ID | Categoría |
  |---|---|---|---|
  | 01–09 | Assault Rifle (+94,95 overflow) | 51–59 | Pistol (+ Revolver: 52,56,57) |
  | 11–19 | SMG | 61–69 | Rocket Launcher |
  | 21–29 | Shotgun | 71–79 | Melee |
  | 31–39 | Sniper (+ DMR: 32,35–38) | 81–89 | Special |
  | 41–49 | LMG | 91–95 | Overflow (Sniper/AR/Revolver cuando su decena se llenó) |

  Fuente: `WEAPON_CATEGORY` (bullet-ops-game.html:1357) y el comentario de
  diseño junto a él.

- **Codename** (`name`, p. ej. `BO-01 VANGUARD`): nombre temático de
  operador/arma, en la línea de nomenclatura de shooters comerciales
  (no describe literalmente la categoría en el texto — igual que "AK-47"
  o "MP5" no dicen "rifle"/"subfusil" en el nombre). Auditados los 68
  nombres: ninguno contradice su categoría real: todos son códigos
  temáticos neutros, así que no hace falta renombrar nada para resolver
  el punto 3 del pedido original ("si el nombre dice una cosa y
  visualmente es otra").

- **Ruta virtual** (nueva, este documento): `Weapons/[Categoria]/[ID]_[CODENAME]/`.

## 2. Dónde vive cada pieza en el código (por categoría, compartido)

Casi todo el contenido de un arma —geometría base, VFX de disparo,
síntesis de sonido, animaciones de ADS/recarga/inspect— es **código
compartido por categoría**, parametrizado por los datos de cada arma en
`WEAPON_CONFIGS` (stats, cadencia, retroceso, `damageFalloff`, etc.). Esto
es lo que reemplaza a "una textura/modelo por arma": en vez de 68 archivos
de modelo, hay 1 función de geometría por categoría (~10) más overrides
únicos para las 11 armas insignia.

| Pieza | Función / constante | Línea | Ámbito |
|---|---|---|---|
| Taxonomía de categorías | `WEAPON_CATEGORY` | 1357 | Global |
| Stats por arma (incl. `damageFalloff`) | `WEAPON_CONFIGS` | 1440 | Por arma (68/68) |
| Registro de accesorios (ópticas) | `ATTACHMENT_REGISTRY` | 1386 | Por slot |
| Stats efectivos con accesorios equipados | `getEffectiveWeaponStats()` | 1417 | Por arma+loadout |
| Modelo/viewmodel (geometría) | `buildWeaponViewmodel()` | 3644 | Por categoría + 11 overrides únicos |
| Visual de accesorio montado | `applyAttachmentVisuals()` | 3152 | Por slot |
| Skins/camuflajes (material) | `SKIN_REGISTRY` | 933 | Por arma (5 skins c/u) |
| Tracer de bala | `spawnBulletTracer()` | 3543 | Universal (todas las armas de proyectil) |
| Casquillo eyectado | `spawnShellCasing()` | 3580 | Universal (armas con recámara) |
| Perfil de muzzle flash (VFX) | `MUZZLE_FLASH_PROFILES` | 3928 | Por categoría (10 perfiles) |
| Motor de sonido (síntesis) | `SoundSynth` | 2828 | Global |
| Disparo (audio, con perfil por arma) | `SoundSynth.playGunshot()` | 3025 | Por arma (vía `soundProfile`) |
| Inspect (audio) | `SoundSynth.playInspect()` | 3039 | Universal |
| Offset de cámara en Inspect | `getInspectCameraOffset()` | 4263 | Por categoría |
| Caída de daño por rango | `damageFalloffMultiplier()` | 4497 | Por arma (`damageFalloff` en config) |
| Controlador (fire/reload/ADS/switch) | `class WeaponController` | 4114 | Universal |

**11 armas insignia con geometría 100% única** (no comparten la plantilla
de su categoría): `BO01`, `BO11`, `BO21`, `BO31`, `BO32`, `BO41`, `BO51`,
`BO52`, `BO61`, `BO71`, `BO81` — exactamente una por cada una de las 11
categorías (AR, SMG, Shotgun, Sniper, DMR, LMG, Pistol, Revolver, Rocket,
Melee, Special). Las 57 restantes usan la plantilla de su categoría con
las mismas stats
de `WEAPON_CONFIGS` pero geometría compartida. Esto es honesto y
deliberado: está documentado como brecha abierta en
`WEAPON_ASSET_BACKLOG.md` (ampliar geometría única arma por arma es
trabajo futuro, no de esta fase).

## 3. Tabla completa — 68 armas → ruta virtual

### Weapons/AssaultRifles/

| ID | Codename | Ruta virtual | Geometría propia |
|---|---|---|---|
| BO01 | BO-01 VANGUARD | Weapons/AssaultRifles/BO01_VANGUARD/ | Sí (insignia) |
| BO02 | BO-02 PREDATOR | Weapons/AssaultRifles/BO02_PREDATOR/ | Compartida (plantilla de categoría) |
| BO03 | BO-03 STORMCALLER | Weapons/AssaultRifles/BO03_STORMCALLER/ | Compartida (plantilla de categoría) |
| BO04 | BO-04 SENTINEL | Weapons/AssaultRifles/BO04_SENTINEL/ | Compartida (plantilla de categoría) |
| BO05 | BO-05 OUTLAW | Weapons/AssaultRifles/BO05_OUTLAW/ | Compartida (plantilla de categoría) |
| BO06 | BO-06 LANCER | Weapons/AssaultRifles/BO06_LANCER/ | Compartida (plantilla de categoría) |
| BO07 | BO-07 SKIRMISH | Weapons/AssaultRifles/BO07_SKIRMISH/ | Compartida (plantilla de categoría) |
| BO08 | BO-08 TRIBURST | Weapons/AssaultRifles/BO08_TRIBURST/ | Compartida (plantilla de categoría) |
| BO09 | BO-09 DUALSTRIKE | Weapons/AssaultRifles/BO09_DUALSTRIKE/ | Compartida (plantilla de categoría) |
| BO94 | BO-94 HAILSTORM | Weapons/AssaultRifles/BO94_HAILSTORM/ | Compartida (plantilla de categoría) |
| BO95 | BO-95 JUDGMENT | Weapons/AssaultRifles/BO95_JUDGMENT/ | Compartida (plantilla de categoría) |

### Weapons/SMGs/

| ID | Codename | Ruta virtual | Geometría propia |
|---|---|---|---|
| BO11 | BO-11 RAZORBACK | Weapons/SMGs/BO11_RAZORBACK/ | Sí (insignia) |
| BO12 | BO-12 WHISPER | Weapons/SMGs/BO12_WHISPER/ | Compartida (plantilla de categoría) |
| BO13 | BO-13 ENFORCER | Weapons/SMGs/BO13_ENFORCER/ | Compartida (plantilla de categoría) |
| BO14 | BO-14 VIPERBITE | Weapons/SMGs/BO14_VIPERBITE/ | Compartida (plantilla de categoría) |
| BO15 | BO-15 UNDERTOW | Weapons/SMGs/BO15_UNDERTOW/ | Compartida (plantilla de categoría) |
| BO16 | BO-16 PDW-9 | Weapons/SMGs/BO16_PDW-9/ | Compartida (plantilla de categoría) |
| BO17 | BO-17 HUSH | Weapons/SMGs/BO17_HUSH/ | Compartida (plantilla de categoría) |
| BO18 | BO-18 THREEPOINT | Weapons/SMGs/BO18_THREEPOINT/ | Compartida (plantilla de categoría) |
| BO19 | BO-19 DELUGE | Weapons/SMGs/BO19_DELUGE/ | Compartida (plantilla de categoría) |

### Weapons/Pistols/

| ID | Codename | Ruta virtual | Geometría propia |
|---|---|---|---|
| BO51 | BO-51 SIDEARM | Weapons/Pistols/BO51_SIDEARM/ | Sí (insignia) |
| BO53 | BO-53 VIPER | Weapons/Pistols/BO53_VIPER/ | Compartida (plantilla de categoría) |
| BO54 | BO-54 ECHO | Weapons/Pistols/BO54_ECHO/ | Compartida (plantilla de categoría) |
| BO55 | BO-55 DUELIST | Weapons/Pistols/BO55_DUELIST/ | Compartida (plantilla de categoría) |
| BO58 | BO-58 TEMPEST | Weapons/Pistols/BO58_TEMPEST/ | Compartida (plantilla de categoría) |
| BO59 | BO-59 GHOSTGRIP | Weapons/Pistols/BO59_GHOSTGRIP/ | Compartida (plantilla de categoría) |

### Weapons/Shotguns/

| ID | Codename | Ruta virtual | Geometría propia |
|---|---|---|---|
| BO21 | BO-21 BREACHER | Weapons/Shotguns/BO21_BREACHER/ | Sí (insignia) |
| BO22 | BO-22 SCATTERGUN | Weapons/Shotguns/BO22_SCATTERGUN/ | Compartida (plantilla de categoría) |
| BO23 | BO-23 WIDOWMAKER | Weapons/Shotguns/BO23_WIDOWMAKER/ | Compartida (plantilla de categoría) |
| BO24 | BO-24 SLUGSTORM | Weapons/Shotguns/BO24_SLUGSTORM/ | Compartida (plantilla de categoría) |
| BO25 | BO-25 RIOT-12 | Weapons/Shotguns/BO25_RIOT-12/ | Compartida (plantilla de categoría) |
| BO26 | BO-26 SAWTOOTH | Weapons/Shotguns/BO26_SAWTOOTH/ | Compartida (plantilla de categoría) |

### Weapons/Snipers/

| ID | Codename | Ruta virtual | Geometría propia |
|---|---|---|---|
| BO31 | BO-31 LONGSHOT | Weapons/Snipers/BO31_LONGSHOT/ | Sí (insignia) |
| BO33 | BO-33 WRAITHFANG | Weapons/Snipers/BO33_WRAITHFANG/ | Compartida (plantilla de categoría) |
| BO34 | BO-34 DEADEYE | Weapons/Snipers/BO34_DEADEYE/ | Compartida (plantilla de categoría) |
| BO91 | BO-91 WHISPER-9 | Weapons/Snipers/BO91_WHISPER-9/ | Compartida (plantilla de categoría) |
| BO92 | BO-92 COLOSSUS | Weapons/Snipers/BO92_COLOSSUS/ | Compartida (plantilla de categoría) |

### Weapons/DMRs/

| ID | Codename | Ruta virtual | Geometría propia |
|---|---|---|---|
| BO32 | BO-32 PHANTOM | Weapons/DMRs/BO32_PHANTOM/ | Sí (insignia) |
| BO35 | BO-35 RIDGELINE | Weapons/DMRs/BO35_RIDGELINE/ | Compartida (plantilla de categoría) |
| BO36 | BO-36 QUICKSILVER | Weapons/DMRs/BO36_QUICKSILVER/ | Compartida (plantilla de categoría) |
| BO37 | BO-37 FALCONER | Weapons/DMRs/BO37_FALCONER/ | Compartida (plantilla de categoría) |
| BO38 | BO-38 IRONCLAD | Weapons/DMRs/BO38_IRONCLAD/ | Compartida (plantilla de categoría) |

### Weapons/LMGs/

| ID | Codename | Ruta virtual | Geometría propia |
|---|---|---|---|
| BO41 | BO-41 JUGGERNAUT | Weapons/LMGs/BO41_JUGGERNAUT/ | Sí (insignia) |
| BO42 | BO-42 RAMPART | Weapons/LMGs/BO42_RAMPART/ | Compartida (plantilla de categoría) |
| BO43 | BO-43 OVERLORD | Weapons/LMGs/BO43_OVERLORD/ | Compartida (plantilla de categoría) |
| BO44 | BO-44 VANDAL | Weapons/LMGs/BO44_VANDAL/ | Compartida (plantilla de categoría) |
| BO45 | BO-45 SIEGEBREAKER | Weapons/LMGs/BO45_SIEGEBREAKER/ | Compartida (plantilla de categoría) |
| BO46 | BO-46 WHIRLWIND | Weapons/LMGs/BO46_WHIRLWIND/ | Compartida (plantilla de categoría) |

### Weapons/Revolvers/

| ID | Codename | Ruta virtual | Geometría propia |
|---|---|---|---|
| BO52 | BO-52 MAGNUM | Weapons/Revolvers/BO52_MAGNUM/ | Sí (insignia) |
| BO56 | BO-56 PEACEMAKER | Weapons/Revolvers/BO56_PEACEMAKER/ | Compartida (plantilla de categoría) |
| BO57 | BO-57 SNAKEEYE | Weapons/Revolvers/BO57_SNAKEEYE/ | Compartida (plantilla de categoría) |
| BO93 | BO-93 WILDCARD | Weapons/Revolvers/BO93_WILDCARD/ | Compartida (plantilla de categoría) |

### Weapons/Launchers/

| ID | Codename | Ruta virtual | Geometría propia |
|---|---|---|---|
| BO61 | BO-61 DEVASTATOR | Weapons/Launchers/BO61_DEVASTATOR/ | Sí (insignia) |
| BO62 | BO-62 SKYFALL | Weapons/Launchers/BO62_SKYFALL/ | Compartida (plantilla de categoría) |
| BO63 | BO-63 BREACHPOINT | Weapons/Launchers/BO63_BREACHPOINT/ | Compartida (plantilla de categoría) |
| BO64 | BO-64 LONGARM | Weapons/Launchers/BO64_LONGARM/ | Compartida (plantilla de categoría) |
| BO65 | BO-65 STINGRAY | Weapons/Launchers/BO65_STINGRAY/ | Compartida (plantilla de categoría) |
| BO66 | BO-66 CATACLYSM | Weapons/Launchers/BO66_CATACLYSM/ | Compartida (plantilla de categoría) |

### Weapons/Melee/

| ID | Codename | Ruta virtual | Geometría propia |
|---|---|---|---|
| BO71 | BO-71 FANG | Weapons/Melee/BO71_FANG/ | Sí (insignia) |
| BO72 | BO-72 KARAMBIT | Weapons/Melee/BO72_KARAMBIT/ | Compartida (plantilla de categoría) |
| BO73 | BO-73 CLEAVER | Weapons/Melee/BO73_CLEAVER/ | Compartida (plantilla de categoría) |
| BO74 | BO-74 WRECKER | Weapons/Melee/BO74_WRECKER/ | Compartida (plantilla de categoría) |
| BO75 | BO-75 TALONS | Weapons/Melee/BO75_TALONS/ | Compartida (plantilla de categoría) |

### Weapons/Special/

| ID | Codename | Ruta virtual | Geometría propia |
|---|---|---|---|
| BO81 | BO-81 SILENTBOLT | Weapons/Special/BO81_SILENTBOLT/ | Sí (insignia) |
| BO82 | BO-82 THUMPER | Weapons/Special/BO82_THUMPER/ | Compartida (plantilla de categoría) |
| BO83 | BO-83 HORNET | Weapons/Special/BO83_HORNET/ | Compartida (plantilla de categoría) |
| BO84 | BO-84 RAILDRIVER | Weapons/Special/BO84_RAILDRIVER/ | Compartida (plantilla de categoría) |
| BO85 | BO-85 WASP | Weapons/Special/BO85_WASP/ | Compartida (plantilla de categoría) |


## 4. Estado real por punto del pedido original

| # | Pedido | Estado |
|---|---|---|
| 1 | Nombres de archivo | No aplica (single-file); resuelto vía ID+codename ya consistentes (sección 1) |
| 2 | Carpetas/estructura de assets | Resuelto como mapa virtual (secciones 2–3), sin archivos físicos |
| 3 | Modelos/skins/texturas por arma | 11/68 con geometría única, 68/68 con skins (`SKIN_REGISTRY`); ampliar geometría es P3 en `WEAPON_ASSET_BACKLOG.md` |
| 4 | Nombres internos en código | Ya consistentes (`WEAPON_CONFIGS` keys), documentados por primera vez aquí |
| 5 | Animaciones asociadas | Estados universales (fire/reload/ADS/inspect) en `WeaponController`; sin animación esquelética (no hay rig, es geometría rígida) |
| 6 | Sonidos asociados | `SoundSynth` con perfil por arma (`soundProfile`) + audio espacial (`PannerNode`); ver `WEAPON_ASSET_BACKLOG.md` para gaps de sonidos no-disparo |
| 7 | Accesorios y ópticas | Solo slot OPTIC poblado (3 miras); GRIP/MAGAZINE/BARREL/STOCK pendientes (P2 backlog) |
| 8 | Estética por arma | VFX de muzzle flash diferenciado por categoría (`MUZZLE_FLASH_PROFILES`); geometría diferenciada solo en las 11 insignia |
| 9 | Iluminación/escala respecto al mapa | No auditado en esta fase — pendiente como tarea siguiente |
| 10 | Ambientación del primer mapa | Fuera del alcance de este documento (es de mapas, no de armas) — ver `MASTER_INDEX.md` para el estado de KRYPTOS-URBAN |

Los puntos 9 y 10 (iluminación/escala del arma respecto al mapa,
ambientación general del mapa) no son de nomenclatura ni de código de
armas: quedan para una fase de arte/iluminación del mapa, no de este
documento.
