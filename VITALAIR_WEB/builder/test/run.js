const pw = require('/opt/node22/lib/node_modules/playwright');
const { chromium } = pw;
const http = require('http'), fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const srv = http.createServer((q, s) => {
  const u = q.url.split('?')[0];
  if (u === '/cart') { s.end('<h1>cart</h1>'); return; }
  const f = path.join(root, u === '/' ? 'test/index.html' : u);
  if (fs.existsSync(f) && fs.statSync(f).isFile()) { s.setHeader('Content-Type', f.endsWith('.js') ? 'text/javascript' : f.endsWith('.css') ? 'text/css' : 'text/html'); s.end(fs.readFileSync(f)); } else { s.statusCode = 404; s.end(); }
});
let fails = 0; const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) fails++; };
const clean = s => s.replace(/\s/g, '').replace(/−/g, '-');
(async () => {
  await new Promise(r => srv.listen(0, r)); const base = 'http://localhost:' + srv.address().port;
  const br = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  async function page(opts, url) {
    const ctx = await br.newContext(opts); const p = await ctx.newPage(); const req = { body: null };
    await p.route('**/cart/add.js', async r => { req.body = JSON.parse(r.request().postData()); await r.fulfill({ status: 200, contentType: 'application/json', body: '{}' }); });
    await p.goto(base + (url || '/')); return { p, req, ctx };
  }
  const M = { viewport: { width: 390, height: 844 } };
  const plus = (p, f) => p.click(`.vb-row[data-f="${f}"] .vb-plus`);
  const minus = (p, f) => p.click(`.vb-row[data-f="${f}"] .vb-minus`);
  const cnt = (p, f) => p.$eval(`.vb-row[data-f="${f}"] .vb-n`, e => +e.textContent);
  const sel = (p, k) => p.$eval(`.vb-l[data-k="${k}"] dd`, e => e.textContent).then(clean).catch(() => null);
  const bar = p => p.$eval('.vb-price b', e => e.textContent).then(clean);
  const submit = async (pg) => { await pg.p.click('.vb-cta'); await pg.p.waitForURL('**/cart'); return pg.req.body; };
  const FL = ['Mango','Mint','Strawberry','Blueberry','Raspberry','Coffee','Cinnamon','Maple Pepper','Orange','Lemon','Grapefruit','Cranberry','Vanilla'];
  const PACKS = { 1: 2490, 2: 4490, 3: 5990, 4: 7790, 5: 9490 }; const FP = 250, FPC = 300, W = .10, BK = .15; // precios y % de prueba
  const fpr = f => f === 'Coffee' ? FPC : FP;
  const eur = c => (c / 100).toFixed(2).replace('.', ',') + '€';
  // esperado: web 15 % por línea; extra 15 % en sabores (si >= 3) sobre el precio ya rebajado
  const expect = (pack, fl, elig = true) => { const n = Object.values(fl).reduce((a, b) => a + b, 0); let sub = pack, d = elig ? Math.round(pack * W) : 0, d2 = 0;
    for (const [f, q] of Object.entries(fl)) { const L = q * fpr(f); sub += L; const a = Math.round(L * W); d += a; if (n >= 3) d2 += Math.round((L - a) * BK); }
    return { sub, d, d2, total: sub - d - d2 }; };

  // 1) precio base y extras con descuento de lanzamiento: 1 inhalador + 1 sabor
  { const pg = await page(M);
    const X0 = expect(PACKS[1], {}), X1 = expect(PACKS[1], { Mango: 1 });
    ok(await sel(pg.p, 'pack') === eur(PACKS[1]), 'precio base 1 inhalador = ' + eur(PACKS[1]));
    ok(await bar(pg.p) === eur(X0.total), 'sin sabores: total con descuento = ' + eur(X0.total));
    await plus(pg.p, 'Mango');
    ok(await sel(pg.p, 'subtotal') === eur(X1.sub), 'subtotal inhalador + 1 sabor = ' + eur(X1.sub));
    ok(await sel(pg.p, 'discount') === '-' + eur(X1.d), 'descuento de lanzamiento = −' + eur(X1.d));
    ok(await sel(pg.p, 'total') === eur(X1.total), 'total = ' + eur(X1.total));
    const b = await submit(pg);
    ok(b.items.length === 2 && b.items[0].id === 101 && b.items[0].quantity === 1 && b.items[1].id === 201 && b.items[1].quantity === 1 && !b.items[0].properties, 'carrito: inhalador + Mango ×1 (líneas reales)');
    await pg.ctx.close(); }

  // 2) varios sabores y repetir
  { const pg = await page(M);
    for (let i = 0; i < 2; i++) await plus(pg.p, 'Mint'); await plus(pg.p, 'Strawberry'); for (let i = 0; i < 2; i++) await plus(pg.p, 'Mango');
    ok(await cnt(pg.p, 'Mint') === 2, 'repetir sabor: Mint × 2');
    const X = expect(PACKS[1], { Mint: 2, Strawberry: 1, Mango: 2 });
    ok(await sel(pg.p, 'subtotal') === eur(X.sub), 'subtotal inhalador + 5 sabores = ' + eur(X.sub));
    ok(await sel(pg.p, 'discount') === '-' + eur(X.d), 'descuento de lanzamiento = ' + eur(X.d));
    ok(await sel(pg.p, 'bulk') === '-' + eur(X.d2), 'extra 15 % en sabores (5 sabores) = ' + eur(X.d2));
    ok(await sel(pg.p, 'total') === eur(X.total), 'total = ' + eur(X.total));
    ok((await pg.p.$eval('.vb-l[data-f="Mint"] dt', e => e.textContent)).includes('Mint × 2'), 'panel muestra "Mint × 2"');
    ok(clean(await pg.p.$eval('.vb-l[data-f="Mint"] dd', e => e.textContent)) === '+' + eur(2 * FP), 'línea Mint × 2 = +' + eur(2 * FP));
    const b = await submit(pg);
    ok(b.items.length === 4 && b.items.find(i => i.id === 202).quantity === 2 && b.items.find(i => i.id === 201).quantity === 2 && b.items.find(i => i.id === 203).quantity === 1, 'carrito: cantidades por sabor correctas');
    await pg.ctx.close(); }

  // 3) sin límite: los 13 sabores, y precio distinto (Coffee distinto)
  { const pg = await page(M); await pg.p.click('.vb-pack[data-n="2"]');
    for (const f of FL) await plus(pg.p, f);
    for (let i = 0; i < 10; i++) await plus(pg.p, 'Mango'); // 11 Mango
    const cnts = {}; for (const f of FL) cnts[f] = await cnt(pg.p, f);
    const real = PACKS[2] + FL.reduce((a, f) => a + cnts[f] * fpr(f), 0);
    ok(Object.values(cnts).every(v => v >= 1) && cnts.Mango === 11, 'los 13 sabores seleccionados, sin tope (Mango × 11)');
    ok(await sel(pg.p, 'subtotal') === (real / 100).toFixed(2).replace('.', ',') + '€', 'subtotal con 13 sabores y precio distinto de Coffee = ' + real / 100);
    const X3 = expect(PACKS[2], cnts);
    ok(await sel(pg.p, 'total') === eur(X3.total), '13 sabores: total con ambos descuentos = ' + eur(X3.total));
    const b = await submit(pg);
    ok(b.items.length === 14 && b.items[0].id === 102, 'carrito: 2 inhaladores (variante 102) + 13 líneas de sabor');
    await pg.ctx.close(); }

  // 3b) extra en sabores: 1-2 sabores no, 3 o más sí
  { const pg = await page(M);
    await plus(pg.p, 'Mango'); await plus(pg.p, 'Mint');
    ok(await sel(pg.p, 'bulk') === null, '2 sabores: sin extra');
    ok((await pg.p.$eval('.vb-hint', e => e.textContent)).includes('Añade 1 sabor más'), '2 sabores: aviso "añade 1 más"');
    await plus(pg.p, 'Strawberry');
    const X = expect(PACKS[1], { Mango: 1, Mint: 1, Strawberry: 1 });
    ok(await sel(pg.p, 'bulk') === '-' + eur(X.d2), '3 sabores: aparece extra en sabores = ' + eur(X.d2));
    ok(await sel(pg.p, 'total') === eur(X.total), '3 sabores: total = ' + eur(X.total));
    await minus(pg.p, 'Strawberry'); ok(await sel(pg.p, 'bulk') === null, 'al bajar a 2, desaparece el extra');
    await pg.ctx.close(); }
  { const pg = await page(M); await pg.p.click('.vb-mode-btn:nth-child(2)');
    for (let i = 0; i < 5; i++) await plus(pg.p, 'Mint');
    ok(await pg.p.$eval('.vb-cta', e => e.disabled), 'solo sabores con 5 (mínimo 6): botón desactivado');
    ok((await pg.p.$eval('.vb-hint', e => e.textContent)).includes('mínimo es de 6') && (await pg.p.$eval('.vb-hint', e => e.textContent)).includes('falta 1'), 'solo sabores: aviso "te falta 1"');
    await plus(pg.p, 'Mint');
    ok(!(await pg.p.$eval('.vb-cta', e => e.disabled)), 'solo sabores con 6: botón activo');
    const Lm = 6 * FP, a = Math.round(Lm * W), b = Math.round((Lm - a) * BK);
    ok(await sel(pg.p, 'total') === eur(Lm - a - b), 'solo sabores ×6 con ambos descuentos = ' + eur(Lm - a - b));
    await pg.ctx.close(); }

  // 4) quitar y cambiar cantidades
  { const pg = await page(M);
    for (let i = 0; i < 3; i++) await plus(pg.p, 'Mango'); await plus(pg.p, 'Mint');
    await minus(pg.p, 'Mango'); await minus(pg.p, 'Mint');
    ok(await cnt(pg.p, 'Mango') === 2 && await cnt(pg.p, 'Mint') === 0, 'quitar y cambiar cantidades');
    ok(await pg.p.$('.vb-l[data-f="Mint"]') === null, 'sabor a 0 desaparece del resumen');
    ok(await pg.p.$eval('.vb-row[data-f="Mint"] .vb-minus', e => e.disabled), '− deshabilitado en 0');
    const b = await submit(pg); ok(b.items.length === 2 && b.items[1].quantity === 2, 'carrito tras cambios correcto');
    await pg.ctx.close(); }

  // 5) packs: precio base y descuento de lanzamiento (solo packs 1-3)
  { const pg = await page(M);
    for (const [n, price] of Object.entries(PACKS).map(([k, v]) => [+k, v])) { await pg.p.click(`.vb-pack[data-n="${n}"]`);
      const txt = (price / 100).toFixed(2).replace('.', ',');
      ok(await sel(pg.p, 'pack').then(s => s.includes(txt)), `precio base ${n} inhaladores = ${txt}`);
      const elig = n <= 3; const X = expect(price, {}, elig);
      ok(await bar(pg.p) === eur(X.total), `total ${n} inhaladores sin sabores = ${eur(X.total)} (${elig ? 'con' : 'sin'} descuento de lanzamiento)`);
      ok((await sel(pg.p, 'discount') !== null) === elig, `${n} inhaladores: ${elig ? 'muestra' : 'no muestra'} línea de descuento`);
      if (!elig) ok((await pg.p.$eval('.vb-fine', e => e.textContent)).includes('ya incluye su mejor precio'), `${n} inhaladores: explica por qué no se suma el descuento`); }
    await pg.p.click('.vb-pack[data-n="3"]');
    ok((await pg.p.$eval('.vb-cap', e => e.textContent)).includes('Pack recomendado'), 'pack de 3 marcado como recomendado');
    ok((await pg.p.$eval('.vb-cap', e => e.textContent)).includes('por inhalador'), 'se muestra el precio por inhalador');
    await pg.p.click('.vb-pack[data-n="2"]');
    ok((await pg.p.$eval('.vb-cap', e => e.textContent)).includes('Con 3 inhaladores pagas'), 'pack de 2 anima a subir a 3');
    ok((await pg.p.$eval('.vb-cap', e => e.textContent)).includes('Ahorras ' + (4980 - PACKS[2]).toFixed(0).replace(/(\d\d)$/, ',$1').replace(/^/, '')) || (await pg.p.$eval('.vb-cap .vb-save', e => e.textContent)).includes('Ahorras'), 'pack de 2 muestra "Ahorras X €"');
    await pg.ctx.close(); }
  // 5b) pack 4 con sabores: el 15 % solo en sabores
  { const pg = await page(M); await pg.p.click('.vb-pack[data-n="4"]');
    for (let i = 0; i < 3; i++) await plus(pg.p, FL[i]);
        // el descuento web no aplica al pack pero sí a los sabores
    const dFl = 3 * Math.round(FP * W); const d2 = 3 * Math.round((FP - Math.round(FP * W)) * BK);
    ok(await sel(pg.p, 'discount') === '-' + eur(dFl), 'pack de 4 + 3 sabores: descuento solo sobre sabores = ' + eur(dFl));
    ok(await sel(pg.p, 'total') === eur(PACKS[4] + 3 * FP - dFl - d2), 'pack de 4 + 3 sabores: total correcto');
    await pg.ctx.close(); }

  // 6) solo sabores
  { const pg = await page(M); await pg.p.click('.vb-mode-btn:nth-child(2)');
    ok(await pg.p.$eval('.vb-kit', e => e.hidden), 'solo sabores: sin inhaladores');
    ok(await pg.p.$eval('.vb-cta', e => e.disabled), 'solo sabores sin elegir: botón desactivado');
    ok(await pg.p.$eval('.vb-cta', e => e.textContent) === 'Mínimo 6 sabores', 'solo sabores: botón dice Mínimo 6 sabores');
    for (let i = 0; i < 4; i++) await plus(pg.p, 'Mint'); for (let i = 0; i < 2; i++) await plus(pg.p, 'Lemon');
    ok(await sel(pg.p, 'subtotal') === eur(6 * FP), 'solo sabores: 6 × precio = ' + eur(6 * FP));
    ok(await sel(pg.p, 'pack') === null, 'solo sabores: sin línea de inhalador');
    const b = await submit(pg);
    ok(b.items.length === 2 && b.items.find(i => i.id === 202).quantity === 4 && b.items.find(i => i.id === 210).quantity === 2, 'solo sabores: líneas y cantidades correctas');
    await pg.ctx.close(); }

  // 7) stock real: Cranberry tiene 3 en la prueba
  { const pg = await page(M);
    for (let i = 0; i < 5; i++) await pg.p.click('.vb-row[data-f="Cranberry"] .vb-plus', { force: true }).catch(() => {});
    ok(await cnt(pg.p, 'Cranberry') === 3, 'no se puede superar el stock (3 → tope 3)');
    ok(await pg.p.$eval('.vb-row[data-f="Cranberry"] .vb-plus', e => e.disabled), '+ bloqueado al agotar stock');
    ok(await pg.p.$eval('.vb-row[data-f="Cranberry"] .vb-minus', e => !e.disabled), '− sigue activo');
    await pg.ctx.close(); }

  // 8) URL preselección
  { const pg = await page(M, '/?variant=104&flavor=Mint');
    ok(await cnt(pg.p, 'Mint') === 1 && (await sel(pg.p, 'pack')).includes('77,90'), 'URL ?variant=104&flavor=Mint');
    await pg.ctx.close(); }

  // 9) sin precio de sabores: no se muestra la sección (nunca sabores a 0 €)
  { const pg = await page(M, '/test/noprice.html');
    ok(await pg.p.$('.vb-list') === null && await pg.p.$('.vb-mode') === null, 'sabores sin precio: sección oculta');
    const b = await submit(pg); ok(b.items.length === 1 && b.items[0].id === 101, 'sin precio de sabores: solo inhalador');
    await pg.ctx.close(); }

  // 10) dispositivos y sin scroll horizontal
  const devs = [['iPhone 13', pw.devices['iPhone 13']], ['Pixel 7', pw.devices['Pixel 7']], ['Desktop', { viewport: { width: 1280, height: 800 } }]];
  for (const [name, d] of devs) {
    const pg = await page(d); await pg.p.click('.vb-pack[data-n="5"]'); for (let i = 0; i < 8; i++) await plus(pg.p, FL[i]);
    const sw = await pg.p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    ok(sw <= 0, `${name}: sin scroll horizontal`);
    ok(await sel(pg.p, 'total') !== null, `${name}: resumen visible`);
    await pg.p.screenshot({ path: path.join(__dirname, `shot-${name.replace(' ', '')}.png`), fullPage: true });
    await pg.ctx.close();
  }
  for (const w of [320, 360, 768]) { const pg = await page({ viewport: { width: w, height: 800 } }); await pg.p.click('.vb-pack[data-n="5"]'); for (let i = 0; i < 6; i++) await plus(pg.p, FL[i]); ok((await pg.p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)) <= 0, `ancho ${w}px sin scroll horizontal`); await pg.ctx.close(); }
  await br.close(); srv.close(); console.log(fails ? `\n${fails} FALLOS` : '\nTODO OK'); process.exit(fails ? 1 : 0);
})();
