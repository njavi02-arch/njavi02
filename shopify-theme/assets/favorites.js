/*
 * Favoritos: Shopify no tiene lista de deseos nativa, así que esto sigue
 * viviendo en localStorage (real, local al navegador, sin backend) tal
 * como en el prototipo original — ahora referenciando product_id reales.
 */
(function () {
    const FAV_KEY = 'vdt-favorites';

    function readFavorites() {
        try { return JSON.parse(localStorage.getItem(FAV_KEY)) || []; } catch (e) { return []; }
    }
    function writeFavorites(list) {
        try { localStorage.setItem(FAV_KEY, JSON.stringify(list)); } catch (e) {}
    }

    function toggleFavorite(item, btnEl) {
        let favs = readFavorites();
        const exists = favs.find((f) => String(f.id) === String(item.id));
        if (exists) {
            favs = favs.filter((f) => String(f.id) !== String(item.id));
            if (btnEl) btnEl.removeAttribute('data-active');
        } else {
            favs.push(item);
            if (btnEl) btnEl.setAttribute('data-active', 'true');
        }
        writeFavorites(favs);
        renderFavorites();
        updateFavoritesBadge();
    }

    function renderFavorites() {
        const container = document.getElementById('favorites-items');
        if (!container) return;
        const favs = readFavorites();
        container.innerHTML = favs.length === 0
            ? '<p class="text-sm text-[var(--brown-500)] font-light">Todavía no agregaste favoritos.</p>'
            : '';
        favs.forEach((item) => {
            const row = document.createElement('div');
            row.className = 'flex items-center justify-between gap-4';
            row.innerHTML =
                '<a href="' + item.url + '" class="flex items-center gap-4 flex-1">' +
                    (item.image ? '<img src="' + item.image + '" alt="" class="w-14 h-14 object-cover flex-shrink-0">' : '') +
                    '<div>' +
                        '<p class="text-sm text-[var(--brown-900)]">' + item.name + '</p>' +
                        '<p class="text-xs text-[var(--brown-500)]">' + (window.VDT.formatMoney ? window.VDT.formatMoney(item.price) : item.price) + '</p>' +
                    '</div>' +
                '</a>' +
                '<button data-unfav="' + item.id + '" class="text-[var(--brown-500)] hover:text-[var(--brown-900)] text-sm">Quitar</button>';
            container.appendChild(row);
        });
        container.querySelectorAll('[data-unfav]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const item = favs.find((f) => String(f.id) === String(btn.dataset.unfav));
                if (item) toggleFavorite(item);
            });
        });
    }

    function updateFavoritesBadge() {
        const favCount = readFavorites().length;
        const favBadge = document.getElementById('favorites-count');
        if (favBadge) {
            favBadge.textContent = favCount;
            favBadge.classList.toggle('hidden', favCount === 0);
            favBadge.classList.toggle('flex', favCount > 0);
        }
        const favIds = readFavorites().map((f) => String(f.id));
        document.querySelectorAll('.fav-btn[data-product-id]').forEach((btn) => {
            btn.toggleAttribute('data-active', favIds.includes(String(btn.dataset.productId)));
        });
    }

    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.fav-btn[data-product-id]');
        if (!btn) return;
        toggleFavorite({
            id: btn.dataset.productId,
            name: btn.dataset.productTitle,
            price: parseInt(btn.dataset.productPrice, 10),
            image: btn.dataset.productImage || '',
            url: btn.dataset.productUrl
        }, btn);
    });

    window.VDT = window.VDT || {};
    window.VDT.favoritesApi = { readFavorites, toggleFavorite, renderFavorites, updateFavoritesBadge };

    document.addEventListener('DOMContentLoaded', () => {
        renderFavorites();
        updateFavoritesBadge();
    });
})();
