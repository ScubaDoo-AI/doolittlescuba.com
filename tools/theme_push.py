#!/usr/bin/env python3
"""Push theme files from shopify-theme/ to a Shopify theme (default: the live one) through the Doolittle Order Bot app.
The chat connector can't write the published theme; the bot app can once it has the write_themes scope.

  tools/theme_push.py blocks/aquatic-personalize.liquid [more paths]   # dry run: shows what would change
  tools/theme_push.py --apply blocks/aquatic-personalize.liquid        # writes them
  --theme <numeric id>   another theme instead of the live (MAIN) one

Each file is compared with the theme's copy first and only changed files are sent. Before writing, the theme's current
copy is saved to theme-backups/<theme id>/<path> (an artifact of the run), so a change can be put back.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aquatic_order as AO

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shopify-theme')
args = [a for a in sys.argv[1:]]
apply = '--apply' in args; args = [a for a in args if a != '--apply']
tid = None
if '--theme' in args:
    i = args.index('--theme'); tid = f'gid://shopify/OnlineStoreTheme/{int(args[i + 1])}'; del args[i:i + 2]
paths = args or sys.exit(__doc__)

if not tid:
    t = AO.shopify('{ themes(first: 1, roles: [MAIN]) { nodes { id name } } }')['themes']['nodes'][0]
    tid = t['id']; print('live theme:', t['name'], tid)
cur = AO.shopify('query($id: ID!, $f: [String!]) { theme(id: $id) { name files(first: 50, filenames: $f) { nodes { filename '
                 'body { ... on OnlineStoreThemeFileBodyText { content } } } } } }', {'id': tid, 'f': paths})['theme']
have = {n['filename']: (n.get('body') or {}).get('content') for n in cur['files']['nodes']}
send = []
for p in paths:
    new = open(os.path.join(ROOT, p), encoding='utf-8').read()
    old = have.get(p)
    if old == new: print('same     ', p); continue
    print('CHANGED  ' if old is not None else 'NEW      ', p, f'({len(old or "")} → {len(new)} chars)')
    if old is not None:
        bk = os.path.join('theme-backups', tid.rsplit('/', 1)[1], p); os.makedirs(os.path.dirname(bk), exist_ok=True)
        open(bk, 'w', encoding='utf-8').write(old)
    send.append({'filename': p, 'body': {'type': 'TEXT', 'value': new}})
if not send: sys.exit(0)
if not apply: print('dry run: add --apply to write'); sys.exit(0)
r = AO.shopify('mutation($id: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) { themeFilesUpsert(themeId: $id, files: $files) '
               '{ upsertedThemeFiles { filename } userErrors { field message } } }', {'id': tid, 'files': send})['themeFilesUpsert']
if r['userErrors']: sys.exit('errors: ' + json.dumps(r['userErrors']))
print('written:', ', '.join(f['filename'] for f in r['upsertedThemeFiles']), '→', cur['name'])
