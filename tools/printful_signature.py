#!/usr/bin/env python3
"""Printful plan for the Signature Series (28 tees: 14 dive-site designs, light + dark) on the Comfort Colors 1717 (product 586), DTG.

Three placements, as the shirts were designed (Printful upload set, 25 Oct 2026; built by the Project's claude/printful_build.py):
  front         left-chest lockup (flag + site name + coordinates) pre-positioned on the full 12 x 16 in area (ink centre 9.5 in
                from the left edge, top 0.5 in). Black ink on the light line, white ink on the dark (flag colours kept).
  back          the dive-site plate + Facts / Species / Water, full 12 x 16 in area. OP-25 thickened set: strokes under the
                0.020 in floor grown to it (p5 0.0187-0.0200 in), chosen 3 Nov for garment-dyed DTG.
  sleeve_right  shark + signature logo, 3.5 x 4 in (one file per ink, the same on every shirt of the line).
Files live in Shopify Files: {CDN}DS-<code>_<site>_PF-{front-leftchest,back}_12x16in_{BLACK,WHITE}[_op25].png and
DS_shark-signature_PF-sleeve-right_3.5x4in_{BLACK,WHITE}.png (uploaded 3 Nov).

Garments follow the store and the site (Shopify colour: tags, img/shirts): every colour is $15.60 at Printful as of Nov 2026, so the
25 Oct price-driven swaps (Midnight / Emerald / Sage / Wine / Khaki) are not used. Light names are Printful's names for the
catalog colours (light blue = Chambray, mint = Island Reef, teal = Seafoam, sage = Bay, aqua = Chalky Mint, berry pink =
Crunchberry, coral = Watermelon, lavender = Orchid, pink = Blossom).
Cost: garment $15.60 / $17.60 / $19.60 + back $5.95 + sleeve $2.49 = $24.04 S-XL · $26.04 2XL · $28.04 3XL against $42 / $45.

  tools/printful_signature.py                         # table
  PRINTFUL_TOKEN=... tools/printful_link.py --only signature [--apply]
"""
import sys

CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
GARMENT = dict(zip(SIZES, [15.60, 15.60, 15.60, 15.60, 17.60, 19.60]))
BACK, SLEEVE = 5.95, 2.49
PRICE = dict(zip(SIZES, [42.0, 42.0, 42.0, 42.0, 45.0, 45.0]))
CHEST_V = {'NAV': '_v2'}   # 12 Nov 2026: the Navy LLCAT chest lockup re-titled "Navy LLCAT" (was "Hovercraft (LLCAT)"); new files so Printful fetches fresh
CHEST_POS = '_top2in'   # 13 Nov 2026: lockup moved from ink top 0.5 in to 2 in (sample proof: tight under the collar on an S); tools/chest_lower.py
AREA = {'area_width': 1800, 'area_height': 2400, 'width': 1800, 'height': 2400, 'top': 0, 'left': 0}
DESIGNS = [('THI', 'Thistlegorm', 'Crunchberry', 'Blue Spruce'), ('BBT', 'Black_Bart', 'Chambray', 'Pepper'), ('NAV', 'Navy_LLCAT', 'Granite', 'Navy'), ('BSP', 'Bridge_Span_14', 'Flo Blue', 'Espresso'), ('BGR', 'Blue_Grotto', 'Island Reef', 'Grape'), ('RRV', 'Rainbow_River', 'Bay', 'Wine'), ('BWP', 'Blue_Water_Park', 'Seafoam', 'Black'), ('DLP', 'Dive_Land_Park', 'Chalky Mint', 'Graphite'), ('THD', 'Thurmond_Dam', 'Ivory', 'Midnight'), ('RRF', 'Rainbow_Reef', 'Orchid', 'Sage'), ('SOM', 'Somosomo_Strait', 'Watermelon', 'Emerald'), ('VUN', 'Vuna_Reef', 'Blossom', 'Moss'), ('BAL', 'Bali', 'Terracotta', 'Denim'), ('DAM', 'Dampier_Strait', 'Butter', 'True Navy')]   # code, site file stem, light garment, dark garment (Printful names)
PF = {
    'Bay': [17707, 17708, 17709, 17710, 17711, 17712],
    'Black': [15114, 15115, 15116, 15117, 15118, 16326],
    'Blossom': [16541, 16542, 16543, 16544, 16545, 16546],
    'Blue Spruce': [17686, 17687, 17688, 17689, 17690, 17691],
    'Butter': [15166, 15167, 15168, 15169, 15170, 16328],
    'Chalky Mint': [21513, 21514, 21515, 21516, 21517, 21518],
    'Chambray': [17648, 17649, 17650, 17651, 17652, 17653],
    'Crunchberry': [21250, 21251, 21252, 21253, 21254, 21255],
    'Denim': [21520, 21521, 21522, 21523, 21524, 21525],
    'Emerald': [52258, 52261, 52264, 52267, 52270, 52273],
    'Espresso': [21243, 21244, 21245, 21246, 21247, 21248],
    'Flo Blue': [15171, 15172, 15173, 15174, 15175, 16329],
    'Granite': [17655, 17656, 17657, 17658, 17659, 17660],
    'Grape': [22096, 22097, 22098, 22099, 22100, 22101],
    'Graphite': [21264, 21265, 21266, 21267, 21268, 21269],
    'Island Reef': [21527, 21528, 21529, 21530, 21531, 21532],
    'Ivory': [16523, 16524, 16525, 16526, 16527, 16528],
    'Midnight': [21541, 21542, 21543, 21544, 21545, 21546],
    'Moss': [17700, 17701, 17703, 17702, 17704, 17705],
    'Navy': [21555, 21556, 21557, 21558, 21559, 21560],
    'Orchid': [21257, 21258, 21259, 21260, 21261, 21262],
    'Pepper': [17693, 17694, 17695, 17696, 17697, 17698],
    'Sage': [21562, 21563, 21564, 21565, 21566, 21567],
    'Seafoam': [16529, 16530, 16531, 16532, 16533, 16534],
    'Terracotta': [17662, 17663, 17664, 17665, 17666, 17667],
    'True Navy': [15181, 15182, 15183, 15184, 15185, 16332],
    'Watermelon': [15191, 15192, 15193, 15194, 15195, 16334],
    'Wine': [52281, 52285, 52289, 52293, 52297, 52301],
}


def plan(route='dtg'):
    out = []
    for code, site, light, dark in DESIGNS:
        for line, colour, ink, suffix in (('light', light, 'BLACK', 'T'), ('dark', dark, 'WHITE', 'TD')):
            files = [{'type': 'front', 'url': f'{CDN}DS-{code}_{site}_PF-front-leftchest_12x16in_{ink}{CHEST_V.get(code, "")}{CHEST_POS}.png', 'position': AREA},
                     {'type': 'back', 'url': f'{CDN}DS-{code}_{site}_PF-back_12x16in_{ink}_op25.png', 'position': AREA},
                     {'type': 'sleeve_right', 'url': f'{CDN}DS_shark-signature_PF-sleeve-right_3.5x4in_{ink}.png'}]
            variants = [dict(sku=f'DS-{code}-{suffix}-{z}', size=z, variant_id=PF[colour][i], cost=round(GARMENT[z] + BACK + SLEEVE, 2),
                             price=PRICE[z], margin=round(PRICE[z] - GARMENT[z] - BACK - SLEEVE, 2)) for i, z in enumerate(SIZES)]
            out.append(dict(code=code, site=site.replace('_', ' '), line=line, colour=colour, files=files, variants=variants))
    return out


if __name__ == '__main__':
    P = plan()
    for p in P:
        v = p['variants']
        print(f"{p['code']} {p['site']:16s} {p['line']:5s} {p['colour']:12s} {','.join(str(x['variant_id']) for x in v):42s} "
              f"cost {v[0]['cost']:.2f}-{v[-1]['cost']:.2f} margin {v[-1]['margin']:.2f}-{v[0]['margin']:.2f}")
    print(f"\n{len(P)} products · {sum(len(p['variants']) for p in P)} variants · front + back + right sleeve")
