#!/usr/bin/env python3
"""Fill Shopify search (SEO) descriptions and fix over-long search titles.

  python tools/seo_fill.py inventory          # dump active products -> seo-inventory.json
  python tools/seo_fill.py dry                # write seo-plan.json / seo-plan.md (no changes)
  python tools/seo_fill.py apply [--only handle,handle]   # productUpdate seo{title,description}
Rules live in tools/seo_rules.py (plan()). Only products whose own SEO description is empty
get one; an existing hand-written SEO description is never overwritten.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from store_seo_audit import gql  # same token / retry logic

Q = '''query($after:String){ products(first:100, after:$after, query:"status:active"){ pageInfo{hasNextPage endCursor}
 nodes{ id handle title productType vendor tags seo{title description}
  priceRangeV2{ minVariantPrice{amount} }
  description(truncateAt:300) } } }'''
M = '''mutation($p:ProductUpdateInput!){ productUpdate(product:$p){ product{ id seo{title description} } userErrors{ field message } } }'''


def inventory():
    out, after = [], None
    while True:
        d = gql(Q, {'after': after})['products']
        out += d['nodes']
        if not d['pageInfo']['hasNextPage']: break
        after = d['pageInfo']['endCursor']
    json.dump(out, open('seo-inventory.json', 'w'), indent=1)
    print(len(out), 'products')
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'dry'
    prods = inventory()
    if mode == 'inventory': return
    from seo_rules import plan
    only = set()
    if '--only' in sys.argv: only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    changes, skipped = [], []
    for p in prods:
        if only and p['handle'] not in only: continue
        ch = plan(p)
        if ch: changes.append(ch)
        else: skipped.append(p['handle'])
    json.dump(changes, open('seo-plan.json', 'w'), indent=1)
    md = [f'# SEO plan ({mode}) — {len(changes)} products to change, {len(skipped)} unchanged', '', '| Product | Search title | Search description | chars |', '|---|---|---|---|']
    md += [f"| {c['handle']} | {c.get('title') or '(unchanged)'} | {c.get('description') or '(unchanged)'} | {len(c.get('description') or '')} |" for c in changes]
    open('seo-plan.md', 'w').write('\n'.join(md) + '\n')
    if os.environ.get('GITHUB_STEP_SUMMARY'): open(os.environ['GITHUB_STEP_SUMMARY'], 'a').write('\n'.join(md[:60]) + '\n')
    if mode != 'apply':
        print('\n'.join(md[:40])); return
    ok = bad = 0
    for c in changes:
        seo = {}
        if c.get('title'): seo['title'] = c['title']
        if c.get('description'): seo['description'] = c['description']
        r = gql(M, {'p': {'id': c['id'], 'seo': seo}})['productUpdate']
        if r['userErrors']: bad += 1; print('ERR', c['handle'], r['userErrors'])
        else: ok += 1
        time.sleep(0.25)
    print(f'applied {ok}, errors {bad}')
    if bad: sys.exit(1)


if __name__ == '__main__':
    main()
