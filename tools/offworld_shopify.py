#!/usr/bin/env python3
"""Shopify inputs for the Off-World Hunt Club: 30 light + 30 dark tees in the Certified-ish product format.

Writes <out>/products.json — a list of ProductSetInput objects (productSet mutation) — and <out>/batches/NN.json,
each a {"query":..., "variables":...} with ten aliased productSet calls, ready for the Admin GraphQL API.
Image URLs are the live site's hashed URLs (run tools/bust.py and push first; Shopify copies the files at import).

Usage: tools/offworld_shopify.py <out dir> <collection gid>
"""
import os, sys, json, hashlib, html as H

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(f'{SITE}/tools/offworld_designs.json'))
BASE = 'https://doolittlescuba.com/'
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
PRICE = {'S': '42.00', 'M': '42.00', 'L': '42.00', 'XL': '42.00', '2XL': '45.00', '3XL': '45.00'}
CUSTOM = 'https://doolittlescuba.com/custom/#colour={c}&amp;tab=offworld&amp;back={s}&amp;bsize=full&amp;chest=dsmark&amp;cpos=left&amp;sleeve=none'


def url(rel):
    h = hashlib.sha1(open(f'{SITE}/{rel}', 'rb').read()).hexdigest()[:8]
    return f'{BASE}{rel}?v={h}'


def article(name):
    return 'an' if name[0].lower() in 'aeiou' else 'a'


def product(d, line, collection):
    s, n, t, punch = d['slug'], d['name'], d['text'], d['punch']
    col = D['colours'][line][d[line]]; cn = col['name']; low = cn.lower(); dark = line == 'dark'
    ink = 'white and red' if dark else 'black and red'
    title = f'Off-World Hunt Club{" Dark" if dark else ""} — {n} tee'
    handle = f'off-world-hunt-club{"-dark" if dark else ""}-{s[3:]}-tee'
    desc = ''
    if dark:
        desc += f'<p><strong>Dark line</strong> — the same design in white and red ink on {cn} Comfort Colors 1717.</p>'
    desc += (f'<p><strong>Off-World Hunt Club — {H.escape(n)}</strong></p>'
             f'<p>From the Off-World Hunt Club: thirty lines in a hunters&rsquo; script from somewhere else, each translated underneath with one word in red. '
             f'This one reads <em>{H.escape(t).replace('&#x27;', '&rsquo;')}</em> Full back on {article(low)} {low} tee; the DS mark with the word in glyphs on the chest.</p>'
             f'<ul>\n<li>\n<strong>Back:</strong> the line in the off-world script, 12 × 16 in, with its translation beneath and {punch} in red.</li>\n'
             f'<li>\n<strong>Chest:</strong> the DS mark with {punch} in glyphs, left chest, 3.5 in.</li>\n'
             f'<li>\n<strong>Shirt:</strong> Comfort Colors 1717, garment-dyed, {low}. Water-based {ink} ink, printed by hand in Newnan, Georgia.</li>\n</ul>'
             f'<p>Shown on a mockup, not a photograph; the design preview is watermarked. <a href="{CUSTOM.format(c=d[line], s=s)}">Make it yours</a>: another colour, your own line.</p>')
    folder = 'img/offworld/dark' if dark else 'img/offworld'
    files = [{'originalSource': url(f'{folder}/{s}-back.webp'), 'contentType': 'IMAGE', 'alt': f'{title[:-4]} in {low}, back: the line in the off-world script, translated, {punch.lower()} in red'},
             {'originalSource': url(f'{folder}/{s}-front.webp'), 'contentType': 'IMAGE', 'alt': f'{title[:-4]} in {low}, front: the DS mark with {punch.lower()} in glyphs on the chest'},
             {'originalSource': url(f'img/designs/{s}.webp'), 'contentType': 'IMAGE', 'alt': f'{n}, the full back print: watermarked preview'}]
    code = f'OW{d["n"]:02d}'
    tags = [f'ow:{s}', 'off-world-hunt-club', f'colour:{d[line]}', 'coming-soon', 'tee'] + (['off-world-hunt-club-dark', 'dark-line'] if dark else [])
    return {'title': title, 'handle': handle, 'descriptionHtml': desc, 'vendor': 'Doolittle Scuba', 'productType': 'T-shirt', 'status': 'DRAFT',
            'tags': sorted(tags), 'collections': [collection], 'files': files,
            'productOptions': [{'name': 'Size', 'position': 1, 'values': [{'name': z} for z in SIZES]}],
            'variants': [{'optionValues': [{'optionName': 'Size', 'name': z}], 'price': PRICE[z], 'sku': f'DS-{code}-{"TD" if dark else "T"}-{z}'} for z in SIZES]}


if __name__ == '__main__':
    out, coll = sys.argv[1], sys.argv[2]; os.makedirs(f'{out}/batches', exist_ok=True)
    prods = [product(d, line, coll) for line in ('light', 'dark') for d in D['designs']]
    json.dump(prods, open(f'{out}/products.json', 'w'), indent=1, ensure_ascii=False)
    for b in range(0, len(prods), 10):
        chunk = prods[b:b + 10]
        q = 'mutation(' + ', '.join(f'$p{i}: ProductSetInput!' for i in range(len(chunk))) + ') {\n' + '\n'.join(
            f'  r{i}: productSet(input: $p{i}, synchronous: true) {{ product {{ id handle }} userErrors {{ field message }} }}' for i in range(len(chunk))) + '\n}'
        json.dump({'query': q, 'variables': {f'p{i}': p for i, p in enumerate(chunk)}}, open(f'{out}/batches/{b // 10:02d}.json', 'w'), ensure_ascii=False)
    print(len(prods), 'products in', (len(prods) + 9) // 10, 'batches')
