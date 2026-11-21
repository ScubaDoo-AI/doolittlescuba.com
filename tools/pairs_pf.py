#!/usr/bin/env python3
"""Pair images on Printful's own mockups (the 19 Nov look): the Signature tee front on the left, the Flexfit 6277 cap front
overlapping it on the right, on the brand navy ground. 2000 x 1200 JPEG, img/pairs/<slug>-<light|dark>.jpg.

Tee: the Printful front used on /signature/ (Shopify CDN, read from signature/index.html). Cap: img/hats/pf/cap-dark-<slug>-front.webp.
Ground and placement were measured from the 19 Nov pair images (ground fitted per channel, mean error < 1 level).

  tools/pairs_pf.py bali dampier-strait ...     # the given sites, both tees
  tools/pairs_pf.py all
  tools/pairs_pf.py --views all                 # also the side and back views, for the shop deck's 360 turn (21 Nov):
                                                #   img/pairs/<slug>-<line>-side.jpg  (tee side + cap left side)
                                                #   img/pairs/<slug>-<line>-back.jpg  (tee back + cap back)
"""
import io, os, re, sys, urllib.request
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 2000, 1200
COEF = [[32.97, -5.7, 6.21, -11.38, -9.08], [56.39, -7.2, -0.06, -11.1, -11.2], [100.46, -6.96, -10.43, -13.73, -17.6]]
TEE = (1165, 237, 12)     # size, left, top
CAP = (735, 965, 422)
CAP_SLUG = {'thistlegorm': 'the-thistlegorm'}


def ground():
    ys, xs = np.mgrid[0:H, 0:W]; u, v = ((xs - 1000) / 1000) ** 2, ys / 1200
    X = [np.ones_like(u), u, v, v ** 2, u * v]
    return Image.fromarray(np.clip(np.stack([sum(c * x for c, x in zip(k, X)) for k in COEF], -1), 0, 255).astype('uint8'))


def tees(view='front'):
    attr = {'front': 'front', 'side': 'sleeve', 'back': 'back'}[view]
    s = open(f'{ROOT}/signature/index.html').read(); out = {}
    for m in re.finditer(r'<figure class="sh" data-line="(plates|dark)" data-slug="([a-z0-9-]+)".*?</figure>', s, re.S):
        u = re.search(r'data-' + attr + r'="([^"]+)"', m.group(0))
        if u: out[(m.group(2), 'light' if m.group(1) == 'plates' else 'dark')] = u.group(1)
    return out


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'doolittlescuba-tools/1.0'})
    with urllib.request.urlopen(req, timeout=60) as r: return Image.open(io.BytesIO(r.read())).convert('RGBA')


CAP_VIEW = {'front': 'front', 'side': 'left', 'back': 'back'}


def build(slug, line, T, G, view='front'):
    out = G.copy().convert('RGBA')
    tee = fetch(T[(slug, line)]).resize((TEE[0], TEE[0]), Image.LANCZOS); out.alpha_composite(tee, (TEE[1], TEE[2]))
    cap = Image.open(f'{ROOT}/img/hats/pf/cap-dark-{CAP_SLUG.get(slug, slug)}-{CAP_VIEW[view]}.webp').convert('RGBA').resize((CAP[0], CAP[0]), Image.LANCZOS)
    out.alpha_composite(cap, (CAP[1], CAP[2]))
    p = f'{ROOT}/img/pairs/{slug}-{line}' + ('' if view == 'front' else '-' + view) + '.jpg'
    out.convert('RGB').save(p, quality=90, optimize=True); return p


if __name__ == '__main__':
    a = sys.argv[1:]; views = ['side', 'back'] if '--views' in a else ['front']; a = [x for x in a if x != '--views']
    G = ground()
    for view in views:
        T = tees(view)
        sites = sorted({s for s, _ in T}) if a == ['all'] else a
        for s in sites:
            for line in ('light', 'dark'):
                if (s, line) in T: print(build(s, line, T, G, view))
