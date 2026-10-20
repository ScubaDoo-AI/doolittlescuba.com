/* Doolittle Scuba dive map. Needs Leaflet loaded first.
   Site data comes from the <script type="application/json" id="sites-data"> block that
   tools/build_sites.py writes into the page. Edit tools/sites.json, not this file. */
(function(){
  var FLAGS={
    us:'<svg viewBox="0 0 26 18" aria-hidden="true"><rect width="26" height="18" fill="#C8202A"/><path d="M0 0h4.5L26 14.5V18h-4.5L0 3.5z" fill="#fff"/></svg>',
    intl:'<svg viewBox="0 0 26 18" aria-hidden="true"><path d="M0 0h13v18H0z" fill="#fff"/><path d="M13 0h13l-6 9 6 9H13z" fill="#1F4FA3"/></svg>'
  };
  var STATUS={available:'Coming soon',finished:'Art finished',progress:'In progress'};
  var REGIONS=[
    {name:'Southeast US',test:function(s){return s.lng<-60&&s.lat>15;}},
    {name:'Red Sea',test:function(s){return s.lng>30&&s.lng<45;}},
    {name:'Indonesia',test:function(s){return s.lng>94&&s.lng<142;}},
    {name:'Fiji',test:function(s){return s.lng>170||s.lng<-170;}}
  ];
  function esc(t){return String(t==null?'':t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function dark(){
    var t=document.documentElement.getAttribute('data-theme');
    if(t)return t==='dark';
    return !!(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches);
  }
  function tiles(){
    // OpenStreetMap's own tiles: free with attribution, no key. Muted to the chart palette in divemap.css.
    return L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
      maxZoom:18,
      attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });
  }
  function icon(s){
    return L.divIcon({className:'pin pin-'+s.flag,html:'<span class="pin-flag">'+FLAGS[s.flag]+'</span>',iconSize:[30,22],iconAnchor:[15,22],popupAnchor:[0,-20]});
  }
  function popup(s,linkGuide){
    return '<div class="pop">'+
      '<p class="pop-st pop-'+esc(s.status)+'">'+esc(STATUS[s.status]||'')+'</p>'+
      '<h3>'+esc(s.name)+'</h3>'+
      (s.place?'<p class="pop-where">'+esc(s.place)+(s.water?' · '+esc(s.water):'')+'</p>':'')+
      '<p class="pop-c">'+(s.approx?'&asymp; ':'')+esc(s.coords)+(s.approx?' <span class="pop-ap">approx.</span>':'')+'</p>'+
      (s.fact?'<p class="pop-f">'+esc(s.fact)+'</p>':'')+
      (linkGuide?'<a class="pop-a" data-umami-event="map-guide" data-umami-event-site="'+esc(s.slug)+'" href="/sites/'+esc(s.slug)+'/">Site guide &rarr;</a>':'')+
    '</div>';
  }
  function make(el,opts){
    var map=L.map(el,{scrollWheelZoom:false,worldCopyJump:true,zoomControl:true,minZoom:1});
    var layer=tiles().addTo(map);
    function retheme(){map.removeLayer(layer);layer=tiles().addTo(map);}
    if(window.matchMedia){var mq=matchMedia('(prefers-color-scheme: dark)');(mq.addEventListener?mq.addEventListener('change',retheme):mq.addListener(retheme));}
    new MutationObserver(retheme).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
    // Let the page scroll on touch; zoom with buttons or two fingers.
    map.on('focus',function(){map.scrollWheelZoom.enable();});
    map.on('blur',function(){map.scrollWheelZoom.disable();});
    return map;
  }
  function data(){
    var n=document.getElementById('sites-data');
    try{return JSON.parse(n.textContent).filter(function(s){return typeof s.lat==='number';});}catch(e){return [];}
  }

  window.DiveMap={
    // Full map with every pinned site and region buttons.
    all:function(el,jumpEl){
      if(!window.L||!el)return;
      var sites=data(), map=make(el), markers={}, group=[];
      // Sites a mile apart (Black Bart, Bridge Span 14) share a numbered cluster that splits on tap.
      var layer=L.markerClusterGroup ? L.markerClusterGroup({
        maxClusterRadius:36, showCoverageOnHover:false, spiderfyOnMaxZoom:true,
        iconCreateFunction:function(c){return L.divIcon({className:'pin-cluster',html:'<span>'+c.getChildCount()+'</span>',iconSize:[34,34]});}
      }) : map;
      sites.forEach(function(s){
        var m=L.marker([s.lat,s.lng],{icon:icon(s),title:s.name,keyboard:true}).bindPopup(popup(s,true),{maxWidth:280});
        m.addTo(layer); markers[s.slug]=m; group.push([s.lat,s.lng]);
      });
      if(layer!==map) map.addLayer(layer);
      function fit(pts){ if(!pts.length){map.setView([20,0],2);return;} if(pts.length===1){map.setView(pts[0],9);return;} map.fitBounds(pts,{padding:[36,36],maxZoom:9}); }
      fit(group);
      if(jumpEl){
        var btns=[{name:'All sites',pts:group}];
        REGIONS.forEach(function(r){
          var pts=sites.filter(r.test).map(function(s){return [s.lat,s.lng];});
          if(pts.length)btns.push({name:r.name,pts:pts});
        });
        if(btns.length>2){
          btns.forEach(function(b,i){
            var x=document.createElement('button'); x.type='button'; x.className='chip'+(i===0?' on':''); x.textContent=b.name;
            x.setAttribute('aria-pressed',i===0?'true':'false');
            x.setAttribute('data-umami-event','map-region'); x.setAttribute('data-umami-event-region',b.name);
            x.addEventListener('click',function(){
              jumpEl.querySelectorAll('.chip').forEach(function(c){c.classList.remove('on');c.setAttribute('aria-pressed','false');});
              x.classList.add('on'); x.setAttribute('aria-pressed','true'); map.closePopup(); fit(b.pts);
            });
            jumpEl.appendChild(x);
          });
        }
      }
      window.addEventListener('resize',function(){map.invalidateSize();});
      return map;
    },
    // Small map for one guide page.
    one:function(el,s){
      if(!window.L||!el||typeof s.lat!=='number')return;
      var map=make(el);
      L.marker([s.lat,s.lng],{icon:icon(s),title:s.name}).addTo(map).bindPopup(popup(s,false),{maxWidth:260});
      map.setView([s.lat,s.lng],10);
      return map;
    }
  };
})();
