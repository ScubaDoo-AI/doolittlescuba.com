#!/usr/bin/env python3
"""Re-dye a garment mockup (flat-lay render or on-model photo) to a new garment colour, keeping the print, the shading,
skin, background and any coloured marks. Used for the organic editions (tools/organic.py), whose colours keep each design's
ink group, so only the fabric changes.

The fabric is found by colour, not by shape: the garment's base colour is the median of the central body, and fabric pixels
are those whose hue and chroma (CIE LCh) sit near it — skin, background, black or white ink and red marks fall outside.
For a near-neutral base (black, graphite, white, grey) the test is chroma-low and lightness-near inside the garment region.
New pixel = new colour scaled by the old pixel's lightness ratio (folds kept, in linear light); a soft alpha on the mask edge.

  organic_redye.py <in> <out> <new_hex> [size]
"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
from skimage.color import rgb2lab, lab2lch


def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def unlin(c): return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)


def redye(src, dst, hexc, size=0, thumb=0):
    im = np.asarray(Image.open(src).convert('RGB')).astype(float) / 255
    H, W = im.shape[:2]
    lch = lab2lch(rgb2lab(im)); Lc, C, h = lch[..., 0], lch[..., 1], np.degrees(lch[..., 2])
    # background = border median; garment region = largest component differing from it
    border = np.concatenate([im[:6].reshape(-1, 3), im[-6:].reshape(-1, 3), im[:, :6].reshape(-1, 3), im[:, -6:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    region = nd.binary_fill_holes(nd.binary_opening(np.abs(im - bg).sum(2) > 0.06, iterations=2))
    lab_, n = nd.label(region)
    if n: region = lab_ == (np.argmax(nd.sum(region, lab_, range(1, n + 1))) + 1)
    # base colour: median of a central window inside the region
    cy, cx = H // 2, W // 2; win = np.zeros_like(region); win[int(H*.30):int(H*.75), int(W*.30):int(W*.70)] = True
    core = region & win
    bL, bC = np.median(Lc[core]), np.median(C[core])
    if bC >= 10:
        bh = np.degrees(np.arctan2(np.median(np.sin(np.radians(h[core]))), np.median(np.cos(np.radians(h[core])))))
        dh = np.abs((h - bh + 180) % 360 - 180)
        fab = region & (dh < 28) & (C > bC * 0.35) & (C < bC * 2.2) & (Lc > bL - 38) & (Lc < bL + 30)
    else:   # near-neutral garment
        fab = region & (C < max(10, bC + 7)) & (np.abs(Lc - bL) < 22)
    fab = nd.binary_closing(fab, iterations=1)
    # soft edge so the fabric/print boundary stays anti-aliased
    a = nd.gaussian_filter(fab.astype(float), 0.8) * fab + nd.gaussian_filter(fab.astype(float), 0.8) * (~fab) * 0.0
    base_lin = lin(np.median(im[core & fab], axis=0) if (core & fab).any() else np.median(im[core], axis=0))
    new = lin(np.array([int(hexc[i:i+2], 16) for i in (1, 3, 5)]) / 255)
    W8 = np.array([0.2126, 0.7152, 0.0722])
    ratio = (lin(im) @ W8) / max(base_lin @ W8, 1e-4)
    out_new = unlin(np.clip(new[None, None, :] * ratio[..., None], 0, 1))
    res = im * (1 - a[..., None]) + out_new * a[..., None]
    out = Image.fromarray((np.clip(res, 0, 1) * 255 + 0.5).astype(np.uint8))
    kw = {'quality': 84, 'method': 6} if dst.endswith('.webp') else {'quality': 90}
    if size: out.resize((size, size), Image.LANCZOS).save(dst, **kw)
    else: out.save(dst, **kw)
    if thumb: out.resize((thumb, thumb), Image.LANCZOS).save(dst.replace('.webp', '-t.webp'), **kw)
    return float(fab.mean())


if __name__ == '__main__':
    src, dst, hexc = sys.argv[1:4]; size = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    print(f'{src.rsplit("/", 1)[-1]} -> {hexc}  fabric {redye(src, dst, hexc, size):.1%}')
