#!/usr/bin/env python3
"""Assets for the /custom/ cap preview on real photos (Eric, 21 Nov 2026: "the make it yours cap needs rerender").

The drawn SVG cap is replaced by Printful's studio photos of the blank Flexfit 6277 (front, left side, right side, back,
in all ten colours), with the real stitch files laid on them at their true size, in the places Printful embroiders:

  - photos: img/cap/<colour>-<view>.webp, white backgrounds knocked out (1000 px, Printful's largest).
  - stitch art: img/cap/stitch/<file>.webp at 200 px/in, the very files tools/custom_cap.py sends to Printful for a dark,
    a light (White, Khaki, Grey: navy thread) and a Red cap.
  - custom/cap-preview.json: the photo for each colour and view, each embroidery area as a rectangle on the photo, and for
    each front / side / back choice the file and its placed size in inches (custom_cap.position(): fitted to the area,
    top-aligned, centred side to side — the same as the order).

Areas on the photos: Printful's mockup templates (product 140) put the 5.90 x 2.00 in front and the 2 x 1 in back on its
flat photos; the rectangles below are those, carried to the studio photos by the brim seam, the button and the crown
width (front: brim seam y 682, button 65, crown 790 px wide → 104 px/in; back: bottom edge 852, button 205). The 4.00 x
1.75 in standard front shares the large front's bottom edge. Side: 2 x 1 in on the side panel, bottom 0.5 in above the band.

  tools/cap_preview.py INDEX.json      (INDEX = the Cap blanks run's index.json: Printful catalog images, product 140)
"""
import os, sys, json, re, io, urllib.request
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import printful_caps as PC
import custom_cap as CC

OUT = os.path.join(ROOT, 'img', 'cap'); ART = os.path.join(OUT, 'stitch'); PPI = 200
VIEWS = ('front', 'left', 'right', 'back')
AREAS = {   # photo px (1000 x 1000): [x, y, w, h] of each Printful embroidery area
    'embroidery_front_large': ('front', [192, 343, 616, 240]),
    'embroidery_front': ('front', [292, 401, 416, 182]),
    'embroidery_left': ('left', [574, 598, 172, 86]),
    'embroidery_right': ('right', [254, 598, 172, 86]),
    'embroidery_back': ('back', [391, 692, 219, 109]),
}
CLASS = {'dark': 'Dark Navy', 'light': 'White', 'red': 'Red'}
MARK_FRONT = CC.MARK_FRONT


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'doolittle-tools'}), timeout=120) as r: return r.read()


def knock_out(im):
    """white studio background → transparent (flood from the edges, so a white cap is untouched)."""
    im = im.convert('RGBA')
    if im.getpixel((2, 2))[3] == 0: return im
    from PIL import ImageDraw
    rgb = im.convert('RGB'); mask = Image.new('L', im.size, 0)
    seed = rgb.copy()
    for xy in ((0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1)):
        ImageDraw.floodfill(seed, xy, (255, 0, 255), thresh=18)
    import numpy as np
    s = np.array(seed); a = np.array(im)
    bg = (s[..., 0] == 255) & (s[..., 1] == 0) & (s[..., 2] == 255)
    a[bg, 3] = 0
    return Image.fromarray(a)


def photos(index):
    d = json.load(open(index)); out = {}
    for s in d['saved']:
        p = re.sub(r'\?.*', '', s['url']).split('/medium/')[-1]
        m = re.match(r'(?:default/)?(front|left|right|back)/[^/]+$', p)
        slug = {v: k for k, v in CC.COLOURS.items()}.get(s['colour'])
        if not (m and slug) or m.group(1) in out.setdefault(slug, {}): continue
        im = knock_out(Image.open(io.BytesIO(fetch(s['url']))))
        name = f'{slug}-{m.group(1)}.webp'; im.save(os.path.join(OUT, name), 'WEBP', quality=90, method=6)
        out[slug][m.group(1)] = 'img/cap/' + name
    for slug in CC.COLOURS:   # Multicam Green is no longer offered (21 Nov), so its photos are skipped
        missing = set(VIEWS) - set(out.get(slug, {}))
        if missing: sys.exit(f'{slug}: no photo for {sorted(missing)}')
    return out


