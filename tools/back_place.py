#!/usr/bin/env python3
"""Where a back print sits on the shirt: the one rule every back follows (Eric, 21 Nov 2026, option B).

Why: the 4 Nov sample (Certified-ish Tech Diver, Comfort Colors 1717) came back with the back art starting about
1 1/4 in under the collar. The back masters are full 12 x 16 in files, Printful places the area's top edge about
1 in below the collar seam, and the art in the files began 0.3-1.2 in down (Certified-ish 0.33, Signature 0.63-1.80,
Off-World 1.03, Surface Interval 1.19). Eric chose B: ink top 2.00 in down the area (about 3 in below the collar),
the same height as the chest fix of 13 Nov, shrinking the art only when it would otherwise run past 15.75 in.

normalize(im) moves the ink box straight down (or up) so its top sits at TOP, keeps its horizontal centre, and
scales it down (never up) to fit between TOP and BOTTOM. Pixels are copied unchanged when no scaling is needed.
"""
from PIL import Image

DPI = 300
TOP = 2.00          # in, ink top from the top of the 12 x 16 in back area
BOTTOM = 15.75      # in, lowest the ink may reach
SUFFIX = '_back2in' # new file names, so Printful fetches fresh files


def new_name(name): return name[:-4] + SUFFIX + '.png'


def url(u):
    """Catalog back URL -> its placed version (used by the printful_* plans)."""
    return u if u.endswith(SUFFIX + '.png') else new_name(u)


def normalize(im):
    """→ (placed image, info). im: full-area RGBA back, any size proportional to 12 x 16 in."""
    im = im.convert('RGBA'); W, H = im.size; d = W / 12
    bb = im.getchannel('A').getbbox()
    if not bb: return im, dict(moved=False, scale=1.0)
    h = bb[3] - bb[1]; room = (BOTTOM - TOP) * d
    s = min(1.0, room / h)
    art = im.crop(bb)
    if s < 1.0:
        art = art.convert('RGBa').resize((max(1, round(art.width * s)), max(1, round(art.height * s))), Image.LANCZOS).convert('RGBA')
    cx = (bb[0] + bb[2]) / 2
    x = round(cx - art.width / 2); y = round(TOP * d)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.alpha_composite(art, (x, y))
    nb = out.getchannel('A').getbbox()
    return out, dict(moved=True, scale=round(s, 3), top_from=round(bb[1] / d, 2), top_to=round(nb[1] / d, 2),
                     bottom_to=round(nb[3] / d, 2), height_in=round((nb[3] - nb[1]) / d, 2), centre_in=round(cx / d, 2))
