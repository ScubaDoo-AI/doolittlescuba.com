#!/usr/bin/env python3
"""Custom orders → Printful drafts, automatically (GitHub "Custom orders", every 15 minutes).

Each run:
  1. Reads the store's paid orders from the last few days (Doolittle Order Bot app, read_orders).
  2. Picks out the custom lines:
       Make it yours tee   SKU DS-MY[AB]-T-<size>, the design in the line property _design (set by /custom/'s Add to cart)
     (personalized Aquatic tees and the Make it yours cap join this job one at a time; see CUSTOM-ORDERS.md)
  3. Skips any order Printful already has (external_id MY<order number>), so a run can repeat safely.
  4. Builds the print files with tools/custom_tee.py, uploads them to Shopify Files (Printful takes files by URL),
     and creates a Printful order as a DRAFT: nothing prints and nothing is charged until Eric confirms it
     (Printful dashboard, or the job with "confirm" + the Printful id).
  5. HOLDS an order instead when a person is needed (a logo, Home Port, a design the page didn't offer, a missing
     _design): nothing goes to Printful, the reason is reported.
  Writes custom_orders.json (what happened per order) for the workflow to open one GitHub issue per draft or hold.

  tools/custom_order.py                  # look at the last 3 days, draft what is new
  tools/custom_order.py --days 7 --dry   # render + report only: no upload, no Printful
  tools/custom_order.py --order 1001     # just this order (even if older)
  tools/custom_order.py --confirm 123456 # confirm a checked Printful draft (starts production, charges the card)
Environment: SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET (or SHOPIFY_TOKEN), PRINTFUL_TOKEN.
"""
import os, sys, re, json, time, tempfile, datetime

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import aquatic_order as AO
import custom_tee as T

MY_RE = re.compile(r'^DS-MY([AB])-T-(S|M|L|XL|2XL|3XL)$')
AREA = {'front': (12, 16), 'back': (12, 16), 'sleeve_left': (3.5, 4), 'sleeve_right': (3.5, 4)}

ORDERS_Q = '''query($q: String!, $a: String) { orders(first: 50, after: $a, query: $q, sortKey: CREATED_AT, reverse: true) {
  pageInfo { hasNextPage endCursor }
  nodes { id name createdAt displayFinancialStatus cancelledAt email
    shippingAddress { name company address1 address2 city provinceCode countryCodeV2 zip phone }
    lineItems(first: 50) { nodes { id sku quantity name originalUnitPriceSet { shopMoney { amount } } customAttributes { key value } } } } } }'''


def pf_get(path):
    """Printful GET that returns None on 404 instead of exiting (to test whether an order exists)."""
    tok = os.environ.get('PRINTFUL_TOKEN') or sys.exit('PRINTFUL_TOKEN not set')
    code, r = AO.http('GET', 'https://api.printful.com' + path, {'Authorization': 'Bearer ' + tok, 'X-PF-Store-Id': AO.PF_STORE})
    return None if code == 404 else r if code < 300 else sys.exit(f'Printful GET {path}: {code} {r}')


def orders(days, number=None):
    if number: q = f'name:"#{str(number).lstrip("#")}"'
    else: q = f'created_at:>={(datetime.datetime.utcnow() - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")}'
    out, a = [], None
    while True:
        r = AO.shopify(ORDERS_Q, {'q': q, 'a': a})['orders']; out += r['nodes']
        if not r['pageInfo']['hasNextPage']: return out
        a = r['pageInfo']['endCursor']


def custom_lines(o):
    L = []
    for li in o['lineItems']['nodes']:
        m = MY_RE.match(li['sku'] or '')
        if not m: continue
        attrs = {x['key']: x['value'] for x in li['customAttributes']}
        L.append(dict(kind='myt', tier=m.group(1), size=m.group(2), qty=li['quantity'], design=attrs.get('_design', ''),
                      mockup=attrs.get('Mockup', ''), price=li['originalUnitPriceSet']['shopMoney']['amount'],
                      line_id=li['id'].rsplit('/', 1)[-1], name=li['name']))
    return L


def recipient(o):
    s = o['shippingAddress'] or {}
    r = {k: v for k, v in dict(name=s.get('name'), company=s.get('company'), address1=s.get('address1'), address2=s.get('address2'),
                                city=s.get('city'), state_code=s.get('provinceCode'), country_code=s.get('countryCodeV2'),
                                zip=s.get('zip'), phone=s.get('phone'), email=o.get('email')).items() if v}
    return r if r.get('address1') and r.get('country_code') else None


