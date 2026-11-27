#!/usr/bin/env python3
"""Hide dive sites from the site without deleting them (26 Nov 2026: Eric, "Hide Kioa for now").

A hidden site keeps its guide page (/sites/<slug>/) at its address, but:
  - its entry leaves every sites-data block (map pins, the Shop by dive site list data)
  - its row leaves the home page site list
  - its card leaves the Signature art grid
  - its entry leaves the design search index (js/designs.json)
  - the guide pager skips it (the neighbours link to each other)
  - its guide leaves sitemap.xml and gets <meta name="robots" content="noindex">
Logbook photos taken there are not touched: they are trip photos, not listings.

To un-hide: take the slug out of HIDDEN and revert this tool's commit (git log -- tools/hide_sites.py), or rebuild the
pages from their sources. Note that tools/line_pages.py regenerates js/designs.json and the Signature art grid, so
re-run this tool after it. Idempotent. Then tools/bust.py.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIDDEN = {'kioa-island': 'Kioa Island'}
rd = lambda p: open(os.path.join(ROOT, p), encoding='utf-8').read()


def wr(p, s, s0):
    if s != s0:
        open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s); print('changed:', p)


def drop_json_objects(s, slug):
    # {"slug": "<slug>", ...} inside a JSON list, with the comma that joins it to its neighbour
    obj = r'\{"slug": "' + re.escape(slug) + r'"[^{}]*\}'
    s = re.sub(r',\s*' + obj, '', s)
    return re.sub(obj + r'\s*,\s*', '', s)


def main():
    pages = [os.path.relpath(os.path.join(d, f), ROOT) for d, _, fs in os.walk(ROOT) for f in fs
             if f.endswith('.html') and not os.path.relpath(d, ROOT).startswith(('renders', 'shopify-theme', '.git'))]
    for p in sorted(pages):
        s = s0 = rd(p)
        for slug, name in HIDDEN.items():
            if p.replace(os.sep, '/') == f'sites/{slug}/index.html':
                continue   # the hidden site's own guide keeps its own map data
            s = drop_json_objects(s, slug)
            s = re.sub(r'\s*<li><a href="(?:\.\./|/)?sites/' + re.escape(slug) + r'/".*?</li>', '', s, flags=re.S)
            s = re.sub(r'<figure class="dz"(?:(?!</figure>).)*?<span class="dz-t">' + re.escape(name) + r'</span>.*?</figure>', '', s, flags=re.S)
        wr(p, s, s0)
    # the guide pager: point each neighbour of a hidden site at the other neighbour
    for slug, name in HIDDEN.items():
        prev = nxt = None
        g = f'sites/{slug}/index.html'
        if os.path.exists(os.path.join(ROOT, g)):
            gs = gs0 = rd(g)
            m = re.search(r'<a class="prev" href="\.\./([a-z0-9-]+)/"><span class="eyebrow">[^<]*</span><span class="n">([^<]*)</span></a>', gs)
            n = re.search(r'<a class="next" href="\.\./([a-z0-9-]+)/"><span class="eyebrow">[^<]*</span><span class="n">([^<]*)</span></a>', gs)
            prev, nxt = (m.groups() if m else None), (n.groups() if n else None)
            if 'name="robots"' not in gs:
                gs = gs.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1)
            wr(g, gs, gs0)
        if prev and nxt:
            p = f'sites/{prev[0]}/index.html'; s = s0 = rd(p)   # prev's "next" → nxt
            s = re.sub(r'(<a class="next" href="\.\./)' + re.escape(slug) + r'(/"><span class="eyebrow">[^<]*</span><span class="n">)[^<]*(</span>)',
                       lambda m: m.group(1) + nxt[0] + m.group(2) + nxt[1] + m.group(3), s)
            wr(p, s, s0)
            p = f'sites/{nxt[0]}/index.html'; s = s0 = rd(p)    # nxt's "prev" → prev
            s = re.sub(r'(<a class="prev" href="\.\./)' + re.escape(slug) + r'(/"><span class="eyebrow">[^<]*</span><span class="n">)[^<]*(</span>)',
                       lambda m: m.group(1) + prev[0] + m.group(2) + prev[1] + m.group(3), s)
            wr(p, s, s0)
        # sitemap
        sm = sm0 = rd('sitemap.xml')
        sm = re.sub(r'\s*<url><loc>https://doolittlescuba\.com/sites/' + re.escape(slug) + r'/</loc>.*?</url>', '', sm, flags=re.S)
        wr('sitemap.xml', sm, sm0)
    # design search index
    dj = os.path.join(ROOT, 'js/designs.json'); d = json.load(open(dj, encoding='utf-8'))
    items = d if isinstance(d, list) else d.get('designs', d.get('items'))
    keep = [x for x in items if x.get('slug') not in HIDDEN]
    if len(keep) != len(items):
        if isinstance(d, list): d = keep
        else: d['designs' if 'designs' in d else 'items'] = keep
        raw = open(dj, encoding='utf-8').read()
        compact = not raw.lstrip().startswith(('[\n', '{\n'))
        open(dj, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, separators=(',', ':')) if compact else json.dumps(d, ensure_ascii=False, indent=1))
        print('changed: js/designs.json (', len(items) - len(keep), 'entry removed )')


if __name__ == '__main__':
    main()
