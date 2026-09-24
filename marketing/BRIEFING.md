# KOHI & CHA — Briefing de marketing (fuente de verdad)

> Este archivo es la memoria persistente del proyecto de publicidad/marketing.
> Actualizarlo al terminar cada encargo para que ninguna sesión futura tenga que
> re-descubrir el contexto desde cero.

## Marca

- **Nombre:** KOHI & CHA
- **Dominio:** kohiycha.com (Shopify, plan Basic)
- **Producto:** té matcha (premium, ceremonial), matcha latte con sabores, café de especialidad, accesorios
- **Ubicación legal:** Parla, Madrid, España — NIF B44984136
- **Idiomas activos en la tienda:** Español (principal), Inglés

## Activos ya creados (no volver a generar desde cero)

- `marketing/assets/kohi-cha-logo-original.jpg` — logo oficial real
- `marketing/assets/products/matcha-latte-*-ebe3d5.png` — cutouts con alpha real de los 5 sabores de Matcha Latte (coco, fresa, mango, orgánico, vainilla), fondo #EBE3D5
- `marketing/email-presentacion-matcha-v2.html` — email de presentación de marca ya diseñado y art-dirigido
- Ficha del producto **ThermoWave — Vaso Térmico** en Shopify: 5 variantes de color con foto propia (Negro, Azul marino, Verde militar, Rosa, Blanco)
- Colección **Matcha**: imagen de banner = campo de té con Monte Fuji
- Colección **Matcha Latte**: imagen de banner = agricultor recogiendo té

## Canales conectados (listos para usar)

- **Shopify** — productos, colecciones, descuentos, inventario
- **MailerLite** — email marketing (campañas, automatizaciones, suscriptores)
- **Adobe Creative / Canva** — diseño de imágenes y gráficos
- **Gmail** — correo

## Canales NO conectados (requieren que el usuario los vincule primero)

- Instagram / TikTok directos (sin conector propio)
- Cualquier plataforma de anuncios de pago (Meta Ads, Google Ads)

## Canales conectados vía Metricool (añadido 2026-09-15)

- **Metricool** — brand/blogId `6963190`, timezone Europe/Madrid, cuenta de Pinterest conectada `kohicha0532`.
  Permite programar y publicar pines de Pinterest directamente (`createScheduledPost`).
  Tableros ya creados por el usuario: "Ritual del Matcha" (id Metricool `1139129368189814603`),
  "Recetas Matcha Latte" (id Metricool `1139129368189814605`) — el `boardId` se puede pasar como
  nombre exacto y Metricool lo resuelve solo si es unívoco.

## Lecciones aprendidas (para no repetir errores)

- Al subir imágenes nuevas para variantes de producto en Shopify: usar `productSet`
  incluyendo **todas** las imágenes deseadas (existentes + nuevas) en la misma
  llamada — nunca solo las nuevas, porque reemplaza toda la galería y borra lo
  que no se incluya explícitamente.
- Las imágenes pegadas directamente en el chat no llegan como archivo accesible;
  el usuario debe subirlas primero a Shopify → Contenido → Archivos, y luego
  confirmar el orden/nombre de subida para poder identificarlas sin ambigüedad.

## Datos reales de la tienda (Shopify Analytics, verificado — no inventar)

- **0 pedidos, 0% conversión** en los últimos 90 días
- 815 sesiones/90d, pero 773 desde EE.UU. con actividad casi nula (patrón de bot); tráfico real de España ~10 sesiones/90d
- Solo 3 clientes registrados, ninguno con pedidos (uno es la cuenta del propio dueño)
- 7 de 23 productos son realmente comprables (10 archivados, 5 en borrador)
- Conclusión: es una tienda pre-lanzamiento sin tracción real, no un negocio con ventas que escalar

## Historial de encargos

| Fecha | Encargo | Resultado |
|---|---|---|
| 2026-09-14 | Plan de crecimiento y captación 90 días (análisis, canales, SEO, países, B2B, contenido, presupuesto) | Documento publicado: https://claude.ai/code/artifact/c848d4bc-fed7-4bff-873c-4aeb03904ac1 |

| 2026-09-14 | Ejecución TOP 10 (parte 1): restaurar SEO de colecciones Matcha/Matcha Latte, publicar artículo "Matcha vs. café" en el blog, enlazar el blog en el menú principal | Hecho — collectionUpdate x2, articleCreate, menuUpdate (añadiendo, no reemplazando, los items existentes) |

## Stock real (confirmado por el usuario, 2026-09-14 — no volver a preguntar)

