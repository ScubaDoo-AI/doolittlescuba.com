#!/usr/bin/env python3
"""Every shirt mockup on the site and in the store, re-rendered at Printful's full size (Eric, 21 Nov 2026).

Why: the back prints moved to ink top 2 in (tools/back_place.py), so every back mockup was out of date, and Eric asked
for all shirt images at the highest quality. Printful's mockup generator renders up to 2000 px (default 1000, which
is what the site and store had).

Modes (run in Actions: Printful token and Shopify app credentials are repo secrets)

  tools/mockups_hd.py plan  [--only LINES]                  list the site's shirt cards and the Printful variant for each
  tools/mockups_hd.py render --out DIR [--only LINES] [--limit N] [--upload]
        For each card: one mockup task at 2000 px with the files and positions the printful_* plans send (the same
        call as `printful_read.py mockup:<line>:<SKU>`), keeping front, back and side (right). Each image is saved as
        WebP (quality 95, method 6) and, with --upload, put in Shopify Files as
        hd-<card slug>-<line>-<view>.webp. Writes DIR/manifest.json: card key → {front, back, side} CDN URLs.
        Resumable: cards already in an existing DIR/manifest.json are skipped.
  tools/mockups_hd.py site MANIFEST                          write the new URLs into tools/printful_images.json
                                                             (then printful_images.py apply + bust.py)
  tools/mockups_hd.py shopify MANIFEST [--apply]            store products: replace each product's front and back
        mockup photos in place (same media, same position, new image) and add the side view after them.

Lines (site card data-line → Printful plan): certifiedish(-dark), signature plates/dark, offworld(-dark), n73,
aquatic-boat-banter, the five personalized Surface Interval groups (family sample names, renders/aquatic-family),
and the organic tees (org-*; caps excluded). One card = Comfort Colors 1717 / Stanley-Stella STTU169 in size M.
"""
import os, sys, re, json, glob, io, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
WIDTH = 2000
VIEWS = ('front', 'back', 'side')
GROUPS = {'certifiedish': ('certifiedish', 'certifiedish-dark'), 'signature': ('plates', 'dark'), 'offworld': ('offworld', 'offworld-dark'),
          'n73': ('n73',), 'aquatic': ('aquatic-boat-banter', 'aquatic-self-logged', 'aquatic-buddy-check', 'aquatic-buddy-system',
                                       'aquatic-till-surface', 'aquatic-master-class'),
          'organic': ('org-signature', 'org-certifiedish', 'org-offworld', 'org-n73', 'org-aquatic')}


def cards(only=None):
    lines = {l for g, ls in GROUPS.items() if not only or g in only for l in ls}
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)):
        rel = os.path.relpath(p, ROOT)
        if rel.startswith(('shopify-theme', 'renders', 'tools')) or rel == 'index.html': continue
        for f in re.findall(r'<figure class="sh"[^>]*>', open(p, encoding='utf-8').read()):
            a = dict(re.findall(r'\bdata-([a-z]+)="([^"]*)"', f))
            if a.get('line') not in lines or a.get('kind') == 'cap': continue
            spec = spec_for(a['line'], a.get('code', ''))
            if spec: out.append(dict(key=f'{rel}|{a["line"]}|{a.get("slug", "")}', page=rel, line=a['line'], slug=a.get('slug', ''),
                                     code=a.get('code', ''), spec=spec))
    return out


def spec_for(line, code):
    """→ 'mockup:<plan line>:<SKU>' for printful_read.mockup, size M."""
    dark = line.endswith('-dark') or line == 'dark'
    sfx = 'TD' if dark else 'T'
    if line.startswith('certifiedish'): return f'mockup:certifiedish:DS-{code}-{sfx}-M'
    if line in ('plates', 'dark'): return f'mockup:signature:DS-{code}-{sfx}-M'
    if line.startswith('offworld'): return f'mockup:offworld:DS-{code[:2]}{code[2:]}-{sfx}-M'
    if line == 'n73': return f'mockup:n73:DS-{code}-T-M'
    if line == 'aquatic-boat-banter': return f'mockup:aquatic:DS-{code}-TD-M'
    if line.startswith('aquatic-'): return f'mockup:aquaticfamily:DS-{code}-TD-M'
    if line == 'org-aquatic' and not code.startswith('DS-ACS'): return f'mockup:organicfamily:{code}-M'
    if line.startswith('org-'): return f'mockup:organic:{code}-M'
    return None


