const {chromium}=require('playwright-core');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox']});
let p=await b.newPage({viewport:{width:1440,height:420}});await p.goto('http://localhost:8765/');await p.waitForTimeout(400);await p.screenshot({path:'s-desktop-1440.png'});await p.close();
p=await b.newPage({viewport:{width:1100,height:420}});await p.goto('http://localhost:8765/');await p.waitForTimeout(400);await p.screenshot({path:'s-tablet-1100.png'});await p.close();
p=await b.newPage({viewport:{width:360,height:640},isMobile:true,hasTouch:true,deviceScaleFactor:2});await p.goto('http://localhost:8765/');await p.waitForTimeout(300);await p.tap('#menu-toggle');await p.waitForTimeout(300);await p.screenshot({path:'s-mobile-360-menu.png'});await p.close();
p=await b.newPage({viewport:{width:390,height:800},isMobile:true,hasTouch:true});await p.goto('http://localhost:8765/#next-drops');await p.waitForTimeout(1200);await p.screenshot({path:'s-mobile-390-anchor.png'});await p.close();
await b.close()})();
