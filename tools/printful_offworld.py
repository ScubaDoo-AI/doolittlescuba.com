#!/usr/bin/env python3
"""Put the 60 Off-World Hunt Club tees (30 light + 30 dark) on Printful.

The print masters live in Shopify Files (cdn.shopify.com/.../files/OW-nn_{back,chest}_{light,dark}.png, 300 dpi,
transparent; backs 12 × 16 in, chests 3.5 × 4 in) and the Shopify products already exist (60 products / 360
variants, all Draft, collection 492954648762). Printful needs a private API token: Printful dashboard → Settings →
Developers → Tokens (scopes: Sync products read+write, File library write), with the store selected. Pass it as
PRINTFUL_TOKEN. Nothing is sent without the token; without it the script prints the plan.

  tools/printful_offworld.py                 # plan: Printful variant per size, cost vs. our price, per product
  tools/printful_offworld.py --route dtf     # the same with both placements as DTF transfers instead of DTG
  PRINTFUL_TOKEN=… tools/printful_offworld.py --link     # Shopify-connected store: attach files + variants to the
                                                         #   products Printful imported from Shopify (matched by SKU)
  PRINTFUL_TOKEN=… tools/printful_offworld.py --create   # manual / API store: create the sync products outright

Garment (Printful catalog, Nov 2026): Comfort Colors 1717 = product 586, 350 variants. Our 13 colours are all
in stock in the US: S–XL $15.60, 2XL $17.60, 3XL $19.60 (4XL $21.60, not offered). DTG front print is included,
the back print adds $5.95; DTF charges $5.95 per placement. So a light or dark tee costs $21.55 / $23.55 / $25.55
on DTG against our $42 / $45 / $45 — about $20 a shirt before shipping. Placement positions are in Printful's
150-dpi print-area pixels (12 × 16 in = 1800 × 2400): the back fills the area; the chest art is 525 × 600 at
top 300, left 1200 — wearer's left chest, 3.75 in off centre, 2 in down. Adjust in Printful's mockup editor.
"""
import os, sys, json, time, urllib.request, urllib.error

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(f'{SITE}/tools/offworld_designs.json'))
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
BASE = {'S': 15.60, 'M': 15.60, 'L': 15.60, 'XL': 15.60, '2XL': 17.60, '3XL': 19.60}
PRICE = {'S': 42.00, 'M': 42.00, 'L': 42.00, 'XL': 42.00, '2XL': 45.00, '3XL': 45.00}
BACK_FEE, DTF_FEE = 5.95, 5.95
STEP = 32768          # Shopify variant ids run S, M, L, XL, 2XL, 3XL in steps of 32768 from the S id

# Printful catalog variant ids for Comfort Colors 1717 (product 586), by our colour key then size
PF = {
    'light-blue': {'S': 17648, 'M': 17649, 'L': 17650, 'XL': 17651, '2XL': 17652, '3XL': 17653},   # Chambray
    'granite':    {'S': 17655, 'M': 17656, 'L': 17657, 'XL': 17658, '2XL': 17659, '3XL': 17660},
    'sage':       {'S': 17707, 'M': 17708, 'L': 17709, 'XL': 17710, '2XL': 17711, '3XL': 17712},   # Bay
    'lagoon-blue': {'S': 17679, 'M': 17681, 'L': 17680, 'XL': 17682, '2XL': 17683, '3XL': 17684},
    'butter':     {'S': 15166, 'M': 15167, 'L': 15168, 'XL': 15169, '2XL': 15170, '3XL': 16328},
    'ivory':      {'S': 16523, 'M': 16524, 'L': 16525, 'XL': 16526, '2XL': 16527, '3XL': 16528},
    'graphite':   {'S': 21264, 'M': 21265, 'L': 21266, 'XL': 21267, '2XL': 21268, '3XL': 21269},
    'true-navy':  {'S': 15181, 'M': 15182, 'L': 15183, 'XL': 15184, '2XL': 15185, '3XL': 16332},
    'midnight':   {'S': 21541, 'M': 21542, 'L': 21543, 'XL': 21544, '2XL': 21545, '3XL': 21546},
    'moss':       {'S': 17700, 'M': 17701, 'L': 17703, 'XL': 17702, '2XL': 17704, '3XL': 17705},
    'blue-spruce': {'S': 17686, 'M': 17687, 'L': 17688, 'XL': 17689, '2XL': 17690, '3XL': 17691},
    'black':      {'S': 15114, 'M': 15115, 'L': 15116, 'XL': 15117, '2XL': 15118, '3XL': 16326},
    'pepper':     {'S': 17693, 'M': 17694, 'L': 17695, 'XL': 17696, '2XL': 17697, '3XL': 17698},
}

