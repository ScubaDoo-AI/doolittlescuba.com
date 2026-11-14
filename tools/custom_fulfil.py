#!/usr/bin/env python3
"""Custom orders → Shopify fulfillment with tracking, when Printful ships them.

Custom lines (Make it yours tee/cap, Aquatic name tees) are made by Printful drafts that tools/custom_order.py
creates through the API, so Printful's Shopify integration doesn't know they belong to a Shopify order: without
this, the Shopify order stays Unfulfilled and the buyer never gets a shipping email.

Every run (the Custom orders workflow, every 15 min):
  1. Shopify orders from the last N days that still have unfulfilled custom lines.
  2. Their Printful order: external id MY<order number> (or <order number> from a hand run of aquatic_order.py).
  3. Each Printful shipment → the Shopify line items it carried (Printful item external_id = Shopify line item id),
     fulfilled with the carrier, tracking number and link; Shopify emails the buyer (notifyCustomer).
  4. The digitization fee line (DS-DIGI-n, ships nothing) is closed with the first cap shipment of that order.
Idempotent: only remaining quantities are fulfilled, so a shipment is never sent twice.
Public repo: the log shows order numbers and counts only, never names, addresses or tracking numbers.

  tools/custom_fulfil.py [--days 45] [--order 1001] [--dry]
Needs: PRINTFUL_TOKEN, SHOPIFY_CLIENT_ID/SECRET with read/write_merchant_managed_fulfillment_orders.
"""
import os, sys, re, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aquatic_order as AO
import custom_order as C

FO_Q = '''query($q: String!, $a: String) { orders(first: 25, after: $a, query: $q, sortKey: CREATED_AT, reverse: true) {
  pageInfo { hasNextPage endCursor }
  nodes { id name displayFulfillmentStatus cancelledAt
    fulfillmentOrders(first: 10) { nodes { id status
      lineItems(first: 50) { nodes { id remainingQuantity lineItem { id sku } } } } } } } }'''
CREATE = '''mutation($f: FulfillmentInput!) { fulfillmentCreate(fulfillment: $f) {
  fulfillment { id status } userErrors { field message } } }'''
CUSTOM = re.compile(r'^(DS-MY[AB]-[TC]-|DS-AC[A-Z]\d\d-TDO?-)')
FEE = re.compile(r'^DS-DIGI-\d$')


def pending(days, number=None):
    since = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')
    q = f'name:"#{str(number).lstrip("#")}"' if number else f'created_at:>={since} -fulfillment_status:shipped financial_status:paid'
    out, after = [], None
    while True:
        r = AO.shopify(FO_Q, {'q': q, 'a': after})['orders']
        out += [o for o in r['nodes'] if not o['cancelledAt']]
        if not r['pageInfo']['hasNextPage']: return out
        after = r['pageInfo']['endCursor']


def open_lines(o):
    """{shopify line item id: [(fulfillment order id, FO line item id, remaining, sku)]} for custom + fee lines."""
    L = {}
    for fo in o['fulfillmentOrders']['nodes']:
        if fo['status'] not in ('OPEN', 'IN_PROGRESS'): continue
        for n in fo['lineItems']['nodes']:
            sku = n['lineItem']['sku'] or ''
            if n['remainingQuantity'] > 0 and (CUSTOM.match(sku) or FEE.match(sku)):
                L.setdefault(n['lineItem']['id'].rsplit('/', 1)[-1], []).append((fo['id'], n['id'], n['remainingQuantity'], sku))
    return L


def printful_order(name):
    n = name.lstrip('#')
    for ext in (f'MY{n}', n):
        r = C.pf_get(f'/v2/orders/@{ext}')
        if r: return ext, r['data']
    return None, None


def handle(o, dry):
    L = open_lines(o)
    if not any(CUSTOM.match(v[0][3]) for v in L.values()): return None
    ext, po = printful_order(o['name'])
    if not po: return f'{o["name"]}: no Printful order yet'
    ships = (C.pf_get(f'/v2/orders/@{ext}/shipments') or {}).get('data') or []
    items = {i['id']: (i.get('external_id') or '') for i in ((C.pf_get(f'/v2/orders/@{ext}/order-items') or {}).get('data') or [])}
    if not ships: return f'{o["name"]}: Printful {po.get("status")}, not shipped'
    done = 0
    for sh in ships:
        if not sh.get('tracking_number') and not sh.get('tracking_url'): continue
        want = {}   # shopify line id -> quantity carried by this shipment
        for si in sh.get('shipment_items') or []:
            lid = items.get(si.get('order_item_id'))
            if lid: want[lid] = want.get(lid, 0) + int(si.get('quantity') or 0)
        if not want:   # Printful gave no item detail: this shipment carries every custom line of the order
            want = {lid: sum(x[2] for x in v) for lid, v in L.items() if CUSTOM.match(v[0][3])}
        by_fo = {}
        for lid, q in want.items():
            for fo, foli, rem, sku in L.get(lid, []):
                take = min(q, rem)
                if take <= 0: continue
                by_fo.setdefault(fo, []).append({'id': foli, 'quantity': take}); q -= take
        caps = any(CUSTOM.match(L[lid][0][3]) and '-C-' in L[lid][0][3] for lid in want if lid in L)
        if caps:   # the one-time digitization fee closes with the cap
            for lid, v in L.items():
                for fo, foli, rem, sku in v:
                    if FEE.match(sku) and rem > 0: by_fo.setdefault(fo, []).append({'id': foli, 'quantity': rem})
        if not by_fo: continue      # already fulfilled on an earlier run
        for fo, lines in by_fo.items():
            f = {'lineItemsByFulfillmentOrder': [{'fulfillmentOrderId': fo, 'fulfillmentOrderLineItems': lines}],
                 'notifyCustomer': True,
                 'trackingInfo': {'number': sh.get('tracking_number') or None, 'url': sh.get('tracking_url') or None,
                                  'company': sh.get('carrier') or None}}
            if dry: done += sum(l['quantity'] for l in lines); continue
            r = AO.shopify(CREATE, {'f': f})['fulfillmentCreate']
            if r['userErrors']: return f'{o["name"]}: Shopify refused the fulfillment: ' + '; '.join(e['message'] for e in r['userErrors'])
            done += sum(l['quantity'] for l in lines)
        L = open_lines(dict(o, fulfillmentOrders={'nodes': []})) if dry else open_lines(pending(0, o['name'])[0])
    return f'{o["name"]}: {"would fulfil" if dry else "fulfilled"} {done} item(s), buyer emailed with tracking' if done else f'{o["name"]}: nothing new'


def main():
    a = sys.argv[1:]
    def opt(k, d=None): return a[a.index(k) + 1] if k in a else d
    dry = '--dry' in a
    found = pending(int(opt('--days', 45)), opt('--order'))
    msgs = [m for m in (handle(o, dry) for o in found) if m]
    print('\n'.join(msgs) if msgs else 'no custom orders waiting for shipment')


if __name__ == '__main__':
    main()
