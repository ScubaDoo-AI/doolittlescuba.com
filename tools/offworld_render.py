#!/usr/bin/env python3
"""Off-World Hunt Club mockups, in the Certified-ish flat-lay style.

The blank shirt (front and back shading, silhouette, studio background) is recovered from the twenty Certified-ish
renders in img/certs/: each render is garment × shading, so dividing by its garment colour and taking the per-pixel
median across the twenty leaves the shading alone (the prints differ per design and fall out; the one fixed sleeve
mark is inpainted). The 12×16 in back and the 3.5×4 in left-chest print from the package are then set on that blank
at the Certified-ish scale (the 12 in canvas = 262 px on the 1200 px render), black + PMS 485 ink on a light garment,
white + red on a dark one.

Usage: tools/offworld_render.py <package dir> <out dir>
  <package dir> = the unzipped OffWorld_HuntClub_Procreate folder
  <out dir>/<slug>-{front,back}.png and <slug>-dark-{front,back}.png, 1200×1200
Also writes <out dir>/designs/<slug>.webp (900×1240 watermarked preview + footer, for img/designs/) and
<out dir>/art/<slug>.webp + <slug>-w.webp (750×1000 alpha art with the watermark baked in, for custom/art/).
"""
import os, sys, json, glob, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops
from scipy import ndimage as nd
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, 'tools', 'offworld_designs.json')))
W = np.array([0.2126, 0.7152, 0.0722])
PPI = 262 / 12.0                     # px per inch on the render (the Certified-ish back art is 262 px for 12 in)
CX = 600                             # torso centre
BACK_TOP = 300                       # top of the 12×16 canvas: ~4.7 in below the collar, as the Certified-ish backs sit
CHEST_CX, CHEST_TOP = 682, 265       # left chest (wearer's left = viewer's right), canvas top 2.5 in under the collar
RED = np.array([0xE0, 0x1F, 0x2D]) / 255   # PMS 485 C on screen, for the ink test only


def blank(view):
    """Median shading map (lum / garment lum) and silhouette mask from the Certified-ish renders."""
    fs = [f for f in sorted(glob.glob(f'{ROOT}/img/certs/*-{view}.webp')) if not f.endswith('-t.webp')]
    S, M, BG = [], [], []
    for f in fs:
        im = np.asarray(Image.open(f).convert('RGB')).astype(float) / 255
        bg = np.median(np.concatenate([im[:8].reshape(-1, 3), im[-8:].reshape(-1, 3), im[:, :8].reshape(-1, 3), im[:, -8:].reshape(-1, 3)]), axis=0)
        mask = nd.binary_fill_holes(nd.binary_opening(np.abs(im - bg).sum(2) > 0.06, iterations=2))
        lab, n = nd.label(mask); sizes = nd.sum(mask, lab, range(1, n + 1)); mask = nd.binary_fill_holes(lab == (np.argmax(sizes) + 1))
        lum = im @ W; base = np.median(im[nd.binary_erosion(mask, iterations=12)], axis=0); lo = base @ W
        s = lum / lo; resid = np.abs(im - base * s[..., None]).sum(2)
        ink = nd.binary_dilation((resid > 0.15) | (s < 0.92), iterations=3)     # the print and its anti-aliased edge
        S.append(np.where(mask & ~ink, s, np.nan)); M.append(mask); BG.append(bg)
    S = np.array(S)
    with np.errstate(all='ignore'):
        med = np.nanmedian(S, axis=0)
    valid = (~np.isnan(S)).sum(0)
    mask = np.median(np.array(M).astype(float), axis=0) > 0.5
    bg = np.array(BG).mean(0)
    # the Certified-ish backs share one text layout, so a few spots are inked in most renders: too few clean samples → inpaint
    hole = (np.isnan(med) | (valid < 8)) & mask
    hole = nd.binary_dilation(hole, iterations=2) & mask
    med = np.where(np.isnan(med), 1.0, med)
    # inpaint the sleeve mark and any other fixed ink; the shading around is smooth so Telea does it cleanly
    s8 = np.clip(med / 1.4 * 255, 0, 255).astype(np.uint8)
    s8 = cv2.inpaint(s8, hole.astype(np.uint8), 5, cv2.INPAINT_TELEA)
    med = np.where(hole, s8.astype(float) / 255 * 1.4, med)
    return med, mask, bg