- **Matcha Premium**: 50 kg reales, activo — coincide con lo que ya marca Shopify
- **ThermoWave**: stock real, activo — sin cambios
- **Matcha Latte** (5 sabores): NO hay stock físico todavía, está en camino. El usuario pidió dejarlo visible/activo en la web tal cual (no ocultarlo mientras llega) — la política de envíos ya cubre el caso de pedido sin stock (reembolso o alternativa)
- **Los 15 productos ocultos** (10 archivados + 5 en borrador: café, matchas ceremoniales, accesorios, packs): sin stock confirmado → **decisión: se quedan como están, no se publica nada nuevo por ahora**

| 2026-09-14 | Contenido (parte 2): 2º artículo del blog ("Ceremonial vs. culinario"), guiones listos para grabar de la semana 1 (TikTok/Reels) | Hecho — artículo publicado; guiones en `marketing/contenido-semana-1.md`. Sin conector de TikTok/Instagram en esta sesión — publicar los vídeos es acción manual del usuario |

| 2026-09-14 | Contenido (parte 3): 10 pines listos para Pinterest, todos con imagen ya existente salvo uno | Hecho — `marketing/pinterest-primeros-pines.md`. Sin conector de Pinterest — publicar es acción manual del usuario |

| 2026-09-15 | Contenido (parte 4): programar los 9 pines listos (todos salvo el #2) en Metricool → Pinterest, en los tableros reales creados por el usuario | Hecho — 9 posts creados vía `createScheduledPost` (Ritual del Matcha: 4, Recetas Matcha Latte: 5), repartidos del 16 al 20 de septiembre. Los 5 cutouts de Matcha Latte se subieron primero a Shopify Files (`stagedUploadsCreate` + `fileCreate`) para tener URL pública. Falta solo el pin #2 (necesita imagen nueva) |

| 2026-09-15 | Reprogramar los 9 pines a mejores horarios | Hecho — Metricool no tiene datos de "mejor hora" para Pinterest (`getBestTimeToPostByNetwork` solo cubre facebook/instagram/twitter/linkedin/tiktok/youtube), y la cuenta es nueva sin historial propio. Se movieron a horario general recomendado para Pinterest (noches entre semana 20:00-21:00, sábado/domingo mañana y noche), del 16 al 22 de septiembre, vía `updateScheduledPost` sobre los mismos 9 posts |

| 2026-09-24 | Auditoría y mejora de profesionalidad web (ecommerce expert) | Hecho — Página Contacto: borrada dirección física y NIF (solo email + teléfono). Aviso Legal: NIF corregido (B44984136). Colecciones: agregadas descripciones profesionales a Accesorios, Regalos, Destacados, Packs Premium, Matcha Latte. Página Sobre Nosotros: reescrita de forma concisa y profesional. Descripción de Matcha: reorganizada en párrafos claros. Resultado: web más seria, sin exposición de datos innecesarios, con UX profesional en todas las colecciones |

| 2026-09-24 | Integración de galería de 6 imágenes en Sobre Nosotros | Hecho — Descargadas 7 imágenes de Adobe Stock (image 07 corrupta). Subidas a Shopify mediante stagedUploadsCreate + fileCreate. URLs permanentes en CDN de Shopify. Página Sobre Nosotros actualizada con grid responsive 4-columnas + texto profesional. Imágenes: 01-Quién hay detrás, 02-Nuestra misión, 03-Nuestra visión, 04-Qué es el matcha, 05-Propiedades y beneficios, 06-Recetas Kohi & Cha. **Todas las imágenes ahora visibles en la web** |

## Decisiones sobre formato de publicación (2026-09-15 — no volver a preguntar)

- **Instagram Reels**: publicar primero como **Trial Reel** (`instagramData.type = "TRIAL_REEL"`,
  visible solo a no-seguidores, sirve para testear rendimiento) y, pasado un tiempo si va bien,
  volver a publicar/promocionar como Reel normal al feed. Aplica a los 6 guiones de
  `marketing/contenido-semana-1.md` en cuanto estén grabados.
- **TikTok**: no tiene equivalente a los Trial Reels — no hay modo de prueba de audiencia,
  todo lo publicado sale directo con la privacidad elegida. Ahí se publica normal desde el principio.
- Bloqueadores para ejecutar esto: (1) conectar Instagram y TikTok en Metricool — solo Pinterest
  está conectado ahora mismo; (2) grabar los 6 vídeos de `contenido-semana-1.md`, que hoy son
  solo guiones.

## Próximo objetivo

Seguir bajando el TOP 10 de acciones inmediatas del plan de crecimiento. Pendiente de decisión/acción del usuario (no ejecutable solo por API):
- Verificar que la tienda no tiene contraseña de "tienda en construcción" activa
- Decidir qué hacer con los 15 productos no publicados
- Instalar app de reseñas de producto (requiere elegir app en la App Store)
- Conectar Google Merchant Center y catálogo de Meta/Instagram Shopping (requieren cuentas externas de Google/Meta)
- Configurar Meta Pixel (requiere cuenta de Meta Business)
