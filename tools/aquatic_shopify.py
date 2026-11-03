#!/usr/bin/env python3
"""Shopify inputs for the Aquatic Comic series: 59 dark tees, Draft, in the Off-World product format.

Writes <out>/products.json (ProductSetInput list) and <out>/batches/NN.json — each {"query", "variables"} with up to
ten aliased productSet calls for the Admin GraphQL API. Image URLs are the live site's hashed URLs (push the site and
check the deploy first; Shopify copies the files at import).

The 39 personalized tees carry templateSuffix "personalized" (templates/product.personalized.json in the
"Horizon — Doolittle Scuba" theme, whose blocks/aquatic-personalize.liquid shows the name fields) and a
personalize:1 / personalize:buddy / personalize:couple tag that picks the fields.

Usage: tools/aquatic_shopify.py <out dir>
"""
import os, sys, json, hashlib, html as H

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(f'{SITE}/tools/aquatic_designs.json', encoding='utf-8'))
BASE = 'https://doolittlescuba.com/'
SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
SUBS = {v['key']: v for v in D['subsets'].values()}
SLOT = {'N': '[name]', 'A': '[diver 1]', 'B': '[diver 2]', 'H': '[husband]', 'W': '[wife]'}
MODE = {'self-logged': '1', 'buddy-check': '1', 'buddy-system': 'buddy', 'till-surface': 'couple', 'master-class': 'couple'}


def url(rel):
    h = hashlib.sha1(open(f'{SITE}/{rel}', 'rb').read()).hexdigest()[:8]
    return f'{BASE}{rel}?v={h}'


def words(t, slots=True):
    t = t.replace('*', '')
    for k, v in (SLOT if slots else D['sample']).items(): t = t.replace('{' + k + '}', v)
    return ' '.join(t.split('\n'))


def red(t):
    out, on, cur, parts = [], False, '', []
    for ch in t:
        if ch == '*':
            if on: parts.append(cur)
            cur = ''; on = not on
        elif on: cur += ch
    return parts


def handle_of(d):
    return f'aquatic-comic-{d["subset"]}-{d["slug"].split("-", 2)[2]}-tee'


def title_of(d):
    return f'Aquatic Comic · {SUBS[d["subset"]]["name"]} — {d["name"]} tee'


def product(d):
    sub = SUBS[d['subset']]; col = D['colours'][d['colour']]; low = col['name'].lower(); custom = d['names'] > 0
    punch = ', '.join(dict.fromkeys(red(d['front']) + red(d['back'])))
    for k, v in SLOT.items(): punch = punch.replace('{' + k + '}', v)
    price = D['price']['custom' if custom else 'stock']
    desc = (f'<p><strong>Aquatic Comic · {H.escape(sub["name"])}</strong> — {H.escape(sub["blurb"])}</p>'
            f'<p>On the left chest, under the DS mark: <em>&ldquo;{H.escape(words(d["front"]))}&rdquo;</em><br>'
            f'On the back: <em>&ldquo;{H.escape(words(d["back"]))}&rdquo;</em></p>')
    if custom:
        n = 'name' if d['names'] == 1 else 'two names'
        desc += (f'<p><strong>Personalized:</strong> type the {n} on this page and we print {"it" if d["names"] == 1 else "them"} into the joke, front and back, exactly as typed '
                 f'(up to {"12 characters" if d["names"] == 1 else "10 characters each"}). The pictures show sample names.'
                 + (' Made as a matching pair: add one shirt for each of you, with the same two names.' if d['names'] == 2 else '') + '</p>')
    desc += ('<ul>\n'
             f'<li>\n<strong>Front:</strong> the DS mark over the slogan, left chest, 3.75 in wide.</li>\n'
             f'<li>\n<strong>Back:</strong> the joke, 11 in wide, white with {H.escape(punch)} in red.</li>\n'
             f'<li>\n<strong>Shirt:</strong> Comfort Colors 1717, garment-dyed, {low}. Water-based white and red ink, printed to order.</li>\n</ul>'
             '<p>Shown on a mockup, not a photograph; the design preview is watermarked.</p>')
    s = d['slug']; t = title_of(d)
    files = [{'originalSource': url(f'img/aquatic/{s}-back.webp'), 'contentType': 'IMAGE',
              'alt': f'{t[:-4]} in {low}, back: {words(d["back"], False)}'[:500]},
             {'originalSource': url(f'img/aquatic/{s}-front.webp'), 'contentType': 'IMAGE',
              'alt': f'{t[:-4]} in {low}, front: the DS mark over “{words(d["front"], False)}” on the left chest'[:500]},
             {'originalSource': url(f'img/designs/{s}.webp'), 'contentType': 'IMAGE', 'alt': f'{d["name"]}, chest lockup and back print: watermarked preview'}]
    tags = ['aquatic-comic', f'ac:{d["subset"]}', f'colour:{d["colour"]}', 'coming-soon', 'tee', 'dark-line']
    if custom: tags += ['personalized', f'personalize:{MODE[d["subset"]]}']
    p = {'title': t, 'handle': handle_of(d), 'descriptionHtml': desc, 'vendor': 'Doolittle Scuba', 'productType': 'T-shirt', 'status': 'DRAFT',
         'tags': sorted(tags), 'files': files,
         'productOptions': [{'name': 'Size', 'position': 1, 'values': [{'name': z} for z in SIZES]}],
         'variants': [{'optionValues': [{'optionName': 'Size', 'name': z}], 'price': price[0] if z in ('S', 'M', 'L', 'XL') else price[1],
                       'sku': f'DS-AC{d["code"]}-TD-{z}'} for z in SIZES]}
    if custom: p['templateSuffix'] = 'personalized'
    return p


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(f'{out}/batches', exist_ok=True)
    prods = [product(d) for d in D['designs']]
    json.dump(prods, open(f'{out}/products.json', 'w'), indent=1, ensure_ascii=False)
    for b in range(0, len(prods), 10):
        chunk = prods[b:b + 10]
        q = 'mutation(' + ', '.join(f'$p{i}: ProductSetInput!' for i in range(len(chunk))) + ') {\n' + '\n'.join(
            f'  r{i}: productSet(input: $p{i}, synchronous: true) {{ product {{ id handle variants(first: 1) {{ nodes {{ id sku }} }} }} userErrors {{ field message }} }}' for i in range(len(chunk))) + '\n}'
        json.dump({'query': q, 'variables': {f'p{i}': p for i, p in enumerate(chunk)}}, open(f'{out}/batches/{b // 10:02d}.json', 'w'), ensure_ascii=False)
    print(len(prods), 'products in', (len(prods) + 9) // 10, 'batches')
