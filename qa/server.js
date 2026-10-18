const http=require('http'),fs=require('fs'),path=require('path'),page=require('./page.js');
let cart={items:[]};
const P={id:55417870549319,product_id:11330769158471,title:'RED SMILE — Matcha Premium en Polvo 1 kg | Edición Limitada',price:7990};
const view=()=>{const items=cart.items.map(i=>({key:i.key,product_id:P.product_id,variant_id:P.id,product_title:P.title,variant_title:'',image:null,final_price:P.price,quantity:i.q,selling_plan_allocation:null}));
 const n=items.reduce((a,i)=>a+i.quantity,0);const s=items.reduce((a,i)=>a+i.quantity*P.price,0);return {items,item_count:n,items_subtotal_price:s,total_price:s,currency:'EUR'}};
http.createServer((req,res)=>{let u=req.url.split('?')[0];
 const send=(t,b)=>{res.writeHead(200,{'Content-Type':t});res.end(b)};
 if(u==='/cart.js') return send('application/json',JSON.stringify(view()));
 if(u==='/cart/reset'){cart={items:[]};return send('text/plain','ok')}
 if(u==='/cart/add.js'||u==='/cart/change.js'){let b='';req.on('data',d=>b+=d);req.on('end',()=>{const j=JSON.parse(b||'{}');
   if(u==='/cart/add.js'){const it=j.items[0];const ex=cart.items[0];if(ex)ex.q+=it.quantity;else cart.items.push({key:P.id+':abc',q:it.quantity});}
   else{const ix=cart.items.findIndex(i=>i.key===j.id);if(ix>=0){if(j.quantity<=0)cart.items.splice(ix,1);else cart.items[ix].q=j.quantity}}
   send('application/json',JSON.stringify({ok:1}))});return}
 if(u==='/'||u==='/index.html'){const q=new URL(req.url,'http://x').searchParams;return send('text/html',page({upsellJson:q.get('upsell')??undefined}))}
 const f=path.join(__dirname,u);if(fs.existsSync(f)&&fs.statSync(f).isFile()){return send(u.endsWith('.css')?'text/css':u.endsWith('.js')?'application/javascript':'text/plain',fs.readFileSync(f))}
 res.writeHead(404);res.end()}).listen(8765,()=>console.log('up'));
