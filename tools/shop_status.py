#!/usr/bin/env python3
"""Shop words on what you can buy, workshop words on the art (26 Nov 2026, review item #4).

Rule: anything a visitor can buy says "Coming soon" now (and the cart's own label once live). "Art finished",
"In progress" and "Sample print" are workshop words: they stay on the art grids (the dz cards under each collection's
"the art") and on a site that has nothing for sale yet (Kioa Island), and come off everything else.

  sites with products (a DS-<code>-T in js/catalog.json)   "finished" → "available" in every sites-data block, the home
                                                           page site list, each guide's header pill and its map pin
  signature/index.html shirt cards                         pill "Sample print" (completed) → "Coming soon" (available)
  js/deck.js                                               the open card's button no longer says "Sample print"

Idempotent. Then tools/bust.py.
"""
import glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairs import SITES, GUIDE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(ROOT, 'js/catalog.json')))
SELLING = {slug for slug, code, *_ in SITES if f'DS-{code}-T' in CAT}


def site_json(s):
    """"status": "finished" → "available" for selling sites, in any JSON list or object on the page."""
    def fix(m):
        return m.group(0).replace('"status": "finished"', '"status": "available"') if m.group(1) in SELLING else m.group(0)
    return re.sub(r'\{"slug": "([a-z0-9-]+)"[^{}]*?\}', fix, s)


def main():
    changed = []
    for p in sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
        rel = os.path.relpath(p, ROOT)
        if rel.startswith(('renders', 'shopify-theme')): continue
        s = s0 = open(p, encoding='utf-8').read()
        s = site_json(s)
        if rel == 'index.html':   # the site list under the map
            for slug in SELLING:
                s = re.sub(r'(data-umami-event-site="' + slug + r'">.*?)<span class="tag finished">Art finished</span>',
                           r'\1<span class="tag available">Coming soon</span>', s, count=1, flags=re.S)
        m = re.match(r'sites/([a-z0-9-]+)/index\.html$', rel.replace(os.sep, '/'))
        if m and m.group(1) in {GUIDE.get(x, x) for x in SELLING}:   # the guide's header pill
            s = s.replace('<span class="pill finished">Art finished</span>', '<span class="pill available">Coming soon</span>')
        if rel == os.path.join('signature', 'index.html'):   # shirt cards only; the art grid keeps its pills
            s = re.sub(r'(<figure class="sh"[^>]*>.*?)<span class="pill completed">Sample print</span>(.*?</figure>)',
                       r'\1<span class="pill available">Coming soon</span>\2', s, flags=re.S)
        if s != s0:
            open(p, 'w', encoding='utf-8').write(s); changed.append(rel)
    d = os.path.join(ROOT, 'js/deck.js'); j = open(d, encoding='utf-8').read()
    j2 = j.replace("(it.statusClass==='completed'?'Sample print':'Coming soon')", "'Coming soon'")
    if j2 != j: open(d, 'w', encoding='utf-8').write(j2); changed.append('js/deck.js')
    print(len(SELLING), 'sites selling;', len(changed), 'files changed:', ', '.join(changed))


if __name__ == '__main__':
    main()