def handle(o, dry):
    ext = 'MY' + re.sub(r'\D', '', o['name'])
    L = custom_lines(o)
    if not L: return None
    rep = dict(order=o['name'], external_id=ext, lines=[], created=o['createdAt'])
    if o.get('cancelledAt'): return dict(rep, status='skipped', reason='order cancelled')
    if o['displayFinancialStatus'] not in ('PAID', 'PARTIALLY_REFUNDED'):
        return dict(rep, status='waiting', reason=f'payment {o["displayFinancialStatus"].lower()}')
    if not dry and pf_get(f'/v2/orders/@{ext}'): return dict(rep, status='exists', reason='already at Printful')
    to = recipient(o)
    plans, holds = [], []
    for i, l in enumerate(L):
        if not l['design']: holds.append(f'{l["name"]}: no design on the line (bought without the custom page?)'); continue
        try:
            p = T.plan(l['design'], l['size']); plans.append((l, p))
            rep['lines'].append(dict(size=l['size'], qty=l['qty'], summary=T.summary(p), mockup=l['mockup']))
        except T.Hold as h:
            holds.append(f'{l["name"]}: {h}'); rep['lines'].append(dict(size=l['size'], qty=l['qty'], hold=str(h), mockup=l['mockup']))
    if not to: holds.append('no shipping address on the order (or the app can\'t see it: protected customer data)')
    if holds:
        kind = 'logo' if any('logo' in h for h in holds) else 'home-port' if any('Home Port' in h for h in holds) else \
               'no-address' if any('shipping address' in h for h in holds) else 'no-design' if any('no design' in h for h in holds) else 'other'
        return dict(rep, status='held', reason='; '.join(holds), reason_kind=kind)
    out = os.path.join(tempfile.gettempdir(), 'custom_orders', ext); items = []
    for n, (l, p) in enumerate(plans):
        files = T.render(p, os.path.join(out, f'line{n + 1}'))
        rep['lines'][n]['files'] = files
        urls = {k: 'file://' + v for k, v in files.items()} if dry else dict(zip(files, AO.upload(list(files.values()), f'{o["name"]} custom tee {n + 1}')))
        items.append({'source': 'catalog', 'catalog_variant_id': p['variant_id'], 'quantity': l['qty'], 'external_id': l['line_id'],
                      'name': f'Make it yours tee · {p["garment"].split(", ")[1]} · {l["size"]}', 'retail_price': f'{float(l["price"]):.2f}',
                      'placements': [{'placement': k, 'technique': 'dtg',
                                      'layers': [{'type': 'file', 'url': u, 'position': {'top': 0, 'left': 0, 'width': AREA[k][0], 'height': AREA[k][1]}}]}
                                     for k, u in urls.items()]})
    order = {'external_id': ext, 'shipping': 'STANDARD', 'recipient': to, 'order_items': items,
             'customization': {'packing_slip': {'store_name': 'Doolittle Scuba', 'custom_order_id': o['name']}}}
    if dry: return dict(rep, status='dry-run', printful=order)
    r = AO.printful('POST', '/v2/orders', order)['data']; oid = r['id']; c = {}
    for _ in range(20):
        c = AO.printful('GET', f'/v2/orders/{oid}')['data']['costs']
        if c.get('calculation_status') == 'done': break
        time.sleep(3)
    return dict(rep, status='draft', printful_id=oid, costs={k: c.get(k) for k in ('subtotal', 'shipping', 'tax', 'total', 'currency')},
                dashboard=f'https://www.printful.com/dashboard/default/orders?search={oid}')


def main():
    a = sys.argv[1:]
    def opt(k, d=None): return a[a.index(k) + 1] if k in a else d
    if opt('--confirm'):
        AO.printful('POST', f'/v2/orders/{opt("--confirm")}/confirmation'); print('confirmed: in production'); return
    dry = '--dry' in a
    reps = [r for r in (handle(o, dry) for o in orders(int(opt('--days', 3)), opt('--order'))) if r]
    # The repo is public, so job logs are too: print order numbers and statuses only, never names, lines of text or links.
    for r in reps:
        print(f'{r["order"]:8s} {r["status"]:8s} {len(r["lines"])} line(s) {r.get("printful_id") or ""}')
        if '--verbose' in a:
            for l in r['lines']: print('   ', l.get('summary') or ('HOLD ' + l.get('hold', '')))
    if not reps: print('no custom orders in the window')
    json.dump([{k: v for k, v in r.items() if k in ('order', 'status', 'printful_id', 'external_id', 'costs', 'dashboard', 'reason_kind')}
               | {'lines': len(r['lines'])} for r in reps], open(opt('--report', 'custom_orders.json'), 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
