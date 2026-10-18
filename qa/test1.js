const {chromium}=require('playwright-core');
(async()=>{
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox']});
const URL='http://localhost:8765/';
const rect=e=>e.getBoundingClientRect().toJSON();
console.log('=== T1 MENÚ ESCRITORIO (Chromium headless, fuente Inter local; Cormorant no disponible -> serif de reserva) ===');
for(const w of [1024,1100,1180,1280,1366,1440,1920]){
  const p=await b.newPage({viewport:{width:w,height:800}});await p.goto(URL);await p.waitForTimeout(300);
  const r=await p.evaluate(()=>{
    const links=[...document.querySelectorAll('#desk-nav a')];const logo=document.querySelector('#logo-mark').getBoundingClientRect();
    const icons=document.querySelector('#search-toggle').getBoundingClientRect();
    const rs=links.map(a=>a.getBoundingClientRect());
    const nav=document.querySelector('#desk-nav').getBoundingClientRect();
    const lineH=parseFloat(getComputedStyle(links[0]).lineHeight)||18;
    return {wrapped:rs.some(x=>x.height>lineH*1.6),leftGapToLogo:Math.round(nav.left-logo.right),rightGapToIcons:Math.round(icons.left-nav.right),
      overflowX:document.documentElement.scrollWidth>innerWidth, hamburgerVisible:getComputedStyle(document.querySelector('#menu-toggle')).display!=='none',
      navWidth:Math.round(nav.width),linkHeights:[...new Set(rs.map(x=>Math.round(x.height)))]}});
  console.log(w, JSON.stringify(r)); await p.close();
}
console.log('\n=== T1b MENÚ MÓVIL ===');
for(const w of [320,360,390,430,768,1023]){
  const p=await b.newPage({viewport:{width:w,height:800},hasTouch:true,isMobile:true});await p.goto(URL);await p.waitForTimeout(300);
  const before=await p.evaluate(()=>getComputedStyle(document.querySelector('#menu-toggle')).display);
  await p.tap('#menu-toggle');await p.waitForTimeout(200);
  const r=await p.evaluate(()=>{const m=document.querySelector('#mobile-menu');const links=[...m.querySelectorAll('a')];
    return {open:getComputedStyle(m).display!=='none',expanded:document.querySelector('#menu-toggle').getAttribute('aria-expanded'),count:links.length,texts:links.map(a=>a.textContent.trim()),
     minTapH:Math.round(Math.min(...links.map(a=>a.getBoundingClientRect().height))),clipped:links.some(a=>a.scrollWidth>a.clientWidth+1),
     menuBottom:Math.round(m.getBoundingClientRect().bottom),overflowX:document.documentElement.scrollWidth>innerWidth,deskNavHidden:getComputedStyle(document.querySelector('#desk-nav')).display==='none'}});
  console.log(w,'hamb:',before,JSON.stringify(r)); 
  if(w===390){await p.screenshot({path:'m390-menu.png'});}
  await p.close();
}
await b.close();})();
