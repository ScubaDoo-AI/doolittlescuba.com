#!/usr/bin/env python3
"""Store SEO audit from the Shopify admin (works while the store is still private).

For every ACTIVE product: images with no alt text, search title (SEO title, or the
product title Shopify falls back to) over 70 characters, missing or too-long search
description (Shopify falls back to the start of the product description), and
duplicate titles. Collections too. Read-only.

  SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET (or SHOPIFY_TOKEN) in the environment.
  python tools/store_seo_audit.py
Writes store-seo-audit.md / .json and the GitHub job summary.
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from collections import Counter

SHOP = os.environ.get('SHOPIFY_STORE', 'x00ytr-y9.myshopify.com')
API_VER = '2026-10'
_TOK = {}


def token():
    if os.environ.get('SHOPIFY_TOKEN'):
        return os.environ['SHOPIFY_TOKEN']
    if 'tok' not in _TOK:
        cid, sec = os.environ.get('SHOPIFY_CLIENT_ID'), os.environ.get('SHOPIFY_CLIENT_SECRET')
        if not (cid and sec):
            sys.exit('set SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET or SHOPIFY_TOKEN')
        req = urllib.request.Request(f'https://{SHOP}/admin/oauth/access_token', method='POST',
                                     data=urllib.parse.urlencode({'grant_type': 'client_credentials', 'client_id': cid, 'client_secret': sec}).encode(),
                                     headers={'Content-Type': 'application/x-www-form-urlencoded'})
        _TOK['tok'] = json.load(urllib.request.urlopen(req, timeout=30))['access_token']
    return _TOK['tok']


def gql(q, v=None):
    for i in range(5):
        req = urllib.request.Request(f'https://{SHOP}/admin/api/{API_VER}/graphql.json', method='POST',
                                     data=json.dumps({'query': q, 'variables': v or {}}).encode(),
                                     headers={'X-Shopify-Access-Token': token(), 'Content-Type': 'application/json'})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503):
                time.sleep(2 + i * 2); continue
            raise
        if r.get('errors') and 'THROTTLED' in json.dumps(r['errors']):
            time.sleep(3); continue
        if r.get('errors'):
            sys.exit(f'GraphQL error: {r["errors"]}')
        return r['data']
    sys.exit('Shopify kept throttling')


Q = '''query($after:String){ products(first:50, after:$after, query:"status:active"){ pageInfo{hasNextPage endCursor}
 nodes{ handle title seo{title description} description(truncateAt:400)
  media(first:20){ nodes{ alt mediaContentType } } } } }'''
QC = '''query($after:String){ collections(first:100, after:$after){ pageInfo{hasNextPage endCursor}
 nodes{ handle title seo{title description} description image{altText} } } }'''


def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def main():
    prods, after = [], None
    while True:
        d = gql(Q, {'after': after})['products']
        prods += d['nodes']
        if not d['pageInfo']['hasNextPage']:
            break
        after = d['pageInfo']['endCursor']
    cols, after = [], None
    while True:
        d = gql(QC, {'after': after})['collections']
        cols += d['nodes']
        if not d['pageInfo']['hasNextPage']:
            break
        after = d['pageInfo']['endCursor']

    rows, noalt_imgs, noalt_prods, long_t, no_desc, long_d = [], 0, 0, 0, 0, 0
    titles = Counter()
    for p in prods:
        st = clean(p['seo']['title']) or clean(p['title'])
        sd = clean(p['seo']['description']) or clean(p['description'])
        imgs = [m for m in p['media']['nodes'] if m['mediaContentType'] == 'IMAGE']
        na = sum(1 for m in imgs if not clean(m['alt']))
        titles[st] += 1
        probs = []
        if na: probs.append(f'{na}/{len(imgs)} images no alt'); noalt_imgs += na; noalt_prods += 1
        if len(st) > 70: probs.append(f'search title {len(st)} chars'); long_t += 1
        if not sd: probs.append('no search description'); no_desc += 1
        elif not clean(p['seo']['description']) and len(sd) > 160: probs.append('search description falls back to body text'); long_d += 1
        elif len(sd) > 160: probs.append(f'search description {len(sd)} chars'); long_d += 1
        if probs: rows.append((p['handle'], probs))
    dups = {t: n for t, n in titles.items() if n > 1}
    crow = []
    for c in cols:
        probs = []
        if not (clean(c['seo']['description']) or clean(c['description'])): probs.append('no description')
        if c['image'] and not clean(c['image']['altText']): probs.append('image no alt')
        if probs: crow.append((c['handle'], probs))

    md = [f"# Store SEO audit (admin) — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}",
          f"{len(prods)} active products · {len(cols)} collections", "",
          "| Check | Products |", "|---|---|",
          f"| Images with no alt text | {noalt_prods} products ({noalt_imgs} images) |",
          f"| Search title over 70 chars | {long_t} |",
          f"| No search description | {no_desc} |",
          f"| Search description too long / falls back to body | {long_d} |",
          f"| Duplicate search titles | {len(dups)} titles ({sum(dups.values())} products) |",
          f"| Collections with problems | {len(crow)} of {len(cols)} |", ""]
    if dups:
        md += ['## Duplicate search titles (first 40)', *[f'- {n}× {t}' for t, n in sorted(dups.items(), key=lambda x: -x[1])[:40]], '']
    if crow:
        md += ['## Collections', *[f'- {h}: {"; ".join(p)}' for h, p in crow], '']
    if rows:
        md += ['## Products (first 150)', '| Product | Problems |', '|---|---|', *[f'| {h} | {"; ".join(p)} |' for h, p in rows[:150]]]
    text = '\n'.join(md) + '\n'
    open('store-seo-audit.md', 'w').write(text)
    json.dump({'products': [{'handle': h, 'problems': p} for h, p in rows], 'collections': [{'handle': h, 'problems': p} for h, p in crow],
               'duplicates': dups}, open('store-seo-audit.json', 'w'), indent=1)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        open(os.environ['GITHUB_STEP_SUMMARY'], 'a').write(text)
    print(text[:6000])


if __name__ == '__main__':
    main()
