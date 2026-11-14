#!/usr/bin/env python3
"""Personalized Aquatic Comic order → Printful, in one step (Printful API v2, beta).

For the 39 name tees (Self-Logged W, Buddy Check R, Buddy System B, Till Surface Do Us Part C, Master Class M).
Each run does the following:

  1. Read the Shopify order. Pick out the personalized lines (SKU DS-AC[WRBCM]nn-TD-<size>) and the names the
     product page collected as line-item properties: "Name on the shirt", "Diver 1" / "Diver 2", "Husband" / "Wife".
  2. Render each shirt's front and back with tools/aquatic_print.py. The masters are 3600 x 4800 at 300 dpi, the
     full 12 x 16 in area.
  3. Upload the PNGs to Shopify Files. Printful only takes print files by URL, and this gives them a CDN URL.
  4. Create a Printful v2 order: Comfort Colors 1717 in the design's colour and size, front + back DTG at full area,
     shipped to the Shopify customer, with external_id = the Shopify order number. Printful creates it as a DRAFT,
     and the script prints Printful's costs.
  5. With --confirm, also confirm it, which starts production and charges the card on file. Leave that off until
     the first draft has been checked in the Printful dashboard.

Boat Banter (S01–S20) lines are skipped. Printful's Shopify sync fulfils those on its own once linked
(tools/printful_link.py --only aquatic).

Usage
  tools/aquatic_order.py 1001                    # Shopify order #1001 → render, upload, Printful draft
  tools/aquatic_order.py 1001 --dry-run          # render and show the names / variants / payload; no upload, no Printful
  tools/aquatic_order.py 1001 --confirm          # …and confirm the Printful order straight away
  tools/aquatic_order.py --confirm-id 123456789  # confirm a draft you have checked (no new order)
  tools/aquatic_order.py --code W03 --size L --name Sam --to recipient.json
                                                 # without a Shopify order (gift, replacement); recipient.json = Printful address
  tools/aquatic_order.py --code C02 --size M --name Mike --name2 Lisa --to recipient.json

Environment (never written to disk by this script)
  SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET
                   from a Dev Dashboard app (dev.shopify.com) installed on the store, scopes read_orders + write_files.
                   The script trades them for a 24-hour Admin token (client credentials grant). This replaces
                   legacy custom-app tokens, which Shopify stopped issuing on 1 Jan 2026.
  SHOPIFY_TOKEN    alternatively, an Admin API access token you already have
  SHOPIFY_STORE    x00ytr-y9.myshopify.com (default)
  PRINTFUL_TOKEN   Printful private token, scope orders (+ files)
  PRINTFUL_STORE   18960047 (default)

Once per store: leave the 39 personalized products' Printful sync variants IGNORED. Otherwise Printful's Shopify
import holds every name order as "needs attention". Run tools/printful_link.py --only aquatic --apply, which ignores them.
"""
import os, sys, json, re, time, tempfile, urllib.request, urllib.error, mimetypes, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aquatic_print as AP
import printful_aquatic as PA

D = AP.D
BY_CODE = {d['code']: d for d in D['designs']}
SHOP = os.environ.get('SHOPIFY_STORE', 'x00ytr-y9.myshopify.com')
API_VER = '2026-10'
PF_STORE = os.environ.get('PRINTFUL_STORE', '18960047')
SKU_RE = re.compile(r'^DS-AC([WRBCM]\d\d)-TD(O?)-(S|M|L|XL|2XL|3XL)$')   # TDO = the organic edition (Stanley/Stella STTU169, tools/organic.py)
FULL_AREA = {'top': 0, 'left': 0, 'width': 12, 'height': 16}          # inches, Printful v2 LayerPosition


# ---------- HTTP ----------
def http(method, url, headers=None, body=None, raw=None, tries=4):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    for k in range(tries):
        req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                txt = r.read().decode() or '{}'
                return r.status, (json.loads(txt) if txt.strip().startswith(('{', '[')) else txt)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:800]
            if e.code == 429 and k < tries - 1: time.sleep(20 * (k + 1)); continue
            return e.code, msg


