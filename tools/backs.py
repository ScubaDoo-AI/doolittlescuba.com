#!/usr/bin/env python3
"""Signature Series back prints -> watermarked previews.

Input: the 14 back-print pages (3600x4800 PNG, plate at the top, Facts / Species / Water below),
one per site, named <slug>.png. Output, same treatment as the Certified-ish finals:

  img/designs/<slug>-back.webp   900x1240  full back print, diagonal credit watermark, footer
  custom/art/<slug>-back.webp    750x1000  alpha line art of the full back, watermark baked in
                                            (the Make it yours mockup, "full back" size)

The plate-only previews (img/designs/<slug>.webp, custom/art/<slug>.webp, custom/t/<slug>.webp)
are unchanged: the plate drawing inside each back print is identical to them.

Usage: tools/backs.py <dir with slug.png files> [slug ...]
Needs Pillow with RAQM; DejaVu Serif for the watermark and footer (as the Certified-ish set).
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WM_FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf'
FOOT_FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
CREDIT = '© 2026 John Eric Doolittle Jr.'
WM_TEXT = CREDIT + '  ·  Doolittle Scuba L.L.C.'
FOOTER = 'Original hand-drawn artwork  ·  ' + CREDIT + '  ·  All rights reserved  ·  Not for reproduction'


def font(path, px):
    return ImageFont.truetype(path, px)


def watermark(img, px=24, angle=30, gap_x=150, gap_y=200, colour=(170, 170, 170)):
    """Diagonal repeating credit line, multiplied onto the art: ink stays black, paper takes the grey."""
    W, H = img.size
    fnt = font(WM_FONT, px)
    tw = int(ImageDraw.Draw(img).textlength(WM_TEXT, font=fnt)) + gap_x
    th = px + gap_y
    diag = int(math.hypot(W, H)) + tw
    layer = Image.new('L', (diag, diag), 0)
    d = ImageDraw.Draw(layer)
    for row, y in enumerate(range(0, diag, th)):
        off = (tw // 2) if row % 2 else 0
        for x in range(-tw + off, diag, tw):
            d.text((x, y), WM_TEXT, font=fnt, fill=255)
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    cx, cy = layer.size[0] // 2, layer.size[1] // 2
    layer = layer.crop((cx - W // 2, cy - H // 2, cx - W // 2 + W, cy - H // 2 + H))
    wm = Image.new('RGB', (W, H), (255, 255, 255))
    wm.paste(Image.new('RGB', (W, H), colour), mask=layer)
    return ImageChops.multiply(img.convert('RGB'), wm)


def add_footer(img, band=40):
    W, H = img.size
    out = Image.new('RGB', (W, H + band), (255, 255, 255))
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    d.line([(40, H + 2), (W - 40, H + 2)], fill=(199, 199, 199), width=1)
    f = font(FOOT_FONT, 15)
    tw = d.textlength(FOOTER, font=f)
    d.text(((W - tw) / 2, H + 14), FOOTER, font=f, fill=(112, 112, 112))
    return out


def alpha_art(rgb):
    """Black ink on transparent, alpha = darkness, so the watermark travels with the art."""
    out = Image.new('RGBA', rgb.size, (0, 0, 0, 0))
    out.putalpha(ImageOps.invert(rgb.convert('L')))
    return out


def trim_page(page, margin=75):
    """Tighten the 3600x4800 page to its ink plus a margin, keeping the full width (plates run edge to edge)."""
    bbox = ImageOps.invert(page).getbbox()
    top = max(0, bbox[1] - margin)
    bottom = min(page.height, bbox[3] + margin)
    return page.crop((0, top, page.width, bottom))


def fit_portrait(page, w=900, h=1200, margin=36):
    """The trimmed page centred on a 3:4 sheet."""
    pw, ph = page.size
    s = min((w - 2 * margin) / pw, (h - 2 * margin) / ph)
    im = page.resize((max(1, int(pw * s)), max(1, int(ph * s))), Image.LANCZOS)
    sheet = Image.new('L', (w, h), 255)
    sheet.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return sheet


def build(slug, src_dir):
    page = trim_page(Image.open(os.path.join(src_dir, slug + '.png')).convert('L'))
    full = add_footer(watermark(fit_portrait(page).convert('RGB')))
    out = os.path.join(ROOT, 'img', 'designs', slug + '-back.webp')
    full.save(out, quality=82, method=6)
    art = watermark(fit_portrait(page, 750, 1000, 20).convert('RGB'), px=20, gap_x=120, gap_y=170)
    out2 = os.path.join(ROOT, 'custom', 'art', slug + '-back.webp')
    alpha_art(art).save(out2, quality=80, method=6, exact=True)
    return out, out2


if __name__ == '__main__':
    src = sys.argv[1]
    slugs = sys.argv[2:] or sorted(f[:-4] for f in os.listdir(src) if f.endswith('.png'))
    for slug in slugs:
        a, b = build(slug, src)
        print(slug, os.path.getsize(a) // 1024, 'KB', os.path.getsize(b) // 1024, 'KB')
