#!/usr/bin/env python3
"""Move the left-chest lockup on the Signature Series and Certified-ish front masters down to 2 in from the top.

Why: the 13 Nov 2026 sample proof (Black Bart light, size S) showed the chest lockup tight under the collar. Those
front files are full 12 x 16 in masters with the ink at centre 9.5 in / top 0.5 in, about 1.5 in below the collar
seam on the Comfort Colors 1717, and Printful prints the same physical position on every size. Eric (13 Nov):
top 2 in, centre 9.5 in — the same height as the Off-World chest mark.

What it does: downloads each front master from Shopify Files, finds the ink box, moves it straight down so the ink
top sits at 2.00 in (600 px at 300 dpi), leaves x alone (checks the ink centre is 9.5 in, within 0.1 in), and saves
it under a new name with `_top2in` before `.png` — new names so Printful fetches fresh files. Pixels are copied, not
resampled.

  tools/chest_lower.py --out DIR            # render + check only
  tools/chest_lower.py --out DIR --upload   # and upload to Shopify Files (needs SHOPIFY_CLIENT_ID/SECRET)
  ... --only signature | certifiedish

Then: printful_signature.py / printful_certifiedish.py point at the _top2in files; relink with
tools/printful_link.py --only signature,certifiedish --apply --force   (and later --only organic).
"""
import os, sys, io, time, urllib.request
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
DPI = 300
TOP = 2 * DPI            # ink top -> 600 px
CX = 9.5 * DPI           # ink centre x, unchanged -> 2850 px
SUFFIX = '_top2in'


def sources(only):
    out = []
    if 'signature' in only:
        import printful_signature as S
        for code, site, *_ in S.DESIGNS:
            for ink in ('BLACK', 'WHITE'):
                out.append(('signature', f'DS-{code}_{site}_PF-front-leftchest_12x16in_{ink}{S.CHEST_V.get(code, "")}.png'))
    if 'certifiedish' in only:
        for ink in ('BLACK', 'WHITE'):
            out.append(('certifiedish', f'CI-front-leftchest_Certified-ish_12x16in_{ink}.png'))
    return out


def new_name(name): return name[:-4] + SUFFIX + '.png'


def fetch(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'doolittle-tools'}), timeout=60) as r:
                return r.read()
        except Exception as e:
            if k == tries - 1: sys.exit(f'download failed {url}: {e}')
            time.sleep(3 * (k + 1))


def lower(name, out):
    src = Image.open(io.BytesIO(fetch(CDN + name))).convert('RGBA')
    if src.size != (12 * DPI, 16 * DPI): sys.exit(f'{name}: {src.size}, expected 3600 x 4800')
    bb = src.getchannel('A').getbbox()
    if not bb: sys.exit(f'{name}: no ink')
    cx = (bb[0] + bb[2]) / 2
    if abs(cx - CX) > 0.1 * DPI: sys.exit(f'{name}: ink centre {cx / DPI:.2f} in, expected 9.50 in — not a left-chest master?')
    dy = TOP - bb[1]
    if bb[3] + dy > 16 * DPI: sys.exit(f'{name}: moving down {dy} px runs off the area')
    canvas = Image.new('RGBA', src.size, (0, 0, 0, 0))
    canvas.alpha_composite(src.crop(bb), (bb[0], bb[1] + dy))
    nb = canvas.getchannel('A').getbbox()
    if nb != (bb[0], bb[1] + dy, bb[2], bb[3] + dy): sys.exit(f'{name}: moved box {nb} unexpected')
    path = os.path.join(out, new_name(name))
    canvas.save(path, dpi=(DPI, DPI), optimize=True)
    return path, bb, nb


def upload(paths):
    import aquatic_order as AO   # Shopify token exchange + staged upload helpers
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
              'alt': f'{os.path.basename(p)[:-4]} · left-chest front, ink top 2 in / centre 9.5 in · 12 x 16 in full-area print master, 300 dpi'}
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
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else 'chest-lower'
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else ['signature', 'certifiedish']
    os.makedirs(out, exist_ok=True)
    paths = []
    for line, name in sources(only):
        p, bb, nb = lower(name, out); paths.append(p)
        print(f'{os.path.basename(p)}  ink top {bb[1] / DPI:.2f} -> {nb[1] / DPI:.2f} in · centre {(bb[0] + bb[2]) / 2 / DPI:.2f} in · '
              f'{(bb[2] - bb[0]) / DPI:.2f} x {(bb[3] - bb[1]) / DPI:.2f} in', flush=True)
    print(f'\nrendered {len(paths)} front masters, ink top 2.00 in', flush=True)
    if '--upload' in sys.argv:
        bad = []
        for i in range(0, len(paths), 10):
            ids, urls = upload(paths[i:i + 10])
            for p, fid, u in zip(paths[i:i + 10], ids, urls):
                ok = u.split('?')[0].endswith('/files/' + os.path.basename(p))
                if not ok: bad.append((os.path.basename(p), u))
                print(f'uploaded {os.path.basename(p)}  {fid}{"" if ok else "  <-- NAME CHANGED " + u}', flush=True)
        if bad: sys.exit(f'{len(bad)} files came back under a different name: {bad}')
        print(f'uploaded {len(paths)} files to Shopify Files', flush=True)
