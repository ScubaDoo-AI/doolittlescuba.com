#!/usr/bin/env python3
"""Make it yours CAP: a /custom/ cap design → Printful embroidery placements (Flexfit 6277, product 140).

The design is the page's cap query string: colour, cf (front), site, cs (side), csp (left/right), cb (back), text, font.
Every element that already exists as a catalog cap file is sent as THAT file (Shopify CDN URL), so Printful reuses the
digitized stitch file and charges nothing new:
  front  site block → the site cap's front file · dsmark / seal / stack / wordmark → The Mark / Seal / Stack / Wordmark fronts
  side   dsmark → the heavy DS mark side file (0.92 x 1.00 in) · seal → the seal fitted 1.00 in tall (ours: digitized once)
  back   tagline → DO A LITTLE over SCUBA · dsmark → the side DS mark file
Only "Your line" makes a NEW stitch file, so only it carries the digitization fee (Eric, 14 Nov): Printful's charge
($6.50 for the first new file, $2.95 for each further one) + $0.50, ONCE per design however many caps — Shopify product
"Embroidery digitization" DS-DIGI-<n>, n = new placements (front line, back line).

Holds (raise Hold): a logo (wholesale quote by email), Home Port (embroidered to order), a back line too long to stitch
at the 0.25 in letter floor, anything the page doesn't offer.

  tools/custom_cap.py 'colour=navy&cf=line&text=Fiji 2024&cs=dsmark&csp=left&cb=tagline' /tmp/cap LXL
"""
import os, sys, re, urllib.parse
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import custom_tee as T
import printful_caps as PC

Hold = T.Hold
DPI = T.DPI
COLOURS = {'navy': 'Dark Navy', 'black': 'Black', 'dark-grey': 'Dark Grey', 'olive': 'Olive', 'royal-blue': 'Royal Blue'}
SIZES = {'SM': 0, 'LXL': 1}
AREA = {'embroidery_front': (5.90, 2.00), 'embroidery_left': (2.00, 1.00), 'embroidery_right': (2.00, 1.00), 'embroidery_back': (2.00, 1.00)}
WHITE, RED = PC.WHITE, PC.RED
FLOOR = 0.25                       # smallest stitched letter (cap height), inches
KEYS = ['colour', 'cf', 'site', 'cs', 'csp', 'cb', 'text', 'font']
BY_CODE = {c[0]: c for c in PC.CAPS}
MARK_FRONT = {'dsmark': 'MRK', 'seal': 'SEA', 'stack': 'STK', 'wordmark': 'WDM'}
FEE_SKU = 'DS-DIGI-{}'
FEE_EACH = (6.50, 2.95)            # Printful: first new embroidery file, each further one
MARKUP = 0.50


def fee(n):
    return round(FEE_EACH[0] + FEE_EACH[1] * (n - 1) + MARKUP, 2) if n else 0.0


def site_code(slug):
    """page plate slug → catalog cap code (handle '<slug>-dark-cap'; The Thistlegorm is 'the-thistlegorm')."""
    for c in PC.CAPS:
        h = c[1].removesuffix('-dark-cap')
        if h == slug or h == 'the-' + slug: return c[0]
    return None


def parse(q):
    S = dict(urllib.parse.parse_qsl(q.lstrip('#?'), keep_blank_values=True)) if isinstance(q, str) else dict(q)
    d = dict(colour='navy', cf='site', site='black-bart', cs='dsmark', csp='left', cb='tagline', text='', font='hand')
    d.update({k: v for k, v in S.items() if k in KEYS})
    d['text'] = re.sub(r'\s+', ' ', d.get('text') or '').strip()[:28]
    return d


