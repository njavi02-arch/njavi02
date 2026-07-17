# KOHI & CHA — theme de Shopify

Theme Online Store 2.0 completo (Liquid + JSON templates), no un prototipo estático.
Todo lo que ves conectado a Shopify es real: productos, colecciones, carrito (Cart AJAX API),
cuenta de cliente, búsqueda predictiva, blog, newsletter.

## Instalar

1. Shopify Admin → **Tienda online → Temas → Agregar tema → Subir archivo ZIP**.
2. Subí el `.zip` de esta carpeta (no del repo entero).
3. El tema se sube **sin publicar** — podés previsualizarlo antes de activarlo.

## Configuración inicial (una sola vez)

Para que se vea igual que el diseño de referencia, necesitás crear estos recursos reales en tu tienda:

- **Colecciones**: `cafe`, `matcha`, `accesorios`, `regalos` (los handles deben coincidir con los
  valores de "Tipo de producto" que uses en cada producto: Cafe / Matcha / Accesorios / Regalos).
- **Menú de navegación** (`Admin → Navegación`): un menú `main-menu` con ítems de 2 niveles
  (ej: "Café" con sub-enlaces "Café en grano", "Café molido", etc.) — el header los convierte
  automáticamente en mega-menú.
- **Menú `footer`**: para las columnas "Comprar" / "Ayuda" del footer.
- **Logo / favicon**: el theme trae un logotipo "KOHI & CHA" construido en vivo (círculo +
  tipografía + texto en japonés) y un favicon incluido — podés reemplazar ambos en
  `Personalizar tema → Configuración del tema → Marca` si tenés archivos de marca definitivos.
- **Suscripciones** (opcional): el toggle "Compra única / Suscribite" en la ficha de café solo
  aparece si el producto tiene un grupo de planes de venta real configurado (Shopify Subscriptions
  u otra app de suscripciones).
- **Reseñas**: el carrusel de reseñas es contenido editable por bloques desde el editor de temas
  (no inventa datos). Para reseñas verificadas reales, conectá una app (Judge.me, Loox, etc.).
- **Código de descuento de bienvenida**: en Configuración del tema → Popup de bienvenida, cargá
  un código que exista de verdad en `Admin → Descuentos` — el popup arma un enlace que lo aplica
  automáticamente al carrito.

## Notas de diseño

Paleta, tipografía y componentes están documentados inline en `config/settings_schema.json`
(grupo "Colores") y en los comentarios de cada sección. Los íconos son un set de líneas propio
(`snippets/icon.liquid`), no un paquete externo.
