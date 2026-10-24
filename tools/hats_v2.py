#!/usr/bin/env python3
"""Hats, blueprint v2 (24 Oct 2026): copy the new cap renders into img/hats/dark/ (1200 px WebP + 600 px thumbs)
and rewrite the hats copy and spec sheet in index.html for the embroidered-base model.
Usage: tools/hats_v2.py <renders-dir>    (then run tools/bust.py)"""
import os, re, sys, glob
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
out = os.path.join(ROOT, 'img', 'hats', 'dark')
for f in sorted(glob.glob(os.path.join(src, 'cap-dark-*.jpg'))):
    stem = os.path.basename(f)[:-4]
    im = Image.open(f).convert('RGB')
    im.resize((1200, 1200), Image.LANCZOS).save(os.path.join(out, stem + '.webp'), quality=84, method=6)
    im.resize((600, 600), Image.LANCZOS).save(os.path.join(out, stem + '-t.webp'), quality=82, method=6)
print('images written')

p = os.path.join(ROOT, 'index.html'); h = open(p, encoding='utf-8').read(); n0 = len(h)
# intro
h = h.replace("Every site gets its chest block in white across the front, the DS mark on the side and the tagline across the back; Home Port carries Newnan; four brand caps are embroidered.",
              "Every cap comes embroidered — the DS mark small on the left side, “Do - A - Little Scuba” across the back — and the site caps get their chest block printed in white on the front when you order. Home Port is made with your own port and coordinates; the four brand caps are embroidered front, side and back.")
# note
h = h.replace("DTF-printed caps are $35, embroidered $40.", "Site caps are $35 (embroidered cap, site block printed to order), brand caps $40 (embroidered throughout).")
# Home Port figure
h = h.replace('data-cap="Home Port cap · Black · Flexfit 6277 · mockup"', 'data-cap="Home Port cap · Black · Flexfit 6277 · made to order with your coordinates · mockup"')
h = h.replace('alt="Home Port cap, black Flexfit 6277: the site block in white on the front"', 'alt="Home Port cap, black Flexfit 6277: your port and coordinates printed in white on the front, DS mark embroidered on the side"')
h = h.replace('<span class="dz-t">Home Port cap</span>', '<span class="dz-t">Home Port — your coordinates</span>')
h = h.replace('<span class="dz-s">Black · Newnan, Georgia</span>', '<span class="dz-s">Black · made to order with your port and coordinates</span>')
h = h.replace('data-slug="cap-dark-home-port" data-code="HMP" data-colour="Black" data-hex="#212327" data-price="$35" data-finish="dtf"',
              'data-slug="cap-dark-home-port" data-code="HMP" data-colour="Black" data-hex="#212327" data-price="$35" data-finish="dtf" data-custom-order="1"')
# site cap alts
h = re.sub(r'(alt="[^"]*Flexfit 6277: the site block in white on the front)"', r'\1, DS mark embroidered on the side"', h)
# The Mark: side plain, back tagline (matches the store listing)
h = h.replace('site=black-bart&cf=dsmark&cs=dsmark&csp=left&cb=none', 'site=black-bart&cf=dsmark&cs=none&csp=left&cb=tagline')
# The Stack: side plain, back plain
h = h.replace('site=black-bart&cf=stack&cs=dsmark&csp=left&cb=none', 'site=black-bart&cf=stack&cs=none&csp=left&cb=none')
# spec sheet
old = "specs:function(it){ var q=it.parts, emb=it.finish==='embroidered'; return [['Front',(MARK[q.cf]||'—')+(emb?', embroidered':', in white')],['Side',q.cs&&q.cs!=='none'?(MARK[q.cs]||q.cs)+' in white and red'+(q.csp?', '+q.csp+' side':''):'plain'],['Back',q.cb&&q.cb!=='none'?(MARK[q.cb]||q.cb)+' in white':'plain'],['Cap','<span class=\"sw\"></span>Flexfit 6277 structured fitted cap, closed stretch back · '+esc(it.colour)],['Sizes','S/M (6¾–7¼) · L/XL (7⅛–7⅝)'],['Finish',emb?'Embroidered':'DTF print, white ink, pressed by hand in Newnan, Georgia'],['Price',it.price||'$35']]; }"
new = ("specs:function(it){ var q=it.parts, emb=it.finish==='embroidered', hp=it.slug==='cap-dark-home-port', thread=/maroon/i.test(it.colour||'')?'white and navy':'white and red'; "
       "var rows=[['Front',hp?'Your home port — name, dive flag and coordinates — printed to order in white':(MARK[q.cf]||'—')+(emb?', embroidered':', printed to order in white')],"
       "['Side',q.cs&&q.cs!=='none'?(MARK[q.cs]||q.cs)+', embroidered in '+thread+(q.csp?', '+q.csp+' side':''):'plain'],"
       "['Back',q.cb&&q.cb!=='none'?(MARK[q.cb]||q.cb)+', embroidered in white':'plain'],"
       "['Cap','<span class=\"sw\"></span>Flexfit 6277 structured fitted cap, closed stretch back · '+esc(it.colour)],['Sizes','S/M (6¾–7¼) · L/XL (7⅛–7⅝)'],"
       "['Finish',emb?'Embroidered — raised satin stitch':'Embroidered mark and tagline; the site block printed to order in white DTF, pressed by hand in Newnan, Georgia'],"
       "['Price',it.price||'$35']]; if(hp){rows.splice(5,0,['Custom','made to order once your coordinates are confirmed']);} return rows; }")
assert old in h, 'specs function not found'
h = h.replace(old, new)
open(p, 'w', encoding='utf-8').write(h)
print('index.html', n0, '->', len(h))
