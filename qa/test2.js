const {chromium}=require('playwright-core');
const URL='http://localhost:8765/';
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox']});
console.log('=== T2 TARJETAS "Soon" ===');
for(const w of [320,390,768,1024,1440]){
 const p=await b.newPage({viewport:{width:w,height:900}});await p.goto(URL);await p.waitForTimeout(250);
 const r=await p.evaluate(()=>{const cards=[...document.querySelectorAll('.kc-rm-card')];const R=e=>e.getBoundingClientRect();
  const info=cards.map(c=>{const bd=c.querySelector('.kc-rm-badge');const cr=R(c),br=R(bd);return {id:c.id,badgeInside:br.left>=cr.left&&br.right<=cr.right&&br.top>=cr.top&&br.bottom<=cr.bottom,badgeTopOffset:Math.round(br.top-cr.top),badgeLeftOffset:Math.round(br.left-cr.left),
   cardW:Math.round(cr.width),cardH:Math.round(cr.height),cols:getComputedStyle(c.parentElement).gridTemplateColumns.split(' ').length}});
  const cr=cards.map(R);const overlap=cr.some((a,i)=>cr.some((b,j)=>i<j&&a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top));
  return {info,cardsOverlap:overlap,overflowX:document.documentElement.scrollWidth>innerWidth,sameHeightRow:new Set(cr.map(x=>Math.round(x.height))).size}});
 console.log(w,JSON.stringify(r)); await p.close();}
console.log('\n=== T2b ANCLAJES del menú vs cabecera fija ===');
for(const [w,mobile] of [[1440,false],[390,true]]){
 for(const id of ['matcha-premium','matcha-latte','next-drops']){
  const p=await b.newPage({viewport:{width:w,height:800},isMobile:mobile,hasTouch:mobile});await p.goto(URL);await p.waitForTimeout(200);
  await p.evaluate(i=>{location.hash='#'+i},id);await p.waitForTimeout(1200);
  const r=await p.evaluate(i=>{const c=document.getElementById(i).getBoundingClientRect(),h=document.getElementById('main-header').getBoundingClientRect();return {cardTop:Math.round(c.top),headerBottom:Math.round(h.bottom),hiddenUnderHeader:c.top<h.bottom}},id);
  console.log(w,id,JSON.stringify(r)); await p.close();}}
await b.close()})();
