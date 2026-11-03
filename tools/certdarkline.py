#!/usr/bin/env python3
"""The Certified-ish Dark line on the home page. Idempotent.

Usage: tools/certdarkline.py <render dir>     (the output of tools/certdark.py: cert-<slug>-{back,front}.png, 1200²)

- img/certs/dark/cert-<slug>-{back,front}.webp (1200) + -t (600)
- index.html: 20 cards in #sh-grid (data-line="certifiedish-dark"), cloned from the light cards and placed after them,
  a deck line "Certified-ish Dark", its captions and specs (white ink), the zoom the light Certified-ish cards get in the
  deck, and a "The dark line" link on the Certified-ish collection tile
- custom/index.html: Yam and Violet in the garment palette (the dark-line colours the palette lacked), so the cards'
  Make it yours links open on the right shirt
Then run tools/bust.py.
"""
import os, re, sys, json, html as H
from PIL import Image

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SITE, 'tools'))
from certdark import CERT_DARK, HEX, NAME

SRC = sys.argv[1]
OUT = f'{SITE}/img/certs/dark'; os.makedirs(OUT, exist_ok=True)
KEY, LINE = 'certifiedish-dark', 'Certified-ish Dark'


def rep(h, old, new, count=1):
    assert h.count(old) == count, (h.count(old), old[:100]); return h.replace(old, new)


# 1. images ----------------------------------------------------------------------------------------------------------------
tot = 0
for slug in CERT_DARK:
    for view in ('back', 'front'):
        im = Image.open(f'{SRC}/{slug}-{view}.png').convert('RGB')
        im.resize((1200, 1200), Image.LANCZOS).save(f'{OUT}/{slug}-{view}.webp', 'webp', quality=86, method=6)
        im.resize((600, 600), Image.LANCZOS).save(f'{OUT}/{slug}-{view}-t.webp', 'webp', quality=80, method=6)
        tot += os.path.getsize(f'{OUT}/{slug}-{view}.webp') + os.path.getsize(f'{OUT}/{slug}-{view}-t.webp')
print('img/certs/dark:', len(os.listdir(OUT)), 'files,', round(tot / 1e6, 2), 'MB')

# 2. home page -------------------------------------------------------------------------------------------------------------
p = f'{SITE}/index.html'; h = open(p, encoding='utf-8').read()
h = re.sub(rf'<figure class="sh" data-line="{KEY}".*?</figure>', '', h, flags=re.S)
light = {m.group(1): m.group(0) for m in re.finditer(r'<figure class="sh" data-line="certifiedish" data-slug="([a-z0-9-]+)".*?</figure>', h, re.S)}
assert set(light) == set(CERT_DARK), set(light) ^ set(CERT_DARK)


def dark_card(slug, c):
    col = CERT_DARK[slug]; name, hexc, low = NAME[col], HEX[col], NAME[col].lower()
    old_name = re.search(r'data-colour="([^"]+)"', c).group(1); old_low = old_name.lower()
    c = c.replace('data-line="certifiedish"', f'data-line="{KEY}"', 1)
    c = re.sub(r'data-colour="[^"]+"', f'data-colour="{name}"', c, count=1)
    c = re.sub(r'data-hex="#[0-9A-Fa-f]{6}"', f'data-hex="{hexc}"', c, count=1)
    c = re.sub(r'data-custom="/custom/#colour=[a-z-]+', f'data-custom="/custom/#colour={col}', c, count=1)
    c = re.sub(r'img/certs/(cert-[a-z0-9-]+-(?:front|back)(?:-t)?\.webp)(?:\?v=[0-9a-f]+)?', r'img/certs/dark/\1', c)
    c = c.replace(f' · {old_name} · Comfort Colors 1717 · mockup', f' · {name} · Comfort Colors 1717 · white ink · mockup')
    c = c.replace(f'shirt, {old_low}"', f'shirt, {low}, dark line"')
    c = c.replace(f'Certified-ish shirt in {old_low}, mockup', f'Certified-ish Dark shirt in {low}, white ink, mockup')
    c = c.replace(f'<span class="dz-s">{old_name} · Certified-ish</span>', f'<span class="dz-s">{name} · Certified-ish Dark</span>')
    c = c.replace(f'data-umami-event-site="{slug}"', f'data-umami-event-site="{slug}-dark"')
    return c


cards = ''.join(dark_card(s, light[s]) for s in light)          # in the light deck's order
last = list(light.values())[-1]
h = rep(h, last, last + cards)
print('cards:', len(light))

