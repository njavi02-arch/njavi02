# VITALAIR — Auditoría Fase 1 (solo lectura, 30/09/2026)

Tienda: bqu0sm-1a.myshopify.com · Plan Basic · EUR · Tema Horizon (único, publicado, sin personalizar)
Nota: competencia (soyvaho.store) y storefront público no accesibles por la red de la sesión; auditoría hecha vía Admin API.

## Bloqueantes (vender así es un riesgo)
1. **Pack System sin stock**: las 4 variantes tienen inventario rastreado con 0 uds → probablemente "agotado", no se puede comprar.
2. **Claims inventados publicados** en los 3 productos individuales (texto escrito como borrador, no verificado con el proveedor):
   "+2.000 reseñas verificadas 4,8/5", "4,9/5 usuarios pro", control por voz IA, app iOS/Android, OLED, 800 inhalaciones,
   garantía 2-3 años "sin condiciones", soporte 24/7, reparación 48 h, envío gratis a toda Europa, "pago Stripe".
   → Reseñas falsas = infracción de consumo UE/ES; specs sin respaldo = reclamaciones/devoluciones.
3. **Esos 3 productos no tienen ninguna foto** (featuredMedia null) y 3 variantes sin tracking de inventario.
4. **Políticas legales**: solo existe Política de privacidad. Faltan Devoluciones, Envíos, Términos, Aviso legal. Footer solo tiene "Buscar".
5. **Categoría regulada**: "Inhalador Smokeless / vapor". Meta, TikTok y Google Ads prohíben o restringen vapeo/nicotina, y procesadores de pago pueden restringirlo. Confirmar qué contiene el producto (¿nicotina? ¿aromas?) y cumplimiento (TPD/Real Decreto 579/2017 si lleva nicotina, edad mínima).
6. Imágenes del pack: generadas con IA (nombre "Gemini_Generated_Image") → no son el producto real.

## Otros fallos
- Nombre de tienda "Mi tienda"; sin descripción SEO ni title/meta en productos.
- Texto basura `]]>` visible al final de todas las descripciones; emojis y precio repetido dentro de la descripción.
- Productos sin sabores como variante (los 13 sabores solo se citan en texto); modelos con una sola variante "Default Title".
- Colección única "Página de inicio" con 1 producto; menú: Inicio / Catálogo / Contacto.
- Página /pages/vitalair con datos inventados (inhalaciones, batería, devolución 30 d, soporte 24/7).
- Sin wallets de pago, sin coste de producto (unitCost null) → no puedo calcular márgenes para packs.
- Precio pack: 1x 19,99 · 3x 44,97 (-25 %) · 4x 57,97 · 5x 64,95 (-35 %). Coherentes entre sí, pero los descuentos dependen de margen desconocido.

## KEEP / IMPROVE / REMOVE / CREATE
KEEP: precios 19,99/49,99/89,99, SKUs, tema Horizon (base rápida), disclaimer "no es producto médico", estructura de packs.
IMPROVE: fichas (copy corto), variantes, SEO, menú, footer, home.
REMOVE: reseñas/ratings inventados, claims técnicos no verificados, `]]>`, emojis en descripciones.
CREATE: fotos reales, selector de sabor, home de marca, FAQ real, políticas, sección de reseñas vacía lista, sticky CTA móvil.

## Necesito de ti (no se puede deducir)
- Ficha técnica REAL del proveedor (qué incluye, batería, puffs, si lleva nicotina).
- Fotos reales del producto (o permiso para usar las del proveedor).
- Política real de envío/devolución/garantía y plazos.
- Coste unitario por modelo (para packs).