def pick(res):
    """Printful's task result → {view: image URL}. Front/back: the placement's own mockup, else the extra view of that
    name. Side: the right sleeve's mockup, else the extra 'Right' view, else 'Left'."""
    ms = res['mockups']; extra = {}
    for m in ms:
        for e in m.get('extra', []): extra.setdefault(e.get('title', '').lower(), e.get('url'))
    own = {m.get('placement'): m.get('mockup_url') for m in ms}
    out = {}
    out['front'] = own.get('front') or own.get('default') or extra.get('front')
    out['back'] = own.get('back') or extra.get('back')
    out['side'] = own.get('sleeve_right') or extra.get('right') or extra.get('left')
    if out['back'] and out['back'] == out['front']: out['back'] = extra.get('back')   # a front-only task repeats the front for 'back'
    return {k: v for k, v in out.items() if v}


def fetch(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'doolittle-tools'}), timeout=120) as r: return r.read()
        except Exception as e:
            if k == tries - 1: raise
            time.sleep(4 * (k + 1))


def webp(png_bytes, path):
    from PIL import Image
    im = Image.open(io.BytesIO(png_bytes)); im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
    im.save(path, 'WEBP', quality=95, method=6)
    return im.size


def upload(paths, alts):
    """Shopify Files, ≤10 at a time → CDN URLs (same order). Names are kept; an existing name gets a suffix, so the URL
    is read back rather than guessed."""
    import aquatic_order as AO
    ins = [{'filename': os.path.basename(p), 'mimeType': 'image/webp', 'httpMethod': 'POST', 'resource': 'IMAGE',
            'fileSize': str(os.path.getsize(p))} for p in paths]
    st = AO.shopify(AO.STAGE_M, {'input': ins})['stagedUploadsCreate']
    if st['userErrors']: raise RuntimeError(f'stagedUploadsCreate: {st["userErrors"]}')
    srcs = []
    for p, t in zip(paths, st['stagedTargets']):
        body, ctype = AO.multipart([(x['name'], x['value']) for x in t['parameters']], p)
        code, r = AO.http('POST', t['url'], {'Content-Type': ctype}, raw=body)
        if code not in (200, 201, 204): raise RuntimeError(f'staged upload {os.path.basename(p)}: {code} {r}')
        srcs.append(t['resourceUrl'])
    files = [{'originalSource': s, 'contentType': 'IMAGE', 'filename': os.path.basename(p), 'alt': a} for s, p, a in zip(srcs, paths, alts)]
    fc = AO.shopify(AO.FILE_M, {'files': files})['fileCreate']
    if fc['userErrors']: raise RuntimeError(f'fileCreate: {fc["userErrors"]}')
    ids = [f['id'] for f in fc['files']]
    for _ in range(80):
        nodes = AO.shopify(AO.FILE_Q, {'ids': ids})['nodes']
        if all(n and n['fileStatus'] == 'READY' for n in nodes): return [n['image']['url'] for n in nodes]
        if any(n and n['fileStatus'] == 'FAILED' for n in nodes): raise RuntimeError(f'Shopify file processing failed: {nodes}')
        time.sleep(3)
    raise RuntimeError('Shopify files not READY after 4 minutes')


def render(out, only, limit, do_upload):
    import printful_read as PR
    os.makedirs(out, exist_ok=True); mpath = os.path.join(out, 'manifest.json')
    man = json.load(open(mpath)) if os.path.exists(mpath) else {}
    todo = [c for c in cards(only) if c['key'] not in man]
    if limit: todo = todo[:limit]
    print(f'{len(todo)} cards to render ({len(man)} already done)', flush=True)
    fails = []
    for i, c in enumerate(todo, 1):
        try:
            res = PR.mockup(c['spec'], width=WIDTH, quiet=True)
            if not res: raise RuntimeError('no result')
            urls = pick(res); paths, alts, sizes = [], [], {}
            for v in VIEWS:
                if v not in urls: continue
                name = f'hd-{c["slug"]}-{c["line"]}-{v}.webp'.lower()
                p = os.path.join(out, name); sizes[v] = webp(fetch(urls[v]), p); paths.append(p)
                alts.append(f'{c["slug"]} · {c["line"]} · {v} · Printful mockup, {WIDTH} px')
            entry = {'spec': c['spec'], 'files': {v: os.path.basename(p) for v, p in zip([v for v in VIEWS if v in urls], paths)}, 'size': sizes}
            if do_upload:
                cdn = upload(paths, alts)
                entry['cdn'] = {v: u.split('?')[0] for v, u in zip([v for v in VIEWS if v in urls], cdn)}
            man[c['key']] = entry
            json.dump(man, open(mpath, 'w'), indent=1)
            print(f'[{i}/{len(todo)}] {c["key"]}  {c["spec"]}  ' + ' '.join(f'{v}={sizes[v][0]}x{sizes[v][1]}' for v in sizes), flush=True)
        except BaseException as e:
            if isinstance(e, KeyboardInterrupt): raise
            fails.append((c['key'], repr(e)[:200])); print(f'[{i}/{len(todo)}] {c["key"]}  FAILED {e!r}'[:300], flush=True)
    print(f'\ndone: {len(man)} cards in the manifest, {len(fails)} failed', flush=True)
    for k, e in fails: print('  FAILED', k, e)


