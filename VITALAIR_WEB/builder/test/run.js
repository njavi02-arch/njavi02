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
  const E = 199; // extra de prueba
  const eur = c => (c / 100).toFixed(2).replace('.', ',') + '€';
  // esperado: web 15 % por línea; extra 15 % en sabores (si >= 3) sobre el precio ya rebajado
  const expect = (pack, fl) => { const n = Object.values(fl).reduce((a, b) => a + b, 0); let sub = pack, d = Math.round(pack * .15), d2 = 0;
    for (const [f, q] of Object.entries(fl)) { const L = q * (f === 'Coffee' ? 249 : 199); sub += L; const a = Math.round(L * .15); d += a; if (n >= 3) d2 += Math.round((L - a) * .15); }
    return { sub, d, d2, total: sub - d - d2 }; };

  // 1) precio base y extras, 15 %: 1 inhalador + 1 sabor
  { const pg = await page(M);
    ok(await sel(pg.p, 'pack') === '19,99€', 'precio base 1 inhalador = 19,99 €');
    ok(await bar(pg.p) === '16,99€', 'sin sabores: total 19,99 − 15 % = 16,99 €');
    await plus(pg.p, 'Mango');
    ok(await sel(pg.p, 'subtotal') === '21,98€', 'subtotal 19,99 + 1,99 = 21,98 €');
    ok(await sel(pg.p, 'discount') === '-3,30€', 'descuento 15 % = −3,30 €');
    ok(await sel(pg.p, 'total') === '18,68€', 'total = 18,68 €');
    const b = await submit(pg);
    ok(b.items.length === 2 && b.items[0].id === 101 && b.items[0].quantity === 1 && b.items[1].id === 201 && b.items[1].quantity === 1 && !b.items[0].properties, 'carrito: inhalador + Mango ×1 (líneas reales)');
    await pg.ctx.close(); }

  // 2) varios sabores y repetir
  { const pg = await page(M);
    for (let i = 0; i < 2; i++) await plus(pg.p, 'Mint'); await plus(pg.p, 'Strawberry'); for (let i = 0; i < 2; i++) await plus(pg.p, 'Mango');
    ok(await cnt(pg.p, 'Mint') === 2, 'repetir sabor: Mint × 2');
    const X = expect(1999, { Mint: 2, Strawberry: 1, Mango: 2 });
    ok(await sel(pg.p, 'subtotal') === eur(X.sub), 'subtotal 19,99 + 5 × 1,99 = ' + eur(X.sub));
    ok(await sel(pg.p, 'discount') === '-' + eur(X.d), 'descuento web 15 % = ' + eur(X.d));
    ok(await sel(pg.p, 'bulk') === '-' + eur(X.d2), 'extra 15 % en sabores (5 sabores) = ' + eur(X.d2));
    ok(await sel(pg.p, 'total') === eur(X.total), 'total = ' + eur(X.total));
    ok((await pg.p.$eval('.vb-l[data-f="Mint"] dt', e => e.textContent)).includes('Mint × 2'), 'panel muestra "Mint × 2"');
    ok(clean(await pg.p.$eval('.vb-l[data-f="Mint"] dd', e => e.textContent)) === '+3,98€', 'línea Mint × 2 = +3,98 €');
    const b = await submit(pg);
    ok(b.items.length === 4 && b.items.find(i => i.id === 202).quantity === 2 && b.items.find(i => i.id === 201).quantity === 2 && b.items.find(i => i.id === 203).quantity === 1, 'carrito: cantidades por sabor correctas');
    await pg.ctx.close(); }

  // 3) sin límite: los 13 sabores, y precio distinto (Coffee 2,49)
  { const pg = await page(M); await pg.p.click('.vb-pack[data-n="2"]');
    for (const f of FL) await plus(pg.p, f);
    for (let i = 0; i < 10; i++) await plus(pg.p, 'Mango'); // 11 Mango
    const tot = 12 * 199 + 249 + 10 * 199; // 12 sabores a 1,99 + café 2,49 + 10 mango extra
    const sub = 3998 + 11 * 199 + 12 * 199 + 249 - 11 * 199 + 11 * 199 - 11 * 199; // se recalcula abajo
    const expSub = 3998 + 13 * 0 + (11 * 199) + (11 * 199 - 11 * 199) + 0;
    const cnts = {}; for (const f of FL) cnts[f] = await cnt(pg.p, f);
    const real = 3998 + FL.reduce((a, f) => a + cnts[f] * (f === 'Coffee' ? 249 : 199), 0);
    ok(Object.values(cnts).every(v => v >= 1) && cnts.Mango === 11, 'los 13 sabores seleccionados, sin tope (Mango × 11)');
    ok(await sel(pg.p, 'subtotal') === (real / 100).toFixed(2).replace('.', ',') + '€', 'subtotal con 13 sabores y precio distinto de Coffee = ' + real / 100);
    const X3 = expect(3998, cnts);
    ok(await sel(pg.p, 'total') === eur(X3.total), '13 sabores: total con 15 % + 15 % extra = ' + eur(X3.total));
    const b = await submit(pg);
    ok(b.items.length === 14 && b.items[0].id === 102, 'carrito: 2 inhaladores (variante 102) + 13 líneas de sabor');
    await pg.ctx.close(); }

  // 3b) extra en sabores: 1-2 sabores no, 3 o más sí
  { const pg = await page(M);
    await plus(pg.p, 'Mango'); await plus(pg.p, 'Mint');
    ok(await sel(pg.p, 'bulk') === null, '2 sabores: sin extra');
    ok((await pg.p.$eval('.vb-hint', e => e.textContent)).includes('Añade 1 sabor más'), '2 sabores: aviso "añade 1 más"');
    await plus(pg.p, 'Strawberry');
    const X = expect(1999, { Mango: 1, Mint: 1, Strawberry: 1 });
    ok(await sel(pg.p, 'bulk') === '-' + eur(X.d2), '3 sabores: aparece extra 15 % = ' + eur(X.d2));
    ok(await sel(pg.p, 'total') === eur(X.total), '3 sabores: total = ' + eur(X.total));
    await minus(pg.p, 'Strawberry'); ok(await sel(pg.p, 'bulk') === null, 'al bajar a 2, desaparece el extra');
    await pg.ctx.close(); }
  { const pg = await page(M); await pg.p.click('.vb-mode-btn:nth-child(2)');
    for (let i = 0; i < 3; i++) await plus(pg.p, 'Mint');
    const X = expect(0, { Mint: 3 }); X.sub -= 0;
    const Lm = 3 * 199, a = Math.round(Lm * .15), b = Math.round((Lm - a) * .15);
    ok(await sel(pg.p, 'total') === eur(Lm - a - b), 'solo sabores ×3 con ambos descuentos = ' + eur(Lm - a - b));
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

  // 5) packs: precio base por cantidad de inhaladores
  { const pg = await page(M);
    for (const [n, txt] of [[1,'19,99'],[2,'39,98'],[3,'44,97'],[4,'57,97'],[5,'64,95']]) { await pg.p.click(`.vb-pack[data-n="${n}"]`); ok(await sel(pg.p, 'pack') .then(s => s.includes(txt)), `precio base ${n} inhaladores = ${txt}`);
      const exp = ((+txt.replace(',', '.') * 100) - Math.round(+txt.replace(',', '.') * 100 * .15)) / 100; ok(await bar(pg.p) === exp.toFixed(2).replace('.', ',') + '€', `total ${n} inhaladores sin sabores con 15 % = ${exp}`); }
    await pg.ctx.close(); }

  // 6) solo sabores
  { const pg = await page(M); await pg.p.click('.vb-mode-btn:nth-child(2)');
    ok(await pg.p.$eval('.vb-kit', e => e.hidden), 'solo sabores: sin inhaladores');
    ok(await pg.p.$eval('.vb-cta', e => e.disabled), 'solo sabores sin elegir: botón desactivado');
    for (let i = 0; i < 4; i++) await plus(pg.p, 'Mint'); for (let i = 0; i < 2; i++) await plus(pg.p, 'Lemon');
    ok(await sel(pg.p, 'subtotal') === '11,94€', 'solo sabores: 6 × 1,99 = 11,94 €');
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
    ok(await cnt(pg.p, 'Mint') === 1 && (await sel(pg.p, 'pack')).includes('57,97'), 'URL ?variant=104&flavor=Mint');
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