# code | slug | light product id | light S variant id | dark product id | dark S variant id   (Shopify, 2026-11-02)
ROWS = [l.split('|') for l in """OW01|ow-cloaked|10413971013818|50922419781818|10413973438650|50922454810810
OW02|ow-souvenir|10413971046586|50922419978426|10413973471418|50922455007418
OW03|ow-wormhole|10413971079354|50922420175034|10413973504186|50922455204026
OW04|ow-nap|10413971112122|50922420371642|10413973536954|50922455400634
OW05|ow-awkward|10413971144890|50922420568250|10413973569722|50922455597242
OW06|ow-nervous|10413971177658|50922420764858|10413973602490|50922455793850
OW07|ow-local|10413971210426|50922420961466|10413973635258|50922455990458
OW08|ow-reef|10413971243194|50922421158074|10413973668026|50922456187066
OW09|ow-light-years|10413971275962|50922421354682|10413973700794|50922456383674
OW10|ow-rude|10413971308730|50922421551290|10413973733562|50922456580282
OW11|ow-okayest|10413972324538|50922440130746|10413974028474|50922465034426
OW12|ow-hot-tub|10413972357306|50922440327354|10413974061242|50922465231034
OW13|ow-fly-back|10413972390074|50922440523962|10413974094010|50922465427642
OW14|ow-two-stars|10413972422842|50922440720570|10413974126778|50922465624250
OW15|ow-dinner|10413972455610|50922440917178|10413974159546|50922465820858
OW16|ow-menu|10413972488378|50922441113786|10413974192314|50922466017466
OW17|ow-dad|10413972521146|50922441310394|10413974225082|50922466214074
OW18|ow-group-chat|10413972586682|50922442686650|10413974257850|50922466410682
OW19|ow-meeting|10413972619450|50922442883258|10413974290618|50922466607290
OW20|ow-aliens|10413972652218|50922443079866|10413974323386|50922466803898
OW21|ow-directions|10413972914362|50922451566778|10413974683834|50922471030970
OW22|ow-pending|10413972947130|50922451763386|10413974716602|50922471227578
OW23|ow-gap-year|10413973012666|50922451992762|10413974749370|50922471424186
OW24|ow-suggestion|10413973045434|50922452189370|10413974782138|50922471620794
OW25|ow-coffee|10413973078202|50922452385978|10413974814906|50922471817402
OW26|ow-hunter|10413973110970|50922452582586|10413974847674|50922472014010
OW27|ow-out-late|10413973143738|50922452779194|10413974880442|50922472210618
OW28|ow-patience|10413973176506|50922452975802|10413974913210|50922472407226
OW29|ow-mornings|10413973209274|50922453172410|10413974945978|50922472603834
OW30|ow-deeper|10413973242042|50922453369018|10413974978746|50922472800442""".strip().splitlines()]

BY_SLUG = {d['slug']: d for d in D['designs']}


def files(code, line, route):
    n = code[2:]; tag = 'light' if line == 'light' else 'dark'
    area = {'area_width': 1800, 'area_height': 2400}
    return [{'type': 'back' if route == 'dtg' else 'back_dtf', 'url': f'{CDN}OW-{n}_back_{tag}.png',
             'position': dict(area, width=1800, height=2400, top=0, left=0)},
            {'type': 'default' if route == 'dtg' else 'front_dtf', 'url': f'{CDN}OW-{n}_chest_{tag}.png',
             'position': dict(area, width=525, height=600, top=300, left=1200)}]


def plan(route):
    out = []
    for code, slug, lp, lv, dp, dv in ROWS:
        d = BY_SLUG[slug]
        for line, pid, vid in (('light', lp, lv), ('dark', dp, dv)):
            ck = d[line]; colour = D['colours'][line][ck]['name']; dark = line == 'dark'
            title = f'Off-World Hunt Club{" Dark" if dark else ""} — {d["name"]} tee'
            fee = BACK_FEE if route == 'dtg' else 2 * DTF_FEE
            variants = []
            for i, z in enumerate(SIZES):
                cost = BASE[z] + fee
                variants.append(dict(sku=f'DS-{code}-{"TD" if dark else "T"}-{z}', size=z, shopify_variant=int(vid) + i * STEP, variant_id=PF[ck][z],
                                     cost=round(cost, 2), price=PRICE[z], margin=round(PRICE[z] - cost, 2)))
            out.append(dict(code=code, slug=slug, line=line, title=title, colour=colour, shopify_product=int(pid), files=files(code, line, route),
                            thumbnail=f'https://doolittlescuba.com/img/offworld/{"dark/" if dark else ""}{slug}-back.webp', variants=variants))
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
    print(f'{"Product":52s} {"colour":12s} {"PF variants (S…3XL)":44s} {"cost":>13s} {"price":>9s} {"margin":>13s}')
    for p in prods:
        v = p['variants']
        print(f'{p["title"]:52s} {p["colour"]:12s} {", ".join(str(x["variant_id"]) for x in v):44s} '
              f'{v[0]["cost"]:6.2f}–{v[-1]["cost"]:5.2f} {v[0]["price"]:4.0f}–{v[-1]["price"]:3.0f} {v[-1]["margin"]:6.2f}–{v[0]["margin"]:5.2f}')
    nv = sum(len(p['variants']) for p in prods)
    print(f'\n{len(prods)} products · {nv} variants · {route.upper()} back + chest · Printful cost one M of each ${sum(p["variants"][1]["cost"] for p in prods):.2f}'
          f' · retail ${sum(p["variants"][1]["price"] for p in prods):.2f}')
    if '--json' in sys.argv: json.dump(prods, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1); print('plan written')
    token = os.environ.get('PRINTFUL_TOKEN')
    if not token or not ({'--link', '--create'} & set(sys.argv)): sys.exit(0)
    by_sku = {v['sku']: (p, v) for p in prods for v in p['variants']}
    by_ext = {str(v['shopify_variant']): (p, v) for p in prods for v in p['variants']}
    if '--link' in sys.argv:
        # products Printful imported from Shopify: sync variants carry the Shopify variant id as external_id, and our sku
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
