/*
 * Carrito real conectado a la Cart AJAX API de Shopify (/cart/add.js,
 * /cart/change.js, /cart.js). Sustituye al carrito de localStorage del
 * prototipo estático: ahora cada línea es un variant_id real de Shopify.
 */
(function () {
    const routes = (window.VDT && window.VDT.routes) || {};
    const FREE_SHIPPING_THRESHOLD = (window.VDT && window.VDT.settings && window.VDT.settings.freeShippingThreshold) || 80;
    const MONEY_FORMAT = (window.VDT && window.VDT.settings && window.VDT.settings.moneyFormat) || '{{amount}}€';

    function formatMoney(cents) {
        const amount = (cents / 100).toFixed(2).replace('.', ',');
        const amountNoDecimals = Math.round(cents / 100).toString();
        const amountComma = amount.replace(',', '.');
        return MONEY_FORMAT
            .replace('{{amount_no_decimals}}', amountNoDecimals)
            .replace('{{amount_with_comma_separator}}', amount)
            .replace('{{amount_with_space_separator}}', amount)
            .replace('{{amount}}', amount)
            .replace(/<\/?[^>]+(>|$)/g, '');
    }
    window.VDT = window.VDT || {};
    window.VDT.formatMoney = formatMoney;

    async function fetchCart() {
        const res = await fetch(routes.cart, { headers: { Accept: 'application/json' } });
        return res.json();
    }

    async function addToCart(id, quantity, properties, sellingPlan) {
        const item = { id: id, quantity: quantity || 1 };
        if (properties) item.properties = properties;
        if (sellingPlan) item.selling_plan = sellingPlan;
        const res = await fetch(routes.cartAdd, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
            body: JSON.stringify({ items: [item] })
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.description || data.message || 'No se pudo añadir el producto al carrito.');
        }
        await refreshCart();
        return data;
    }

    async function changeLine(key, quantity) {
        const res = await fetch(routes.cartChange, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
            body: JSON.stringify({ id: key, quantity: quantity })
        });
        const data = await res.json();
        await refreshCart();
        return data;
    }

    function cartItemRow(item) {
        const row = document.createElement('div');
        row.className = 'flex items-center gap-4';
        const image = item.image
            ? '<img src="' + item.image + '" alt="" class="w-16 h-16 object-cover flex-shrink-0">'
            : '';
        row.innerHTML =
            image +
            '<div class="flex-1">' +
                '<p class="text-sm text-[var(--brown-900)]">' + item.product_title + '</p>' +
                (item.variant_title ? '<p class="text-xs text-[var(--brown-500)]">' + item.variant_title + '</p>' : '') +
                (item.selling_plan_allocation ? '<p class="text-xs text-[var(--matcha-700)]">' + item.selling_plan_allocation.selling_plan.name + '</p>' : '') +
                '<p class="text-xs text-[var(--brown-500)]">' + formatMoney(item.final_price) + '</p>' +
                '<div class="flex items-center gap-2 mt-2">' +
                    '<button data-qty="-1" data-key="' + item.key + '" data-current="' + item.quantity + '" class="qty-btn border border-[var(--brown-500)]/40 text-sm" aria-label="Restar una unidad">-</button>' +
                    '<span class="text-sm w-4 text-center">' + item.quantity + '</span>' +
                    '<button data-qty="1" data-key="' + item.key + '" data-current="' + item.quantity + '" class="qty-btn border border-[var(--brown-500)]/40 text-sm" aria-label="Sumar una unidad">+</button>' +
                '</div>' +
            '</div>' +
            '<button data-remove="' + item.key + '" class="text-[var(--brown-500)] hover:text-[var(--brown-900)] text-sm">Quitar</button>';
        return row;
    }

    function renderCart(cart) {
        const container = document.getElementById('cart-items');
        if (!container) return;
        container.innerHTML = '';
        if (cart.item_count === 0) {
            container.innerHTML = '<p class="text-sm text-[var(--brown-500)] font-light">Tu carrito está vacío.</p>';
        }
        cart.items.forEach((item) => container.appendChild(cartItemRow(item)));

        const subtotalEl = document.getElementById('cart-subtotal');
        const shippingEl = document.getElementById('cart-shipping');
        const totalEl = document.getElementById('cart-total');
        if (subtotalEl) subtotalEl.textContent = formatMoney(cart.items_subtotal_price);
        const freeShippingCents = FREE_SHIPPING_THRESHOLD * 100;
        const qualifiesFreeShipping = cart.items_subtotal_price >= freeShippingCents;
        if (shippingEl) shippingEl.textContent = cart.item_count === 0 ? '—' : (qualifiesFreeShipping ? 'Gratis' : 'Se calcula en el checkout');
        if (totalEl) totalEl.textContent = formatMoney(cart.total_price);

        const progressFill = document.getElementById('shipping-progress-fill');
        const progressText = document.getElementById('shipping-progress-text');
        if (progressFill && progressText) {
            const pct = Math.min(100, (cart.items_subtotal_price / freeShippingCents) * 100);
            progressFill.style.width = pct + '%';
            if (qualifiesFreeShipping) {
                progressText.textContent = 'Envío gratis desbloqueado';
            } else {
                const missing = formatMoney(freeShippingCents - cart.items_subtotal_price);
                progressText.textContent = 'Te faltan ' + missing + ' para conseguir envío gratis';
            }
        }

        container.querySelectorAll('[data-qty]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const next = Math.max(0, parseInt(btn.dataset.current, 10) + parseInt(btn.dataset.qty, 10));
                changeLine(btn.dataset.key, next);
            });
        });
        container.querySelectorAll('[data-remove]').forEach((btn) => {
            btn.addEventListener('click', () => changeLine(btn.dataset.remove, 0));
        });

        renderUpsell(cart);
    }

    function renderUpsell(cart) {
        const upsellBox = document.getElementById('cart-upsell');
        if (!upsellBox) return;
        upsellBox.innerHTML = '';
        const dataEl = document.getElementById('cart-upsell-data');
        if (cart.item_count === 0 || !dataEl) return;
        let candidates;
        try { candidates = JSON.parse(dataEl.textContent); } catch (e) { return; }
        const cartProductIds = cart.items.map((i) => i.product_id);
        const suggestions = candidates.filter((p) => !cartProductIds.includes(p.product_id)).slice(0, 2);
        if (suggestions.length === 0) return;

        const title = document.createElement('p');
        title.className = 'text-xs eyebrow uppercase text-[var(--brown-500)] mb-3';
        title.textContent = 'Combinalo con...';
        upsellBox.appendChild(title);

        suggestions.forEach((item) => {
            const row = document.createElement('div');
            row.className = 'flex items-center justify-between gap-3 mb-3';
            row.innerHTML =
                '<span class="text-sm text-[var(--brown-700)] font-light">' + item.title + ' · ' + formatMoney(item.price) + '</span>' +
                '<button data-upsell-add="' + item.variant_id + '" class="text-xs uppercase tracking-wide text-[var(--matcha-700)] hover:text-[var(--matcha-900)]">Añadir</button>';
            upsellBox.appendChild(row);
        });
        upsellBox.querySelectorAll('[data-upsell-add]').forEach((btn) => {
            btn.addEventListener('click', () => addToCart(btn.dataset.upsellAdd, 1));
        });
    }

    function updateBadges(cart) {
        const cartBadge = document.getElementById('cart-count');
        if (cartBadge) {
            cartBadge.textContent = cart.item_count;
            cartBadge.classList.toggle('hidden', cart.item_count === 0);
            cartBadge.classList.toggle('flex', cart.item_count > 0);
        }
    }

    async function refreshCart() {
        const cart = await fetchCart();
        window.VDT.cart = cart;
        renderCart(cart);
        updateBadges(cart);
        document.dispatchEvent(new CustomEvent('vdt:cart:updated', { detail: cart }));
        return cart;
    }

    function flashAdded(btn) {
        if (!btn) return;
        const original = btn.textContent;
        btn.textContent = 'Añadido ✓';
        btn.classList.add('cart-added');
        setTimeout(() => { btn.textContent = original; btn.classList.remove('cart-added'); }, 1500);
    }

    window.VDT.cartApi = { addToCart, changeLine, refreshCart, formatMoney, flashAdded };

    document.addEventListener('DOMContentLoaded', () => {
        refreshCart().catch(() => {});

        document.getElementById('checkout-btn') && document.getElementById('checkout-btn').addEventListener('click', () => {
            window.location.href = '/checkout';
        });
    });
})();
