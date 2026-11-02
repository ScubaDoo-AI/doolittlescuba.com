#!/usr/bin/env python3
"""The Signature Series dark line on the home page: copies the dark mockups (made by darkset.py from the photographed
light shirts) into img/shirts/dark/, adds one card per site to #sh-grid (data-line="dark") and teaches the shirts deck
the third line. Idempotent. Usage: tools/darkline.py <render_dir>   (expects <slug>-front.png / <slug>-back.png)"""
import os, re, sys, json, html as H
from PIL import Image

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/darkset/out'
OUT = f'{SITE}/img/shirts/dark'; os.makedirs(OUT, exist_ok=True)
DARK = {  # slug: (Comfort Colors name, custom-page slug, hex as it photographs, tone)
    'black-bart': ('Pepper', 'pepper', '#464340'), 'bridge-span-14': ('Espresso', 'espresso', '#4B3631'), 'blue-grotto': ('Grape', 'grape', '#332552'),
    'blue-water-park': ('Black', 'black', '#222426'), 'dampier-strait': ('True navy', 'true-navy', '#15284A'), 'bali': ('Denim', 'denim', '#3F5163'),
    'rainbow-river': ('Wine', 'wine', '#4D2A48'), 'navy-llcat': ('Navy', 'navy', '#1B2D4A'), 'dive-land-park': ('Graphite', 'graphite', '#262C33'),
    'thurmond-dam': ('Midnight', 'midnight', '#22365A'), 'thistlegorm': ('Blue spruce', 'blue-spruce', '#3A5752'), 'somosomo-strait': ('Emerald', 'emerald', '#0F6156'),
    'rainbow-reef': ('Dark sage', 'dark-sage', '#444D33'), 'vuna-reef': ('Moss', 'moss', '#27392E')}

p = f'{SITE}/index.html'; h = open(p, encoding='utf-8').read()
sites = {s['slug']: s for s in json.loads(re.search(r'<script type="application/json" id="sites-data">(.*?)</script>', h, re.S).group(1))}
order = [s for s in sites if s in DARK]                                   # the catalog order

# 1. images: 1200 px for the site and the shop, 600 px thumbnails ---------------------------------------------------
tot = 0
for slug in order:
    for view in ('front', 'back'):
        im = Image.open(f'{SRC}/{slug}-{view}.png').convert('RGB')
        im.resize((1200, 1200), Image.LANCZOS).save(f'{OUT}/{slug}-{view}.webp', 'webp', quality=86, method=6)
        im.resize((600, 600), Image.LANCZOS).save(f'{OUT}/{slug}-{view}-t.webp', 'webp', quality=80, method=6)
        tot += os.path.getsize(f'{OUT}/{slug}-{view}.webp') + os.path.getsize(f'{OUT}/{slug}-{view}-t.webp')
print('img/shirts/dark:', len(os.listdir(OUT)), 'files,', round(tot / 1e6, 2), 'MB')

# 2. cards ---------------------------------------------------------------------------------------------------------------
def card(slug):
    s = sites[slug]; name, cslug, hexc = DARK[slug]; n = s['name']; low = name.lower()
    return (f'<figure class="sh" data-line="dark" data-slug="{slug}" data-code="{s["code"] if "code" in s else ""}" data-colour="{H.escape(name)}" data-hex="{hexc}" '
            f'data-art="img/designs/{slug}-back.webp" data-guide="/sites/{slug}/" data-custom="/custom/#colour={cslug}&back={slug}&site={slug}">'
            f'<button type="button" class="sh-img" data-front="img/shirts/dark/{slug}-front.webp" data-back="img/shirts/dark/{slug}-back.webp" '
            f'data-cap="{H.escape(n)} · {H.escape(name)} · Comfort Colors 1717 · dark line, white ink" data-umami-event="shirt-open" data-umami-event-site="{slug}-dark" '
            f'aria-label="Open mockup: {H.escape(n)} shirt, {H.escape(low)}, dark line">'
            f'<img src="img/shirts/dark/{slug}-front-t.webp" width="600" height="600" loading="lazy" decoding="async" '
            f'alt="{H.escape(n)} shirt in {H.escape(low)}, dark line: the photographed shirt re-dyed, chest print in white ink with the dive flag, site name and coordinates"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(n)}</span><span class="pill available">Coming soon</span></span>'
            f'<span class="dz-s">{H.escape(name)} · white ink · <a href="/sites/{slug}/" data-umami-event="shirt-site">site guide</a></span>'
            f'<span class="sh-flip" role="group" aria-label="Show front or back"><button type="button" class="on" data-side="front" aria-pressed="true">Front</button><button type="button" data-side="back" aria-pressed="false">Back</button></span></figcaption></figure>')
