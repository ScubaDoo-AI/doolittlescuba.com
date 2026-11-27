#!/usr/bin/env python3
"""Every product image on the store's dark background with the DS mark as wallpaper (Eric, 26 Nov 2026:
"All product images should be on a dark themed matching background with the DS mark as wallpaper"; samples approved,
then "update the printful images with the new backgrounds").

The look: store navy #0E1B33 (the theme palette background), small DS marks tiled a few steps lighter (subtle), a soft
light pool behind the product so dark garments still separate, a soft shadow under the product. Same pixel size and
file type as the original.

How each image is treated
  transparent already (the hd- tee mockups, the cap mockups)  → placed straight on the wallpaper
  sticker products (tag sticker/stickers)                      → kept whole as a card (the sheet is the product)
  a photo or close-up that fills the frame (varied border)    → left alone
  a product or design on a plain ground (white or one flat colour) → cut out, then as below
  everything else (white-background Printful mockups)         → cut out with rembg (isnet-general-use), then placed.
        If the cut-out is basically the whole rectangle (art previews, sheets) it is kept whole as a card instead.
        If the cut-out is mostly empty space inside its outline (line art, lettering: a design preview) it is kept
        whole as a card too.
        If the item fills the frame (touches 3+ edges: a close-up) the image is left alone.
        If the cut-out is near empty (< 2 % of the image) the image is left alone and listed in the report.
  already done (corner pixels match the background)            → skipped, so a re-run never processes an image twice

Modes (run in Actions, .github/workflows/dark-bg.yml; the Shopify app credentials are repo secrets)
  inventory                      list every product image (ACTIVE and DRAFT products), one row per file → inventory.json
  run [--apply] [--offset N] [--limit N] [--shard i/n]
        process the images; without --apply nothing is uploaded (previews only). With --apply each new image replaces
        the original in place (fileUpdate originalSource): same file, same products, same position, same alt text.
        Every original is saved under backups/ first (the run's artifact). previews/ holds before|after pairs and
        report.json the outcome of every image.
Undo: put originals from a run's backup artifact in tools/dark_bg_restore/ (file names are the MediaImage ids) and run
      mode restore; it fileUpdates each one back in place.
"""
import argparse, io, json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from PIL import Image, ImageChops, ImageDraw, ImageFilter

BG = (14, 27, 51)            # #0E1B33
TILE = (27, 44, 76)
POOL = (44, 66, 108)
MARK = Image.open(os.path.join(HERE, 'dark_bg_mark.png')).split()[-1]   # alpha of the DS mark


# ---------- look ----------
def wallpaper(w, h):
    bg = Image.new('RGB', (w, h), BG)
    size = max(24, int(w * 0.075))
    m = MARK.resize((size, int(size * MARK.height / MARK.width)), Image.LANCZOS)
    fill = Image.new('RGB', m.size, TILE)
    sx, sy = int(size * 2.3), int(m.height * 2.1)
    for r, y in enumerate(range(-m.height, h + m.height, sy)):
        off = (sx // 2) if r % 2 else 0
        for x in range(-size + off, w + size, sx):
            bg.paste(fill, (x, y), m)
    g = Image.new('L', (w, h), 0); rr = int(w * 0.36)
    ImageDraw.Draw(g).ellipse((w // 2 - rr, h // 2 - rr, w // 2 + rr, h // 2 + rr), fill=255)
    g = g.filter(ImageFilter.GaussianBlur(w * 0.12)).point(lambda v: int(v * 0.55))
    return Image.composite(Image.new('RGB', (w, h), POOL), bg, g)


def place(product, w, h):
    """product: RGBA, already the canvas size, transparent around the item."""
    bg = wallpaper(w, h).convert('RGBA')
    a = product.split()[-1]
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: 150 if v > 40 else 0))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(w * .015)), (int(w * .006), int(h * .012)))
    bg.alpha_composite(product)
    return bg.convert('RGB')


def card(im, w, h):
    bg = wallpaper(w, h).convert('RGBA')
    p = im.convert('RGBA').resize((int(w * .86), int(h * .86)), Image.LANCZOS)
    x, y = (w - p.width) // 2, (h - p.height) // 2
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh.paste(Image.new('RGBA', p.size, (0, 0, 0, 150)), (x + int(w * .008), y + int(h * .012)))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(w * .012)))
    bg.alpha_composite(p, (x, y))
    return bg.convert('RGB')


