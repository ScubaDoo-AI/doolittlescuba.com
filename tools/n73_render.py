#!/usr/bin/env python3
"""1N73LL1G3NC3 mockups in the site's flat-lay style (the Off-World blank: the Certified-ish renders' median shading).

Each design is a full-front print: the art (transparent PNG from the Procreate package, 3600 px = its own width) is set
about 11.5 in wide (no taller than 13.5 in), centred, its top 3 in under the collar, in its own ink colours. The back is
the dyed blank. One garment per design, from the site palette (tools/n73_designs.json), chosen for the theme.

Usage: tools/n73_render.py <PNG-transparent dir> <out dir> [slug ...]
  <out dir>/<slug>-{front,back}.png 1200x1200
  <out dir>/designs/<slug>.webp  900x1240 watermarked preview on the garment colour, with the footer (img/designs/)
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import offworld_render as ow

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, 'tools', 'n73_designs.json')))
COLLAR = 210                       # collar seam on the 1200 px front blank (Off-World chest top 265 = 2.5 in under it)
FRONT_TOP = COLLAR + int(3.0 * ow.PPI)


def optical(png):
    """The art cropped to its ink, and the x of its visual centre (alpha-weighted, with the column profile clipped so
    the big blocks lead and a right-aligned tagline only nudges) as a fraction of the cropped width."""
    im = Image.open(png).convert('RGBA'); im = im.crop(im.getchannel('A').getbbox())
    a = np.asarray(im.getchannel('A'), dtype=float) / 255
    col = a.sum(0); col = np.minimum(col, np.percentile(col[col > 0], 90))
    cx = (col * np.arange(len(col))).sum() / col.sum()
    # keep the ink inside a 12 in wide print area around the centre line: never let the shift exceed the slack
    f = cx / im.width
    return im, min(max(f, 0.5 - 0.12), 0.5 + 0.12)


def place_centred(res, shade, im, f, top, scale, dark, tmp):
    """ow.place, but with the cropped art's optical centre on the torso centre line."""
    w = im.width * scale
    shift = (0.5 - f) * w                               # move the box so its optical centre lands on CX
    im.save(tmp)
    return ow.place(res, shade, tmp, ow.CX + shift, top, w / ow.PPI, dark)


def preview(png, hexc, dark, out):
    """The art on a sheet of the garment colour, watermark tiled over it, the site footer underneath."""
    W, H = 900, 1200
    sheet = Image.new('RGB', (W, H), hexc)
    art, f = optical(png)
    s = min((W - 160) / art.width, (H - 220) / art.height)
    art = art.resize((max(1, int(art.width * s)), max(1, int(art.height * s))), Image.LANCZOS)
    x = int(round(W / 2 - f * art.width)); x = min(max(x, 40), W - 40 - art.width)
    sheet.paste(art, (x, (H - 40 - art.height) // 2), art)
    layer = ow.watermark_layer(sheet.size)
    tint = Image.new('RGB', sheet.size, (255, 255, 255) if dark else (60, 60, 60))
    sheet = Image.composite(tint, sheet, layer.point(lambda v: int(v * (0.16 if dark else 0.22))))
    ow.add_footer(sheet).save(out, quality=82, method=6)


def main():
    src, out = sys.argv[1], sys.argv[2]; only = set(sys.argv[3:])
    os.makedirs(f'{out}/designs', exist_ok=True)
    B = ow.blanks_()
    for d in D['designs']:
        if only and d['slug'] not in only: continue
        col = D['colours'][d['colour']]; dark = d['dark']; png = os.path.join(src, d['png'])
        art = Image.open(png)
        width_in = min(11.5, 13.5 * art.width / art.height)     # the frame's size on the shirt, as before
        crop, f = optical(png); scale = width_in * ow.PPI / art.width
        tmp = f'{out}/_crop.png'
        for view in ('front', 'back'):
            shade, mask, bg = B[view]
            res = ow.garment(shade, mask, bg, col['hex'], dark)
            if view == 'front':
                res = place_centred(res, shade, crop, f, FRONT_TOP, scale, dark, tmp)
            Image.fromarray((np.clip(res, 0, 1) * 255).astype(np.uint8)).save(f'{out}/{d["slug"]}-{view}.png')
        preview(png, col['hex'], dark, f'{out}/designs/{d["slug"]}.webp')
        print(d['slug'], col['name'], f'{width_in:.1f} in', flush=True)


if __name__ == '__main__':
    main()
