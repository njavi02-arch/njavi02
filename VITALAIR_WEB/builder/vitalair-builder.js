/* VitalAir builder: elige inhaladores + sabores (o solo sabores) y añade al carrito.
   Lee la configuración de <script type="application/json" id="va-config"> y se monta en #va-builder. */
(function () {
  'use strict';
  var root = document.getElementById('va-builder');
  var cfgEl = document.getElementById('va-config');
  if (!root || !cfgEl) return;
  var cfg;
  try { cfg = JSON.parse(cfgEl.textContent); } catch (e) { return; }

  var PER = cfg.perInhaler || 3;
  var MAX_ONLY = cfg.maxOnly || 30;
  var fmt = new Intl.NumberFormat(cfg.locale || 'es-ES', { style: 'currency', currency: cfg.currency || 'EUR' });
  function money(c) { return fmt.format(c / 100); }

  var packs = cfg.packs.slice().sort(function (a, b) { return a.n - b.n; });
  var flavors = cfg.flavors;
  var base = packs.length ? packs[0].price / packs[0].n : 0;

  var state = { mode: 'kit', n: packs.length ? packs[0].n : 1, counts: {}, order: [], busy: false };
  flavors.forEach(function (f) { state.counts[f.name] = 0; });

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function total() { var t = 0; for (var k in state.counts) t += state.counts[k]; return t; }
  function maxNow() { return state.mode === 'kit' ? state.n * PER : MAX_ONLY; }
  function pack() { return packs.filter(function (p) { return p.n === state.n; })[0]; }

  /* ---------- estructura ---------- */
  root.innerHTML = '';
  var ui = {};
  root.classList.add('vb');

  if (cfg.only) {
    ui.mode = el('div', 'vb-mode');
    ui.mode.setAttribute('role', 'tablist');
    ui.modeKit = el('button', 'vb-mode-btn', '<strong>Inhalador + sabores</strong><span>Combina los sabores como quieras</span>');
    ui.modeOnly = el('button', 'vb-mode-btn', '<strong>Solo sabores</strong><span>Sin inhalador</span>');
    [ui.modeKit, ui.modeOnly].forEach(function (b) { b.type = 'button'; b.setAttribute('role', 'tab'); ui.mode.appendChild(b); });
    root.appendChild(ui.mode);
    ui.modeKit.addEventListener('click', function () { setMode('kit'); });
    ui.modeOnly.addEventListener('click', function () { setMode('only'); });
  }

  ui.kitBox = el('div', 'vb-kit');
  ui.kitBox.appendChild(el('h3', 'vb-h', '<span>1</span>¿Cuántos inhaladores?'));
  ui.packs = el('div', 'vb-packs');
  ui.packs.setAttribute('role', 'group');
  ui.packs.setAttribute('aria-label', 'Número de inhaladores');
  packs.forEach(function (p) {
    var b = el('button', 'vb-pack');
    b.type = 'button';
    b.dataset.n = p.n;
    var save = p.compare && p.compare > p.price ? '<em>−' + Math.floor((p.compare - p.price) * 100 / p.compare) + ' %</em>' : '';
    b.innerHTML = '<b>' + p.n + '</b><span>' + money(p.price) + '</span>' + save;
    b.setAttribute('aria-label', p.n + (p.n > 1 ? ' inhaladores' : ' inhalador') + ', ' + money(p.price));
    if (!p.available) { b.disabled = true; b.classList.add('is-off'); }
    b.addEventListener('click', function () { setPacks(p.n); });
    ui.packs.appendChild(b);
  });
  ui.kitBox.appendChild(ui.packs);
  ui.cap = el('p', 'vb-cap');
  ui.cap.setAttribute('aria-live', 'polite');
  ui.kitBox.appendChild(ui.cap);
  root.appendChild(ui.kitBox);

  ui.flHead = el('h3', 'vb-h');
  root.appendChild(ui.flHead);

  ui.list = el('div', 'vb-list');
  if (cfg.sprite) ui.list.style.setProperty('--sp', "url('" + cfg.sprite + "')");
  var rows = {};
  flavors.forEach(function (f) {
    var r = el('div', 'vb-row');
    r.dataset.f = f.name;
    r.innerHTML =
      '<i class="va-sp" data-f="' + esc(f.name) + '" aria-hidden="true"></i>' +
      '<div class="vb-name"><strong>' + esc(f.name) + '</strong><span>' + esc(f.desc || '') + '</span></div>' +
      '<div class="vb-step"><button type="button" class="vb-minus" aria-label="Quitar ' + esc(f.name) + '">−</button>' +
      '<output class="vb-n" aria-live="polite">0</output>' +
      '<button type="button" class="vb-plus" aria-label="Añadir ' + esc(f.name) + '">+</button></div>';
    r.querySelector('.vb-minus').addEventListener('click', function () { change(f.name, -1); });
    r.querySelector('.vb-plus').addEventListener('click', function () { change(f.name, +1); });
    rows[f.name] = { row: r, n: r.querySelector('.vb-n'), minus: r.querySelector('.vb-minus'), plus: r.querySelector('.vb-plus') };
    ui.list.appendChild(r);
  });
  root.appendChild(ui.list);

  ui.note = el('p', 'vb-toast');
  ui.note.setAttribute('role', 'status');
  root.appendChild(ui.note);

  ui.bar = el('div', 'vb-bar');
  ui.barInfo = el('div', 'vb-info');
  ui.barCount = el('div', 'vb-count');
  ui.barTrack = el('div', 'vb-track', '<i></i>');
  ui.barSum = el('div', 'vb-sum');
  ui.barPrice = el('div', 'vb-price');
  ui.barInfo.appendChild(ui.barCount);
  ui.barInfo.appendChild(ui.barTrack);
  ui.barInfo.appendChild(ui.barSum);
  ui.cta = el('button', 'vb-cta');
  ui.cta.type = 'button';
  ui.hint = el('p', 'vb-hint');
  ui.hint.setAttribute('aria-live', 'polite');
  ui.barInfo.appendChild(ui.hint);
  ui.bar.appendChild(ui.barInfo);
  var right = el('div', 'vb-right');
  right.appendChild(ui.barPrice);
  right.appendChild(ui.cta);
  ui.bar.appendChild(right);
  root.appendChild(ui.bar);

  ui.cta.addEventListener('click', addToCart);

  /* ---------- lógica ---------- */
  function setMode(m) {
    if (m === state.mode) return;
    state.mode = m;
    state.counts = {}; state.order = [];
    flavors.forEach(function (f) { state.counts[f.name] = 0; });
    ui.note.textContent = '';
    render();
  }

  function setPacks(n) {
    state.n = n;
    var max = maxNow(), t = total();
    if (t > max) {
      var removed = t - max;
      while (total() > max && state.order.length) {
        var last = state.order.pop();
        if (state.counts[last] > 0) state.counts[last]--;
      }
      ui.note.textContent = 'Hemos ajustado tu selección a ' + max + ' sabores (' + (removed === 1 ? 'se ha quitado 1' : 'se han quitado ' + removed) + ').';
    } else {
      ui.note.textContent = '';
    }
    render();
  }

  function change(name, d) {
    var c = state.counts[name];
    if (d > 0) {
      if (total() >= maxNow()) return; /* la interfaz impide pasarse del límite */
      state.counts[name] = c + 1;
      state.order.push(name);
    } else {
      if (c <= 0) return;
      state.counts[name] = c - 1;
      var i = state.order.lastIndexOf(name);
      if (i > -1) state.order.splice(i, 1);
    }
    ui.note.textContent = '';
    render();
  }

  function summary() {
    return flavors.filter(function (f) { return state.counts[f.name] > 0; })
      .map(function (f) { return f.name + ' ×' + state.counts[f.name]; }).join(', ');
  }

  function onlyTotal() { return total() * (cfg.only ? cfg.only.price : 0); }

  function render() {
    var t = total(), max = maxNow(), kit = state.mode === 'kit';
    root.dataset.mode = state.mode;
    if (cfg.only) {
      ui.modeKit.setAttribute('aria-selected', kit);
      ui.modeOnly.setAttribute('aria-selected', !kit);
      ui.modeKit.classList.toggle('is-on', kit);
      ui.modeOnly.classList.toggle('is-on', !kit);
    }
    ui.kitBox.hidden = !kit;
    ui.packs.querySelectorAll('.vb-pack').forEach(function (b) {
      var on = +b.dataset.n === state.n;
      b.classList.toggle('is-on', on);
      b.setAttribute('aria-pressed', on);
    });
    var p = pack();
    if (kit) {
      ui.cap.innerHTML = '<b>' + state.n + (state.n > 1 ? ' inhaladores' : ' inhalador') + '</b> · hasta <b>' + max + ' sabores</b>';
      ui.flHead.innerHTML = '<span>2</span>Elige tus sabores';
    } else {
      ui.flHead.innerHTML = '<span>1</span>Elige tus sabores';
    }
    flavors.forEach(function (f) {
      var r = rows[f.name], c = state.counts[f.name];
      r.n.textContent = c;
      r.row.classList.toggle('is-on', c > 0);
      r.minus.disabled = c === 0;
      r.plus.disabled = t >= max;
    });
    ui.list.classList.toggle('is-full', t >= max);

    var pct = max ? Math.min(100, Math.round(t * 100 / max)) : 0;
    if (kit) {
      ui.barCount.innerHTML = 'Sabores <b>' + t + ' / ' + max + '</b>';
      ui.barTrack.hidden = false;
      ui.barTrack.firstChild.style.width = pct + '%';
      ui.barSum.textContent = state.n + (state.n > 1 ? ' inhaladores' : ' inhalador');
      var price = p ? p.price : 0;
      ui.barPrice.innerHTML = (p && p.compare && p.compare > p.price ? '<s>' + money(p.compare) + '</s>' : '') + '<b>' + money(price) + '</b>';
    } else {
      ui.barCount.innerHTML = 'Sabores <b>' + t + '</b>';
      ui.barTrack.hidden = true;
      ui.barSum.textContent = t ? t + (t > 1 ? ' sobres' : ' sobre') + ' · ' + money(cfg.only.price) + ' cada uno' : 'Sin inhalador';
      ui.barPrice.innerHTML = '<b>' + money(onlyTotal()) + '</b>';
    }

    var msg = '', ok = t > 0 && !state.busy;
    if (t === 0) msg = 'Elige al menos un sabor para continuar.';
    else if (kit && t < max) msg = 'Puedes elegir ' + (max - t) + (max - t === 1 ? ' sabor más' : ' sabores más') + '. Es opcional.';
    else if (kit) msg = 'Selección completa.';
    ui.hint.textContent = msg;
    ui.hint.classList.toggle('is-warn', t === 0);
    if (kit) {
      var free = p && p.price >= (cfg.freeShipFrom || 5500);
      ui.hint.dataset.ship = free ? '1' : '';
    }
    ui.cta.disabled = !ok;
    ui.cta.textContent = state.busy ? 'Añadiendo…' : (t === 0 ? 'Elige un sabor' : 'Añadir al carrito');
    if (kit && p && !p.available) { ui.cta.disabled = true; ui.cta.textContent = 'Agotado'; }
  }

  function uid() { return 'b' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6); }

  function buildItems() {
    if (state.mode === 'kit') {
      var p = pack();
      return [{ id: p.id, quantity: 1, properties: { 'Sabores': summary(), 'Nº de sabores': String(total()), '_bundle': uid() } }];
    }
    return flavors.filter(function (f) { return state.counts[f.name] > 0; })
      .map(function (f) { return { id: cfg.only.variants[f.name], quantity: state.counts[f.name] }; });
  }

  function addToCart() {
    if (total() === 0 || state.busy) return;
    var items = buildItems();
    state.busy = true; render();
    fetch(cfg.addUrl || '/cart/add.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ items: items })
    }).then(function (r) {
      if (!r.ok) throw new Error('add failed');
      return r.json();
    }).then(function () {
      window.location.assign(cfg.cartUrl || '/cart');
    }).catch(function () {
      state.busy = false; render();
      ui.note.textContent = 'No hemos podido añadirlo al carrito. Inténtalo de nuevo.';
    });
  }

  /* ---------- preselección por URL (?variant=ID&flavor=Nombre) ---------- */
  try {
    var q = new URLSearchParams(location.search);
    var v = q.get('variant'), fl = q.get('flavor');
    if (v) { var pp = packs.filter(function (x) { return String(x.id) === v; })[0]; if (pp) state.n = pp.n; }
    if (fl && state.counts.hasOwnProperty(fl)) { state.counts[fl] = 1; state.order.push(fl); }
  } catch (e) {}

  render();

  /* API mínima para pruebas */
  root.vbState = state;
})();
