#!/usr/bin/env python3
"""Printful plan for the Aquatic Comic series (Comfort Colors 1717 = Printful product 586, DTG, front + back).

Only Boat Banter (S01–S20) is linked for automatic fulfilment: its print files are fixed and live in Shopify Files
(AC-Sxx_front.png / AC-Sxx_back.png, 3600 x 4800 px = the full 12 x 16 in area at 300 dpi). The 39 personalized
tees (Self-Logged, Buddy Check, Buddy System, Till Surface Do Us Part, Master Class) carry the customer's name(s),
so each order is made by hand:

  1. read the order's line-item properties (Name on the shirt / Diver 1 + Diver 2 / Husband + Wife)
  2. tools/aquatic_print.py order <code> <out> --name X [--name2 Y]     (code = the SKU's middle part, e.g. W03)
  3. Printful → New order → Comfort Colors 1717, the design's colour and the size ordered → front + back files at
     full area (12 x 16 in, no reposition) → ship to the Shopify customer. Leave those Printful sync products ignored.

  tools/printful_aquatic.py                 # table: products, colours, Printful variants, cost / price / margin
  tools/printful_aquatic.py --json out.json
  PRINTFUL_TOKEN=… tools/printful_link.py --only aquatic [--apply]     # link S01–S20 (matched by SKU)
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aquatic_designs.json'), encoding='utf-8'))
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
PF = {'true-navy': dict(zip(SIZES, [15181, 15182, 15183, 15184, 15185, 16332])),
      'black': dict(zip(SIZES, [15114, 15115, 15116, 15117, 15118, 16326])),
      'graphite': dict(zip(SIZES, [21264, 21265, 21266, 21267, 21268, 21269]))}
GARMENT = dict(zip(SIZES, [15.60, 15.60, 15.60, 15.60, 17.60, 19.60]))   # front included
BACK_FEE = 5.95
AREA = {'area_width': 1800, 'area_height': 2400, 'width': 1800, 'height': 2400, 'top': 0, 'left': 0}


def price(d, z):
    p = D['price']['custom' if d['names'] else 'stock']
    return float(p[0] if z in ('S', 'M', 'L', 'XL') else p[1])


def plan(route='dtg', all_designs=False):
    out = []
    for d in D['designs']:
        stock = d['names'] == 0
        if not stock and not all_designs: continue
        files = [{'type': 'front', 'url': f'{CDN}AC-{d["code"]}_front.png', 'position': AREA},
                 {'type': 'back', 'url': f'{CDN}AC-{d["code"]}_back.png', 'position': AREA}] if stock else []
        variants = [dict(sku=f'DS-AC{d["code"]}-TD-{z}', size=z, variant_id=PF[d['colour']][z],
                         cost=round(GARMENT[z] + BACK_FEE, 2), price=price(d, z),
                         margin=round(price(d, z) - GARMENT[z] - BACK_FEE, 2)) for z in SIZES]
        out.append(dict(code=d['code'], slug=d['slug'], name=d['name'], colour=D['colours'][d['colour']]['name'],
                        fulfilment='auto' if stock else 'manual (personalized)', files=files, variants=variants))
    return out


if __name__ == '__main__':
    prods = plan(all_designs=True)
    print(f'{"Code":5s} {"Design":20s} {"Colour":10s} {"Fulfil":22s} {"PF S…3XL":42s} {"cost":>11s} {"price":>7s} {"margin":>11s}')
    for p in prods:
        v = p['variants']
        print(f'{p["code"]:5s} {p["name"]:20s} {p["colour"]:10s} {p["fulfilment"]:22s} {",".join(str(x["variant_id"]) for x in v):42s} '
              f'{v[0]["cost"]:5.2f}–{v[-1]["cost"]:5.2f} {v[0]["price"]:3.0f}–{v[-1]["price"]:3.0f} {v[-1]["margin"]:5.2f}–{v[0]["margin"]:5.2f}')
    auto = [p for p in prods if p['files']]
    print(f'\n{len(prods)} designs · {len(auto)} auto-linked ({len(auto) * 6} variants) · {len(prods) - len(auto)} personalized, ordered by hand')
    if '--json' in sys.argv: json.dump(prods, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1, ensure_ascii=False); print('plan written')
