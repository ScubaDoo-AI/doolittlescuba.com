#!/usr/bin/env python3
"""Printful plan for the 37 three-sticker packs (DS-PK-*).

One pack = one Printful kiss-cut sticker sheet, 5.83 × 8.27 in (catalog product 505, variant 12917, $5.15 in
Nov 2026). The print masters are 1749 × 2481 px at 300 dpi — the sheet exactly — and live in Shopify Files as
`files/DS-PK-<xx>.png` (never in this repo). The pack list, names and contents come from tools/packs.json; the
Shopify variant ids below are what Printful's Shopify import carries as external_id, so tools/printful_link.py
can match a sync variant even when the SKU didn't come across.

  tools/printful_packs.py          # plan: SKU, name, sheet, cost vs. price, file URL
  tools/printful_link.py --only packs [--apply]   # attach the sheet + file to Printful's imported products

Retail is $10 a pack (packs.json "price") — a $4.85 margin on the sheet before Printful's shipping. Check the
sheet's size and price against Printful's current template before the first real order; the sample is the proof.
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
SHEET, SHEET_COST = 12917, 5.15          # Printful kiss-cut sticker sheet 5.83 × 8.27 in (product 505)

# Shopify product id, variant id — created 10 Nov 2026 (handle sticker-pack-<slug>, $10, Active, no channel)
SHOPIFY = {
    'DS-PK-T01': (10427044921530, 51000161108154), 'DS-PK-T02': (10427045019834, 51000161435834),
    'DS-PK-T03': (10427045118138, 51000162615482), 'DS-PK-T04': (10427045249210, 51000163008698),
    'DS-PK-T05': (10427045281978, 51000163139770), 'DS-PK-T06': (10427045380282, 51000163664058),
    'DS-PK-T07': (10427045413050, 51000163696826), 'DS-PK-T08': (10427045478586, 51000163860666),
    'DS-PK-T09': (10427045511354, 51000163893434), 'DS-PK-T10': (10427045576890, 51000164188346),
    'DS-PK-T11': (10427045937338, 51000173166778), 'DS-PK-T12': (10427045970106, 51000173199546),
    'DS-PK-T13': (10427046002874, 51000173232314), 'DS-PK-T14': (10427046035642, 51000173265082),
    'DS-PK-T15': (10427046068410, 51000173297850), 'DS-PK-T16': (10427046101178, 51000173330618),
    'DS-PK-T17': (10427046133946, 51000173363386), 'DS-PK-T18': (10427046166714, 51000173396154),
    'DS-PK-T19': (10427046199482, 51000173428922), 'DS-PK-T20': (10427046232250, 51000173461690),
    'DS-PK-T21': (10427046461626, 51000175853754), 'DS-PK-T22': (10427046494394, 51000175952058),
    'DS-PK-T23': (10427046527162, 51000175984826), 'DS-PK-T24': (10427046559930, 51000176017594),
    'DS-PK-T25': (10427046592698, 51000176050362), 'DS-PK-T26': (10427046625466, 51000176083130),
    'DS-PK-C01': (10427046658234, 51000176115898), 'DS-PK-C02': (10427046691002, 51000176148666),
    'DS-PK-C03': (10427046756538, 51000176214202), 'DS-PK-C04': (10427046789306, 51000176246970),
    'DS-PK-C05': (10427047280826, 51000187191482), 'DS-PK-B01': (10427047313594, 51000187224250),
    'DS-PK-B02': (10427047346362, 51000187257018), 'DS-PK-B03': (10427047379130, 51000187289786),
    'DS-PK-B04': (10427047444666, 51000187355322), 'DS-PK-B05': (10427047477434, 51000187388090),
    'DS-PK-B06': (10427047510202, 51000187420858),
}


def packs():
    with open(os.path.join(HERE, 'packs.json')) as f: return json.load(f)


def plan():
    d = packs(); price = float(d.get('price', 10))
    out = []
    for p in d['packs']:
        pid, vid = SHOPIFY.get(p['sku'], (None, None))
        out.append(dict(sku=p['sku'], title=p['name'] + ' — Sticker Pack', line=p['line'], stickers=p['stickers'],
                        shopify_product=pid, shopify_variant=vid, variant_id=SHEET, product='Kiss-cut sticker sheet 5.83×8.27 in',
                        cost=SHEET_COST, price=price, margin=round(price - SHEET_COST, 2), file=CDN + p['sku'] + '.png'))
    return out


if __name__ == '__main__':
    rows = plan()
    print(f'{"SKU":11s} {"pack":26s} {"line":8s} {"cost":>6s} {"price":>6s} {"margin":>7s}  shopify variant')
    for r in rows: print(f'{r["sku"]:11s} {r["title"][:-15]:26s} {r["line"]:8s} {r["cost"]:6.2f} {r["price"]:6.2f} {r["margin"]:7.2f}  {r["shopify_variant"]}')
    print(f'\n{len(rows)} packs on Printful sheet variant {SHEET} · one of each costs ${sum(r["cost"] for r in rows):.2f} · retail ${sum(r["price"] for r in rows):.2f}')
    missing = [r['sku'] for r in rows if not r['shopify_variant']]
    if missing: print('no Shopify variant recorded for:', ', '.join(missing))