def done_already(im):
    """True when the border is the wallpaper (background or mark colour) all round: this image was converted before."""
    rgb = im.convert('RGB'); w, h = rgb.size
    pts = [(int(w * f), y) for f in (0.02, 0.2, 0.4, 0.6, 0.8, 0.98) for y in (2, h - 3)] + \
          [(x, int(h * f)) for f in (0.2, 0.4, 0.6, 0.8) for x in (2, w - 3)]
    near = lambda p, c: max(abs(p[i] - c[i]) for i in range(3)) <= 12
    hits = sum(1 for q in pts if near(rgb.getpixel(q), BG) or near(rgb.getpixel(q), TILE))
    return hits >= len(pts) - 2


def border_kind(im):
    """'white' or 'plain' (one flat ground: cut it out) or 'photo' (a varied border: a close-up or a photo)."""
    rgb = im.convert('RGB'); w, h = rgb.size
    pts = [(int(w * f / 20), y) for f in range(1, 20) for y in (1, h - 2)] + [(x, int(h * f / 20)) for f in range(1, 20) for x in (1, w - 2)]
    px = [rgb.getpixel(q) for q in pts]
    if sum(1 for p in px if min(p) >= 225) >= 0.5 * len(px): return 'white'
    mean = [sum(p[i] for p in px) / len(px) for i in range(3)]
    spread = max((sum((p[i] - mean[i]) ** 2 for p in px) / len(px)) ** 0.5 for i in range(3))
    return 'plain' if spread < 12 else 'photo'


_SESSION = {}


def cutout(im):
    from rembg import remove, new_session
    if 's' not in _SESSION: _SESSION['s'] = new_session('isnet-general-use')
    cut = remove(im.convert('RGB'), session=_SESSION['s']).convert('RGBA')
    # fill enclosed holes (a white sticker centre, the inside of a collar): a physical product has none
    # (only large ones: a towel's hanging ring or a grommet stays see-through)
    import numpy as np
    from scipy.ndimage import binary_fill_holes, label
    a = np.array(cut.split()[-1]); holes = binary_fill_holes(a > 128) & (a <= 128)
    lab, n = label(holes)
    if n:
        sizes = np.bincount(lab.ravel()); big = [i for i in range(1, n + 1) if sizes[i] > 0.015 * a.size]
        if big:
            a = np.where(np.isin(lab, big), 255, a).astype('uint8')
        rgb = np.array(im.convert('RGB')); cut = Image.fromarray(np.dstack([rgb, a]), 'RGBA')
    return cut


def transform(im, tags):
    """→ (new RGB image or None, method)"""
    w, h = im.size
    if done_already(im): return None, 'already'
    if 'sticker' in tags or 'stickers' in tags: return card(im, w, h), 'card'
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        rgba = im.convert('RGBA')
        if rgba.split()[-1].getextrema()[0] < 20:            # real transparency around the item
            return place(rgba, w, h), 'transparent'
    kind = border_kind(im)
    if kind == 'photo': return None, 'skip-fullbleed'          # a close-up or a photo that fills the frame: leave it
    cut = cutout(im)
    a = cut.split()[-1]
    hist = a.histogram(); cover = sum(hist[128:]) / float(w * h)
    if cover < 0.02: return None, 'skip-empty-cutout'
    bb = a.point(lambda v: 255 if v > 128 else 0).getbbox()
    if bb:
        edges = sum((bb[0] <= 2, bb[1] <= 2, bb[2] >= w - 3, bb[3] >= h - 3))
        if edges >= 3 and cover > 0.6:
            return None, 'skip-fullbleed'                      # a close-up that fills the frame: leave it as it is
        bw, bh = bb[2] - bb[0], bb[3] - bb[1]
        density = cover / max(1e-6, (bw * bh) / float(w * h))
        if density > 0.93 and bw * bh > 0.8 * w * h:
            return card(im, w, h), 'card'                      # the item is a rectangle: an art preview or a sheet
        if density < 0.45:
            return card(im, w, h), 'card-art'                  # line art or lettering (a design preview): keep it whole
    return place(cut, w, h), 'cutout'