def blanks_():
    """Front and back. The Certified-ish backs all carry a print (and its watermark) over the same area, so the back's
    torso shading comes from the front map — same silhouette, same light — and only the collar keeps the back's own."""
    f, fm, bg = blank('front'); b, bm, _ = blank('back')
    yy = np.arange(f.shape[0])[:, None]
    back = np.where((yy < 262) | ~fm, b, f)
    return {'front': (f, fm, bg), 'back': (back, bm, bg)}


def garment(shade, mask, bg, hexc, dark):
    """Dye the blank: multiplicative shading on a light garment; on a dark one the highlights are added back."""
    new = np.array([int(hexc[i:i + 2], 16) for i in (1, 3, 5)]) / 255
    s = shade[..., None]
    if dark:
        a = np.clip(0.7 * (s - 1) / 0.3, 0, 1) * 0.9
        out = np.where(s > 1, new + a * (1 - new), new * s)
    else:
        out = new * s
    res = np.where(mask[..., None], out, bg)
    # soften the cut-out edge
    edge = nd.binary_dilation(mask, iterations=1) & ~nd.binary_erosion(mask, iterations=1)
    blur = cv2.GaussianBlur(res.astype(np.float32), (0, 0), 0.8)
    res[edge] = blur[edge]
    return np.clip(res, 0, 1)


def place(res, shade, png, cx, top, width_in, dark):
    """Composite a print PNG (RGBA, transparent) with its canvas width in inches, centred on cx with its top at `top`."""
    im = Image.open(png).convert('RGBA')
    w = int(round(width_in * PPI)); h = int(round(im.height * w / im.width))
    im = im.resize((w, h), Image.LANCZOS)
    a = np.asarray(im).astype(float) / 255
    x0 = int(round(cx - w / 2)); y0 = top
    sub = res[y0:y0 + h, x0:x0 + w]; sh = np.clip(shade[y0:y0 + h, x0:x0 + w], 0.6, 1.08)[..., None]
    ink = a[..., :3]
    # the ink takes the folds: a little darker in a fold, a touch lighter on a ridge; white ink sits on top a bit flatter
    ink = ink * (sh ** (0.35 if dark else 0.5))
    al = a[..., 3:4] * (0.97 if dark else 1.0)
    res[y0:y0 + h, x0:x0 + w] = sub * (1 - al) + ink * al
    return res


# ---- design previews (img/designs) and the Make it yours art (custom/art), as tools/backs.py but keeping the red ----
WM_FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf'
FOOT_FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
CREDIT = '© 2026 John Eric Doolittle Jr.'
WM_TEXT = CREDIT + '  ·  Doolittle Scuba L.L.C.'
FOOTER = 'Original artwork  ·  ' + CREDIT + '  ·  All rights reserved  ·  Not for reproduction'


