#!/usr/bin/env python3
"""Sample order to Eric: one Printful order (API v1, DRAFT) with any mix of linked and personalized tees.

Each item is a SKU, written `SKU` or `SKU:Name` or `SKU:Name1:Name2`:
  - Linked lines (Signature, Certified-ish, Aquatic Boat Banter, 1N73LL1G3NC3) use exactly the variant and print files the
    store link uses (tools/printful_*.py plans), so the sample is the shirt a customer would get.
  - Aquatic personalized tees (DS-AC[WRBCM]nn-TD-<size>) render the names with tools/aquatic_print.py and upload the
    files to Shopify Files first, the same way tools/aquatic_order.py does.
The order is created as a DRAFT (v1 confirm=false). Printful's costs are printed. Confirm in the Printful dashboard,
or run with --confirm-id <order id>.

  SAMPLE_SHIP_TO='{"name":…,"address1":…,"city":…,"state_code":"GA","country_code":"US","zip":…}' \
  PRINTFUL_TOKEN=… SHOPIFY_CLIENT_ID=… SHOPIFY_CLIENT_SECRET=… \
  tools/sample_order.py DS-THI-TD-XL DS-ACW01-TD-XL:Eric DS-TEC-TD-XL [--dry-run]
  tools/sample_order.py --confirm-id 123456789

The address comes only from the environment (a GitHub secret in the Actions job) and is never written to disk or logs.
"""
import os, sys, json, re, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aquatic_order as AO

STORE = os.environ.get('PRINTFUL_STORE', '18960047')


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def catalog():
    """SKU -> (variant_id, files, label, price) for every linked tee line."""
    out = {}
    for mod in ('printful_signature', 'printful_certifiedish', 'printful_aquatic'):
        for p in load(mod).plan('dtg'):
            for v in p['variants']:
                label = p.get('name') or p.get('site') or p.get('code')
                out[v['sku']] = (v['variant_id'], p['files'], f"{label} {p.get('line', '')} {v['size']}".strip(), v['price'])
    for p in load('printful_n73').plan('dtg'):
        files = [dict(f, type='front' if f['type'] == 'default' else f['type']) for f in p['files']]
        for v in p['variants']:
            out[v['sku']] = (v['variant_id'], files, f"{p['title']} {v['size']}", v['price'])
    return out


def v1(method, path, body=None):
    tok = os.environ.get('PRINTFUL_TOKEN') or sys.exit('PRINTFUL_TOKEN not set')
    code, r = AO.http(method, 'https://api.printful.com' + path,
                      {'Authorization': 'Bearer ' + tok, 'X-PF-Store-Id': STORE, 'Content-Type': 'application/json'}, body)
    if code >= 300: sys.exit(f'Printful {method} {path}: {code} {r}')
    return r['result']


def main():
    a = sys.argv[1:]
    if '--confirm-id' in a:
        oid = a[a.index('--confirm-id') + 1]
        if not oid.isdigit(): sys.exit('order id must be digits')
        r = v1('POST', f'/orders/{oid}/confirm'); print(f'order {oid} confirmed: {r.get("status")}'); return
    dry = '--dry-run' in a
    specs = [x for x in a if not x.startswith('--')]
    if not specs: sys.exit(__doc__)
    cat = catalog(); items = []; out = os.path.join(tempfile.gettempdir(), 'sample_order')
    for sp in specs:
        sku, *names = sp.split(':')
        m = AO.SKU_RE.match(sku)
        if m:                                                    # personalized Aquatic tee
            code, size = m.groups()
            shirt = dict(code=code, size=size, qty=1, names=names)
            nm, fp, bp = AO.render(shirt, out); shirt['names'] = list(nm.values())
            if dry: fu, bu = 'file://' + fp, 'file://' + bp
            else: fu, bu = AO.upload([fp, bp], 'sample')
            v2 = AO.item(shirt, fu, bu)
            vid = v2['catalog_variant_id']; files = [{'type': pl['placement'], 'url': pl['layers'][0]['url'],
                     'position': {'area_width': 1800, 'area_height': 2400, 'width': 1800, 'height': 2400, 'top': 0, 'left': 0}} for pl in v2['placements']]
            label, price = v2['name'], float(v2['retail_price'])
        elif sku in cat:
            vid, files, label, price = cat[sku]
        else:
            sys.exit(f'{sku}: not a known SKU (linked tee lines or DS-AC[WRBCM]nn-TD-<size>)')
        items.append({'variant_id': vid, 'quantity': 1, 'name': f'SAMPLE {label}', 'retail_price': f'{price:.2f}', 'files': files})
        print(f'{sku:18s} → variant {vid}  {label}  [{", ".join(f["type"] for f in files)}]')
    ship = os.environ.get('SAMPLE_SHIP_TO')
    if dry:
        print(json.dumps(items, indent=1)[:4000]); print('\ndry run: no upload, no Printful order'); return
    if not ship: sys.exit('SAMPLE_SHIP_TO not set (JSON address; a GitHub secret in the Actions job)')
    order = {'external_id': 'sample-' + re.sub(r'\D', '', __import__('time').strftime('%Y%m%d%H%M')), 'shipping': 'STANDARD',
             'recipient': json.loads(ship), 'items': items,
             'packing_slip': {'store_name': 'Doolittle Scuba', 'message': 'Sample order'}}
    r = v1('POST', '/orders?confirm=false', order)
    c = r.get('costs', {})
    print(f'\nPrintful draft order {r["id"]} ({r.get("status")}): subtotal {c.get("subtotal")} · shipping {c.get("shipping")} · '
          f'tax {c.get("tax")} · total {c.get("total")} {c.get("currency", "")}')
    print('Check it at https://www.printful.com/dashboard/default/orders, then confirm there or run the job with confirm + this id.')


if __name__ == '__main__':
    main()
