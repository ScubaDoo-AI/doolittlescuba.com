#!/usr/bin/env python3
"""Logbook-only dive sites: the site stays, its art comes off (26 Nov 2026: Eric, "Hide Kioa for now",
then "Leave photos intact only remove references to the art").

A logbook-only site keeps everything about the place: its guide page with its photos and field notes, its map pin,
its row in the home page site list, the guide pager and the sitemap. What comes off is the art:
  - its card in the Signature art grid ("The art")
  - its entry in the design search index (js/designs.json)
  - the "In progress" art status: in the sites data it becomes "logbook" (the map popup and the home list say "Logbook")
  - on its guide: the "In progress" pill, the "Tell me when it's finished" button and its line about the release, the
    "On the shirt" section, and "drawn for the Doolittle Scuba line" in the page description

To bring a site's art back once it is for sale: take the slug out of LOGBOOK, revert this tool's commit for that site
(or rebuild the pages), and set its status in the sites data. tools/line_pages.py regenerates the art grid and
js/designs.json, so re-run this tool after it. Idempotent. Then tools/bust.py.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGBOOK = {'kioa-island': 'Kioa Island'}
rd = lambda p: open(os.path.join(ROOT, p), encoding='utf-8').read()


def wr(p, s, s0):
    if s != s0:
        open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s); print('changed:', p)


def main():
    pages = [os.path.relpath(os.path.join(d, f), ROOT) for d, _, fs in os.walk(ROOT) for f in fs
             if f.endswith('.html') and not os.path.relpath(d, ROOT).startswith(('renders', 'shopify-theme', '.git'))]
    for p in sorted(pages):
        s = s0 = rd(p)
        for slug, name in LOGBOOK.items():
            # sites data (map pins, lists): art status → logbook
            s = re.sub(r'(\{"slug": "' + re.escape(slug) + r'"[^{}]*?"status": ")(?:progress|finished)(")', r'\1logbook\2', s)
            # home page site list row: the art tag → Logbook
            s = re.sub(r'(<li><a href="(?:\.\./|/)?sites/' + re.escape(slug) + r'/".*?)<span class="tag (?:progress|finished)">[^<]*</span>',
                       r'\1<span class="tag logbook">Logbook</span>', s, count=1, flags=re.S)
            # Signature art grid card
            s = re.sub(r'<figure class="dz"(?:(?!</figure>).)*?<span class="dz-t">' + re.escape(name) + r'</span>.*?</figure>', '', s, flags=re.S)
            # the site's own guide: art pill, "On the shirt", description wording
            if p.replace(os.sep, '/') == f'sites/{slug}/index.html':
                s = re.sub(r'<span class="pill (?:progress|finished)">[^<]*</span>', '', s)
                s = re.sub(r'\s*<section aria-labelledby="shirt-h">.*?</section>', '', s, count=1, flags=re.S)
                s = re.sub(r'\s*<a class="btn" href="/\?site=' + re.escape(slug) + r'#contact"[^>]*>[^<]*</a>', '', s)   # "Tell me when it's finished" (the art release)
                s = s.replace(' Use the button above and they\u2019ll reach you with the release.', '')
                s = s.replace('a dive site we have dived and drawn for the Doolittle Scuba line.',
                              'a dive site we have dived. Photos and field notes from our logbook.')
        wr(p, s, s0)
    # design search index
    dj = os.path.join(ROOT, 'js/designs.json'); d = json.load(open(dj, encoding='utf-8'))
    keep = [x for x in d if x.get('slug') not in LOGBOOK]
    if len(keep) != len(d):
        open(dj, 'w', encoding='utf-8').write(json.dumps(keep, ensure_ascii=False, separators=(',', ':')))
        print('changed: js/designs.json (', len(d) - len(keep), 'entry removed )')
    # map popup label and list tag colour for the new status
    m = os.path.join(ROOT, 'js/divemap.js'); j = open(m, encoding='utf-8').read()
    j2 = j.replace("progress:'In progress'};", "progress:'In progress',logbook:'Logbook'};")
    if j2 != j: open(m, 'w', encoding='utf-8').write(j2); print('changed: js/divemap.js')
    c = os.path.join(ROOT, 'css/site.css'); cs = open(c, encoding='utf-8').read()
    if '.tag.logbook' not in cs:
        cs = cs.replace('.tag.progress{color:var(--red)}', '.tag.progress{color:var(--red)}.tag.logbook{color:var(--muted)}', 1)
        open(c, 'w', encoding='utf-8').write(cs); print('changed: css/site.css')


if __name__ == '__main__':
    main()
