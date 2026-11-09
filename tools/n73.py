#!/usr/bin/env python3
"""The 1N73LL1G3NC3 line on the site, in the Off-World format. Idempotent.

Usage: tools/n73.py <render dir>      (the output of tools/n73_render.py)

- img/n73/<slug>-{front,back}.webp (1200) + -t (600): the mockups the cards use (front = the design; back blank)
- img/designs/<slug>.webp: watermarked preview on the garment colour, for the designs grid and the shirt viewer
- 1n73ll1g3nc3/index.html (the collection page; was index.html until 9 Nov 2026): 36 cards in #sh-grid (data-line="n73"), a deck line, a collection tile, 36 designs-grid cards,
  a designs chip, counts and copy
Make it yours links open the configurator on the design's garment colour (the line is a front print; the configurator's
back designs are not involved). Run tools/bust.py afterwards.
"""
import os, re, sys, json, html as H
from PIL import Image

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/n73_out'
D = json.load(open(f'{SITE}/tools/n73_designs.json'))
LINE = D['line']; KEY = D['key']
OUT = f'{SITE}/img/n73'; os.makedirs(OUT, exist_ok=True)


def rep(h, old, new, count=1):
    assert h.count(old) == count, (h.count(old), old[:90]); return h.replace(old, new)


# 1. images --------------------------------------------------------------------------------------------------------------
tot = 0
for d in D['designs']:
    s = d['slug']
    for view in ('front', 'back'):
        src, dst = f'{SRC}/{s}-{view}.png', f'{OUT}/{s}-{view}'
        if not (os.path.exists(f'{dst}-t.webp') and os.path.getmtime(f'{dst}-t.webp') > os.path.getmtime(src)):
            im = Image.open(src).convert('RGB')
            im.resize((1200, 1200), Image.LANCZOS).save(f'{dst}.webp', 'webp', quality=86, method=6)
            im.resize((600, 600), Image.LANCZOS).save(f'{dst}-t.webp', 'webp', quality=80, method=6)
        tot += os.path.getsize(f'{dst}.webp') + os.path.getsize(f'{dst}-t.webp')
    Image.open(f'{SRC}/designs/{s}.webp').save(f'{SITE}/img/designs/{s}.webp', 'webp', quality=82, method=6)
print('images:', round(tot / 1e6, 2), 'MB in img/n73')

# 2. the collection page -----------------------------------------------------------------------------------------------------------
p = f'{SITE}/1n73ll1g3nc3/index.html'; h = open(p, encoding='utf-8').read()   # the line's own page (tools/line_pages.py builds the shell)
CAT = D['categories']


def card(d):
    s = d['slug']; col = D['colours'][d['colour']]; n = d['name']; low = col['name'].lower(); t = d['text']; cat = CAT[d['cat']]
    return (f'<figure class="sh" data-line="{KEY}" data-slug="{s}" data-code="N{d["n"]:02d}" data-colour="{H.escape(col["name"])}" data-hex="{col["hex"]}" '
            f'data-art="/img/designs/{s}.webp" data-text="{H.escape(cat + " · " + t)}" data-custom="/custom/#colour={d["colour"]}" hidden>'
            f'<button type="button" class="sh-img" data-front="/img/n73/{s}-front.webp" data-back="/img/n73/{s}-back.webp" data-side="front" '
            f'data-cap="{H.escape(n)} · {H.escape(col["name"])} · Comfort Colors 1717 · mockup" data-umami-event="shirt-open" data-umami-event-site="{s}" '
            f'aria-label="Open mockup: {H.escape(n)} shirt, {H.escape(low)}">'
            f'<img src="/img/n73/{s}-front-t.webp" width="600" height="600" loading="lazy" decoding="async" '
            f'alt="{H.escape(n)} {LINE} shirt in {H.escape(low)}, mockup: a hidden-message design printed full front"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(n)}</span><span class="pill available">Coming soon</span></span>'
            f'<span class="dz-s">{H.escape(col["name"])} · {H.escape(cat)}</span>'
            f'<span class="sh-flip" role="group" aria-label="Show front or back"><button type="button" class="on" data-side="front" aria-pressed="true">Front</button><button type="button" data-side="back" aria-pressed="false">Back</button></span></figcaption></figure>')


def dz(d):
    s = d['slug']; n = d['name']
    return (f'<figure class="dz" data-status="completed" data-line="{KEY}"><button type="button" class="dz-img" data-full="/img/designs/{s}.webp" '
            f'data-cap="{H.escape(n)} · {LINE} · the front print" data-umami-event="design-open" data-umami-event-design="{s}" aria-label="Open the full design: {H.escape(n)}">'
            f'<img src="/img/designs/{s}.webp" width="600" height="450" loading="lazy" decoding="async" draggable="false" alt="{H.escape(n)} design preview, watermarked"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(n)}</span><span class="pill completed">Art finished</span></span><span class="dz-s">{H.escape(d["text"])}</span></figcaption></figure>')


h = re.sub(rf'<figure class="sh" data-line="{KEY}".*?</figure>', '', h, flags=re.S)
h = re.sub(rf'<figure class="dz" data-status="completed" data-line="{KEY}".*?</figure>', '', h, flags=re.S)
cards = ''.join(card(d) for d in D['designs']); dzs = ''.join(dz(d) for d in D['designs'])
h = rep(h, '<!-- SH:END -->', cards + '<!-- SH:END -->')
h = rep(h, '<!-- DZ:END -->', dzs + '<!-- DZ:END -->')
print('cards:', len(D['designs']), '× 2')

# (Until 9 Nov 2026 this section also patched the home page's deck config, collection tile and intro copy the first time it
#  ran. Those live elsewhere now: the deck config in js/deck.js (DS.shirtsCfg), the tile on the home page, the page shell in
#  tools/line_pages.py. See git history for the original patches.)
# designs chip counts, from the grid itself
grid = h[h.index('<div class="dz-grid" id="dz-grid">'):h.index('<p class="dz-note">All artwork')]
cnt = {k: len(re.findall(rf'<figure class="dz" data-status="{k}"', grid)) for k in ('available', 'completed', 'progress')}
h = re.sub(r'(data-f="all"[^>]*>All <span class="mono">)\d+', rf'\g<1>{sum(cnt.values())}', h)
for k in cnt:
    h = re.sub(rf'(data-f="{k}"[^>]*>[^<]*<span class="mono">)\d+', rf'\g<1>{cnt[k]}', h)
open(p, 'w', encoding='utf-8').write(h)
print('1n73ll1g3nc3/index.html updated; designs grid', cnt)
