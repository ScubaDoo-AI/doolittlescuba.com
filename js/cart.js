/* DoolittleScuba.com cart (Eric, 21 Nov 2026: "Cart on the site").
   Browse and add to cart here; pay at Shopify's checkout on shop.doolittlescuba.com.
   - Cart lives in Shopify (Storefront API, public token); its id is kept in this browser (localStorage ds-cart).
   - Product cards carry data-buy="<SKU stem>" (tools/catalog_map.py); js/catalog.json lists each stem's variants.
   - Automatic discounts (tee + cap, sticker bundles) are Shopify's and show in the drawer as they apply.
   - Partner tracking: a remembered ?src= (localStorage ds-src) rides along as a cart attribute and on the checkout link.
   LAUNCH SWITCH: LIVE=false keeps every card on "Coming soon" for visitors. To try the cart before launch, open any page
   with ?cart=preview (remembered in this browser; ?cart=off ends it). */
(function(){
  'use strict';
  var LIVE = false;
  var TOKEN = 'b048eedb23178c86ccff32db1f44d1f8', API = 'https://shop.doolittlescuba.com/api/2026-10/graphql.json';
  function ls(k,v){ try{ if(v===undefined) return localStorage.getItem(k); if(v===null) localStorage.removeItem(k); else localStorage.setItem(k,v); }catch(e){ return null; } }
  var qp = (location.search.match(/[?&]cart=(preview|off)/)||[])[1];
  if(qp==='preview') ls('ds-cart-preview','1'); if(qp==='off') ls('ds-cart-preview',null);
  if(!LIVE && ls('ds-cart-preview')!=='1') return;
  var PREVIEW = !LIVE;

  function esc(t){ return String(t==null?'':t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }
  function money(n){ n=+n; return '$'+(n%1?n.toFixed(2):n.toFixed(0)); }
  function track(n,d){ try{ window.umami && umami.track(n,d); }catch(e){} }
  function gql(q,v){ return fetch(API,{method:'POST',headers:{'Content-Type':'application/json','X-Shopify-Storefront-Access-Token':TOKEN},body:JSON.stringify({query:q,variables:v||{}})})
    .then(function(r){ return r.json(); }).then(function(j){ if(j.errors) throw new Error(j.errors[0].message); return j.data; }); }
  function partner(){ try{ var r=JSON.parse(ls('ds-src')||'null'); return r&&Date.now()-r.t<2592e6?r.s:null; }catch(e){ return null; } }

  /* ---------- catalog ---------- */
  var catP=null;
  function catalog(){ if(!catP) catP=fetch('/js/catalog.json',{cache:'no-cache'}).then(function(r){ return r.json(); }); return catP; }

  /* ---------- style ---------- */
  var css = ''
   +'.ds-buy{margin:.2rem 0 1rem;display:grid;gap:.55rem}'
   +'.ds-buy .dsc-opt{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center}'
   +'.ds-buy .dsc-opt b{font-family:var(--f-data,monospace);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);min-width:5.5em;font-weight:600}'
   +'.ds-buy .dsc-opt button{font:inherit;font-size:.9rem;min-width:2.6em;padding:.35em .7em;border:1px solid var(--rule);background:var(--panel);color:var(--text);border-radius:6px;cursor:pointer}'
   +'.ds-buy .dsc-opt button[aria-pressed="true"]{border-color:var(--ink);background:var(--ink);color:var(--paper)}'
   +'.ds-buy .dsc-opt button:disabled{opacity:.35;text-decoration:line-through;cursor:not-allowed}'
   +'.ds-buy .dsc-go{display:flex;gap:.6rem;align-items:center;flex-wrap:wrap}'
   +'.ds-buy .dsc-go .dsc-price{font-size:1.15rem;font-weight:700;color:var(--ink)}'
   +'.ds-buy .dsc-go .btn{background:var(--red);border-color:var(--red);color:#fff}'
   +'.ds-buy .dsc-msg{font-size:.85rem;color:var(--muted);min-height:1.2em}'
   +'.ds-buy.mini{margin:.4rem 0 0;gap:.35rem}.ds-buy.mini .dsc-opt b{display:none}.ds-buy.mini .dsc-go .btn{padding:.35em .8em;font-size:.85rem}'
   +'#ds-cart-fab{position:fixed;right:16px;bottom:16px;z-index:60;background:var(--red);color:#fff;border:0;border-radius:999px;padding:.7em 1.1em;font:inherit;font-weight:700;box-shadow:0 6px 20px rgba(0,0,0,.25);cursor:pointer}'
   +'#ds-cart-fab[hidden]{display:none}'
   +'#ds-cart{position:fixed;inset:0;z-index:70;display:flex;justify-content:flex-end;background:rgba(5,12,24,.45)}#ds-cart[hidden]{display:none}'
   +'#ds-cart .dsc-pane{width:min(420px,100%);height:100%;background:var(--paper);color:var(--text);display:flex;flex-direction:column;box-shadow:-8px 0 30px rgba(0,0,0,.3)}'
   +'#ds-cart header{display:flex;justify-content:space-between;align-items:center;padding:1rem 1.1rem;border-bottom:1px solid var(--rule)}'
   +'#ds-cart header h2{margin:0;font-size:1.2rem;color:var(--ink)}#ds-cart header button{font:inherit;font-size:1.4rem;background:none;border:0;color:var(--text);cursor:pointer}'
   +'#ds-cart .dsc-lines{flex:1;overflow:auto;padding:.4rem 1.1rem}'
   +'#ds-cart .dsc-line{display:grid;grid-template-columns:64px 1fr auto;gap:.7rem;padding:.8rem 0;border-bottom:1px solid var(--rule);align-items:start}'
   +'#ds-cart .dsc-line img{width:64px;height:64px;object-fit:contain;background:var(--panel);border-radius:6px}'
   +'#ds-cart .dsc-line .dsc-t{font-weight:600;line-height:1.25}#ds-cart .dsc-line .dsc-v,#ds-cart .dsc-line .dsc-d{font-size:.82rem;color:var(--muted)}#ds-cart .dsc-line .dsc-d{color:var(--red)}'
   +'#ds-cart .dsc-qty{display:flex;align-items:center;gap:.4rem;margin-top:.35rem}#ds-cart .dsc-qty button{width:1.8em;height:1.8em;border:1px solid var(--rule);background:var(--panel);color:var(--text);border-radius:6px;cursor:pointer;font:inherit}'
   +'#ds-cart .dsc-qty .dsc-rm{width:auto;border:0;background:none;color:var(--muted);text-decoration:underline;font-size:.8rem;padding:0 .2em}'
   +'#ds-cart .dsc-sum{padding:1rem 1.1rem;border-top:1px solid var(--rule);display:grid;gap:.4rem}'
   +'#ds-cart .dsc-sum .dsc-r{display:flex;justify-content:space-between}#ds-cart .dsc-sum .dsc-save{color:var(--red)}#ds-cart .dsc-sum .dsc-tot{font-weight:700;font-size:1.1rem}'
   +'#ds-cart .dsc-sum .dsc-note{font-size:.8rem;color:var(--muted)}'
   +'#ds-cart .dsc-checkout{display:block;text-align:center;background:var(--red);color:#fff;border-radius:8px;padding:.85em;font-weight:700;text-decoration:none}'
   +'#ds-cart .dsc-pick:not(:empty){padding:.9rem 1.1rem;border-bottom:1px solid var(--rule);background:var(--panel)}'
   +'#ds-cart .dsc-empty{padding:2rem 0;color:var(--muted)}'
   +'#ds-cart .dsc-pv{font-size:.78rem;background:#fff3c4;color:#5a4500;padding:.45rem 1.1rem}';
  var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);

  /* ---------- cart state ---------- */
  var LINE='id quantity cost{ totalAmount{ amount } subtotalAmount{ amount } } discountAllocations{ discountedAmount{ amount } ... on CartAutomaticDiscountAllocation{ title } } merchandise{ ... on ProductVariant{ id title image{ url(transform:{maxWidth:160}) } product{ title handle } } }';
  var CART='id checkoutUrl totalQuantity cost{ subtotalAmount{ amount } totalAmount{ amount } } discountAllocations{ discountedAmount{ amount } ... on CartAutomaticDiscountAllocation{ title } } lines(first:100){ nodes{ '+LINE+' } }';
  var cart=null;
  function save(c){ cart=c; if(c) ls('ds-cart',c.id); else ls('ds-cart',null); paint(); return c; }
  function load(){ var id=ls('ds-cart'); if(!id) return Promise.resolve(save(null));
    return gql('query($id:ID!){ cart(id:$id){ '+CART+' } }',{id:id}).then(function(d){ return save(d.cart||null); }).catch(function(){ return cart; }); }
  function add(lines){
    var attrs=[]; var p=partner(); if(p) attrs.push({key:'_partner',value:p});
    var q = cart ? gql('mutation($id:ID!,$l:[CartLineInput!]!){ cartLinesAdd(cartId:$id,lines:$l){ cart{ '+CART+' } userErrors{ message } } }',{id:cart.id,l:lines}).then(function(d){ return d.cartLinesAdd; })
                 : gql('mutation($i:CartInput!){ cartCreate(input:$i){ cart{ '+CART+' } userErrors{ message } } }',{i:{lines:lines,attributes:attrs}}).then(function(d){ return d.cartCreate; });
    return q.then(function(r){ if(r.userErrors&&r.userErrors.length) throw new Error(r.userErrors[0].message); return save(r.cart); });
  }
  function setQty(lineId,qty){
    var q = qty>0 ? gql('mutation($id:ID!,$l:[CartLineUpdateInput!]!){ cartLinesUpdate(cartId:$id,lines:$l){ cart{ '+CART+' } } }',{id:cart.id,l:[{id:lineId,quantity:qty}]}).then(function(d){ return d.cartLinesUpdate.cart; })
                  : gql('mutation($id:ID!,$l:[ID!]!){ cartLinesRemove(cartId:$id,lineIds:$l){ cart{ '+CART+' } } }',{id:cart.id,l:[lineId]}).then(function(d){ return d.cartLinesRemove.cart; });
    return q.then(save);
  }

  /* ---------- drawer ---------- */
  var fab=document.createElement('button'); fab.id='ds-cart-fab'; fab.type='button'; fab.hidden=true; document.body.appendChild(fab);
  var dr=document.createElement('div'); dr.id='ds-cart'; dr.hidden=true; dr.setAttribute('role','dialog'); dr.setAttribute('aria-modal','true'); dr.setAttribute('aria-label','Your cart');
  dr.innerHTML='<div class="dsc-pane"><header><h2>Your cart</h2><button type="button" class="dsc-x" aria-label="Close the cart">&times;</button></header>'+(PREVIEW?'<div class="dsc-pv">Cart preview: visitors still see “Coming soon”. The shop opens when the store password comes off.</div>':'')+'<div class="dsc-pick"></div><div class="dsc-lines"></div><div class="dsc-sum"></div></div>';
  document.body.appendChild(dr);
  function openCart(){ dr.hidden=false; document.body.style.overflow='hidden'; dr.querySelector('.dsc-x').focus(); load(); track('cart-open'); }
  function closeCart(){ dr.hidden=true; document.body.style.overflow=''; dr.querySelector('.dsc-pick').innerHTML=''; }
  dr.addEventListener('click',function(e){ if(e.target===dr||e.target.closest('.dsc-x')) closeCart(); });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape'&&!dr.hidden) closeCart(); });
  fab.addEventListener('click',openCart);
  document.addEventListener('click',function(e){ var a=e.target.closest('a[href^="https://shop.doolittlescuba.com/cart"]'); if(a&&!a.closest('#ds-cart')){ e.preventDefault(); openCart(); } });
  // any other link to a shop product page (site guides' "Add the pair", store links): pick it here instead of leaving
  document.addEventListener('click',function(e){ var a=e.target.closest('a[href*="shop.doolittlescuba.com/products/"],a[href*="doolittlescuba.myshopify.com/products/"]');
    if(!a||a.closest('#ds-cart')||e.defaultPrevented) return; var h=(a.getAttribute('href').match(/\/products\/([a-z0-9-]+)/)||[])[1]; if(!h) return;
    e.preventDefault(); catalog().then(function(cat){ var st=cat._h&&cat._h[h]; if(!st){ location.href=a.href; return; }
      openCart(); var pk=dr.querySelector('.dsc-pick'); pk.innerHTML=''; var b=document.createElement('div'); b.className='ds-buy'; pk.appendChild(b); widget(b,st,'',cat[st].dsc-t,false); }); });

  function paint(){
    var n=cart?cart.totalQuantity:0; fab.hidden=!n; fab.textContent='Cart · '+n;
    var L=dr.querySelector('.dsc-lines'), S=dr.querySelector('.dsc-sum');
    if(!cart||!n){ L.innerHTML='<p class="dsc-empty">Your cart is empty.</p>'; S.innerHTML=''; return; }
    L.innerHTML=cart.lines.nodes.map(function(l){ var m=l.merchandise||{}, img=m.image&&m.image.url,
        disc=(l.discountAllocations||[]).reduce(function(a,d){ return a+(+d.discountedAmount.amount); },0);
      return '<div class="dsc-line" data-id="'+esc(l.id)+'">'+(img?'<img src="'+esc(img)+'" alt="">':'<span></span>')
        +'<div><div class="dsc-t">'+esc(m.product?m.product.title:'')+'</div>'+(m.title&&m.title!=='Default Title'?'<div class="dsc-v">'+esc(m.title)+'</div>':'')
        +(disc?'<div class="dsc-d">−'+money(disc)+' '+esc((l.discountAllocations[0]||{}).title||'')+'</div>':'')
        +'<div class="dsc-qty"><button type="button" data-q="'+(l.quantity-1)+'" aria-label="One fewer">−</button><span>'+l.quantity+'</span><button type="button" data-q="'+(l.quantity+1)+'" aria-label="One more">+</button><button type="button" class="dsc-rm" data-q="0">Remove</button></div></div>'
        +'<div>'+money(l.cost.totalAmount.amount)+'</div></div>'; }).join('');
    var sub=+cart.cost.subtotalAmount.amount, tot=+cart.cost.totalAmount.amount,
        lineSave=cart.lines.nodes.reduce(function(a,l){ return a+(l.discountAllocations||[]).reduce(function(b,d){ return b+(+d.discountedAmount.amount); },0); },0),
        cartSave=(cart.discountAllocations||[]).reduce(function(a,d){ return a+(+d.discountedAmount.amount); },0), save=lineSave+cartSave;
    var url=cart.checkoutUrl, p=partner(); if(p) url+=(url.indexOf('?')>-1?'&':'?')+'utm_source='+encodeURIComponent(p)+'&utm_medium=partner';
    S.innerHTML=(save?'<div class="dsc-r dsc-save"><span>You save</span><span>−'+money(save)+'</span></div>':'')
      +'<div class="dsc-r dsc-tot"><span>Total</span><span>'+money(tot)+'</span></div>'
      +'<div class="dsc-note">Shipping and tax are added at checkout. Everything is printed or stitched to order.</div>'
      +'<a class="dsc-checkout" href="'+esc(url)+'" data-umami-event="checkout">Checkout</a>';
  }
  dr.addEventListener('click',function(e){ var b=e.target.closest('button[data-q]'); if(!b) return; var line=b.closest('.dsc-line'); b.disabled=true;
    setQty(line.getAttribute('data-id'),+b.getAttribute('data-q')).catch(function(){ b.disabled=false; }); });

  /* ---------- buy widget ---------- */
  function variants(p,fixed){ return p.v.filter(function(v){ return Object.keys(fixed).every(function(k){ var i=p.o.indexOf(k); return i<0||v[1][i]===fixed[k]; }); }); }
  function widget(box,stem,optStr,label,mini){
    catalog().then(function(cat){
      var p=cat[stem]; if(!p){ box.innerHTML=''; return; }
      var fixed={}; (optStr||'').split('&').forEach(function(kv){ var q=kv.split('='); if(q[0]&&q[1]) fixed[q[0]]=q[1]; });
      var vs=variants(p,fixed); if(!vs.length){ box.innerHTML=''; return; }
      var open=p.o.map(function(n,i){ return n in fixed?null:i; }).filter(function(i){ return i!==null; });
      var sel={}; open.forEach(function(i){ var first=vs.filter(function(v){ return v[3]; })[0]||vs[0]; sel[i]=null; if(vs.every(function(v){ return v[1][i]===vs[0][1][i]; })) sel[i]=vs[0][1][i]; });
      function match(){ return vs.filter(function(v){ return open.every(function(i){ return sel[i]==null||v[1][i]===sel[i]; }); }); }
      function draw(){
        var m=match(), chosen=open.every(function(i){ return sel[i]!=null; })?m[0]:null, prices=m.map(function(v){ return v[2]; });
        var lo=Math.min.apply(null,prices), hi=Math.max.apply(null,prices);
        box.innerHTML=(label?'<div class="dsc-opt"><b>'+esc(label)+'</b></div>':'')+open.map(function(i){
            var vals=[]; vs.forEach(function(v){ if(vals.indexOf(v[1][i])<0) vals.push(v[1][i]); });
            if(vals.length<2) return '';
            return '<div class="dsc-opt" role="group" aria-label="'+esc(p.o[i])+'"><b>'+esc(p.o[i])+'</b>'+vals.map(function(val){
              var ok=vs.some(function(v){ return v[1][i]===val&&v[3]&&open.every(function(j){ return j===i||sel[j]==null||v[1][j]===sel[j]; }); });
              return '<button type="button" data-i="'+i+'" data-val="'+esc(val)+'" aria-pressed="'+(sel[i]===val)+'"'+(ok?'':' disabled')+'>'+esc(val)+'</button>'; }).join('')+'</div>'; }).join('')
          +'<div class="dsc-go"><span class="dsc-price">'+(chosen?money(chosen[2]):lo===hi?money(lo):money(lo)+'–'+money(hi))+'</span>'
          +'<button type="button" class="btn dsc-add"'+(chosen&&chosen[3]?'':' disabled')+'>'+(chosen&&!chosen[3]?'Sold out':'Add to cart')+'</button></div><div class="dsc-msg" aria-live="polite">'+(chosen?'':'Choose '+open.filter(function(i){ return sel[i]==null; }).map(function(i){ return p.o[i].toLowerCase(); }).join(' and ')+'.')+'</div>';
        box.querySelectorAll('.dsc-opt button').forEach(function(b){ b.addEventListener('click',function(){ var i=+b.getAttribute('data-i'); sel[i]=sel[i]===b.getAttribute('data-val')?null:b.getAttribute('data-val'); draw(); }); });
        var ad=box.querySelector('.dsc-add'); ad.addEventListener('click',function(){ if(!chosen) return; ad.disabled=true; ad.textContent='Adding…';
          add([{merchandiseId:'gid://shopify/ProductVariant/'+chosen[0],quantity:1}]).then(function(){ track('cart-add',{item:p.h}); ad.textContent='Added ✓'; box.querySelector('.dsc-msg').innerHTML='In your cart. <a href="#" class="dsc-see">See the cart</a>';
            box.querySelector('.dsc-see').addEventListener('click',function(e){ e.preventDefault(); openCart(); }); setTimeout(draw,2500); })
          .catch(function(err){ ad.disabled=false; ad.textContent='Add to cart'; box.querySelector('.dsc-msg').textContent='Could not add it: '+err.message; }); });
      }
      if(mini) box.classList.add('dsc-mini'); draw();
    }).catch(function(){ box.innerHTML=''; });
  }

  // opened deck card: the size picker goes in; "Coming soon" goes; "Add the pair" opens the pair picker here
  document.addEventListener('ds:open',function(e){
    var root=e.detail&&e.detail.el; if(!root) return;
    var box=root.querySelector('.ds-buy'); if(!box) return;
    var news=root.querySelector('[data-umami-event="deck-launch-news"]'); if(news) news.remove();
    widget(box,box.getAttribute('data-buy'),box.getAttribute('data-buy-opt'),'',false);
    var pairStem=box.getAttribute('data-buy-pair'), pairBtn=root.querySelector('[data-umami-event="deck-pair"]');
    if(pairBtn&&pairStem){ pairBtn.addEventListener('click',function(ev){ ev.preventDefault(); var pb=root.querySelector('.ds-buy.pair');
      if(!pb){ pb=document.createElement('div'); pb.className='ds-buy pair'; box.after(pb); widget(pb,pairStem,'','The pair · cap + shirt',false); }
      pb.scrollIntoView({block:'nearest',behavior:'smooth'}); }); }
  });

  // cards outside a deck (sticker singles, jackets, packs shown as a grid): a small picker under the caption
  function loose(){ document.querySelectorAll('figure[data-buy]').forEach(function(f){
      if(f.hidden||f.closest('[hidden]')||!f.getClientRects().length||f.querySelector('.ds-buy')) return;
      var cap=f.querySelector('figcaption')||f; var b=document.createElement('div'); b.className='ds-buy'; cap.appendChild(b);
      widget(b,f.getAttribute('data-buy'),f.getAttribute('data-buy-opt'),'',true);
      var pill=f.querySelector('.pill.available'); if(pill) pill.textContent='Ready to order'; }); }

  load(); loose();
  if(PREVIEW) try{ console.info('[cart] preview mode (LIVE=false): only this browser sees the cart. ?cart=off to leave.'); }catch(e){}
})();
