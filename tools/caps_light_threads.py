#!/usr/bin/env python3
"""Stitch files for the light and red Flexfit 6277 caps (cap recolour, 21 Nov 2026).

The cap fronts are stitched in 1801 White + 1839 Red (diver-down flag) or 1842 Royal (Alpha flag); white disappears on a
White, Khaki or Grey cap. This rewrites a file for those caps:
  light  white -> 1966 Navy #333366 everywhere, except the inside of the flag: the flag's white backing band (the border
         around the red or blue field) turns navy, the white inside it (the diver-down stripe, the Alpha hoist) stays white,
         so the flag reads as itself with a navy outline.
  red    for the Red cap: 1839 Red -> 1966 Navy (the side DS mark's S would vanish on red); white stays.
Pixels stay exactly the thread colours (the files are two-colour, no anti-aliasing), as Printful's digitizer expects.

  tools/caps_light_threads.py light IN.png OUT.png
  tools/caps_light_threads.py plain IN.png OUT.png    # no flag: side DS mark, wordmark, back tagline
  tools/caps_light_threads.py red   IN.png OUT.png
  tools/caps_light_threads.py preview IN.png OUT.png '#bdaa97'    # file on a cap colour, for checking
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

WHITE, NAVY, RED, ROYAL = (255, 255, 255), (0x33, 0x33, 0x66), (0xCC, 0x33, 0x33), (0x00, 0x53, 0x97)


def light(a):
    rgb, op = a[..., :3], a[..., 3] > 0
    white = op & np.all(rgb == WHITE, axis=-1)
    colour = op & ~white
    out = a.copy()
    if not colour.any():                      # no flag (wordmark, tagline, side mark without colour): all white -> navy
        out[white, :3] = NAVY
        return out
    lab, n = ndimage.label(op)                # the flag is the opaque component(s) that hold the red or blue field
    flag = np.isin(lab, np.unique(lab[colour]))
    dist = ndimage.distance_transform_edt(op)           # distance of each opaque pixel to the transparent ground
    band = dist[colour & flag].min() + 0.5               # the white backing is as thick as the gap from field to edge
    keep = white & flag & (dist > band)                  # white inside the flag outline: stripe / hoist
    out[white & ~keep, :3] = NAVY
    return out


def plain(a):
    """no flag (side DS mark, wordmark, tagline): every white -> navy, the red S stays red."""
    out = a.copy()
    m = (a[..., 3] > 0) & np.all(a[..., :3] == WHITE, axis=-1)
    out[m, :3] = NAVY
    return out


def red(a):
    out = a.copy()
    m = (a[..., 3] > 0) & np.all(a[..., :3] == RED, axis=-1)
    out[m, :3] = NAVY
    return out


if __name__ == '__main__':
    mode, src, dst = sys.argv[1:4]
    a = np.array(Image.open(src).convert('RGBA'))
    if mode == 'preview':
        im = Image.fromarray(a); bg = Image.new('RGBA', im.size, sys.argv[4]); bg.alpha_composite(im); bg.convert('RGB').save(dst)
    else:
        out = {'light': light, 'plain': plain, 'red': red}[mode](a)
        Image.fromarray(out).save(dst, dpi=(300, 300))
        cols = {tuple(c) for c in out[out[..., 3] > 0][:, :3]}
        print(dst, 'colours', sorted(cols))
