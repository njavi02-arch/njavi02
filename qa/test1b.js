const {chromium}=require('playwright-core');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox']});
for(const w of [320,340,360,375,390,414,430,768,1023]){
 const p=await b.newPage({viewport:{width:w,height:800},hasTouch:true,isMobile:true});await p.goto('http://localhost:8765/');await p.waitForTimeout(250);
 const r=await p.evaluate(()=>{const g=s=>document.querySelector(s).getBoundingClientRect();const t=g('#menu-toggle'),l=g('#logo-mark'),c=g('#cart-toggle');
  return {vw:innerWidth,docW:document.documentElement.scrollWidth,logoRight:Math.round(l.right),firstIconLeft:Math.round(g('#search-toggle').left),toggleRight:Math.round(t.right),toggleInside:t.right<=innerWidth,logoW:Math.round(l.width),headerOverlap:g('#search-toggle').left<l.right}});
 console.log(JSON.stringify(r)); await p.close();}
await b.close()})();
