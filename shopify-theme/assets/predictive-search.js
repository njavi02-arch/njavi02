/*
 * Búsqueda real contra la Predictive Search API de Shopify
 * (/search/suggest.json) — sustituye el filtro en memoria del prototipo.
 */
(function () {
    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    const overlay = document.getElementById('search-overlay');
    if (!input || !results) return;

    const routes = (window.VDT && window.VDT.routes) || {};
    let debounceTimer = null;
    let activeController = null;

    function renderEmpty(query) {
        results.innerHTML = '<p class="p-6 text-sm text-[var(--brown-500)] font-light">Sin resultados para "' + query + '".</p>';
    }

    function renderResults(products) {
        results.innerHTML = '';
        products.forEach((item) => {
            const row = document.createElement('a');
            row.href = item.url;
            row.className = 'flex items-center justify-between gap-4 px-6 py-4 border-b border-[var(--brown-500)]/10 hover:bg-[var(--cream-deep)]';
            row.innerHTML =
                '<span class="flex items-center gap-4">' +
                    (item.image ? '<img src="' + item.image + '" alt="" class="w-10 h-10 object-cover flex-shrink-0">' : '') +
                    '<span class="text-sm text-[var(--brown-900)]">' + item.title + '</span>' +
                '</span>' +
                '<span class="text-sm text-[var(--brown-500)] flex-shrink-0">' + item.price + '</span>';
            row.addEventListener('click', () => overlay && overlay.classList.remove('open'));
            results.appendChild(row);
        });
    }

    input.addEventListener('input', () => {
        const query = input.value.trim();
        clearTimeout(debounceTimer);
        if (query.length < 2) {
            results.innerHTML = '';
            return;
        }
        debounceTimer = setTimeout(async () => {
            if (activeController) activeController.abort();
            activeController = new AbortController();
            try {
                const url = routes.predictiveSearch + '?q=' + encodeURIComponent(query) +
                    '&resources[type]=product&resources[limit]=8&resources[options][unavailable_products]=last';
                const res = await fetch(url, { signal: activeController.signal, headers: { Accept: 'application/json' } });
                const data = await res.json();
                const products = (data.resources && data.resources.results && data.resources.results.products) || [];
                if (products.length === 0) { renderEmpty(input.value); return; }
                renderResults(products);
            } catch (err) {
                if (err.name !== 'AbortError') renderEmpty(input.value);
            }
        }, 220);
    });
})();