def site(mpath):
    """Card images → the new CDN URLs (front/back/sleeve + thumb) in tools/printful_images.json."""
    man = json.load(open(mpath)); dbp = os.path.join(HERE, 'printful_images.json'); db = json.load(open(dbp))
    n = 0
    for key, e in man.items():
        cdn = e.get('cdn') or {}
        if not cdn: continue
        rec = db.setdefault(key, {})
        for v, attr in (('front', 'data-front'), ('back', 'data-back'), ('side', 'data-sleeve')):
            if v in cdn and (attr in rec or v != 'side'): rec[attr] = cdn[v]
        side = rec.get('src', '')   # the card thumb shows the same view as before (back or front), 600 px from the CDN
        view = 'front' if re.search(r'front', side) else 'back'
        if view in cdn: rec['src'] = cdn[view] + '?width=600'
        n += 1
    json.dump(db, open(dbp, 'w'), indent=1, ensure_ascii=False, sort_keys=True)
    print(f'{n} cards updated in {dbp}')


PROD_Q = '''query($q: String!) { productVariants(first: 1, query: $q) { nodes { product { id title
  media(first: 30) { nodes { id alt ... on MediaImage { image { url } } } } } } } }'''
FILES_Q = '''query($q: String!) { files(first: 10, query: $q) { nodes { id alt ... on MediaImage { fileStatus image { url } } } } }'''
UPD_M = '''mutation($files: [FileUpdateInput!]!) { fileUpdate(files: $files) { files { id } userErrors { field message code } } }'''
REORDER_M = '''mutation($id: ID!, $moves: [MoveInput!]!) { productReorderMedia(id: $id, moves: $moves) { job { id } mediaUserErrors { field message } } }'''
VIEW_RE = re.compile(r'/files/[^/?]*?-(front|back)(?:_[0-9a-f-]{36})?\.(?:webp|png|jpe?g)', re.I)


def shopify(mpath, apply):
    """Each card's store product: the old front/back mockup photos are swapped for the 2000 px ones in the same places,
    the side view goes in right after them, everything else (the watermarked art preview) keeps its place."""
    import aquatic_order as AO
    man = json.load(open(mpath)); done = skipped = 0
    for key, e in man.items():
        cdn = e.get('cdn') or {}
        sku = e['spec'].split(':')[2]
        if not cdn: skipped += 1; continue
        nodes = AO.shopify(PROD_Q, {'q': f'sku:{sku}'})['productVariants']['nodes']
        if not nodes: print(f'{key}: no store product for {sku}'); skipped += 1; continue
        prod = nodes[0]['product']; pid = prod['id']; media = prod['media']['nodes']
        new = {}
        for v, url in cdn.items():
            fname = url.rsplit('/', 1)[-1]
            hits = [f for f in AO.shopify(FILES_Q, {'q': f'filename:{fname}'})['files']['nodes'] if f.get('image') and f['image']['url'].split('?')[0].endswith('/' + fname)]
            if hits: new[v] = hits[0]['id']
        if {'front', 'back'} - set(new): print(f'{key}: new files not found in Shopify Files ({sorted(new)})'); skipped += 1; continue
        if any(m['id'] in new.values() for m in media): print(f'{key}: already done'); done += 1; continue
        old = [(m, (VIEW_RE.search((m.get('image') or {}).get('url', '')) or [None, None])[1]) for m in media]
        order, removed, alts = [], [], {}
        last_mock = max([i for i, (_, v) in enumerate(old) if v] or [-1])
        for i, (m, v) in enumerate(old):
            if v and v.lower() in new:
                if new[v.lower()] not in order: order.append(new[v.lower()]); alts[v.lower()] = m.get('alt') or ''
                removed.append(m['id'])   # a second old photo of the same view just goes
            else: order.append(m['id'])
            if i == last_mock and 'side' in new: order.append(new['side'])
        for v in ('back', 'front'):   # a product with no mockup of that view yet: put it first
            if new[v] not in order: order.insert(0, new[v])
        if 'side' in new and new['side'] not in order: order.insert(2, new['side'])
        side_alt = (alts.get('front') or prod['title']).split(':')[0].replace(', front', '').strip() + ', side: the right sleeve (Printful mockup)'
        print(f'{prod["title"]}: replace {len(removed)} mockup photo(s), add {len(new) - len(removed)} → {len(order)} photos', flush=True)
        if not apply: continue
        adds = [{'id': new[v], 'referencesToAdd': [pid], 'alt': alts.get(v) or (side_alt if v == 'side' else f'{prod["title"]}, {v} (Printful mockup)')} for v in new]
        r = AO.shopify(UPD_M, {'files': adds})['fileUpdate']
        if r['userErrors']: print('   add failed:', r['userErrors']); continue
        if removed:
            r = AO.shopify(UPD_M, {'files': [{'id': i, 'referencesToRemove': [pid]} for i in removed]})['fileUpdate']
            if r['userErrors']: print('   remove failed:', r['userErrors'])
        r = AO.shopify(REORDER_M, {'id': pid, 'moves': [{'id': i, 'newPosition': str(n)} for n, i in enumerate(order)]})['productReorderMedia']
        if r['mediaUserErrors']: print('   reorder failed:', r['mediaUserErrors'])
        done += 1
    print(f'\n{done} products {"updated" if apply else "planned"}, {skipped} skipped')


