#!/usr/bin/env python3
"""Custom shirt per series: any design from the series on any shirt colour, light and dark (Eric, 22 Nov 2026:
"Each product shirt series should offer a custom shirt option any shirt color any design from the series split light
and dark"). Answers that day: a picker on the product page; price = the series tee + $5; all five series.

Ten Shopify products, one Light and one Dark per series, Size the only variant; SKU DS-CU-<SER>-<L|D>-<size>.
The product page's picker (theme block ds-series-custom) sends two line properties: "Design" (the design's name) and
"Shirt colour", plus "_design" (its slug) and "_colour" (the colour slug). The custom-orders job
(tools/custom_order.py) turns a paid line into a Printful draft with resolve() below: the catalog shirt's own print
files (same placements, sizes, ink) on the chosen Comfort Colors 1717 colour. Light shirts get the dark-ink files
(the catalog's light line); dark shirts the white-ink files (the dark line). 1N73LL1G3NC3 and Surface Interval
exist only as dark-shirt art; their light version is the same art recoloured (white and light inks to navy and deep
blue, red kept), made by light_ink() when the order is drafted and for the previews.

  tools/series_custom.py --data            # write shopify-theme/assets/ds-series-custom.json (the picker's data)
  tools/series_custom.py --previews        # render the picker's art previews into img/custom-series/ (needs the CDN)
  tools/series_custom.py --resolve SIG L black-bart navy M    # print the Printful item for one line
"""
import os, sys, re, io, json, colorsys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
NAVY = (16, 42, 84)
SKU_RE = re.compile(r'^DS-CU-(SIG|CI|OW|N73|SIB)-([LD])-(S|M|L|XL|2XL|3XL)$')

# series key, title, collection page on the site, catalog price S-XL (2XL/3XL +$3), the shop handle stem
SERIES = {
    'SIG': dict(title='Signature Series', page='/signature/', price=42, handle='signature-series'),
    'CI':  dict(title='Certified-ish', page='/certified-ish/', price=40, handle='certified-ish'),
    'OW':  dict(title='Off-World Hunt Club', page='/off-world/', price=38, handle='off-world-hunt-club'),
    'N73': dict(title='1N73LL1G3NC3', page='/1n73ll1g3nc3/', price=36, handle='1n73ll1g3nc3'),
    'SIB': dict(title='Surface Interval · Boat Banter', page='/surface-interval/', price=38, handle='surface-interval-boat-banter'),
}
SURCHARGE = 5
TONE = {'L': 'Light', 'D': 'Dark'}


def price(ser, size):
    return SERIES[ser]['price'] + SURCHARGE + (3 if size in ('2XL', '3XL') else 0)


def colours():
    """The Make it yours tee colours (custom/index.html), split light / dark, with their Comfort Colors names."""
    import custom_tee as T
    s = open(os.path.join(ROOT, 'custom', 'index.html'), encoding='utf-8').read()
    d = json.loads(re.search(r'<script type="application/json" id="custom-data">(.*?)</script>', s, re.S).group(1))
    out = {'L': [], 'D': []}
    for c in d['colours']:
        if c.get('cap') and not c.get('tee'): continue
        out['D' if c.get('dark') else 'L'].append(dict(slug=c['slug'], name=c['name'], hex=c['hex'], cc=T.CC[c['slug']]))
    return out


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def designs():
    """series → [{slug, name, code, files: {L: [...], D: [...]}, hero: placement for the preview}] in catalog order.
    A files list is Printful's [{type, url, position}]; files['L'] is None where the light version is recoloured."""
    import printful_signature as S, printful_certifiedish as C, printful_offworld as O, printful_n73 as N, printful_aquatic as A
    out = {k: [] for k in SERIES}

    def add(ser, slug, name, code, line, files, hero):
        e = next((x for x in out[ser] if x['slug'] == slug), None)
        if not e:
            e = dict(slug=slug, name=name, code=code, files={'L': None, 'D': None}, hero=hero); out[ser].append(e)
        e['files'][line] = files

    for p in S.plan():
        add('SIG', slugify(p['site']), p['site'], p['code'], 'L' if p['line'] == 'light' else 'D', p['files'], 'back')
    for p in C.plan():
        add('CI', 'cert-' + p['code'].lower(), p['name'], p['code'], 'L' if p['line'] == 'light' else 'D', p['files'], 'back')
    for p in O.plan('dtg'):
        add('OW', p['slug'], p['title'], p['code'], 'L' if p['line'] == 'light' else 'D', p['files'], 'back')
    for p in N.plan('dtg'):
        add('N73', p['slug'], p['title'], 'N73-%02d' % p['n'], 'D', p['files'], 'default')
    for p in A.plan():
        if not p['slug'].startswith('ac-s'): continue          # Boat Banter only: the name tees keep their own flow
        add('SIB', p['slug'], p['name'], p['code'], 'D', p['files'], 'back')
    return out


