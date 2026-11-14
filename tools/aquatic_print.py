#!/usr/bin/env python3
"""Aquatic Comic print masters for Printful (Comfort Colors 1717, DTG), dark palette.

Every file is the Printful print area at 1:1: 12 x 16 in = 3600 x 4800 px, 300 dpi, RGBA with binary alpha
(0 / 255), sRGB profile embedded, two inks only — white #FFFFFF and PMS 485 C red #DA291C.

  front  left-chest lockup: the DS mark (white D + red S) centred over the slogan, IM Fell English Italic,
         one sentence per line, punch words red at 125 %. Lockup centred 9.75 in from the file's left edge
         (3.75 in off centre, wearer's left) with its top 2.0 in down — the placement the Off-World chests use.
         Lines never run wider than 3.75 in; a long name shrinks the slogan to fit.
  back   the joke, IM Fell English Roman, about 80 pt, one sentence per paragraph with a blank line between,
         wrapped in an 11 in block centred, top 1.0 in down; shrinks if it would run past 15.5 in.

Text comes from tools/aquatic_designs.json: *word* is red; {N} one name; {A} {B} buddy pair; {H} {W} husband / wife.

Usage
  tools/aquatic_print.py all <out dir>                 # 59 fronts + 59 backs (custom designs with the sample names)
  tools/aquatic_print.py order <code> <out dir> --name Sam [--name2 Alex]
                                                        # one customer's files, e.g. W03 Sam, B01 Sam Alex, C02 Mike Lisa
Assets (default /home/claude/aquatic/assets, or $AQUATIC_ASSETS): IMFellItalic.ttf, IMFellRoman.ttf (OFL),
DS_mark_transparent.png (the project's navy + red mark; navy is turned white here).
"""
import os, sys, json, re, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageCms
from scipy import ndimage as nd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aquatic_designs.json'), encoding='utf-8'))
_HERE = os.path.dirname(os.path.abspath(__file__))
A = os.environ.get('AQUATIC_ASSETS') or (os.path.join(_HERE, 'assets') if os.path.isdir(os.path.join(_HERE, 'assets')) else '/home/claude/aquatic/assets')
DPI = 300; W, H = 3600, 4800; SS = 2                      # supersample for clean edges, then threshold
WHITE = (255, 255, 255); RED = (0xDA, 0x29, 0x1C)
IT, RO = os.path.join(A, 'IMFellItalic.ttf'), os.path.join(A, 'IMFellRoman.ttf')
ACC = 1.25                                                # red words at 125 %
FRONT = dict(font=IT, size=0.3646, lh=1.2, gap=0.45, maxw=3.75, cx=9.75, top=2.0, mark_h=1.125, mark_gap=0.0625)
BACK = dict(font=RO, size=1.1364, lh=1.25, gap=1.1, maxw=11.0, cx=6.0, top=1.0, bottom=15.5)
_fonts = {}


def font(path, px):
    k = (path, int(round(px)))
    if k not in _fonts: _fonts[k] = ImageFont.truetype(path, k[1])
    return _fonts[k]


def fill_names(text, names):
    t = text
    for k, v in names.items(): t = t.replace('{' + k + '}', v)
    return t


STD = {1: 12, 2: 10}      # the length the layout is drawn for (one name / each of two)
CAP = {1: 20, 2: 16}      # the most the page accepts: longer than STD is fitted (smaller, or the line wraps) and flagged
FLOOR = 0.80              # front lettering below 80 % of its size wraps onto two lines instead of shrinking further
MIN_SCALE = 0.60
REF = {1: 'Alexanderson', 2: 'Alexandria'}   # standard-length reference names (12 / 10) for the fit check          # never smaller than this on the front or the back: below it, hold for a hand edit


def clean_name(s, maxlen):
    s = re.sub(r'\s+', ' ', s.strip()).replace("'", '’').replace('"', '')
    if not s: raise SystemExit('empty name')
    if len(s) > maxlen: raise SystemExit(f'name "{s}" is {len(s)} characters; the line allows {maxlen}')
    return s


def words(line):
    """A line with *red* marks → list of words, each a list of (text, red) runs."""
    runs, red, cur = [], False, ''
    for ch in line:
        if ch == '*':
            if cur: runs.append((cur, red))
            cur = ''; red = not red
        else: cur += ch
    if cur: runs.append((cur, red))
    out, w = [], []
    for text, r in runs:
        parts = text.split(' ')
        for i, p in enumerate(parts):
            if i > 0:
                if w: out.append(w)
                w = []
            if p: w.append((p, r))
    if w: out.append(w)
    return out


