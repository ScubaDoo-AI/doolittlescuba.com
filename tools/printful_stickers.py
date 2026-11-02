#!/usr/bin/env python3
"""Put the 45 sticker SKUs on Printful.

The print files live in Shopify Files (cdn.shopify.com/.../files/<SKU>.png, 300 dpi, transparent) and the Shopify
products already exist (32 products / 45 variants, all Draft). Printful needs a private API token: Printful
dashboard → Settings → Developers → Tokens (scopes: Sync products read+write, File library write), with the store
selected. Pass it as PRINTFUL_TOKEN. Nothing is sent without the token; without it the script prints the plan.

  tools/printful_stickers.py                 # plan: Printful product, size, cost vs. our price, per SKU
  tools/printful_stickers.py --route diecut  # the same on Printful's die-cut vinyl instead of kiss-cut
  PRINTFUL_TOKEN=… tools/printful_stickers.py --link     # Shopify-connected store: attach files + sizes to the
                                                         #   products Printful imported from Shopify (matched by SKU)
  PRINTFUL_TOKEN=… tools/printful_stickers.py --create   # manual / API store: create the sync products outright

Routes (Printful catalog, Nov 2026): kiss-cut vinyl #358 (3×3 $2.34, 4×4 $2.54, 5.5×5.5 $2.74, 15×3.75 $5.47),
die-cut matte vinyl #957 (2–6 in squares, $3.86–6.08), kiss-cut sheet #505 (5.83×8.27 in, $5.15). Our prices only
clear on the kiss-cut route; die-cut needs a price rise (see the plan). The Full Set is an 8.5×11 sheet; Printful's
sheet is A5, so it is served as the re-laid-out `DS-STK-A-SET12-A5.png` when that file exists in Shopify Files.
"""
import os, sys, json, csv, time, urllib.request, urllib.error

CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
KISS = {'3': 10163, '4': 10164, '5.5': 10165, '15': 16362}
KISS_COST = {'3': 2.34, '4': 2.54, '5.5': 2.74, '15': 5.47}
DIE = {'2': 24964, '3': 24965, '4': 24966, '5': 24967, '6': 24968}
DIE_COST = {'2': 3.86, '3': 4.36, '4': 4.84, '5': 5.33, '6': 6.08}
SHEET, SHEET_COST = 12917, 5.15
PRICE = {'A': 4.00, 'SET': 15.00, 'SEA': 5.00, 'STK': 5.00, 'HOR': 6.00, 'TAG': 5.00, 'KIT': 6.00, 'BMP': 7.00}

