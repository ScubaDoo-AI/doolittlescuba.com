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


def preview(png, hexc, dark, out):
    """The art on a sheet of the garment colour, watermark tiled over it, the site footer underneath."""
    W, H = 900, 1200
    sheet = Image.new('RGB', (W, H), hexc)
    art = Image.open(png).convert('RGBA')
    s = min((W - 140) / art.width, (H - 180) / art.height)
    art = art.resize((max(1, int(art.width * s)), max(1, int(art.height * s))), Image.LANCZOS)
    sheet.paste(art, ((W - art.width) // 2, (H - art.height) // 2), art)
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
        width_in = min(11.5, 13.5 * art.width / art.height)
        for view in ('front', 'back'):
            shade, mask, bg = B[view]
            res = ow.garment(shade, mask, bg, col['hex'], dark)
            if view == 'front':
                res = ow.place(res, shade, png, ow.CX, FRONT_TOP, width_in, dark)
            Image.fromarray((np.clip(res, 0, 1) * 255).astype(np.uint8)).save(f'{out}/{d["slug"]}-{view}.png')
        preview(png, col['hex'], dark, f'{out}/designs/{d["slug"]}.webp')
        print(d['slug'], col['name'], f'{width_in:.1f} in', flush=True)


if __name__ == '__main__':
    main()
