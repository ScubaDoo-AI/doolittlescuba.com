#!/usr/bin/env python3
"""Shop-partner source tracking (D17, Eric 16 Nov 2026).

A partner's QR card or link opens doolittlescuba.com/?src=shop-<name>. This script stamps a small inline
script into every content page that:
  - remembers the src for 30 days (localStorage, key ds-src; only [a-z0-9-] values are accepted);
  - appends utm_source=shop-<name>&utm_medium=partner to every link and form that goes to
    https://shop.doolittlescuba.com, so Shopify's order "customer journey" credits the shop;
  - sends one Umami event, partner, with the src, so the site side can be reported too.

Usage:  python3 tools/partner_src.py          # stamp or restamp every page (idempotent, uses SRC markers)
Run it after any page generator, like tools/status_flag.py. Redirect stubs are skipped.
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, END = '<!-- SRC:START -->', '<!-- SRC:END -->'
SHOP = 'https://shop.doolittlescuba.com'

JS = ("<script>(function(){try{var K='ds-src',D=30*864e5,q=new URLSearchParams(location.search),s=q.get('src'),now=Date.now();"
      "if(s&&/^[a-z0-9-]{1,40}$/.test(s)){localStorage.setItem(K,JSON.stringify({s:s,t:now}));}"
      "else{var r=JSON.parse(localStorage.getItem(K)||'null');s=r&&now-r.t<D?r.s:null;}"
      "if(!s)return;var u='utm_source='+encodeURIComponent(s)+'&utm_medium=partner';window.DS_SRC_UTM=u;"
      "function add(h){return h.indexOf('utm_source=')>-1?h:h+(h.indexOf('?')>-1?'&':'?')+u;}"
      "function stamp(){document.querySelectorAll('a[href^=\"" + SHOP + "\"]').forEach(function(a){a.href=add(a.href);});"
      "document.querySelectorAll('form[action^=\"" + SHOP + "\"]').forEach(function(f){f.action=add(f.action);});}"
      "stamp();document.addEventListener('DOMContentLoaded',function(){stamp();if(window.umami&&umami.track)umami.track('partner',{src:s});});"
      "document.addEventListener('click',function(e){var a=e.target&&e.target.closest&&e.target.closest('a[href^=\"" + SHOP + "\"]');if(a)a.href=add(a.href);},true);"
      "}catch(e){}})();</script>")

BLOCK = START + JS + END


def stamp(path):
    with open(path, encoding='utf-8') as f:
        h = f.read()
    if 'http-equiv="refresh"' in h or '</body>' not in h:
        return False
    if START in h:
        h2 = re.sub(re.escape(START) + '.*?' + re.escape(END), lambda m: BLOCK, h, count=1, flags=re.S)
    else:
        h2 = h.replace('</body>', BLOCK + '\n</body>', 1)
    if h2 != h:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(h2)
    return True


if __name__ == '__main__':
    pages = sorted(p for p in glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True) if '/.git/' not in p and '/node_modules/' not in p)
    n = sum(1 for p in pages if stamp(p))
    print(f'partner src block on {n} pages')
