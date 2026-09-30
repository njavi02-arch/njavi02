const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const srv = http.createServer((q, s) => {
  const u = q.url.split('?')[0];
  if (u === '/cart') { s.end('<h1>cart</h1>'); return; }
  const f = path.join(root, u === '/' ? 'test/index.html' : u);
  if (fs.existsSync(f) && fs.statSync(f).isFile()) { s.setHeader('Content-Type', f.endsWith('.js') ? 'text/javascript' : f.endsWith('.css') ? 'text/css' : 'text/html'); s.end(fs.readFileSync(f)); } else { s.statusCode = 404; s.end(); }
});
let fails = 0; const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) fails++; };
(async () => {
  await new Promise(r => srv.listen(0, r)); const base = 'http://localhost:' + srv.address().port;
  const br = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  async function page(vw, url) {
    const ctx = await br.newContext({ viewport: vw }); const p = await ctx.newPage(); const req = { body: null };
    await p.route('**/cart/add.js', async r => { req.body = JSON.parse(r.request().postData()); await r.fulfill({ status: 200, contentType: 'application/json', body: '{}' }); });
    await p.goto(base + (url || '/')); return { p, req, ctx };
  }
  const plus = (p, f) => p.click(`.vb-row[data-f="${f}"] .vb-plus`);
  const minus = (p, f) => p.click(`.vb-row[data-f="${f}"] .vb-minus`);
  const cnt = (p, f) => p.$eval(`.vb-row[data-f="${f}"] .vb-n`, e => +e.textContent);
  const total = p => p.$eval('.vb-count b', e => e.textContent);
  const submit = async (pg) => { await pg.p.click('.vb-cta'); await pg.p.waitForURL('**/cart'); return pg.req.body; };
  const FL = ['Mango','Mint','Strawberry','Blueberry','Raspberry','Coffee','Cinnamon','Maple Pepper','Orange','Lemon','Grapefruit','Cranberry','Vanilla'];

  // 1) inhalador 1..3 sabores
  for (const k of [1, 2, 3]) {
    const pg = await page({ width: 390, height: 844 });
    for (let i = 0; i < k; i++) await plus(pg.p, FL[i]);
    ok(await total(pg.p) === `${k} / 3`, `1 inhalador + ${k} sabor(es): contador ${k} / 3`);
    const b = await submit(pg);
    ok(b.items.length === 1 && b.items[0].id === 101 && b.items[0].quantity === 1 && b.items[0].properties['Nº de sabores'] === String(k), `1 inhalador + ${k}: carrito correcto (${b.items[0].properties.Sabores})`);
    await pg.ctx.close();
  }
  // 2) n inhaladores, distribución libre y tope
  const dist = { 2: [3, 2, 1], 3: [5, 2, 1, 1], 4: [4, 4, 2, 2], 5: [5, 4, 3, 2, 1] };
  for (const n of [2, 3, 4, 5]) {
    const pg = await page({ width: 390, height: 844 });
    await pg.p.click(`.vb-pack[data-n="${n}"]`);
    ok((await pg.p.$eval('.vb-cap', e => e.textContent)).includes(`hasta ${n * 3} sabores`), `${n} inhaladores: hasta ${n * 3} sabores`);
    const d = dist[n]; let exp = {};
    for (let i = 0; i < d.length; i++) for (let j = 0; j < d[i]; j++) { await plus(pg.p, FL[i]); }
    const t = d.reduce((a, b) => a + b, 0);
    ok(await total(pg.p) === `${t} / ${n * 3}`, `${n} inhaladores: ${t} / ${n * 3}`);
    // llenar hasta el tope y comprobar bloqueo
    while ((await total(pg.p)).split(' / ')[0] !== String(n * 3)) await plus(pg.p, 'Vanilla');
    const disabled = await pg.p.$eval('.vb-row[data-f="Orange"] .vb-plus', e => e.disabled);
    ok(disabled, `${n} inhaladores: + bloqueado al llegar a ${n * 3}`);
    await pg.p.click('.vb-row[data-f="Orange"] .vb-plus', { force: true }).catch(() => {});
    ok((await total(pg.p)) === `${n * 3} / ${n * 3}`, `${n} inhaladores: no pasa del máximo`);
    const minusOk = await pg.p.$eval('.vb-row[data-f="Mango"] .vb-minus', e => !e.disabled);
    ok(minusOk, `${n} inhaladores: se puede quitar con el tope alcanzado`);
    const b = await submit(pg);
    ok(b.items.length === 1 && b.items[0].id === 100 + n && b.items[0].properties['Nº de sabores'] === String(n * 3), `${n} inhaladores: carrito variante ${100 + n}, ${n * 3} sabores`);
    await pg.ctx.close();
  }
  // 3) cambiar, eliminar, reasignar
  { const pg = await page({ width: 390, height: 844 }); await pg.p.click('.vb-pack[data-n="2"]');
    for (let i = 0; i < 3; i++) await plus(pg.p, 'Mango'); for (let i = 0; i < 3; i++) await plus(pg.p, 'Mint');
    await minus(pg.p, 'Mango'); await minus(pg.p, 'Mango'); await plus(pg.p, 'Coffee');
    ok(await cnt(pg.p, 'Mango') === 1 && await cnt(pg.p, 'Mint') === 3 && await cnt(pg.p, 'Coffee') === 1 && await total(pg.p) === '5 / 6', 'cambiar/eliminar/reasignar cantidades');
    const b = await submit(pg); ok(b.items[0].properties.Sabores === 'Mango ×1, Mint ×3, Coffee ×1', 'resumen de sabores ordenado: ' + b.items[0].properties.Sabores);
    await pg.ctx.close(); }
  // 4) bajar nº de inhaladores con exceso
  { const pg = await page({ width: 390, height: 844 }); await pg.p.click('.vb-pack[data-n="3"]');
    for (let i = 0; i < 9; i++) await plus(pg.p, FL[i % 4]);
    await pg.p.click('.vb-pack[data-n="1"]');
    ok(await total(pg.p) === '3 / 3', 'bajar de 3 a 1 inhalador: ajusta a 3 / 3');
    ok((await pg.p.$eval('.vb-toast', e => e.textContent)).includes('ajustado'), 'aviso de ajuste visible');
    await pg.ctx.close(); }
  // 5) sin sabores
  { const pg = await page({ width: 390, height: 844 });
    ok(await pg.p.$eval('.vb-cta', e => e.disabled), 'sin sabores: botón desactivado');
    ok((await pg.p.$eval('.vb-hint', e => e.textContent)) === 'Elige al menos un sabor para continuar.', 'sin sabores: mensaje correcto');
    await plus(pg.p, 'Mango'); ok(!(await pg.p.$eval('.vb-cta', e => e.disabled)), 'con 1 sabor (menos del máximo) se puede continuar');
    await pg.ctx.close(); }
  // 6) solo sabores
  { const pg = await page({ width: 390, height: 844 }); await pg.p.click('.vb-mode-btn:nth-child(2)');
    ok(await pg.p.$eval('.vb-kit', e => e.hidden), 'solo sabores: no aparece la lógica de inhaladores');
    for (let i = 0; i < 4; i++) await plus(pg.p, 'Mint'); for (let i = 0; i < 2; i++) await plus(pg.p, 'Lemon');
    ok(await total(pg.p) === '6', 'solo sabores: contador sin máximo = 6');
    ok((await pg.p.$eval('.vb-price', e => e.textContent)).replace(/\s/g, '').includes('59,70'), 'solo sabores: total 6 × 9,95 = 59,70');
    const b = await submit(pg);
    ok(b.items.length === 2 && b.items.find(i => i.id === 202).quantity === 4 && b.items.find(i => i.id === 210).quantity === 2, 'solo sabores: líneas por sabor con cantidades correctas');
    await pg.ctx.close(); }
  // 7) precio por pack
  { const pg = await page({ width: 390, height: 844 });
    for (const [n, txt] of [[1,'19,99'],[2,'39,98'],[3,'44,97'],[4,'57,97'],[5,'64,95']]) { await pg.p.click(`.vb-pack[data-n="${n}"]`); ok((await pg.p.$eval('.vb-price', e => e.textContent)).replace(/\s/g,'').includes(txt), `precio ${n} inhaladores = ${txt}`); }
    await pg.ctx.close(); }
  // 8) URL preselección
  { const pg = await page({ width: 390, height: 844 }, '/?variant=104&flavor=Mint');
    ok(await total(pg.p) === '1 / 12' && await cnt(pg.p, 'Mint') === 1, 'URL ?variant=104&flavor=Mint: 4 inhaladores y Mint ×1');
    await pg.ctx.close(); }
  // 9) sin scroll horizontal, móvil y escritorio
  for (const w of [320, 360, 390, 768, 1280]) {
    const pg = await page({ width: w, height: 800 });
    await pg.p.click('.vb-pack[data-n="5"]'); for (let i = 0; i < 6; i++) await plus(pg.p, FL[i]);
    const sw = await pg.p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    ok(sw <= 0, `ancho ${w}px: sin scroll horizontal (${sw})`);
    if (w === 390 || w === 1280) await pg.p.screenshot({ path: path.join(__dirname, `shot-${w}.png`), fullPage: true });
    await pg.ctx.close();
  }
  await br.close(); srv.close(); console.log(fails ? `\n${fails} FALLOS` : '\nTODO OK'); process.exit(fails ? 1 : 0);
})();