def text_fit(text, font, w_in, h_in, max_em=0.62):
    """Largest single line (or two, split at the middle space) that fits w x h with letters >= FLOOR; None if impossible."""
    fp = os.path.join(HERE, 'assets', 'fonts', T.FONTS[font])
    def cap_ratio(em_px):
        f = ImageFont.truetype(fp, em_px); l, t, r, b = f.getbbox('H'); return (b - t) / em_px
    cr = cap_ratio(200)
    options = [[text]]
    if ' ' in text:
        sp = [i for i, ch in enumerate(text) if ch == ' ']; mid = min(sp, key=lambda i: abs(i - len(text) / 2))
        options.append([text[:mid], text[mid + 1:]])
    best = None
    for lines in options:
        em = max_em
        while em * cr >= FLOOR - 1e-6:
            f = ImageFont.truetype(fp, round(em * DPI))
            ims = []
            for ln in lines:
                l, t, r, b = f.getbbox(ln); im = Image.new('RGBA', (r - l + 8, b - t + 8), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((4 - l, 4 - t), ln, font=f, fill=(255, 255, 255, 255)); ims.append(T.ink_crop(im))
            gap = round(0.22 * em * DPI)
            W = max(i.width for i in ims); H = sum(i.height for i in ims) + gap * (len(ims) - 1)
            if W <= w_in * DPI and H <= h_in * DPI:
                if best is None or em > best[0]:
                    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); y = 0
                    for i in ims: out.alpha_composite(i, ((W - i.width) // 2, y)); y += i.height + gap
                    best = (em, out)
                break
            em -= 0.01
    return best[1] if best else None


def catalog(name, threads):
    im = T.fetch(name)
    return dict(kind='catalog', url=T.CDN + name, image=im, threads=threads, name=name)


def plan(q, size='LXL'):
    S = parse(q)
    if S['colour'] not in COLOURS: raise Hold(f'cap colour {S["colour"]!r}')
    if size not in SIZES: raise Hold(f'cap size {size!r}')
    if S['font'] not in T.FONTS: raise Hold(f'font {S["font"]!r}')
    if 'logo' in (S['cf'], S['cs'], S['cb']): raise Hold('logo cap: wholesale quote by email (digitization fee + $0.50, once per design)')
    P = {}
    # front
    if S['cf'] == 'site':
        if S['site'] == 'home-port': raise Hold('Home Port front: embroidered to order by hand')
        c = site_code(S['site']) or (_ for _ in ()).throw(Hold(f'site {S["site"]!r}'))
        P['embroidery_front'] = catalog(BY_CODE[c][3], BY_CODE[c][4])
    elif S['cf'] in MARK_FRONT:
        c = BY_CODE[MARK_FRONT[S['cf']]]; P['embroidery_front'] = catalog(c[3], c[4])
    elif S['cf'] == 'line':
        if not S['text']: raise Hold('front line chosen but no text')
        im = text_fit(S['text'], S['font'], 5.60, 1.90)
        if im is None: raise Hold('front line too long to stitch')
        P['embroidery_front'] = dict(kind='new', image=im, threads=[WHITE], name='front-line')
    elif S['cf'] != 'none': raise Hold(f'front {S["cf"]!r}')
    # side
    side = {'left': 'embroidery_left', 'right': 'embroidery_right'}.get(S['csp']) or (_ for _ in ()).throw(Hold(f'side {S["csp"]!r}'))
    if S['cs'] == 'dsmark': P[side] = catalog(PC.SIDE_FILE, [WHITE, RED])
    elif S['cs'] == 'seal':
        im = T.fit(T.ink_crop(T.asset('DS_seal_PF-front_2.25in_A2-bezel-star_white-red.png')), 2.0, 1.0)
        P[side] = dict(kind='ours', image=im, threads=[WHITE, RED], name='side-seal')
    elif S['cs'] != 'none': raise Hold(f'side {S["cs"]!r}')
    # back
    if S['cb'] == 'tagline': P['embroidery_back'] = catalog(PC.BACK_FILE, [WHITE])
    elif S['cb'] == 'dsmark': P['embroidery_back'] = catalog(PC.SIDE_FILE, [WHITE, RED])
    elif S['cb'] == 'line':
        if not S['text']: raise Hold('back line chosen but no text')
        im = text_fit(S['text'], S['font'], 1.95, 0.95, max_em=0.40)
        if im is None: raise Hold('back line too long to stitch (keep it to about 20 characters)')
        P['embroidery_back'] = dict(kind='new', image=im, threads=[WHITE], name='back-line')
    elif S['cb'] != 'none': raise Hold(f'back {S["cb"]!r}')
    # every cap carries the DS mark (the page enforces it too)
    if not any(S[k] in ('dsmark', 'seal', 'stack') for k in ('cf', 'cs', 'cb')): raise Hold('no DS mark on the cap')
    if not P: raise Hold('empty cap')
    colour = COLOURS[S['colour']]
    n_new = sum(1 for v in P.values() if v['kind'] == 'new')
    return dict(design=S, size=size, colour=colour, variant_id=PC.PF[colour][SIZES[size]], placements=P,
                cost=round(PC.BLANK + PC.EXTRA * (len(P) - 1), 2), new_files=n_new, fee=fee(n_new),
                fee_key='|'.join(f'{k}:{S["font"]}:{S["text"]}' for k, v in sorted(P.items()) if v['kind'] == 'new'))


def position(k, im):
    w, h = im.width / DPI, im.height / DPI; aw, ah = AREA[k]
    sc = min(1.0, aw / w, ah / h); w, h = w * sc, h * sc     # catalog files carry 0.05 in of clear margin: fit, as the sync does
    return {'width': round(w, 3), 'height': round(h, 3), 'top': 0, 'left': round((aw - w) / 2, 3)}


def render(p, out):
    """Write the files that are not catalog files (new text, our side seal) → {placement: path}."""
    os.makedirs(out, exist_ok=True); files = {}
    for k, v in p['placements'].items():
        if v['kind'] == 'catalog': continue
        path = os.path.join(out, f'{k}.png'); v['image'].save(path, dpi=(DPI, DPI), optimize=True); files[k] = path
    return files


def item(p, urls, qty, retail, external_id, label):
    pls = []
    for k, v in p['placements'].items():
        url = v['url'] if v['kind'] == 'catalog' else urls[k]
        pls.append({'placement': k, 'technique': 'embroidery',
                    'layers': [{'type': 'file', 'url': url, 'position': position(k, v['image']),
                                'layer_options': [{'name': 'thread_colors', 'value': v['threads']}]
                                + ([{'name': '3d_puff', 'value': False}] if k == 'embroidery_front' else [])}]})
    return {'source': 'catalog', 'catalog_variant_id': p['variant_id'], 'quantity': qty, 'external_id': external_id,
            'name': label, 'retail_price': f'{float(retail):.2f}', 'placements': pls}


def summary(p):
    out = [f'Flexfit 6277 {p["colour"]} {p["size"]} → Printful variant {p["variant_id"]}, cost ${p["cost"]:.2f}, '
           f'new stitch files {p["new_files"]} (fee ${p["fee"]:.2f})']
    for k, v in p['placements'].items():
        out.append(f'  {k:17s} {v["kind"]:7s} {v["image"].width / DPI:.2f}×{v["image"].height / DPI:.2f} in  {v["name"]}')
    return '\n'.join(out)


if __name__ == '__main__':
    q = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
    try: p = plan(q, sys.argv[3] if len(sys.argv) > 3 else 'LXL')
    except Hold as h: print('HOLD:', h); sys.exit(2)
    print(summary(p)); print(render(p, sys.argv[2] if len(sys.argv) > 2 else '/tmp/custom_cap'))
