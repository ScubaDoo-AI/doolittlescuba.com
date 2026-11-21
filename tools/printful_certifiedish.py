#!/usr/bin/env python3
"""Printful plan for Certified-ish (40 tees: 20 designs, light + dark) on the Comfort Colors 1717 (product 586), DTG.

  front  the "Certified Diver ~ish" left-chest logo (tools/certifiedish_front.py): black + PMS 485 red on the light line,
         white + red on the dark, on the full 12 x 16 in area (one file per ink for all 20 designs).
  back   the 23 Oct married back (drawing + Facts / Side Effects / Fine Print), 3600 x 4800 = the full area, stroke p5 0.020 in.
         Built 3 Nov from Eric's 1-bit seps: CI-<code>_back_12x16in_{BLACK,WHITE}.png.
Garments follow the Shopify colour: tags (light: light-blue = Chambray, pink = Blossom, coral = Watermelon, lagoon-blue,
butter; dark: emerald, violet, moss, grape, and since 21 Nov mystic blue, true navy, blue spruce, midnight, black,
graphite, denim, hemp in place of yam and espresso). Every one is $15.60 at Printful as of Nov 2026.
  sleeve_right  the DS mark (navy + red on light, white + red on dark), 1.00 in wide at the bottom of the area. Brand rule (Eric, 3 Nov): a shirt with
         no DS mark or shark signature carries the DS mark on the right sleeve.
Cost: garment + back $5.95 + sleeve $2.49 (the front rides in the base price) = $24.04 S-XL · $26.04 2XL · $28.04 3XL, against $42 / $45.

  tools/printful_certifiedish.py
  PRINTFUL_TOKEN=... tools/printful_link.py --only certifiedish [--apply]
"""
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
GARMENT = dict(zip(SIZES, [15.60, 15.60, 15.60, 15.60, 17.60, 19.60])); BACK = 5.95 + 2.49   # back + right-sleeve DS mark
PRICE = dict(zip(SIZES, [40.0, 40.0, 40.0, 40.0, 43.0, 43.0]))   # 15 Nov 2026 price table (Company): Certified-ish $40, 2XL-3XL +$3
AREA = {'area_width': 1800, 'area_height': 2400, 'width': 1800, 'height': 2400, 'top': 0, 'left': 0}
# Right-sleeve DS mark (fix of 17 Nov 2026, see SLEEVE-MARK-FIX). Printful's sleeve print file for the 1717 (586) and the
# STTU169 (456) is printfile 130: 600 x 525 px at 150 dpi = 4.00 in wide x 3.50 in tall, fill_mode fit. Sent without a
# position, the old 3.5 x 4 in file printed the mark about 2x and high on the arm (sample #sample-202611040806). The new
# file is the mark alone, 330 x 358 px at 300 dpi = 1.10 x 1.19 in (ink 1.00 x 1.09 in + 0.05 in pad). Position, in
# printfile pixels: width 165, height 179, centred (left 218), bottom edge on the area's bottom edge (top 346). The area's
# bottom edge sits about 0.9-1.0 in above the sleeve hem on both blanks (mockup templates 253304 / 324414), so this is the
# lowest Printful allows; the mark lands ~1 in above the hem, not the 1/2 in Eric asked for.
SLEEVE_POS = {'area_width': 600, 'area_height': 525, 'width': 165, 'height': 179, 'top': 346, 'left': 218}
SLEEVE_FILE = 'DS_mark_PF-sleeve-right_1.00in_{ink}.png'   # NAVYRED on light shirts, WHITERED on dark
DESIGNS = [  # code, name, light garment, dark garment (Printful names, from the Shopify colour: tags)
    ('OWD', 'Open Water Diver', 'Blossom', 'Moss'), ('AOW', 'Advanced Open Water Diver', 'Watermelon', 'Emerald'),
    ('ALT', 'Altitude Diver', 'Chambray', 'Mystic Blue'), ('BOA', 'Boat Diver', 'Chambray', 'True Navy'), ('BUO', 'Buoyancy', 'Chambray', 'Blue Spruce'),
    ('CAV', 'Cave Diver', 'Lagoon Blue', 'Graphite'), ('DEE', 'Deep Diver', 'Lagoon Blue', 'True Navy'), ('DPV', 'DPV Diver', 'Butter', 'Violet'),
    ('DRI', 'Drift Diver', 'Chambray', 'Midnight'), ('FSH', 'Fish ID', 'Chambray', 'Emerald'), ('ICE', 'Ice Diver', 'Lagoon Blue', 'Denim'),
    ('NGT', 'Night Diver', 'Lagoon Blue', 'Black'), ('NTX', 'Nitrox', 'Butter', 'Violet'), ('REB', 'Rebreather Diver', 'Butter', 'Grape'),
    ('SAR', 'Search and Recovery', 'Lagoon Blue', 'Hemp'), ('SRD', 'Self-Reliant Diver', 'Butter', 'Grape'),
    ('SID', 'Sidemount Diver', 'Butter', 'Grape'), ('SMB', 'Surface Marker Buoy', 'Butter', 'Violet'), ('TEC', 'Tech Diver', 'Butter', 'Grape'),
    ('UWP', 'Underwater Photographer', 'Chambray', 'Black')]