def watermark_layer(size, px=24, angle=30, gap_x=150, gap_y=200):
    Wd, H = size
    fnt = ImageFont.truetype(WM_FONT, px)
    tw = int(ImageDraw.Draw(Image.new('L', (10, 10))).textlength(WM_TEXT, font=fnt)) + gap_x
    th = px + gap_y
    diag = int(math.hypot(Wd, H)) + tw
    layer = Image.new('L', (diag, diag), 0); d = ImageDraw.Draw(layer)
    for row, y in enumerate(range(0, diag, th)):
        off = (tw // 2) if row % 2 else 0
        for x in range(-tw + off, diag, tw):
            d.text((x, y), WM_TEXT, font=fnt, fill=255)
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    cx, cy = layer.size[0] // 2, layer.size[1] // 2
    return layer.crop((cx - Wd // 2, cy - H // 2, cx - Wd // 2 + Wd, cy - H // 2 + H))


def watermark_rgb(img, colour=(170, 170, 170), **kw):
    layer = watermark_layer(img.size, **kw)
    wm = Image.new('RGB', img.size, (255, 255, 255)); wm.paste(Image.new('RGB', img.size, colour), mask=layer)
    return ImageChops.multiply(img.convert('RGB'), wm)


def add_footer(img, band=40):
    Wd, H = img.size
    out = Image.new('RGB', (Wd, H + band), (255, 255, 255)); out.paste(img, (0, 0))
    d = ImageDraw.Draw(out); d.line([(40, H + 2), (Wd - 40, H + 2)], fill=(199, 199, 199), width=1)
    f = ImageFont.truetype(FOOT_FONT, 15); tw = d.textlength(FOOTER, font=f)
    d.text(((Wd - tw) / 2, H + 14), FOOTER, font=f, fill=(112, 112, 112))
    return out


def fit_sheet(rgba, w, h, margin):
    """The print's ink, trimmed with a margin, centred on a w×h sheet; returns RGBA."""
    bbox = rgba.getchannel('A').getbbox()
    m = 75
    page = rgba.crop((0, max(0, bbox[1] - m), rgba.width, min(rgba.height, bbox[3] + m)))     # full width, like the plates
    s = min((w - 2 * margin) / page.width, (h - 2 * margin) / page.height)
    im = page.resize((max(1, int(page.width * s)), max(1, int(page.height * s))), Image.LANCZOS)
    sheet = Image.new('RGBA', (w, h), (0, 0, 0, 0)); sheet.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return sheet


def preview(light_png, dark_png, out_dir, slug):
    os.makedirs(f'{out_dir}/designs', exist_ok=True); os.makedirs(f'{out_dir}/art', exist_ok=True)
    sheet = fit_sheet(Image.open(light_png).convert('RGBA'), 900, 1200, 36)
    white = Image.new('RGBA', sheet.size, (255, 255, 255, 255)); white.alpha_composite(sheet)
    full = add_footer(watermark_rgb(white))
    full.save(f'{out_dir}/designs/{slug}.webp', quality=82, method=6)
    # the Make it yours art: alpha from the print, watermark multiplied into the ink colour; a white-ink twin for dark garments
    for src, suffix in ((light_png, ''), (dark_png, '-w')):
        art = fit_sheet(Image.open(src).convert('RGBA'), 750, 1000, 20)
        rgb = Image.merge('RGB', art.split()[:3])
        if suffix:   # white ink: the watermark darkens it a little instead of greying it
            rgb = ImageChops.multiply(rgb, Image.merge('RGB', [watermark_layer(art.size, px=20, gap_x=120, gap_y=170).point(lambda v: 255 - int(v * 0.33))] * 3))
        else:
            rgb = watermark_rgb(rgb, px=20, gap_x=120, gap_y=170)
        out = rgb.convert('RGBA'); out.putalpha(art.getchannel('A'))
        out.save(f'{out_dir}/art/{slug}{suffix}.webp', quality=80, method=6, exact=True)


def main():
    pkg, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    only = set(sys.argv[3:])
    blanks = blanks_()
    for d in D['designs']:
        if only and d['slug'] not in only: continue
        n = d['n']
        for line in ('light', 'dark'):
            col = D['colours'][line][d[line]]; dark = line == 'dark'
            for view in ('front', 'back'):
                shade, mask, bg = blanks[view]
                res = garment(shade, mask, bg, col['hex'], dark)
                if view == 'back':
                    res = place(res, shade, f'{pkg}/01_Backs_12x16in/PNG_{line}_{"white" if dark else "black"}-ink/OW-{n:02d}_back_{line}.png', CX, BACK_TOP, 12.0, dark)
                else:
                    res = place(res, shade, f'{pkg}/02_Chests_3.5in/PNG/OW-{n:02d}_chest_{line}.png', CHEST_CX, CHEST_TOP, 3.5, dark)
                name = f'{d["slug"]}{"-dark" if dark else ""}-{view}.png'
                Image.fromarray((res * 255 + 0.5).astype(np.uint8)).save(f'{out}/{name}')
        preview(f'{pkg}/01_Backs_12x16in/PNG_light_black-ink/OW-{n:02d}_back_light.png',
                f'{pkg}/01_Backs_12x16in/PNG_dark_white-ink/OW-{n:02d}_back_dark.png', out, d['slug'])
        print(d['slug'], d['light'], '/', d['dark'])


if __name__ == '__main__':
    main()
