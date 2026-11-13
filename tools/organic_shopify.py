#!/usr/bin/env python3
"""Shopify inputs for the organic editions (tools/organic.py): one productSet input per product, as JSONL for a bulk mutation.

  tools/organic_shopify.py <out.jsonl>     -> {"input": ProductSetInput} per line (242 lines) + <out>.collection.json

Every organic edition is its own product (Eric: keep eco separate), DRAFT, vendor Doolittle Scuba, titled like its regular
product with "organic" before the noun ("Black Bart — Signature Series organic tee", "Bali — organic cap", "The Mark — organic
beanie"). Shopify makes the handle from the title. Tags: the line's tags + organic-line, eco, organic:<series>, colour:<organic
colour>, fulfil:printful-<blank>, coming-soon. Same prices as the regular variants. Images: the re-dyed mockups on the live site
(img/organic/...). No charity or donation wording (Eric, 13 Nov: hold off on that claim).
The 14 "<Site>, organic tee" drafts made on 12 Nov (White / Black options, DS-<code>-TE-… SKUs) are rewritten in place as the
Signature Series light organic editions (productSet with their ids), so nothing is duplicated.
"""
import os, re, sys, json, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import organic, organic_site as OS, organic_mockups as OM

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGIN = 'https://doolittlescuba.com'


def vurl(u):
    """Site image URL with the content-hash query the site uses (Porkbun's CDN caches by URL for 30 days)."""
    import hashlib
    p = os.path.join(SITE_ROOT, u.replace(ORIGIN, '').lstrip('/'))
    return u + '?v=' + hashlib.sha1(open(p, 'rb').read()).hexdigest()[:8] if os.path.exists(p) else u
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = json.load(open(f'{SITE}/img/organic/manifest.json'))
AQD = json.load(open(f'{SITE}/tools/aquatic_designs.json'))
AQ_SUB = {v['key']: v for v in AQD['subsets'].values()}
PERS = {0: None, 1: 'personalize:1'}
EXISTING = {'BBT': 10429329801402, 'BSP': 10429348610234, 'BGR': 10429349396666, 'BWP': 10429349986490, 'DAM': 10429350576314,
            'BAL': 10429376856250, 'RRV': 10429377642682, 'NAV': 10429378298042, 'DLP': 10429378953402, 'THD': 10429379674298,
            'THI': 10429400875194, 'SOM': 10429401759930, 'RRF': 10429402513594, 'VUN': 10429403070650}   # 12 Nov drafts
BLANK = {'tee': 'a Stanley/Stella Creator 2.0 tee, 100% organic ring-spun cotton, 180 g/m²',
         'cap': 'an Econscious EC7000 baseball cap in organic cotton twill, one size, adjustable strap',
         'beanie': 'an Atlantis rib beanie, 100% organic cotton, one size'}
FULFIL = {'tee': 'fulfil:printful-sttu169', 'cap': 'fulfil:printful-ec7000', 'beanie': 'fulfil:printful-atlantis-449'}


def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def describe(p):
    code = p['regular_key'].split('-')[1]; dark = p.get('group') == 'dark'
    name = OS.title(p); line = p['line']; tags = []; extra = ''
    if line == 'signature':
        s = OM.SIG[code]; site = s.replace('the-', '') if s.startswith('the-') and s != 'the-thistlegorm' else s
        site = 'thistlegorm' if 'thistlegorm' in s else site
        title = f'{name} — Signature Series{" Dark" if dark else ""} organic tee'
        tags = ['signature-series', f'site:{site}'] + (['signature-series-dark', 'dark-line'] if dark else [])
        extra = 'Back: the full site illustration with facts, species and water. Chest: site name, dive flag and coordinates. Sleeve: the signature shark mark.'
    elif line == 'certifiedish':
        title = f'Certified-ish{" Dark" if dark else ""} — {name} organic tee'
        tags = ['certified-ish'] + (['certified-ish-dark', 'dark-line'] if dark else [])
        extra = 'Back: the full Certified-ish diagram. Front: the Certified-ish logo. Sleeve: the DS mark.'
    elif line == 'offworld':
        x = OM.OW[int(code[2:])]
        title = f'Off-World Hunt Club{" Dark" if dark else ""} — {name} organic tee'
        tags = ['off-world-hunt-club', f'ow:{x["slug"].replace("ow-", "")}'] + (['off-world-hunt-club-dark', 'dark-line'] if dark else [])
        extra = f'Back: “{H.escape(x["text"])}” in the off-world script, translated beneath it. Chest: the DS mark with the punch word in glyphs.'
    elif line == 'n73':
        x = OM.N73[int(code[1:])]
        title = f'1N73LL1G3NC3 — {name} organic tee'; tags = ['1n73ll1g3nc3', f'n73-{x["cat"]}']
        extra = f'{H.escape(x["text"])} Front: the design, full front. Sleeve: the DS mark.'
    elif line == 'aquatic':
        x = OM.AQ[code[2:]]; sub = AQ_SUB[x['subset']]
        title = f'Aquatic Comic · {sub["name"]} — {name} organic tee'
        tags = ['aquatic-comic', f'ac:{x["subset"]}', 'dark-line']
        if sub['names']:
            tags += ['personalized', 'personalize:' + ('1' if sub['names'] == 1 else 'couple' if x['subset'] in ('till-surface', 'master-class') else 'buddy')]
            extra = f'Personalized: {H.escape(sub.get("label", "your names"))}, added when you order. '
        extra += 'Front: the DS mark over the slogan. Back: the joke, the punch words in red.'
    elif line == 'caps':
        site = OM.CAPS[code]; brand = code in ('MRK', 'SEA', 'STK', 'WDM')
        title = f'{name} — organic cap'
        tags = ['cap', 'hat', 'embroidered', 'front:embroidered'] + (['brand', 'brand-cap'] if brand else ['site-cap', f'site:{site.replace("the-thistlegorm", "thistlegorm")}'])
        extra = 'Embroidered in the same threads and placements as the Flexfit cap: the front design, the DS mark on the side and the tagline on the back where the regular cap has them.'
    else:
        title = 'The Mark — organic beanie'; tags = ['beanie', 'hat', 'embroidered', 'front:embroidered', 'brand', 'brand-beanie']
        extra = 'The DS mark, 1.5 in, embroidered in white and red on the cuff.'
    return title, tags, extra


