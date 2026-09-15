/*
 * Selector de variantes (color/talle) + alta al carrito real, para las
 * fichas de producto (main-product y featured-product) y las tarjetas
 * simples de la grilla. Cada formulario embebe el JSON real del producto
 * de Shopify (product.variants) en un <script type="application/json">.
 */
(function () {
    function initProductForm(form) {
        const dataEl = form.querySelector('[data-product-json]');
        if (!dataEl) return;
        let product;
        try { product = JSON.parse(dataEl.textContent); } catch (e) { return; }

        const optionInputs = form.querySelectorAll('[data-option-index]');
        const variantIdInput = form.querySelector('[data-variant-id-input]');
        const priceDisplay = form.querySelector('[data-price-display]');
        const compareAtDisplay = form.querySelector('[data-compare-at-display]');
        const productImage = form.querySelector('[data-product-image]');
        const addBtn = form.querySelector('[data-add-to-cart]');
        const sellingPlanRadios = form.querySelectorAll('[data-selling-plan-option]');

        function currentSelection() {
            const selection = {};
            optionInputs.forEach((input) => {
                const isActive = input.matches('[data-active="true"]') || (input.tagName === 'SELECT');
                if (input.tagName === 'SELECT') {
                    selection[input.dataset.optionIndex] = input.value;
                } else if (isActive) {
                    selection[input.dataset.optionIndex] = input.dataset.optionValue;
                }
            });
            return selection;
        }

        function findVariant(selection) {
            return product.variants.find((variant) => {
                return ['1', '2', '3'].every((i) => {
                    if (!selection[i]) return true;
                    return variant['option' + i] === selection[i];
                });
            });
        }

        function selectedSellingPlanId() {
            const checked = form.querySelector('[data-selling-plan-option]:checked, [data-selling-plan-option][data-active="true"]');
            if (!checked || checked.dataset.sellingPlanId === 'onetime') return null;
            return checked.dataset.sellingPlanId;
        }

        function updateUI() {
            const variant = findVariant(currentSelection()) || product.variants[0];
            if (!variant) return;
            if (variantIdInput) variantIdInput.value = variant.id;

            const sellingPlanId = selectedSellingPlanId();
            let price = variant.price;
            let compareAt = variant.compare_at_price;
            let sellingPlanUnavailable = false;
            if (sellingPlanId) {
                const allocation = (variant.selling_plan_allocations || []).find((a) => String(a.selling_plan_id) === String(sellingPlanId));
                if (allocation) {
                    price = allocation.price;
                } else {
                    sellingPlanUnavailable = true;
                }
            }

            if (priceDisplay) priceDisplay.textContent = window.VDT.formatMoney(price) + (sellingPlanId && !sellingPlanUnavailable ? ' / mes' : '');
            if (compareAtDisplay) {
                if (compareAt && compareAt > variant.price && !sellingPlanId) {
                    compareAtDisplay.textContent = window.VDT.formatMoney(compareAt);
                    compareAtDisplay.classList.remove('hidden');
                } else {
                    compareAtDisplay.classList.add('hidden');
                }
            }
            if (productImage && variant.featured_image && variant.featured_image.src) {
                productImage.style.opacity = '0';
                setTimeout(() => {
                    productImage.src = variant.featured_image.src;
                    productImage.alt = variant.featured_image.alt || product.title;
                    productImage.style.opacity = '1';
                }, 150);
            }
            if (addBtn) {
                addBtn.disabled = !variant.available || sellingPlanUnavailable;
                addBtn.textContent = !variant.available
                    ? addBtn.dataset.labelSoldOut
                    : addBtn.dataset.labelAvailable;
            }
        }

        optionInputs.forEach((input) => {
            const evt = input.tagName === 'SELECT' ? 'change' : 'click';
            input.addEventListener(evt, () => {
                if (input.tagName !== 'SELECT') {
                    const group = form.querySelectorAll('[data-option-index="' + input.dataset.optionIndex + '"]');
                    group.forEach((el) => el.removeAttribute('data-active'));
                    input.setAttribute('data-active', 'true');
                    const labelTarget = form.querySelector('[data-option-label="' + input.dataset.optionIndex + '"]');
                    if (labelTarget) labelTarget.textContent = input.dataset.optionValue;
                }
                updateUI();
            });
        });

        sellingPlanRadios.forEach((radio) => {
            radio.addEventListener('click', () => {
                sellingPlanRadios.forEach((r) => r.removeAttribute('data-active'));
                radio.setAttribute('data-active', 'true');
                if (radio.type === 'radio') radio.checked = true;
                updateUI();
            });
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!addBtn || addBtn.disabled) return;
            const variant = findVariant(currentSelection()) || product.variants[0];
            const sellingPlanId = selectedSellingPlanId();
            try {
                addBtn.classList.add('opacity-60');
                await window.VDT.cartApi.addToCart(variant.id, 1, null, sellingPlanId);
                window.VDT.cartApi.flashAdded(addBtn);
                if (window.VDT.ui) window.VDT.ui.openPanel('cart-panel');
            } catch (err) {
                alert(err.message);
            } finally {
                addBtn.classList.remove('opacity-60');
            }
        });

        updateUI();
    }

    function initSimpleAddButtons() {
        document.querySelectorAll('[data-add-to-cart-simple]').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const variantId = btn.dataset.addToCartSimple;
                try {
                    btn.classList.add('opacity-60');
                    await window.VDT.cartApi.addToCart(variantId, 1);
                    window.VDT.cartApi.flashAdded(btn);
                    if (window.VDT.ui) window.VDT.ui.openPanel('cart-panel');
                } catch (err) {
                    alert(err.message);
                } finally {
                    btn.classList.remove('opacity-60');
                }
            });
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('[data-product-form]').forEach(initProductForm);
        initSimpleAddButtons();
    });
})();