_TOK = {}


def shopify_token():
    if os.environ.get('SHOPIFY_TOKEN'): return os.environ['SHOPIFY_TOKEN']
    cid, sec = os.environ.get('SHOPIFY_CLIENT_ID'), os.environ.get('SHOPIFY_CLIENT_SECRET')
    if not (cid and sec): sys.exit('set SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET (Dev Dashboard app) or SHOPIFY_TOKEN')
    if 'tok' not in _TOK:
        import urllib.parse
        code, r = http('POST', f'https://{SHOP}/admin/oauth/access_token', {'Content-Type': 'application/x-www-form-urlencoded'},
                       raw=urllib.parse.urlencode({'grant_type': 'client_credentials', 'client_id': cid, 'client_secret': sec}).encode())
        if code != 200 or not isinstance(r, dict) or 'access_token' not in r: sys.exit(f'Shopify token exchange failed: {code} {r}')
        _TOK['tok'] = r['access_token']
    return _TOK['tok']


def shopify(query, variables=None):
    tok = shopify_token()
    code, r = http('POST', f'https://{SHOP}/admin/api/{API_VER}/graphql.json',
                   {'X-Shopify-Access-Token': tok, 'Content-Type': 'application/json'}, {'query': query, 'variables': variables or {}})
    if code != 200 or not isinstance(r, dict) or r.get('errors'): sys.exit(f'Shopify {code}: {r}')
    return r['data']


def printful(method, path, body=None):
    tok = os.environ.get('PRINTFUL_TOKEN') or sys.exit('PRINTFUL_TOKEN not set')
    code, r = http(method, 'https://api.printful.com' + path,
                   {'Authorization': 'Bearer ' + tok, 'X-PF-Store-Id': PF_STORE, 'Content-Type': 'application/json'}, body)
    if code >= 300: sys.exit(f'Printful {method} {path}: {code} {r}')
    return r


# ---------- Shopify order → shirts ----------
ORDER_Q = '''query($q: String!) { orders(first: 1, query: $q) { nodes {
  id name email
  shippingAddress { name company address1 address2 city provinceCode province countryCodeV2 country zip phone }
  lineItems(first: 50) { nodes { id sku quantity name customAttributes { key value } } } } } }'''


def names_from(code, attrs):
    a = {x['key'].strip().lower(): (x['value'] or '').strip() for x in attrs}
    n = BY_CODE[code]['names']
    if n == 1: return [a.get('name on the shirt', '')]
    if code[0] == 'B': return [a.get('diver 1', ''), a.get('diver 2', '')]
    return [a.get('husband', ''), a.get('wife', '')]


def from_shopify(number):
    q = f'name:"#{str(number).lstrip("#")}"'
    nodes = shopify(ORDER_Q, {'q': q})['orders']['nodes']
    if not nodes: sys.exit(f'no Shopify order {q}')
    o = nodes[0]; s = o['shippingAddress'] or sys.exit(f'order {o["name"]} has no shipping address')
    recipient = {k: v for k, v in dict(name=s['name'], company=s['company'], address1=s['address1'], address2=s['address2'],
                                        city=s['city'], state_code=s['provinceCode'], country_code=s['countryCodeV2'],
                                        zip=s['zip'], phone=s['phone'], email=o['email']).items() if v}
    shirts, skipped = [], []
    for li in o['lineItems']['nodes']:
        m = SKU_RE.match(li['sku'] or '')
        if not m: skipped.append(li['sku'] or li['name']); continue
        code, organic, size = m.groups()
        shirts.append(dict(code=code, size=size, organic=bool(organic), qty=li['quantity'], names=names_from(code, li['customAttributes']),
                           external_id=li['id'].rsplit('/', 1)[-1]))
    return o['name'], recipient, shirts, skipped


