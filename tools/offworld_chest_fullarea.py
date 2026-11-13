#!/usr/bin/env python3
"""Off-World Hunt Club: put each 3.5 x 4 in chest mark on a full 12 x 16 in front master, at the wearer's left chest.

Why: the first Off-World sample proof (13 Nov 2026) showed the chest mark centred on the shirt. Printful had stored the
3.5 x 4 in chest file at left 4.25 in / top 6 in, i.e. dead centre, even though tools/printful_offworld.py sends
position top 300 / left 1200 (150-dpi area px). Printful's v1 sync variants keep the file but not the offset, so this
line now does what Signature, Certified-ish, 1N73LL1G3NC3 and Aquatic Comic already do: the front file fills the whole
print area and the art sits inside it where it should print.

Placement (unchanged from the plan): left 8.00 in, top 2.00 in of the 12 x 16 in front area -> 3.75 in right of centre
as you look at the shirt (wearer's left chest), 2 in below the top of the area. At 300 dpi: x 2400 px, y 600 px on a
3600 x 4800 transparent canvas. The chest art itself is copied pixel for pixel (no resampling).

Sources: Shopify Files  OW-<nn>_chest_{light,dark}.png  (1050 x 1200 px, 300 dpi).
Output:  Shopify Files  OW-<nn>_front-leftchest_12x16in_{light,dark}.png  (3600 x 4800 px, 300 dpi, transparent).

  tools/offworld_chest_fullarea.py --out DIR            # render the 60 masters only, check geometry (no upload)
  tools/offworld_chest_fullarea.py --out DIR --upload   # render + upload to Shopify Files (needs SHOPIFY_CLIENT_ID/SECRET)
  ... --only OW03                                       # one design (both inks)

After the upload: tools/printful_link.py --only offworld --apply --force --show  (printful_offworld.py sends the new
front file on the full area).
"""
import os, sys, io, time, urllib.request
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CDN = 'https://cdn.shopify.com/s/files/1/0787/3350/8794/files/'
DPI = 300
AREA = (12 * DPI, 16 * DPI)          # 3600 x 4800
CHEST = (int(3.5 * DPI), 4 * DPI)    # 1050 x 1200
AT = (8 * DPI, 2 * DPI)              # left 8 in, top 2 in -> (2400, 600)
CODES = [f'OW{n:02d}' for n in range(1, 31)]


def front_name(code, tag): return f'OW-{code[2:]}_front-leftchest_12x16in_{tag}.png'


def fetch(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'doolittle-tools'}), timeout=60) as r:
                return r.read()
        except Exception as e:
            if k == tries - 1: sys.exit(f'download failed {url}: {e}')
            time.sleep(3 * (k + 1))


def render(code, tag, out):
    src = Image.open(io.BytesIO(fetch(f'{CDN}OW-{code[2:]}_chest_{tag}.png'))).convert('RGBA')
    if src.size != CHEST: sys.exit(f'{code} {tag}: chest file is {src.size}, expected {CHEST}')
    canvas = Image.new('RGBA', AREA, (0, 0, 0, 0))
    canvas.alpha_composite(src, AT)
    # geometry check: the ink box must land inside the 1050 x 1200 slot at (2400, 600) and nowhere else
    bb, sbb = canvas.getchannel('A').getbbox(), src.getchannel('A').getbbox()
    want = (sbb[0] + AT[0], sbb[1] + AT[1], sbb[2] + AT[0], sbb[3] + AT[1])
    if bb != want: sys.exit(f'{code} {tag}: ink box {bb} != expected {want}')
    path = os.path.join(out, front_name(code, tag))
    canvas.save(path, dpi=(DPI, DPI), optimize=True)
    return path, bb


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
    files = []
    for s, p in zip(srcs, paths):
        n = os.path.basename(p); code = 'OW' + n[3:5]; ink = 'white + red' if n.endswith('_dark.png') else 'black + red'
        files.append({'originalSource': s, 'contentType': 'IMAGE', 'filename': n,
                      'alt': f'Off-World Hunt Club · {code} · front, chest mark on the wearer\'s left chest '
                             f'(left 8 in, top 2 in) · {ink} · 12 x 16 in full-area print master, 300 dpi'})
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
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else 'offworld-front'
    os.makedirs(out, exist_ok=True)
    codes = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else CODES
    paths = []
    for c in codes:
        for tag in ('light', 'dark'):
            p, bb = render(c, tag, out); paths.append(p)
            print(f'{os.path.basename(p)}  ink box {bb}  (slot {AT[0]},{AT[1]} - {AT[0] + CHEST[0]},{AT[1] + CHEST[1]})', flush=True)
    print(f'\nrendered {len(paths)} front masters, 3600 x 4800 @ 300 dpi, chest at left 8 in / top 2 in', flush=True)
    if '--upload' in sys.argv:
        bad = []
        for i in range(0, len(paths), 10):
            ids, urls = upload(paths[i:i + 10])
            for p, fid, u in zip(paths[i:i + 10], ids, urls):
                ok = u.split('?')[0].endswith('/files/' + os.path.basename(p))
                if not ok: bad.append((os.path.basename(p), u))
                print(f'uploaded {os.path.basename(p)}  {fid}  {u.split("?")[0]}{"" if ok else "  <-- NAME CHANGED"}', flush=True)
        if bad: sys.exit(f'{len(bad)} files came back under a different name (an older file with that name exists): {bad}')
        print(f'uploaded {len(paths)} files to Shopify Files', flush=True)
