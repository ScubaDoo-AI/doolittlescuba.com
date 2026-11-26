#!/usr/bin/env python3
"""The site's product map, for the cart on DoolittleScuba.com (Eric, 21 Nov 2026: "Cart on the site").

1. Reads every product the Headless storefront can see, through the Storefront API with the PUBLIC token (made to sit in
   website code; the private token is never used here).
2. Writes js/catalog.json: one entry per product, keyed by its SKU stem (the part every variant's SKU shares, e.g.
   DS-BBT-T for the Black Bart tee, DS-BAL-PR for the Bali light pair):
     {"DS-BBT-T": {"h": handle, "t": title, "o": [option names], "v": [[variant number, [option values], price, sellable], ...]}}
   plus "_h": {handle: stem} so a pair link can be turned into a stem.
3. Stamps data-buy="<stem>" (and data-buy-opt="Colour=Navy" where one product spans several cards, data-buy-pair for
   the pair button) on the product cards of every page, so js/cart.js knows what each card adds. Idempotent.

Cards with no stem on purpose: Make it yours, Home Port and the personalized Surface Interval tees (they need a name,
a pin or a design first and keep their own flows), the collection cards.

  tools/catalog_map.py            # fetch, write, stamp, report
  tools/catalog_map.py --check    # report only
Run daily by .github/workflows/catalog-map.yml (prices and sold-out state follow Shopify), then tools/bust.py.
"""
import json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = 'b048eedb23178c86ccff32db1f44d1f8'     # public Storefront API token, Headless storefront "Doolittle Scuba Designs Headless"
API = 'https://shop.doolittlescuba.com/api/2026-10/graphql.json'
PAGES = ['index.html', 'signature/index.html', 'certified-ish/index.html', 'off-world/index.html', '1n73ll1g3nc3/index.html',
         'surface-interval/index.html', 'organic/index.html', 'stickers/index.html', 'towels/index.html', 'rash-guards/index.html']
SUFFIX = {'plates': ['T'], 'dark': ['TD'], 'certifiedish': ['T'], 'certifiedish-dark': ['TD'], 'offworld': ['T'],
          'offworld-dark': ['TD'], 'n73': ['T'], 'aquatic-boat-banter': ['TD', 'T']}
JACKET = {'champion-packable-anorak': 'the-mark-champion-packable-anorak', 'basic-windbreaker': 'the-mark-basic-windbreaker'}
Q = '''query($a:String){ products(first:100, after:$a){ nodes{ handle title options{ name }
  variants(first:100){ nodes{ id sku availableForSale price{ amount } selectedOptions{ name value } } } }
  pageInfo{ hasNextPage endCursor } } }'''


def fetch():
    out, after = [], None
    while True:
        r = urllib.request.Request(API, data=json.dumps({'query': Q, 'variables': {'a': after}}).encode(),
                                   headers={'Content-Type': 'application/json', 'X-Shopify-Storefront-Access-Token': TOKEN})
        d = json.load(urllib.request.urlopen(r, timeout=60))['data']['products']; out += d['nodes']
        if not d['pageInfo']['hasNextPage']: return out
        after = d['pageInfo']['endCursor']


def stem(skus):
    parts = [s.split('-') for s in skus if s]
    if not parts: return None
    if len(parts) == 1: return '-'.join(parts[0])
    n = 0
    while all(len(p) > n and p[n] == parts[0][n] for p in parts): n += 1
    return '-'.join(parts[0][:n]) or None


def build(products):
    cat, by_h, by_sku = {}, {}, {}
    for p in products:
        vs = p['variants']['nodes']; st = stem([v['sku'] for v in vs]) or ('H-' + p['handle'])   # Printful-made SKUs share no stem (the jackets): key by handle
        if not st or st in cat: continue
        num = lambda gid: int(gid.rsplit('/', 1)[1])
        names = [o['name'] for o in p['options']]
        cat[st] = {'h': p['handle'], 't': p['title'], 'o': [] if names == ['Title'] else names,
                   'v': [[num(v['id']), [] if names == ['Title'] else [o['value'] for o in v['selectedOptions']],
                          float(v['price']['amount']), 1 if v['availableForSale'] else 0] for v in vs]}
        by_h[p['handle']] = st
        for v in vs: by_sku[v['sku']] = st
    cat['_h'] = by_h
    return cat, by_sku