PF = {'Blossom': [16541, 16542, 16543, 16544, 16545, 16546], 'Watermelon': [15191, 15192, 15193, 15194, 15195, 16334],
      'Chambray': [17648, 17649, 17650, 17651, 17652, 17653], 'Lagoon Blue': [17679, 17681, 17680, 17682, 17683, 17684],
      'Butter': [15166, 15167, 15168, 15169, 15170, 16328], 'Moss': [17700, 17701, 17703, 17702, 17704, 17705],
      'Emerald': [52258, 52261, 52264, 52267, 52270, 52273], 'Yam': [21271, 21272, 21273, 21274, 21275, 21276],
      'Espresso': [21243, 21244, 21245, 21246, 21247, 21248], 'Violet': [15186, 15187, 15188, 15189, 15190, 16333],
      'Grape': [22096, 22097, 22098, 22099, 22100, 22101],
      # 21 Nov 2026: the Yam / Espresso dark tees recoloured (Eric: "not a fan of the orange and brown"), all US in stock
      'Mystic Blue': [22076, 22078, 22080, 22082, 22084, 22086], 'True Navy': [15181, 15182, 15183, 15184, 15185, 16332],
      'Blue Spruce': [17686, 17687, 17688, 17689, 17690, 17691], 'Midnight': [21541, 21542, 21543, 21544, 21545, 21546],
      'Black': [15114, 15115, 15116, 15117, 15118, 16326], 'Graphite': [21264, 21265, 21266, 21267, 21268, 21269],
      'Denim': [21520, 21521, 21522, 21523, 21524, 21525], 'Hemp': [22103, 22104, 22105, 22106, 22107, 22108]}


def plan(route='dtg'):
    out = []
    for code, name, light, dark in DESIGNS:
        for line, colour, ink, sfx in (('light', light, 'BLACK', 'T'), ('dark', dark, 'WHITE', 'TD')):
            # front: ink top 2 in (was 0.5 in) since 13 Nov 2026, tools/chest_lower.py
            files = [{'type': 'front', 'url': f'{CDN}CI-front-leftchest_Certified-ish_12x16in_{ink}_top2in.png', 'position': AREA},
                     {'type': 'back', 'url': f'{CDN}CI-{code}_back_12x16in_{ink}.png', 'position': AREA},
                     {'type': 'sleeve_right', 'url': CDN + SLEEVE_FILE.format(ink='NAVYRED' if line == 'light' else 'WHITERED'), 'position': SLEEVE_POS}]
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