# ---------- render ----------
def render(shirt, out):
    d = BY_CODE[shirt['code']]
    n1, n2 = (shirt['names'] + ['', ''])[:2]
    if not n1 or (d['names'] == 2 and not n2):
        sys.exit(f'{shirt["code"]}: missing name(s) on the order line {shirt["names"]}. Ask the customer, then use --code mode')
    nm = AP.names_for(d, n1, n2 or None)                      # cleans quotes, enforces 12 / 10 characters
    tag = '_' + '-'.join(re.sub(r'[^A-Za-z0-9]+', '', v) for v in nm.values())
    AP.build(d, out, nm, tag)
    stem = f'{out}/AC-{d["code"]}{tag}'
    return nm, f'{stem}_front.png', f'{stem}_back.png'


# ---------- Shopify Files ----------
STAGE_M = '''mutation($input: [StagedUploadInput!]!) { stagedUploadsCreate(input: $input) {
  stagedTargets { url resourceUrl parameters { name value } } userErrors { field message } } }'''
FILE_M = '''mutation($files: [FileCreateInput!]!) { fileCreate(files: $files) { files { id } userErrors { field message } } }'''
FILE_Q = '''query($ids: [ID!]!) { nodes(ids: $ids) { ... on MediaImage { id fileStatus image { url } } } }'''


def multipart(fields, path):
    b = uuid.uuid4().hex; out = b''
    for k, v in fields:
        out += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    out += (f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{os.path.basename(path)}"\r\n'
            f'Content-Type: image/png\r\n\r\n').encode() + open(path, 'rb').read() + f'\r\n--{b}--\r\n'.encode()
    return out, f'multipart/form-data; boundary={b}'


def upload(paths, label):
    ins = [{'filename': os.path.basename(p), 'mimeType': 'image/png', 'httpMethod': 'POST', 'resource': 'IMAGE',
            'fileSize': str(os.path.getsize(p))} for p in paths]
    st = shopify(STAGE_M, {'input': ins})['stagedUploadsCreate']
    if st['userErrors']: sys.exit(f'stagedUploadsCreate: {st["userErrors"]}')
    srcs = []
    for p, t in zip(paths, st['stagedTargets']):
        body, ctype = multipart([(x['name'], x['value']) for x in t['parameters']], p)
        code, r = http('POST', t['url'], {'Content-Type': ctype}, raw=body)
        if code not in (200, 201, 204): sys.exit(f'staged upload {os.path.basename(p)}: {code} {r}')
        srcs.append(t['resourceUrl'])
    fc = shopify(FILE_M, {'files': [{'originalSource': s, 'contentType': 'IMAGE', 'filename': os.path.basename(p),
                                     'alt': f'Custom print · {label} · {os.path.basename(p)}'} for s, p in zip(srcs, paths)]})['fileCreate']
    if fc['userErrors']: sys.exit(f'fileCreate: {fc["userErrors"]}')
    ids = [f['id'] for f in fc['files']]
    for _ in range(40):                                       # wait for Shopify to process (usually < 10 s)
        nodes = shopify(FILE_Q, {'ids': ids})['nodes']
        if all(n and n['fileStatus'] == 'READY' for n in nodes): return [n['image']['url'] for n in nodes]
        if any(n and n['fileStatus'] == 'FAILED' for n in nodes): sys.exit(f'Shopify file processing failed: {nodes}')
        time.sleep(3)
    sys.exit('Shopify files not READY after 2 minutes; re-run later')


# ---------- Printful ----------
def item(shirt, front_url, back_url):
    d = BY_CODE[shirt['code']]
    v = next(x for x in PA.plan(all_designs=True) if x['code'] == shirt['code'])['variants']
    var = next(x for x in v if x['size'] == shirt['size'])
    if shirt.get('organic'):   # same files and price, organic blank: the STTU169 variant from tools/organic.py
        import importlib.util as _u
        _s = _u.spec_from_file_location('organic', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'organic.py'))
        _m = _u.module_from_spec(_s); _s.loader.exec_module(_m)
        o = next(x for x in _m.tee_plans() if x['line'] == 'aquatic' and x['regular_key'] == f'DS-AC{shirt["code"]}-TD')
        var = dict(var, variant_id=next(x for x in o['variants'] if x['size'] == shirt['size'])['variant_id'])
    it = {'source': 'catalog', 'catalog_variant_id': var['variant_id'], 'quantity': shirt.get('qty', 1),
          'name': f'Aquatic Comic {shirt["code"]}{" organic" if shirt.get("organic") else ""} {d["name"]} ({" & ".join(shirt["names"])}) {shirt["size"]}',
          'retail_price': f'{var["price"]:.2f}',
          'placements': [{'placement': 'front', 'technique': 'dtg', 'layers': [{'type': 'file', 'url': front_url, 'position': FULL_AREA}]},
                         {'placement': 'back', 'technique': 'dtg', 'layers': [{'type': 'file', 'url': back_url, 'position': FULL_AREA}]}]}
    if shirt.get('external_id'): it['external_id'] = shirt['external_id']
    return it