# sku, title, colourway, design size (in), Shopify variant id
ROWS = [l.split('|') for l in """DS-STK-A-OWD|Freshly Certified — Achievement Sticker||3.50x1.20|50892497060026
DS-STK-A-RES|Not On My Watch — Achievement Sticker||3.50x1.20|50892497092794
DS-STK-A-MSD|Master Diver — Achievement Sticker||3.50x1.20|50892497125562
DS-STK-A-DRI|Along For The Ride — Achievement Sticker||3.50x1.20|50892497158330
DS-STK-A-BUO|Hover Mode — Achievement Sticker||3.50x1.20|50892497191098
DS-STK-A-NTX|Spicy Air — Achievement Sticker||3.50x1.20|50892497223866
DS-STK-A-UWP|Photobombed — Achievement Sticker||3.50x1.20|50892497256634
DS-STK-A-SAR|Lost & Found — Achievement Sticker||3.50x1.20|50892497289402
DS-STK-A-SID|Dual Wield — Achievement Sticker||3.50x1.20|50892497322170
DS-STK-A-SHK|Friendly NPC — Achievement Sticker||3.50x1.20|50892497354938
DS-STK-A-FSH|Bestiary — Achievement Sticker||3.50x1.20|50892497387706
DS-STK-A-ALT|High Score — Achievement Sticker||3.50x1.20|50892497420474
DS-STK-D-OWD|Freshly Certified Sticker||2.69x3.00|50892497453242
DS-STK-D-AOW|Level Up Sticker||2.69x3.00|50892497846458
DS-STK-D-RES|Not On My Watch Sticker||2.90x3.00|50892497879226
DS-STK-D-MSD1|Master Diver (Octopus) Sticker||2.99x3.00|50892497911994
DS-STK-D-MSD2|Master Diver (Chess King) Sticker||2.50x3.00|50892497944762
DS-STK-D-DEE|Deep Diver Sticker||2.98x3.00|50892497977530
DS-STK-D-DRI|Drift Diver Sticker||3.00x2.45|50892498010298
DS-STK-D-BUO|Perfect Buoyancy Sticker||1.82x3.00|50892498043066
DS-STK-D-DRS|Warm & Dry-ish Sticker||2.49x3.00|50892498075834
DS-STK-D-NTX|Spicy Air Sticker||1.76x3.00|50892498108602
DS-STK-D-SID|Sidemount Turtle Sticker||3.00x2.40|50892498141370
DS-STK-D-FSH|ID Fish Eye Chart Sticker||2.05x3.00|50892498174138
DS-STK-D-ALT|Altitude Diver Sticker||2.70x3.00|50892498239674
DS-STK-A-SET12|Achievement Unlocked — Full Set Sticker Sheet||8.50x11.00|50892498272442
DS-STK-D-SEA-CLASSIC|The DS Seal Sticker|Classic|3.00x3.00|50920746811578
DS-STK-D-SEA-BLACK|The DS Seal Sticker|Black|3.00x3.00|50920746844346
DS-STK-D-SEA-NAVY|The DS Seal Sticker|Navy|3.00x3.00|50920746877114
DS-STK-D-SEA-RED|The DS Seal Sticker|Red|3.00x3.00|50920746909882
DS-STK-D-STK-CLASSIC|The DS Stacked Logo Sticker|Classic|3.42x2.88|50920771256506
DS-STK-D-STK-BLACK|The DS Stacked Logo Sticker|Black|3.42x2.88|50920771289274
DS-STK-D-STK-NAVY|The DS Stacked Logo Sticker|Navy|3.42x2.88|50920771322042
DS-STK-D-STK-RED|The DS Stacked Logo Sticker|Red|3.42x2.88|50920771354810
DS-STK-D-HOR-CLASSIC|The DS Horizontal Logo Sticker|Classic|5.42x1.76|50920771387578
DS-STK-D-HOR-BLACK|The DS Horizontal Logo Sticker|Black|5.42x1.76|50920771420346
DS-STK-D-HOR-NAVY|The DS Horizontal Logo Sticker|Navy|5.42x1.76|50920771453114
DS-STK-D-HOR-RED|The DS Horizontal Logo Sticker|Red|5.42x1.76|50920771485882
DS-STK-D-TAG-CLASSIC|Do - A - Little Scuba Stacked Sticker|Classic|3.42x2.51|50920771518650
DS-STK-D-TAG-NAVY|Do - A - Little Scuba Stacked Sticker|Navy|3.42x2.51|50920771551418
DS-STK-D-TAG-BLACK|Do - A - Little Scuba Stacked Sticker|Black|3.42x2.51|50920771584186
DS-STK-D-KIT-CLASSIC|Do - A - Little Scuba Dive Kit Sticker|Classic|4.92x1.82|50920771616954
DS-STK-D-KIT-NAVY|Do - A - Little Scuba Dive Kit Sticker|Navy|4.92x1.82|50920771649722
DS-STK-D-KIT-BLACK|Do - A - Little Scuba Dive Kit Sticker|Black|4.92x1.82|50920771682490
DS-STK-D-BMP-CLASSIC|Do - A - Little Scuba Bumper Sticker||7.62x3.24|50920771715258""".strip().splitlines()]

def family(sku):
    p = sku.split('-')
    if p[2] == 'A': return 'SET' if p[3].startswith('SET') else 'A'
    return p[3] if p[3] in PRICE else 'D'

