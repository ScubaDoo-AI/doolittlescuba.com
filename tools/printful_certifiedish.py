#!/usr/bin/env python3
"""Printful plan for Certified-ish (40 tees: 20 designs, light + dark) on the Comfort Colors 1717 (product 586), DTG.

  front  the "Certified Diver ~ish" left-chest logo (tools/certifiedish_front.py): black + PMS 485 red on the light line,
         white + red on the dark, on the full 12 x 16 in area (one file per ink for all 20 designs).
  back   the 23 Oct married back (drawing + Facts / Side Effects / Fine Print), 3600 x 4800 = the full area, stroke p5 0.020 in.
         Built 3 Nov from Eric's 1-bit seps: CI-<code>_back_12x16in_{BLACK,WHITE}.png.
Garments follow the Shopify colour: tags (light: light-blue = Chambray, pink = Blossom, coral = Watermelon, lagoon-blue,
butter; dark: emerald, yam, espresso, violet, moss, grape). Every one is $15.60 at Printful as of Nov 2026.
  sleeve_right  the DS mark (navy + red on light, white + red on dark), 2.5 x 2.75 in. Brand rule (Eric, 3 Nov): a shirt with
         no DS mark or shark signature carries the DS mark on the right sleeve.
Cost: garment + back $5.95 + sleeve $2.49 (the front rides in the base price) = $24.04 S-XL · $26.04 2XL · $28.04 3XL, against $42 / $45.

  tools/printful_certifiedish.py
  PRINTFUL_TOKEN=... tools/printful_link.py --only certifiedish [--apply]
"""
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
GARMENT = dict(zip(SIZES, [15.60, 15.60, 15.60, 15.60, 17.60, 19.60])); BACK = 5.95 + 2.49   # back + right-sleeve DS mark
PRICE = dict(zip(SIZES, [42.0, 42.0, 42.0, 42.0, 45.0, 45.0]))
AREA = {'area_width': 1800, 'area_height': 2400, 'width': 1800, 'height': 2400, 'top': 0, 'left': 0}
DESIGNS = [  # code, name, light garment, dark garment (Printful names, from the Shopify colour: tags)
    ('OWD', 'Open Water Diver', 'Blossom', 'Moss'), ('AOW', 'Advanced Open Water Diver', 'Watermelon', 'Emerald'),
    ('ALT', 'Altitude Diver', 'Chambray', 'Yam'), ('BOA', 'Boat Diver', 'Chambray', 'Yam'), ('BUO', 'Buoyancy', 'Chambray', 'Yam'),
    ('CAV', 'Cave Diver', 'Lagoon Blue', 'Espresso'), ('DEE', 'Deep Diver', 'Lagoon Blue', 'Espresso'), ('DPV', 'DPV Diver', 'Butter', 'Violet'),
    ('DRI', 'Drift Diver', 'Chambray', 'Yam'), ('FSH', 'Fish ID', 'Chambray', 'Yam'), ('ICE', 'Ice Diver', 'Lagoon Blue', 'Espresso'),
    ('NGT', 'Night Diver', 'Lagoon Blue', 'Espresso'), ('NTX', 'Nitrox', 'Butter', 'Violet'), ('REB', 'Rebreather Diver', 'Butter', 'Grape'),
    ('SAR', 'Search and Recovery', 'Lagoon Blue', 'Espresso'), ('SRD', 'Self-Reliant Diver', 'Butter', 'Grape'),
    ('SID', 'Sidemount Diver', 'Butter', 'Grape'), ('SMB', 'Surface Marker Buoy', 'Butter', 'Violet'), ('TEC', 'Tech Diver', 'Butter', 'Grape'),
    ('UWP', 'Underwater Photographer', 'Chambray', 'Yam')]
PF = {'Blossom': [16541, 16542, 16543, 16544, 16545, 16546], 'Watermelon': [15191, 15192, 15193, 15194, 15195, 16334],
      'Chambray': [17648, 17649, 17650, 17651, 17652, 17653], 'Lagoon Blue': [17679, 17681, 17680, 17682, 17683, 17684],
      'Butter': [15166, 15167, 15168, 15169, 15170, 16328], 'Moss': [17700, 17701, 17703, 17702, 17704, 17705],
      'Emerald': [52258, 52261, 52264, 52267, 52270, 52273], 'Yam': [21271, 21272, 21273, 21274, 21275, 21276],
      'Espresso': [21243, 21244, 21245, 21246, 21247, 21248], 'Violet': [15186, 15187, 15188, 15189, 15190, 16333],
      'Grape': [22096, 22097, 22098, 22099, 22100, 22101]}


def plan(route='dtg'):
    out = []
    for code, name, light, dark in DESIGNS:
        for line, colour, ink, sfx in (('light', light, 'BLACK', 'T'), ('dark', dark, 'WHITE', 'TD')):
            files = [{'type': 'front', 'url': f'{CDN}CI-front-leftchest_Certified-ish_12x16in_{ink}.png', 'position': AREA},
                     {'type': 'back', 'url': f'{CDN}CI-{code}_back_12x16in_{ink}.png', 'position': AREA},
                     {'type': 'sleeve_right', 'url': f'{CDN}DS_mark_PF-sleeve-right_3.5x4in_{"NAVYRED" if line == "light" else "WHITERED"}.png'}]
            variants = [dict(sku=f'DS-{code}-{sfx}-{z}', size=z, variant_id=PF[colour][i], cost=round(GARMENT[z] + BACK, 2), price=PRICE[z],
                             margin=round(PRICE[z] - GARMENT[z] - BACK, 2)) for i, z in enumerate(SIZES)]
            out.append(dict(code=code, name=name, line=line, colour=colour, files=files, variants=variants))
    return out


if __name__ == '__main__':
    P = plan()
    for p in P:
        v = p['variants']
        print(f"{p['code']} {p['name']:26s} {p['line']:5s} {p['colour']:11s} {','.join(map(str, (x['variant_id'] for x in v)))}  "
              f"cost {v[0]['cost']:.2f}-{v[-1]['cost']:.2f} margin {v[-1]['margin']:.2f}-{v[0]['margin']:.2f}")
    print(f"\n{len(P)} products · {sum(len(p['variants']) for p in P)} variants · front + back + right sleeve")
