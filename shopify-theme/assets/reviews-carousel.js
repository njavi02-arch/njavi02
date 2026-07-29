/*
 * Carrusel de reseñas: misma UX del prototipo (autoplay, mantener pulsado,
 * swipe), ahora leyendo los datos desde los bloques editables de la
 * sección (Theme Editor) en vez de un array fijo en JS.
 */
(function () {
    document.querySelectorAll('[data-reviews-section]').forEach((section) => {
        try {
            const dataEl = section.querySelector('[data-reviews-json]');
            const track = section.querySelector('.reviews-track');
            const viewport = section.querySelector('.reviews-viewport');
            const dotsBox = section.querySelector('[data-reviews-dots]');
            const holdBtn = section.querySelector('[data-reviews-hold]');
            const avgLabel = section.querySelector('[data-reviews-average]');
            if (!dataEl || !track) return;
            const reviews = JSON.parse(dataEl.textContent);
            if (reviews.length === 0) return;

            const avatarColors = ['var(--brown-700)', 'var(--matcha-700)', 'var(--gold)', 'var(--brown-500)', 'var(--matcha-500)'];
            const dateFormatter = new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short', year: 'numeric' });

            track.innerHTML = reviews.map((r, i) => {
                const stars = '★'.repeat(r.rating) + '☆'.repeat(5 - r.rating);
                let dateLabel = '';
                try { dateLabel = dateFormatter.format(new Date(r.date)); } catch (e) {}
                return (
                    '<div class="review-card">' +
                        '<div class="text-[var(--gold)] mb-5 text-lg">' + stars + '</div>' +
                        '<p class="text-[var(--brown-700)] mb-8 leading-relaxed font-light italic">&ldquo;' + r.text + '&rdquo;</p>' +
                        '<div class="flex items-center gap-3">' +
                            '<div class="review-avatar" style="background:' + avatarColors[i % avatarColors.length] + '">' + r.initials + '</div>' +
                            '<div>' +
                                '<p class="text-sm text-[var(--brown-900)]">' + r.name + '</p>' +
                                '<p class="text-xs text-[var(--brown-500)]">' + dateLabel + '</p>' +
                            '</div>' +
                        '</div>' +
                    '</div>'
                );
            }).join('');

            if (avgLabel) {
                const avg = reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length;
                avgLabel.textContent = avg.toFixed(1) + ' ★ · basado en ' + reviews.length + ' reseñas';
            }

            if (dotsBox) dotsBox.innerHTML = reviews.map(() => '<span class="review-dot"></span>').join('');
            const dots = dotsBox ? [...dotsBox.children] : [];

            let currentIndex = 0;
            function cardStep() {
                const card = track.children[0];
                if (!card) return 0;
                const style = getComputedStyle(track);
                const gap = parseFloat(style.columnGap || style.gap || '0');
                return card.getBoundingClientRect().width + gap;
            }
            function goTo(index) {
                currentIndex = ((index % reviews.length) + reviews.length) % reviews.length;
                track.style.transform = 'translateX(-' + (currentIndex * cardStep()) + 'px)';
                dots.forEach((d, i) => d.classList.toggle('active', i === currentIndex));
            }
            goTo(0);
            window.addEventListener('resize', () => goTo(currentIndex));

            let autoplayTimer = null;
            function startAutoplay() {
                stopAutoplay();
                autoplayTimer = setInterval(() => goTo(currentIndex + 1), 4500);
            }
            function stopAutoplay() {
                if (autoplayTimer) clearInterval(autoplayTimer);
                autoplayTimer = null;
            }
            startAutoplay();
            if (viewport) {
                viewport.addEventListener('mouseenter', stopAutoplay);
                viewport.addEventListener('mouseleave', startAutoplay);
            }

            if (holdBtn) {
                let holdTimer = null;
                function pressStart() {
                    stopAutoplay();
                    holdBtn.classList.add('pressed');
                    holdTimer = setInterval(() => goTo(currentIndex + 1), 420);
                }
                function pressEnd() {
                    if (holdTimer) clearInterval(holdTimer);
                    holdTimer = null;
                    holdBtn.classList.remove('pressed');
                    startAutoplay();
                }
                holdBtn.addEventListener('mousedown', pressStart);
                holdBtn.addEventListener('touchstart', (e) => { e.preventDefault(); pressStart(); }, { passive: false });
                window.addEventListener('mouseup', pressEnd);
                window.addEventListener('touchend', pressEnd);
                holdBtn.addEventListener('mouseleave', () => { if (holdTimer) pressEnd(); });
            }

            let touchStartX = null;
            if (viewport) {
                viewport.addEventListener('touchstart', (e) => { touchStartX = e.touches[0].clientX; stopAutoplay(); }, { passive: true });
                viewport.addEventListener('touchend', (e) => {
                    if (touchStartX === null) return;
                    const dx = e.changedTouches[0].clientX - touchStartX;
                    if (Math.abs(dx) > 40) goTo(currentIndex + (dx < 0 ? 1 : -1));
                    touchStartX = null;
                    startAutoplay();
                });
            }
        } catch (err) {
            console.error('Carrusel de reseñas no disponible.', err);
        }
    });
})();