# ---------- store ----------
def AO():
    import importlib.util as u
    s = u.spec_from_file_location('aquatic_order', os.path.join(HERE, 'aquatic_order.py')); m = u.module_from_spec(s); s.loader.exec_module(m)
    return m


INV_Q = '''query($after: String) { products(first: 50, after: $after, query: "status:active OR status:draft") {
  pageInfo { hasNextPage endCursor }
  nodes { id handle status tags media(first: 40) { nodes { ... on MediaImage { id image { url width height } } } } } } }'''
UPD_M = '''mutation($files: [FileUpdateInput!]!) { fileUpdate(files: $files) { files { id } userErrors { field message code } } }'''
FILE_Q = '''query($ids: [ID!]!) { nodes(ids: $ids) { ... on MediaImage { id fileStatus image { url } } } }'''
STAGE_M = '''mutation($input: [StagedUploadInput!]!) { stagedUploadsCreate(input: $input) {
  stagedTargets { url resourceUrl parameters { name value } } userErrors { field message } } }'''


def inventory(ao):
    rows, seen, after = [], set(), None
    while True:
        d = ao.shopify(INV_Q, {'after': after})['products']
        for p in d['nodes']:
            for m in p['media']['nodes']:
                if not m or not m.get('image') or m['id'] in seen: continue
                seen.add(m['id'])
                rows.append({'id': m['id'], 'url': m['image']['url'], 'w': m['image']['width'], 'h': m['image']['height'],
                             'product': p['handle'], 'status': p['status'], 'tags': p['tags']})
        if not d['pageInfo']['hasNextPage']: break
        after = d['pageInfo']['endCursor']
    return rows


def ext_of(url):
    path = url.split('?')[0].lower()
    for e, fmt, mime in (('.jpg', 'JPEG', 'image/jpeg'), ('.jpeg', 'JPEG', 'image/jpeg'), ('.png', 'PNG', 'image/png'), ('.webp', 'WEBP', 'image/webp')):
        if path.endswith(e): return e, fmt, mime
    return '.jpg', 'JPEG', 'image/jpeg'


def save(img, fmt):
    b = io.BytesIO()
    if fmt == 'JPEG': img.save(b, 'JPEG', quality=90, optimize=True)
    elif fmt == 'WEBP': img.save(b, 'WEBP', quality=90, method=6)
    else: img.save(b, 'PNG', optimize=True)
    return b.getvalue()


def replace(ao, items):
    """items: [(media id, filename, bytes, mime)] → upload and fileUpdate in place; waits for READY."""
    ins = [{'filename': fn, 'mimeType': mime, 'httpMethod': 'POST', 'resource': 'IMAGE', 'fileSize': str(len(b))} for _, fn, b, mime in items]
    st = ao.shopify(STAGE_M, {'input': ins})['stagedUploadsCreate']
    if st['userErrors']: raise RuntimeError(f'stagedUploadsCreate: {st["userErrors"]}')
    ups = []
    for (mid, fn, b, mime), t in zip(items, st['stagedTargets']):
        tmp = f'/tmp/{fn}'; open(tmp, 'wb').write(b)
        body, ctype = ao.multipart([(x['name'], x['value']) for x in t['parameters']], tmp)
        body = body.replace(b'Content-Type: image/png\r\n', f'Content-Type: {mime}\r\n'.encode(), 1)
        code, r = ao.http('POST', t['url'], {'Content-Type': ctype}, raw=body)
        if code not in (200, 201, 204): raise RuntimeError(f'staged upload {fn}: {code} {str(r)[:200]}')
        ups.append({'id': mid, 'originalSource': t['resourceUrl']})
    r = ao.shopify(UPD_M, {'files': ups})['fileUpdate']
    if r['userErrors']: raise RuntimeError(f'fileUpdate: {r["userErrors"]}')
    ids = [u['id'] for u in ups]
    for _ in range(60):
        nodes = ao.shopify(FILE_Q, {'ids': ids})['nodes']
        if all(n and n['fileStatus'] == 'READY' for n in nodes): return
        if any(n and n['fileStatus'] == 'FAILED' for n in nodes): raise RuntimeError(f'processing failed: {[n["id"] for n in nodes if n["fileStatus"] == "FAILED"]}')
        time.sleep(3)
    raise RuntimeError('files not READY after 3 minutes')