def art(name, threads, colour, red_too=False):
    """custom_cap.for_colour → the stitch file, saved for the page, with its placed size in each area it can go in."""
    c = CC.for_colour(name, threads, colour, red_too=red_too)
    im = c['image']; base = re.sub(r'\.png$', '', c['name'].rsplit('/', 1)[-1])
    path = os.path.join(ART, base + '.webp')
    if not os.path.exists(path):
        w, h = im.width / CC.DPI, im.height / CC.DPI
        im.resize((max(1, round(w * PPI)), max(1, round(h * PPI))), Image.LANCZOS).save(path, 'WEBP', quality=92, method=6)
    return dict(src='img/cap/stitch/' + base + '.webp', w=round(im.width / CC.DPI, 3), h=round(im.height / CC.DPI, 3))


def main(index):
    os.makedirs(ART, exist_ok=True)
    P = photos(index)
    A = {}
    # fronts: every catalog site cap, by its page slug, and the four brand fronts
    for c in PC.CAPS:
        key = 'site:' + c[1].removesuffix('-dark-cap').removeprefix('the-') if c[0] not in MARK_FRONT.values() else None
        if c[0] in MARK_FRONT.values(): key = 'mark:' + {v: k for k, v in MARK_FRONT.items()}[c[0]]
        red_too = c[0] in MARK_FRONT.values()
        A[key] = {k: art(c[3], c[4], col, red_too) for k, col in CLASS.items()}
    A['side:dsmark'] = {k: art(PC.SIDE_FILE, [PC.WHITE, PC.RED], col, True) for k, col in CLASS.items()}
    A['back:tagline'] = {k: art(PC.BACK_FILE, [PC.WHITE], col) for k, col in CLASS.items()}
    A['back:dsmark'] = A['side:dsmark']
    hmp = 'DS-HMP_Newnan_PF-cap-front_2.96x1.99in_white-red.png'   # Home Port: the Newnan sample front (each order's is built by hand)
    A['site:home-port'] = {k: art(PC.SITE + hmp, None, 'Dark Navy') for k in CLASS}
    cls = {slug: ('light' if col in PC.LIGHT else 'red' if col == 'Red' else 'dark') for slug, col in CC.COLOURS.items()}
    data = dict(photos=P, areas={k: dict(view=v[0], rect=v[1], inches=CC.AREA[k]) for k, v in AREAS.items()},
                art=A, cls=cls, ink={'dark': '#FFFFFF', 'red': '#FFFFFF', 'light': PC.NAVY})
    def ver(rel):   # ?v=<content hash> so a re-render reaches browsers
        import hashlib; return '../' + rel + '?v=' + hashlib.md5(open(os.path.join(ROOT, rel), 'rb').read()).hexdigest()[:8]
    for c in P.values():
        for v in c: c[v] = ver(c[v])
    for a in A.values():
        for k in a: a[k] = dict(a[k], src=ver(a[k]['src'])) if not a[k]['src'].startswith('../') else a[k]
    js = json.dumps(data, separators=(',', ':'), sort_keys=True)
    page = os.path.join(ROOT, 'custom', 'index.html'); h = open(page, encoding='utf-8').read()
    h2 = re.sub(r'(<script type="application/json" id="cap-preview">).*?(</script>)', lambda m: m.group(1) + js + m.group(2), h, count=1, flags=re.S)
    if h2 == h and js not in h: sys.exit('custom/index.html: no cap-preview block')
    open(page, 'w', encoding='utf-8').write(h2)
    print(f'{sum(len(v) for v in P.values())} photos, {len(A)} art choices, {len(os.listdir(ART))} stitch files')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__))
