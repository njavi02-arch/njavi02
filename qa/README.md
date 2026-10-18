# Banco de pruebas (simulación, no web real)

Renderiza el HTML equivalente al del tema (cabecera, tarjetas "Próximamente", carrito) con el CSS y JS **reales** del tema
en Chromium (Playwright) y un carrito simulado en memoria. Limitaciones: sin Liquid real, sin GSAP, iconos como círculos,
fuente Cormorant Garamond no disponible (se usa una serif de reserva, más ancha: resultado conservador), sin dispositivo físico.

Uso: copiar `assets/theme.css`, `assets/theme.js`, `assets/cart.js` (como `theme-cart.js`) y `assets/tailwind-built.css` del tema junto a estos
archivos, extraer el `<style>` de `launch-roadmap.liquid` a `roadmap.css` y el de `header.liquid` a `header-fix.css`;
`node server.js &` y `node test1.js` (…`test4.js`, `green.js`, `shots.js`).