def fetch(url):
    for k in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r: return r.read()
        except Exception:
            if k == 3: raise
            time.sleep(5 * (k + 1))


def run(ao, rows, apply, out):
    for d in ('backups', 'previews'): os.makedirs(os.path.join(out, d), exist_ok=True)
    report, batch = [], []

    def flush():
        if not batch: return
        try:
            replace(ao, batch)
            for mid, *_ in batch: next(r for r in report if r['id'] == mid)['replaced'] = True
        except Exception as e:
            for mid, *_ in batch: next(r for r in report if r['id'] == mid)['error'] = str(e)[:300]
            print('  batch failed:', e)
        batch.clear()

    for i, row in enumerate(rows):
        rec = {'id': row['id'], 'product': row['product'], 'url': row['url']}; report.append(rec)
        try:
            raw = fetch(row['url'])
            im = Image.open(io.BytesIO(raw)); im.load()
            new, how = transform(im, row['tags'])
            rec['method'] = how
            if new is None: continue
            nid = row['id'].rsplit('/', 1)[-1]
            e, fmt, mime = ext_of(row['url'])
            open(os.path.join(out, 'backups', nid + e), 'wb').write(raw)
            pv = Image.new('RGB', (640, 320)); pv.paste(im.convert('RGB').resize((320, 320)), (0, 0)); pv.paste(new.resize((320, 320)), (320, 0))
            pv.save(os.path.join(out, 'previews', f'{row["product"][:60]}-{nid}.jpg'), quality=80)
            if apply:
                fn = os.path.basename(row['url'].split('?')[0])
                batch.append((row['id'], fn, save(new, fmt), mime))
                if len(batch) >= 10: flush()
        except Exception as ex:
            rec['error'] = str(ex)[:300]
        if i % 25 == 0: print(f'{i + 1}/{len(rows)}', row['product'], rec.get('method'), flush=True)
    flush()
    json.dump(report, open(os.path.join(out, 'report.json'), 'w'), indent=1)
    from collections import Counter
    print('methods:', dict(Counter(r.get('method', 'error') for r in report)),
          '| replaced:', sum(1 for r in report if r.get('replaced')), '| errors:', sum(1 for r in report if r.get('error')))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['inventory', 'run', 'restore'])
    ap.add_argument('--dir', default=os.path.join(HERE, 'dark_bg_restore'), help='restore: originals named <MediaImage id>.<ext>')
    ap.add_argument('--apply', action='store_true'); ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--limit', type=int, default=0); ap.add_argument('--shard', default='0/1')
    ap.add_argument('--only', default='', help='comma-separated product handles'); ap.add_argument('--out', default='dark-bg-out')
    a = ap.parse_args()
    ao = AO()
    if a.mode == 'restore':
        mimes = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}
        for f in sorted(os.listdir(a.dir)):
            stem, e = os.path.splitext(f)
            if e.lower() not in mimes: continue
            replace(ao, [(f'gid://shopify/MediaImage/{stem}', f, open(os.path.join(a.dir, f), 'rb').read(), mimes[e.lower()])])
            print('restored', f)
        return
    rows = inventory(ao)
    os.makedirs(a.out, exist_ok=True)
    json.dump(rows, open(os.path.join(a.out, 'inventory.json'), 'w'), indent=1)
    print(len(rows), 'images on', len({r['product'] for r in rows}), 'products')
    if a.mode == 'inventory': return
    if a.only: rows = [r for r in rows if r['product'] in set(a.only.split(','))]
    k, n = (int(x) for x in a.shard.split('/'))
    rows = [r for j, r in enumerate(rows) if j % n == k]
    rows = rows[a.offset:]
    if a.limit: rows = rows[:a.limit]
    print('processing', len(rows), 'images', '(apply)' if a.apply else '(dry run)')
    run(ao, rows, a.apply, a.out)


if __name__ == '__main__':
    main()
