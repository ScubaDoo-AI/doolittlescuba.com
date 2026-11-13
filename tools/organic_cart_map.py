#!/usr/bin/env python3
"""The colour-to-colour connections behind the cart's "Make it organic" converter.

Every regular product key is tied to its organic twin: the organic SKU key, the organic product's Shopify handle, and the
garment colour before and after (name + swatch hex), so the cart can show the buyer exactly how the colour changes.
The organic line has no pastels (Eric, 13 Nov): Cotton Pink is out of the palette, so every pink design lands on Heather Grey.

Size rule per entry:  s = keep the size suffix (tees)   1 = one size (caps: S/M and L/XL both go to the one-size EC7000)
                      b = beanie colour code (BLK -> BLK, FNV -> NVY)

  tools/organic_cart_map.py [out.json]     # default: shopify-theme/assets/ds-organic-map.json
Re-run after any change to tools/organic.py, then upload the asset to the theme (see SHOPIFY-STORE.md).
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import organic, organic_csv, organic_shopify as OSH, organic_mockups as OM

ROOT = os.path.dirname(HERE)
# the 14 Signature light organic drafts were created on 12 Nov with short handles; everything else gets the title handle
EXISTING_HANDLE = {
    'BBT': 'black-bart-organic-tee', 'BSP': 'bridge-span-14-organic-tee', 'BGR': 'blue-grotto-organic-tee',
    'BWP': 'blue-water-park-organic-tee', 'DAM': 'dampier-strait-organic-tee', 'BAL': 'bali-organic-tee',
    'RRV': 'rainbow-river-organic-tee', 'NAV': 'navy-llcat-organic-tee', 'DLP': 'dive-land-park-organic-tee',
    'THD': 'thurmond-dam-organic-tee', 'THI': 'the-thistlegorm-organic-tee', 'SOM': 'somosomo-strait-organic-tee',
    'RRF': 'rainbow-reef-organic-tee', 'VUN': 'vuna-reef-organic-tee'}
CAP_REG_HEX = {'Black': '#111111', 'Dark Navy': '#1F2A44', 'Royal Blue': '#2A4B9B', 'Dark Grey': '#4A4A4A', 'Olive': '#5B5A3A'}
BEANIE = {'BLK': ('Black', '#111111', 'BLK', 'Black', '#111111'), 'FNV': ('French Navy', '#112537', 'NVY', 'Oxford Navy', '#1B2333')}


def build():
    cc_hex = {c: h for c, z, h in json.load(open(os.path.join(HERE, 'pf_586_variants.json'))).values()}
    titles = {}
    for i in OSH.build():
        k = i['variants'][0]['sku']
        titles[k.rsplit('-', 1)[0] if k.count('-') == 3 else k] = i['title']
    out = {}
    for p in organic.plan():
        if p['kind'] == 'beanie':
            for code, (fn, fh, oc, tn, th) in BEANIE.items():
                out[f'DS-MRK-BN-{code}'] = [f'DS-MRK-BNO-{oc}', organic_csv.handle(titles.get('DS-MRK-BNO', 'The Mark — organic beanie')),
                                            fn, fh, tn, th, 'b']
            continue
        code = p['key'].split('-')[1]
        if p['kind'] == 'cap':
            title = titles.get(p['key']); fh = CAP_REG_HEX.get(p['regular_colour'], '#333333'); th = OM.CAP_HEX[p['colour']]
            out[p['regular_key']] = [p['key'], organic_csv.handle(title), p['regular_colour'], fh, p['colour'], th, '1']
            continue
        title = titles.get(p['key'])
        handle = EXISTING_HANDLE[code] if p['line'] == 'signature' and p['group'] == 'light' and code in EXISTING_HANDLE \
            else organic_csv.handle(title)
        out[p['regular_key']] = [p['key'], handle, p['regular_colour'], cc_hex.get(p['regular_colour'], '#888888'),
                                 p['colour'], p['hex'], 's']
    return out


if __name__ == '__main__':
    M = build()
    dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'shopify-theme', 'assets', 'ds-organic-map.json')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    json.dump({'v': 1, 'pastels': False, 'map': M}, open(dst, 'w'), ensure_ascii=False, separators=(',', ':'))
    from collections import Counter
    print(len(M), 'regular keys ->', dst, os.path.getsize(dst), 'bytes')
    print(Counter((v[2], v[4]) for v in M.values()).most_common(40))
