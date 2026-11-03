#!/usr/bin/env python3
"""The Off-World Hunt Club on the site, in the Certified-ish format. Idempotent.

Usage: tools/offworld.py <render dir>      (the output of tools/offworld_render.py)

- img/offworld/<slug>-{front,back}.webp (1200) + -t (600): the light-line mockups the cards use
- img/offworld/dark/<slug>-{front,back}.webp: the dark-line mockups, not linked from any page (the Shopify image source)
- img/designs/<slug>.webp: watermarked preview for the designs grid and the shirt viewer
- custom/art/<slug>.webp, <slug>-w.webp, custom/t/<slug>.webp: the Make it yours art and thumbnails
- index.html: 30 cards in #sh-grid (data-line="offworld"), the deck config, a collection tile, 30 designs-grid cards,
  a designs chip, counts and copy
- custom/index.html: an Off-World Hunt Club tab in the Back step, with white-ink art on dark garments
Run tools/bust.py afterwards.
"""
import os, re, sys, json, html as H
from PIL import Image

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/offworld_out'
D = json.load(open(f'{SITE}/tools/offworld_designs.json'))
LINE = D['line']; KEY = D['key']
OUT = f'{SITE}/img/offworld'; os.makedirs(f'{OUT}/dark', exist_ok=True)
os.makedirs(f'{SITE}/custom/t', exist_ok=True); os.makedirs(f'{SITE}/custom/art', exist_ok=True)


def rep(h, old, new, count=1):
    assert h.count(old) == count, (h.count(old), old[:80]); return h.replace(old, new)


