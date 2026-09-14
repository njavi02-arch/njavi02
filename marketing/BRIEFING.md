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

- Instagram / Pinterest (redes sociales)
- Cualquier plataforma de anuncios de pago (Meta Ads, Google Ads)

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

## Próximo objetivo

Seguir bajando el TOP 10 de acciones inmediatas del plan de crecimiento. Pendiente de decisión/acción del usuario (no ejecutable solo por API):
- Verificar que la tienda no tiene contraseña de "tienda en construcción" activa
- Decidir qué hacer con los 15 productos no publicados
- Instalar app de reseñas de producto (requiere elegir app en la App Store)
- Conectar Google Merchant Center y catálogo de Meta/Instagram Shopping (requieren cuentas externas de Google/Meta)
- Configurar Meta Pixel (requiere cuenta de Meta Business)
