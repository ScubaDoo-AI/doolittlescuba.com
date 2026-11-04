#!/usr/bin/env python3
"""Certified-ish left-chest front (3 Nov 2026), from Eric's 'Certified Diver ~ish' logo (4800 x 3600 @ 300 dpi, opaque RGB).

The boxed "Certified Diver" is black, the "~ish" script is red; the box interior becomes transparent, so the shirt shows through it.
Two inks per file: black (light shirts) or white (dark shirts), plus PMS 485 C red #DA291C. The source is split into black and red
coverage maps, scaled at greyscale (BW-05), thresholded last, then given the OP-25 pass to the 0.020 in floor. The result is placed on
Printful's full 12 x 16 in front area at the Signature Series chest position: ink centre 9.50 in from the left edge
(wearer's left), ink top 0.50 in.
usage: cert_front.py <src.png> <out dir> [ink width in, default 3.50]
"""
import sys, os, numpy as np, cv2
from PIL import Image, ImageCms
from skimage.morphology import skeletonize
DPI, W, H, FLOOR = 300, 3600, 4800, 6.0
CX_IN, TOP_IN = 9.50, 0.50
RED = (0xDA, 0x29, 0x1C)
SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()

def op25(ink):
    dt = cv2.distanceTransform(ink.astype(np.uint8), cv2.DIST_L2, 5); sk = skeletonize(ink); thin = sk & (2*dt < FLOOR)
    if not thin.any(): return ink
    need = np.zeros_like(dt); need[thin] = (FLOOR-2*dt[thin])/2.0; fix = np.zeros_like(ink)
    for r in (1, 2, 3):
        sel = (need > r-1) & (need <= r) & thin
        if sel.any(): fix |= cv2.dilate(sel.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))) > 0
    return ink | (cv2.dilate(fix.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))) > 0)

def p5(m):
    sk = skeletonize(m)
    return float(np.percentile(2*cv2.distanceTransform(m.astype(np.uint8), cv2.DIST_L2, 5)[sk], 5)/DPI) if sk.any() else 0.0

if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]; w_in = float(sys.argv[3]) if len(sys.argv) > 3 else 3.50
    os.makedirs(out, exist_ok=True)
    a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    redcov = np.clip(r - np.maximum(g, b), 0, 1)                      # 1 = full red, 0 = white / black
    blkcov = np.clip(1 - np.maximum(np.maximum(r, g), b) - 0, 0, 1) * (1 - redcov)   # darkness, red excluded
    ys, xs = np.nonzero((redcov > 0.5) | (blkcov > 0.5)); x0, x1, y0, y1 = xs.min(), xs.max()+1, ys.min(), ys.max()+1
    nw = int(round(w_in * DPI)); s = nw / (x1 - x0); nh = int(round((y1 - y0) * s))
    rs = lambda m: cv2.resize(m[y0:y1, x0:x1], (nw, nh), interpolation=cv2.INTER_AREA)
    red = rs(redcov) >= 0.5; blk = (rs(blkcov) >= 0.5) & ~red
    red, blk = op25(red), op25(blk) & ~op25(red)
    px, py = int(round(CX_IN*DPI - nw/2)), int(round(TOP_IN*DPI))
    for ink, name in (((0, 0, 0), 'BLACK'), ((255, 255, 255), 'WHITE')):
        c = np.zeros((H, W, 4), np.uint8)
        c[py:py+nh, px:px+nw][blk] = ink + (255,); c[py:py+nh, px:px+nw][red] = RED + (255,)
        Image.fromarray(c, 'RGBA').save(f'{out}/CI-front-leftchest_Certified-ish_12x16in_{name}.png', dpi=(DPI, DPI), icc_profile=SRGB, optimize=True)
    print(dict(ink_in=(round(nw/DPI, 2), round(nh/DPI, 2)), x_in=(round(px/DPI, 2), round((px+nw)/DPI, 2)), y_in=(round(py/DPI, 2), round((py+nh)/DPI, 2)),
               p5_black=round(p5(blk), 4), p5_red=round(p5(red), 4), red_px=int(red.sum()), black_px=int(blk.sum())))
