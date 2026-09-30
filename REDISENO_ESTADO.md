# VITALAIR — Estado del rediseño (30/09/2026)

Tema borrador (NO publicado): "VitalAir Rediseño (borrador)" · id 210824036743
Vista previa: https://bqu0sm-1a.myshopify.com/?preview_theme_id=210824036743
Tema publicado (Horizon, id 210811715975) sin tocar.

## Hecho en el borrador
- assets/vitalair.css + snippets/vitalair-base.liquid (paleta crema/bosque/madera, Fraunces + Inter, mobile-first)
- sections/vitalair-home.liquid + templates/index.json: hero, qué es, piezas, sabores (13), 3 pasos, packs con precio/unidad y ahorro calculado, opiniones (desactivado hasta tener reseñas reales), FAQ, CTA final
- sections/vitalair-product.liquid + templates/product.json: galería, selector de pack, selector de sabores (propiedad "Sabores" en el pedido), CTA sticky móvil, acordeones
- Barra de anuncio sin claims; cabecera sin buscador/país/idioma
- Textos solo con datos comprobables (fotos: piezas, 13 sabores, packs 1/3/4/5, precios)

## Pendiente (store-level, se aplica al publicar)
- Corregir fichas: los 3 modelos "Básico/Premium/Pro" describen un aparato electrónico (batería, OLED, app) que NO coincide con las fotos reales → pasar a borrador
- Pack: renombrar título, reescribir descripción, SEO, alt de fotos, adjuntar foto iryiz6, desactivar tracking de stock (0 uds = agotado)
- Nombre de tienda "Mi tienda", menú, footer, políticas (envíos/devoluciones/términos/aviso legal)
- Envío, devolución y garantía reales; coste por producto; ¿lleva nicotina?

## Actualización (marca de un solo producto)
- Producto publicado en "Tienda online" (antes daba 404 en la vista previa).
- Home: hero "Un nuevo ritual para tu día", qué es, elige tu sabor (13 tarjetas con foto, descripción sensorial y enlace que preselecciona el sabor en la ficha), cómo funciona, hábito (pequeños pasos, sin claims médicos), bienestar/materiales, packs, confianza (envío, pago, 14 días, garantía legal, info@vitalair.online), FAQ, CTA final.
- Ficha: lee ?flavor= y preselecciona el sabor (sections/vitalair-preselect.liquid).
- Fotos localizadas por texto alternativo, no por posición. Raspberry/Lemon/Maple Pepper asignadas por orden de envío (sin verificar).
- Copy sensorial por sabor basado solo en el nombre del sabor: confirmar con el proveedor.
- Pendiente: instrucciones de uso reales, duración, qué contiene cada sobre, nombre de la tienda, políticas, reseñas reales, publicar el tema.

## Constructor de compra (VitalAir v3)
- Tema borrador "VitalAir v3 (corrección sabores)" id 210832589191: corrige sabores cortados por comas en la home y el cambio de fotos Raspberry/Lemon, y estrena el constructor.
- Ficha: [Inhalador + sabores] N inhaladores (1-5) x 3 = máximo de sabores, repartidos libremente, contador N/M, barra fija, tope que bloquea el "+". Se añade UNA línea al carrito (variante del pack) con propiedades "Sabores", "Nº de sabores" y _bundle (oculta, evita fusiones).
- [Solo sabores]: aparece solo si existe el producto activo con handle vitalair-sabores y 13 variantes cuyo título sea el nombre del sabor. Falta el precio por sabor (no inventado).
- Variante nueva 2 inhaladores (39,98 €, sin tachado), opciones renombradas "N inhaladores (Nx)".
- Código en VITALAIR_WEB/builder (js, css, test Playwright: 54 comprobaciones OK).

## v4 — Sabores como extras + 15 % (30/09/2026)
- Tema borrador: "VitalAir v4 (extras + 15%)" (duplicado del v3, sin publicar).
- Producto `vitalair-sabores` ("Sabor extra VitalAir", 13 variantes por sabor, DRAFT): 100 uds reales por variante, rastreadas, política DENY. Precio 0,00 a propósito: **falta el precio del sabor**. Mientras valga 0 o el producto esté en borrador, la web no muestra sabores (nunca se venden a 0 €).
- Descuento automático real "VitalAir 15% en toda la tienda" (todo el pedido, combina solo con envío). Cambiar % en `snippets/vitalair-promo-pct.liquid` + en Shopify.
- Builder: inhalador base + sabores como líneas propias del carrito (sin límite, tope = stock), resumen Subtotal / 15 % / Total. 51 pruebas OK (`VITALAIR_WEB/builder/test/run.js`).
- Pop-up del 15 % (`sections/vitalair-promo.liquid`, en footer-group), barra superior y home/FAQ/packs actualizados. Retirados los mensajes "envío gratis incluido" por pack y "hasta 3 sabores".
