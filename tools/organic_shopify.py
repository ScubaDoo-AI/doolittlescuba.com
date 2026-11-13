#!/usr/bin/env python3
"""Shopify inputs for the organic editions (tools/organic.py), as productSet batches. The store write itself goes through the
Shopify connector (productSet, ten per call), like the other lines.

  tools/organic_shopify.py <regular.json> <out_dir>
      regular.json: the regular products, one object per product key (DS-THI-T, DS-BAL-CD, DS-MRK-BN, ...):
                    {"key": {"id", "handle", "title", "tags": [...], "descriptionHtml", "productType"}}
                    (a Shopify query by SKU prefix; see QUERY below)
      out_dir/batch-NN.json   productSet inputs, ten per file
      out_dir/collection.json the "The organic line" smart collection (tag organic-line)

Every organic product: own product (Eric: keep eco separate), DRAFT, handle <regular handle>-organic, title "<Name> — organic tee"
(cap / beanie), vendor Doolittle Scuba, the regular product's type and its non-colour tags plus `organic-line`, `eco`,
`organic:<series>`, `colour:<organic colour>`, `fulfil:printful-<blank>`. Same prices as the regular variants. Images: the
re-dyed mockups from the live site (img/organic/...), front then back. Descriptions: an organic paragraph, then the regular
description with the garment line rewritten. The 14 drafts "<Site>, organic tee" made on 12 Nov are the Signature light
editions: the push updates them in place (productSet by id) instead of adding duplicates.
"""
import os, re, sys, json, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import organic, organic_site as OS

ORIGIN = 'https://doolittlescuba.com'
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = json.load(open(f'{SITE}/img/organic/manifest.json'))
QUERY = '''query($q: String!) { products(first: 1, query: $q) { nodes { id handle title tags descriptionHtml productType } } }'''
BLANK_TXT = {'tee': 'a Stanley/Stella Creator 2.0, 100% organic ring-spun cotton, 180 g/m²',
             'cap': 'an Econscious EC7000 organic cotton baseball cap, one size, adjustable',
             'beanie': 'an Atlantis organic rib beanie, 100% organic cotton, one size'}
FULFIL = {'tee': 'fulfil:printful-sttu169', 'cap': 'fulfil:printful-ec7000', 'beanie': 'fulfil:printful-atlantis-449'}
NOUN = {'tee': 'tee', 'cap': 'cap', 'beanie': 'beanie'}


def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def build(regular):
    out = []
    for p in organic.plan():
        r = regular.get(p['regular_key'])
        if not r: print('no regular product for', p['key']); continue
        name = OS.title(p); kind = p['kind']; colour = p['colour']
        dark_tee = kind == 'tee' and p['group'] == 'dark'
        title = f'{name} — organic {"dark " if dark_tee and p["line"] in ("signature", "certifiedish", "offworld") else ""}{NOUN[kind]}'
        tags = [t for t in r['tags'] if not t.startswith(('colour:', 'fulfil:', 'flexfit-'))]
        tags += ['organic-line', 'eco', f'organic:{p["line"]}', FULFIL[kind]]
        tags += [f'colour:{slug(c)}' for c in (['Black', 'Oxford Navy'] if kind == 'beanie' else [colour])]
        body = re.sub(r'Comfort Colors 1717[^<.]*', 'Stanley/Stella Creator 2.0, 100% organic cotton', r['descriptionHtml'] or '')
        body = re.sub(r'Flexfit 6277[^<.]*', 'Econscious EC7000 organic cotton cap, one size', body)
        lead = (f'<p><strong>Organic edition.</strong> The same design as the regular {H.escape(r["title"])}, on {BLANK_TXT[kind]}'
                f'{", in " + H.escape(colour) if kind != "beanie" else ", in Black or Oxford Navy"}. Same art, same price; printed or embroidered to order.</p>')
        if kind == 'beanie':
            imgs = [f'{ORIGIN}/img/organic/beanie/beanie-the-mark-organic-black.webp', f'{ORIGIN}/img/organic/beanie/beanie-the-mark-organic-oxford-navy.webp']
            options = [{'name': 'Colour', 'values': [{'name': 'Black'}, {'name': 'Oxford Navy'}]}]
            variants = [{'optionValues': [{'optionName': 'Colour', 'name': v['colour']}], 'price': f'{v["price"]:.2f}', 'sku': v['sku'],
                         'inventoryPolicy': 'DENY'} for v in p['variants']]
        elif kind == 'cap':
            imgs = [ORIGIN + u for u in MAN[p['key']]['images']]
            options = [{'name': 'Size', 'values': [{'name': 'One size'}]}]
            variants = [{'optionValues': [{'optionName': 'Size', 'name': 'One size'}], 'price': f'{p["variants"][0]["price"]:.2f}',
                         'sku': p['variants'][0]['sku'], 'inventoryPolicy': 'DENY'}]
        else:
            imgs = [ORIGIN + u for u in MAN[p['key']]['images']]
            if p['line'] in ('certifiedish', 'offworld', 'aquatic'): imgs = imgs[::-1]   # these lines lead with the back
            options = [{'name': 'Size', 'values': [{'name': v['size']} for v in p['variants']]}]
            variants = [{'optionValues': [{'optionName': 'Size', 'name': v['size']}], 'price': f'{v["price"]:.2f}', 'sku': v['sku'],
                         'inventoryPolicy': 'DENY'} for v in p['variants']]
        alt = f'{name}, organic edition in {colour}: mockup'
        inp = {'title': title, 'handle': f'{r["handle"]}-organic', 'status': 'DRAFT', 'vendor': 'Doolittle Scuba',
               'productType': r['productType'], 'tags': sorted(set(tags)), 'descriptionHtml': lead + body,
               'productOptions': options, 'variants': variants,
               'files': [{'originalSource': u, 'contentType': 'IMAGE', 'alt': alt + (' · back' if i else '')} for i, u in enumerate(imgs)]}
        out.append(dict(key=p['key'], regular_id=r['id'], input=inp))
    return out


if __name__ == '__main__':
    reg = json.load(open(sys.argv[1])); od = sys.argv[2]; os.makedirs(od, exist_ok=True)
    P = build(reg)
    for i in range(0, len(P), 10):
        json.dump(P[i:i + 10], open(f'{od}/batch-{i // 10:02d}.json', 'w'), indent=1)
    json.dump({'title': 'The organic line', 'handle': 'organic',
               'descriptionHtml': '<p>Every Doolittle Scuba design again on organic cotton: the five tee series, the caps and the beanie. Same art, same price.</p>',
               'ruleSet': {'appliedDisjunctively': False, 'rules': [{'column': 'TAG', 'relation': 'EQUALS', 'condition': 'organic-line'}]}},
              open(f'{od}/collection.json', 'w'), indent=1)
    print(len(P), 'products in', (len(P) + 9) // 10, 'batches')
