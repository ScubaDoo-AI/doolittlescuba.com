#!/usr/bin/env python3
"""Create the organic products in Shopify as drafts, one productSet per product, then the "The organic line" collection.

Needs the Doolittle Order Bot app with write_products (+ read_products). Idempotent: a product whose first SKU already
exists in the store is skipped, so the job can be re-run after a failure. Everything is created as DRAFT; nothing is
published to a sales channel.

  python tools/organic_import.py            # dry run: what would be created
  python tools/organic_import.py --apply    # create
Environment: SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET (or SHOPIFY_TOKEN), as tools/aquatic_order.py.
"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import aquatic_order as AO
import organic_shopify as OSH

SET = '''mutation($i: ProductSetInput!) { productSet(synchronous: true, input: $i) {
  product { id handle } userErrors { field message } } }'''
SKU_Q = '''query($q: String!) { productVariants(first: 1, query: $q) { nodes { sku product { id } } } }'''
COLL_Q = '''query { collections(first: 1, query: "handle:organic") { nodes { id } } }'''
COLL = '''mutation($i: CollectionInput!) { collectionCreate(input: $i) { collection { id handle } userErrors { field message } } }'''


def exists(sku):
    return bool(AO.shopify(SKU_Q, {'q': f'sku:{sku}'})['productVariants']['nodes'])


def main(apply):
    inputs = [i for i in OSH.build() if 'id' not in i]     # the 14 earlier drafts are updated separately
    made = skipped = failed = 0
    for n, i in enumerate(inputs, 1):
        sku = i['variants'][0]['sku']
        if exists(sku):
            skipped += 1; print(f'{n:3d} skip   {sku:18s} {i["title"]}'); continue
        if not apply:
            print(f'{n:3d} would  {sku:18s} {i["title"]}'); continue
        r = AO.shopify(SET, {'i': i})['productSet']
        if r['userErrors']:
            failed += 1; print(f'{n:3d} ERROR  {sku:18s} {r["userErrors"]}')
        else:
            made += 1; print(f'{n:3d} made   {sku:18s} {r["product"]["handle"]}')
        time.sleep(0.6)
    coll = (AO.shopify(COLL_Q)['collections']['nodes'] or [None])[0]
    if coll:
        print('collection: exists', coll['id'])
    elif apply:
        c = json.load(open('/tmp/organic_products.collection.json')) if os.path.exists('/tmp/organic_products.collection.json') else {
            'title': 'The organic line', 'handle': 'organic',
            'descriptionHtml': '<p>Every Doolittle Scuba design again on organic cotton: the five tee series, the caps and the beanie. Same art, same price.</p>',
            'ruleSet': {'appliedDisjunctively': False, 'rules': [{'column': 'TAG', 'relation': 'EQUALS', 'condition': 'organic-line'}]}}
        r = AO.shopify(COLL, {'i': c})['collectionCreate']
        print('collection:', r['collection'] or r['userErrors'])
    else:
        print('collection: would create "The organic line" (tag organic-line)')
    print(f'\n{len(inputs)} products · made {made} · already there {skipped} · errors {failed} · {"APPLIED" if apply else "dry run"}')
    if failed: sys.exit(1)


ACT_Q = '''query($a: String) { products(first: 100, after: $a, query: "(tag:organic-line OR tag:jacket) AND status:draft") {
  nodes { id title } pageInfo { hasNextPage endCursor } } }'''
ACT = '''mutation($id: ID!) { productUpdate(product: {id: $id, status: ACTIVE}) { product { status } userErrors { message } } }'''


def activate(apply):
    """Draft -> ACTIVE for the organic line and the jackets (Eric, 13 Nov: "Activate the jackets - organics as well").
    The storefront is password-protected, so Active + Online Store shows nothing publicly (same as the 12 Nov pass)."""
    ids, a = [], None
    while True:
        r = AO.shopify(ACT_Q, {'a': a})['products']; ids += r['nodes']
        if not r['pageInfo']['hasNextPage']: break
        a = r['pageInfo']['endCursor']
    print(len(ids), 'draft products (organic-line or jacket)')
    bad = 0
    for n, p in enumerate(ids, 1):
        if not apply: print('would activate', p['title']); continue
        e = AO.shopify(ACT, {'id': p['id']})['productUpdate']['userErrors']
        if e: bad += 1; print('ERROR', p['title'], e)
        time.sleep(0.3)
    print(f"{len(ids)} {'activated' if apply else 'to activate'} · errors {bad}")
    if bad: sys.exit(1)


if __name__ == '__main__':
    if '--activate' in sys.argv: activate('--apply' in sys.argv)
    else: main('--apply' in sys.argv)
