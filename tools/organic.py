#!/usr/bin/env python3
"""The organic (eco) editions: every tee design, every cap and the beanie, on organic blanks, through the same pipeline.

Eric, 13 Nov 2026: "Create organic options for all the series as well as caps and beanies. Then add them into the system"
(the system = DoolittleScuba.com + Shopify + Printful). Standing rules: eco products are kept separate from the regular line
and pushed wherever possible (their own products, tag `organic-line`, their own collection); same price as the regular item
(13 Nov; a per-sale donation to ocean conservation or schools is being decided).

Blanks (Printful catalog API, 13 Nov 2026):
  tees   Stanley/Stella STTU169 Creator 2.0, 100% organic cotton (product 456), DTG — $13.95 S-XL, $15.25 2XL, $16.75 3XL,
         $1.65-$2.85 under the Comfort Colors 1717. Same placements (front, back +$5.95, sleeves +$2.49). Only eight colours run
         S-3XL; the line uses those: light (black ink) Cotton Pink, Desert Dust, White, Heather Grey; dark (white ink) Black,
         French Navy, Khaki (an olive, #6E6B4D), Stargazer (a deep teal). Each design takes the nearest by CIEDE2000 on Printful's
         swatch codes within its ink group (MAP below; Watermelon moved to Cotton Pink to keep its family).
  caps   Econscious EC7000 Organic Baseball Cap (product 491), $16.92 (+$0.41 on the 6277), embroidery, same placement keys.
         Dark only (the cap threads are white): Black, Charcoal, Pacific (navy), Jungle (olive). One size.
  beanie Atlantis Organic Ribbed Beanie, 100% organic (product 449), $17.94: Black, Oxford Navy. (The STAU295 beanie is 90% organic.)

Print files are the regular lines' files, unchanged — the organic colours keep each design's ink group.
SKUs: the regular product key + "O" (DS-THI-T-M -> DS-THI-TO-M, DS-THI-TD-M -> DS-THI-TDO-M, DS-BAL-CD-SM -> DS-BAL-CO,
DS-MRK-BN-BLK -> DS-MRK-BNO-BLK). Shopify variant ids are matched by SKU at link time.

  tools/organic.py                 # table + totals
  tools/organic.py --json out.json # the full plan (products, variants, files, options, prices) for the store build
  PRINTFUL_TOKEN=... tools/printful_link.py --only organic [--apply]
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
TEE = {  # STTU169 variant ids S..3XL, swatch hex, ink group
    'Cotton Pink': ([17412, 17413, 17414, 17415, 17416, 53666], '#FFE9EB', 'light'),
    'Desert Dust': ([12429, 12430, 12431, 12432, 12433, 17230], '#DCCCB4', 'light'),
    'White': ([11864, 11865, 11866, 11867, 11868, 17228], '#FFFFFF', 'light'),
    'Heather Grey': ([11884, 11885, 11886, 11887, 11888, 54614], '#CFCBC8', 'light'),
    'Black': ([11869, 11870, 11871, 11872, 11873, 17229], '#111111', 'dark'),
    'French Navy': ([11879, 11880, 11881, 11882, 11883, 17231], '#112537', 'dark'),
    'Khaki': ([17144, 17145, 17146, 17147, 17148, 53676], '#6E6B4D', 'dark'),
    'Stargazer': ([12439, 12440, 12441, 12442, 12443, 53672], '#3D737D', 'dark'),
}
TEE_COST = dict(zip(SIZES, [13.95, 13.95, 13.95, 13.95, 15.25, 16.75]))
CC_COST = dict(zip(SIZES, [15.60, 15.60, 15.60, 15.60, 17.60, 19.60]))
# Comfort Colors 1717 colour (Printful name) -> organic colour, by ink group (CIEDE2000 nearest, 13 Nov)
MAP = {
    'light': {'Bay': 'Heather Grey', 'Blossom': 'Cotton Pink', 'Butter': 'Desert Dust', 'Chalky Mint': 'White', 'Chambray': 'White',
              'Crunchberry': 'Cotton Pink', 'Flo Blue': 'Heather Grey', 'Granite': 'Heather Grey', 'Island Reef': 'White',
              'Ivory': 'Desert Dust', 'Lagoon Blue': 'Heather Grey', 'Orchid': 'Cotton Pink', 'Seafoam': 'Heather Grey',
              'Terracotta': 'Desert Dust', 'Watermelon': 'Cotton Pink'},
    'dark': {'Black': 'Black', 'Blue Spruce': 'Khaki', 'Denim': 'Stargazer', 'Emerald': 'Stargazer', 'Espresso': 'Khaki',
             'Grape': 'French Navy', 'Graphite': 'Black', 'Midnight': 'French Navy', 'Moss': 'Khaki', 'Navy': 'French Navy',
             'Pepper': 'Khaki', 'Sage': 'Khaki', 'True Navy': 'French Navy', 'Violet': 'Stargazer', 'Wine': 'Khaki', 'Yam': 'Khaki'},
}
CAP = {'Black': ('Black', 12689), 'Dark Navy': ('Pacific', 12693), 'Royal Blue': ('Pacific', 12693),
       'Dark Grey': ('Charcoal', 12690), 'Olive': ('Jungle', 12691)}
CAP_COST, CAP6277 = 16.92, 16.51
BEANIE = [('BLK', 'Black', 11706), ('NVY', 'Oxford Navy', 11708)]
BEANIE_COST = 17.94


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def cc_colours():
    """Comfort Colors 1717 variant id -> (Printful colour, size), from the catalog snapshot pf_586_variants.json (API, 13 Nov)."""
    d = json.load(open(os.path.join(HERE, 'pf_586_variants.json')))
    return {int(k): (c, z) for k, (c, z, _) in d.items()}


def okey(sku):
    """DS-THI-TD-M -> (DS-THI-TDO, M)"""
    k, z = sku.rsplit('-', 1); return k + 'O', z


def tee_plans():
    CC = cc_colours(); out = []
    lines = [('signature', 'printful_signature', {}), ('certifiedish', 'printful_certifiedish', {}), ('offworld', 'printful_offworld', {}),
             ('n73', 'printful_n73', {}), ('aquatic', 'printful_aquatic', {'all_designs': True})]
    for line, mod, kw in lines:
        for p in load(mod).plan('dtg', **kw):
            v0 = p['variants'][0]; colour = CC[v0['variant_id']][0]
            group = 'light' if colour in MAP['light'] else 'dark'
            oc = MAP[group][colour]; ids = dict(zip(SIZES, TEE[oc][0]))
            key = okey(v0['sku'])[0]
            extra = round(v0['cost'] - CC_COST['S'], 2) if 'cost' in v0 else None   # placements beyond the garment
            variants = []
            for v in p['variants']:
                z = okey(v['sku'])[1]
                cost = round(TEE_COST[z] + (extra or 0), 2) if extra is not None else None
                variants.append(dict(sku=f'{key}-{z}', size=z, variant_id=ids[z], regular_sku=v['sku'], price=v.get('price'),
                                     cost=cost, margin=round(v['price'] - cost, 2) if v.get('price') and cost is not None else None))
            out.append(dict(line=line, kind='tee', key=key, regular_key=v0['sku'].rsplit('-', 1)[0], regular_colour=colour, group=group,
                            colour=oc, hex=TEE[oc][1], files=p['files'], options=p.get('options'), personalized=not p['files'],
                            variants=variants))
    return out


def cap_plans():
    out = []
    for p in load('printful_caps').plan():
        colour, vid = CAP[p['colour']]; key = f"DS-{p['code']}-CO"
        v0 = p['variants'][0]; extra = round(v0['cost'] - CAP6277, 2); cost = round(CAP_COST + extra, 2)
        out.append(dict(line='caps', kind='cap', key=key, regular_key=f"DS-{p['code']}-CD", regular_colour=p['colour'], colour=colour,
                        files=p['files'], options=p['options'], personalized=False,
                        variants=[dict(sku=key, size='One size', variant_id=vid, regular_sku=v0['sku'], price=v0['price'], cost=cost,
                                       margin=round(v0['price'] - cost, 2))]))
    return out


def beanie_plans():
    b = load('printful_beanie').plan()[0]
    return [dict(line='beanie', kind='beanie', key='DS-MRK-BNO', regular_key='DS-MRK-BN', regular_colour='Black / French Navy',
                 colour='Black / Oxford Navy', files=b['files'], options=b['options'], personalized=False,
                 variants=[dict(sku=f'DS-MRK-BNO-{s}', size=c, colour=c, variant_id=v, price=35.0, cost=BEANIE_COST,
                                margin=round(35.0 - BEANIE_COST, 2)) for s, c, v in BEANIE])]


def plan():
    return tee_plans() + cap_plans() + beanie_plans()


if __name__ == '__main__':
    P = plan()
    if '--json' in sys.argv:
        json.dump(P, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
    from collections import Counter
    for p in P:
        v = p['variants'][0]
        print(f"{p['line']:12s} {p['key']:16s} {p['regular_colour']:18s} -> {p['colour']:16s} "
              f"{'personalized' if p['personalized'] else ''} cost {v['cost']} price {v['price']} margin {v['margin']}")
    print('\n', dict(Counter(p['line'] for p in P)), f"{len(P)} products · {sum(len(p['variants']) for p in P)} variants")
