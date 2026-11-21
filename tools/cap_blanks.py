#!/usr/bin/env python3
"""Real Flexfit 6277 blanks for the /custom/ cap preview (Eric, 21 Nov 2026: the drawn cap needed a re-render).

Reads Printful's catalog images for product 140 (every colour, every view it has), downloads the largest file of each
and writes them with a JSON index to OUT, for the run's artifact:

  tools/cap_blanks.py OUT
    OUT/index.json             raw catalog answer, plus what was saved
    OUT/<colour>-<placement>.<ext>
"""
import os, sys, json, re, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import printful_read as PR

out = sys.argv[1] if len(sys.argv) > 1 else 'cap-blanks'; os.makedirs(out, exist_ok=True)
pages, off = [], 0
while True:
    r = PR.get(f'/v2/catalog-products/140/images?limit=20&offset={off}')
    if 'data' not in r: sys.exit(f'catalog images: {json.dumps(r)[:500]}')
    pages += r["data"]; off += 20
    if off >= (r.get('paging') or {}).get('total', 0): break
saved = []
for g in pages:
    col = re.sub(r'[^a-z0-9]+', '-', (g.get('color') or g.get('colour') or 'x').lower()).strip('-')
    for im in g.get('images', []):
        url = im.get('image_url') or im.get('background_image')
        if not url: continue
        pl = re.sub(r'[^a-z0-9_]+', '-', str(im.get('placement') or 'x').lower())
        ext = url.split('?')[0].rsplit('.', 1)[-1][:4]
        name = f'{col}-{pl}.{ext}'
        if any(s['file'] == name for s in saved): name = f'{col}-{pl}-{len(saved)}.{ext}'
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'doolittle-tools'}), timeout=120) as f: b = f.read()
        open(os.path.join(out, name), 'wb').write(b)
        saved.append(dict(file=name, colour=g.get('color'), hex=g.get('primary_hex'), placement=im.get('placement'),
                          bg=im.get('background_color'), url=url, bytes=len(b)))
        print(f'{name:40s} {len(b) // 1024:5d} KB  {url[:90]}', flush=True)
json.dump(dict(catalog=pages, saved=saved), open(os.path.join(out, 'index.json'), 'w'), indent=1)
print(f'\n{len(saved)} images for {len(pages)} colour groups')

# Where each embroidery area sits on the template photos (mockup generator templates for product 140).
t = PR.get('/mockup-generator/templates/140')
json.dump(t, open(os.path.join(out, 'templates.json'), 'w'), indent=1)
for tp in (t.get('result') or {}).get('templates', []):
    print('template', tp.get('template_id'), tp.get('image_url', '')[-70:], tp.get('template_width'), tp.get('template_height'),
          'area', tp.get('print_area_left'), tp.get('print_area_top'), tp.get('print_area_width'), tp.get('print_area_height'))
for vm in (t.get('result') or {}).get('variant_mapping', [])[:2]: print('mapping', json.dumps(vm)[:400])
