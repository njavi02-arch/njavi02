// Genera el HTML equivalente al que producen header.liquid, launch-roadmap.liquid y cart-drawer.liquid
const nav = [
  ['RED SMILE','/products/red-smile-matcha-premium-1kg'],
  ['Matcha Premium · Soon','/#matcha-premium'],
  ['Matcha Latte · Soon','/#matcha-latte'],
  ['Next Drops','/#next-drops'],
  ['Nuestra historia','/pages/sobre-nosotros'],
];
const icon = (id,cls)=>`<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="9"/></svg>`;
const cards = [
  ['matcha-premium','Coming soon','Matcha Premium','Una nueva forma de descubrir el matcha está en camino.','Avísame'],
  ['matcha-latte','Próximamente','Matcha Latte','Estamos preparando las futuras variedades de matcha latte. Todavía no están disponibles.','Avísame'],
  ['next-drops','Next drop','Nuevos lanzamientos','RED SMILE es el primero de una serie de ediciones. Cuando haya novedades confirmadas, serás de los primeros en saberlo.','Apuntarme'],
];
module.exports = (opts={}) => `<!DOCTYPE html><html lang="es" class="scroll-smooth"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="/tailwind-built.css"><link rel="stylesheet" href="/theme.css"><link rel="stylesheet" href="/roadmap.css"><link rel="stylesheet" href="/header-fix.css">
<style>html{overflow-x:hidden}.side-panel{box-shadow:none}.side-panel.open{box-shadow:-24px 0 50px rgba(74,44,32,.18)}
:root{--cream:#F3ECE0;--cream-deep:#E8DECB;--beige:#CBB99C;--brown-900:#211811;--brown-800:#332619;--brown-700:#4A3A28;--brown-500:#7C6A54;--matcha-900:#14100D;--matcha-700:#B3261E;--matcha-500:#E4574D;--gold:#A47B4C}
${opts.extraCss||''}</style></head>
<body class="antialiased"><div id="custom-cursor"><span id="custom-cursor-text"></span></div>
<div id="site">
<div class="fixed top-0 left-0 w-full z-50 bg-[var(--brown-900)] text-[var(--cream)]" id="ann"><div class="max-w-7xl mx-auto px-6 md:px-10 py-2.5"><div class="announcement-rotator"><span class="announcement-msg text-[0.68rem] tracking-[0.2em] uppercase">Matcha premium · Origen China</span></div></div></div>
<header id="main-header" class="fixed top-8 left-0 w-full z-40"><nav class="max-w-7xl mx-auto flex items-center justify-between px-6 md:px-10 py-5 gap-4">
<a href="/" id="logo-mark" class="shrink-0"><span class="inline-flex items-center gap-2.5"><svg viewBox="0 0 32 32" class="w-6 h-6 shrink-0" fill="none" stroke="var(--matcha-700)" stroke-width="1.4"><circle cx="16" cy="16" r="13.5"></circle></svg><span class="font-display italic text-2xl tracking-wide leading-none">KOHI &amp; CHA</span></span></a>
<div class="kc-nav-desktop items-center gap-9 text-xs tracking-[0.15em] uppercase" id="desk-nav">${nav.map(([t,u])=>`<a href="${u}" class="header-link">${t}</a>`).join('')}</div>
<div class="kc-nav-icons flex items-center gap-5 shrink-0">
<button id="search-toggle" class="header-icon">${icon('s','w-[1.1rem] h-[1.1rem]')}</button><button id="account-toggle" class="header-icon">${icon('a','w-[1.1rem] h-[1.1rem]')}</button><button id="favorites-toggle" class="relative header-icon">${icon('h','w-[1.1rem] h-[1.1rem]')}<span id="favorites-count" class="hidden">0</span></button>
<button id="cart-toggle" class="relative header-icon">${icon('b','w-[1.1rem] h-[1.1rem]')}<span id="cart-count" class="hidden absolute -top-2 -right-2 bg-[var(--matcha-700)] text-[var(--cream)] text-[0.6rem] w-4 h-4 rounded-full items-center justify-center">0</span></button>
<button id="menu-toggle" class="kc-nav-toggle header-icon" aria-expanded="false">${icon('m','w-6 h-6')}</button></div></nav>
<div id="mobile-menu" class="hidden flex-col gap-1 px-6 pb-6 text-[var(--brown-700)] bg-[var(--cream)] max-h-[70vh] overflow-y-auto"><a href="/" class="py-3 border-b border-[var(--brown-500)]/10">Inicio</a>${nav.map(([t,u])=>`<a href="${u}" class="py-3 border-b border-[var(--brown-500)]/10">${t}</a>`).join('')}</div></header>
<main><section id="hero-ph" style="min-height:100vh;background:#211811;color:#F3ECE0;padding:9rem 1.5rem 3rem"><h1 style="font-size:4rem">RED SMILE</h1><a class="kc-rh-cta" href="/products/red-smile-matcha-premium-1kg" style="background:#B3261E;color:#fff;display:inline-flex;min-height:3rem;padding:0 2rem;align-items:center">Comprar RED SMILE</a><input id="t-input" type="email" placeholder="email" style="display:block;margin-top:1rem;color:#000"></section>
<section id="proximamente" class="kc-rm"><div class="kc-rm-head reveal"><div class="gold-rule mx-auto mb-5"></div><span class="eyebrow text-xs uppercase text-[var(--matcha-700)]">Próximos lanzamientos</span><h2 class="font-display italic kc-rm-title">RED SMILE es solo el primero</h2><p class="kc-rm-sub">Trabajamos por lanzamientos. Estas categorías están en preparación y todavía no se pueden comprar.</p></div>
<div class="kc-rm-grid">${cards.map(([id,b,t,x,c])=>`<article class="kc-rm-card reveal" id="${id}"><span class="kc-rm-badge">${b}</span><h3 class="kc-rm-card-title">${t}</h3><p class="kc-rm-card-text">${x}</p><a href="#club" class="kc-rm-cta">${c}</a></article>`).join('')}</div></section>
<section id="club" style="min-height:70vh;background:#211811;color:#F3ECE0;padding:6rem 1.5rem"><h2>Sé de los primeros</h2></section></main></div>
<div class="panel-backdrop" id="panel-backdrop"></div>
<aside id="cart-panel" class="side-panel"><div class="flex items-center justify-between p-7 border-b border-[var(--brown-500)]/15"><h3 class="font-display text-2xl text-[var(--brown-900)] italic">Carrito</h3><button class="panel-close text-2xl leading-none text-[var(--brown-700)]">&times;</button></div>
<div class="px-7 pt-5"><p id="shipping-progress-text" class="text-xs text-[var(--brown-700)] mb-2">…</p><div class="shipping-progress-track"><div id="shipping-progress-fill" class="shipping-progress-fill" style="width:0%"></div></div></div>
<div id="cart-items" class="flex-1 overflow-y-auto p-7 flex flex-col gap-6"></div><div id="cart-upsell" class="px-7 pb-3"></div><style>#cart-upsell:empty { display: none; }</style>
<div class="p-7 border-t border-[var(--brown-500)]/15 text-sm text-[var(--brown-700)]"><div class="flex justify-between mb-2"><span>Subtotal</span><span id="cart-subtotal">0,00 €</span></div><div class="flex justify-between mb-2"><span>Envío</span><span id="cart-shipping">—</span></div><div class="flex justify-between text-[var(--brown-900)] text-base mt-4 pt-4 border-t"><span>Total</span><span id="cart-total">0,00 €</span></div><button id="checkout-btn" class="mt-6 w-full bg-[var(--matcha-700)] text-[var(--cream)] py-4 text-xs tracking-[0.2em] uppercase">Finalizar compra</button></div></aside>
${opts.upsellJson!==undefined?`<script type="application/json" id="cart-upsell-data">${opts.upsellJson}</script>`:''}
<script>window.VDT={routes:{cartAdd:'/cart/add.js',cartChange:'/cart/change.js',cartUpdate:'/cart/update.js',cart:'/cart.js'},settings:{freeShippingThreshold:55,moneyFormat:'{{amount_with_comma_separator}} €'}};</script>
<script src="/theme.js"></script><script src="/theme-cart.js"></script></body></html>`;
