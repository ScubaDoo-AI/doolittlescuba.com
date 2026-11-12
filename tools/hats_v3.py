#!/usr/bin/env python3
"""Hats, blueprint v3 (11 Nov 2026): every cap embroidered on three sides — the DTF site front is gone.
Copies the embroidered-front renders into img/hats/dark/ (1200 px WebP + 600 px thumbs) and rewrites the hats copy,
the figure data and the spec sheet in index.html; the "Site block" label in js/deck.js becomes "Site front".
Home Port stays a custom order: the buyer's port and coordinates are embroidered to order.
Usage: tools/hats_v3.py renders/caps-2026-11-11    (then run tools/bust.py)"""
import os, re, sys, glob
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
out = os.path.join(ROOT, 'img', 'hats', 'dark')
n = 0
for f in sorted(glob.glob(os.path.join(src, 'cap-dark-*.jpg'))):
    stem = os.path.basename(f)[:-4]
    im = Image.open(f).convert('RGB')
    im.resize((1200, 1200), Image.LANCZOS).save(os.path.join(out, stem + '.webp'), quality=84, method=6)
    im.resize((600, 600), Image.LANCZOS).save(os.path.join(out, stem + '-t.webp'), quality=82, method=6)
    n += 1
print(n, 'renders ->', 2 * n, 'images in img/hats/dark/')


def swap(h, old, new, count=1):
    k = h.count(old); assert k == count, f'{k} of expected {count}: {old[:70]}…'
    return h.replace(old, new)


p = os.path.join(ROOT, 'index.html'); h = open(p, encoding='utf-8').read(); n0 = len(h)
# intro
h = swap(h, "Every cap comes embroidered — the DS mark small on the left side, “Do - A - Little Scuba” across the back — and the site caps get their chest block printed in white on the front when you order. Home Port is made with your own port and coordinates; the four brand caps are embroidered front, side and back.",
         "Every cap is embroidered on three sides — the site front (dive flag, name and coordinates) across the front panels, the DS mark small on the left side, “Do - A - Little Scuba” arched across the back. Nothing is printed. Home Port is made to order with your own port and coordinates; the four brand caps carry the marks instead of a site.")
# note
h = swap(h, "Site caps are $35 (embroidered cap, site block printed to order), brand caps $40 (embroidered throughout).",
         "Site caps are $35, brand caps $40 — all embroidered.")
# figure data: the 14 site caps and Home Port were DTF fronts
h = swap(h, 'data-price="$35" data-finish="dtf"', 'data-price="$35" data-finish="embroidered"', 15)
# alt texts
h = swap(h, "the site block in white on the front, DS mark embroidered on the side",
         "the site front embroidered across the front panels, DS mark on the side, tagline on the back", 14)
h = swap(h, "your port and coordinates printed in white on the front, DS mark embroidered on the side",
         "your port and coordinates embroidered to order on the front, DS mark on the side, tagline on the back")
# spec sheet
old = re.search(r'specs:function\(it\)\{.*?return rows; \}', h).group(0)
new = ("specs:function(it){ var q=it.parts, hp=it.slug==='cap-dark-home-port', thread=/maroon/i.test(it.colour||'')?'white and navy':'white and red'; "
       "var rows=[['Front',hp?'Your home port — name, dive flag and coordinates — embroidered to order':(DS.MARK[q.cf]||'—')+', embroidered'],"
       "['Side',q.cs&&q.cs!=='none'?(DS.MARK[q.cs]||q.cs)+', embroidered in '+thread+(q.csp?', '+q.csp+' side':''):'plain'],"
       "['Back',q.cb&&q.cb!=='none'?(DS.MARK[q.cb]||q.cb)+', embroidered in white':'plain'],"
       "['Cap','<span class=\"sw\"></span>Flexfit 6277 structured fitted cap, closed stretch back · '+DS.esc(it.colour)],['Sizes','S/M (6¾–7¼) · L/XL (7⅛–7⅝)'],"
       "['Finish','Embroidered throughout — raised satin stitch'],"
       "['Price',it.price||'$35']]; if(hp){rows.splice(5,0,['Custom','made to order once your coordinates are confirmed']);} return rows; }")
h = h.replace(old, new)
assert 'DTF' not in h and 'printed to order' not in h, 'a DTF reference is left on the home page'
open(p, 'w', encoding='utf-8').write(h)
print('index.html', n0, '->', len(h))

p = os.path.join(ROOT, 'js', 'deck.js'); j = open(p, encoding='utf-8').read()
j = swap(j, "site:'Site block: name, dive flag and coordinates'", "site:'Site front: dive flag, site name and coordinates'")
open(p, 'w', encoding='utf-8').write(j); print('js/deck.js: Site block -> Site front')
