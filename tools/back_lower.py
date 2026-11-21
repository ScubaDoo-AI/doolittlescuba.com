#!/usr/bin/env python3
"""Re-place every catalog back master by tools/back_place.py (ink top 2.00 in, fit above 15.75 in) — Eric, 21 Nov 2026.

Lines: certifiedish (40 files), signature (28), offworld (60), aquatic (20 Boat Banter). The organic editions and the
Make it yours tee use these same files through the plans, so they follow once the plans point at the new names.

What it does: downloads each back named in the plans (under its old name), moves the ink so its top sits 2.00 in down
the 12 x 16 in area, keeps the horizontal centre, shrinks only what would run past 15.75 in, and saves it as
<old name>_back2in.png. New names so Printful fetches fresh files.

  tools/back_lower.py --out DIR                          # render + report only
  tools/back_lower.py --out DIR --upload                 # and upload to Shopify Files (SHOPIFY_CLIENT_ID/SECRET)
  ... --only certifiedish,signature,offworld,aquatic

Then relink: Actions → Printful link, lines 'offworld,signature,certifiedish' and 'aquatic', apply + force; then organic.
"""
import os, sys, io, importlib
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import back_place as BP
from chest_lower import fetch, CDN

LINES = {'certifiedish': ('printful_certifiedish', ()), 'signature': ('printful_signature', ()),
         'offworld': ('printful_offworld', ('dtg',)), 'aquatic': ('printful_aquatic', ())}


def sources(only):
    out = []
    for line in only:
        mod, args = LINES[line]
        P = importlib.import_module(mod).plan(*args)
        for u in sorted({f['url'] for p in P for f in p['files'] if f['type'].startswith('back')}):
            name = u.split('/')[-1]
            if name.endswith(BP.SUFFIX + '.png'): name = name[:-len(BP.SUFFIX) - 4] + '.png'
            out.append((line, name))
    return out


def lower(name, out):
    src = Image.open(io.BytesIO(fetch(CDN + name))).convert('RGBA')
    if src.size != (3600, 4800): sys.exit(f'{name}: {src.size}, expected 3600 x 4800')
    im, info = BP.normalize(src)
    path = os.path.join(out, BP.new_name(name)); im.save(path, dpi=(300, 300), optimize=True)
    return path, info


def upload(paths):
    import aquatic_order as AO, time
    ins = [{'filename': os.path.basename(p), 'mimeType': 'image/png', 'httpMethod': 'POST', 'resource': 'IMAGE',
            'fileSize': str(os.path.getsize(p))} for p in paths]
    st = AO.shopify(AO.STAGE_M, {'input': ins})['stagedUploadsCreate']
    if st['userErrors']: sys.exit(f'stagedUploadsCreate: {st["userErrors"]}')
    srcs = []
    for p, t in zip(paths, st['stagedTargets']):
        body, ctype = AO.multipart([(x['name'], x['value']) for x in t['parameters']], p)
        code, r = AO.http('POST', t['url'], {'Content-Type': ctype}, raw=body)
        if code not in (200, 201, 204): sys.exit(f'staged upload {os.path.basename(p)}: {code} {r}')
        srcs.append(t['resourceUrl'])
    files = [{'originalSource': s, 'contentType': 'IMAGE', 'filename': os.path.basename(p),
              'alt': f'{os.path.basename(p)[:-4]} · back, ink top 2 in · 12 x 16 in full-area print master, 300 dpi'}
             for s, p in zip(srcs, paths)]
    fc = AO.shopify(AO.FILE_M, {'files': files})['fileCreate']
    if fc['userErrors']: sys.exit(f'fileCreate: {fc["userErrors"]}')
    ids = [f['id'] for f in fc['files']]
    for _ in range(60):
        nodes = AO.shopify(AO.FILE_Q, {'ids': ids})['nodes']
        if all(n and n['fileStatus'] == 'READY' for n in nodes): return ids, [n['image']['url'] for n in nodes]
        if any(n and n['fileStatus'] == 'FAILED' for n in nodes): sys.exit(f'Shopify file processing failed: {nodes}')
        time.sleep(3)
    sys.exit('Shopify files not READY after 3 minutes; re-run later')


if __name__ == '__main__':
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else 'back-lower'
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else list(LINES)
    os.makedirs(out, exist_ok=True)
    src = sources(only)
    with ThreadPoolExecutor(8) as ex: res = list(ex.map(lambda s: (s[0], *lower(s[1], out)), src))
    for line, p, i in res:
        print(f'{line:12s} {os.path.basename(p)}  top {i["top_from"]:.2f} -> {i["top_to"]:.2f} in · bottom {i["bottom_to"]:.2f} · '
              f'{i["height_in"]:.2f} in tall · scale {i["scale"] * 100:.1f} %', flush=True)
    print(f'\nrendered {len(res)} back masters, ink top {BP.TOP:.2f} in, bottom ≤ {BP.BOTTOM:.2f} in', flush=True)
    if '--upload' in sys.argv:
        paths = [p for _, p, _ in res]; bad = []
        for i in range(0, len(paths), 10):
            ids, urls = upload(paths[i:i + 10])
            for p, fid, u in zip(paths[i:i + 10], ids, urls):
                ok = u.split('?')[0].endswith('/files/' + os.path.basename(p))
                if not ok: bad.append((os.path.basename(p), u))
                print(f'uploaded {os.path.basename(p)}  {fid}{"" if ok else "  <-- NAME CHANGED " + u}', flush=True)
        if bad: sys.exit(f'{len(bad)} files came back under a different name: {bad}')
        print(f'uploaded {len(paths)} files to Shopify Files', flush=True)
