#!/usr/bin/env python3
"""Printful plan for The Side Mark cap (Eric, 21 Nov 2026): a plain Flexfit 6277 with only the DS mark on the left side,
in every colour Printful stocks, with an optional "Do A Little Scuba" back.

  "I would like to add a cap that is plain with just the DS mark on the side, make it custom to any color selectable
   and optional Do A Little Scuba tag line on the back."  Price: $32 plain, $36 with the back.

Colours, variant ids, stitch files and thread rules come from printful_caps.py (the 21 Nov recolour): white thread on the dark
caps, 1966 Navy on White / Khaki / Grey, and the side mark's S in navy on Red.

Shopify: one product, options Colour (10) x Size (S/M, L/XL) x Back (Plain, Do A Little Scuba) = 40 variants.
SKU DS-SDM-<COLOUR>-<SM|LXL> plain, DS-SDM-<COLOUR>-<SM|LXL>-B with the back.

  tools/printful_sidemark.py                      # table
  PRINTFUL_TOKEN=... tools/printful_link.py --only sidemark [--apply]
"""
import importlib.util, os

_spec = importlib.util.spec_from_file_location('pc', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'printful_caps.py'))
PC = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(PC)

HANDLE = 'the-side-mark-cap'
TITLE = 'The Side Mark — cap'
PRICE_PLAIN, PRICE_BACK = 32.0, 36.0
COLOURS = ['Black', 'Dark Navy', 'Dark Grey', 'Grey', 'White', 'Khaki', 'Olive', 'Multicam Green', 'Royal Blue', 'Red']
CODE = {c: c.upper().replace(' ', '') for c in COLOURS}          # BLACK, DARKNAVY, MULTICAMGREEN ...
SIZES = (('SM', 'S/M'), ('LXL', 'L/XL'))
BACKS = (('', 'Plain'), ('-B', 'Do A Little Scuba'))


def files_for(colour, back):
    side_url, side_thr = PC.CDN + PC.SIDE_FILE, [PC.WHITE, PC.RED]
    back_url, back_thr = PC.CDN + PC.BACK_FILE, [PC.WHITE]
    if colour in PC.LIGHT:
        side_url, side_thr, back_url, back_thr = PC.LIGHT_SIDE, [PC.NAVY, PC.RED], PC.LIGHT_BACK, [PC.NAVY]
    if colour == 'Red':
        side_url, side_thr = PC.RED_SIDE, [PC.WHITE, PC.NAVY]
    files = [{'type': 'embroidery_left', 'url': side_url}]
    options = [{'id': 'embroidery_type', 'value': 'flat'}, {'id': 'thread_colors_left', 'value': side_thr}]
    if back:
        files.append({'type': 'embroidery_back', 'url': back_url}); options.append({'id': 'thread_colors_back', 'value': back_thr})
    return files, options


def plan():
    """One entry per (colour, back) so each carries its own files; variants are the two sizes."""
    out = []
    for colour in COLOURS:
        for suffix, back_label in BACKS:
            back = bool(suffix)
            files, options = files_for(colour, back)
            cost = round(PC.BLANK + PC.EXTRA * (len(files) - 1), 2)
            price = PRICE_BACK if back else PRICE_PLAIN
            variants = [dict(sku=f'DS-SDM-{CODE[colour]}-{z}{suffix}', size=sz, colour=colour, back=back_label,
                             variant_id=PC.PF[colour][i], cost=cost, price=price, margin=round(price - cost, 2))
                        for i, (z, sz) in enumerate(SIZES)]
            out.append(dict(code='SDM', handle=HANDLE, colour=colour, back=back_label, files=files, options=options, variants=variants))
    return out


if __name__ == '__main__':
    P = plan()
    for p in P:
        v = p['variants']; pl = '+'.join(f['type'].replace('embroidery_', '') for f in p['files'])
        print(f"{v[0]['sku']:26s} {p['colour']:15s} {pl:10s} {v[0]['variant_id']}/{v[1]['variant_id']}  cost {v[0]['cost']:.2f}  price {v[0]['price']:.0f}  margin {v[0]['margin']:.2f}")
    print(f"\n{sum(len(p['variants']) for p in P)} variants · Flexfit 6277 (140), flat embroidery")