codes = {m.group(2): m.group(1) for m in re.finditer(r'data-code="([A-Z0-9]+)" data-colour="[^"]*" data-hex="[^"]*" data-art="img/designs/([a-z0-9-]+)-back', h)}
for slug in order: sites[slug]['code'] = codes[slug]
h = re.sub(r'<figure class="sh" data-line="dark".*?</figure>', '', h, flags=re.S)       # replace any earlier version
anchor = '<figure class="sh" data-line="certifiedish"'
i = h.index(anchor); h = h[:i] + ''.join(card(s) for s in order) + h[i:]
print('cards:', len(order))

# 3. the deck knows the line ---------------------------------------------------------------------------------------------
def rep(old, new):
    global h; assert h.count(old) == 1, old[:70]; h = h.replace(old, new)
if "['dark','Signature Series Dark']" not in h:
    rep("lines:[['plates','Signature Series'],['certifiedish','Certified-ish']], step:{plates:64,certifiedish:44},",
        "lines:[['plates','Signature Series'],['dark','Signature Series Dark'],['certifiedish','Certified-ish']], step:{plates:64,dark:64,certifiedish:44},")
    rep("eyebrow:function(it){ return it.line==='plates'?'Signature Series':'Certified-ish'; },",
        "eyebrow:function(it){ return it.line==='plates'?'Signature Series':it.line==='dark'?'Signature Series Dark':'Certified-ish'; },")
    rep("defaultView:function(it){ return it.line==='plates'?'front':'back'; },",
        "defaultView:function(it){ return it.line==='certifiedish'?'back':'front'; },")
    rep("caption:function(it,v){ var sig=it.line==='plates'; return v==='art'?(sig?'The back print · plate, facts, species and water · watermarked':'Watermarked preview of the back print'):v==='back'?(sig?'Back · worn, photographed':'Back · mockup'):(sig?'Front · worn, photographed':'Front · mockup, DS mark along the sleeve'); },",
        "caption:function(it,v){ var sig=it.line==='plates', dk=it.line==='dark'; return v==='art'?(sig||dk?'The back print · plate, facts, species and water · watermarked':'Watermarked preview of the back print'):v==='back'?(sig?'Back · worn, photographed':dk?'Back · mockup on the photographed shirt, white ink':'Back · mockup'):(sig?'Front · worn, photographed':dk?'Front · mockup on the photographed shirt, white ink':'Front · mockup, DS mark along the sleeve'); },")
    rep("specs:function(it){ var sw='<span class=\"sw\"></span>Comfort Colors 1717, garment-dyed · '+esc(it.colour); return it.line==='plates'\n      ?[",
        "specs:function(it){ var sw='<span class=\"sw\"></span>Comfort Colors 1717, garment-dyed · '+esc(it.colour); if(it.line==='dark') return [['Back','Full site illustration with facts, species and water conditions'],['Chest','Site name, dive flag and GPS coordinates'],['Sleeve','Signature shark mark'],['Shirt',sw],['Ink','Water-based white, printed by hand · the flag in colour'],['Price','$42 · $45 in 2XL and 3XL']]; return it.line==='plates'\n      ?[")
    rep("sub:function(it){ return it.site?it.site.place:'Certified-ish back print · DS mark'; },",
        "sub:function(it){ return it.site?it.site.place+(it.line==='dark'?' · dark line':''):'Certified-ish back print · DS mark'; },")
    # copy
    rep("<p>The fourteen sites photographed on the shirt, and the twenty Certified-ish backs on the tee they ship on. Every design gets its own garment colour, so the deck is the palette of the line. Run across the tabs to pull a shirt forward; open it for the photos, the facts and the back print.</p>",
        "<p>The fourteen sites photographed on the shirt, the same fourteen as the dark line (white ink on a dark garment, shown as mockups built from those photographs), and the twenty Certified-ish backs on the tee they ship on. Every design gets its own garment colour, so each deck is the palette of its line. Run across the tabs to pull a shirt forward; open it for the photos, the facts and the back print.</p>")
    rep("<p>Wrecks, springs and reefs drawn from real dives, labelled with depths and landmarks, and screen-printed in one colour on soft pastel tees.</p>",
        "<p>Wrecks, springs and reefs drawn from real dives, labelled with depths and landmarks, and printed in one colour: black on the soft pastel tees, white on the dark line.</p>")
    rep('data-umami-event-line="plates">See the shirts</a>', 'data-umami-event-line="plates">See the shirts</a><a class="txt" href="#shirts" data-deck-line="dark" data-umami-event="line-open" data-umami-event-line="dark">The dark line &rarr;</a>')
open(p, 'w', encoding='utf-8').write(h)
print('index.html updated')
