#!/usr/bin/env python3
"""Put the 36 1N73LL1G3NC3 tees on Printful.

The print masters live in Shopify Files (cdn.shopify.com/.../files/N73-nn_front.png: the 12 x 16 in front area at
300 dpi, transparent, the ink at true size — up to 11.5 x 15 in — in its own colours) and the Shopify products already
exist (36 products / 216 variants, all Draft, collection 492952813754). Printful needs a private API token: Printful
dashboard → Settings → Developers → Tokens (scopes: Sync products read+write, File library write), with the store
selected. Pass it as PRINTFUL_TOKEN. Nothing is sent without the token; without it the script prints the plan.

  tools/printful_n73.py                 # plan: Printful variant per size, cost vs. our price, per product
  tools/printful_n73.py --route dtf     # the same as a DTF transfer instead of DTG
  PRINTFUL_TOKEN=… tools/printful_n73.py --link     # Shopify-connected store: attach the file + variants to the
                                                    #   products Printful imported from Shopify (matched by SKU)
  PRINTFUL_TOKEN=… tools/printful_n73.py --create   # manual / API store: create the sync products outright

Garment (Printful catalog, Nov 2026): Comfort Colors 1717 = product 586. Our nine colours are in stock in the US:
S–XL $15.60, 2XL $17.60, 3XL $19.60. One placement, the front: DTG is included in the blank price, so a tee costs
$15.60 / $17.60 / $19.60 against our $42 / $45 / $45 — about $26 a shirt before shipping; DTF adds $5.95. The master
fills Printful's front area exactly (1800 x 2400 at 150 dpi), so no positioning is needed.
"""
import os, sys, json, time, urllib.request, urllib.error

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(f'{SITE}/tools/n73_designs.json'))
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
BASE = {'S': 15.60, 'M': 15.60, 'L': 15.60, 'XL': 15.60, '2XL': 17.60, '3XL': 19.60}
PRICE = {'S': 42.00, 'M': 42.00, 'L': 42.00, 'XL': 42.00, '2XL': 45.00, '3XL': 45.00}
DTF_FEE = 5.95
STEP = 32768          # Shopify variant ids run S, M, L, XL, 2XL, 3XL in steps of 32768 from the S id

# Printful catalog variant ids for Comfort Colors 1717 (product 586), by our colour key then size (checked 2 Nov 2026)
PF = {
    'black':      {'S': 15114, 'M': 15115, 'L': 15116, 'XL': 15117, '2XL': 15118, '3XL': 16326},
    'blue-spruce': {'S': 17686, 'M': 17687, 'L': 17688, 'XL': 17689, '2XL': 17690, '3XL': 17691},
    'granite':    {'S': 17655, 'M': 17656, 'L': 17657, 'XL': 17658, '2XL': 17659, '3XL': 17660},
    'graphite':   {'S': 21264, 'M': 21265, 'L': 21266, 'XL': 21267, '2XL': 21268, '3XL': 21269},
    'ivory':      {'S': 16523, 'M': 16524, 'L': 16525, 'XL': 16526, '2XL': 16527, '3XL': 16528},
    'midnight':   {'S': 21541, 'M': 21542, 'L': 21543, 'XL': 21544, '2XL': 21545, '3XL': 21546},
    'moss':       {'S': 17700, 'M': 17701, 'L': 17703, 'XL': 17702, '2XL': 17704, '3XL': 17705},
    'pepper':     {'S': 17693, 'M': 17694, 'L': 17695, 'XL': 17696, '2XL': 17697, '3XL': 17698},
    'true-navy':  {'S': 15181, 'M': 15182, 'L': 15183, 'XL': 15184, '2XL': 15185, '3XL': 16332},
}

# n | product id | S variant id   (Shopify, 2026-11-03)
ROWS = [l.split('|') for l in """01|10413955809466|50922238836922
02|10413955940538|50922240475322
03|10413955973306|50922240671930
04|10413956006074|50922240868538
05|10413956038842|50922241065146
06|10413956071610|50922241261754
07|10413956104378|50922241458362
08|10413956137146|50922241654970
09|10413956169914|50922241851578
10|10413956202682|50922242048186
11|10413956464826|50922245226682
12|10413956497594|50922245423290
13|10413956530362|50922245619898
14|10413956563130|50922245816506
15|10413956628666|50922246045882
16|10413956661434|50922246242490
17|10413956694202|50922246439098
18|10413956726970|50922246635706
19|10413956759738|50922246832314
20|10413957054650|50922249879738
21|10413957087418|50922255253690
22|10413957120186|50922255450298
23|10413957152954|50922255646906
24|10413957185722|50922255843514
25|10413957251258|50922256072890
26|10413957284026|50922256269498
27|10413957316794|50922256466106
28|10413957349562|50922256662714
29|10413957382330|50922256859322
30|10413957415098|50922257055930
31|10413957447866|50922257252538
32|10413957480634|50922257449146
33|10413957513402|50922257645754
34|10413957546170|50922257842362
35|10413957578938|50922258038970
36|10413957611706|50922258235578""".strip().splitlines()]
IDS = {int(n): (int(p), int(v)) for n, p, v in ROWS}


