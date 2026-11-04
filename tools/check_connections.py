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


if __name__ == '__main__':
    if os.environ.get('SHOPIFY_CLIENT_ID') or os.environ.get('SHOPIFY_TOKEN'):
        check('Shopify', shopify); check('Shopify Files', files)
    else:
        results.append(('Shopify', False, 'SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET not set'))
    if os.environ.get('PRINTFUL_TOKEN'): check('Printful', printful)
    else: results.append(('Printful', False, 'PRINTFUL_TOKEN not set'))
    out = [f'{"PASS" if ok else "FAIL"}  {n}: {m}' for n, ok, m in results]
    print('\n'.join(out))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
            f.write('## Connection check\n\n' + '\n'.join(f'- {"✅" if ok else "❌"} **{n}** — {m}' for n, ok, m in results) + '\n')
    sys.exit(0 if all(ok for _, ok, _ in results) else 1)
