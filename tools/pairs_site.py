#!/usr/bin/env python3
"""The pairs on the website (12 Nov 2026): an "Add the pair" button on each of the 14 site guides, on each site cap
in the home page hats deck and on each Signature tee (light and dark) in the Signature deck, pointing at the pair
products in the store (tools/pairs.py). The button names both pieces (Eric, 12 Nov: "Add the pair should reference
the shirt and hat"). Idempotent — re-running only normalises the labels.
  sites/<slug>/index.html   .cta gains  <a class="btn ghost" href="…/products/<h>-pair-dark">Add the pair · shirt + cap · $69</a>
                            "On the shirt" gains a line naming both pairs (light tee / dark tee)
  index.html                the 14 site-cap figures gain data-pair="…/products/<h>-pair-dark"
  signature/index.html      the 28 tee figures gain data-pair: light tees → …-pair-light, dark tees → …-pair-dark
                            (tools/line_pages.py harvests these cards from the page, so the attribute survives a rebuild)
  js/deck.js                the deck's CTA renders "Add the pair · cap + shirt · $69" on caps, "· shirt + cap ·" on shirts
Then run tools/bust.py."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairs import SITES, CAP_SLUG, GUIDE, SHOP
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE_LABEL = 'Add the pair &middot; shirt + cap &middot; $69'
DECK_LABEL = "'Add the pair &middot; '+(cfg.noun==='cap'?'cap + shirt':'shirt + cap')+' &middot; $69'"


def save(p, s, old):
    if s != old: open(p, 'w', encoding='utf-8').write(s); return 1
    return 0


n = 0
for slug, code, name, *_ in SITES:
    h = CAP_SLUG.get(slug, slug); p = f'{ROOT}/sites/{GUIDE.get(slug, slug)}/index.html'; s = s0 = open(p, encoding='utf-8').read()
    dark, light = f'{SHOP}/products/{h}-pair-dark', f'{SHOP}/products/{h}-pair-light'
    if 'guide-pair' not in s:
        old = f'<a class="btn ghost" href="/#map" data-umami-event="guide-map">Back to the map</a>'
        assert s.count(old) == 1, p
        s = s.replace(old, f'<a class="btn ghost" href="{dark}" data-umami-event="guide-pair" data-umami-event-site="{slug}">{GUIDE_LABEL}</a>\n          ' + old)
        old = '<p class="more"><a href="/#craft">How the plates are made &rarr;</a></p>'
        assert s.count(old) == 1, p
        the = '' if name.startswith('The ') else 'the '
        s = s.replace(old, f'<p class="pair"><strong>The pair.</strong> This shirt and {the}{name} cap together, $8 under the two apart: '
                           f'<a href="{light}" data-umami-event="guide-pair-light">with the light tee</a> or <a href="{dark}" data-umami-event="guide-pair-dark">the dark tee</a>, $69 ($72 in 2XL&ndash;3XL).</p>\n      ' + old)
        s = s.replace('.more{margin-top:20px}', '.pair{margin-top:20px;max-width:62ch}.pair a{color:var(--red)}\n.more{margin-top:20px}', 1)
    # normalise the label (the first version read "Add the pair · $69")
    s = re.sub(r'(data-umami-event="guide-pair" data-umami-event-site="[a-z0-9-]+">)Add the pair[^<]*(</a>)', lambda m: m.group(1) + GUIDE_LABEL + m.group(2), s)
    n += save(p, s, s0)
print(n, 'site guides changed')

p = f'{ROOT}/index.html'; s = s0 = open(p, encoding='utf-8').read(); k = 0
for slug, *_ in SITES:
    h = CAP_SLUG.get(slug, slug); key = f'data-slug="cap-dark-{h}"'
    assert s.count(key) == 1, key
    if f'data-pair="{SHOP}/products/{h}-pair-dark"' in s: continue
    s = s.replace(key, f'{key} data-pair="{SHOP}/products/{h}-pair-dark"'); k += 1
save(p, s, s0); print(k, 'cap figures on the home page')

p = f'{ROOT}/signature/index.html'; s = s0 = open(p, encoding='utf-8').read(); k = 0
for slug, *_ in SITES:
    h = CAP_SLUG.get(slug, slug)
    for line, pl in (('plates', 'light'), ('dark', 'dark')):
        key = f'data-line="{line}" data-slug="{slug}"'; url = f'{SHOP}/products/{h}-pair-{pl}'
        assert s.count(key) == 1, key
        if f'{key} data-pair="{url}"' in s: continue
        s = s.replace(key, f'{key} data-pair="{url}"'); k += 1
save(p, s, s0); print(k, 'tee figures on the Signature page')

p = f'{ROOT}/js/deck.js'; j = j0 = open(p, encoding='utf-8').read()
if 'pair:f.dataset.pair' not in j:
    old = "guide:f.dataset.guide||'', custom:f.dataset.custom||'/custom/',"
    assert j.count(old) == 1
    j = j.replace(old, "guide:f.dataset.guide||'', pair:f.dataset.pair||'', custom:f.dataset.custom||'/custom/',")
    old = "(cfg.custom===false?'':'<a class=\"btn ghost\" href=\"'+esc(it.custom)+'\" data-umami-event=\"deck-custom\">Make it yours</a>')"
    assert j.count(old) == 1
    j = j.replace(old, "(it.pair?'<a class=\"btn ghost\" href=\"'+esc(it.pair)+'\" data-umami-event=\"deck-pair\">Add the pair &middot; $69</a>':'')+" + old)
# normalise the label
old = "data-umami-event=\"deck-pair\">Add the pair &middot; $69</a>':'')"
if old in j:
    j = j.replace(old, "data-umami-event=\"deck-pair\">'+" + DECK_LABEL + "+'</a>':'')")
assert j.count(DECK_LABEL) == 1, 'deck.js pair label'
if save(p, j, j0): print('deck.js: pair button')
