#!/usr/bin/env python3
"""The pairs on the website (12 Nov 2026): an "Add the pair" button on each of the 14 site guides and on each site cap
in the home page hats deck, pointing at the pair products in the store (tools/pairs.py). Idempotent.
  sites/<slug>/index.html  .cta gains  <a class="btn ghost" href="…/products/<h>-pair-dark">Add the pair · $69</a>
                           "On the shirt" gains a line naming both pairs (light tee / dark tee)
  index.html               the 14 site-cap figures gain data-pair="…/products/<h>-pair-dark"
  js/deck.js               the deck's CTA renders "Add the pair" when an item carries data-pair
Then run tools/bust.py."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairs import SITES, CAP_SLUG, GUIDE, SHOP
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

n = 0
for slug, code, name, *_ in SITES:
    h = CAP_SLUG.get(slug, slug); p = f'{ROOT}/sites/{GUIDE.get(slug, slug)}/index.html'; s = open(p, encoding='utf-8').read()
    if 'guide-pair' in s: continue
    dark, light = f'{SHOP}/products/{h}-pair-dark', f'{SHOP}/products/{h}-pair-light'
    old = f'<a class="btn ghost" href="/#map" data-umami-event="guide-map">Back to the map</a>'
    assert s.count(old) == 1, p
    s = s.replace(old, f'<a class="btn ghost" href="{dark}" data-umami-event="guide-pair" data-umami-event-site="{slug}">Add the pair &middot; $69</a>\n          ' + old)
    old = '<p class="more"><a href="/#craft">How the plates are made &rarr;</a></p>'
    assert s.count(old) == 1, p
    the = '' if name.startswith('The ') else 'the '
    s = s.replace(old, f'<p class="pair"><strong>The pair.</strong> This shirt and {the}{name} cap together, $8 under the two apart: '
                       f'<a href="{light}" data-umami-event="guide-pair-light">with the light tee</a> or <a href="{dark}" data-umami-event="guide-pair-dark">the dark tee</a>, $69 ($72 in 2XL&ndash;3XL).</p>\n      ' + old)
    s = s.replace('.more{margin-top:20px}', '.pair{margin-top:20px;max-width:62ch}.pair a{color:var(--red)}\n.more{margin-top:20px}', 1)
    open(p, 'w', encoding='utf-8').write(s); n += 1
print(n, 'site guides')

p = f'{ROOT}/index.html'; s = open(p, encoding='utf-8').read(); k = 0
for slug, *_ in SITES:
    h = CAP_SLUG.get(slug, slug); key = f'data-slug="cap-dark-{h}"'
    assert s.count(key) == 1, key
    if f'data-pair="{SHOP}/products/{h}-pair-dark"' in s: continue
    s = s.replace(key, f'{key} data-pair="{SHOP}/products/{h}-pair-dark"'); k += 1
open(p, 'w', encoding='utf-8').write(s); print(k, 'cap figures on the home page')

p = f'{ROOT}/js/deck.js'; j = open(p, encoding='utf-8').read()
if 'pair:f.dataset.pair' not in j:
    old = "guide:f.dataset.guide||'', custom:f.dataset.custom||'/custom/',"
    assert j.count(old) == 1
    j = j.replace(old, "guide:f.dataset.guide||'', pair:f.dataset.pair||'', custom:f.dataset.custom||'/custom/',")
    old = "(cfg.custom===false?'':'<a class=\"btn ghost\" href=\"'+esc(it.custom)+'\" data-umami-event=\"deck-custom\">Make it yours</a>')"
    assert j.count(old) == 1
    j = j.replace(old, "(it.pair?'<a class=\"btn ghost\" href=\"'+esc(it.pair)+'\" data-umami-event=\"deck-pair\">Add the pair &middot; $69</a>':'')+" + old)
    open(p, 'w', encoding='utf-8').write(j); print('deck.js: pair button')
