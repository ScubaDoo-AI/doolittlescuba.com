#!/usr/bin/env python3
"""The 1N73LL1G3NC3 line on the site, in the Off-World format. Idempotent.

Usage: tools/n73.py <render dir>      (the output of tools/n73_render.py)

- img/n73/<slug>-{front,back}.webp (1200) + -t (600): the mockups the cards use (front = the design; back blank)
- img/designs/<slug>.webp: watermarked preview on the garment colour, for the designs grid and the shirt viewer
- index.html: 36 cards in #sh-grid (data-line="n73"), a deck line, a collection tile, 36 designs-grid cards,
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

# 2. home page -----------------------------------------------------------------------------------------------------------
p = f'{SITE}/index.html'; h = open(p, encoding='utf-8').read()
CAT = D['categories']


def card(d):
    s = d['slug']; col = D['colours'][d['colour']]; n = d['name']; low = col['name'].lower(); t = d['text']; cat = CAT[d['cat']]
    return (f'<figure class="sh" data-line="{KEY}" data-slug="{s}" data-code="N{d["n"]:02d}" data-colour="{H.escape(col["name"])}" data-hex="{col["hex"]}" '
            f'data-art="img/designs/{s}.webp" data-text="{H.escape(cat + " · " + t)}" data-custom="/custom/#colour={d["colour"]}" hidden>'
            f'<button type="button" class="sh-img" data-front="img/n73/{s}-front.webp" data-back="img/n73/{s}-back.webp" data-side="front" '
            f'data-cap="{H.escape(n)} · {H.escape(col["name"])} · Comfort Colors 1717 · mockup" data-umami-event="shirt-open" data-umami-event-site="{s}" '
            f'aria-label="Open mockup: {H.escape(n)} shirt, {H.escape(low)}">'
            f'<img src="img/n73/{s}-front-t.webp" width="600" height="600" loading="lazy" decoding="async" '
            f'alt="{H.escape(n)} {LINE} shirt in {H.escape(low)}, mockup: a hidden-message design printed full front"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(n)}</span><span class="pill available">Coming soon</span></span>'
            f'<span class="dz-s">{H.escape(col["name"])} · {H.escape(cat)}</span>'
            f'<span class="sh-flip" role="group" aria-label="Show front or back"><button type="button" class="on" data-side="front" aria-pressed="true">Front</button><button type="button" data-side="back" aria-pressed="false">Back</button></span></figcaption></figure>')


def dz(d):
    s = d['slug']; n = d['name']
    return (f'<figure class="dz" data-status="completed" data-line="{KEY}"><button type="button" class="dz-img" data-full="img/designs/{s}.webp" '
            f'data-cap="{H.escape(n)} · {LINE} · the front print" data-umami-event="design-open" data-umami-event-design="{s}" aria-label="Open the full design: {H.escape(n)}">'
            f'<img src="img/designs/{s}.webp" width="600" height="450" loading="lazy" decoding="async" draggable="false" alt="{H.escape(n)} design preview, watermarked"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(n)}</span><span class="pill completed">Art finished</span></span><span class="dz-s">{H.escape(d["text"])}</span></figcaption></figure>')


h = re.sub(rf'<figure class="sh" data-line="{KEY}".*?</figure>', '', h, flags=re.S)
h = re.sub(rf'<figure class="dz" data-status="completed" data-line="{KEY}".*?</figure>', '', h, flags=re.S)
cards = ''.join(card(d) for d in D['designs']); dzs = ''.join(dz(d) for d in D['designs'])
h = rep(h, '</div>\n      <p class="dz-note">Colours are the garment colours each site was printed on', cards + '</div>\n      <p class="dz-note">Colours are the garment colours each site was printed on')
h = rep(h, '\n      </div>\n      <p class="dz-note">All artwork &copy; 2026', '\n        ' + dzs + '\n      </div>\n      <p class="dz-note">All artwork &copy; 2026')
print('cards:', len(D['designs']), '× 2')

if f"['{KEY}','{LINE}']" not in h:
    BLURB = ('A message in plain sight: read the bold characters, the dials or the code and it speaks. '
             'One full-front print, on a garment colour chosen for its theme.')
    # deck
    h = rep(h, "['offworld-dark','Off-World Hunt Club Dark']], step:{plates:64,dark:64,certifiedish:44,offworld:44,'offworld-dark':44},",
            f"['offworld-dark','Off-World Hunt Club Dark'],['{KEY}','{LINE}']], step:{{plates:64,dark:64,certifiedish:44,offworld:44,'offworld-dark':44,{KEY}:44}},")
    h = rep(h, "it.line==='offworld-dark'?'Off-World Hunt Club Dark':'Certified-ish'; },",
            f"it.line==='offworld-dark'?'Off-World Hunt Club Dark':it.line==='{KEY}'?'{LINE}':'Certified-ish'; }},")
    h = rep(h, ":it.line.indexOf('offworld')===0?it.text:'Certified-ish back print · DS mark'; },",
            f":it.line.indexOf('offworld')===0||it.line==='{KEY}'?it.text:'Certified-ish back print · DS mark'; }},")
    h = rep(h, "blurb:function(it){ return it.line.indexOf('offworld')===0?",
            f"blurb:function(it){{ return it.line==='{KEY}'?'{BLURB}':it.line.indexOf('offworld')===0?")
    h = rep(h, "return v==='art'?(sig||dk?'The back print · plate, facts, species and water · watermarked':'Watermarked preview of the back print')",
            f"return v==='art'?(sig||dk?'The back print · plate, facts, species and water · watermarked':it.line==='{KEY}'?'Watermarked preview of the front print':'Watermarked preview of the back print')")
    h = rep(h, "it.line==='offworld'?'Front · mockup, DS mark and the word in glyphs on the chest':",
            f"it.line==='{KEY}'?'Front · mockup, the full-front print':it.line==='offworld'?'Front · mockup, DS mark and the word in glyphs on the chest':")
    h = rep(h, "if(it.line.indexOf('offworld')===0) return [[",
            f"if(it.line==='{KEY}') return [['Front','The design, full front, about 11.5 in wide'],['Back','Plain'],['Shirt',sw],['Ink','Water-based, in the colours shown, printed by hand'],['Price','$42 · $45 in 2XL and 3XL']]; if(it.line.indexOf('offworld')===0) return [[")
    # copy: collections intro, tile, shirts intro, designs intro, designs chip
    h = rep(h, '<p>Three lines, one hand. Pick a line to see every design in it.</p>', '<p>Four lines, one hand. Pick a line to see every design in it.</p>')
    first = 'n73-trust-but-test'
    tile = (f'''        <article class="line" aria-labelledby="line-{KEY}-h">
          <figure class="line-art" oncontextmenu="return false"><img src="img/lines/n73-tile.webp" width="800" height="600" loading="lazy" decoding="async" draggable="false" alt="Trust But Test {LINE} preview, watermarked"></figure>
          <div class="line-body">
            <p class="eyebrow">{LINE} &middot; <span data-count="{KEY}">{len(D['designs'])}</span> designs</p>
            <h3 id="line-{KEY}-h">Messages hiding in plain sight</h3>
            <p>Thirty-six shirts that say something once you read them right: the bold characters, the meter dials, the bubbles, the hex. &ldquo;N3V3R H0LD Y0UR BR34TH.&rdquo; &ldquo;7RU57 8U7 7357.&rdquo; &ldquo;0N3 M0R3 P4CK.&rdquo; Dive, utility and power, mindset, flight, code and RC cars, each printed full front on a colour picked for its theme.</p>
            <p class="line-links"><a class="btn" href="#shirts" data-deck-line="{KEY}" data-umami-event="line-open" data-umami-event-line="{KEY}">See the {LINE} shirts</a><a class="txt" href="#designs" data-show-line="{KEY}" data-umami-event="line-art" data-umami-event-line="{KEY}">The art &rarr;</a></p>
          </div>
        </article>
''')
    h = rep(h, '        </article>\n      </div>\n    </section>\n\n    <section id="shirts"', '        </article>\n' + tile + '      </div>\n    </section>\n\n    <section id="shirts"')
    h = rep(h, 'and the thirty Off-World Hunt Club lines, each on a light tee and again on a dark one (mockups, one garment colour each way).',
            'the thirty Off-World Hunt Club lines, each on a light tee and again on a dark one, and the thirty-six 1N73LL1G3NC3 hidden-message fronts (mockups, one garment colour each).')
    h = rep(h, '<p>Every plate and Certified-ish back, drawn by hand, and the thirty Off-World Hunt Club lines. Tap a design',
            '<p>Every plate and Certified-ish back, drawn by hand, the thirty Off-World Hunt Club lines and the thirty-six 1N73LL1G3NC3 fronts. Tap a design')
    h = rep(h, '<button type="button" class="chip" data-l="offworld" data-umami-event="designs-line" data-umami-event-line="offworld" aria-pressed="false">Off-World Hunt Club</button>',
            f'<button type="button" class="chip" data-l="offworld" data-umami-event="designs-line" data-umami-event-line="offworld" aria-pressed="false">Off-World Hunt Club</button>\n        <button type="button" class="chip" data-l="{KEY}" data-umami-event="designs-line" data-umami-event-line="{KEY}" aria-pressed="false">{LINE}</button>')
# designs chip counts, from the grid itself
grid = h[h.index('<div class="dz-grid" id="dz-grid">'):h.index('<p class="dz-note">All artwork')]
cnt = {k: len(re.findall(rf'<figure class="dz" data-status="{k}"', grid)) for k in ('available', 'completed', 'progress')}
h = re.sub(r'(data-f="all"[^>]*>All <span class="mono">)\d+', rf'\g<1>{sum(cnt.values())}', h)
for k in cnt:
    h = re.sub(rf'(data-f="{k}"[^>]*>[^<]*<span class="mono">)\d+', rf'\g<1>{cnt[k]}', h)
open(p, 'w', encoding='utf-8').write(h)
print('index.html updated; designs grid', cnt)
