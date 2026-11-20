#!/usr/bin/env python3
"""Home Port cap (Shopify "Home Port — Dark cap", SKU DS-HMP-CD-SM / DS-HMP-CD-LXL) → Printful embroidery placements.

The product page's map picker (shopify-theme/blocks/home-port-picker.liquid) puts three line properties on the order:
  Home Port name          the buyer's port, up to 16 characters ("Lake Lanier")
  Home Port coordinates   "33°22.842'N 084°47.982'W" (degrees and decimal minutes, as on the site caps)
  Home Port flag          "Dive flag" (US ports) or "Alpha flag" (ports abroad)
The front is drawn like the site caps' fronts (and the Newnan sample in renders/caps/): the flag from a catalog site cap
file (dive flag from Rainbow River, Alpha flag from Bali), the name in Almendra Bold, the two coordinate lines under it,
white thread with the flag's red or royal blue, inside the 4.00 x 2.00 in standard front so it sits like the other caps.
Side (heavy DS mark) and back (DO A LITTLE over SCUBA) are the catalog files every site cap uses: already digitized.
The cap is Black, as the Printful sync plan for Home Port (Rainbow River's black plan) had it. The new front is one new
stitch file; Printful's digitization charge for it comes out of the $48 price (no fee line for the buyer).

Holds (raise Hold): no name, coordinates the picker can't have made, an unknown flag, a name too long to stitch at the
0.25 in letter floor, language the name rules refuse.

  tools/homeport_cap.py "Newnan" "33°22.842'N 084°47.982'W" "Dive flag" /tmp/hp SM
"""
import os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import custom_tee as T
import custom_cap as CAP
import printful_caps as PC

Hold = T.Hold
DPI = T.DPI
SKU_RE = re.compile(r'^DS-HMP-CD-(SM|LXL)$')
FLAGS = {'Dive flag': 'RRV', 'Alpha flag': 'BAL'}       # catalog cap whose front carries that flag (top block of the file)
MAX_W, MAX_H = 3.90, 1.99                               # inches: inside Printful's 4.00 in standard cap front, like the site caps
NAME_CAP, COORD_CAP = 0.42, 0.33                        # cap heights (inches) of the Newnan sample; shrunk to fit, never below FLOOR
FLOOR = CAP.FLOOR                                       # 0.25 in: smallest stitched letter
GAP = 0.06                                              # inches between flag, name and coordinate lines
FONT = os.path.join(HERE, 'assets', 'fonts', T.FONTS['hand'])
COORD_RE = re.compile(r"^(\d{2})°(\d{2}\.\d{3})'([NS])\s+(\d{3})°(\d{2}\.\d{3})'([EW])$")


def flag_image(flag):
    if flag not in FLAGS: raise Hold(f'Home Port flag {flag!r}')
    c = CAP.BY_CODE[FLAGS[flag]]
    im = T.fetch(c[3]).convert('RGBA'); rows = (np.array(im.getchannel('A')) > 8).any(1)
    top = int(np.argmax(rows)); end = top
    while end < len(rows) and rows[end]: end += 1                          # the flag is the first block, above a clear gap
    return T.ink_crop(im.crop((0, top, im.width, end))), c[4]


def text_line(text, cap_in):
    em = 200; f = ImageFont.truetype(FONT, em); l, t, r, b = f.getbbox('H'); ratio = (b - t) / em
    f = ImageFont.truetype(FONT, max(8, round(cap_in / ratio * DPI)))
    l, t, r, b = f.getbbox(text); im = Image.new('RGBA', (r - l + 8, b - t + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - l, 4 - t), text, font=f, fill=(255, 255, 255, 255))
    return T.ink_crop(im)


def check(name, coords):
    name = re.sub(r'\s+', ' ', name or '').strip()
    if not name: raise Hold('Home Port: no port name on the line')
    if len(name) > 20: raise Hold('Home Port: port name longer than the page allows')
    import name_rules
    if name_rules.language_problem(name): raise Hold('Home Port: name not allowed (language)')
    m = COORD_RE.match((coords or '').strip())
    if not m: raise Hold('Home Port: coordinates not in the picker\'s format')
    la, lam, ns, lo, lom, ew = m.groups()
    if int(la) > 90 or int(lo) > 180 or float(lam) >= 60 or float(lom) >= 60: raise Hold('Home Port: coordinates out of range')
    return name, [f"{la}°{lam}'{ns}", f"{lo}°{lom}'{ew}"]


def front(name, coords, flag):
    name, lines = check(name, coords)
    fl, threads = flag_image(flag)
    W, H = MAX_W * DPI, MAX_H * DPI
    nm = text_line(name, NAME_CAP)
    if nm.width > W:                                                      # long name: smaller letters, down to the floor
        cap = NAME_CAP * W / nm.width
        if cap < FLOOR: raise Hold('Home Port: name too long to stitch (0.25 in letter floor)')
        nm = text_line(name, cap)
    co = [text_line(s, COORD_CAP) for s in lines]
    parts = [fl, nm] + co; gap = round(GAP * DPI)
    w = max(p.width for p in parts); h = sum(p.height for p in parts) + gap * (len(parts) - 1)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); y = 0
    for p in parts: out.alpha_composite(p, ((w - p.width) // 2, y)); y += p.height + gap
    sc = min(1.0, W / w, H / h)
    if sc < 1.0:
        if COORD_CAP * sc < FLOOR - 1e-6: raise Hold('Home Port: front too big to stitch at the letter floor')
        out = out.resize((round(w * sc), round(h * sc)), Image.LANCZOS)
    return out, threads


def plan(name, coords, flag, size='LXL'):
    if size not in CAP.SIZES: raise Hold(f'cap size {size!r}')
    im, threads = front(name, coords, flag)
    P = {'embroidery_front': dict(kind='new', image=im, threads=threads, name='home-port-front'),
         'embroidery_left': CAP.catalog(PC.SIDE_FILE, [PC.WHITE, PC.RED]),
         'embroidery_back': CAP.catalog(PC.BACK_FILE, [PC.WHITE])}
    colour = 'Black'
    return dict(design={'cs': 'dsmark', 'csp': 'left'}, size=size, colour=colour, variant_id=PC.PF[colour][CAP.SIZES[size]],
                placements=P, cost=round(PC.BLANK + PC.EXTRA * (len(P) - 1), 2), new_files=1, fee=0.0,
                fee_key=f'homeport|{name}|{coords}|{flag}', label='Home Port cap')


if __name__ == '__main__':
    if len(sys.argv) < 4: sys.exit(__doc__)
    try: p = plan(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[5] if len(sys.argv) > 5 else 'LXL')
    except Hold as h: print('HOLD:', h); sys.exit(2)
    print(CAP.summary(p)); print(CAP.render(p, sys.argv[4] if len(sys.argv) > 4 else '/tmp/home_port'))
