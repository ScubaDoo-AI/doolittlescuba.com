#!/usr/bin/env python3
"""All 14 site caps on Printful-stocked Flexfit 6277 colours (Eric, 12 Nov 2026: "correct this to be Printful stocked colors").
The six caps that were going to the outside embroiderer move to the nearest dark colour Printful carries:
  Blue Grotto      purple -> Royal Blue      Rainbow River    maroon -> Black
  Bridge Span 14   brown  -> Olive           Somosomo Strait  spruce -> Olive
  The Thistlegorm  spruce -> Dark Grey       Vuna Reef        spruce -> Olive
What this does (idempotent):
  img/hats/dark/        the six re-rendered caps (front + back, from build_caps_v3.py with the new colours) -> 1200 px WebP + 600 px thumbs
  index.html            the six hats-deck figures' data-colour / data-hex; the spec sheet's "white and navy on maroon" thread rule goes
  custom/index.html     cap colours offered on Make it yours = Printful's dark set: Navy, Black, Dark grey, Olive, Royal blue
                        (Brown, Purple, Maroon, Spruce drop out — nothing could make them)
  tools/pairs.py        the cap-colour column for the six (the store copy and the pair images read it)
Then: tools/pairs.py images · tools/bust.py · the store (tools/caps_printful_colours_store.py) · tools/printful_caps.py + the link workflow.
usage: tools/caps_printful_colours.py <renders_dir>"""
import os, re, sys, json, glob
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW = {  # cap slug: (colour name, swatch hex, pairs.py colour word)
    'blue-grotto': ('Royal blue', '#1E4597', 'royal blue'), 'bridge-span-14': ('Olive', '#4A4C33', 'olive'),
    'rainbow-river': ('Black', '#212327', 'black'), 'somosomo-strait': ('Olive', '#4A4C33', 'olive'),
    'the-thistlegorm': ('Dark grey', '#484A4B', 'dark grey'), 'vuna-reef': ('Olive', '#4A4C33', 'olive')}
OLD = {'blue-grotto': 'purple', 'bridge-span-14': 'brown', 'rainbow-river': 'maroon', 'somosomo-strait': 'spruce', 'thistlegorm': 'spruce', 'vuna-reef': 'spruce'}

# 1. renders
src = sys.argv[1] if len(sys.argv) > 1 else ''; out = f'{ROOT}/img/hats/dark'; n = 0
for f in sorted(glob.glob(os.path.join(src, 'cap-dark-*.jpg'))) if src else []:
    stem = os.path.basename(f)[:-4]; im = Image.open(f).convert('RGB')
    im.resize((1200, 1200), Image.LANCZOS).save(f'{out}/{stem}.webp', quality=84, method=6)
    im.resize((600, 600), Image.LANCZOS).save(f'{out}/{stem}-t.webp', quality=82, method=6); n += 1
print(n, 'renders ->', 2 * n, 'images in img/hats/dark/')

# 2. index.html
p = f'{ROOT}/index.html'; h = h0 = open(p, encoding='utf-8').read()
for slug, (name, hx, _) in NEW.items():
    m = re.search(rf'(data-slug="cap-dark-{slug}"[^>]*?)data-colour="[^"]*" data-hex="[^"]*"', h); assert m, slug
    h = h[:m.start()] + m.group(1) + f'data-colour="{name}" data-hex="{hx}"' + h[m.end():]
old = "thread=/maroon/i.test(it.colour||'')?'white and navy':'white and red'"
if old in h: h = h.replace(old, "thread='white and red'")
assert not re.search(r'data-colour="(Purple|Brown|Maroon|Spruce)"', h)
if h != h0: open(p, 'w', encoding='utf-8').write(h); print('index.html: six figures recoloured')

# 3. custom/index.html
p = f'{ROOT}/custom/index.html'; c = c0 = open(p, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="custom-data">)(.*?)(</script>)', c, re.S); d = json.loads(m.group(2))
cols = [x for x in d['colours'] if x['slug'] not in ('brown', 'purple', 'maroon', 'spruce')]
if not any(x['slug'] == 'royal-blue' for x in cols):
    i = next(k for k, x in enumerate(cols) if x['slug'] == 'olive')
    cols.insert(i + 1, {'slug': 'royal-blue', 'name': 'Royal blue', 'hex': '#1E4597', 'tone': 'cool', 'dark': True, 'cap': True})
d['colours'] = cols
c = c[:m.start(2)] + json.dumps(d, separators=(',', ':'), ensure_ascii=False) + c[m.end(2):]
if c != c0: open(p, 'w', encoding='utf-8').write(c); print('custom/index.html: cap colours = Navy, Black, Dark grey, Olive, Royal blue')

# 4. tools/pairs.py
p = f'{ROOT}/tools/pairs.py'; t = t0 = open(p, encoding='utf-8').read()
for slug, old in OLD.items():
    key = NEW['the-thistlegorm' if slug == 'thistlegorm' else slug][2]
    m = re.search(rf"\(\s*'{slug}',.*?\)", t); assert m, slug
    row = m.group(0); new_row = re.sub(rf"'{old}'(, '[^']*', '[^']*'\))$", lambda mm: f"'{key}'" + mm.group(1), row)
    t = t.replace(row, new_row)
if t != t0: open(p, 'w', encoding='utf-8').write(t); print('tools/pairs.py: cap colours updated')
