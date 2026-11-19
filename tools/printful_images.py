#!/usr/bin/env python3
"""The Printful images, kept so no page builder can put an old render back.

tools/printful_images.json maps "<page>|<data-line>|<data-slug>" to the figure's image attributes
(data-front, data-back, data-sleeve and the thumb's src). Those images are Printful's own mockups,
on the Shopify CDN or in img/sleeves, img/hats/pf.

  tools/printful_images.py capture   record every figure that already shows a Printful image
  tools/printful_images.py apply     write the recorded images back into the pages (bust.py runs this first)

A builder that regenerates a page (n73.py, certdark.py, line_pages.py, hats_v3.py, ...) writes its old
local paths; the next bust.py run puts the Printful images back.
"""
import json, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'tools', 'printful_images.json')
FIG = re.compile(r'<figure class="sh"[^>]*>.*?</figure>', re.S)
KEYS = ('data-front', 'data-back', 'data-sleeve')


def printful(v):
    return bool(v) and ('cdn.shopify.com' in v or '/sleeves/' in v or '/hats/pf/' in v)


def pages():
    for p in sorted(glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)):
        rel = os.path.relpath(p, ROOT)
        if not rel.startswith(('shopify-theme', 'renders', 'tools')): yield rel, p


def key(rel, fig):
    a = dict(re.findall(r'\bdata-(line|slug)="([^"]*)"', fig.split('>', 1)[0]))
    return f'{rel}|{a.get("line", "")}|{a.get("slug", "")}'


def capture():
    db = {}
    for rel, p in pages():
        for fig in FIG.findall(open(p, encoding='utf-8').read()):
            btn = re.search(r'<button[^>]*class="sh-img"[^>]*>', fig)
            if not btn: continue
            attrs = dict(re.findall(r'\b(data-front|data-back|data-sleeve)="([^"]*)"', btn.group(0)))
            if not any(printful(v) for v in attrs.values()): continue
            img = re.search(r'<img src="([^"]+)"', fig)
            db[key(rel, fig)] = {**attrs, 'src': img.group(1) if img else ''}
    json.dump(db, open(DB, 'w'), indent=1, sort_keys=True)
    print(len(db), 'figures recorded')


def apply():
    if not os.path.exists(DB): return 0
    db = json.load(open(DB)); changed = 0
    for rel, p in pages():
        s = open(p, encoding='utf-8').read()
        def fix(m):
            fig = m.group(0); rec = db.get(key(rel, fig))
            if not rec: return fig
            def btn(b):
                b = b.group(0)
                for k in KEYS:
                    if k not in rec: continue
                    if f'{k}="' in b: b = re.sub(rf'\b{k}="[^"]*"', f'{k}="{rec[k]}"', b, count=1)
                    else: b = b.replace('class="sh-img"', f'class="sh-img" {k}="{rec[k]}"', 1)
                return b
            fig = re.sub(r'<button[^>]*class="sh-img"[^>]*>', btn, fig, count=1)
            if rec.get('src'): fig = re.sub(r'(<img src=")[^"]*(")', lambda k: k.group(1) + rec['src'] + k.group(2), fig, count=1)
            return fig
        t = FIG.sub(fix, s)
        if t != s: open(p, 'w', encoding='utf-8').write(t); changed += 1; print('printful images:', rel)
    return changed


if __name__ == '__main__':
    {'capture': capture, 'apply': apply}[sys.argv[1] if len(sys.argv) > 1 else 'apply']()