def plan(route):
    out = []
    for sku, title, colour, size, vid in ROWS:
        w, h = (float(x) for x in size.split('x')); longest = max(w, h) + 0.25        # 0.12 in white border each side
        fam = family(sku); price = PRICE.get(fam, 5.00)
        if fam == 'SET':
            pv, cost, pname = SHEET, SHEET_COST, 'Kiss-cut sticker sheet 5.83×8.27 (A5 re-layout)'; url = CDN + 'DS-STK-A-SET12-A5.png'
        elif route == 'kiss':
            key = '3' if longest <= 3 else '4' if longest <= 4 else '5.5' if max(w, h) <= 5.5 else '15'   # on the 5.5 Printful scales the art a little to fit its border
            pv, cost, pname = KISS[key], KISS_COST[key], f'Kiss-cut vinyl {key}×{"3.75" if key == "15" else key} in'; url = CDN + sku + '.png'
        else:
            key = next((k for k in ('2', '3', '4', '5', '6') if longest <= float(k)), None)
            if key is None: pv, cost, pname = KISS['15'], KISS_COST['15'], 'Kiss-cut vinyl 15×3.75 in (no die-cut this size)'
            else: pv, cost, pname = DIE[key], DIE_COST[key], f'Die-cut matte vinyl {key}×{key} in'
            url = CDN + sku + '.png'
        out.append(dict(sku=sku, title=title, colour=colour, size=size, shopify_variant=vid, variant_id=pv, product=pname, cost=cost, price=price, margin=round(price - cost, 2), file=url))
    return out

def api(token, method, path, body=None):
    req = urllib.request.Request('https://api.printful.com' + path, data=json.dumps(body).encode() if body is not None else None, method=method,
                                 headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f'{method} {path}: {e.code} {e.read().decode()[:400]}')

if __name__ == '__main__':
    route = 'diecut' if '--route' in sys.argv and sys.argv[sys.argv.index('--route') + 1] == 'diecut' else 'kiss'
    rows = plan(route)
    print(f'{"SKU":22s} {"Printful product":44s} {"cost":>6s} {"price":>6s} {"margin":>7s}')
    for r in rows: print(f'{r["sku"]:22s} {r["product"]:44s} {r["cost"]:6.2f} {r["price"]:6.2f} {r["margin"]:7.2f}')
    print(f'\n{len(rows)} SKUs · total Printful cost one of each ${sum(r["cost"] for r in rows):.2f} · retail ${sum(r["price"] for r in rows):.2f}')
    token = os.environ.get('PRINTFUL_TOKEN')
    if not token or not ({'--link', '--create'} & set(sys.argv)): sys.exit(0)
    by_sku = {r['sku']: r for r in rows}
    if '--link' in sys.argv:
        # products Printful imported from Shopify: sync variants carry the Shopify variant id as external_id, and our sku
        items = []; offset = 0
        while True:
            res = api(token, 'GET', f'/store/products?offset={offset}&limit=100'); items += res['result']
            if len(items) >= res['paging']['total']: break
            offset += 100
        done = 0
        for p in items:
            d = api(token, 'GET', f'/store/products/{p["id"]}')
            for v in d['result']['sync_variants']:
                r = by_sku.get(v.get('sku') or '') or next((x for x in rows if str(x['shopify_variant']) == str(v.get('external_id'))), None)
                if not r: continue
                api(token, 'PUT', f'/store/variants/{v["id"]}', {'variant_id': r['variant_id'], 'retail_price': f'{r["price"]:.2f}', 'is_ignored': False,
                                                               'files': [{'type': 'default', 'url': r['file']}]})
                done += 1; print('linked', r['sku'], '→ variant', r['variant_id']); time.sleep(0.4)
        print(f'{done} of {len(rows)} variants linked; the rest are not in Printful yet (Printful → Stores → Sync products → import)')
    else:
        groups = {}
        for r in rows: groups.setdefault(r['title'], []).append(r)
        for title, rs in groups.items():
            body = {'sync_product': {'name': 'Doolittle Scuba — ' + title, 'thumbnail': rs[0]['file']},
                    'sync_variants': [{'variant_id': r['variant_id'], 'retail_price': f'{r["price"]:.2f}', 'sku': r['sku'], 'external_id': str(r['shopify_variant']),
                                       'files': [{'type': 'default', 'url': r['file']}]} for r in rs]}
            res = api(token, 'POST', '/store/products', body); print('created', title, '→', res['result']['id']); time.sleep(0.5)
