#!/usr/bin/env python3
"""Printful plan for the embroidered caps: 18 of the 19 Dark caps on the Flexfit 6277 (product 140), flat embroidery.

Printful stocks the 6277 in Black, Dark Navy, Dark Grey, Olive, Royal Blue (plus Grey, Khaki, Red, White, Multicam). Since 12 Nov
every site cap is on one of those: the six that were going to the outside embroiderer moved to the nearest dark colour Printful
carries — Blue Grotto Royal Blue, Bridge Span 14 / Somosomo Strait / Vuna Reef Olive, Rainbow River Black, The Thistlegorm Dark
Grey (Eric: "correct this to be Printful stocked colors"). Home Port is custom-order (the buyer's own coordinates) and is not linked.

Three placements, sized to the 6277's actual Printful templates (printfiles API, 11 Nov: front 5.90 x 2.00 in; left, right and
back 2.00 x 1.00 in at 300 dpi). Files in Shopify Files, built by the Project's printful_caps_files.py from the embroiderer pack:
  embroidery_front  the site front (flag + name + coordinates, coordinates at 0.32 in caps so the oldstyle figures clear the
                    0.25 in text floor; <= 2.00 in tall) or the brand front (The Mark, Seal and Stack scaled to 2.00 in tall)
  embroidery_left   the heavy DS mark fitted to the 2 x 1 in side template: 0.92 x 1.00 in — below the 1.50 in line spec and
                    the 0.05 in line floor on the eye ring (p5 0.88 mm after the weight pass); sample one cap first
  embroidery_back   "DO A LITTLE" (0.25 in caps) over "SCUBA" (0.30 in), straight, 2.00 x 0.67 in — the 2 x 1 in back cannot
                    take the 4.00 in "DO - A - LITTLE" arc at the text floor, so the dashes and the arc are dropped here only
Every file is weight-passed to Printful's 0.05 in line floor and recoloured to its thread palette: 1801 White #FFFFFF,
1839 Red #CC3333 (the mark's S and the diver-down flag), 1842 Royal #005397 (the Alpha flag).
The Mark has no side mark; The Stack has no side and no back.

Cost: blank $16.51 with the first placement; each extra placement +$2.95 → site caps and The Seal / The Wordmark $22.41,
The Mark $19.46, The Stack $16.51, against $35 (site caps) / $40 (brand caps) in the store.

  tools/printful_caps.py                         # table
  PRINTFUL_TOKEN=... tools/printful_link.py --only caps [--apply]
  (the six recoloured caps: the link workflow with lines=caps, sku=DS-BGR,DS-BSP,DS-RRV,DS-SOM,DS-THI,DS-VUN)
"""
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
BLANK, EXTRA = 16.51, 2.95
PF = {'Black': (5276, 5277), 'Dark Navy': (5278, 5279), 'Dark Grey': (5280, 5281), 'Olive': (15901, 15902), 'Royal Blue': (5286, 5287)}   # (S/M, L/XL), catalog API 12 Nov
WHITE, RED, ROYAL = '#FFFFFF', '#CC3333', '#005397'
SIDE_FILE = 'DS_mark_HEAVY_PF-cap-left_FIT_0.92x1.00in_white-red.png'
BACK_FILE = 'DS_tagline_PF-cap-back_DO-A-LITTLE-over-SCUBA_2.00x0.67in_white.png'
# code, handle, Printful colour, front file, front threads, side?, back?, price
CAPS = [
    ('BAL', 'bali-dark-cap', 'Dark Navy', 'DS-BAL_Bali_PF-cap-front_2.46x1.88in_white-blue.png', [WHITE, ROYAL], True, True, 35),
    ('DAM', 'dampier-strait-dark-cap', 'Dark Navy', 'DS-DAM_Dampier_Strait_PF-cap-front_3.57x1.99in_white-blue.png', [WHITE, ROYAL], True, True, 35),
    ('NAV', 'navy-llcat-dark-cap', 'Dark Navy', 'DS-NAV_Navy_LLCAT_PF-cap-front_2.81x1.96in_white-red.png', [WHITE, RED], True, True, 35),
    ('THD', 'thurmond-dam-dark-cap', 'Dark Navy', 'DS-THD_Thurmond_Dam_PF-cap-front_3.78x1.89in_white-red.png', [WHITE, RED], True, True, 35),
    ('BBT', 'black-bart-dark-cap', 'Dark Grey', 'DS-BBT_Black_Bart_PF-cap-front_2.83x1.88in_white-red.png', [WHITE, RED], True, True, 35),
    ('DLP', 'dive-land-park-dark-cap', 'Dark Grey', 'DS-DLP_Dive_Land_Park_PF-cap-front_3.61x1.88in_white-red.png', [WHITE, RED], True, True, 35),
    ('BWP', 'blue-water-park-dark-cap', 'Black', 'DS-BWP_Blue_Water_Park_PF-cap-front_3.95x1.88in_white-red.png', [WHITE, RED], True, True, 35),
    ('RRF', 'rainbow-reef-dark-cap', 'Olive', 'DS-RRF_Rainbow_Reef_PF-cap-front_3.33x1.99in_white-blue.png', [WHITE, ROYAL], True, True, 35),
    ('BGR', 'blue-grotto-dark-cap', 'Royal Blue', 'DS-BGR_Blue_Grotto_PF-cap-front_2.68x1.88in_white-red.png', [WHITE, RED], True, True, 35),
    ('BSP', 'bridge-span-14-dark-cap', 'Olive', 'DS-BSP_Bridge_Span_14_PF-cap-front_3.44x1.99in_white-red.png', [WHITE, RED], True, True, 35),
    ('RRV', 'rainbow-river-dark-cap', 'Black', 'DS-RRV_Rainbow_River_PF-cap-front_3.57x1.89in_white-red.png', [WHITE, RED], True, True, 35),
    ('SOM', 'somosomo-strait-dark-cap', 'Olive', 'DS-SOM_Somosomo_Strait_PF-cap-front_4.02x1.89in_white-blue.png', [WHITE, ROYAL], True, True, 35),
    ('THI', 'the-thistlegorm-dark-cap', 'Dark Grey', 'DS-THI_Thistlegorm_PF-cap-front_3.93x2.00in_white-blue.png', [WHITE, ROYAL], True, True, 35),
    ('VUN', 'vuna-reef-dark-cap', 'Olive', 'DS-VUN_Vuna_Reef_PF-cap-front_2.46x1.97in_white-blue.png', [WHITE, ROYAL], True, True, 35),
    ('MRK', 'the-mark-dark-cap', 'Black', 'DS_PF-cap-front_the-mark_2.00in-tall_white-red.png', [WHITE, RED], False, True, 40),
    ('SEA', 'the-seal-dark-cap', 'Black', 'DS_PF-cap-front_the-seal_A2-bezel-star_2.00in-tall_white-red.png', [WHITE, RED], True, True, 40),
    ('STK', 'the-stack-dark-cap', 'Black', 'DS_PF-cap-front_the-stack_2.00in-tall_white-red.png', [WHITE, RED], False, False, 40),
    ('WDM', 'the-wordmark-dark-cap', 'Black', 'DS_PF-cap-front_the-wordmark_4.50x1.93in_white-red.png', [WHITE, RED], True, True, 40),
]
# Shopify variant ids (S/M, L/XL), from the store 11 Nov 2026 — the link also matches by SKU DS-<code>-CD-SM / -LXL
SHOPIFY = {'BAL': (50823900659898, 50823900692666), 'DAM': (50823901020346, 50823901053114), 'NAV': (50823901216954, 50823901249722),
           'THD': (50823909179578, 50823909212346), 'BBT': (50823900725434, 50823900758202), 'DLP': (50823901085882, 50823901118650),
           'BWP': (50823900856506, 50823900889274), 'RRF': (50823901282490, 50823901315258), 'MRK': (50823904460986, 50823904493754),
           'SEA': (50823904526522, 50823904559290), 'STK': (50823905771706, 50823905804474), 'WDM': (50823909114042, 50823909146810),
           'BGR': (50823900790970, 50823900823738), 'BSP': (50823900922042, 50823900954810), 'RRV': (50823904329914, 50823904362682),
           'SOM': (50823904395450, 50823904428218), 'THI': (50823909048506, 50823909081274), 'VUN': (50823909245114, 50823909277882)}


