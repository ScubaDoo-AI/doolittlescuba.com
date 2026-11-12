#!/usr/bin/env python3
"""Check the Shopify and Printful keys without changing anything and without printing a key.

  Shopify       SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET → 24-hour token → shop name + granted scopes
  Shopify Files read one file; ask for an upload slot (stagedUploadsCreate; nothing is uploaded or created)
  Printful      PRINTFUL_TOKEN → token scopes, the stores it reaches, store 18960047's synced products

Exit code 0 when all three pass. Run from GitHub Actions ("Check connections") or locally with the env vars set.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aquatic_order as O

NEED_SHOPIFY = {'read_orders', 'read_files', 'write_files'}
results = []


def check(name, fn):
    try:
        msg = fn(); results.append((name, True, msg))
    except SystemExit as e:
        results.append((name, False, str(e)[:300]))
    except Exception as e:
        results.append((name, False, f'{type(e).__name__}: {str(e)[:300]}'))


def shopify():
    d = O.shopify('{ shop { name myshopifyDomain } currentAppInstallation { app { title } accessScopes { handle } } }')
    got = {s['handle'] for s in d['currentAppInstallation']['accessScopes']}
    miss = NEED_SHOPIFY - got
    if miss: raise SystemExit(f'connected to {d["shop"]["name"]}, but missing scopes: {", ".join(sorted(miss))}')
    return f'{d["shop"]["name"]} ({d["shop"]["myshopifyDomain"]}) via "{d["currentAppInstallation"]["app"]["title"]}"; scopes {", ".join(sorted(got))}'


def files():
    f = O.shopify('{ files(first: 1) { nodes { fileStatus } } }')['files']['nodes']
    st = O.shopify(O.STAGE_M, {'input': [{'filename': 'connection-check.png', 'mimeType': 'image/png', 'httpMethod': 'POST',
                                          'resource': 'IMAGE', 'fileSize': '1000'}]})['stagedUploadsCreate']
    if st['userErrors'] or not st['stagedTargets']: raise SystemExit(f'upload slot refused: {st["userErrors"]}')
    return f'read OK ({len(f)} file sampled); upload slot granted (nothing uploaded)'


def printful():
    sc = O.printful('GET', '/v2/oauth-scopes').get('data', [])
    names = sorted({s.get('value') or s.get('name') or str(s) for s in sc}) if isinstance(sc, list) else sc
    stores = O.printful('GET', '/v2/stores').get('data', [])
    ours = [s for s in stores if str(s.get('id')) == O.PF_STORE]
    if not ours: raise SystemExit(f'token works but does not reach store {O.PF_STORE} (reaches: {[s.get("name") for s in stores]})')
    code, r = O.http('GET', 'https://api.printful.com/sync/products?limit=1',
                     {'Authorization': 'Bearer ' + os.environ['PRINTFUL_TOKEN'], 'X-PF-Store-Id': O.PF_STORE})
    sync = f'{r["paging"]["total"]} synced products visible' if code == 200 else f'sync products NOT readable ({code}) — linking will fail'
    if code != 200: raise SystemExit(f'store "{ours[0].get("name")}" reached; {sync}')
    return f'store "{ours[0].get("name")}" ({O.PF_STORE}); {sync}; scopes {", ".join(map(str, names))}'


def cap_areas():
    """Flexfit 6277 (140) embroidery areas, read-only: the exact per-placement template sizes the caps' files must fit
    (tools/printful_caps.py assumes front <= 2.25 in tall, left 1.25 in, back ~3 x 1 in from Printful's general guidance)."""
    code, r = O.http('GET', 'https://api.printful.com/mockup-generator/printfiles/140',
                     {'Authorization': 'Bearer ' + os.environ['PRINTFUL_TOKEN'], 'X-PF-Store-Id': O.PF_STORE})
    if code != 200: raise SystemExit(f'printfiles not readable ({code})')
    res = r['result']; pf = {f['printfile_id']: f for f in res.get('printfiles', [])}
    out = [f"available {res.get('available_placements')}; printfiles {[(f.get('printfile_id'), f.get('width'), f.get('height'), f.get('dpi'), f.get('fill_mode')) for f in res.get('printfiles', [])]}; "
           f"variant 0 placements {res.get('variant_printfiles', [{}])[0].get('placements')}"]
    for v in res.get('variant_printfiles', [])[:1]:
        for pl, pid in v.get('placements', {}).items():
            f = pf.get(pid, {}); dpi = f.get('dpi') or 300
            out.append(f"{pl}: {f.get('width')}x{f.get('height')} px @ {dpi} dpi = {f.get('width', 0)/dpi:.2f} x {f.get('height', 0)/dpi:.2f} in")
    return '6277 areas — ' + '; '.join(out)


if __name__ == '__main__':
    if os.environ.get('SHOPIFY_CLIENT_ID') or os.environ.get('SHOPIFY_TOKEN'):
        check('Shopify', shopify); check('Shopify Files', files)
    else:
        results.append(('Shopify', False, 'SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET not set'))
    if os.environ.get('PRINTFUL_TOKEN'): check('Printful', printful); check('Printful cap areas', cap_areas)
    else: results.append(('Printful', False, 'PRINTFUL_TOKEN not set'))
    out = [f'{"PASS" if ok else "FAIL"}  {n}: {m}' for n, ok, m in results]
    print('\n'.join(out))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
            f.write('## Connection check\n\n' + '\n'.join(f'- {"✅" if ok else "❌"} **{n}** — {m}' for n, ok, m in results) + '\n')
    sys.exit(0 if all(ok for _, ok, _ in results) else 1)
