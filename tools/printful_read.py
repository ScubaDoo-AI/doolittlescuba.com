#!/usr/bin/env python3
"""Read-only Printful lookups for the Actions log (the token lives only in repo secrets).

  PRINTFUL_TOKEN=… tools/printful_read.py /mockup-generator/printfiles/586 /mockup-generator/templates/586

Known paths get a compact summary; anything else is printed as JSON, trimmed to 4,000 characters.
  /mockup-generator/printfiles/<product>   print-file sizes (px, dpi, fill mode) and which placement uses which file
  /mockup-generator/templates/<product>    the mockup templates, one line per placement, with the print-area box
  /products/<product>                       blank name, model and its variant count
"""
import json, os, sys, urllib.request, urllib.error

TOKEN = os.environ.get('PRINTFUL_TOKEN') or sys.exit('PRINTFUL_TOKEN not set')
STORE = '18960047'


def get(path):
    req = urllib.request.Request('https://api.printful.com' + path,
                                 headers={'Authorization': f'Bearer {TOKEN}', 'X-PF-Store-Id': STORE, 'User-Agent': 'doolittlescuba-tools/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {'code': e.code, 'error': e.read().decode()[:300]}


def show(path):
    res = get(path)
    print(f'\n== {path} ==')
    if 'result' not in res:
        print(json.dumps(res)[:600]); return
    r = res['result']
    if '/printfiles/' in path:
        print('product', r.get('product_id'), '| available placements:', json.dumps(r.get('available_placements')))
        for pf in r.get('printfiles', []):
            w, h, dpi = pf.get('width') or 0, pf.get('height') or 0, pf.get('dpi') or 1
            print(f"  printfile {pf.get('printfile_id', pf.get('id'))}: {w} x {h} px @ {dpi} dpi = {w/dpi:.2f} x {h/dpi:.2f} in, "
                  f"fill_mode={pf.get('fill_mode')}, can_rotate={pf.get('can_rotate')} | raw={json.dumps(pf)[:200]}")
        vp = r.get('variant_printfiles', [])
        if vp:
            print('  placement → printfile (first variant', vp[0].get('variant_id'), '):', json.dumps(vp[0].get('placements')))
            diff = {json.dumps(v.get('placements'), sort_keys=True) for v in vp}
            print('  distinct placement maps across variants:', len(diff))
        return
    if '/templates/' in path:
        vm = r.get('variant_mapping', [])
        want = {}
        for v in vm[:1]:
            for t in v.get('templates', []):
                if 'sleeve' in (t.get('placement') or '') or '--all' in sys.argv: want[t.get('template_id')] = t.get('placement')
        if vm: print('  variant', vm[0].get('variant_id'), 'templates:', json.dumps(vm[0].get('templates')))
        for t in r.get('templates', []):
            if t.get('template_id') not in want: continue
            print(f"  template {t.get('template_id')} ({want[t.get('template_id')]}): image={t.get('template_width')}x{t.get('template_height')} "
                  f"print_area left={t.get('print_area_left')} top={t.get('print_area_top')} w={t.get('print_area_width')} h={t.get('print_area_height')} "
                  f"printfile={t.get('printfile_id')} orientation={t.get('orientation')} is_template_on_front={t.get('is_template_on_front')}")
            print('    image_url', t.get('image_url')); print('    background_url', t.get('background_url'))
        return
    if path.startswith('/products/'):
        p = r.get('product', {})
        print(p.get('id'), p.get('brand'), p.get('model'), '|', p.get('title'), '| variants:', len(r.get('variants', [])))
        return
    print(json.dumps(r)[:4000])


def post(path, body):
    req = urllib.request.Request('https://api.printful.com' + path, data=json.dumps(body).encode(), method='POST',
                                 headers={'Authorization': f'Bearer {TOKEN}', 'X-PF-Store-Id': STORE, 'Content-Type': 'application/json', 'User-Agent': 'doolittlescuba-tools/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {'code': e.code, 'error': e.read().decode()[:400]}


def mockup(spec):
    """mockup:<line>:<SKU> — render Printful's own mockups for one planned variant with the files and positions the
    printful_*.py plan would send (nothing is written to the product). Prints one image URL per placement."""
    import importlib.util, time
    _, line, sku = spec.split(':', 2)
    lp = importlib.util.spec_from_file_location('printful_link', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'printful_link.py'))
    L = importlib.util.module_from_spec(lp); lp.loader.exec_module(L)
    t = L.targets([line]).get(sku) or sys.exit(f'{sku} not in the {line} plan')
    v = get(f'/products/variant/{t["variant_id"]}')
    pid = v.get('result', {}).get('variant', {}).get('product_id') or sys.exit(f'no product for variant {t["variant_id"]}: {json.dumps(v)[:200]}')
    files = [{'placement': 'front' if f['type'] == 'default' else f['type'], 'image_url': f['url'], **({'position': f['position']} if f.get('position') else {})}
             for f in t['files'] if f['type'] != 'preview']
    missing = [f for f in files if not f.get('position')]
    if missing:   # no position in the plan: Printful fits and centres the file in the print area, so the mockup does the same
        import struct
        pf = get(f'/mockup-generator/printfiles/{pid}').get('result', {})
        pmap = next((v.get('placements', {}) for v in pf.get('variant_printfiles', []) if v.get('variant_id') == t['variant_id']), {})
        sizes = {p.get('printfile_id', p.get('id')): (p['width'], p['height']) for p in pf.get('printfiles', [])}
        for f in missing:
            W, H = sizes[pmap[f['placement']]]
            req = urllib.request.Request(f['image_url'], headers={'User-Agent': 'doolittlescuba-tools/1.0', 'Range': 'bytes=0-31'})
            with urllib.request.urlopen(req, timeout=60) as r:
                w, h = struct.unpack('>II', r.read(32)[16:24])
            s = min(W / w, H / h); nw, nh = round(w * s), round(h * s)
            f['position'] = {'area_width': W, 'area_height': H, 'width': nw, 'height': nh, 'top': (H - nh) // 2, 'left': (W - nw) // 2}
    print(f'\n== mockup {sku} → product {pid} variant {t["variant_id"]} ==')
    for f in files: print('  ', f['placement'], f['image_url'].rsplit('/', 1)[-1], json.dumps(f.get('position')))
    body = {'variant_ids': [t['variant_id']], 'format': 'png', 'files': files}
    if t.get('options'): body['product_options'] = {o['id']: o['value'] for o in t['options']}   # embroidery: thread colours and type
    r = post(f'/mockup-generator/create-task/{pid}', body)
    key = r.get('result', {}).get('task_key') or sys.exit(f'create-task failed: {json.dumps(r)[:400]}')
    for _ in range(40):
        time.sleep(6)
        st = get(f'/mockup-generator/task?task_key={key}').get('result', {})
        if st.get('status') == 'completed':
            for m in st.get('mockups', []):
                print('  mockup', m.get('placement'), m.get('mockup_url'))
                for e in m.get('extra', []): print('    extra', e.get('title'), e.get('url'))
            return
        if st.get('status') == 'failed': sys.exit(f'mockup task failed: {st.get("error")}')
    sys.exit('mockup task timed out')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        if p.startswith('/'): show(p)
        elif p.startswith('mockup:'): mockup(p)
