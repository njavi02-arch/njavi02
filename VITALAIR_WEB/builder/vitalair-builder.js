/* VitalAir builder v4: inhalador(es) como producto base + sabores como extras con precio.
   Lee la configuración de <script type="application/json" id="va-config"> y se monta en #va-builder.
   Cada sabor es una variante real de Shopify (inventario propio) y entra al carrito como línea propia. */
(function () {
  'use strict';
  var root = document.getElementById('va-builder');
  var cfgEl = document.getElementById('va-config');
  if (!root || !cfgEl) return;
  var cfg;
  try { cfg = JSON.parse(cfgEl.textContent); } catch (e) { return; }

  var PCT = +cfg.discountPct || 0;
  var BULK = cfg.bulk && cfg.bulk.min > 0 && cfg.bulk.pct > 0 ? cfg.bulk : null; /* % extra en sabores al llevar N o más */
  var ONLY_MIN = +cfg.onlyMin || 0; /* mínimo de sabores al comprar sin inhalador */
  var MAX_LINE = 99;
  var fmt = new Intl.NumberFormat(cfg.locale || 'es-ES', { style: 'currency', currency: cfg.currency || 'EUR' });
  function money(c) { return fmt.format(c / 100); }
  function disc(c) { return PCT ? Math.round(c * PCT / 100) : 0; }

  var packs = cfg.packs.slice().sort(function (a, b) { return a.n - b.n; });
  /* un sabor solo se vende si tiene variante, precio real (> 0) y stock */
  var flavors = (cfg.flavors || []).filter(function (f) { return f.id && f.price > 0; });
  flavors.forEach(function (f) { f.cap = Math.max(0, Math.min(f.stock == null ? MAX_LINE : f.stock, MAX_LINE)); if (f.available === false) f.cap = 0; });
  var hasExtras = flavors.length > 0;

  var state = { mode: 'kit', n: packs.length ? packs[0].n : 1, counts: {}, busy: false };
  flavors.forEach(function (f) { state.counts[f.name] = 0; });

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function total() { var t = 0; for (var k in state.counts) t += state.counts[k]; return t; }
  function pack() { return packs.filter(function (p) { return p.n === state.n; })[0]; }
  function chosen() { return flavors.filter(function (f) { return state.counts[f.name] > 0; }); }

  /* lines: [{label, qty, unit, amount}] */
  function lines() {
    var out = [];
    if (state.mode === 'kit') {
      var p = pack();
      if (p) out.push({ kind: 'pack', label: state.n + (state.n > 1 ? ' inhaladores' : ' inhalador'), amount: p.price, compare: p.compare });
    }
    chosen().forEach(function (f) { var q = state.counts[f.name]; out.push({ kind: 'flavor', label: f.name, qty: q, unit: f.price, amount: f.price * q }); });
    return out;
  }
  /* El descuento web se calcula sobre cada línea; el extra de sabores se aplica después, sobre el precio ya rebajado. */
  function totals() {
    var sub = 0, d = 0, d2 = 0, bulkOn = !!BULK && total() >= BULK.min;
    lines().forEach(function (l) {
      sub += l.amount;
      var a = disc(l.amount);
      d += a;
      if (bulkOn && l.kind === 'flavor') d2 += Math.round((l.amount - a) * BULK.pct / 100);
    });
    return { sub: sub, disc: d, bulk: d2, bulkOn: bulkOn, total: sub - d - d2 };
  }

  /* ---------- estructura ---------- */
  root.innerHTML = '';
  var ui = {};
  root.classList.add('vb');

  if (hasExtras) {
    ui.mode = el('div', 'vb-mode');
    ui.mode.setAttribute('role', 'tablist');
    ui.modeKit = el('button', 'vb-mode-btn', '<strong>Inhalador + sabores</strong><span>Tu inhalador y los sabores que quieras</span>');
    ui.modeOnly = el('button', 'vb-mode-btn', '<strong>Solo sabores</strong><span>Sin inhalador</span>');
    [ui.modeKit, ui.modeOnly].forEach(function (b) { b.type = 'button'; b.setAttribute('role', 'tab'); ui.mode.appendChild(b); });
    root.appendChild(ui.mode);
    ui.modeKit.addEventListener('click', function () { setMode('kit'); });
    ui.modeOnly.addEventListener('click', function () { setMode('only'); });
  }

  ui.kitBox = el('div', 'vb-kit');
  ui.kitBox.appendChild(el('h3', 'vb-h', '<span>1</span>Elige tu inhalador'));
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
    b.addEventListener('click', function () { state.n = p.n; render(); });
    ui.packs.appendChild(b);
  });
  ui.kitBox.appendChild(ui.packs);
  ui.cap = el('p', 'vb-cap');
  ui.cap.setAttribute('aria-live', 'polite');
  ui.kitBox.appendChild(ui.cap);
  root.appendChild(ui.kitBox);

  var rows = {};
  if (hasExtras) {
    ui.flHead = el('h3', 'vb-h');
    root.appendChild(ui.flHead);
    ui.list = el('div', 'vb-list');
    if (cfg.sprite) ui.list.style.setProperty('--sp', "url('" + cfg.sprite + "')");
    flavors.forEach(function (f) {
      var r = el('div', 'vb-row');
      r.dataset.f = f.name;
      r.innerHTML =
        '<i class="va-sp" data-f="' + esc(f.name) + '" aria-hidden="true"></i>' +
        '<div class="vb-name"><strong>' + esc(f.name) + '</strong><span>' + esc(f.desc || '') + '</span></div>' +
        '<div class="vb-side"><span class="vb-extra">+' + money(f.price) + '</span>' +
        '<div class="vb-step"><button type="button" class="vb-minus" aria-label="Quitar ' + esc(f.name) + '">−</button>' +
        '<output class="vb-n" aria-live="polite">0</output>' +
        '<button type="button" class="vb-plus" aria-label="Añadir ' + esc(f.name) + ' (+' + money(f.price) + ')">+</button></div></div>';
      r.querySelector('.vb-minus').addEventListener('click', function () { change(f, -1); });
      r.querySelector('.vb-plus').addEventListener('click', function () { change(f, +1); });
      rows[f.name] = { row: r, n: r.querySelector('.vb-n'), minus: r.querySelector('.vb-minus'), plus: r.querySelector('.vb-plus'), extra: r.querySelector('.vb-extra') };
      ui.list.appendChild(r);
    });
    root.appendChild(ui.list);
  }

  ui.note = el('p', 'vb-toast');
  ui.note.setAttribute('role', 'status');
  root.appendChild(ui.note);

  ui.order = el('div', 'vb-order');
  root.appendChild(ui.order);

  ui.bar = el('div', 'vb-bar');
  ui.barInfo = el('div', 'vb-info');
  ui.barCount = el('div', 'vb-count');
  ui.barSum = el('div', 'vb-sum');
  ui.barPrice = el('div', 'vb-price');
  ui.barInfo.appendChild(ui.barCount);
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
    state.counts = {};
    flavors.forEach(function (f) { state.counts[f.name] = 0; });
    ui.note.textContent = '';
    render();
  }

  function change(f, d) {
    var c = state.counts[f.name];
    if (d > 0) {
      if (c >= f.cap) { ui.note.textContent = 'No hay más unidades de ' + f.name + ' disponibles.'; return; }
      state.counts[f.name] = c + 1;
    } else {
      if (c <= 0) return;
      state.counts[f.name] = c - 1;
    }
    ui.note.textContent = '';
    render();
  }

  function orderHtml(t) {
    var ls = lines();
    if (!ls.length) return '';
    var h = '<h4>Tu pedido</h4><dl>';
    var fl = ls.filter(function (l) { return l.kind === 'flavor'; });
    ls.filter(function (l) { return l.kind === 'pack'; }).forEach(function (l) {
      h += '<div class="vb-l" data-k="pack"><dt>' + l.label + '</dt><dd>' + (l.compare && l.compare > l.amount ? '<s>' + money(l.compare) + '</s> ' : '') + money(l.amount) + '</dd></div>';
    });
    if (fl.length) {
      h += '<div class="vb-l vb-l--head"><dt>Sabores</dt><dd></dd></div>';
      fl.forEach(function (l) {
        h += '<div class="vb-l vb-l--sub" data-k="flavor" data-f="' + esc(l.label) + '"><dt>' + esc(l.label) + ' × ' + l.qty + '</dt><dd>+' + money(l.amount) + '</dd></div>';
      });
    }
    h += '<div class="vb-l vb-l--line" data-k="subtotal"><dt>Subtotal</dt><dd>' + money(t.sub) + '</dd></div>';
    if (PCT) h += '<div class="vb-l vb-l--disc" data-k="discount"><dt>' + PCT + ' % de descuento</dt><dd>−' + money(t.disc) + '</dd></div>';
    if (t.bulkOn) h += '<div class="vb-l vb-l--disc" data-k="bulk"><dt>' + BULK.pct + ' % extra en sabores (' + BULK.min + ' o más)</dt><dd>−' + money(t.bulk) + '</dd></div>';
    h += '<div class="vb-l vb-l--total" data-k="total"><dt>Total</dt><dd>' + money(t.total) + '</dd></div></dl>';
    if (PCT) h += '<p class="vb-fine">Los descuentos se aplican automáticamente, sin códigos.</p>';
    return h;
  }

  function render() {
    var t = total(), kit = state.mode === 'kit';
    root.dataset.mode = state.mode;
    if (hasExtras) {
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
      ui.cap.innerHTML = '<b>' + state.n + (state.n > 1 ? ' inhaladores' : ' inhalador') + '</b>' +
        (p && p.compare && p.compare > p.price ? ' · <span class="vb-legend">el ahorro del pack es frente a comprar las unidades sueltas</span>' : '');
    }
    if (hasExtras) {
      ui.flHead.innerHTML = '<span>' + (kit ? 2 : 1) + '</span>Añade tus sabores <small>(opcional · sin límite)</small>';
      flavors.forEach(function (f) {
        var r = rows[f.name], c = state.counts[f.name];
        r.n.textContent = c;
        r.row.classList.toggle('is-on', c > 0);
        r.minus.disabled = c === 0;
        r.plus.disabled = c >= f.cap;
        r.extra.textContent = f.cap === 0 ? 'Agotado' : (c > 0 ? c + ' × ' : '') + '+' + money(f.price);
        r.row.classList.toggle('is-out', f.cap === 0);
      });
    }

    var tt = totals();
    ui.order.innerHTML = orderHtml(tt);
    ui.barCount.innerHTML = hasExtras ? 'Sabores <b>' + t + '</b>' : '';
    ui.barSum.textContent = kit ? (state.n + (state.n > 1 ? ' inhaladores' : ' inhalador')) + (t ? ' + ' + t + (t > 1 ? ' sabores' : ' sabor') : '') : (t ? t + (t > 1 ? ' sabores' : ' sabor') + ' sin inhalador' : '');
    ui.barPrice.innerHTML = (PCT && tt.sub > 0 ? '<s>' + money(tt.sub) + '</s>' : '') + '<b>' + money(tt.total) + '</b>';

    var msg = '', ok = !state.busy;
    if (!kit && t < Math.max(1, ONLY_MIN)) {
      var need = Math.max(1, ONLY_MIN) - t;
      msg = ONLY_MIN > 1 ? 'Sin inhalador, el mínimo es de ' + ONLY_MIN + ' sabores' + (t ? ' (te ' + (need === 1 ? 'falta 1' : 'faltan ' + need) + ').' : '.') : 'Elige al menos un sabor para continuar.';
      ok = false;
    }
    else if (kit && t === 0 && hasExtras) msg = 'Puedes añadir sabores ahora o continuar solo con el inhalador.';
    var blocked = !kit && t < Math.max(1, ONLY_MIN);
    if (blocked) { /* se queda el aviso del mínimo */ }
    else if (BULK && hasExtras && t > 0 && t < BULK.min) { var miss = BULK.min - t; msg = 'Añade ' + miss + (miss === 1 ? ' sabor más' : ' sabores más') + ' y tienes un ' + BULK.pct + ' % extra en los sabores.'; }
    else if (BULK && hasExtras && t >= BULK.min) msg = '¡Conseguido! ' + BULK.pct + ' % extra en tus sabores.';
    else if (BULK && hasExtras && t === 0 && kit) msg = 'Con ' + BULK.min + ' sabores o más, ' + BULK.pct + ' % extra en los sabores.';
    ui.hint.textContent = msg;
    ui.hint.classList.toggle('is-warn', !kit && t < Math.max(1, ONLY_MIN));
    ui.cta.disabled = !ok;
    ui.cta.textContent = state.busy ? 'Añadiendo…' : (!kit && t < Math.max(1, ONLY_MIN) ? (ONLY_MIN > 1 ? 'Mínimo ' + ONLY_MIN + ' sabores' : 'Elige un sabor') : 'Añadir al carrito');
    if (kit && p && !p.available) { ui.cta.disabled = true; ui.cta.textContent = 'Agotado'; }
  }

  function buildItems() {
    var items = [];
    if (state.mode === 'kit') items.push({ id: pack().id, quantity: 1 });
    chosen().forEach(function (f) { items.push({ id: f.id, quantity: state.counts[f.name] }); });
    return items;
  }

  function addToCart() {
    if (state.busy) return;
    if (state.mode === 'only' && total() < Math.max(1, ONLY_MIN)) return;
    var items = buildItems();
    state.busy = true; render();
    fetch(cfg.addUrl || '/cart/add.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ items: items })
    }).then(function (r) {
      if (!r.ok) return r.json().then(function (j) { throw new Error((j && (j.description || j.message)) || 'add failed'); }, function () { throw new Error('add failed'); });
      return r.json();
    }).then(function () {
      window.location.assign(cfg.cartUrl || '/cart');
    }).catch(function (e) {
      state.busy = false; render();
      ui.note.textContent = (e && e.message && e.message !== 'add failed') ? e.message : 'No hemos podido añadirlo al carrito. Inténtalo de nuevo.';
    });
  }

  /* ---------- preselección por URL (?variant=ID&flavor=Nombre) ---------- */
  try {
    var q = new URLSearchParams(location.search);
    var v = q.get('variant'), fl = q.get('flavor');
    if (v) { var pp = packs.filter(function (x) { return String(x.id) === v; })[0]; if (pp) state.n = pp.n; }
    if (fl && state.counts.hasOwnProperty(fl)) state.counts[fl] = 1;
  } catch (e) {}

  render();

  /* API mínima para pruebas */
  root.vbState = state;
  root.vbTotals = totals;
})();
