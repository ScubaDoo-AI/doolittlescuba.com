#!/usr/bin/env python3
"""4:3 collection-tile images (img/lines/) cut from a design preview (img/designs/*.webp): the whole design framed with a
margin and centred on its ink, the sheet colour and the watermark carried on where the frame runs past the preview.
Usage: tools/line_tiles.py <preview.webp> <out.webp> [margin]    (then tools/bust.py)"""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import offworld_render as ow

src, dst = sys.argv[1], sys.argv[2]; margin = float(sys.argv[3]) if len(sys.argv) > 3 else 0.10
im = Image.open(src).convert('RGB'); W, H = im.size; H -= 40                  # drop the footer band
im = im.crop((0, 0, W, H)); a = np.asarray(im, float)
bg = np.median(a[:30, :30].reshape(-1, 3), 0); dark = bg.mean() < 128
diff = np.abs(a - bg).max(2)
m = diff > (70 if dark else 110)                                           # ink, not the watermark
rows = np.where(m.sum(1) > 2)[0]; cols = np.where(m.sum(0) > 2)[0]
x0, x1, y0, y1 = cols.min(), cols.max(), rows.min(), rows.max()
bw, bh = x1 - x0, y1 - y0
ch = int(max(bh, bw * 3 / 4) * (1 + 2 * margin)); cw = int(ch * 4 / 3)
cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
L, T = cx - cw // 2, cy - ch // 2
canvas = Image.new('RGB', (cw, ch), tuple(int(v) for v in bg))
inside = Image.new('L', (cw, ch), 0)
sx0, sy0 = max(L, 0), max(T, 0); sx1, sy1 = min(L + cw, W), min(T + ch, H)
canvas.paste(im.crop((sx0, sy0, sx1, sy1)), (sx0 - L, sy0 - T))
inside.paste(255, (sx0 - L, sy0 - T, sx1 - L, sy1 - T))
# the watermark, only where the frame runs past the preview (inside it is already there)
layer = ow.watermark_layer((cw, ch))
tint = Image.new('RGB', (cw, ch), (255, 255, 255) if dark else (60, 60, 60))
k = 0.16 if dark else 0.22
mask = Image.fromarray((np.asarray(layer, float) * k * (1 - np.asarray(inside, float) / 255)).astype(np.uint8))
canvas = Image.composite(tint, canvas, mask)
canvas.resize((800, 600), Image.LANCZOS).save(dst, 'webp', quality=84, method=6)
print(dst, 'ink', (x0, y0, x1, y1), 'frame', (L, T, cw, ch), 'dark' if dark else 'light')
