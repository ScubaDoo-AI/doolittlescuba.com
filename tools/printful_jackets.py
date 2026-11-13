#!/usr/bin/env python3
"""Doolittle Scuba jackets through Printful: embroidered DS mark, left chest only (Eric, 13 Nov 2026).

  Champion Packable Anorak  CO200   Printful 399  $43.42 S-XL / $45.42 2XL  + $2.95 left-chest embroidery
  SOL'S Basic Windbreaker   32000   Printful 661  $20.76 S-XL / $22.76 2XL  + $2.95 left-chest embroidery

Art: the heavy DS mark at the line spec 1.50 x 1.64 in, weight-passed to Printful's 0.05 in floor, white D + red S — the same
file as the beanie cuff and the cap side (Shopify Files). Threads 1801 White #FFFFFF, 1839 Red #CC3333, flat.
Colours: the dark ones that carry white + red thread and match the brand (navy / black), both stocked S-2XL (catalog API 13 Nov).

  tools/printful_jackets.py                          # plan table
  PRINTFUL_TOKEN=... tools/printful_jackets.py --mockups out_dir    # Printful Mockup Generator: real product mockups
  PRINTFUL_TOKEN=... tools/printful_link.py --only jackets [--apply]
"""
import os, sys, json, time, urllib.request, urllib.error

CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
CHEST = 'DS_mark_HEAVY_PF-beanie-front_1.50x1.64in_white-red.png'      # 1.60 x 1.74 in canvas incl. 0.05 in pad, 300 dpi
CHEST_IN = (1.60, 1.74)
WHITE, RED = '#FFFFFF', '#CC3333'
EMB = 2.95
SIZES = ['S', 'M', 'L', 'XL', '2XL']
# code, Printful product, title, model, colours {name: (hex, [variant ids S..2XL])}, blank cost S-XL / 2XL, price S-XL / 2XL
JACKETS = [
    dict(code='CHA', product=399, name='Champion Packable Anorak', model='CO200', handle='the-mark-champion-packable-anorak',
         colours={'Black': ('#070707', [11008, 11009, 11010, 11011, 11012]), 'Navy': ('#1e303f', [11014, 11015, 11016, 11017, 11018])},
         cost=(43.42, 45.42), price=(89.0, 92.0),
         blurb='Champion packable anorak: quarter-zip pullover, hood, kangaroo pocket, packs into its own pouch. Water-resistant 100% nylon shell.'),
    dict(code='WND', product=661, name="SOL'S Basic Windbreaker", model='32000', handle='the-mark-basic-windbreaker',
         colours={'Black': ('#1c1b1b', [16424, 16425, 16426, 16427, 16428]), 'Navy': ('#2b2e39', [16434, 16435, 16436, 16437, 16438])},
         cost=(20.76, 22.76), price=(49.0, 52.0),
         blurb="SOL'S basic windbreaker: full-zip, hood with drawcord, two pockets, folds into a pocket. Water-repellent 100% nylon."),
]
CC = {'Black': 'BLK', 'Navy': 'NVY'}


def plan():
    out = []
    for j in JACKETS:
        files = [{'type': 'embroidery_chest_left', 'url': CDN + CHEST}]
        options = [{'id': 'thread_colors_chest_left', 'value': [WHITE, RED]}]
        variants = []
        for colour, (hexc, ids) in j['colours'].items():
            for z, vid in zip(SIZES, ids):
                big = z == '2XL'
                cost = round((j['cost'][1] if big else j['cost'][0]) + EMB, 2); price = j['price'][1] if big else j['price'][0]
                variants.append(dict(sku=f"DS-MRK-{j['code']}-{CC[colour]}-{z}", colour=colour, hex=hexc, size=z, variant_id=vid,
                                     cost=cost, price=price, margin=round(price - cost, 2)))
        out.append(dict(j, files=files, options=options, variants=variants))
    return out


# ---------------- Printful Mockup Generator (v1) ----------------
def pf(method, path, body=None):
    tok = os.environ.get('PRINTFUL_TOKEN') or sys.exit('PRINTFUL_TOKEN not set')
    req = urllib.request.Request('https://api.printful.com' + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json',
                                          'X-PF-Store-Id': os.environ.get('PRINTFUL_STORE', '18960047')})
    for k in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as r: return json.loads(r.read().decode())['result']
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:600]
            if e.code == 429: time.sleep(30 * (k + 1)); continue
            sys.exit(f'Printful {method} {path}: {e.code} {msg}')


def fetch(url, dst):
    with urllib.request.urlopen(url, timeout=120) as r, open(dst, 'wb') as f: f.write(r.read())


def mockups(out):
    os.makedirs(out, exist_ok=True); log = {}
    for j in plan():
        pfi = pf('GET', f"/mockup-generator/printfiles/{j['product']}")
        area = next(p for p in pfi['printfiles'] if p['printfile_id'] in
                    {vp['placements'].get('embroidery_chest_left') for vp in pfi['variant_printfiles']})
        W, H, dpi = area['width'], area['height'], area['dpi']
        w, h = round(CHEST_IN[0] * dpi), round(CHEST_IN[1] * dpi)          # true size, never stretched to the area
        pos = dict(area_width=W, area_height=H, width=w, height=h, top=0, left=round((W - w) / 2))
        log[j['code']] = dict(area=[W, H, dpi], area_in=[round(W / dpi, 2), round(H / dpi, 2)], position=pos,
                              option_groups=pfi.get('option_groups'), options=pfi.get('options'))
        print(j['code'], 'left chest area', W, 'x', H, '@', dpi, 'dpi =', round(W / dpi, 2), 'x', round(H / dpi, 2), 'in; mark', w, 'x', h)
        for colour, (hexc, ids) in j['colours'].items():
            body = dict(variant_ids=[ids[1]], format='jpg', width=1600,
                        files=[dict(placement='embroidery_chest_left', image_url=CDN + CHEST, position=pos)],
                        product_options={'thread_colors_chest_left': [WHITE, RED]})
            task = pf('POST', f"/mockup-generator/create-task/{j['product']}", body)
            for _ in range(60):
                time.sleep(6); t = pf('GET', f"/mockup-generator/task?task_key={task['task_key']}")
                if t['status'] != 'pending': break
            if t['status'] != 'completed': print('  FAILED', colour, t.get('error')); continue
            n = 0
            for m in t['mockups']:
                shots = [(m.get('placement', 'main'), m['mockup_url'])] + [(x.get('title') or x.get('option') or 'extra', x['url']) for x in m.get('extra', [])]
                for title, url in shots:
                    slug = ''.join(c if c.isalnum() else '-' for c in title.lower()).strip('-')
                    dst = f"{out}/{j['handle']}-{colour.lower()}-{n:02d}-{slug}.jpg"; fetch(url, dst); n += 1
                    print('  ', colour, title, '->', os.path.basename(dst))
            log[j['code']].setdefault('shots', {})[colour] = n
    json.dump(log, open(f'{out}/mockups.json', 'w'), indent=1)


if __name__ == '__main__':
    if '--mockups' in sys.argv:
        mockups(sys.argv[sys.argv.index('--mockups') + 1])
    else:
        for p in plan():
            print(f"{p['name']} ({p['model']}, Printful {p['product']})")
            for v in p['variants']:
                print(f"  {v['sku']:20s} {v['colour']:6s} {v['size']:4s} PF {v['variant_id']}  cost {v['cost']:.2f}  price {v['price']:.0f}  margin {v['margin']:.2f}")
