#!/usr/bin/env python3
"""Link the products Printful imported from Shopify to their Printful blanks and print files.

The store is Shopify-connected (Printful store 18960047), so the sync API applies: GET /sync/products,
GET /sync/products/{id}, PUT /sync/variant/{id}. (The /store/products routes in printful_stickers.py,
printful_offworld.py, printful_n73.py only work on a manual / API store.) The plans come from the printful_*.py
scripts: stickers (kiss-cut route), Off-World Hunt Club
light + dark (DTG back + chest), 1N73LL1G3NC3 (DTG front), Aquatic Comic Boat Banter (DTG front + back,
printful_aquatic.py), Signature Series, Certified-ish and the embroidered caps (printful_caps.py, item-level thread options).
Sync variants are matched by SKU, then by Shopify variant id (external_id).
The 37 three-sticker packs (DS-PK-*) are not on Printful: Sticker Mule prints them in bulk from the 4 x 6 PDFs
(tools/packs.json "print", archived in Shopify Files), so there is no packs line here (retired 12 Nov 2026).

  PRINTFUL_TOKEN=… tools/printful_link.py                  # dry run: what would be linked, what is unmatched
  PRINTFUL_TOKEN=… tools/printful_link.py --apply          # write the links
  PRINTFUL_TOKEN=… tools/printful_link.py --apply --only stickers,n73,offworld
  PRINTFUL_TOKEN=… tools/printful_link.py --apply --only caps        # the 18 embroidered Flexfit 6277 caps (printful_caps.py)
  PRINTFUL_TOKEN=… tools/printful_link.py --apply --only organic     # every organic edition (tools/organic.py)
  PRINTFUL_TOKEN=… tools/printful_link.py --apply --only beanie      # The Mark — Beanie, Stanley/Stella STAU295 (printful_beanie.py)
  PRINTFUL_TOKEN=… tools/printful_link.py --apply --force --only signature,caps --sku DS-NAV   # one site, after a print-file change

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
    if 'caps' in only:   # 12 embroidered Flexfit 6277 caps (printful_caps.py): front + left + back, thread colours as item options
        for p in load('printful_caps').plan():
            for v in p['variants']:
                out[v['sku']] = dict(line='caps', ext=str(v['shopify_variant']), variant_id=v['variant_id'], files=p['files'], options=p['options'])
    if 'beanie' in only:   # The Mark — Beanie, Stanley/Stella STAU295 (printful_beanie.py): cuff embroidery, item-level thread options
        for p in load('printful_beanie').plan():
            for v in p['variants']:
                out[v['sku']] = dict(line='beanie', ext=str(v['shopify_variant']), variant_id=v['variant_id'], files=p['files'], options=p['options'])
    if 'jackets' in only:   # Champion CO200 anorak + SOL'S 32000 windbreaker (printful_jackets.py): left-chest DS mark, matched by SKU
        for p in load('printful_jackets').plan():
            for v in p['variants']:
                out[v['sku']] = dict(line='jackets', ext='sku:' + v['sku'], variant_id=v['variant_id'], files=p['files'], options=p['options'])
    if 'organic' in only:   # the organic editions (tools/organic.py): STTU169 tees, EC7000 caps, Atlantis beanie — matched by SKU
        for p in load('organic').plan():
            for v in p['variants']:
                if p['personalized']:   # made per order by aquatic_order.py (TDO SKUs), never by the sync
                    out[v['sku']] = dict(line='organic-ignored', ext='sku:' + v['sku'], variant_id=None, files=[], ignore=True); continue
                t = dict(line='organic-' + p['kind'], ext='sku:' + v['sku'], variant_id=v['variant_id'], files=fix(p['files']))
                if p.get('options'): t['options'] = p['options']
                out[v['sku']] = t
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
    T = targets(only)
    if '--sku' in sys.argv:   # restrict to SKUs starting with any of the given prefixes, e.g. --sku DS-NAV (one site's tees and caps)
        pre = tuple(sys.argv[sys.argv.index('--sku') + 1].split(',')); T = {s: t for s, t in T.items() if s.startswith(pre)}
        print(f'--sku {",".join(pre)}: {len(T)} planned variants', flush=True)
    by_ext = {t['ext']: s for s, t in T.items()}
    items, off = [], 0
    while True:
        res = api(token, 'GET', f'/sync/products?offset={off}&limit=100'); items += res['result']
        off += 100
        if off >= res['paging']['total']: break
    seen, linked, failed = set(), 0, []
    # only open the products whose name belongs to the lines asked for (a 295-product store took 20+ min opening all)
    NAMES = {'aquatic': ['aquatic comic'], 'signature': ['signature series'], 'certifiedish': ['certified-ish'],
             'n73': ['1n73ll1g3nc3'], 'offworld': ['off-world'], 'stickers': ['sticker', 'achievement', 'seal', 'logo', 'bumper', 'kit'],
             'caps': ['dark cap'], 'beanie': ['beanie'], 'organic': ['organic'], 'jackets': ['anorak', 'windbreaker']}
    keys = [k for l in only for k in NAMES.get(l, [])]
    if keys and '--all-products' not in sys.argv:
        picked = [sp for sp in items if any(k in (sp.get('name') or '').lower() for k in keys)]
        print(f'opening {len(picked)} of {len(items)} sync products (name match: {", ".join(keys)})', flush=True)
        if picked: items = picked
    for sp in items:
        det = api(token, 'GET', f'/sync/products/{sp["id"]}'); time.sleep(0.3)
        if 'result' not in det: print('skip', sp.get('name'), det.get('code'), str(det.get('error'))[:120], flush=True); continue
        for sv in det['result']['sync_variants']:
            sku = sv.get('sku') or ''
            if sku not in T: sku = by_ext.get(str(sv.get('external_id')), '')
            if not sku: continue
            seen.add(sku); t = T[sku]
            if '--show' in sys.argv:   # read back what Printful stores per file (placement + position), e.g. to check a left-chest offset
                print('stored', sku, json.dumps([{k: f.get(k) for k in ('type', 'filename', 'position')} for f in sv.get('files', [])]), flush=True)
            if not apply: continue
            if t.get('ignore'):   # personalized: made per order by tools/aquatic_order.py, never by the sync
                if sv.get('is_ignored') and '--force' not in sys.argv: continue
                r = api(token, 'PUT', f'/sync/variant/{sv["id"]}', {'is_ignored': True})
                if r.get('code') == 200: linked += 1; print('ignored', sku, flush=True)
                else: failed.append((sku, r.get('error'))); print('FAILED', sku, r.get('error'), flush=True)
                time.sleep(0.6); continue
            if sv.get('synced') and sv.get('variant_id') == t['variant_id'] and '--force' not in sys.argv: continue   # already linked
            body = {'variant_id': t['variant_id'], 'files': t['files'], 'is_ignored': False}
            if t.get('options'): body['options'] = t['options']   # embroidery: thread colours + embroidery_type ride on the variant, not the file
            r = api(token, 'PUT', f'/sync/variant/{sv["id"]}', body)
            if r.get('code') == 200:
                linked += 1; print('linked', sku, '→', t['variant_id'], flush=True)
                if '--show' in sys.argv:
                    print('  now', json.dumps([{k: f.get(k) for k in ('type', 'filename', 'position')} for f in r['result'].get('files', [])]), flush=True)
            else: failed.append((sku, r.get('error'))); print('FAILED', sku, r.get('error'), flush=True)
            time.sleep(0.6)
    missing = sorted(set(T) - seen)
    by_line = {}
    for s in seen: by_line[T[s]['line']] = by_line.get(T[s]['line'], 0) + 1
    print(f'\nPrintful sync products: {len(items)} · planned variants: {len(T)} · matched: {len(seen)} {by_line}')
    if missing: print(f'not found in Printful ({len(missing)}):', ', '.join(missing[:40]))
    if apply: print(f'linked {linked} · failed {len(failed)}')
