const {chromium}=require('playwright-core');
const BASE='http://localhost:8765';
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox']});
async function run(label,query,vw){
 await fetch(BASE+'/cart/reset');
 const p=await b.newPage({viewport:{width:vw,height:800},isMobile:vw<500,hasTouch:vw<500});const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto(BASE+'/'+query);await p.waitForTimeout(400);
 console.log('\n--- '+label+' (ancho '+vw+') ---');
 await p.evaluate(()=>window.VDT.cartApi.addToCart(55417870549319,1));      // lo que hace el botón "Añadir al carrito"
 await p.waitForTimeout(300);
 await p.click('#cart-toggle');await p.waitForTimeout(600);
 const s=()=>p.evaluate(()=>{const g=i=>document.getElementById(i);const up=g('cart-upsell');
  return {abierto:g('cart-panel').classList.contains('open'),badge:g('cart-count').textContent,lineas:g('cart-items').querySelectorAll('[data-qty="1"]').length,
   producto:(g('cart-items').querySelector('p')||{}).textContent,cantidad:(g('cart-items').querySelector('span.w-4')||{}).textContent,
   subtotal:g('cart-subtotal').textContent,envio:g('cart-shipping').textContent,total:g('cart-total').textContent,progreso:g('shipping-progress-text').textContent,
   upsell:{hijos:up.children.length,alto:Math.round(up.getBoundingClientRect().height),visible:getComputedStyle(up).display!=='none'&&up.getBoundingClientRect().height>0},
   panelSinDesbordeX:g('cart-panel').scrollWidth<=g('cart-panel').clientWidth+1}});
 console.log('1 unidad  :',JSON.stringify(await s()));
 await p.click('[data-qty="1"]');await p.waitForTimeout(400);console.log('+1 -> 2    :',JSON.stringify((({cantidad,subtotal,total,envio})=>({cantidad,subtotal,total,envio}))(await s())));
 await p.click('[data-qty="-1"]');await p.waitForTimeout(400);console.log('-1 -> 1    :',JSON.stringify((({cantidad,subtotal,total})=>({cantidad,subtotal,total}))(await s())));
 await p.click('[data-remove]');await p.waitForTimeout(400);
 console.log('quitar     :',JSON.stringify(await p.evaluate(()=>({vacio:document.getElementById('cart-items').textContent.trim(),total:document.getElementById('cart-total').textContent,badgeOculto:document.getElementById('cart-count').classList.contains('hidden')}))));
 console.log('errores JS :',errs.length?errs:'ninguno');
 await p.screenshot({path:'cart-'+label.replace(/\W+/g,'_')+'.png'});await p.close();}
await run('sin datos de sugerencias (script ausente)','',1440);
await run('coleccion vacia -> JSON []','?upsell=%5B%5D',1440);
await run('coleccion vacia -> JSON [] movil','?upsell=%5B%5D',390);
await run('con 1 sugerencia valida (simula accesorios con stock)','?upsell='+encodeURIComponent(JSON.stringify([{product_id:1,variant_id:2,title:"Chasen (ejemplo de prueba)",price:1890,image:null}])),1440);
await b.close()})();
