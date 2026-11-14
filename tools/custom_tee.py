#!/usr/bin/env python3
"""Make it yours tee → Printful print files, from the design the buyer built on /custom/.

The /custom/ page describes a shirt as a short query string (the same one its share link and the order carry):
  colour, tab, back, bsize, chest, site, ccert, cpos, sleeve, spos, upper, text, font, tpos
This module turns it into the files Printful prints on a Comfort Colors 1717 (Printful 586):
  front         12 x 16 in   chest print (site lockup, a Certified-ish design or a brand mark) + the buyer's line under it
  back          12 x 16 in   back design (plate / Certified-ish / Off-World, full or upper-back) + upper-back mark or line
  sleeve_right  3.5 x 4 in   sleeve mark (or the buyer's line, when it goes on the other sleeve)
  sleeve_left   3.5 x 4 in
Every piece comes from the catalog masters already in Shopify Files (the same files the store's shirts print), or from
tools/assets (the heavy DS mark, the stack, wordmark and seal, the page's three fonts), so a custom shirt prints at the
same sizes and positions as the catalog ones. Layout follows the page's drawing (tee 600 px wide, 23.7 px = 1 in).

  tools/custom_tee.py 'colour=navy&back=black-bart&bsize=full&chest=site&site=black-bart&cpos=left&sleeve=shark&spos=right' out/
     → out/front.png, out/back.png, out/sleeve_right.png … and a plan (garment, variant, placements, cost) on stdout.

A design is HELD (no files, reason given) when it needs a person: a logo, Home Port (a custom block), or anything the
page did not offer.
"""
import os, sys, io, json, re, urllib.request, urllib.parse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
DPI = 300
A_W, A_H = 12, 16            # front / back area, inches
S_W, S_H = 3.5, 4            # sleeve area
PX = 23.7                    # page px per inch (chest left lockup centre 383 px = 9.5 in; tee centre 300 px = 6 in)
NAVY = (16, 42, 84)          # the heavy mark kit's navy, used for brand marks on light shirts
CACHE = os.environ.get('DS_CACHE', os.path.join('/tmp', 'ds_masters'))

# site palette → Comfort Colors (Printful) names. Light ones follow the catalog (printful_signature.py / _certifiedish.py);
# Caribbean blue has no CC twin, Flo Blue is the nearest (the store moved Bridge Span 14 the same way).
CC = {'light-blue': 'Chambray', 'caribbean-blue': 'Flo Blue', 'mint': 'Island Reef', 'teal': 'Seafoam', 'aqua': 'Chalky Mint',
      'sage': 'Bay', 'lavender': 'Orchid', 'ivory': 'Ivory', 'butter': 'Butter', 'mustard': 'Mustard', 'terracotta': 'Terracotta',
      'coral': 'Watermelon', 'berry-pink': 'Crunchberry', 'pink': 'Blossom', 'lagoon-blue': 'Lagoon Blue', 'flo-blue': 'Flo Blue',
      'granite': 'Granite',
      'navy': 'Navy', 'black': 'Black', 'pepper': 'Pepper', 'graphite': 'Graphite', 'midnight': 'Midnight', 'true-navy': 'True Navy',
      'denim': 'Denim', 'blue-spruce': 'Blue Spruce', 'emerald': 'Emerald', 'moss': 'Moss', 'dark-sage': 'Sage', 'espresso': 'Espresso',
      'wine': 'Wine', 'grape': 'Grape', 'yam': 'Yam', 'violet': 'Violet'}
DARK = {'navy', 'black', 'pepper', 'graphite', 'midnight', 'true-navy', 'denim', 'blue-spruce', 'emerald', 'moss', 'dark-sage',
        'espresso', 'wine', 'grape', 'yam', 'violet'}
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
# Printful's extra charges on the 1717 (catalog API, Nov 2026); the front rides in the blank price
BLANK = {'S': 15.60, 'M': 15.60, 'L': 15.60, 'XL': 15.60, '2XL': 17.60, '3XL': 19.60}
EXTRA = {'back': 5.95, 'sleeve_left': 2.49, 'sleeve_right': 2.49}
FONTS = {'hand': 'Almendra-Bold.ttf', 'plain': 'AlegreyaSans-Medium.ttf', 'mono': 'IBMPlexMono-Regular.ttf'}
MARK_FILES = {'dsmark': ('DS_mark_HEAVY_navy-red_3.00in.png', 'DS_mark_HEAVY_white-red_3.00in.png'),
              'stack': (None, 'DS_stack_PF-front_4.27x2.13in_white-red.png'),
              'wordmark': (None, 'DS_wordmark_PF-front_4.50x1.92in_white-red.png'),
              'seal': (None, 'DS_seal_PF-front_2.25in_A2-bezel-star_white-red.png')}
