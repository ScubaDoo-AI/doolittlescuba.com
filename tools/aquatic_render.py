#!/usr/bin/env python3
"""Aquatic Comic mockups and previews, in the site's flat-lay style (the Off-World blank, tools/offworld_render.py).

The print masters from tools/aquatic_print.py (12 x 16 in at 300 dpi, white + red ink) are set on the dyed blank at
their true size and place: the front file's area top 0.5 in under the collar (so the lockup, 2.0 in down the file,
sits 2.5 in under the collar like the Off-World chests), the back file's area at the Off-World back position.

Usage: tools/aquatic_render.py <masters dir> <out dir> [code ...]
  <out dir>/<slug>-{front,back}.png  1200 x 1200
  <out dir>/designs/<slug>.webp      1200 x 900 watermarked preview: chest lockup and back print on the garment colour
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import offworld_render as ow

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aquatic_designs.json'), encoding='utf-8'))
COLLAR = 210
SUBS = {v['key']: v for v in D['subsets'].values()}


def ink_crop(png, tmp):
    im = Image.open(png).convert('RGBA'); bb = im.getchannel('A').getbbox(); im.crop(bb).save(tmp)
    return bb


def preview(front_png, back_png, d, out):
    """Front lockup (left) and back print (right) on a sheet of the garment colour, watermarked, footer below."""
    col = D['colours'][d['colour']]
    W, Hh = 1200, 860
    sheet = Image.new('RGB', (W, Hh), col['hex'])
    f = Image.open(front_png).convert('RGBA'); f = f.crop(f.getchannel('A').getbbox())
    b = Image.open(back_png).convert('RGBA'); b = b.crop((150, 150, 3450, 4750))   # the 11 x 15.33 in text block area
    bh = Hh - 80; b = b.resize((int(b.width * bh / b.height), bh), Image.LANCZOS)
    sheet.paste(b, (W - b.width - 40, 40), b)
    fw = min(360, int(f.width * 380 / f.height)); f = f.resize((fw, int(f.height * fw / f.width)), Image.LANCZOS)
    lx = (W - b.width - 40) // 2 - f.width // 2
    sheet.paste(f, (max(30, lx), (Hh - f.height) // 2 - 20), f)
    dr = ImageDraw.Draw(sheet); fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
    for x, label in ((max(30, lx) + f.width // 2, 'FRONT · LEFT CHEST'), (W - 40 - b.width // 2, 'BACK')):
        tw = dr.textlength(label, font=fnt); dr.text((x - tw / 2, Hh - 34), label, font=fnt, fill=(205, 205, 205))
    layer = ow.watermark_layer(sheet.size)
    sheet = Image.composite(Image.new('RGB', sheet.size, (255, 255, 255)), sheet, layer.point(lambda v: int(v * 0.14)))
    ow.add_footer(sheet).save(out, quality=82, method=6)


def main():
    src, out = sys.argv[1], sys.argv[2]; only = set(c.upper() for c in sys.argv[3:])
    os.makedirs(f'{out}/designs', exist_ok=True)
    B = ow.blanks_(); tmp = f'{out}/_crop.png'
    for d in D['designs']:
        if only and d['code'] not in only: continue
        col = D['colours'][d['colour']]
        fp, bp = f'{src}/AC-{d["code"]}_front.png', f'{src}/AC-{d["code"]}_back.png'
        for view, png, area_top in (('front', fp, COLLAR + 0.5 * ow.PPI), ('back', bp, ow.BACK_TOP)):
            shade, mask, bg = B[view]
            res = ow.garment(shade, mask, bg, col['hex'], True)
            bb = ink_crop(png, tmp)
            w_in = (bb[2] - bb[0]) / 300; cx = ow.CX + ((bb[0] + bb[2]) / 2 - 1800) / 300 * ow.PPI
            res = ow.place(res, shade, tmp, cx, int(round(area_top + bb[1] / 300 * ow.PPI)), w_in, True)
            Image.fromarray((np.clip(res, 0, 1) * 255).astype(np.uint8)).save(f'{out}/{d["slug"]}-{view}.png')
        preview(fp, bp, d, f'{out}/designs/{d["slug"]}.webp')
        print(d['code'], col['name'], flush=True)
    if os.path.exists(tmp): os.remove(tmp)


if __name__ == '__main__':
    main()
