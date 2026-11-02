#!/usr/bin/env python3
"""Dark-line mockups from the photographed light Signature Series shirts.
For each site: segment the shirt (U2Net cloth-seg prior + GrabCut), separate the print from the fabric,
re-dye the fabric to the dark garment (shading kept, in linear light), turn the black ink white, keep the
flag colours, rebuild the anti-aliased edges against whatever is next to the shirt (background, skin).
Usage: DS_SRC=<dir of <slug>-{front,back}.jpg originals> DS_OUT=<out dir> tools/darkset.py [slug ...]
Needs rembg (u2net_cloth_seg), opencv, scipy. The originals are the 2048 px on-model photos (not in the repo)."""
import sys, os, json
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as nd

SRC = os.environ.get('DS_SRC', '/home/claude/catalog_src')
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sess = None
def cloth_mask(pil):
    global _sess
    from rembg import new_session, remove
    if _sess is None: _sess = new_session('u2net_cloth_seg')
    out = np.asarray(remove(pil, session=_sess))[..., 3]          # 3 stacked masks: upper, lower, full
    h = pil.height; parts = [out[i * h:(i + 1) * h] for i in range(3)]
    return (parts[0] > 128) | (parts[2] > 128)

def srgb2lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lin2srgb(c): return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]; return (x * x + y * y <= r * r).astype(np.uint8)