def build():
    out = []
    for p in organic.plan():
        kind = p['kind']; title, tags, extra = describe(p)
        colours = ['Black', 'Oxford Navy'] if kind == 'beanie' else [p['colour']]
        tags = sorted(set(tags + ['organic-line', 'eco', f'organic:{p["line"]}', FULFIL[kind], 'coming-soon',
                                  {'tee': 'tee', 'cap': 'cap', 'beanie': 'beanie'}[kind]] + [f'colour:{slug(c)}' for c in colours]))
        col = 'Black or Oxford Navy' if kind == 'beanie' else p['colour']
        body = (f'<p><strong>Organic edition.</strong> {H.escape(OS.title(p))}, the same design as the regular {"tee" if kind == "tee" else kind}, '
                f'on {BLANK[kind]}, in {H.escape(col)}. Same art, same price.</p><p>{extra}</p>'
                f'<p>Printed or embroidered to order. Shown as a mockup, not a photograph: samples are on the way.</p>')
        if kind == 'beanie':
            imgs = [vurl(f'{ORIGIN}/img/organic/beanie/beanie-the-mark-organic-black.webp'), vurl(f'{ORIGIN}/img/organic/beanie/beanie-the-mark-organic-oxford-navy.webp')]
            opt = 'Colour'; values = [(v['colour'], v) for v in p['variants']]
        elif kind == 'cap':
            imgs = [vurl(ORIGIN + u) for u in MAN[p['key']]['images']]; opt = 'Size'; values = [('One size', p['variants'][0])]
        else:
            imgs = [vurl(ORIGIN + u) for u in MAN[p['key']]['images']]
            if p['line'] in ('certifiedish', 'offworld', 'aquatic'): imgs = imgs[::-1]   # these lines lead with the back
            opt = 'Size'; values = [(v['size'], v) for v in p['variants']]
        inp = {'title': title, 'status': 'DRAFT', 'vendor': 'Doolittle Scuba',
               'productType': {'tee': 'T-shirt', 'cap': 'Cap', 'beanie': 'Beanie'}[kind], 'tags': tags, 'descriptionHtml': body,
               'productOptions': [{'name': opt, 'values': [{'name': n} for n, _ in values]}],
               'variants': [{'optionValues': [{'optionName': opt, 'name': n}], 'price': f'{v["price"]:.2f}', 'sku': v['sku'],
                             'inventoryPolicy': 'DENY'} for n, v in values],
               'files': [{'originalSource': u, 'contentType': 'IMAGE', 'alt': f'{OS.title(p)}, organic edition in {col}: mockup' + (', back' if i else '')}
                         for i, u in enumerate(imgs)]}
        code = p['regular_key'].split('-')[1]
        if p['line'] == 'signature' and p['group'] == 'light' and code in EXISTING:
            inp['id'] = f'gid://shopify/Product/{EXISTING[code]}'
        out.append(inp)
    return out


if __name__ == '__main__':
    P = build(); dst = sys.argv[1] if len(sys.argv) > 1 else '/tmp/organic_products.jsonl'
    with open(dst, 'w') as f:
        for i in P: f.write(json.dumps({'input': i}, ensure_ascii=False) + '\n')
    json.dump({'title': 'The organic line', 'handle': 'organic',
               'descriptionHtml': '<p>Every Doolittle Scuba design again on organic cotton: the five tee series, the caps and the beanie. Same art, same price.</p>',
               'ruleSet': {'appliedDisjunctively': False, 'rules': [{'column': 'TAG', 'relation': 'EQUALS', 'condition': 'organic-line'}]}},
              open(dst.replace('.jsonl', '.collection.json'), 'w'), indent=1)
    print(len(P), 'products ->', dst, '·', sum(1 for i in P if 'id' in i), 'update existing drafts')