KEYS = ['colour', 'tab', 'back', 'bsize', 'chest', 'site', 'ccert', 'cpos', 'sleeve', 'spos', 'upper', 'text', 'font', 'tpos']


class Hold(Exception):
    """The design needs a person (logo, Home Port, something the page doesn't offer)."""


# ---------------- catalog lookups ----------------
def _variants():
    d = json.load(open(os.path.join(HERE, 'pf_586_variants.json')))
    return {(c, z): int(v) for v, (c, z, h) in d.items()}


def _catalog():
    """slug → master file names (light ink, dark ink) for every back/chest the page offers."""
    import printful_signature as S, printful_certifiedish as C, printful_offworld as O
    cat = {}
    for p in S.plan():
        names = [f['url'].split('/')[-1] for f in p['files']]
        stem = re.match(r'DS-[A-Z]+_(.+?)_PF-', names[0]).group(1)
        slug = stem.lower().replace('_', '-')
        ink = 'dark' if any('WHITE' in n for n in names) else 'light'
        e = cat.setdefault(slug, {'kind': 'plate', 'code': p['code']})
        e[ink] = dict(front=next(n for n in names if '-front-' in n), back=next(n for n in names if '-back_' in n))
    for p in C.plan():
        names = [f['url'].split('/')[-1] for f in p['files']]
        ink = 'dark' if any('WHITE' in n for n in names) else 'light'
        e = cat.setdefault('cert:' + p['name'].lower(), {'kind': 'cert', 'code': p['code']})
        e[ink] = dict(back=next(n for n in names if '_back_' in n))
    for p in O.plan('dtg'):
        names = [f['url'].split('/')[-1] for f in p['files']]
        ink = 'dark' if any('_dark' in n for n in names) else 'light'
        e = cat.setdefault(p['slug'], {'kind': 'ow', 'code': p['code']})
        e[ink] = dict(back=next(n for n in names if '_back_' in n))
    return cat


def page_data():
    s = open(os.path.join(ROOT, 'custom', 'index.html'), encoding='utf-8').read()
    return json.loads(re.search(r'<script type="application/json" id="custom-data">(.*?)</script>', s, re.S).group(1))


# ---------------- images ----------------
def fetch(name):
    os.makedirs(CACHE, exist_ok=True); p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        with urllib.request.urlopen(CDN + urllib.parse.quote(name), timeout=120) as r, open(p + '.part', 'wb') as f: f.write(r.read())
        os.replace(p + '.part', p)
    return Image.open(p).convert('RGBA')


def asset(name):
    return Image.open(os.path.join(HERE, 'assets', 'marks', name)).convert('RGBA')


def ink_crop(im):
    bb = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
    return im.crop(bb) if bb else im


def plate_only(im):
    """A Signature back is the plate over Facts / Species / Water; the upper-back print is the plate alone:
    keep the ink above the first clear band at least 0.3 in tall."""
    a = np.asarray(im.getchannel('A')) > 8
    rows = np.nonzero(a.any(1))[0]
    if not len(rows): return im
    gaps = np.nonzero(np.diff(rows) > int(0.3 * DPI))[0]
    end = rows[gaps[0]] + 1 if len(gaps) else rows[-1] + 1
    return ink_crop(im.crop((0, 0, im.width, int(end))))


def recolour(im, rgb):
    """White ink → rgb, red kept (brand marks drawn white + red, used on light shirts)."""
    a = np.asarray(im).copy()
    m = (a[..., 3] > 0) & (a[..., 0] > 180) & (a[..., 1] > 180) & (a[..., 2] > 180)
    a[m, :3] = rgb
    return Image.fromarray(a, 'RGBA')


def fit(im, w_in, h_in, upscale_max=1.8):
    s = min(w_in * DPI / im.width, h_in * DPI / im.height, upscale_max)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS) if abs(s - 1) > 1e-3 else im


def place(canvas, im, cx_in, top_in):
    canvas.alpha_composite(im, (round(cx_in * DPI - im.width / 2), round(top_in * DPI)))
    return top_in + im.height / DPI


def text_img(text, font, em_in, max_w_in, rgb):
    f = ImageFont.truetype(os.path.join(HERE, 'assets', 'fonts', FONTS[font]), round(em_in * DPI))
    l, t, r, b = f.getbbox(text)
    im = Image.new('RGBA', (r - l + 8, b - t + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - l, 4 - t), text, font=f, fill=(*rgb, 255))
    im = ink_crop(im)
    if im.width > max_w_in * DPI:   # the page squeezes long lines to the width; keep the height, narrow the line
        im = im.resize((round(max_w_in * DPI), im.height), Image.LANCZOS)
    return im