# 1. images --------------------------------------------------------------------------------------------------------------
tot = 0
for d in D['designs']:
    s = d['slug']
    for view in ('front', 'back'):
        im = Image.open(f'{SRC}/{s}-{view}.png').convert('RGB')
        im.resize((1200, 1200), Image.LANCZOS).save(f'{OUT}/{s}-{view}.webp', 'webp', quality=86, method=6)
        im.resize((600, 600), Image.LANCZOS).save(f'{OUT}/{s}-{view}-t.webp', 'webp', quality=80, method=6)
        Image.open(f'{SRC}/{s}-dark-{view}.png').convert('RGB').resize((1200, 1200), Image.LANCZOS).save(f'{OUT}/dark/{s}-{view}.webp', 'webp', quality=86, method=6)
        tot += os.path.getsize(f'{OUT}/{s}-{view}.webp') + os.path.getsize(f'{OUT}/{s}-{view}-t.webp') + os.path.getsize(f'{OUT}/dark/{s}-{view}.webp')
    Image.open(f'{SRC}/designs/{s}.webp').save(f'{SITE}/img/designs/{s}.webp', 'webp', quality=82, method=6)
    for suf in ('', '-w'):
        Image.open(f'{SRC}/art/{s}{suf}.webp').save(f'{SITE}/custom/art/{s}{suf}.webp', 'webp', quality=80, method=6, exact=True)
    # Make it yours thumbnail, 320×240 on white, like custom/t/cert-*.webp
    art = Image.open(f'{SRC}/art/{s}.webp').convert('RGBA')
    bb = art.getchannel('A').getbbox(); art = art.crop(bb)
    sc = min(300 / art.width, 220 / art.height); art = art.resize((max(1, int(art.width * sc)), max(1, int(art.height * sc))), Image.LANCZOS)
    th = Image.new('RGBA', (320, 240), (255, 255, 255, 255)); th.alpha_composite(art, ((320 - art.width) // 2, (240 - art.height) // 2))
    th.convert('RGB').save(f'{SITE}/custom/t/{s}.webp', 'webp', quality=80, method=6)
print('images:', round(tot / 1e6, 2), 'MB in img/offworld')

# 2. home page -----------------------------------------------------------------------------------------------------------
p = f'{SITE}/index.html'; h = open(p, encoding='utf-8').read()
CUSTOM = '/custom/#colour={c}&tab=offworld&back={s}&bsize=full&chest=dsmark&cpos=left&sleeve=none'


def card(d):
    s = d['slug']; col = D['colours']['light'][d['light']]; n = d['name']; low = col['name'].lower(); t = d['text']
    return (f'<figure class="sh" data-line="{KEY}" data-slug="{s}" data-code="OW{d["n"]:02d}" data-colour="{H.escape(col["name"])}" data-hex="{col["hex"]}" '
            f'data-art="img/designs/{s}.webp" data-text="{H.escape(t)}" data-custom="{CUSTOM.format(c=d["light"], s=s)}" hidden>'
            f'<button type="button" class="sh-img" data-front="img/offworld/{s}-front.webp" data-back="img/offworld/{s}-back.webp" data-side="back" '
            f'data-cap="{H.escape(n)} · {H.escape(col["name"])} · Comfort Colors 1717 · mockup" data-umami-event="shirt-open" data-umami-event-site="{s}" '
            f'aria-label="Open mockup: {H.escape(n)} shirt, {H.escape(low)}">'
            f'<img src="img/offworld/{s}-back-t.webp" width="600" height="600" loading="lazy" decoding="async" '
            f'alt="{H.escape(n)} {LINE} shirt in {H.escape(low)}, mockup: the line in the off-world script on the back, translated, with {H.escape(d["punch"].lower())} in red"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(n)}</span><span class="pill available">Coming soon</span></span>'
            f'<span class="dz-s">{H.escape(col["name"])} · {LINE}</span>'
            f'<span class="sh-flip" role="group" aria-label="Show front or back"><button type="button" data-side="front" aria-pressed="false">Front</button><button type="button" class="on" data-side="back" aria-pressed="true">Back</button></span></figcaption></figure>')


def dz(d):
    s = d['slug']; n = d['name']
    return (f'<figure class="dz" data-status="completed" data-line="{KEY}"><button type="button" class="dz-img" data-full="img/designs/{s}.webp" '
            f'data-cap="{H.escape(n)} · {LINE} · the full back print" data-umami-event="design-open" data-umami-event-design="{s}" aria-label="Open the full design: {H.escape(n)}">'
            f'<img src="img/designs/{s}.webp" width="450" height="620" loading="lazy" decoding="async" draggable="false" alt="{H.escape(n)} design preview, watermarked"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(n)}</span><span class="pill completed">Art finished</span></span><span class="dz-s">{H.escape(d["text"])}</span></figcaption></figure>')


h = re.sub(rf'<figure class="sh" data-line="{KEY}".*?</figure>', '', h, flags=re.S)
h = re.sub(rf'<figure class="dz" data-status="completed" data-line="{KEY}".*?</figure>', '', h, flags=re.S)
cards = ''.join(card(d) for d in D['designs']); dzs = ''.join(dz(d) for d in D['designs'])
h = rep(h, '</div>\n      <p class="dz-note">Colours are the garment colours each site was printed on', cards + '</div>\n      <p class="dz-note">Colours are the garment colours each site was printed on')
h = rep(h, '\n      </div>\n      <p class="dz-note">All artwork &copy; 2026', '\n        ' + dzs + '\n      </div>\n      <p class="dz-note">All artwork &copy; 2026')
print('cards:', len(D['designs']), '× 2')

first = D['designs'][0]['slug']
if f"['{KEY}','{LINE}']" not in h:
    # deck
    h = rep(h, "lines:[['plates','Signature Series'],['dark','Signature Series Dark'],['certifiedish','Certified-ish']], step:{plates:64,dark:64,certifiedish:44},",
            f"lines:[['plates','Signature Series'],['dark','Signature Series Dark'],['certifiedish','Certified-ish'],['{KEY}','{LINE}']], step:{{plates:64,dark:64,certifiedish:44,{KEY}:44}},")
    h = rep(h, "front:b.dataset.front, back:b.dataset.back, art:f.dataset.art||'', thumb:img.getAttribute('src'), cap:b.dataset.cap, sub:sub,",
            "front:b.dataset.front, back:b.dataset.back, art:f.dataset.art||'', thumb:img.getAttribute('src'), cap:b.dataset.cap, sub:sub, text:f.dataset.text||'',")
    h = rep(h, "eyebrow:function(it){ return it.line==='plates'?'Signature Series':it.line==='dark'?'Signature Series Dark':'Certified-ish'; },",
            f"eyebrow:function(it){{ return it.line==='plates'?'Signature Series':it.line==='dark'?'Signature Series Dark':it.line==='{KEY}'?'{LINE}':'Certified-ish'; }},")
    h = rep(h, "sub:function(it){ return it.site?it.site.place+(it.line==='dark'?' · dark line':''):'Certified-ish back print · DS mark'; },",
            f"sub:function(it){{ return it.site?it.site.place+(it.line==='dark'?' · dark line':''):it.line==='{KEY}'?it.text:'Certified-ish back print · DS mark'; }},")
    h = rep(h, "blurb:function(){ return 'One tongue-in-cheek diagram for the specialty in your logbook, printed full size on the back.'; },",
            f"blurb:function(it){{ return it.line==='{KEY}'?'One line in the hunters\\u2019 script across the back, translated underneath with one word in red; the DS mark carries that word on the chest, in glyphs.':'One tongue-in-cheek diagram for the specialty in your logbook, printed full size on the back.'; }},")
    h = rep(h, "defaultView:function(it){ return it.line==='certifiedish'?'back':'front'; },",
            f"defaultView:function(it){{ return it.line==='certifiedish'||it.line==='{KEY}'?'back':'front'; }},")
    h = rep(h, "(sig?'Front · worn, photographed':dk?'Front · mockup on the photographed shirt, white ink':'Front · mockup, DS mark along the sleeve'); },",
            f"(sig?'Front · worn, photographed':dk?'Front · mockup on the photographed shirt, white ink':it.line==='{KEY}'?'Front · mockup, DS mark and the word in glyphs on the chest':'Front · mockup, DS mark along the sleeve'); }},")
    h = rep(h, "if(it.line==='dark') return [['Back','Full site illustration with facts, species and water conditions'],",
            f"if(it.line==='{KEY}') return [['Back','The line in the off-world script, 12 × 16 in, translated beneath it with the punch word in red'],['Chest','The DS mark with the punch word in glyphs, left chest'],['Shirt',sw],['Ink','Water-based black and red, printed by hand'],['Price','$42 · $45 in 2XL and 3XL']]; if(it.line==='dark') return [['Back','Full site illustration with facts, species and water conditions'],")
    # copy: collections intro, tile, shirts intro, designs intro, designs chip
    h = rep(h, '<p>Two lines, one hand. Pick a line to see every design in it.</p>', '<p>Three lines, one hand. Pick a line to see every design in it.</p>')
    tile = (f'''        <article class="line" aria-labelledby="line-{KEY}-h">
          <figure class="line-art cert" oncontextmenu="return false"><img src="img/designs/{first}.webp" width="450" height="620" loading="lazy" decoding="async" draggable="false" alt="{D['designs'][0]['name']} {LINE} preview, watermarked"></figure>
          <div class="line-body">
            <p class="eyebrow">{LINE} &middot; <span data-count="{KEY}">{len(D['designs'])}</span> designs</p>
            <h3 id="line-{KEY}-h">A hunters&rsquo; script from somewhere else</h3>
            <p>Thirty lines in an off-world script, each translated underneath with one word in red: &ldquo;I&rsquo;m not ignoring you. I&rsquo;m cloaked.&rdquo; &ldquo;Came for the trophy. Stayed for the reef.&rdquo; &ldquo;Dive deep. Hunt deeper.&rdquo; The DS mark carries the word on the chest, in glyphs.</p>
            <p class="line-links"><a class="btn" href="#shirts" data-deck-line="{KEY}" data-umami-event="line-open" data-umami-event-line="{KEY}">See the Off-World shirts</a><a class="txt" href="#designs" data-show-line="{KEY}" data-umami-event="line-art" data-umami-event-line="{KEY}">The art &rarr;</a></p>
          </div>
        </article>
''')
    h = rep(h, '        </article>\n      </div>\n    </section>\n\n    <section id="shirts"', '        </article>\n' + tile + '      </div>\n    </section>\n\n    <section id="shirts"')
    h = rep(h, 'and the twenty Certified-ish backs on the tee they ship on. Every design gets its own garment colour, so each deck is the palette of its line.',
            'the twenty Certified-ish backs on the tee they ship on, and the thirty Off-World Hunt Club lines (mockups, one garment colour each). Every design gets its own garment colour, so each deck is the palette of its line.')
    h = rep(h, '<p>Every plate and Certified-ish back, drawn by hand. Tap a design for the full back print, facts and all.',
            '<p>Every plate and Certified-ish back, drawn by hand, and the thirty Off-World Hunt Club lines. Tap a design for the full back print, facts and all.')
    h = rep(h, '<button type="button" class="chip" data-l="certifiedish" data-umami-event="designs-line" data-umami-event-line="certifiedish" aria-pressed="false">Certified-ish</button>',
            f'<button type="button" class="chip" data-l="certifiedish" data-umami-event="designs-line" data-umami-event-line="certifiedish" aria-pressed="false">Certified-ish</button>\n        <button type="button" class="chip" data-l="{KEY}" data-umami-event="designs-line" data-umami-event-line="{KEY}" aria-pressed="false">{LINE}</button>')
# designs chip counts, from the grid itself
grid = h[h.index('<div class="dz-grid" id="dz-grid">'):h.index('<p class="dz-note">All artwork')]
cnt = {k: len(re.findall(rf'<figure class="dz" data-status="{k}"', grid)) for k in ('available', 'completed', 'progress')}
h = re.sub(r'(data-f="all"[^>]*>All <span class="mono">)\d+', rf'\g<1>{sum(cnt.values())}', h)
for k in cnt:
    h = re.sub(rf'(data-f="{k}"[^>]*>[^<]*<span class="mono">)\d+', rf'\g<1>{cnt[k]}', h)
open(p, 'w', encoding='utf-8').write(h)
print('index.html updated; designs grid', cnt)

# 3. Make it yours ---------------------------------------------------------------------------------------------------------
p = f'{SITE}/custom/index.html'; c = open(p, encoding='utf-8').read()
m = re.search(r'<script type="application/json" id="custom-data">(.*?)</script>', c, re.S)
data = json.loads(m.group(1))
data['offworld'] = [{'slug': d['slug'], 'name': d['name'], 'text': d['text'], 'w': 750, 'h': 1000} for d in D['designs']]
c = c[:m.start(1)] + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + c[m.end(1):]
if 'data-dtab="offworld"' not in c:
    c = rep(c, "D.certs.forEach(function(c){byId[c.slug]=c}); (D.extra||[])", "D.certs.forEach(function(c){byId[c.slug]=c}); (D.offworld||[]).forEach(function(c){c.ow=true; byId[c.slug]=c}); (D.extra||[])")
    c = rep(c, '<span class="sub">a dive-site plate or a Certified-ish back</span>', '<span class="sub">a dive-site plate, a Certified-ish back or an Off-World line</span>')
    c = rep(c, '<button type="button" class="chip" data-dtab="certs">Certified-ish</button>', '<button type="button" class="chip" data-dtab="certs">Certified-ish</button><button type="button" class="chip" data-dtab="offworld">Off-World Hunt Club</button>')
    c = rep(c, "var list=S.tab==='plates'?D.plates:S.tab==='certs'?D.certs:[];", "var list=S.tab==='plates'?D.plates:S.tab==='certs'?D.certs:S.tab==='offworld'?(D.offworld||[]):[];")
    c = rep(c, "(d.place?'<small>'+d.place+'</small>':'<small>Certified-ish</small>')", "(d.place?'<small>'+d.place+'</small>':d.ow?'<small>'+d.text+'</small>':'<small>Certified-ish</small>')")
    c = rep(c, "if(pair[1]==='tab'){ if(S.tab==='none') S.back='none'; else if(S.back==='none'||(S.tab==='plates')!==!!(byId[S.back]&&byId[S.back].flag)) S.back=(S.tab==='plates'?D.plates:D.certs)[0].slug; }",
            "if(pair[1]==='tab'){ if(S.tab==='none') S.back='none'; else { var tl=S.tab==='plates'?D.plates:S.tab==='certs'?D.certs:(D.offworld||[]); if(S.back==='none'||!tl.some(function(x){return x.slug===S.back})) S.back=tl[0].slug; } }")
    c = rep(c, "if(S.back!=='none' && !byId[S.back]) S.back='black-bart';", "if(S.back!=='none' && !byId[S.back]) S.back='black-bart'; if(byId[S.back]&&byId[S.back].ow) S.tab='offworld';")
    c = rep(c, "var bsrc='art/'+d.slug+'.webp', bw=d.w, bh=d.h; if(full&&d.flag){ bsrc='art/'+d.slug+'-back.webp'; bw=750; bh=1000; f=fit(bw,bh,mw,mh); }",
            "var bsrc='art/'+d.slug+'.webp', bw=d.w, bh=d.h, bbl=true; if(full&&d.flag){ bsrc='art/'+d.slug+'-back.webp'; bw=750; bh=1000; f=fit(bw,bh,mw,mh); } if(d.ow){ bbl=false; if(dark()) bsrc='art/'+d.slug+'-w.webp'; } /* Off-World art keeps its red: no blend, a white-ink twin on dark garments */")
    c = rep(c, "var bn=img(bsrc,bw,bh,300,top+f[1]/2,mw,mh,true,0); B.appendChild(bn); }", "var bn=img(bsrc,bw,bh,300,top+f[1]/2,mw,mh,bbl,0); B.appendChild(bn); }")
    c = rep(c, "$('#bsize-upper').title=certBack()?'A Certified-ish design goes full back, not smaller':'';", "$('#bsize-upper').title=certBack()?'A Certified-ish or Off-World design goes full back, not smaller':'';")
    c = rep(c, "(byId[S.back].flag?' plate':' (Certified-ish)')", "(byId[S.back].flag?' plate':byId[S.back].ow?' (Off-World Hunt Club)':' (Certified-ish)')")
    c = rep(c, '<p><b>Back designs</b> go on the back: the dive-site plates and the Certified-ish backs.', '<p><b>Back designs</b> go on the back: the dive-site plates, the Certified-ish backs and the Off-World Hunt Club lines (full back only).')
open(p, 'w', encoding='utf-8').write(c)
print('custom/index.html updated')