def plan():
    """files carry only type + url; the thread colours and the embroidery type are item-level options (Printful API, Common/Options)."""
    out = []
    for code, handle, colour, front, threads, side, back, price in CAPS:
        files = [{'type': 'embroidery_front', 'url': CDN + front}]
        options = [{'id': 'embroidery_type', 'value': 'flat'}, {'id': 'thread_colors', 'value': threads}]
        if side: files.append({'type': 'embroidery_left', 'url': CDN + SIDE_FILE}); options.append({'id': 'thread_colors_left', 'value': [WHITE, RED]})
        if back: files.append({'type': 'embroidery_back', 'url': CDN + BACK_FILE}); options.append({'id': 'thread_colors_back', 'value': [WHITE]})
        cost = round(BLANK + EXTRA*(len(files) - 1), 2)
        variants = [dict(sku=f'DS-{code}-CD-{z}', size=sz, variant_id=PF[colour][i], shopify_variant=SHOPIFY[code][i],
                         cost=cost, price=float(price), margin=round(price - cost, 2)) for i, (z, sz) in enumerate((('SM', 'S/M'), ('LXL', 'L/XL')))]
        out.append(dict(code=code, handle=handle, colour=colour, files=files, options=options, variants=variants))
    return out


if __name__ == '__main__':
    P = plan()
    for p in P:
        v = p['variants']; pl = '+'.join(f['type'].replace('embroidery_', '') for f in p['files'])
        print(f"{p['code']} {p['handle']:26s} {p['colour']:10s} {pl:16s} {v[0]['variant_id']}/{v[1]['variant_id']}  cost {v[0]['cost']:.2f}  price {v[0]['price']:.0f}  margin {v[0]['margin']:.2f}")
    print(f"\n{len(P)} products · {sum(len(p['variants']) for p in P)} variants · Flexfit 6277 (140), flat embroidery")
    print("not through Printful: Home Port (custom order)")
