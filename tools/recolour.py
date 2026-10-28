#!/usr/bin/env python3
"""Re-dye a flat-lay shirt mockup: recolour.py <in> <out> <new_hex> [light|dark] [size]
Keeps shading, ink (black on light / white on dark) and the coloured sleeve mark."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
src, dst, hexc = sys.argv[1:4]; line = sys.argv[4] if len(sys.argv) > 4 else "light"; size = int(sys.argv[5]) if len(sys.argv) > 5 else 0
im = np.asarray(Image.open(src).convert("RGB")).astype(float) / 255
bg = np.median(np.concatenate([im[:8].reshape(-1,3), im[-8:].reshape(-1,3), im[:, :8].reshape(-1,3), im[:, -8:].reshape(-1,3)]), axis=0)
diff = np.abs(im - bg).sum(2)
mask = nd.binary_fill_holes(nd.binary_opening(diff > 0.06, iterations=2))
lab, n = nd.label(mask); sizes = nd.sum(mask, lab, range(1, n + 1)); mask = lab == (np.argmax(sizes) + 1)
mask = nd.binary_fill_holes(mask)
W = np.array([0.2126, 0.7152, 0.0722]); lum = im @ W
body = nd.binary_erosion(mask, iterations=12)
base = np.median(im[body], axis=0); lo = base @ W
new = np.array([int(hexc[i:i+2], 16) for i in (1, 3, 5)]) / 255
s = (lum / max(lo, 1e-3))[..., None]
if line == "dark":
    a = np.clip((lum - lo) / max(1 - lo, 1e-3), 0, 1)[..., None]
    model_old = np.where(lum[..., None] > lo, a + (1 - a) * base, base * s)
    out_new = np.where(lum[..., None] > lo, a + (1 - a) * new, new * s)
else:
    model_old = base * s; out_new = new * s
resid = np.abs(im - model_old).sum(2)
mark = nd.binary_dilation((resid > 0.30) & nd.binary_erosion(mask, iterations=6), iterations=1)
res = im.copy(); sel = mask & ~mark
res[sel] = np.clip(out_new[sel], 0, 1)
# re-dye the anti-aliased rim (background/old-garment blend) just outside and on the mask edge
band = nd.binary_dilation(mask, iterations=3) & ~nd.binary_erosion(mask, iterations=1) & ~mark
t = np.clip(np.abs(im - bg).sum(2) / max(np.abs(base - bg).sum(), 1e-3), 0, 1)[..., None]
res[band] = (bg * (1 - t) + new * t)[band]
out = Image.fromarray((res * 255 + 0.5).astype(np.uint8))
if size: out = out.resize((size, size), Image.LANCZOS)
kw = {"quality": 84, "method": 6} if dst.endswith(".webp") else {"quality": 90}
out.save(dst, **kw)
print(f"{src.split('/')[-1]}: base #{''.join(f'{int(c*255):02x}' for c in base)} -> {hexc}, mark px {int(mark.sum())}")