def plan(route):
    out = []
    for d in D['designs']:
        pid, vid = IDS[d['n']]; ck = d['colour']; colour = D['colours'][ck]['name']
        fee = 0.0 if route == 'dtg' else DTF_FEE
        files = [{'type': 'default' if route == 'dtg' else 'front_dtf', 'url': f'{CDN}N73-{d["n"]:02d}_front.png',
                  'position': {'area_width': 1800, 'area_height': 2400, 'width': 1800, 'height': 2400, 'top': 0, 'left': 0}}]
        variants = [dict(sku=f'DS-N{d["n"]:02d}-T-{z}', size=z, shopify_variant=vid + i * STEP, variant_id=PF[ck][z],
                         cost=round(BASE[z] + fee, 2), price=PRICE[z], margin=round(PRICE[z] - BASE[z] - fee, 2)) for i, z in enumerate(SIZES)]
        out.append(dict(n=d['n'], slug=d['slug'], title=f'1N73LL1G3NC3 — {d["name"]} tee', colour=colour, shopify_product=pid, files=files,
                        thumbnail=f'https://doolittlescuba.com/img/n73/{d["slug"]}-front.webp', variants=variants))
    return out


def api(token, method, path, body=None):
    req = urllib.request.Request('https://api.printful.com' + path, data=json.dumps(body).encode() if body is not None else None, method=method,
                                 headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f'{method} {path}: {e.code} {e.read().decode()[:400]}')


if __name__ == '__main__':
    route = 'dtf' if '--route' in sys.argv and sys.argv[sys.argv.index('--route') + 1] == 'dtf' else 'dtg'
    prods = plan(route)
    print(f'{"Product":44s} {"colour":12s} {"PF variants (S…3XL)":44s} {"cost":>13s} {"price":>9s} {"margin":>13s}')
    for p in prods:
        v = p['variants']
        print(f'{p["title"]:44s} {p["colour"]:12s} {", ".join(str(x["variant_id"]) for x in v):44s} '
              f'{v[0]["cost"]:6.2f}–{v[-1]["cost"]:5.2f} {v[0]["price"]:4.0f}–{v[-1]["price"]:3.0f} {v[-1]["margin"]:6.2f}–{v[0]["margin"]:5.2f}')
    nv = sum(len(p['variants']) for p in prods)
    print(f'\n{len(prods)} products · {nv} variants · {route.upper()} front · Printful cost one M of each ${sum(p["variants"][1]["cost"] for p in prods):.2f}'
          f' · retail ${sum(p["variants"][1]["price"] for p in prods):.2f}')
    if '--json' in sys.argv: json.dump(prods, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1); print('plan written')
    token = os.environ.get('PRINTFUL_TOKEN')
    if not token or not ({'--link', '--create'} & set(sys.argv)): sys.exit(0)
    by_sku = {v['sku']: (p, v) for p in prods for v in p['variants']}
    by_ext = {str(v['shopify_variant']): (p, v) for p in prods for v in p['variants']}
    if '--link' in sys.argv:
        items = []; offset = 0
        while True:
            res = api(token, 'GET', f'/store/products?offset={offset}&limit=100'); items += res['result']
            if len(items) >= res['paging']['total']: break
            offset += 100
        done = 0
        for sp in items:
            det = api(token, 'GET', f'/store/products/{sp["id"]}')
            for sv in det['result']['sync_variants']:
                hit = by_sku.get(sv.get('sku') or '') or by_ext.get(str(sv.get('external_id')))
                if not hit: continue
                p, v = hit
                api(token, 'PUT', f'/store/variants/{sv["id"]}', {'variant_id': v['variant_id'], 'retail_price': f'{v["price"]:.2f}', 'is_ignored': False,
                                                                'sku': v['sku'], 'files': p['files']})
                done += 1; print('linked', v['sku'], '→ variant', v['variant_id']); time.sleep(0.4)
        print(f'{done} of {nv} variants linked; the rest are not in Printful yet (Printful → Stores → Sync products → import)')
    else:
        for p in prods:
            body = {'sync_product': {'name': 'Doolittle Scuba — ' + p['title'], 'thumbnail': p['thumbnail']},
                    'sync_variants': [{'variant_id': v['variant_id'], 'retail_price': f'{v["price"]:.2f}', 'sku': v['sku'], 'external_id': str(v['shopify_variant']),
                                       'files': p['files']} for v in p['variants']]}
            res = api(token, 'POST', '/store/products', body); print('created', p['title'], '→', res['result']['id']); time.sleep(0.5)
