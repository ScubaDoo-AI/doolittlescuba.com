#!/usr/bin/env python3
"""The site's own copies of product images on the dark DS wallpaper (26 Nov 2026), the same look and rules as
tools/dark_bg.py (which does the store). The deck images that come from Shopify's CDN follow the store by themselves;
these folders hold local copies:

  img/hats/pf, img/organic/caps, img/organic/beanie, img/jackets, img/towels   product photos
  img/stickers                                                                    single die-cut badges: cut out
  img/packs                                                                       pack sheets: kept whole as cards

Page heroes, banners, tiles and share images (names with hero / banner / tile / og / sheet-bg) are left alone.
Each file is rewritten in place in its own format; already-converted files are skipped, so re-running is safe.
Originals: git history. Then tools/bust.py.

usage: tools/dark_bg_site.py [--dry] [folders...]
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import dark_bg as D
from PIL import Image

FOLDERS = {'img/hats/pf': [], 'img/organic/caps': [], 'img/organic/beanie': [], 'img/jackets': [], 'img/towels': [],
           'img/stickers': [], 'img/packs': ['sticker']}
SKIP = ('hero', 'banner', 'tile', 'og-', 'sheet-bg')


def main():
    dry = '--dry' in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    from collections import Counter
    c = Counter()
    for folder, tags in FOLDERS.items():
        if only and folder not in only: continue
        for f in sorted(os.listdir(os.path.join(ROOT, folder))):
            p = os.path.join(ROOT, folder, f); low = f.lower()
            if not low.endswith(('.webp', '.jpg', '.jpeg', '.png')) or any(s in low for s in SKIP):
                c['left'] += 1; continue
            im = Image.open(p); im.load()
            new, how = D.transform(im, tags)
            c[how] += 1
            if new is None or dry: continue
            fmt = {'.webp': 'WEBP', '.png': 'PNG'}.get(os.path.splitext(low)[1], 'JPEG')
            open(p, 'wb').write(D.save(new, fmt))
            print(how.ljust(12), folder + '/' + f, flush=True)
    print(dict(c))


if __name__ == '__main__':
    main()
