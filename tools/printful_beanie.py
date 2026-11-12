#!/usr/bin/env python3
"""Printful plan for the embroidered beanie: "The Mark — Beanie" on the Stanley/Stella STAU295 Rib Knit Beanie 2.0 (product 1709).

One placement, embroidery_front (the folded cuff), included in the $14.25 base: the heavy DS mark at the line spec 1.50 x 1.64 in,
weight-passed to Printful's 0.05 in floor (p5 1.35 mm), white D + red S — the same art as the jacket chest mark and the cap.
Threads 1801 White #FFFFFF, 1839 Red #CC3333, flat. Colours Black (53657) and French Navy (53658), one size, catalog API 12 Nov 2026.
If Printful's cuff template is under 1.64 in tall it scales the file down on placement; check the first sync's mockup.

  tools/printful_beanie.py                                  # table
  PRINTFUL_TOKEN=... tools/printful_link.py --only beanie [--apply]
"""
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
FRONT = 'DS_mark_HEAVY_PF-beanie-front_1.50x1.64in_white-red.png'   # Shopify Files MediaImage 47401168470202
WHITE, RED = '#FFFFFF', '#CC3333'
BLANK = 14.25
# sku, colour, Printful variant, Shopify variant (product 10429487022266), price
VARIANTS = [('DS-MRK-BN-BLK', 'Black', 53657, 51012569202874, 35.0),
            ('DS-MRK-BN-FNV', 'French Navy', 53658, 51012569235642, 35.0)]


def plan():
    files = [{'type': 'embroidery_front', 'url': CDN + FRONT}]
    options = [{'id': 'embroidery_type', 'value': 'flat'}, {'id': 'thread_colors', 'value': [WHITE, RED]}]
    variants = [dict(sku=s, colour=c, variant_id=v, shopify_variant=sv, cost=BLANK, price=p, margin=round(p - BLANK, 2)) for s, c, v, sv, p in VARIANTS]
    return [dict(code='MRK-BN', handle='the-mark-beanie', files=files, options=options, variants=variants)]


if __name__ == '__main__':
    for p in plan():
        for v in p['variants']:
            print(f"{v['sku']:15s} {v['colour']:12s} PF {v['variant_id']}  Shopify {v['shopify_variant']}  cost {v['cost']:.2f}  price {v['price']:.0f}  margin {v['margin']:.2f}")
