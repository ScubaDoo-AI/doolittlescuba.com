#!/usr/bin/env python3
"""Pair images on Printful's own mockups (the 19 Nov look): the Signature tee front on the left, the Flexfit 6277 cap front
overlapping it on the right, on the brand navy ground. 2000 x 1200 JPEG, img/pairs/<slug>-<light|dark>.jpg.

Tee: the Printful front used on /signature/ (Shopify CDN, read from signature/index.html). Cap: img/hats/pf/cap-dark-<slug>-front.webp.
Ground and placement were measured from the 19 Nov pair images (ground fitted per channel, mean error < 1 level).

  tools/pairs_pf.py bali dampier-strait ...     # the given sites, both tees
  tools/pairs_pf.py all
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


def tees():
    s = open(f'{ROOT}/signature/index.html').read()
    return {(m.group(2), 'light' if m.group(1) == 'plates' else 'dark'): m.group(3)
            for m in re.finditer(r'<figure class="sh" data-line="(plates|dark)" data-slug="([a-z0-9-]+)".*?data-front="([^"]+)"', s, re.S)}


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'doolittlescuba-tools/1.0'})
    with urllib.request.urlopen(req, timeout=60) as r: return Image.open(io.BytesIO(r.read())).convert('RGBA')


def build(slug, line, T, G):
    out = G.copy().convert('RGBA')
    tee = fetch(T[(slug, line)]).resize((TEE[0], TEE[0]), Image.LANCZOS); out.alpha_composite(tee, (TEE[1], TEE[2]))
    cap = Image.open(f'{ROOT}/img/hats/pf/cap-dark-{CAP_SLUG.get(slug, slug)}-front.webp').convert('RGBA').resize((CAP[0], CAP[0]), Image.LANCZOS)
    out.alpha_composite(cap, (CAP[1], CAP[2]))
    p = f'{ROOT}/img/pairs/{slug}-{line}.jpg'; out.convert('RGB').save(p, quality=90, optimize=True); return p


if __name__ == '__main__':
    T, G = tees(), ground()
    sites = sorted({s for s, _ in T}) if sys.argv[1:] == ['all'] else sys.argv[1:]
    for s in sites:
        for line in ('light', 'dark'): print(build(s, line, T, G))
