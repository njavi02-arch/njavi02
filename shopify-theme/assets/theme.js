/*
 * Interacciones globales del theme: intro, animaciones GSAP, header al
 * hacer scroll, menú móvil, paneles laterales, cursor premium, tilt de
 * tarjetas y filtros por categoría (reutilizado en home y colección).
 */
(function () {
    const overlay = document.getElementById('intro-overlay');
    const site = document.getElementById('site');

    /* ===================== Intro en video ===================== */
    if (overlay && site) {
        const skipBtn = document.getElementById('intro-skip');
        const introVideo = document.getElementById('intro-video');

        let revealed = false;
        function showSiteNow() {
            if (revealed) return;
            revealed = true;
            clearTimeout(safetyTimer);
            try { sessionStorage.setItem('vdt-intro-seen', 'true'); } catch (e) {}
            overlay.style.transition = 'opacity 0.6s ease';
            overlay.style.opacity = '0';
            setTimeout(() => { overlay.style.display = 'none'; }, 650);
            site.style.transition = 'opacity 0.8s ease';
            site.style.opacity = '1';
            document.querySelectorAll('.reveal').forEach((el) => {
                el.style.opacity = '1';
                el.style.transform = 'none';
            });
        }
        window.VDT = window.VDT || {};
        window.VDT.showSiteNow = showSiteNow;

        if (skipBtn) skipBtn.addEventListener('click', showSiteNow);
        let safetyTimer = setTimeout(showSiteNow, 15000);

        let alreadySeen = false;
        try { alreadySeen = sessionStorage.getItem('vdt-intro-seen') === 'true'; } catch (e) {}

        if (alreadySeen) {
            clearTimeout(safetyTimer);
            overlay.style.display = 'none';
            site.style.opacity = '1';
            document.querySelectorAll('.reveal').forEach((el) => { el.style.opacity = '1'; el.style.transform = 'none'; });
        } else if (introVideo) {
            introVideo.addEventListener('loadedmetadata', () => {
                if (introVideo.duration && isFinite(introVideo.duration)) {
                    clearTimeout(safetyTimer);
                    safetyTimer = setTimeout(showSiteNow, (introVideo.duration * 1000) + 1500);
                }
            });
            introVideo.addEventListener('ended', showSiteNow);
            introVideo.addEventListener('error', showSiteNow);
            introVideo.play().catch(() => showSiteNow());
        } else {
            showSiteNow();
        }
    } else if (site) {
        site.style.opacity = '1';
    }

    /* ===================== Animaciones de entrada y scroll ===================== */
    try {
        gsap.registerPlugin(ScrollTrigger);
        gsap.from('#logo-mark', { opacity: 0, y: -8, duration: 0.8, delay: 0.2, ease: 'power2.out' });
        gsap.utils.toArray('.reveal').forEach((el) => {
            gsap.fromTo(el,
                { opacity: 0, y: 32 },
                { opacity: 1, y: 0, duration: 1, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 85%' } }
            );
        });
        gsap.to('#hero-parallax', {
            y: 120, ease: 'none',
            scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: true }
        });
    } catch (err) {
        console.error('Animaciones no disponibles, el contenido queda visible sin animar.', err);
    }

    /* ===================== Header: transparente sobre el hero, sólido al hacer scroll ===================== */
    (function headerScrollState() {
        const header = document.getElementById('main-header');
        if (!header) return;
        const heroSection = document.getElementById('hero');
        function update() {
            const threshold = heroSection ? heroSection.offsetHeight - 120 : 400;
            header.classList.toggle('header-solid', window.scrollY > threshold);
        }
        window.addEventListener('scroll', update, { passive: true });
        update();
    })();

    /* ===================== Menú móvil ===================== */
    const menuToggle = document.getElementById('menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', () => {
            const isOpen = !mobileMenu.classList.contains('hidden');
            mobileMenu.classList.toggle('hidden');
            mobileMenu.classList.toggle('flex');
            menuToggle.setAttribute('aria-expanded', String(!isOpen));
        });
    }

    /* ===================== Filtros por categoría (home + colección) ===================== */
    function initFilterGroup(bar) {
        const gridSelector = bar.dataset.filterBar;
        const grid = document.querySelector(gridSelector);
        if (!grid) return;
        const noResults = grid.parentElement.querySelector('[data-no-results]');
        function applyFilter(filter) {
            let visibleCount = 0;
            grid.querySelectorAll('[data-category]').forEach((card) => {
                const match = filter === 'todos' || card.dataset.category === filter;
                card.style.display = match ? '' : 'none';
                if (match) visibleCount++;
            });
            if (noResults) noResults.classList.toggle('hidden', visibleCount > 0);
        }
        bar.querySelectorAll('.filter-pill').forEach((pill) => {
            pill.addEventListener('click', () => {
                bar.querySelectorAll('.filter-pill').forEach((p) => p.removeAttribute('data-active'));
                pill.setAttribute('data-active', 'true');
                applyFilter(pill.dataset.filter);
            });
        });
        const preset = bar.querySelector('.filter-pill[data-active="true"]');
        applyFilter(preset ? preset.dataset.filter : 'todos');
    }
    document.querySelectorAll('[data-filter-bar]').forEach(initFilterGroup);

    document.querySelectorAll('[data-filter-link]').forEach((link) => {
        link.addEventListener('click', () => {
            const bar = document.querySelector('[data-filter-bar]');
            if (!bar) return;
            const target = bar.querySelector('[data-filter="' + link.dataset.filterLink + '"]');
            if (target) setTimeout(() => target.click(), 400);
        });
    });

    /* ===================== Paneles laterales ===================== */
    const backdrop = document.getElementById('panel-backdrop');
    function openPanel(id) {
        document.querySelectorAll('.side-panel').forEach((p) => p.classList.remove('open'));
        const panel = document.getElementById(id);
        if (panel) panel.classList.add('open');
        if (backdrop) backdrop.classList.add('open');
    }
    function closeAllPanels() {
        document.querySelectorAll('.side-panel').forEach((p) => p.classList.remove('open'));
        if (backdrop) backdrop.classList.remove('open');
    }
    window.VDT = window.VDT || {};
    window.VDT.ui = { openPanel, closeAllPanels };

    const cartToggle = document.getElementById('cart-toggle');
    const favoritesToggle = document.getElementById('favorites-toggle');
    const accountToggle = document.getElementById('account-toggle');
    if (cartToggle) cartToggle.addEventListener('click', () => openPanel('cart-panel'));
    if (favoritesToggle) favoritesToggle.addEventListener('click', () => openPanel('favorites-panel'));
    if (accountToggle) accountToggle.addEventListener('click', () => openPanel('account-panel'));
    if (backdrop) backdrop.addEventListener('click', closeAllPanels);
    document.querySelectorAll('.panel-close').forEach((btn) => btn.addEventListener('click', closeAllPanels));

    /* ===================== Búsqueda: apertura/cierre del overlay ===================== */
    const searchToggle = document.getElementById('search-toggle');
    const searchOverlay = document.getElementById('search-overlay');
    const searchInput = document.getElementById('search-input');
    const searchClose = document.getElementById('search-close');
    if (searchToggle && searchOverlay) {
        searchToggle.addEventListener('click', () => {
            searchOverlay.classList.add('open');
            if (searchInput) { searchInput.value = ''; setTimeout(() => searchInput.focus(), 100); }
            const results = document.getElementById('search-results');
            if (results) results.innerHTML = '';
        });
        if (searchClose) searchClose.addEventListener('click', () => searchOverlay.classList.remove('open'));
        searchOverlay.addEventListener('click', (e) => { if (e.target === searchOverlay) searchOverlay.classList.remove('open'); });
    }

    /* ===================== Cursor premium + tilt de tarjetas (solo puntero fino) ===================== */
    (function initPremiumInteractions() {
        try {
            if (!window.matchMedia('(pointer: fine)').matches) return;
            const cursor = document.getElementById('custom-cursor');
            const cursorText = document.getElementById('custom-cursor-text');
            if (!cursor) return;
            document.body.classList.add('custom-cursor-active');

            let mouseX = window.innerWidth / 2, mouseY = window.innerHeight / 2, curX = mouseX, curY = mouseY;
            window.addEventListener('mousemove', (e) => { mouseX = e.clientX; mouseY = e.clientY; });
            (function loop() {
                curX += (mouseX - curX) * 0.2;
                curY += (mouseY - curY) * 0.2;
                cursor.style.left = curX + 'px';
                cursor.style.top = curY + 'px';
                requestAnimationFrame(loop);
            })();

            function setCursorState(el, text, gold) {
                el.addEventListener('mouseenter', () => {
                    cursor.classList.add('cursor-grow');
                    if (gold) cursor.classList.add('cursor-gold');
                    cursorText.textContent = text;
                });
                el.addEventListener('mouseleave', () => {
                    cursor.classList.remove('cursor-grow', 'cursor-gold');
                    cursorText.textContent = '';
                });
            }

            document.querySelectorAll('.product-card').forEach((card) => setCursorState(card, 'VER PRODUCTO', false));
            document.querySelectorAll('.add-cart-btn, [data-add-to-cart], [data-add-to-cart-simple]').forEach((btn) => setCursorState(btn, 'AÑADIR', true));
            const checkoutBtn = document.getElementById('checkout-btn');
            if (checkoutBtn) setCursorState(checkoutBtn, 'COMPRAR', true);
            document.querySelectorAll('.category-tile').forEach((tile) => setCursorState(tile, 'EXPLORAR', false));

            document.querySelectorAll('.product-card').forEach((card) => {
                card.addEventListener('mousemove', (e) => {
                    const rect = card.getBoundingClientRect();
                    const x = (e.clientX - rect.left) / rect.width - 0.5;
                    const y = (e.clientY - rect.top) / rect.height - 0.5;
                    card.style.transform = 'perspective(900px) rotateY(' + (x * 5) + 'deg) rotateX(' + (-y * 5) + 'deg) translateY(-4px)';
                });
                card.addEventListener('mouseleave', () => { card.style.transform = ''; });
            });
        } catch (err) {
            console.error('Interacciones premium no disponibles.', err);
        }
    })();

    /* ===================== Newsletter: envío real por fetch, sin recargar ===================== */
    document.querySelectorAll('[data-newsletter-form]').forEach((form) => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = document.getElementById(form.dataset.messageTarget);
            try {
                const res = await fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } });
                if (!res.ok) throw new Error('request-failed');
                form.reset();
                if (message) message.classList.remove('hidden');
            } catch (err) {
                form.submit();
            }
        });
    });
})();