# ---------------- the design ----------------
def parse(q):
    if isinstance(q, dict): S = dict(q)
    else: S = dict(urllib.parse.parse_qsl(q.lstrip('#?'), keep_blank_values=True))
    d = dict(colour='light-blue', tab='plates', back='black-bart', bsize='full', chest='site', site='black-bart', cpos='left',
             sleeve='shark', spos='right', upper='none', text='', font='hand', tpos='chest', ccert='cert-night')
    d.update({k: v for k, v in S.items() if k in KEYS})
    d['text'] = re.sub(r'\s+', ' ', d.get('text') or '').strip()[:40]
    return d


def plan(q, size='L'):
    """→ dict(garment, variant_id, ink, placements {name: list of layers}, cost, summary) or raises Hold."""
    S = parse(q); D = page_data(); cat = _catalog()
    if S['colour'] not in CC: raise Hold(f'colour {S["colour"]!r} is not a tee colour')
    if size not in SIZES: raise Hold(f'size {size!r}')
    if S['chest'] == 'logo':   # Eric, 13 Nov: a logo or own artwork on the chest → the DS mark on the sleeve, no shark signature
        S['sleeve'] = 'dsmark'
        if S['upper'] == 'shark': S['upper'] = 'none'
    for k in ('chest', 'sleeve', 'upper'):
        if S[k] == 'logo': raise Hold('the design uses the buyer\'s logo: get the file and check it (rule: DS mark on the sleeve, no shark signature)')
    if S['font'] not in FONTS: raise Hold(f'font {S["font"]!r}')
    dark = S['colour'] in DARK; ink = 'dark' if dark else 'light'
    txt_rgb = (255, 255, 255) if dark else (17, 17, 17)
    plates = {p['slug']: p for p in D['plates']}; certs = {c['slug']: c for c in D['certs']}
    L = {'front': [], 'back': [], 'sleeve_right': [], 'sleeve_left': []}

    def mark(key):
        if key == 'shark':
            return ink_crop(fetch(f'DS_shark-signature_PF-sleeve-right_3.5x4in_{"WHITE" if dark else "BLACK"}.png'))
        if key not in MARK_FILES: raise Hold(f'mark {key!r}')
        light, darkf = MARK_FILES[key]
        if dark: return ink_crop(asset(darkf))
        return ink_crop(asset(light)) if light else ink_crop(recolour(asset(darkf), NAVY))

    def cert_art(slug):
        c = certs.get(slug) or (_ for _ in ()).throw(Hold(f'Certified-ish design {slug!r}'))
        e = cat.get('cert:' + c['name'].lower()) or (_ for _ in ()).throw(Hold(f'no print master for {c["name"]}'))
        return fetch(e[ink]['back']), e

    # ---- front: chest print, then the line under it ----
    left = S['cpos'] == 'left'
    cx = 9.5 if left else 6.0
    chest_bottom = None
    if S['chest'] == 'site':
        if S['site'] not in plates: raise Hold(f'chest block {S["site"]!r} is a custom block (Home Port): make it by hand')
        e = cat[S['site']]
        master = fetch(e[ink]['front'])
        if left:
            L['front'].append(('master', e[ink]['front'])); bb = master.getchannel('A').getbbox(); chest_bottom = bb[3] / DPI
        else:
            im = ink_crop(master); im = im.resize((round(im.width * 1.7), round(im.height * 1.7)), Image.LANCZOS)
            L['front'].append(('image', im, cx, 3.0)); chest_bottom = 3.0 + im.height / DPI
    elif S['chest'] == 'cert':
        art, e = cert_art(S['ccert']); im = fit(ink_crop(art), *((4.0, 4.4) if left else (9.1, 8.4)), upscale_max=1.0)
        top = 2.0 if left else 3.0
        L['front'].append(('image', im, cx, top)); chest_bottom = top + im.height / DPI
    elif S['chest'] != 'none':
        box = ((3.0, 3.0) if S['chest'] in ('dsmark', 'seal') else (4.0, 2.4)) if left else (7.6, 6.3)
        im = fit(mark(S['chest']), *box)
        top = 2.0 if left else 3.0
        L['front'].append(('image', im, cx, top)); chest_bottom = top + im.height / DPI
    if S['text'] and S['tpos'] == 'chest':
        em = 0.46 if left else 0.68
        t = text_img(S['text'], S['font'], em, 4.9 if left else 9.3, txt_rgb)
        L['front'].append(('image', t, cx, (chest_bottom + 0.3) if chest_bottom else (3.0 if left else 4.0)))

    # ---- sleeves ----
    if S['sleeve'] != 'none':
        im = fit(mark(S['sleeve']), 3.0, 2.2 if S['sleeve'] in ('shark', 'stack', 'wordmark') else 2.6, upscale_max=1.0)
        if S['sleeve'] == 'dsmark': im = fit(mark('dsmark'), 1.0, 1.09, upscale_max=1.0)   # the line's 1 in sleeve mark
        L['sleeve_' + S['spos']].append(('image', im, S_W / 2, (S_H - im.height / DPI) / 2))
    if S['text'] and S['tpos'] == 'sleeve':
        other = 'left' if S['spos'] == 'right' else 'right'
        t = text_img(S['text'], S['font'], 0.38, 3.2, txt_rgb)
        L['sleeve_' + other].append(('image', t, S_W / 2, (S_H - t.height / DPI) / 2))

    # ---- back: upper mark / line, then the design ----
    y = 0.25; has_upper = False
    if S['upper'] != 'none':
        im = fit(mark(S['upper']), 6.3, 2.4 if S['text'] and S['tpos'] == 'upper' else 2.6)
        L['back'].append(('image', im, 6.0, y)); y += im.height / DPI + 0.25; has_upper = True
    if S['text'] and S['tpos'] == 'upper':
        t = text_img(S['text'], S['font'], 0.63, 11.0, txt_rgb)
        L['back'].append(('image', t, 6.0, y if has_upper else 1.2)); y = (y if has_upper else 1.2) + t.height / DPI + 0.25; has_upper = True
    if S['back'] != 'none':
        slug = S['back']
        e = cat.get(slug) if slug in plates or slug.startswith('ow-') else None
        if slug.startswith('cert-'): art, e = cert_art(slug)
        elif e: art = fetch(e[ink]['back'])
        else: raise Hold(f'back design {slug!r}')
        full = S['bsize'] == 'full' or e['kind'] != 'plate'   # Certified-ish and Off-World go full back only (as on the page)
        if full and not has_upper:
            L['back'].append(('master', e[ink]['back']))
        else:
            im = ink_crop(art) if full else plate_only(art)
            top = max(y, 3.74 if has_upper else 1.8)
            box = (11.5, A_H - top - 0.2) if full else (5.9, 6.3)
            im = fit(im, *box, upscale_max=1.0 if full else 1.4)
            L['back'].append(('image', im, 6.0, top))

    L = {k: v for k, v in L.items() if v}
    if not L: raise Hold('nothing to print')
    var = _variants().get((CC[S['colour']], size)) or (_ for _ in ()).throw(Hold(f'{CC[S["colour"]]} {size} not at Printful'))
    cost = round(BLANK[size] + sum(EXTRA.get(k, 0) for k in L), 2)
    return dict(design=S, size=size, garment=f'Comfort Colors 1717, {CC[S["colour"]]}', colour=S['colour'], ink=ink,
                variant_id=var, layers=L, cost=cost)