def segment(rgb8, prior):
    """GrabCut refinement of the cloth-seg prior → binary shirt mask. Seeds: the garment colour (from the prior's core)
    marks sure foreground; skin-like and paper-white pixels inside the prior are released to GrabCut as probable background."""
    im = rgb8.astype(np.float32) / 255; lum = im @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    hsv = cv2.cvtColor(rgb8, cv2.COLOR_RGB2HSV).astype(np.float32); hue, sat = hsv[..., 0] * 2, hsv[..., 1] / 255
    core = nd.binary_erosion(prior, iterations=14)
    base0 = np.median(im[core & (lum > 0.3)], axis=0); dist0 = np.abs(im - base0).sum(2)
    skin = (hue > 3) & (hue < 40) & (sat > 0.22) & (sat < 0.75) & (lum > 0.12) & (lum < 0.85) & (dist0 > 0.3)
    gh = cv2.cvtColor((base0[None, None, :] * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)[0, 0, 0] * 2     # the garment's hue
    paper = (lum > 0.9) & (sat < 0.07) & (dist0 > 0.25)
    gc = np.full(prior.shape, cv2.GC_BGD, np.uint8)
    band = nd.binary_dilation(prior, iterations=16)
    gc[band] = cv2.GC_PR_BGD; gc[prior] = cv2.GC_PR_FGD
    gc[core & (dist0 < 0.35) & ~skin] = cv2.GC_FGD
    gc[prior & (skin | paper)] = cv2.GC_PR_BGD
    gc[nd.binary_erosion(prior, iterations=40) & (lum < 0.35)] = cv2.GC_FGD          # ink deep inside the shirt
    bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
    bgr = cv2.cvtColor(rgb8, cv2.COLOR_RGB2BGR)
    cv2.grabCut(bgr, gc, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
    m = (gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)
    m = nd.binary_fill_holes(nd.binary_opening(m, iterations=2))
    lab, n = nd.label(m)
    if n > 1: m = lab == (np.argmax(nd.sum(m, lab, range(1, n + 1))) + 1)
    # pale hem interiors (lit from behind) read as paper to GrabCut: close small notches, but only inside the cloth prior
    closed = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, disk(12)).astype(bool)
    m = m | (closed & nd.binary_dilation(prior, iterations=3) & ~skin)
    # a hand or forearm beside the hem, in shadow, can pass as a pink or red shirt: skin near the cloth-seg edge is not shirt
    if not (gh <= 45):
        skin2 = (hue > 3) & (hue < 40) & (sat > 0.2) & (sat < 0.9) & (lum > 0.05) & (lum < 0.85) & (dist0 > 0.3)   # the arm's shadow side too
        m = m & ~nd.binary_opening(skin2, iterations=2)
    m = nd.binary_fill_holes(m)
    # a hole open only to the bottom edge (the shirt runs out of frame) is shirt if it has the garment colour
    filled = nd.binary_fill_holes(np.vstack([m, np.ones((1, m.shape[1]), bool)]))[:-1]
    lab, n = nd.label(filled & ~m)
    for i in range(1, n + 1):
        c = lab == i
        if c.sum() > 200 and np.median(dist0[c]) < 0.3 and skin[c].mean() < 0.2: m |= c
    return m

def convert(slug, view, hexc, out_dir, flag='us'):
    pil = Image.open(f'{SRC}/{slug}-{view}.jpg').convert('RGB'); rgb8 = np.asarray(pil)
    im = rgb8.astype(np.float32) / 255; H, W = im.shape[:2]
    mask = segment(rgb8, cloth_mask(pil))
    lum = im @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    body = nd.binary_erosion(mask, iterations=20)
    # --- print separation -------------------------------------------------------------------------------
    mx, mn = im.max(2), im.min(2); chroma = mx - mn
    hsv = cv2.cvtColor(rgb8, cv2.COLOR_RGB2HSV).astype(np.float32); hue, sat = hsv[..., 0] * 2, hsv[..., 1] / 255
    base0 = np.median(im[body & (lum > 0.3)], axis=0)
    dist0 = np.abs(im - base0).sum(2)
    # the flag: red (US, diver-down) or blue (international, alpha) — saturated, far from the garment colour
    fh = (hue < 20) | (hue > 338) if flag == 'us' else ((hue > 195) & (hue < 250))
    colored = mask & (sat > 0.45) & (chroma > 0.22) & fh & (dist0 > 0.35)
    colored = nd.binary_opening(colored, iterations=1)
    fabric_px = body & (lum > 0.3) & (dist0 < 0.25) & ~nd.binary_dilation(colored, iterations=6)
    base = np.median(im[fabric_px], axis=0); lo = float(np.median(lum[fabric_px]))
    ink_floor = 0.07
    def normconv(v, wgt, sig):
        a = cv2.GaussianBlur(v * wgt, (0, 0), sig); b = cv2.GaussianBlur(wgt, (0, 0), sig); return a, b
    # ink vs fabric: medians ignore strokes thinner than the window but follow fold shadows; wider windows
    # (gated by an absolute darkness ratio) catch solid fills
    # medians over the shirt only: outside the mask, substitute the nearby fabric so the silhouette never reads as a stroke
    a_, b_ = normconv(lum, mask.astype(np.float32), 12); lum_fill = np.where(mask, lum, a_ / np.maximum(b_, 1e-4))
    lum_fill = np.where(mask | (b_ > 0.02), lum_fill, lo)
    lum8 = (np.clip(lum_fill, 0, 1) * 255).astype(np.uint8)
    M9 = cv2.medianBlur(lum8, 19).astype(np.float32) / 255
    M25 = cv2.medianBlur(lum8, 51).astype(np.float32) / 255
    M60 = cv2.medianBlur(cv2.resize(lum8, (W // 4, H // 4), interpolation=cv2.INTER_AREA), 31); M60 = cv2.resize(M60, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
    def kk(M, gate):
        kv = np.clip((M - lum) / np.maximum(M - ink_floor, 0.05), 0, 1); return kv * (lum < gate * M)
    # a stroke needs a sure-ink core (under half the local median; fold creases almost never get there); its
    # anti-aliased edge pixels are kept around the core
    sure = (lum < 0.5 * M9) & mask
    # ...and the core must have crisp edges: crease shadows reach the same darkness but fade in over many pixels
    gl = cv2.GaussianBlur(lum, (0, 0), 1.0); gm = np.hypot(cv2.Sobel(gl, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(gl, cv2.CV_32F, 0, 1, ksize=3)) / 8
    inner6 = nd.binary_erosion(mask, iterations=6)
    bd = sure & ~nd.binary_erosion(sure, iterations=2) & inner6
    crisp = bd & (gm / np.maximum(M9 - lum, 0.05) > 0.25)
    sure = sure & nd.binary_dilation(crisp, iterations=4)
    # a wide dark core that keeps the garment's saturation is a crease, not ink (thin strokes are exempt: JPEG chroma
    # subsampling smears the fabric colour into them, so only cores 6 px and wider are judged)
    sat_base = float(np.median((mx - mn)[fabric_px] / np.maximum(mx[fabric_px], 0.05)))
    if sat_base >= 0.38:                                             # only on strongly coloured shirts: the chroma smear is small next to a crease's
        satv = (mx - mn) / np.maximum(mx, 0.05); wide = nd.distance_transform_edt(sure) >= 3
        lab, n = nd.label(sure)
        if n:
            idx = np.arange(1, n + 1); nw = nd.sum(wide, lab, idx); sw = nd.sum(satv * wide, lab, idx)
            crease = (nw >= 30) & (sw / np.maximum(nw, 1) > max(0.6 * sat_base, 0.3))
            sure = sure & ~np.concatenate([[False], crease])[lab]
    # specks (the weave's dark pits in a fold) are not ink unless they sit right next to a stroke
    lab, n = nd.label(sure)
    if n:
        size = nd.sum(sure, lab, np.arange(1, n + 1)); big = np.concatenate([[False], size >= 12])[lab] & sure
        sure = big | (sure & nd.binary_dilation(big, iterations=4))
    strokes = kk(M9, 0.85) * mask * nd.binary_dilation(sure, iterations=2)
    # the print zone: where sure ink is dense. Solid fills only count inside it, so deep hem/armpit shadows stay fabric
    pz = cv2.GaussianBlur((sure & (strokes > 0.3) & nd.binary_erosion(mask, iterations=12)).astype(np.float32), (0, 0), 30) > 0.012
    pz = nd.binary_dilation(pz, iterations=20)
    # dark blobs with soft boundaries are fold shadows (ink fills have crisp edges): no solid-fill test inside them
    blobs = cv2.morphologyEx((mask & (cv2.GaussianBlur(lum, (0, 0), 3) < 0.55 * lo)).astype(np.uint8), cv2.MORPH_OPEN, disk(4)).astype(bool)   # regions: text and weave blur away, fills and shadows stay
    lab, n = nd.label(blobs); soft = np.zeros_like(mask)
    for i in range(1, n + 1):
        b = lab == i
        if b.sum() < 300: continue
        bd = b & ~nd.binary_erosion(b, iterations=2) & inner6
        if bd.sum() < 20: continue
        li = float(lum[b].mean()); frac = float((gm[bd] / max(lo - li, 0.05) > 0.12).mean())
        if not (frac >= 0.55 or (frac >= 0.3 and li / lo < 0.25)): soft |= b
    soft = nd.binary_dilation(soft, iterations=4)
    k0 = np.maximum.reduce([strokes * pz, kk(M25, 0.5) * (chroma < 0.22) * pz * ~soft, kk(M60, 0.42) * (chroma < 0.22) * pz * ~soft]) * mask
    hi = min(0.24, 0.45 * lo); k_abs = np.clip((hi - lum) / (hi * 0.3), 0, 1) * (chroma < 0.14) * mask * pz * ~soft
    k0 = np.maximum(k0, k_abs)
    # fabric luminance without the ink: normalised convolution, widening where the ink is solid
    wgt = (1 - k0) ** 2 * mask * (cv2.GaussianBlur(np.clip(k0, 0, 1), (0, 0), 2.0) < 0.04)   # keep the JPEG halo round strokes out of the fabric estimate
    L_fab = np.zeros_like(lum); cov = np.zeros_like(lum)
    for sig in (3, 10, 30, 80):
        a, b = normconv(lum, wgt, sig); fill = (cov < 0.15) & (b > 0.15); L_fab[fill] = (a / np.maximum(b, 1e-4))[fill]; cov[fill] = 1
    L_fab[cov == 0] = lo
    k = np.clip((L_fab - lum) / np.maximum(L_fab - ink_floor, 0.05), 0, 1)
    k = np.minimum(k, np.maximum(k0 * 1.6, 0) ** 0.5)         # only where the median test agreed (no fold-shadow leakage)
    k = np.maximum(k, k_abs)
    k = np.clip((k - 0.12) / 0.88, 0, 1) * mask                  # crisp edges: drop the JPEG-ringing tail
    # flag colours: keep
    flagzone = nd.binary_fill_holes(nd.binary_dilation(colored, iterations=22)) if colored.any() else np.zeros_like(mask)
    L_open = cv2.GaussianBlur(cv2.morphologyEx(lum, cv2.MORPH_OPEN, disk(18)), (0, 0), 4)
    w = np.clip((lum - L_open - 0.02) / 0.10, 0, 1) * flagzone * (chroma < 0.2)
    k = np.maximum(k, w)
    cmask = nd.binary_dilation(colored, iterations=1)
    k[cmask] = 0
    # --- re-dye --------------------------------------------------------------------------------------------
    new = np.array([int(hexc[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
    s_lin = srgb2lin(np.clip(L_fab, 0.02, 1)) / srgb2lin(lo)                          # shading, linear light
    s_lin = np.where(s_lin > 1, 1 + (s_lin - 1) * 0.6, s_lin); s_lin = np.clip(s_lin, 0.25, 1.35)   # dark cloth: softer highlights
    near_ink = cv2.GaussianBlur(np.clip(k, 0, 1), (0, 0), 2.5) > 0.03
    grain = ((lum - L_fab) / np.maximum(L_fab, 0.1)) * (1 - k) * (~near_ink)             # fabric grain, ink and its JPEG halo excluded
    s_fab = s_lin * np.clip(1 + 0.55 * grain, 0.6, 1.4)
    fab = lin2srgb(srgb2lin(new)[None, None, :] * s_fab[..., None])
    inkc = np.array([0.95, 0.94, 0.92], np.float32)
    ink = lin2srgb(srgb2lin(inkc)[None, None, :] * np.clip(s_lin, 0.45, 1.15)[..., None] ** 0.7)
    outp = fab * (1 - k[..., None]) + ink * k[..., None]
    res = im.copy(); inner = nd.binary_erosion(mask, iterations=2)
    res[inner] = outp[inner]
    res[cmask] = im[cmask]
    # --- edge band: rebuild each anti-aliased pixel against its own outside neighbour -----------------------
    chrom = im / np.maximum(im.sum(2, keepdims=True), 0.05); cdist = np.abs(chrom - base / base.sum()).sum(2)        # colour without brightness
    band = (nd.binary_dilation(mask, iterations=3) | (nd.binary_dilation(mask, iterations=8) & (cdist < 0.12))) & ~inner & ~cmask   # plus garment-coloured leftovers just outside the mask
    outside = ~nd.binary_dilation(mask, iterations=4)
    # local outside colour: blur of outside pixels, normalised
    o = np.zeros_like(im); o[outside] = im[outside]; wgt = outside.astype(np.float32)
    ob = cv2.GaussianBlur(o, (0, 0), 9); wb = cv2.GaussianBlur(wgt, (0, 0), 9)
    bg_local = ob / np.maximum(wb[..., None], 1e-4)
    d = base[None, None, :] - bg_local; t = ((im - bg_local) * d).sum(2) / np.maximum((d * d).sum(2), 1e-4)
    t = np.clip(t, 0, 1)[..., None]
    fab_edge = lin2srgb(srgb2lin(new)[None, None, :] * np.clip(s_lin, 0.5, 1.2)[..., None])
    res[band] = (bg_local * (1 - t) + fab_edge * t)[band]
    # a pink or red shirt bounces colour into the skin shadow beside it; a dark shirt would not
    gh = cv2.cvtColor((base[None, None, :] * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)[0, 0, 0] * 2
    if gh > 320 or gh < 30:
        bounce = nd.binary_dilation(mask, iterations=10) & ~mask & ~band & ((hue < 15) | (hue > 345)) & (sat > 0.45) & (lum < 0.3)
        grey = lum[..., None] * np.array([1.0, 0.9, 0.85], np.float32)
        res[bounce] = (0.3 * im + 0.7 * grey)[bounce]
    if os.environ.get('DSDEBUG'):
        dd = os.environ['DSDEBUG']; os.makedirs(dd, exist_ok=True)
        for nm, arr in (('mask', mask), ('pz', pz), ('kabs', k_abs), ('k0', k0), ('k', k), ('strokes', strokes), ('band', band), ('colored', colored), ('soft', soft), ('sure', sure)):
            Image.fromarray((np.clip(arr.astype(np.float32), 0, 1) * 255).astype(np.uint8)).save(f'{dd}/{slug}-{view}-{nm}.png')
    out = Image.fromarray((np.clip(res, 0, 1) * 255 + 0.5).astype(np.uint8))
    os.makedirs(out_dir, exist_ok=True)
    out.save(f'{out_dir}/{slug}-{view}.png')
    return dict(base=[round(float(b), 3) for b in base], lo=round(lo, 3), mask_frac=round(float(mask.mean()), 3), ink_px=int((k > 0.3).sum()), flag_px=int(colored.sum()))

import re as _re
_home = open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()
FLAG = {x['slug']: x['flag'] for x in json.loads(_re.search(r'<script type="application/json" id="sites-data">(.*?)</script>', _home, _re.S).group(1))}
DARK = {  # Comfort Colors 1717 dark line, as the garment-dyed shirt photographs (swatch lifted/muted a little)
    'black-bart': ('Pepper', '#464340'), 'bridge-span-14': ('Espresso', '#4b3631'), 'blue-grotto': ('Grape', '#332552'),
    'blue-water-park': ('Black', '#222426'), 'dampier-strait': ('True Navy', '#15284a'), 'bali': ('Denim', '#3f5163'),
    'rainbow-river': ('Wine', '#4d2a48'), 'navy-llcat': ('Navy', '#1b2d4a'), 'dive-land-park': ('Graphite', '#262c33'),
    'thurmond-dam': ('Midnight', '#22365a'), 'thistlegorm': ('Blue Spruce', '#3a5752'), 'somosomo-strait': ('Emerald', '#0f6156'),
    'rainbow-reef': ('Sage', '#444d33'), 'vuna-reef': ('Moss', '#27392e')}
if __name__ == '__main__':
    out_dir = os.environ.get('DS_OUT', '/home/claude/darkset/out')
    slugs = sys.argv[1:] or list(DARK)
    for slug in slugs:
        name, hexc = DARK[slug]
        for view in os.environ.get('DSVIEWS', 'front,back').split(','):
            print(slug, name, view, convert(slug, view, hexc, out_dir, FLAG[slug]), flush=True)