def main():
    a = sys.argv[1:]
    def opt(k): return a[a.index(k) + 1] if k in a else None
    dry, confirm = '--dry-run' in a, '--confirm' in a
    if opt('--confirm-id'):
        printful('POST', f'/v2/orders/{opt("--confirm-id")}/confirmation'); print('confirmed: in production'); return
    if opt('--code'):
        code = opt('--code').upper()
        if code not in BY_CODE or BY_CODE[code]['names'] == 0: sys.exit(f'{code} is not a personalized Aquatic Comic design')
        to = opt('--to') or sys.exit('--to recipient.json is required in --code mode')
        label, recipient = opt('--ref') or f'manual-{code}', json.load(open(to))
        shirts, skipped = [dict(code=code, size=(opt('--size') or 'L').upper(), qty=int(opt('--qty') or 1),
                                names=[x for x in (opt('--name'), opt('--name2')) if x])], []
    else:
        num = next((x for x in a if not x.startswith('--') and re.fullmatch(r'#?\d+', x)), None) or sys.exit(__doc__)
        label, recipient, shirts, skipped = from_shopify(num)
    if skipped: print('not personalized Aquatic Comic, left to Printful sync:', ', '.join(skipped))
    if not shirts: sys.exit(f'{label}: no personalized Aquatic Comic lines')
    out = opt('--out') or os.path.join(tempfile.gettempdir(), 'aquatic_orders', re.sub(r'[^A-Za-z0-9]+', '', label))
    items = []
    for s in shirts:
        nm, fp, bp = render(s, out)
        s['names'] = list(nm.values())
        print(f'{s["code"]} {BY_CODE[s["code"]]["name"]:16s} {s["size"]:3s} x{s.get("qty", 1)}  {" & ".join(s["names"]):24s} → {fp}')
        if dry: items.append(item(s, 'file://' + fp, 'file://' + bp)); continue
        fu, bu = upload([fp, bp], label)
        items.append(item(s, fu, bu))
    order = {'external_id': re.sub(r'[^A-Za-z0-9_-]', '', label)[:32], 'shipping': opt('--shipping') or 'STANDARD',
             'recipient': recipient, 'order_items': items,
             'customization': {'packing_slip': {'store_name': 'Doolittle Scuba', 'custom_order_id': label}}}
    if dry:
        print(json.dumps(order, indent=1, ensure_ascii=False)); print('\ndry run: nothing uploaded, no Printful order'); return
    r = printful('POST', '/v2/orders', order)['data']
    oid = r['id']; print(f'Printful order {oid} created ({r["status"]}), external_id {order["external_id"]}')
    for _ in range(20):                                       # Printful calculates costs asynchronously
        c = printful('GET', f'/v2/orders/{oid}')['data']['costs']
        if c.get('calculation_status') == 'done': break
        time.sleep(3)
    print(f'Printful costs: subtotal {c.get("subtotal")} · shipping {c.get("shipping")} · tax {c.get("tax")} · total {c.get("total")} {c.get("currency")}'
          f' ({c.get("calculation_status")})')
    if confirm:
        printful('POST', f'/v2/orders/{oid}/confirmation'); print('confirmed: in production')
    else:
        print(f'draft only. Check it at https://www.printful.com/dashboard/default/orders, then confirm there or run --confirm-id {oid}')


if __name__ == '__main__':
    main()