def layout(lines, spec, scale, wrap):
    """Lay the paragraphs out (CSS-like line boxes). Returns [(x_runs, baseline)], block width, block height, at px."""
    base = spec['size'] * DPI * SS * scale; lh = spec['lh']; maxw = spec['maxw'] * DPI * SS
    fb = font(spec['font'], base); sp = fb.getlength(' ')

    def run_px(r): return base * (ACC if r else 1.0)

    def metrics(size):
        a, d = font(spec['font'], size).getmetrics(); hl = (lh * size - (a + d)) / 2
        return a + hl, d + hl

    placed, y, widest = [], 0.0, 0.0
    for pi, para in enumerate(lines):
        ws = words(para)
        wid = [sum(font(spec['font'], run_px(r)).getlength(t) for t, r in w) for w in ws]
        rows, cur, cw = [], [], 0.0
        for w, ww in zip(ws, wid):
            add = ww if not cur else cw + sp + ww
            if cur and wrap and add > maxw: rows.append((cur, cw)); cur, cw = [w], ww
            else: cur.append(w); cw = add
        if cur: rows.append((cur, cw))
        if pi > 0: y += spec['gap'] * base
        for row, rw in rows:
            asc, desc = metrics(base)
            for w in row:
                for t, r in w:
                    a2, d2 = metrics(run_px(r)); asc = max(asc, a2); desc = max(desc, d2)
            baseline = y + asc; x = -rw / 2; runs = []
            for wi, w in enumerate(row):
                if wi: x += sp
                for t, r in w:
                    f = font(spec['font'], run_px(r)); runs.append((x, t, r, f)); x += f.getlength(t)
            placed.append((runs, baseline)); widest = max(widest, rw); y = baseline + desc
    return placed, widest, y


def draw(placed, cx, top, size):
    """Draw laid-out text into white and red masks (supersampled), centred on cx (px at SS) from top."""
    wm = Image.new('L', size, 0); rm = Image.new('L', size, 0)
    dw, dr = ImageDraw.Draw(wm), ImageDraw.Draw(rm)
    for runs, baseline in placed:
        for x, t, r, f in runs:
            (dr if r else dw).text((cx + x, top + baseline), t, font=f, fill=255, anchor='ls')
    return wm, rm


