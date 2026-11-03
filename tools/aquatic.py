#!/usr/bin/env python3
"""The Aquatic Comic series on the site, in the Off-World / 1N73LL1G3NC3 format. Idempotent.

Usage: tools/aquatic.py <render dir>      (the output of tools/aquatic_render.py)

- img/aquatic/<slug>-{front,back}.webp (1200) + -t (600): the mockups the cards use (dark garments, white + red ink)
- img/designs/<slug>.webp: watermarked preview (chest lockup + back print on the garment colour)
- index.html: 59 cards in #sh-grid, one deck line per subset (Boat Banter, Self-Logged, Buddy Check, Buddy System,
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

# 2. home page -----------------------------------------------------------------------------------------------------------
p = f'{SITE}/index.html'; h = open(p, encoding='utf-8').read()


def card(d):
    s = d['slug']; col = D['colours'][d['colour']]; n = d['name']; low = col['name'].lower(); sub = SUBS[d['subset']]
    joke = plain(d['front']); custom = d['names'] > 0
    tag = f'{sub["name"]} · ' + ('your name on it · ' if custom else '')
    return (f'<figure class="sh" data-line="{lk(sub["key"])}" data-slug="{s}" data-code="AC{d["code"]}" data-colour="{H.escape(col["name"])}" data-hex="{col["hex"]}" '
            f'data-art="img/designs/{s}.webp" data-text="{H.escape(sub["name"] + " · " + joke)}" data-custom="/custom/#colour={d["colour"]}" hidden>'
            f'<button type="button" class="sh-img" data-front="img/aquatic/{s}-front.webp" data-back="img/aquatic/{s}-back.webp" data-side="back" '
            f'data-cap="{H.escape(n)} · {H.escape(sub["name"])} · {H.escape(col["name"])} · Comfort Colors 1717 · mockup, white ink{", sample names" if custom else ""}" '
            f'data-umami-event="shirt-open" data-umami-event-site="{s}" aria-label="Open mockup: {H.escape(n)} shirt, {H.escape(sub["name"])}, {H.escape(low)}">'
            f'<img src="img/aquatic/{s}-back-t.webp" width="600" height="600" loading="lazy" decoding="async" '
            f'alt="{H.escape(n)} {LINE} shirt in {H.escape(low)}, mockup: the joke on the back in white with its punch words in red; the DS mark and &ldquo;{H.escape(joke)}&rdquo; on the left chest"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(n)}</span><span class="pill available">Coming soon</span></span>'
            f'<span class="dz-s">{H.escape(col["name"])} · {H.escape(tag)}{LINE}</span>'
            f'<span class="sh-flip" role="group" aria-label="Show front or back"><button type="button" data-side="front" aria-pressed="false">Front</button><button type="button" class="on" data-side="back" aria-pressed="true">Back</button></span></figcaption></figure>')


def dz(d):
    s = d['slug']; n = d['name']; sub = SUBS[d['subset']]
    return (f'<figure class="dz" data-status="completed" data-line="{KEY}"><button type="button" class="dz-img" data-full="img/designs/{s}.webp" '
            f'data-cap="{H.escape(n)} · {LINE} · {H.escape(sub["name"])} · chest and back" data-umami-event="design-open" data-umami-event-design="{s}" aria-label="Open the full design: {H.escape(n)}, {H.escape(sub["name"])}">'
            f'<img src="img/designs/{s}.webp" width="600" height="450" loading="lazy" decoding="async" draggable="false" alt="{H.escape(n)} design preview, watermarked"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(n)}</span><span class="pill completed">Art finished</span></span><span class="dz-s">{H.escape(sub["name"])} · {H.escape(plain(d["front"]))}</span></figcaption></figure>')


h = re.sub(rf'<figure class="sh" data-line="{KEY}-[a-z-]+".*?</figure>', '', h, flags=re.S)
h = re.sub(rf'<figure class="dz" data-status="completed" data-line="{KEY}".*?</figure>', '', h, flags=re.S)
cards = ''.join(card(d) for k in ORDER for d in D['designs'] if d['subset'] == k)
dzs = ''.join(dz(d) for d in D['designs'])
h = rep(h, '</div>\n      <p class="dz-note">Colours are the garment colours each site was printed on', cards + '</div>\n      <p class="dz-note">Colours are the garment colours each site was printed on')
h = rep(h, '\n      </div>\n      <p class="dz-note">All artwork &copy; 2026', '\n        ' + dzs + '\n      </div>\n      <p class="dz-note">All artwork &copy; 2026')
print('cards:', len(D['designs']), '× 2')

if f"['{lk(ORDER[0])}'," not in h:
    deck = ','.join(f"['{lk(k)}','{LINE} · {SUBS[k]['name']}']" for k in ORDER)
    steps = ','.join(f"'{lk(k)}':44" for k in ORDER)
    h = rep(h, "['n73','1N73LL1G3NC3']], step:{plates:64,dark:64,certifiedish:44,'certifiedish-dark':44,offworld:44,'offworld-dark':44,n73:44},",
            f"['n73','1N73LL1G3NC3'],{deck}], step:{{plates:64,dark:64,certifiedish:44,'certifiedish-dark':44,offworld:44,'offworld-dark':44,n73:44,{steps}}},")
    h = rep(h, "it.line==='n73'?'1N73LL1G3NC3':", f"it.line==='n73'?'1N73LL1G3NC3':it.line.indexOf('{KEY}-')===0?'{LINE}':")
    h = rep(h, "it.line.indexOf('offworld')===0||it.line==='n73'?it.text:", f"it.line.indexOf('offworld')===0||it.line==='n73'||it.line.indexOf('{KEY}-')===0?it.text:")
    BLURB = ('Dive-deck humour in IM Fell: the DS mark over the slogan on the left chest, the joke on the back, '
             'its punch words in red. White and red ink on a dark tee.')
    h = rep(h, "blurb:function(it){ return it.line==='n73'?", f"blurb:function(it){{ return it.line.indexOf('{KEY}-')===0?'{BLURB}':it.line==='n73'?")
    h = rep(h, "defaultView:function(it){ return it.line.indexOf('certifiedish')===0||it.line.indexOf('offworld')===0?'back':'front'; },",
            f"defaultView:function(it){{ return it.line.indexOf('certifiedish')===0||it.line.indexOf('offworld')===0||it.line.indexOf('{KEY}-')===0?'back':'front'; }},")
    h = rep(h, ":it.line==='n73'?'Watermarked preview of the front print':",
            f":it.line==='n73'?'Watermarked preview of the front print':it.line.indexOf('{KEY}-')===0?'Watermarked preview of the chest lockup and the back print':")
    h = rep(h, "it.line==='n73'?'Front · mockup, the full-front print':",
            f"it.line==='n73'?'Front · mockup, the full-front print':it.line.indexOf('{KEY}-')===0?'Front · mockup, the DS mark over the slogan, left chest':")
    custom_lines = '||'.join(f"it.line==='{lk(k)}'" for k in ORDER[1:])
    h = rep(h, "if(it.line==='n73') return [[",
            f"if(it.line.indexOf('{KEY}-')===0) return [['Front','The DS mark over the slogan, left chest, 3.75 in'],['Back','The joke, white with the punch words in red, 11 in wide'],"
            f"['Shirt',sw],['Ink','Water-based white and red, printed by hand'],"
            f"['Price',({custom_lines})?'$47 · $50 in 2XL and 3XL, with the name or names you choose':'$42 · $45 in 2XL and 3XL']]; if(it.line==='n73') return [[")
    # copy: collections intro, tile, shirts intro, designs intro, designs chip
    h = rep(h, '<p>Four lines, one hand. Pick a line to see every design in it.</p>', '<p>Five lines, one hand. Pick a line to see every design in it.</p>')
    links = ''.join(f'<a class="txt" href="#shirts" data-deck-line="{lk(k)}" data-umami-event="line-open" data-umami-event-line="{lk(k)}">{H.escape(SUBS[k]["name"])}</a>' for k in ORDER[1:])
    tile = (f'''        <article class="line" aria-labelledby="line-{KEY}-h">
          <figure class="line-art" oncontextmenu="return false"><img src="img/lines/aquatic-tile.webp" width="800" height="600" loading="lazy" decoding="async" draggable="false" alt="Plan the dive, {LINE} preview, watermarked"></figure>
          <div class="line-body">
            <p class="eyebrow">{LINE} &middot; <span data-count="{KEY}">{len(D['designs'])}</span> designs</p>
            <h3 id="line-{KEY}-h">Jokes told on the dive deck</h3>
            <p>The DS mark over the slogan on the left chest, the joke on the back, its punch words in red: &ldquo;Plan the dive. Dive the plan. Blame the current.&rdquo; Twenty to wear as they are (Boat Banter), and five sets with your names in the joke: Self-Logged, about you; Buddy Check, about your dive buddy; Buddy System, two names for a pair; Till Surface Do Us Part, for a husband-and-wife dive team; Master Class, for two Master Scuba Divers. White and red ink on dark tees.</p>
            <p class="line-links"><a class="btn" href="#shirts" data-deck-line="{lk(ORDER[0])}" data-umami-event="line-open" data-umami-event-line="{lk(ORDER[0])}">See the {LINE} shirts</a>{links}<a class="txt" href="#designs" data-show-line="{KEY}" data-umami-event="line-art" data-umami-event-line="{KEY}">The art &rarr;</a></p>
          </div>
        </article>
''')
    h = rep(h, '        </article>\n      </div>\n    </section>\n\n    <section id="shirts"', '        </article>\n' + tile + '      </div>\n    </section>\n\n    <section id="shirts"')
    h = rep(h, 'and the thirty-six 1N73LL1G3NC3 hidden-message fronts (mockups, one garment colour each).',
            'the thirty-six 1N73LL1G3NC3 hidden-message fronts, and the fifty-nine Aquatic Comic jokes on dark tees, thirty-nine of them with your names in them (mockups, one garment colour each).')
    h = rep(h, 'and the thirty-six 1N73LL1G3NC3 fronts. Tap a design', 'the thirty-six 1N73LL1G3NC3 fronts and the fifty-nine Aquatic Comic chest-and-back jokes. Tap a design')
    h = rep(h, '<button type="button" class="chip" data-l="n73" data-umami-event="designs-line" data-umami-event-line="n73" aria-pressed="false">1N73LL1G3NC3</button>',
            f'<button type="button" class="chip" data-l="n73" data-umami-event="designs-line" data-umami-event-line="n73" aria-pressed="false">1N73LL1G3NC3</button>\n        <button type="button" class="chip" data-l="{KEY}" data-umami-event="designs-line" data-umami-event-line="{KEY}" aria-pressed="false">{LINE}</button>')
# designs chip counts, from the grid itself
grid = h[h.index('<div class="dz-grid" id="dz-grid">'):h.index('<p class="dz-note">All artwork')]
cnt = {k: len(re.findall(rf'<figure class="dz" data-status="{k}"', grid)) for k in ('available', 'completed', 'progress')}
h = re.sub(r'(data-f="all"[^>]*>All <span class="mono">)\d+', rf'\g<1>{sum(cnt.values())}', h)
for k in cnt:
    h = re.sub(rf'(data-f="{k}"[^>]*>[^<]*<span class="mono">)\d+', rf'\g<1>{cnt[k]}', h)
open(p, 'w', encoding='utf-8').write(h)
print('index.html updated; designs grid', cnt)
