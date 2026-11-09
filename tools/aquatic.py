#!/usr/bin/env python3
"""The Aquatic Comic series on the site, in the Off-World / 1N73LL1G3NC3 format. Idempotent.

Usage: tools/aquatic.py <render dir>      (the output of tools/aquatic_render.py)

- img/aquatic/<slug>-{front,back}.webp (1200) + -t (600): the mockups the cards use (dark garments, white + red ink)
- img/designs/<slug>.webp: watermarked preview (chest lockup + back print on the garment colour)
- aquatic-comic/index.html (the collection page; was index.html until 9 Nov 2026): 59 cards in #sh-grid, one deck line per subset (Boat Banter, Self-Logged, Buddy Check, Buddy System,
  Till Surface Do Us Part, Master Class), a collection tile, 59 designs-grid cards, a designs chip, counts and copy
Make it yours links open the configurator on the design's garment colour. Run tools/bust.py afterwards.
"""
import os, re, sys, json, html as H
from PIL import Image

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/aquatic/renders'
D = json.load(open(f'{SITE}/tools/aquatic_designs.json', encoding='utf-8'))
LINE = D['line']; KEY = D['key']
SUBS = {v['key']: v for v in D['subsets'].values()}
ORDER = [D['subsets'][k]['key'] for k in 'SWRBCM']
OUT = f'{SITE}/img/aquatic'; os.makedirs(OUT, exist_ok=True)


def rep(h, old, new, count=1):
    assert h.count(old) == count, (h.count(old), old[:90]); return h.replace(old, new)


def lk(sub): return f'{KEY}-{sub}'                      # deck line key per subset


def plain(text, names=None):
    """Design text for captions: red marks dropped, sample names in, one line."""
    t = text.replace('*', '')
    for k, v in (names or D['sample']).items(): t = t.replace('{' + k + '}', v)
    return ' '.join(t.split('\n'))


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
print('images:', round(tot / 1e6, 2), 'MB in img/aquatic')

# 2. the collection page -----------------------------------------------------------------------------------------------------------
p = f'{SITE}/aquatic-comic/index.html'; h = open(p, encoding='utf-8').read()   # the line's own page (tools/line_pages.py builds the shell)


def card(d):
    s = d['slug']; col = D['colours'][d['colour']]; n = d['name']; low = col['name'].lower(); sub = SUBS[d['subset']]
    joke = plain(d['front']); custom = d['names'] > 0
    tag = f'{sub["name"]} · ' + ('your name on it · ' if custom else '')
    return (f'<figure class="sh" data-line="{lk(sub["key"])}" data-slug="{s}" data-code="AC{d["code"]}" data-colour="{H.escape(col["name"])}" data-hex="{col["hex"]}" '
            f'data-art="/img/designs/{s}.webp" data-text="{H.escape(sub["name"] + " · " + joke)}" data-custom="/custom/#colour={d["colour"]}" hidden>'
            f'<button type="button" class="sh-img" data-front="/img/aquatic/{s}-front.webp" data-back="/img/aquatic/{s}-back.webp" data-side="back" '
            f'data-cap="{H.escape(n)} · {H.escape(sub["name"])} · {H.escape(col["name"])} · Comfort Colors 1717 · mockup, white ink{", sample names" if custom else ""}" '
            f'data-umami-event="shirt-open" data-umami-event-site="{s}" aria-label="Open mockup: {H.escape(n)} shirt, {H.escape(sub["name"])}, {H.escape(low)}">'
            f'<img src="/img/aquatic/{s}-back-t.webp" width="600" height="600" loading="lazy" decoding="async" '
            f'alt="{H.escape(n)} {LINE} shirt in {H.escape(low)}, mockup: the joke on the back in white with its punch words in red; the DS mark and &ldquo;{H.escape(joke)}&rdquo; on the left chest"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(n)}</span><span class="pill available">Coming soon</span></span>'
            f'<span class="dz-s">{H.escape(col["name"])} · {H.escape(tag)}{LINE}</span>'
            f'<span class="sh-flip" role="group" aria-label="Show front or back"><button type="button" data-side="front" aria-pressed="false">Front</button><button type="button" class="on" data-side="back" aria-pressed="true">Back</button></span></figcaption></figure>')


def dz(d):
    s = d['slug']; n = d['name']; sub = SUBS[d['subset']]
    return (f'<figure class="dz" data-status="completed" data-line="{KEY}" data-sub="{d["subset"]}"><button type="button" class="dz-img" data-full="/img/designs/{s}.webp" '
            f'data-cap="{H.escape(n)} · {LINE} · {H.escape(sub["name"])} · chest and back" data-umami-event="design-open" data-umami-event-design="{s}" aria-label="Open the full design: {H.escape(n)}, {H.escape(sub["name"])}">'
            f'<img src="/img/designs/{s}.webp" width="600" height="450" loading="lazy" decoding="async" draggable="false" alt="{H.escape(n)} design preview, watermarked"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(n)}</span><span class="pill completed">Art finished</span></span><span class="dz-s">{H.escape(sub["name"])} · {H.escape(plain(d["front"]))}</span></figcaption></figure>')


h = re.sub(rf'<figure class="sh" data-line="{KEY}-[a-z-]+".*?</figure>', '', h, flags=re.S)
h = re.sub(rf'<figure class="dz" data-status="completed" data-line="{KEY}".*?</figure>', '', h, flags=re.S)
cards = ''.join(card(d) for k in ORDER for d in D['designs'] if d['subset'] == k)
dzs = ''.join(dz(d) for d in D['designs'])
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
print('aquatic-comic/index.html updated; designs grid', cnt)
