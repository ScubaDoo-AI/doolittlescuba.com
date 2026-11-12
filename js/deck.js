// deck.js · 11 Nov 2026, late: rolling decks drag-rolled (no native scroll), tabs fitted to the width
/* Doolittle Scuba — the shared page scripts: the photo viewer, the shirts/hats as a deck of cards, and the designs grid filter.
   Used by the home page and the collection pages. Each page calls what it has:
     DS.lightbox()                               every .sh-grid on the page opens its photos in #sh-lb
     DS.deck('shirts','sh-grid',DS.shirtsCfg({lines:[['plates','Signature Series'],…], contact:'/#contact'}))
     DS.deck('hats','ht-grid',{…})               a deck with its own config (see the home page)
     DS.deck('lines','co-grid',{…, bar:false, status:'', start:0, go:function(it){…}})   the collections as a deck: no chips, no pill,
                                                 rests on the first card (pulled forward, tag showing), open = go to the page
     DS.designs()                                #dz-grid: status / line / subset chips, counts, the viewer
   A deck opens on the line named in the URL hash (/off-world/#offworld-dark), so other pages can deep-link a line. */
window.DS=(function(){
  var DS={};
  var sites={}; try{ JSON.parse(document.getElementById('sites-data').textContent).forEach(function(x){ sites[x.slug]=x; }); }catch(e){}
  var CW=280;
  function track(n,d){ try{ window.umami && umami.track(n,d); }catch(e){} }
  function h(tag,cls,html){ var e=document.createElement(tag); if(cls) e.className=cls; if(html!=null) e.innerHTML=html; return e; }
  function esc(t){ return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }
  function dark(hex){ var r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16); return (r*299+g*587+b*114)/1000<128; }
  function flag(us){ return us?'<svg viewBox="0 0 26 18" role="img" aria-label="Diver-down flag, US waters"><rect width="26" height="18" fill="#C8202A"/><path d="M0 0h4.5L26 14.5V18h-4.5L0 3.5z" fill="#fff"/></svg>':'<svg viewBox="0 0 26 18" role="img" aria-label="Alpha flag, international"><path d="M0 0h13v18H0z" fill="#fff" stroke="#8a97a8" stroke-width=".6"/><path d="M13 0h13l-6 9 6 9H13z" fill="#1F4FA3"/></svg>'; }
  var MARK={site:'Site front: dive flag, site name and coordinates',dsmark:'DS mark',stack:'DS stacked lockup',wordmark:'Wordmark',seal:'The seal',tagline:'“Do - A - Little Scuba”',none:'plain'};

  function deck(sectionId, gridId, cfg){
    if(!window.requestAnimationFrame) return;
    var sec=document.getElementById(sectionId), grid=document.getElementById(gridId); if(!sec||!grid) return;
    var figs=Array.prototype.slice.call(grid.querySelectorAll('figure.sh[data-slug]')); if(figs.length<3) return;
    var items=figs.map(function(f){
      var b=f.querySelector('.sh-img'), img=b.querySelector('img'), pill=f.querySelector('.pill'), siteSlug=(f.dataset.custom||'').match(/[#&]site=([a-z0-9-]+)/);
      var site=sites[f.dataset.slug]||(siteSlug&&f.dataset.line==='site'?sites[siteSlug[1]]:null)||null;
      var sub=f.querySelector('.dz-s'); sub=sub?sub.textContent.replace(/\s+/g,' ').trim():'';
      return {slug:f.dataset.slug, line:f.dataset.line, name:f.querySelector('.dz-t').textContent, code:f.dataset.code, colour:f.dataset.colour, hex:f.dataset.hex,
        front:b.dataset.front, back:b.dataset.back, art:f.dataset.art||'', thumb:img.getAttribute('src'), cap:b.dataset.cap, sub:sub, text:f.dataset.text||'',
        status:pill?pill.textContent:(cfg.status!=null?cfg.status:'Coming soon'), statusClass:pill?pill.className.replace('pill','').trim():'available',
        guide:f.dataset.guide||'', custom:f.dataset.custom||'/custom/', site:site, price:f.dataset.price||'', finish:f.dataset.finish||'', parts:(function(){ var o={}; (f.dataset.custom||'').replace(/^[^#]*#/,'').split('&').forEach(function(kv){ var q=kv.split('='); o[q[0]]=q[1]; }); return o; })()};
    });
    var state={line:cfg.lines[0][0], active:-1, open:-1, view:'front', touch:false}, lastPointer='mouse', curStep=0, rolls=false, drag=null, fling=0;
    var MIN_FIT=26, ROLL_PX=48, shifted=false; try{ shifted=matchMedia('(hover: hover)').matches; }catch(e){}
    try{ if(matchMedia('(hover: none)').matches){ lastPointer='touch'; state.touch=true; } }catch(e){}
    var list=function(){ return items.filter(function(x){return x.line===state.line;}); };

    sec.classList.add('has-deck');
    var wrap=h('div','deck-wrap'+(cfg.cls?' '+cfg.cls:'')), bar=h('div','deck-bar'); bar.setAttribute('role','group'); bar.setAttribute('aria-label','Choose a line');
    var chips={};
    if(cfg.bar!==false) cfg.lines.forEach(function(l){
      var c=h('button','chip',esc(l[1])+' <span class="mono">'+items.filter(function(x){return x.line===l[0];}).length+'</span>'); c.type='button'; c.dataset.deckLine=l[0];
      c.addEventListener('click',function(){ setLine(l[0]); track('deck-line',{deck:gridId,line:l[0]}); }); bar.appendChild(c); chips[l[0]]=c;
    });
    var dk=h('div','deck'+(cfg.cls?' '+cfg.cls:'')), hint=h('p','deck-hint',''), row=h('div','deck-row'); dk.appendChild(hint); dk.appendChild(row);
    var foot=h('div','deck-foot','<span class="cnt"></span><span class="kbd">Tab moves along the deck &middot; Enter opens</span>');
    var open=h('div','sh-open'); open.hidden=true;
    if(cfg.bar!==false) wrap.appendChild(bar); wrap.appendChild(dk); wrap.appendChild(foot); wrap.appendChild(open);
    grid.parentNode.insertBefore(wrap, grid);

    var cards=[];
    // Two layouts. When the whole deck fits the screen (its own tab width, or narrower tabs down to MIN_FIT px), the tabs lie
    // side by side and the card under the pointer or finger pulls forward. When it cannot fit (phones), the deck ROLLS:
    // it is a strip wider than the screen that slides to keep the pulled card in the middle, and a drag across it rolls the
    // cards one per ROLL_PX px of travel (a flick carries on a little). No native scrolling: the browser cannot bounce it.
    function padL(){ return parseFloat(getComputedStyle(row).paddingLeft)||0; }
    function padX(){ var cs=getComputedStyle(row); return (parseFloat(cs.paddingLeft)||0)+(parseFloat(cs.paddingRight)||0); }
    function layoutFor(n){
      var base=cfg.step[state.line]; if(cfg.cls==='deck-coll'||n<2||!dk.clientWidth) return {step:base, rolls:false};
      var cs=getComputedStyle(dk), avail=dk.clientWidth-(parseFloat(cs.paddingLeft)||0)-(parseFloat(cs.paddingRight)||0)-padX()-2, fit=Math.floor((avail-280)/(n-1));
      if(fit>=base) return {step:base, rolls:false};
      if(fit>=MIN_FIT) return {step:fit, rolls:false};
      return {step:Math.max(base,ROLL_PX), rolls:true};
    }
    function build(){
      row.innerHTML=''; cards=[]; var L=list(), lay=layoutFor(L.length), step=lay.step; curStep=step; rolls=lay.rolls;
      dk.classList.toggle('rolls',rolls); row.style.setProperty('--step',step+'px'); row.style.transform='';
      L.forEach(function(it,i){
        var card=h('div','dk'); card.dataset.line=it.line; card.style.setProperty('--hex',it.hex); card.style.setProperty('--step',step+'px');
        var face=h('button','dk-face'); face.type='button'; face.setAttribute('aria-label',it.name+', '+(it.colour||'').toLowerCase()+'. Pull forward or open');
        face.innerHTML='<span class="dk-tab'+(dark(it.hex)?' dark':'')+'" style="background:'+it.hex+'"><span class="nm">'+esc(it.name)+'</span>'+(step>=56&&it.code?'<span class="cd">No. '+esc(it.code)+'</span>':'')+'</span><span class="dk-pic"><img src="'+esc(it.thumb)+'" width="600" height="600" loading="lazy" decoding="async" alt=""></span>';
        var tag=h('div','dk-tag','<div class="r"><span class="ln">'+esc(cfg.eyebrow(it))+(it.code?' &middot; No. '+esc(it.code):'')+'</span>'+(it.status?'<span class="pill '+esc(it.statusClass)+'">'+esc(it.status)+'</span>':'')+'</div><p class="t">'+esc(it.name)+'</p><p class="s">'+esc(cfg.sub(it))+'</p><button type="button" class="dk-open"><span class="c"><i></i>'+esc(it.colour)+'</span><span class="g">'+(cfg.openLabel?esc(cfg.openLabel(it)):(it.price||cfg.price)+' &middot; Open')+'</span></button>');
        face.addEventListener('pointerdown',function(e){ lastPointer=e.pointerType||'mouse'; if(touchLike()&&!state.touch){ state.touch=true; hintText(); } });
        face.addEventListener('keydown',function(){ lastPointer='key'; });
        face.addEventListener('focus',function(){ if(rolls) dk.scrollLeft=0; if(!touchLike()) activate(i); else if(rolls) shiftTo(i); });
        face.addEventListener('click',function(){ if(touchLike()&&state.active!==i){ activate(i); shiftTo(i); return; } openIt(i); });
        tag.querySelector('.dk-open').addEventListener('click',function(){ openIt(i); });
        card.appendChild(face); card.appendChild(tag); row.appendChild(card); cards.push(card);
      });
      var st=startFor(); if(state.active<0&&st!=null&&L[st]) state.active=st;
      foot.querySelector('.cnt').innerHTML=L.length+' '+cfg.noun+(L.length>1?'s':'')+' &middot; '+(typeof cfg.footNote==='function'?cfg.footNote(state.line,L):cfg.footNote);
      Object.keys(chips).forEach(function(k){ var on=k===state.line; chips[k].classList.toggle('on',on); chips[k].setAttribute('aria-pressed',on); });
      hintText(); paint(); if(rolls&&state.active>=0) shiftTo(state.active);
    }
    function touchLike(){ return lastPointer==='touch'||lastPointer==='pen'; }
    function startFor(){ var st=cfg.start; if(st!=null&&typeof st==='object') st=st[state.line]; return st==null?null:st; }   // the card a line opens on: one index for every line, or {line:index}
    function hintText(){ hint.textContent=rolls?(state.touch?'Drag across the deck to roll through the '+cfg.noun+'s · tap one to open':'Drag the deck to roll through the '+cfg.noun+'s · click one to open'):(state.touch?'Drag a finger across the tabs to pull a '+cfg.noun+' forward · tap it to open':'Run across the tabs to pull a '+cfg.noun+' forward · click it to open'); }
    // rolling deck: slide the strip so card i sits in the middle of the screen
    function shiftTo(i){ if(!rolls||i<0) return; var cs=getComputedStyle(dk), left=parseFloat(cs.paddingLeft)||0; row.style.transform='translateX('+Math.round(dk.clientWidth/2-(left+padL()+i*curStep+140))+'px)'; }
    // which card's tab sits under a point on a fitted deck: tabs are laid out every step px from the row's left edge (the spread collections deck has no overlap, so the element under the point is the card)
    function indexAt(cx,cy){
      var n=cards.length; if(!n) return -1;
      if(cfg.cls==='deck-coll'){ var el=document.elementFromPoint(cx,cy), c=el&&el.closest('.dk'); return c?cards.indexOf(c):-1; }
      var r=row.getBoundingClientRect(), x=cx-r.left-padL(), s=curStep||1;
      if(x<0||x>280+(n-1)*s) return -1;
      var i=Math.floor(x/s), a=state.active;
      if(shifted&&a>=0){ if(i>a) i=Math.max(a,Math.floor((x-14)/s)); else if(i<a) i=Math.min(a,Math.floor((x+8)/s)); }
      return Math.min(n-1,Math.max(0,i));
    }
    function inBand(cy){ var r=row.getBoundingClientRect(); return cy>=r.top-56&&cy<=r.bottom+6; }   // the cards, not the tag above the lifted one
    function clampI(i){ return Math.max(0,Math.min(cards.length-1,i)); }
    // the mouse running across the tabs of a fitted deck pulls the card under it forward
    dk.addEventListener('pointermove',function(e){
      if(e.pointerType==='touch'||e.pointerType==='pen'||drag) return;
      if(e.pointerType==='mouse') lastPointer='mouse'; if(touchLike()||rolls) return;
      if(inBand(e.clientY)){ var i=indexAt(e.clientX,e.clientY); if(i>=0) activate(i); }
    });
    // a drag: on a fitted deck the finger pulls the card under it forward; on a rolling deck any pointer rolls the cards by distance
    dk.addEventListener('pointerdown',function(e){
      var touch=e.pointerType==='touch'||e.pointerType==='pen'; if(!touch&&!rolls) return; if(!touch&&e.button!==0) return;
      cancelAnimationFrame(fling); fling=0;
      drag={id:e.pointerId,x:e.clientX,y:e.clientY,on:false,from:state.active>=0?state.active:0,last:e.clientX,t:e.timeStamp,v:0};
    });
    function dragMove(e){
      if(!drag||e.pointerId!==drag.id) return;
      if(!drag.on){ var dx=e.clientX-drag.x, dy=e.clientY-drag.y; if(Math.abs(dx)<8&&Math.abs(dy)<8) return; if(Math.abs(dy)>Math.abs(dx)){ drag=null; return; } drag.on=true; }
      var dt=e.timeStamp-drag.t; if(dt>0){ drag.v=0.6*drag.v+0.4*(e.clientX-drag.last)/dt; } drag.last=e.clientX; drag.t=e.timeStamp;
      if(rolls){ var k=clampI(drag.from-Math.round((e.clientX-drag.x)/ROLL_PX)); activate(k); shiftTo(k); e.preventDefault(); return; }
      var j=indexAt(e.clientX,e.clientY); if(j>=0) activate(j);
    }
    function dragEnd(e){
      if(!drag||(e&&e.pointerId!==drag.id)) return; var d=drag; drag=null;
      if(!rolls||!d.on||e.type==='pointercancel') return;
      // a flick keeps rolling a little: the velocity decays and each ROLL_PX px of virtual travel is one more card
      var v=d.v, travel=0, prev=state.active, t=performance.now();
      if(Math.abs(v)<0.25) return;
      (function step(){ var now=performance.now(), dt=Math.min(40,now-t); t=now; travel+=v*dt; v*=Math.pow(0.9,dt/16);
        var k=clampI(prev-Math.round(travel/ROLL_PX)); if(k!==state.active){ activate(k); shiftTo(k); }
        if(Math.abs(v)>0.05&&k>0&&k<cards.length-1) fling=requestAnimationFrame(step); else fling=0; })();
    }
    window.addEventListener('pointermove',dragMove,{passive:false}); window.addEventListener('pointerup',dragEnd); window.addEventListener('pointercancel',dragEnd);
    var rt=0; window.addEventListener('resize',function(){ clearTimeout(rt); rt=setTimeout(function(){ if(state.open>=0) return; var lay=layoutFor(list().length); if(lay.step!==curStep||lay.rolls!==rolls) build(); },150); });
    function paint(){
      dk.classList.toggle('live',state.active>=0);
      cards.forEach(function(c,i){ c.classList.toggle('on',i===state.active); c.classList.toggle('after',state.active>=0&&i>state.active); c.classList.toggle('before',state.active>=0&&i<state.active); c.style.zIndex=i===state.active?200:i+1; });
    }
    function activate(i){ if(state.active!==i){ state.active=i; paint(); } }
    function setLine(l){ if(state.line===l){ if(state.open>=0) closeIt(); return; } state.line=l; state.active=-1; state.open=-1; open.hidden=true; dk.hidden=false; foot.hidden=false; build(); }
    dk.addEventListener('mouseleave',function(){ if(!rolls&&lastPointer==='mouse'&&state.active>=0){ var st=startFor(); state.active=st!=null?st:-1; paint(); } });

    function openIt(i){ var it=list()[i]; track(cfg.openEvent,{item:it.slug,via:'deck'}); if(cfg.go){ cfg.go(it); return; } state.open=i; state.view=cfg.defaultView(it); render(); }
    function closeIt(){ var i=state.open; state.open=-1; open.hidden=true; dk.hidden=false; foot.hidden=false; state.active=i; paint(); shiftTo(i); var f=cards[i]&&cards[i].querySelector('.dk-face'); if(f) f.focus({preventScroll:true}); }
    function render(){
      var L=list(), it=L[state.open]; if(!it) return;
      dk.hidden=true; foot.hidden=true; open.hidden=false;
      var v=state.view, src=v==='art'?it.art:v==='back'?it.back:it.front, s=it.site||{};
      var views=[['front','Front']]; if(it.back) views.push(['back','Back']); if(it.art) views.push(['art','The art']);
      open.innerHTML='<div class="sh-open-bar"><button type="button" class="txt sh-back">&larr; Back to the deck</button><div class="sh-nav"><span class="pos">'+(state.open+1)+' of '+L.length+'</span><button type="button" class="arrow sh-prev" aria-label="Previous">&lsaquo;</button><button type="button" class="arrow sh-next" aria-label="Next">&rsaquo;</button></div></div>'
        +'<div class="sh-panel" style="--hex:'+it.hex+'"><div class="sh-detail"><div class="sh-view"><button type="button" class="big'+(v==='art'?' art':'')+'" aria-label="Open the full-size image"><img src="'+esc(src)+'" alt="'+esc(it.name+', '+it.colour.toLowerCase()+', '+v)+'"></button>'
        +'<div class="row">'+(views.length>1?'<span class="sh-flip" role="group" aria-label="Show front, back or the art">'+views.map(function(w){ return '<button type="button" data-v="'+w[0]+'" class="'+(v===w[0]?'on':'')+'" aria-pressed="'+(v===w[0])+'">'+w[1]+'</button>'; }).join('')+'</span>':'')+'<span class="cap">'+esc(cfg.caption(it,v))+'</span></div></div>'
        +'<div class="sh-info"><p class="eyebrow">'+esc(cfg.eyebrow(it))+(it.code?' &middot; No. '+esc(it.code):'')+'</p><h3>'+esc(it.name)+'</h3>'
        +(it.site?'<p class="where">'+flag(s.flag==='us')+'<span>'+esc(s.place||'')+(s.water?' · '+esc(s.water):'')+'</span></p><p class="coords mono">'+esc(s.coords||'')+'</p>':'<p style="color:var(--muted);max-width:48ch">'+esc(cfg.blurb(it))+'</p>')
        +'<dl class="specs">'+cfg.specs(it).map(function(r){return '<dt>'+r[0]+'</dt><dd>'+r[1]+'</dd>';}).join('')+'</dl>'
        +(s.fact&&cfg.facts?'<p class="fact">'+esc(s.fact)+'</p>':'')
        +'<div class="cta"><a class="btn" href="'+esc(cfg.contact||'#contact')+'" data-umami-event="deck-launch-news">'+(it.statusClass==='completed'?'Sample print':'Coming soon')+' &middot; get launch news</a>'+(cfg.custom===false?'':'<a class="btn ghost" href="'+esc(it.custom)+'" data-umami-event="deck-custom">Make it yours</a>')+(it.guide?'<a class="txt" href="'+esc(it.guide)+'" data-umami-event="deck-guide">Site guide &rarr;</a>':'')+'</div></div></div></div>';
      open.querySelector('.sh-back').addEventListener('click',closeIt);
      open.querySelector('.sh-prev').addEventListener('click',function(){ state.open=(state.open-1+L.length)%L.length; state.view=cfg.defaultView(list()[state.open]); render(); });
      open.querySelector('.sh-next').addEventListener('click',function(){ state.open=(state.open+1)%L.length; state.view=cfg.defaultView(list()[state.open]); render(); });
      open.querySelectorAll('.sh-flip button').forEach(function(b){ b.addEventListener('click',function(){ state.view=b.dataset.v; render(); }); });
      open.querySelector('.big').addEventListener('click',function(){
        var lb=document.getElementById('sh-lb'), im=document.getElementById('sh-lb-img'), c=document.getElementById('sh-lb-cap'); if(!lb) return;
        im.src=src; im.alt=it.name+', '+v; c.textContent=it.cap+' · '+(v==='art'?'the art':v); if(lb.showModal) lb.showModal(); else window.open(src,'_blank');
      });
      open.querySelector('.sh-open-bar').scrollIntoView({block:'nearest'});
    }
    open.addEventListener('contextmenu',function(e){ if(e.target.closest('.big')) e.preventDefault(); });
    sec.addEventListener('click',function(e){ var a=e.target.closest('a[href="#shirts"],a[href="#hats"]'); if(a&&a.dataset.deckLine) setLine(a.dataset.deckLine); });
    document.querySelectorAll('a[data-deck-line][href="#'+sectionId+'"]').forEach(function(a){ a.addEventListener('click',function(){ setLine(a.getAttribute('data-deck-line')); }); });
    build();
    // a line named in the URL hash opens that line: /off-world/#offworld-dark, /aquatic-comic/#aquatic-buddy-check
    function fromHash(){ var k=(location.hash||'').replace(/^#/,''); if(!k||!cfg.lines.some(function(l){return l[0]===k;})) return false; setLine(k); return true; }
    if(fromHash()) setTimeout(function(){ wrap.scrollIntoView({block:'start'}); },0);
    window.addEventListener('hashchange',function(){ if(fromHash()) wrap.scrollIntoView({block:'start'}); });
  }
  DS.deck=deck; DS.esc=esc; DS.MARK=MARK;


  // The shirts deck: one config for every line, so a collection page passes only the lines it holds.
  DS.SHIRT_LINES=[['plates','Signature Series'],['dark','Signature Series Dark'],['certifiedish','Certified-ish'],['certifiedish-dark','Certified-ish Dark'],['offworld','Off-World Hunt Club'],['offworld-dark','Off-World Hunt Club Dark'],['n73','1N73LL1G3NC3'],['aquatic-boat-banter','Aquatic Comic · Boat Banter'],['aquatic-self-logged','Aquatic Comic · Self-Logged'],['aquatic-buddy-check','Aquatic Comic · Buddy Check'],['aquatic-buddy-system','Aquatic Comic · Buddy System'],['aquatic-till-surface','Aquatic Comic · Till Surface Do Us Part'],['aquatic-master-class','Aquatic Comic · Master Class']];
  DS.shirtsCfg=function(o){ o=o||{}; var lines=o.lines||DS.SHIRT_LINES, step={}; lines.forEach(function(l){ step[l[0]]=(l[0]==='plates'||l[0]==='dark')?64:44; });
   return {
    lines:lines, step:step, noun:'shirt', price:'$42', openEvent:'shirt-open', contact:o.contact||'#contact',
    footNote:'one garment colour each &middot; Comfort Colors 1717', facts:true,
    eyebrow:function(it){ return it.line==='plates'?'Signature Series':it.line==='dark'?'Signature Series Dark':it.line==='offworld'?'Off-World Hunt Club':it.line==='offworld-dark'?'Off-World Hunt Club Dark':it.line==='n73'?'1N73LL1G3NC3':it.line.indexOf('aquatic-')===0?'Aquatic Comic':it.line==='certifiedish-dark'?'Certified-ish Dark':'Certified-ish'; },
    sub:function(it){ return it.site?it.site.place+(it.line==='dark'?' · dark line':''):it.line.indexOf('offworld')===0||it.line==='n73'||it.line.indexOf('aquatic-')===0?it.text:it.line==='certifiedish-dark'?'Certified-ish back print · white ink · DS mark':'Certified-ish back print · DS mark'; },
    blurb:function(it){ return it.line.indexOf('aquatic-')===0?'Dive-deck humour in IM Fell: the DS mark over the slogan on the left chest, the joke on the back, its punch words in red. White and red ink on a dark tee.':it.line==='n73'?'A message in plain sight: read the bold characters, the dials or the code and it speaks. One full-front print, on a garment colour chosen for its theme.':it.line.indexOf('offworld')===0?'One line in the hunters\u2019 script across the back, translated underneath with one word in red; the DS mark carries that word on the chest, in glyphs.':'One tongue-in-cheek diagram for the specialty in your logbook, printed full size on the back.'; },
    defaultView:function(it){ return it.line.indexOf('certifiedish')===0||it.line.indexOf('offworld')===0||it.line.indexOf('aquatic-')===0?'back':'front'; },
    caption:function(it,v){ var sig=it.line==='plates', dk=it.line==='dark'; return v==='art'?(sig||dk?'The back print · plate, facts, species and water · watermarked':it.line==='n73'?'Watermarked preview of the front print':it.line.indexOf('aquatic-')===0?'Watermarked preview of the chest lockup and the back print':'Watermarked preview of the back print'):v==='back'?(sig?'Back · worn, photographed':dk?'Back · mockup on the photographed shirt, white ink':it.line==='offworld-dark'||it.line==='certifiedish-dark'?'Back · mockup, white ink':'Back · mockup'):(sig?'Front · worn, photographed':dk?'Front · mockup on the photographed shirt, white ink':it.line==='offworld-dark'?'Front · mockup, DS mark and the word in glyphs on the chest, white ink':it.line==='n73'?'Front · mockup, the full-front print':it.line.indexOf('aquatic-')===0?'Front · mockup, the DS mark over the slogan, left chest':it.line==='offworld'?'Front · mockup, DS mark and the word in glyphs on the chest':it.line==='certifiedish-dark'?'Front · mockup, DS mark along the sleeve in white and red':'Front · mockup, DS mark along the sleeve'); },
    specs:function(it){ var sw='<span class="sw"></span>Comfort Colors 1717, garment-dyed · '+esc(it.colour); if(it.line.indexOf('aquatic-')===0) return [['Front','The DS mark over the slogan, left chest, 3.75 in'],['Back','The joke, white with the punch words in red, 11 in wide'],['Shirt',sw],['Ink','Water-based white and red, printed by hand'],['Price',(it.line==='aquatic-self-logged'||it.line==='aquatic-buddy-check'||it.line==='aquatic-buddy-system'||it.line==='aquatic-till-surface'||it.line==='aquatic-master-class')?'$47 · $50 in 2XL and 3XL, with the name or names you choose':'$42 · $45 in 2XL and 3XL']]; if(it.line==='n73') return [['Front','The design, full front, about 11.5 in wide'],['Back','Plain'],['Shirt',sw],['Ink','Water-based, in the colours shown, printed by hand'],['Price','$42 · $45 in 2XL and 3XL']]; if(it.line.indexOf('offworld')===0) return [['Back','The line in the off-world script, 12 × 16 in, translated beneath it with the punch word in red'],['Chest','The DS mark with the punch word in glyphs, left chest'],['Shirt',sw],['Ink',it.line==='offworld-dark'?'Water-based white and red, printed by hand':'Water-based black and red, printed by hand'],['Price','$42 · $45 in 2XL and 3XL']]; if(it.line==='dark') return [['Back','Full site illustration with facts, species and water conditions'],['Chest','Site name, dive flag and GPS coordinates'],['Sleeve','Signature shark mark'],['Shirt',sw],['Ink','Water-based white, printed by hand · the flag in colour'],['Price','$42 · $45 in 2XL and 3XL']]; return it.line==='plates'
      ?[['Back','Full site illustration with facts, species and water conditions'],['Chest','Site name, dive flag and GPS coordinates'],['Sleeve','Signature shark mark'],['Shirt',sw],['Ink','Water-based black, printed by hand'],['Price','$42 · $45 in 2XL and 3XL']]
      :[['Back','The full Certified-ish diagram, printed full size'],['Mark','DS mark along the sleeve · the shark stays on the Signature Series'],['Shirt',sw],['Ink',it.line==='certifiedish-dark'?'Water-based white, printed by hand · the DS mark in white and red':'Water-based black, printed by hand'],['Price','$42 · $45 in 2XL and 3XL']]; }
   };
  };

  // The sticker packs deck: 37 kiss-cut sheets in three lines; a card opens the sheet proof and what is on it
  DS.packsCfg=function(o){ o=o||{}; var NAME={set:'Achievement set',themed:'Themed',classic:'Classic die-cuts',brand:'Brand set'};
   function inside(it){ return it.sub.replace(/\s*·\s*\$\d+\s*$/,''); }
   function fillers(it){ return /fillers/.test(it.cap||''); }
   return {
    lines:o.lines||[['set','Achievement set'],['themed','Themed'],['classic','Classic die-cuts'],['brand','Brand']], step:{set:64,themed:36,classic:64,brand:64}, noun:'pack', price:'$10', openEvent:'pack-open', cls:'deck-packs', custom:false, contact:o.contact||'/#contact',
    start:{set:0},   // the deck opens on the Achievement set, the opener
    footNote:function(line){ return line==='set'?'all twelve badges, the Achievement Hunter and 100% Complete badges and three DS marks on one 5.83 &times; 8.27 in sheet':'three kiss-cut stickers on one 4 &times; 6 in sheet, most with small fillers'; }, facts:false,
    eyebrow:function(it){ return NAME[it.line]||'Sticker pack'; },
    sub:function(it){ return it.line==='set'?'All twelve badges + five extras':inside(it); },
    blurb:function(it){ return it.text||'Three kiss-cut stickers on one sheet. Peel them one at a time for the tank, the dive box, the laptop and the logbook.'; },
    defaultView:function(){ return 'front'; },
    caption:function(it){ return it.line==='set'?'The sheet · proof of the full set, 5.83 × 8.27 in':'The sheet · proof of the three stickers'+(fillers(it)?' and the fillers':'')+', 4 × 6 in'; },
    specs:function(it){ var c=inside(it); if(it.line==='set') return [['Sheet','5.83 × 8.27 in kiss-cut sheet, seventeen stickers'],['Badges','Freshly Certified · Not On My Watch · Master Diver · Along For The Ride · Hover Mode · Spicy Air · Photobombed · Lost & Found · Dual Wield · Friendly NPC · Bestiary · High Score'],['Extras','Achievement Hunter · 100% Complete · the seal · the horizontal logo · Do A Little Scuba'],['Vinyl','Printed vinyl, glossy film, waterproof'],['Price',it.price||'$15']];
      return [['Sheet','4 × 6 in kiss-cut sheet, three stickers'+(fillers(it)?' and small fillers':'')],['Stickers',/^three stickers$/i.test(c)?'Three, drawn for the pack':esc(c)],['Vinyl','Printed vinyl, glossy film, waterproof'],['Mark','The DS mark on every sticker'],['Price',it.price||'$10']]; }
   };
  };

  // The photo viewer: every .sh-grid (shirts, hats, stickers) opens its photos in the #sh-lb dialog
  DS.lightbox=function(){
  var lb=document.getElementById('sh-lb'), im=document.getElementById('sh-lb-img'), cap=document.getElementById('sh-lb-cap'); if(!lb) return;
  lb.querySelector('.lb-x').addEventListener('click',function(){lb.close();});
  lb.addEventListener('click',function(e){ if(e.target===lb) lb.close(); });
  lb.addEventListener('close',function(){ im.removeAttribute('src'); });
  document.querySelectorAll('.sh-grid').forEach(function(grid){
  grid.querySelectorAll('.sh-flip button').forEach(function(b){
    b.addEventListener('click',function(){
      var fig=b.closest('.sh'), btn=fig.querySelector('.sh-img'), img=btn.querySelector('img'), side=b.dataset.side;
      var full=btn.dataset[side]; if(!full) return;
      img.src=full.replace('.webp','-t.webp'); btn.dataset.side=side;
      img.alt=img.alt.replace(/: (chest|back) print[^]*$/, side==='back' ? ': back print with the full site illustration, facts, species and water notes' : ': chest print with dive flag, site name and coordinates');
      fig.querySelectorAll('.sh-flip button').forEach(function(x){var on=x===b;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on);});
    });
  });
  grid.querySelectorAll('.sh-img').forEach(function(btn){
    btn.addEventListener('click',function(){
      var side=btn.dataset.side||'front', full=btn.dataset[side]||btn.dataset.front;
      im.src=full; im.alt=btn.querySelector('img').alt; cap.textContent=btn.dataset.cap+(btn.dataset.back?(side==='back'?' · back':' · front'):'');
      if(lb.showModal) lb.showModal(); else window.open(full,'_blank');
    });
  });
  grid.addEventListener('contextmenu',function(e){ if(e.target.closest('.sh-img')) e.preventDefault(); });
  });
  };

  // The designs grid: chips filter by status (data-f), line (data-l) or subset (data-s); a tap opens the full print in the viewer
  DS.designs=function(){
  var grid=document.getElementById('dz-grid'); if(!grid) return;
  var st='all', ln='', sb='', q='', none=document.querySelector('.dz-none');
  // the words on each design, for the search box: its name and subtitle, the alt text and caption, and the text on its shirt card
  var text={}; document.querySelectorAll('figure.sh[data-slug][data-text]').forEach(function(f){ text[f.dataset.slug]=f.dataset.text; });
  grid.querySelectorAll('.dz').forEach(function(f){
    var b=f.querySelector('.dz-img'), img=f.querySelector('img'), slug=b&&b.getAttribute('data-umami-event-design');
    f.dataset.q=(f.textContent+' '+(img?img.alt:'')+' '+(b&&b.dataset.cap||'')+' '+(f.dataset.sub||'').replace(/-/g,' ')+' '+(slug&&text[slug]||'')).replace(/\s+/g,' ').toLowerCase();
  });
  // plus, once someone searches, the words read off the artwork itself (js/designs.json, built by tools/line_pages.py)
  var extra={}, extraLoad=null;
  function loadExtra(){ if(!extraLoad) extraLoad=fetch('/js/designs.json').then(function(r){ return r.json(); }).then(function(d){ d.forEach(function(x){ extra[x.slug]=x.q; }); apply(); }).catch(function(){}); return extraLoad; }
  function apply(){
    var words=q.split(/\s+/).filter(Boolean), shown=0;
    grid.querySelectorAll('.dz').forEach(function(f){
      var b=f.querySelector('.dz-img'), slug=b&&b.getAttribute('data-umami-event-design'), hay=f.dataset.q+' '+(slug&&extra[slug]||'');
      var hit=(st==='all'||f.dataset.status===st)&&(!ln||f.dataset.line===ln)&&(!sb||f.dataset.sub===sb)&&words.every(function(w){ return hay.indexOf(w)>=0; });
      f.hidden=!hit; if(hit) shown++;
    });
    if(none) none.hidden=shown>0;
  }
  var box=document.querySelector('.dz-bar .dz-q'), qt=0;
  if(box){ box.addEventListener('focus',loadExtra,{once:true}); box.addEventListener('input',function(){ loadExtra(); clearTimeout(qt); qt=setTimeout(function(){ q=box.value.trim().toLowerCase(); apply(); if(q.length>2) track('designs-search',{q:q}); },120); }); }
  document.querySelectorAll('.dz-bar .chip').forEach(function(b){
    b.addEventListener('click',function(){
      if(b.dataset.f){ st=b.dataset.f; document.querySelectorAll('.dz-bar [data-f]').forEach(function(x){var on=x===b;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on);}); }
      else if(b.dataset.l){ ln=(ln===b.dataset.l)?'':b.dataset.l; document.querySelectorAll('.dz-bar [data-l]').forEach(function(x){var on=x.dataset.l===ln;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on);}); }
      else if(b.dataset.s){ sb=(sb===b.dataset.s)?'':b.dataset.s; document.querySelectorAll('.dz-bar [data-s]').forEach(function(x){var on=x.dataset.s===sb;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on);}); }
      apply();
    });
  });
  // Tap a design for the full back print, in the same viewer as the shirts
  var lb=document.getElementById('sh-lb'), im=document.getElementById('sh-lb-img'), cap=document.getElementById('sh-lb-cap');
  grid.querySelectorAll('button.dz-img[data-full]').forEach(function(btn){
    btn.addEventListener('click',function(){
      im.src=btn.dataset.full; im.alt=btn.dataset.cap; cap.textContent=btn.dataset.cap;
      if(lb.showModal) lb.showModal(); else window.open(btn.dataset.full,'_blank');
    });
  });
  grid.addEventListener('contextmenu',function(e){e.preventDefault();});
  document.querySelectorAll('[data-count]').forEach(function(n){
    var c=grid.querySelectorAll('.dz[data-line="'+n.getAttribute('data-count')+'"]').length; if(c) n.textContent=c;
  });
  document.querySelectorAll('[data-show-line]').forEach(function(a){
    a.addEventListener('click',function(){
      var want=a.getAttribute('data-show-line');
      var all=document.querySelector('.dz-bar [data-f="all"]'); if(all && st!=='all') all.click();
      var chip=document.querySelector('.dz-bar [data-l="'+want+'"]'); if(chip && ln!==want) chip.click();
    });
  });
  grid.addEventListener('dragstart',function(e){e.preventDefault();});
  // a design named in the URL hash scrolls into view and is marked: /off-world/#d-ow-cloaked (the home-page search links this way)
  function toHash(){ var m=(location.hash||'').match(/^#d-([a-z0-9-]+)$/); if(!m) return; var b=grid.querySelector('[data-umami-event-design="'+m[1]+'"]'); if(!b) return;
    if(box&&q){ box.value=''; q=''; apply(); }
    var f=b.closest('.dz'); grid.querySelectorAll('.dz.hit').forEach(function(x){ x.classList.remove('hit'); }); f.classList.add('hit');
    setTimeout(function(){ f.scrollIntoView({block:'center'}); try{ b.focus({preventScroll:true}); }catch(e){} },50); }
  toHash(); window.addEventListener('hashchange',toHash);
  };
  return DS;
})();
