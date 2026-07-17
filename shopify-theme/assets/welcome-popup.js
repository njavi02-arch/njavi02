/*
 * Popup de bienvenida + barra de countdown. El nombre/email se guardan
 * localmente y también se envían al formulario real de newsletter de
 * Shopify (ver snippets/welcome-popup.liquid). El código de descuento y
 * los minutos del countdown vienen de Theme settings — el código debe
 * existir de verdad en Shopify (Descuentos) para que el enlace funcione.
 */
(function () {
    const backdrop = document.getElementById('welcome-backdrop');
    if (!backdrop) return;
    try {
        const WELCOME_SHOWN_KEY = 'vdt-welcome-shown';
        const DEADLINE_KEY = 'vdt-discount-deadline';
        const countdownMinutes = parseInt(backdrop.dataset.countdownMinutes, 10) || 30;
        const COUNTDOWN_MS = countdownMinutes * 60 * 1000;

        const closeBtn = document.getElementById('welcome-close');
        const form = document.getElementById('welcome-form');
        const formView = document.getElementById('welcome-form-view');
        const confirmView = document.getElementById('welcome-confirmation-view');
        const nameDisplay = document.getElementById('welcome-name-display');
        const continueBtn = document.getElementById('welcome-continue');

        function closePopup() {
            backdrop.classList.remove('open');
            try { localStorage.setItem(WELCOME_SHOWN_KEY, 'true'); } catch (e) {}
        }

        let alreadyShown = false;
        try { alreadyShown = localStorage.getItem(WELCOME_SHOWN_KEY) === 'true'; } catch (e) {}

        if (!alreadyShown) {
            setTimeout(() => backdrop.classList.add('open'), 1800);
        }

        if (closeBtn) closeBtn.addEventListener('click', closePopup);
        backdrop.addEventListener('click', (e) => { if (e.target === backdrop) closePopup(); });
        if (continueBtn) continueBtn.addEventListener('click', closePopup);

        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const name = document.getElementById('welcome-name').value.trim() || 'cliente VDT';
                try {
                    await fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } });
                } catch (err) { /* el signup real ya quedó registrado del lado de Shopify si el fetch falla por CORS del navegador */ }
                try {
                    localStorage.setItem(WELCOME_SHOWN_KEY, 'true');
                    if (!localStorage.getItem(DEADLINE_KEY)) {
                        localStorage.setItem(DEADLINE_KEY, String(Date.now() + COUNTDOWN_MS));
                    }
                } catch (err) {}
                if (nameDisplay) nameDisplay.textContent = name;
                if (formView) formView.classList.add('hidden');
                if (confirmView) confirmView.classList.remove('hidden');
                startCountdown();
            });
        }

        function startCountdown() {
            const bar = document.getElementById('discount-countdown');
            const timerLabel = document.getElementById('discount-countdown-timer');
            const textLabel = document.getElementById('discount-countdown-text');
            if (!bar) return;
            let deadline;
            try { deadline = parseInt(localStorage.getItem(DEADLINE_KEY), 10); } catch (e) { return; }
            if (!deadline) return;

            bar.classList.remove('hidden');
            setTimeout(() => bar.classList.add('show'), 50);

            const tick = () => {
                const remaining = deadline - Date.now();
                if (remaining <= 0) {
                    clearInterval(intervalId);
                    if (textLabel) textLabel.textContent = 'Tu descuento de bienvenida ya no está reservado';
                    if (timerLabel) timerLabel.textContent = 'Escribinos y te ayudamos';
                    try { localStorage.removeItem(DEADLINE_KEY); } catch (e) {}
                    setTimeout(() => bar.classList.remove('show'), 8000);
                    return;
                }
                const totalSeconds = Math.floor(remaining / 1000);
                const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
                const seconds = String(totalSeconds % 60).padStart(2, '0');
                if (timerLabel) timerLabel.textContent = minutes + ':' + seconds;
            };
            tick();
            const intervalId = setInterval(tick, 1000);
        }

        try {
            if (localStorage.getItem(DEADLINE_KEY)) startCountdown();
        } catch (e) {}
    } catch (err) {
        console.error('Popup de bienvenida no disponible.', err);
    }
})();