if f"['{KEY}','{LINE}']" not in h:
    h = rep(h, "['certifiedish','Certified-ish'],['offworld'", f"['certifiedish','Certified-ish'],['{KEY}','{LINE}'],['offworld'")
    h = rep(h, "certifiedish:44,offworld:44", f"certifiedish:44,'{KEY}':44,offworld:44")
    h = rep(h, ":it.line==='n73'?'1N73LL1G3NC3':'Certified-ish'; },", f":it.line==='n73'?'1N73LL1G3NC3':it.line==='{KEY}'?'{LINE}':'Certified-ish'; }},")
    h = rep(h, ":'Certified-ish back print · DS mark'; },", f":it.line==='{KEY}'?'Certified-ish back print · white ink · DS mark':'Certified-ish back print · DS mark'; }},")
    h = rep(h, "defaultView:function(it){ return it.line==='certifiedish'||", "defaultView:function(it){ return it.line.indexOf('certifiedish')===0||")
    h = rep(h, "it.line==='offworld-dark'?'Back · mockup, white ink':'Back · mockup'",
            f"it.line==='offworld-dark'||it.line==='{KEY}'?'Back · mockup, white ink':'Back · mockup'")
    h = rep(h, ":'Front · mockup, DS mark along the sleeve'); },",
            f":it.line==='{KEY}'?'Front · mockup, DS mark along the sleeve in white and red':'Front · mockup, DS mark along the sleeve'); }},")
    h = rep(h, "['Mark','DS mark along the sleeve · the shark stays on the Signature Series'],['Shirt',sw],['Ink','Water-based black, printed by hand']",
            f"['Mark','DS mark along the sleeve · the shark stays on the Signature Series'],['Shirt',sw],['Ink',it.line==='{KEY}'?'Water-based white, printed by hand · the DS mark in white and red':'Water-based black, printed by hand']")
    h = rep(h, '.dk[data-line="certifiedish"] .dk-pic img{', f'.dk[data-line="certifiedish"] .dk-pic img,.dk[data-line="{KEY}"] .dk-pic img{{')
    # the collection tile and the shirts intro
    h = rep(h, '<a class="btn" href="#shirts" data-deck-line="certifiedish" data-umami-event="line-open" data-umami-event-line="certifiedish">See the Certified-ish shirts</a>',
            f'<a class="btn" href="#shirts" data-deck-line="certifiedish" data-umami-event="line-open" data-umami-event-line="certifiedish">See the Certified-ish shirts</a>'
            f'<a class="txt" href="#shirts" data-deck-line="{KEY}" data-umami-event="line-open" data-umami-event-line="{KEY}">The dark line &rarr;</a>')
    h = rep(h, 'One tongue-in-cheek diagram for each specialty in your logbook, from Open Water to Rebreather. Deep Diver charts narcosis one martini at a time; Night Diver labels everything that is watching you.</p>',
            'One tongue-in-cheek diagram for each specialty in your logbook, from Open Water to Rebreather. Deep Diver charts narcosis one martini at a time; Night Diver labels everything that is watching you. Black ink on a light tee, or white ink on a dark one.</p>')
    h = rep(h, 'the twenty Certified-ish backs on the tee they ship on,', 'the twenty Certified-ish backs on the tee they ship on and again in white ink on a dark one,')
open(p, 'w', encoding='utf-8').write(h)
print('index.html updated')

# 3. the Make it yours palette: Yam and Violet -----------------------------------------------------------------------------
p = f'{SITE}/custom/index.html'; c = open(p, encoding='utf-8').read()
m = re.search(r'\{"slug":"grape","name":"Grape","hex":"#[0-9A-Fa-f]{6}"[^}]*\}', c); assert m, 'grape entry'
g = m.group(0); add = ''
for slug, tone in (('yam', 'warm'), ('violet', 'cool')):
    if f'"slug":"{slug}"' in c: continue
    e = re.sub(r'"slug":"grape"', f'"slug":"{slug}"', g); e = e.replace('"name":"Grape"', f'"name":"{NAME[slug]}"')
    e = re.sub(r'"hex":"#[0-9A-Fa-f]{6}"', f'"hex":"{HEX[slug]}"', e); e = re.sub(r'"tone":"[a-z]+"', f'"tone":"{tone}"', e)
    add += ',' + e
if add:
    c = rep(c, g, g + add); open(p, 'w', encoding='utf-8').write(c); print('custom palette: added', add.count('slug'))