def card_stem(a, cat, by_sku):
    """(stem, option filter) for one card's attributes, or (None, None)."""
    if a.get('custom-order') or a.get('line', '').startswith('aquatic-') and a.get('line') != 'aquatic-boat-banter': return None, None
    if 'sku' in a: return by_sku.get(a['sku']) or (a['sku'] if a['sku'] in cat else None), None
    code, line, kind, slug = a.get('code', ''), a.get('line', ''), a.get('kind', ''), a.get('slug', '')
    if re.match(r'DS-AC[A-RT-Z]\d', code): return None, None      # personalized Surface Interval (names on the shirt): own flow
    if code.startswith('DS-'): return (code if code in cat else by_sku.get(code)), None
    if line in ('rg-light', 'rg-dark') and code:   # rash guards: the card opens on the men's long sleeve; deck.js swaps the stem with the style picker
        c = f"DS-{code}-RGMLS-{'L' if line == 'rg-light' else 'D'}"
        return (c if c in cat else None), None
    if kind == 'jacket':
        for k, h in JACKET.items():
            if k in slug:
                st = cat['_h'].get(h); on = 'Color' if st and 'Color' in cat[st]['o'] else 'Colour'   # Printful-made products name it Color
                return st, on + '=' + a.get('colour', '')
    if slug.startswith('beanie-'): return cat['_h'].get('the-mark-beanie'), 'Colour=' + a.get('colour', '')
    if kind in ('site', 'brand') and code:
        for c in (f'DS-{code}-CD', f'DS-{code}'):
            if c in cat: return c, None
    for suf in SUFFIX.get(line, []):
        if f'DS-{code}-{suf}' in cat: return f'DS-{code}-{suf}', None
    return None, None


def stamp(cat, by_sku, write=True):
    report = {}
    for page in PAGES:
        path = f'{ROOT}/{page}'; s = open(path).read(); n = miss = 0; misses = []
        def fix(m):
            nonlocal n, miss
            tag = m.group(0)
            if 'data-line="coll"' in tag: return tag
            tag = re.sub(r' data-buy(-opt|-pair)?="[^"]*"', '', tag)
            a = dict(re.findall(r'data-([a-z-]+)="([^"]*)"', tag))
            st, opt = card_stem(a, cat, by_sku)
            add = ''
            if st: add += f' data-buy="{st}"'; n += 1
            elif not (a.get('custom-order') or a.get('line', '').startswith('aquatic-') or 'make-it-yours' in a.get('slug', '')
                      or re.match(r'DS-AC[A-RT-Z]\d', a.get('code', ''))
                      or a.get('sku', '').startswith('DS-STK-D-')):   # die-cut / brand singles: sold only inside the packs
                miss += 1; misses.append(a.get('slug') or a.get('sku') or '?')
            if st and opt: add += f' data-buy-opt="{opt}"'
            pm = re.search(r'/products/([a-z0-9-]+)', a.get('pair', ''))
            if pm and pm.group(1) in cat['_h']: add += f' data-buy-pair="{cat["_h"][pm.group(1)]}"'
            return tag[:-1] + add + '>'
        s2 = re.sub(r'<figure class="sh(?: [^"]*)?"[^>]*>', fix, s)
        if write and s2 != s: open(path, 'w').write(s2)
        report[page] = (n, miss, misses[:6])
    return report


if __name__ == '__main__':
    check = '--check' in sys.argv
    cat, by_sku = build(fetch())
    if not check:
        json.dump(cat, open(f'{ROOT}/js/catalog.json', 'w'), separators=(',', ':'), ensure_ascii=False)
    print(len(cat) - 1, 'products in the map')
    for page, (n, miss, ex) in stamp(cat, by_sku, write=not check).items():
        print(f'{page:32s} {n:4d} cards linked' + (f', {miss} without a product: {ex}' if miss else ''))