CAP_PRODUCT_SKU = 'DS-MYA-C-SM'
CAP_DESIGN = 'Black Bart front, DS mark on the left side, Do A Little Scuba on the back'


def cap(out, colours, apply):
    """Make it yours cap: Printful mockups at 2000 px of a sample design (the files and threads custom_cap.py sends) in each
    colour, front / side / back, become the product's photos in place of the old one."""
    import printful_read as PR, aquatic_order as AO
    os.makedirs(out, exist_ok=True); paths, alts = [], []
    names = {s: n for s, n in __import__('custom_cap').COLOURS.items()}
    for col in colours:
        res = PR.mockup(f'mockup:customcap:{col}', width=WIDTH, quiet=True)
        own = {m.get('placement'): m.get('mockup_url') for m in res['mockups']}
        own.setdefault('embroidery_front', own.get('embroidery_front_large'))   # Printful's mockup generator only has the large front for the 6277
        for v, pl in (('front', 'embroidery_front'), ('side', 'embroidery_left'), ('back', 'embroidery_back')):
            if not own.get(pl): print(f'{col}: no {pl} mockup'); continue
            name = f'hd-make-it-yours-cap-{col}-{v}.webp'; p = os.path.join(out, name); size = webp(fetch(own[pl]), p)
            paths.append(p); alts.append(f'Make it yours cap in {names[col]} (Flexfit 6277), {v}: {CAP_DESIGN} (Printful mockup)')
            print(f'{name}  {size[0]}x{size[1]}', flush=True)
    if not apply: return
    cdn = [u.split('?')[0] for i in range(0, len(paths), 10) for u in upload(paths[i:i + 10], alts[i:i + 10])]
    prod = AO.shopify(PROD_Q, {'q': f'sku:{CAP_PRODUCT_SKU}'})['productVariants']['nodes'][0]['product']; pid = prod['id']
    new = []
    for u in cdn:
        fname = u.rsplit('/', 1)[-1]
        hit = [f for f in AO.shopify(FILES_Q, {'q': f'filename:{fname}'})['files']['nodes'] if f.get('image') and f['image']['url'].split('?')[0].endswith('/' + fname)]
        new.append(hit[0]['id'])
    old = [m['id'] for m in prod['media']['nodes']]
    r = AO.shopify(UPD_M, {'files': [{'id': i, 'referencesToAdd': [pid], 'alt': a} for i, a in zip(new, alts)]})['fileUpdate']
    if r['userErrors']: sys.exit(f'add: {r["userErrors"]}')
    if old:
        r = AO.shopify(UPD_M, {'files': [{'id': i, 'referencesToRemove': [pid]} for i in old]})['fileUpdate']
        if r['userErrors']: print('remove:', r['userErrors'])
    r = AO.shopify(REORDER_M, {'id': pid, 'moves': [{'id': i, 'newPosition': str(n)} for n, i in enumerate(new)]})['productReorderMedia']
    if r['mediaUserErrors']: print('reorder:', r['mediaUserErrors'])
    print(f'{prod["title"]}: {len(new)} photos at {WIDTH} px, {len(old)} old photo(s) taken off')
    json.dump(dict(zip([os.path.basename(p) for p in paths], cdn)), open(os.path.join(out, 'cap.json'), 'w'), indent=1)


if __name__ == '__main__':
    a = sys.argv[1:]
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    only = opt('--only').split(',') if opt('--only') else None
    if not a: sys.exit(__doc__)
    if a[0] == 'plan':
        C = cards(only)
        for c in C: print(c['key'], c['spec'])
        print(len(C), 'cards')
    elif a[0] == 'render': render(opt('--out', 'mockups-hd'), only, int(opt('--limit', 0)), '--upload' in a)
    elif a[0] == 'site': site(a[1])
    elif a[0] == 'shopify': shopify(a[1], '--apply' in a)
    elif a[0] == 'cap': cap(opt('--out', 'mockups-hd'), (opt('--colours') or 'navy,khaki').split(','), '--apply' in a)
    else: sys.exit(__doc__)