def render(p, out):
    """Write one full-area PNG per placement (300 dpi, transparent) → {placement: path}."""
    os.makedirs(out, exist_ok=True); files = {}
    for k, layers in p['layers'].items():
        if len(layers) == 1 and layers[0][0] == 'master':   # the catalog file unchanged
            im = fetch(layers[0][1])
        else:
            w, h = (S_W, S_H) if k.startswith('sleeve') else (A_W, A_H)
            im = Image.new('RGBA', (round(w * DPI), round(h * DPI)), (0, 0, 0, 0))
            for ly in layers:
                if ly[0] == 'master': im.alpha_composite(fetch(ly[1]))
                else: place(im, ly[1], ly[2], ly[3])
        path = os.path.join(out, f'{k}.png'); im.save(path, dpi=(DPI, DPI), optimize=True); files[k] = path
    return files


def summary(p):
    S = p['design']; out = [f'{p["garment"]} ({S["colour"]}), {p["size"]} → Printful variant {p["variant_id"]}, cost ${p["cost"]:.2f}']
    for k, v in p['layers'].items():
        out.append(f'  {k:12s} ' + ' + '.join(x[1] if x[0] == 'master' else f'{x[1].width / DPI:.2f}×{x[1].height / DPI:.2f} in at ({x[2]:.2f}, {x[3]:.2f})' for x in v))
    return '\n'.join(out)


if __name__ == '__main__':
    q = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
    out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/custom_tee'
    size = sys.argv[3] if len(sys.argv) > 3 else 'L'
    try:
        p = plan(q, size)
    except Hold as h:
        print('HOLD:', h); sys.exit(2)
    print(summary(p)); print(render(p, out))
