#!/usr/bin/env python3
"""Certified-ish Dark mockups from the light site mockups (img/certs/cert-<slug>-{back,front}.webp).

The light renders already carry the shirt, the back print and the DS sleeve mark exactly where the dark line has them,
so the dark set is made from them rather than re-rendered: the fabric is re-dyed to the dark garment (its folds kept),
the black ink becomes white ink (sitting a little flatter, as plastisol-free white does), the red of the DS mark stays red,
and the anti-aliased rim is rebuilt against the background.

Usage: tools/certdark.py <out dir> [slug ...]      ->  <out>/cert-<slug>-{back,front}.png  (1200²)
Colours: CERT_DARK below (the 23 Oct dark map, as tagged on the Shopify drafts); hexes from the custom page palette.
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEX = {'emerald': '#0F6156', 'espresso': '#4B3631', 'grape': '#332552', 'moss': '#27392E', 'yam': '#BE531C', 'violet': '#7474C1'}
NAME = {'emerald': 'Emerald', 'espresso': 'Espresso', 'grape': 'Grape', 'moss': 'Moss', 'yam': 'Yam', 'violet': 'Violet'}
CERT_DARK = {  # site slug: dark garment  (Shopify tag colour:<x> on "Certified-ish Dark — … tee")
    'cert-open-water': 'moss', 'cert-advanced-open-water': 'emerald', 'cert-altitude': 'yam', 'cert-boat': 'yam',
    'cert-buoyancy': 'yam', 'cert-cave': 'espresso', 'cert-deep': 'espresso', 'cert-dpv': 'violet', 'cert-drift': 'yam',
    'cert-fish-id': 'yam', 'cert-ice': 'espresso', 'cert-night': 'espresso', 'cert-nitrox': 'violet', 'cert-rebreather': 'grape',
    'cert-search-recovery': 'espresso', 'cert-self-reliant': 'grape', 'cert-sidemount': 'grape', 'cert-smb': 'violet',
    'cert-tech': 'grape', 'cert-uw-photo': 'yam'}
W = np.array([0.2126, 0.7152, 0.0722])
WHITE = np.array([0.96, 0.95, 0.93])           # white ink, a hair warm
DSRED = np.array([0xC8, 0x20, 0x26]) / 255     # the DS mark red (PMS 1795 C match)


def hexrgb(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255


def convert(src, dst, hexc):
    im = np.asarray(Image.open(src).convert('RGB')).astype(float) / 255
    edge = np.concatenate([im[:8].reshape(-1, 3), im[-8:].reshape(-1, 3), im[:, :8].reshape(-1, 3), im[:, -8:].reshape(-1, 3)])
    bg = np.median(edge, 0)
    diff = np.abs(im - bg).sum(2)
    mask = nd.binary_fill_holes(nd.binary_opening(diff > 0.06, iterations=2))
    lab, n = nd.label(mask); mask = lab == (np.argmax(nd.sum(mask, lab, range(1, n + 1))) + 1)
    mask = nd.binary_fill_holes(mask)
    lum = im @ W
    body = nd.binary_erosion(mask, iterations=12)
    base = np.median(im[body], 0); lo = base @ W
    # red of the DS mark, as soft coverage: much redder than the fabric, and only on a sleeve (black ink mixed into a coral or
    # pink fabric keeps the fabric's own red ÷ green+blue, so it is not caught). On a red-ish fabric (coral) the shape is
    # taken from a non-red render instead — the mark sits in the same place on every shirt of the template.
    def red_cov(img, b):
        ratio = img[..., 0] / (img[..., 1] + img[..., 2] + 0.02); br = b[0] / (b[1] + b[2] + 0.02)
        t0 = max(0.62, 1.35 * br)
        c = np.clip((ratio - t0) / max(1.15 - t0, 0.15), 0, 1) * (img[..., 0] - np.maximum(img[..., 1], img[..., 2]) > 0.08)
        c[:, 380:820] = 0                                  # the DS mark is only ever on a sleeve
        return c
    base_ratio = base[0] / (base[1] + base[2] + 0.02)
    if base_ratio > 0.8:
        ref = np.asarray(Image.open(src.replace(os.path.basename(src).split('-back')[0].split('-front')[0], 'cert-night')).convert('RGB')).astype(float) / 255
        rb = np.median(ref[nd.binary_erosion(mask, iterations=12)], 0)
        ra = red_cov(ref, rb)
    else:
        ra = red_cov(im, base)
    ra = ra * nd.binary_erosion(mask, iterations=6)
    red = ra > 0.02
    # fabric luminance without the ink: grey closing (ink is darker than the fabric), then smooth
    fab = nd.grey_closing(np.where(mask, lum, lo), size=(9, 9))
    fab = np.maximum(nd.gaussian_filter(fab, 1.5), lum)
    # ink is near-black against the fabric; seams, folds and the outline are only a little darker: tell them apart by ratio
    r = lum / np.maximum(fab, 1e-3)
    a = np.clip((0.86 - r) / 0.50, 0, 1) ** 0.85
    a[~nd.binary_erosion(mask, iterations=6)] = 0          # the shirt's own outline stays fabric
    a = a * (1 - ra)
    fab = np.where(a > 0, fab, lum)                        # where there is no ink, every fold and seam is kept as it was
    shade = np.clip(fab / max(lo, 1e-3), 0.45, 1.15)
    new = hexrgb(hexc)
    fabric = new * shade[..., None]
    ink = WHITE * (np.clip(shade, 0.8, 1.1)[..., None] ** 0.35)
    out = fabric * (1 - a[..., None]) + ink * a[..., None]
    out = out * (1 - ra[..., None]) + DSRED * np.clip(shade, 0.8, 1.1)[..., None] * ra[..., None]
    # the edge: the light render's rim mixes background and the old colour, so rebuild it — a smoothed outline, the edge
    # pixels taking the shade of the nearest interior pixel, blended into the background with soft coverage
    core = nd.binary_erosion(mask, iterations=3)
    idx = nd.distance_transform_edt(~core, return_distances=False, return_indices=True)
    out_edge = out[idx[0], idx[1]]
    smooth = nd.gaussian_filter(mask.astype(float), 1.6) > 0.5
    cov = np.clip(nd.gaussian_filter(smooth.astype(float), 0.8), 0, 1)
    full = np.where(core[..., None], out, out_edge)
    res = bg * (1 - cov[..., None]) + full * cov[..., None]
    Image.fromarray((np.clip(res, 0, 1) * 255 + 0.5).astype(np.uint8)).save(dst)


def main():
    out = sys.argv[1]; only = set(sys.argv[2:]); os.makedirs(out, exist_ok=True)
    for slug, col in CERT_DARK.items():
        if only and slug not in only: continue
        for view in ('back', 'front'):
            convert(f'{SITE}/img/certs/{slug}-{view}.webp', f'{out}/{slug}-{view}.png', HEX[col])
        print(slug, NAME[col], flush=True)


if __name__ == '__main__':
    main()
