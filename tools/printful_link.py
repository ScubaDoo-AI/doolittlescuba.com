#!/usr/bin/env python3
"""Link the products Printful imported from Shopify to their Printful blanks and print files.

The store is Shopify-connected (Printful store 18960047), so the sync API applies: GET /sync/products,
GET /sync/products/{id}, PUT /sync/variant/{id}. (The /store/products routes in printful_stickers.py,
printful_offworld.py, printful_n73.py only work on a manual / API store.) The plans come from those three
scripts: stickers (kiss-cut route), Off-World Hunt Club light + dark (DTG back + chest) 1N73LL1G3NC3 (DTG front) and Aquatic Comic Boat Banter (DTG front + back, printful_aquatic.py).
Sync variants are matched by SKU, then by Shopify variant id (external_id).

  PRINTFUL_TOKEN=… tools/printful_link.py                  # dry run: what would be linked, what is unmatched
  PRINTFUL_TOKEN=… tools/printful_link.py --apply          # write the links
  PRINTFUL_TOKEN=… tools/printful_link.py --apply --only stickers,n73,offworld

Retail prices stay Shopify's; only the Printful variant, the files and is_ignored are sent.
"""
import os, sys, json, time, urllib.request, urllib.error, importlib.util

STORE = '18960047'
HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def fix(files):
    # the 1717 (product 586) names its DTG placements front / back; 'default' is rejected on the sync API
    return [dict(f, type='front' if f['type'] == 'default' else f['type']) for f in files]


def targets(only):
    out = {}
    if 'stickers' in only:
        for r in load('printful_stickers').plan('kiss'):
            out[r['sku']] = dict(line='stickers', ext=str(r['shopify_variant']), variant_id=r['variant_id'],
                                 files=[{'type': 'default', 'url': r['file']}])
    if 'offworld' in only:
        for p in load('printful_offworld').plan('dtg'):
            for v in p['variants']:
                out[v['sku']] = dict(line='offworld', ext=str(v['shopify_variant']), variant_id=v['variant_id'], files=fix(p['files']))
    if 'n73' in only:
        for p in load('printful_n73').plan('dtg'):
            for v in p['variants']:
                out[v['sku']] = dict(line='n73', ext=str(v['shopify_variant']), variant_id=v['variant_id'], files=fix(p['files']))
    if 'certifiedish' in only:   # 20 designs x light + dark, front logo + back
        for p in load('printful_certifiedish').plan('dtg'):
            for v in p['variants']:
                out[v['sku']] = dict(line='certifiedish', ext='sku:' + v['sku'], variant_id=v['variant_id'], files=p['files'])
    if 'signature' in only:   # 14 designs x light + dark, front + back + right sleeve
        for p in load('printful_signature').plan('dtg'):
            for v in p['variants']:
                out[v['sku']] = dict(line='signature', ext='sku:' + v['sku'], variant_id=v['variant_id'], files=p['files'])
    if 'aquatic' in only:   # Boat Banter S01–S20 only; the personalized Aquatic Comic tees are ordered by hand
        for p in load('printful_aquatic').plan('dtg'):
            for v in p['variants']:
                out[v['sku']] = dict(line='aquatic', ext='sku:' + v['sku'], variant_id=v['variant_id'], files=p['files'])
        for p in load('printful_aquatic').plan('dtg', all_designs=True):   # name tees: ignore, so Shopify imports don't hold
            if p['files']: continue
            for v in p['variants']:
                out[v['sku']] = dict(line='aquatic-ignored', ext='sku:' + v['sku'], variant_id=None, files=[], ignore=True)
    return out


def api(token, method, path, body=None, tries=4):
    for k in range(tries):
        req = urllib.request.Request('https://api.printful.com' + path, method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={'Authorization': 'Bearer ' + token, 'X-PF-Store-Id': STORE, 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=90) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:500]
            if e.code == 429 and k < tries - 1: time.sleep(30); continue
            return {'code': e.code, 'error': msg}


if __name__ == '__main__':
    token = os.environ.get('PRINTFUL_TOKEN') or sys.exit('PRINTFUL_TOKEN not set')
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else ['stickers', 'offworld', 'n73', 'aquatic', 'signature', 'certifiedish']
    apply = '--apply' in sys.argv
    T = targets(only); by_ext = {t['ext']: s for s, t in T.items()}
    items, off = [], 0
    while True:
        res = api(token, 'GET', f'/sync/products?offset={off}&limit=100'); items += res['result']
        off += 100
        if off >= res['paging']['total']: break
    seen, linked, failed = set(), 0, []
    for sp in items:
        det = api(token, 'GET', f'/sync/products/{sp["id"]}'); time.sleep(0.3)
        for sv in det['result']['sync_variants']:
            sku = sv.get('sku') or ''
            if sku not in T: sku = by_ext.get(str(sv.get('external_id')), '')
            if not sku: continue
            seen.add(sku); t = T[sku]
            if not apply: continue
            if t.get('ignore'):   # personalized: made per order by tools/aquatic_order.py, never by the sync
                if sv.get('is_ignored') and '--force' not in sys.argv: continue
                r = api(token, 'PUT', f'/sync/variant/{sv["id"]}', {'is_ignored': True})
                if r.get('code') == 200: linked += 1; print('ignored', sku, flush=True)
                else: failed.append((sku, r.get('error'))); print('FAILED', sku, r.get('error'), flush=True)
                time.sleep(0.6); continue
            if sv.get('synced') and sv.get('variant_id') == t['variant_id'] and '--force' not in sys.argv: continue   # already linked
            r = api(token, 'PUT', f'/sync/variant/{sv["id"]}', {'variant_id': t['variant_id'], 'files': t['files'], 'is_ignored': False})
            if r.get('code') == 200: linked += 1; print('linked', sku, '→', t['variant_id'], flush=True)
            else: failed.append((sku, r.get('error'))); print('FAILED', sku, r.get('error'), flush=True)
            time.sleep(0.6)
    missing = sorted(set(T) - seen)
    by_line = {}
    for s in seen: by_line[T[s]['line']] = by_line.get(T[s]['line'], 0) + 1
    print(f'\nPrintful sync products: {len(items)} · planned variants: {len(T)} · matched: {len(seen)} {by_line}')
    if missing: print(f'not found in Printful ({len(missing)}):', ', '.join(missing[:40]))
    if apply: print(f'linked {linked} · failed {len(failed)}')