# ---------------- light ink for dark-only art ----------------
def light_ink(img):
    """White-ink art (RGBA) → ink for a light shirt: greys/whites → navy (lighter greys stay a slate), coloured ink keeps
    its hue a shade deeper, red stays red. Alpha unchanged."""
    import numpy as np
    from PIL import Image
    a = np.asarray(img.convert('RGBA')).astype(np.float32) / 255
    rgb, al = a[..., :3], a[..., 3:]
    mx, mn = rgb.max(-1), rgb.min(-1); v = mx; s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    red = (r > g * 1.6) & (r > b * 1.6) & (s > .45)
    navy = np.array(NAVY, np.float32) / 255; slate = np.array((92, 104, 128), np.float32) / 255
    grey = slate[None, None, :] + (navy - slate)[None, None, :] * v[..., None]          # v 1 → navy, v .5 → between
    deep = rgb * 0.55
    out = np.where((s < .25)[..., None], grey, deep)
    out = np.where(red[..., None], rgb, out)
    res = np.concatenate([out, al], -1)
    return Image.fromarray((res * 255).clip(0, 255).astype('uint8'), 'RGBA')


def light_files(ser, d):
    """The light-shirt file list for a dark-only design: the same placements, the art recoloured (url marked
    'recolour:'), the sleeve DS mark swapped to its navy-and-red twin."""
    out = []
    for f in d['files']['D']:
        f = dict(f); n = f['url'].split('/')[-1]
        if n.startswith('DS_mark_PF-sleeve-right') and 'WHITERED' in n:
            f['url'] = f['url'].replace('WHITERED', 'NAVYRED')
        else:
            f['url'] = 'recolour:' + f['url']
        out.append(f)
    return out


def resolve(ser, tone, slug, colour_slug, size, D=None, C=None):
    """One order line → (Printful catalog variant id, files) or raises ValueError with the reason to hold."""
    import custom_tee as T
    D = D or designs(); C = C or colours()
    d = next((x for x in D.get(ser, []) if x['slug'] == slug), None)
    if not d: raise ValueError(f'{ser}: no design {slug!r} in the series')
    c = next((x for x in C[tone] if x['slug'] == colour_slug), None)
    if not c: raise ValueError(f'colour {colour_slug!r} is not a {TONE[tone].lower()} shirt colour')
    files = d['files'][tone] if d['files'][tone] else light_files(ser, d)
    var = T._variants().get((c['cc'], size))
    if not var: raise ValueError(f'Comfort Colors 1717 {c["cc"]} {size} is not in Printful\'s catalog')
    return var, files


def materialise(files, upload):
    """Replace 'recolour:<url>' files with the recoloured master: download, light_ink(), upload(png bytes, name) → url."""
    from PIL import Image
    out = []
    for f in files:
        if f['url'].startswith('recolour:'):
            src = f['url'][9:]; name = src.split('/')[-1].replace('.png', '_LIGHTINK.png')
            im = Image.open(io.BytesIO(urllib.request.urlopen(src, timeout=120).read()))
            buf = io.BytesIO(); light_ink(im).save(buf, 'PNG', optimize=True)
            f = dict(f, url=upload(buf.getvalue(), name))
        out.append(f)
    return out


# ---------------- the picker's data and previews ----------------
PREV = os.path.join(ROOT, 'img', 'custom-series')


def picker_data():
    D, C = designs(), colours()
    out = {'colours': C, 'series': {}, 'sizes': SIZES, 'surcharge': SURCHARGE,
           'img': 'https://doolittlescuba.com/img/custom-series/'}
    for ser, meta in SERIES.items():
        out['series'][ser] = dict(title=meta['title'], page='https://doolittlescuba.com' + meta['page'], price=meta['price'] + SURCHARGE,
                                  view='front' if ser == 'N73' else 'back',
                                  designs=[dict(slug=d['slug'], name=d['name']) for d in D[ser]])
    return out


def previews():
    """img/custom-series/<slug>-<l|d>.webp: the hero placement (back, or the front for 1N73LL1G3NC3), the full 12 x 16 in
    print area at 330 x 440 px with transparency, so the picker can lay it on a drawn shirt of any colour."""
    from PIL import Image
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(PREV, exist_ok=True)
    D = designs(); jobs = []
    for ser, ds in D.items():
        for d in ds:
            for tone in 'LD':
                files = d['files'][tone] or light_files(ser, d)
                f = next(x for x in files if x['type'] == d['hero'])
                jobs.append((d['slug'], tone, f['url']))

    def one(j):
        slug, tone, url = j; dst = os.path.join(PREV, f'{slug}-{tone.lower()}.webp')
        if os.path.exists(dst): return
        rec = url.startswith('recolour:'); url = url[9:] if rec else url
        im = Image.open(io.BytesIO(urllib.request.urlopen(url, timeout=180).read())).convert('RGBA').resize((330, 440), Image.LANCZOS)
        if rec: im = light_ink(im)
        im.save(dst, 'WEBP', quality=82, method=6)
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, jobs))
    print(len(jobs), 'previews in', PREV)


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--data' in a:
        p = os.path.join(ROOT, 'shopify-theme', 'assets', 'ds-series-custom.json')
        json.dump(picker_data(), open(p, 'w'), ensure_ascii=False, separators=(',', ':')); print('wrote', p)
    if '--previews' in a: previews()
    if '--resolve' in a:
        i = a.index('--resolve'); ser, tone, slug, col, size = a[i + 1:i + 6]
        print(json.dumps(resolve(ser, tone, slug, col, size), indent=1))
