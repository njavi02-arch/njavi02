const {chromium}=require('playwright-core');
const URL=process.env.URL||'http://localhost:8765/';
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox']});
console.log('=== T3 CURSOR (ratón simulado, Chromium escritorio 1440x900) ===');
let p=await b.newPage({viewport:{width:1440,height:900}});const errs=[];p.on('pageerror',e=>errs.push(String(e)));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto(URL);await p.waitForTimeout(400);
const st=async()=>p.evaluate(()=>({ring:document.getElementById('custom-cursor').className,dot:(document.getElementById('custom-cursor-dot')||{}).className,bodyActive:document.body.classList.contains('custom-cursor-active'),
 ringBox:(r=>({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),w:Math.round(r.width)}))(document.getElementById('custom-cursor').getBoundingClientRect()),
 dotBox:(r=>({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)}))((document.getElementById('custom-cursor-dot')||document.body).getBoundingClientRect())}));
await p.mouse.move(700,600,{steps:5});await p.waitForTimeout(500);
console.log('reposo      ',JSON.stringify(await st()));
await p.hover('#desk-nav a:nth-child(1)',{force:true}).catch(()=>{});
// en 1440 el menú de escritorio existe
await p.mouse.move(300,500,{steps:4});await p.hover('.kc-rh-cta');await p.waitForTimeout(500);
console.log('botón compra',JSON.stringify(await st()));
await p.hover('.kc-rm-cta');await p.waitForTimeout(300);console.log('enlace      ',JSON.stringify(await st()));
await p.hover('#t-input');await p.waitForTimeout(300);console.log('campo texto ',JSON.stringify(await st()), 'cursor css del input:',await p.evaluate(()=>getComputedStyle(document.getElementById('t-input')).cursor));
await p.mouse.move(700,600);await p.waitForTimeout(400);
console.log('pointer-events ring/dot:',await p.evaluate(()=>[getComputedStyle(document.getElementById('custom-cursor')).pointerEvents,getComputedStyle(document.getElementById('custom-cursor-dot')).pointerEvents]));
// click a través del cursor
await p.evaluate(()=>{window.__c=0;document.querySelector('.kc-rh-cta').addEventListener('click',e=>{e.preventDefault();window.__c++})});
await p.click('.kc-rh-cta');console.log('click en botón llegó al botón:',await p.evaluate(()=>window.__c===1));
const top=await p.evaluate(()=>{const e=document.querySelector('.kc-rh-cta').getBoundingClientRect();return document.elementFromPoint(e.x+e.width/2,e.y+e.height/2).className});
console.log('elementFromPoint sobre botón (no debe ser el cursor):',top);
// scroll
await p.mouse.wheel(0,1500);await p.waitForTimeout(500);console.log('scrollY tras rueda:',await p.evaluate(()=>Math.round(scrollY)));
// colores verdes en estilos computados del cursor
const col=await p.evaluate(()=>['custom-cursor','custom-cursor-dot'].map(id=>{const s=getComputedStyle(document.getElementById(id));return [id,s.backgroundColor,s.borderColor,s.boxShadow]}));
console.log('colores cursor:',JSON.stringify(col));
console.log('errores de consola/JS:',errs.length?errs:'ninguno');
// pantalla táctil: no debe activarse
const t=await b.newPage({viewport:{width:390,height:800},hasTouch:true,isMobile:true});await t.goto(URL);await t.waitForTimeout(300);
console.log('móvil táctil -> cursor activo:',await t.evaluate(()=>document.body.classList.contains('custom-cursor-active')),'| dot existe:',await t.evaluate(()=>!!document.getElementById('custom-cursor-dot')));
// reduced motion
const rm=await b.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'});await rm.goto(URL);await rm.mouse.move(100,100);await rm.mouse.move(900,500);await rm.waitForTimeout(100);
console.log('reduced-motion: ring en destino sin retraso:',await rm.evaluate(()=>{const r=document.getElementById('custom-cursor').getBoundingClientRect();return Math.abs(r.x+r.width/2-900)<2&&Math.abs(r.y+r.height/2-500)<2}));
await p.screenshot({path:'cursor-1440.png'});
await b.close()})();
