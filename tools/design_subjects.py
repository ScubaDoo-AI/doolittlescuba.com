#!/usr/bin/env python3
"""The words on each design, read off the watermarked previews with OCR, for the design search.

    tools/design_subjects.py          # OCR every design the collection pages show that tools/design_subjects.json lacks
    tools/design_subjects.py --all    # redo them all (after previews change)

Writes tools/design_subjects.json {slug: "words …"}: the species, landmarks, labels, facts and fine print that are only in
the artwork — "goliath grouper", "narcosis", "torch", "wheel house" — so a search for a subject finds the plate or diagram
that carries it. tools/line_pages.py folds these into js/designs.json; the search boxes (home page and each collection
page) read that. OCR of hand lettering is rough, so the output is a word bag, not a transcript: lower-case, de-duplicated,
without the copyright line and without tokens that are plainly noise. Needs tesseract (apt: tesseract-ocr) + pytesseract.
"""
import json, os, re, sys
from PIL import Image, ImageOps, ImageStat
import pytesseract

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f'{SITE}/tools/design_subjects.json'
PAGES = ['signature', 'certified-ish', 'off-world', '1n73ll1g3nc3', 'aquatic-comic']
BOILER = set('original hand drawn artwork john eric doolittle all rights reserved not for reproduction jr llc copyright'.split())


def words(text):
    seen, out = set(), []
    for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]+", text):
        w = w.lower().strip("'’-")
        if len(w) < 3 or w in BOILER or w in seen or not re.search(r'[aeiouy0-9]', w): continue
        if w.isdigit() or (len(w) <= 4 and w.upper() == w): continue          # bare numbers; OCR shrapnel like RRL, CLO
        seen.add(w); out.append(w)
    return ' '.join(out)


def ocr(path):
    im = Image.open(path).convert('L')
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    im = ImageOps.autocontrast(im)
    dark = ImageStat.Stat(im).mean[0] < 128
    if dark: im = ImageOps.invert(im)
    im = im.point(lambda v: 255 if v > 150 else 0)
    return pytesseract.image_to_string(im, config='--psm 6')


def main():
    have = json.load(open(OUT)) if os.path.exists(OUT) and '--all' not in sys.argv else {}
    todo = []
    for d in PAGES:
        h = open(f'{SITE}/{d}/index.html', encoding='utf-8').read()
        for m in re.finditer(r'<button type="button" class="dz-img" data-full="([^"?]+)[^"]*" data-cap="[^"]*" data-umami-event="design-open" data-umami-event-design="([a-z0-9-]+)"', h):
            if m.group(2) not in have: todo.append((m.group(2), m.group(1)))
    for slug, src in todo:
        f = f'{SITE}/{src.lstrip("/")}'
        if not os.path.isfile(f): print('missing', src); continue
        have[slug] = words(ocr(f)); print(f'{slug:34s} {len(have[slug].split()):3d} words')
    json.dump(dict(sorted(have.items())), open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(have), 'designs in', os.path.relpath(OUT, SITE), f'({len(todo)} read now)')


if __name__ == '__main__':
    main()