def binarise(mask_ss):
    m = mask_ss.resize((mask_ss.width // SS, mask_ss.height // SS), Image.LANCZOS)
    return np.asarray(m) >= 128


_mark = None


def mark_masks(h_px):
    """White D + red S from the project's navy + red mark, scaled at greyscale to h_px tall, thresholded."""
    global _mark
    if _mark is None:
        im = Image.open(os.path.join(A, 'DS_mark_transparent.png')).convert('RGBA')
        im = im.crop(im.getchannel('A').getbbox()); a = np.asarray(im).astype(int)
        alpha = a[..., 3]; red = (a[..., 0] > a[..., 2] + 40) & (alpha > 0)
        _mark = (Image.fromarray(np.where(red, 0, alpha).astype(np.uint8)), Image.fromarray(np.where(red, alpha, 0).astype(np.uint8)))
    wsrc, rsrc = _mark
    w_px = int(round(wsrc.width * h_px / wsrc.height))
    return (np.asarray(wsrc.resize((w_px, h_px), Image.LANCZOS)) >= 128, np.asarray(rsrc.resize((w_px, h_px), Image.LANCZOS)) >= 128)


def op25(m, floor_in=0.02, passes=2):
    """Stroke pass (as OP-25 on the plates): grow only the strokes thinner than the floor, one pixel a side per pass,
    so hairline serifs and the mark's tentacle tips reach 0.020 in while counters and full-weight stems stay as drawn."""
    from skimage.morphology import skeletonize
    for _ in range(passes):
        dt = nd.distance_transform_edt(m); sk = skeletonize(m)
        thin = sk & (2 * dt < floor_in * DPI)
        if not thin.any(): break
        near = nd.binary_dilation(thin, iterations=int(np.ceil(floor_in * DPI / 2)) + 1)
        m = m | (nd.binary_dilation(m) & near)
    return m


def compose(white, red):
    out = np.zeros((H, W, 4), np.uint8)
    out[white] = WHITE + (255,); out[red] = RED + (255,)     # red wins where they touch
    return Image.fromarray(out, 'RGBA')


SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()


def save(im, path):
    im.save(path, dpi=(DPI, DPI), icc_profile=SRGB, optimize=True)


def front(text):
    s = FRONT; lines = text.split('\n'); scale = 1.0
    placed, widest, bh = layout(lines, s, scale, wrap=False)
    lim = s['maxw'] * DPI * SS; wrapped = False; rows0 = len(placed)
    if widest > lim:
        scale = lim / widest * 0.995
        if scale < FLOOR:          # a long name: keep the letters readable, let the line wrap (text reorientation)
            scale = 1.0; wrapped = True; placed, widest, bh = layout(lines, s, scale, wrap=True)
            while widest > lim and scale > MIN_SCALE:
                scale *= 0.97; placed, widest, bh = layout(lines, s, scale, wrap=True)
        else:
            placed, widest, bh = layout(lines, s, scale, wrap=False)
    mh = int(round(s['mark_h'] * DPI)); mw_, mr_ = mark_masks(mh)
    cx = s['cx'] * DPI; top = s['top'] * DPI
    white = np.zeros((H, W), bool); red = np.zeros((H, W), bool)
    x0 = int(round(cx - mw_.shape[1] / 2)); y0 = int(round(top))
    white[y0:y0 + mh, x0:x0 + mw_.shape[1]] |= mw_; red[y0:y0 + mh, x0:x0 + mw_.shape[1]] |= mr_
    ty = (top + mh + s['mark_gap'] * DPI) * SS
    wm, rm = draw(placed, cx * SS, ty, (W * SS, H * SS))
    white |= binarise(wm); red |= binarise(rm)
    white, red = op25(white), op25(red)
    return compose(white, red), dict(scale=round(scale, 3), width_in=round(max(widest / SS, mw_.shape[1]) / DPI, 2),
                                     wrapped=wrapped and len(placed) > rows0, rows=len(placed))


def back(text):
    s = BACK; lines = text.split('\n'); scale = 1.0
    room = (s['bottom'] - s['top']) * DPI * SS
    placed, widest, bh = layout(lines, s, scale, wrap=True)
    while bh > room and scale > 0.6:
        scale *= 0.97; placed, widest, bh = layout(lines, s, scale, wrap=True)
    wm, rm = draw(placed, s['cx'] * DPI * SS, s['top'] * DPI * SS, (W * SS, H * SS))
    return compose(binarise(wm), binarise(rm)), dict(scale=round(scale, 3), height_in=round(bh / SS / DPI, 2), rows=len(placed))


def names_for(d, n1=None, n2=None):
    g = d['code'][0]; smp = D['sample']
    if d['names'] == 0: return {}
    if d['names'] == 1: return {'N': clean_name(n1 or smp['N'], CAP[1])}
    k1, k2 = ('A', 'B') if g == 'B' else ('H', 'W')
    return {k1: clean_name(n1 or smp[k1], CAP[2]), k2: clean_name(n2 or smp[k2], CAP[2])}


def fit_report(d, names):
    """How a set of names fits this design: what had to change from the standard layout (empty = nothing).
    Used to flag a design edit for approval. Renders front and back once (the same work build() does)."""
    std = STD[1 if d['names'] == 1 else 2]; edits = []
    long = [v for v in names.values() if len(v) > std]
    if long: edits.append(f'{len(long)} name(s) over {std} characters')
    _, fi = front(fill_names(d['front'], names)); _, bi = back(fill_names(d['back'], names))
    ref = {k: REF[1 if d['names'] == 1 else 2] for k in names}      # the longest name the layout is drawn for
    _, f0 = front(fill_names(d['front'], ref)); _, b0 = back(fill_names(d['back'], ref))
    if fi['wrapped']: edits.append(f'front line wrapped onto {fi["rows"]} lines (standard: {f0["rows"]})')
    elif fi['scale'] < f0['scale'] - 0.005: edits.append(f'front lettering {round(fi["scale"] * 100)} % (standard {round(f0["scale"] * 100)} %)')
    if bi['rows'] > b0['rows']: edits.append(f'back runs {bi["rows"]} lines (standard: {b0["rows"]})')
    if bi['scale'] < b0['scale'] - 0.005: edits.append(f'back lettering {round(bi["scale"] * 100)} % (standard {round(b0["scale"] * 100)} %)')
    hold = fi['scale'] < MIN_SCALE + 0.001 or bi['scale'] < MIN_SCALE + 0.001
    return dict(edits=edits, hold=hold, front=fi, back=bi)


def build(d, out, names, tag=''):
    os.makedirs(out, exist_ok=True)
    f, fi = front(fill_names(d['front'], names)); b, bi = back(fill_names(d['back'], names))
    stem = f'AC-{d["code"]}{tag}'
    save(f, f'{out}/{stem}_front.png'); save(b, f'{out}/{stem}_back.png')
    return dict(code=d['code'], slug=d['slug'], names=names, front=fi, back=bi)


if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    if sys.argv[1] == 'all':
        out = sys.argv[2]; rep = []
        for d in D['designs']:
            r = build(d, out, names_for(d)); rep.append(r); print(r['code'], r['front'], r['back'], flush=True)
        json.dump(rep, open(f'{out}/build_report.json', 'w'), indent=1, ensure_ascii=False)
    elif sys.argv[1] == 'order':
        code, out = sys.argv[2].upper(), sys.argv[3]
        d = next(x for x in D['designs'] if x['code'] == code)
        a = sys.argv[4:]
        n1 = a[a.index('--name') + 1] if '--name' in a else None
        n2 = a[a.index('--name2') + 1] if '--name2' in a else None
        if d['names'] and not n1: sys.exit('this design needs --name' + (' and --name2' if d['names'] == 2 else ''))
        if d['names'] == 2 and not n2: sys.exit('this design needs --name2')
        nm = names_for(d, n1, n2)
        tag = '_' + '-'.join(re.sub(r'[^A-Za-z0-9]+', '', v) for v in nm.values()) if nm else ''
        print(build(d, out, nm, tag))
