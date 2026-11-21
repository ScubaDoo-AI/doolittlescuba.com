#!/usr/bin/env python3
"""Read-only Printful lookups for the Actions log (the token lives only in repo secrets).

  PRINTFUL_TOKEN=… tools/printful_read.py /mockup-generator/printfiles/586 /mockup-generator/templates/586

Known paths get a compact summary; anything else is printed as JSON, trimmed to 4,000 characters.
  /mockup-generator/printfiles/<product>   print-file sizes (px, dpi, fill mode) and which placement uses which file
  /mockup-generator/templates/<product>    the mockup templates, one line per placement, with the print-area box
  /products/<product>                       blank name, model and its variant count
"""
import time, json, os, sys, urllib.request, urllib.error

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
        print(json.dumps(res)[:12000 if 'data' in res else 600]); return   # v2 catalog answers (placements, prices) are long
    r = res['result']
    if '/printfiles/' in path:
        print('product', r.get('product_id'), '| available placements:', json.dumps(r.get('available_placements')))
        print('  option groups:', json.dumps(r.get('option_groups')), '| options:', json.dumps(r.get('options')))
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


def post(path, body, tries=4):
    for _ in range(tries):   # the mockup generator allows ~10 tasks a minute: wait out a 429 and try again
        r = _post(path, body)
        if r.get('code') != 429: return r
        time.sleep(62)
    return r


def _post(path, body):
    req = urllib.request.Request('https://api.printful.com' + path, data=json.dumps(body).encode(), method='POST',
                                 headers={'Authorization': f'Bearer {TOKEN}', 'X-PF-Store-Id': STORE, 'Content-Type': 'application/json', 'User-Agent': 'doolittlescuba-tools/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {'code': e.code, 'error': e.read().decode()[:400]}


def mockup(spec, width=None, quiet=False):
    """mockup:<line>:<SKU> — render Printful's own mockups for one planned variant with the files and positions the
    printful_*.py plan would send (nothing is written to the product). Prints one image URL per placement."""
    import importlib.util, time
    _, line, sku = spec.split(':', 2)
    views = None   # mockup:<line>:<SKU>?g=Flat&o=Front,Back,Left — Printful's extra camera views (option groups / options), printed as "extra"
    if '?' in sku:
        sku, q = sku.split('?', 1); kv = dict(x.split('=', 1) for x in q.split('&'))
        views = {'option_groups': kv['g'].split(',') if kv.get('g') else None, 'options': kv['o'].split(',') if kv.get('o') else None}
    lp = importlib.util.spec_from_file_location('printful_link', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'printful_link.py'))
    L = importlib.util.module_from_spec(lp); lp.loader.exec_module(L)
    if line == 'aquaticfamily':   # personalized Surface Interval tees, family sample names (tools/aquatic_family.py)
        A = importlib.util.module_from_spec(importlib.util.spec_from_file_location('pa', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'printful_aquatic.py')))
        A.__spec__.loader.exec_module(A)
        code = sku.split('-')[1][2:]; d = next(x for x in A.D['designs'] if x['code'] == code)
        base = f'https://doolittlescuba.com/renders/aquatic-family/AC-{code}'
        t = {'variant_id': A.PF[d['colour']]['M'], 'files': [{'type': 'front', 'url': base + '_front.png', 'position': A.AREA},
                                                             {'type': 'back', 'url': base + '_back.png', 'position': A.AREA}]}
    elif line == 'organicfamily':   # organic personalized Surface Interval tees (TDO), family sample names, Stanley/Stella organic blank
        O = importlib.util.module_from_spec(importlib.util.spec_from_file_location('og', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'organic.py')))
        O.__spec__.loader.exec_module(O)
        p = next(x for x in O.plan() if any(v['sku'] == sku for v in x['variants'])); code = p['key'].split('-')[1][2:]
        area = {'area_width': 1800, 'area_height': 2400, 'width': 1800, 'height': 2400, 'top': 0, 'left': 0}
        base = f'https://doolittlescuba.com/renders/aquatic-family/AC-{code}'
        t = {'variant_id': next(v['variant_id'] for v in p['variants'] if v['sku'] == sku),
             'files': [{'type': 'front', 'url': base + '_front.png', 'position': area}, {'type': 'back', 'url': base + '_back.png', 'position': area}]}
    elif line == 'homeport':   # Home Port cap (made to order): Rainbow River's black plan with the Newnan sample front
        t = json.loads(json.dumps(L.targets(['caps'])['DS-RRV-CD-SM']))
        for f in t['files']:
            if f['type'] == 'embroidery_front': f['url'] = 'https://doolittlescuba.com/renders/caps/DS-HMP_Newnan_PF-cap-front_2.96x1.99in_white-red.png'; f.pop('position', None)
    elif line == 'customcap':   # Make it yours cap (Eric, 21 Nov 2026): the files and threads tools/custom_cap.py sends; sku = /custom/ design query
        import custom_cap as CC
        pc = CC.plan(sku if '=' in sku else f'colour={sku}&cf=site&site=black-bart&cs=dsmark&csp=left&cb=tagline', 'LXL')
        opt = {'embroidery_front': 'thread_colors', 'embroidery_front_large': 'thread_colors', 'embroidery_left': 'thread_colors_left',
               'embroidery_right': 'thread_colors_right', 'embroidery_back': 'thread_colors_back'}
        t = {'variant_id': pc['variant_id'], 'files': [], 'options': [{'id': 'embroidery_type', 'value': 'flat'}]}
        for k, pl in pc['placements'].items():
            if pl['kind'] != 'catalog': sys.exit(f'customcap mockup: {k} is new text; use a catalog design')
            t['files'].append({'type': k, 'url': pl['url']})
            t['options'].append({'id': opt[k], 'value': pl['threads'] or CC.threads_of(pl['image'])})
    elif line == 'plainside':   # a cap with no side embroidery (The Mark, The Stack): Printful only renders embroidered placements,
        # so the left side gets a 0.03 in black dot (renders/caps/plain-side-dot.png) to make it draw the plain side. Mockup only.
        ln, sk = sku.split('/', 1)
        t = json.loads(json.dumps(L.targets([ln]).get(sk) or sys.exit(f'{sk} not in the {ln} plan')))
        t['files'].append({'type': 'embroidery_left', 'url': 'https://doolittlescuba.com/renders/caps/plain-side-dot.png'})
        t.setdefault('options', []).append({'id': 'thread_colors_left', 'value': ['#000000']})
    else:
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
            if f['placement'] not in pmap and f['placement'] + '_large' in pmap: f['placement'] += '_large'   # caps: the front is embroidery_front_large
            if f['placement'] not in pmap or pmap[f['placement']] not in sizes:
                print('   no printfile for', f['placement'], '| placements:', json.dumps(pmap), '| printfiles:', json.dumps(sizes)); continue
            W, H = sizes[pmap[f['placement']]]
            req = urllib.request.Request(f['image_url'], headers={'User-Agent': 'doolittlescuba-tools/1.0', 'Range': 'bytes=0-31'})
            with urllib.request.urlopen(req, timeout=60) as r:
                w, h = struct.unpack('>II', r.read(32)[16:24])
            s = min(W / w, H / h); nw, nh = round(w * s), round(h * s)
            f['position'] = {'area_width': W, 'area_height': H, 'width': nw, 'height': nh, 'top': (H - nh) // 2, 'left': (W - nw) // 2}
    if not quiet:
        print(f'\n== mockup {sku} → product {pid} variant {t["variant_id"]} ==')
        for f in files: print('  ', f['placement'], f['image_url'].rsplit('/', 1)[-1], json.dumps(f.get('position')))
    body = {'variant_ids': [t['variant_id']], 'format': 'png', 'files': files}
    if width: body['width'] = width   # mockup image width in px (Printful: max 2000, default 1000)
    if views:
        body.update({k: v for k, v in views.items() if v})
    if t.get('options'): body['product_options'] = {o['id']: o['value'] for o in t['options']}   # embroidery: thread colours and type
    r = post(f'/mockup-generator/create-task/{pid}', body)
    key = r.get('result', {}).get('task_key') or sys.exit(f'create-task failed: {json.dumps(r)[:400]}')
    for _ in range(40):
        time.sleep(6)
        st = get(f'/mockup-generator/task?task_key={key}').get('result', {})
        if st.get('status') == 'completed':
            if quiet: return dict(product=pid, variant=t['variant_id'], placements=[f['placement'] for f in files], mockups=st.get('mockups', []))
            for m in st.get('mockups', []):
                print('  mockup', m.get('placement'), m.get('mockup_url'))
                for e in m.get('extra', []): print('    extra', e.get('title'), e.get('url'))
            return
        if st.get('status') == 'failed': sys.exit(f'mockup task failed: {st.get("error")}')
    sys.exit('mockup task timed out')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        if p.startswith('/'): show(p)
        elif p.startswith('mockup:'):
            try: mockup(p)
            except BaseException as e: print(f'\n== {p} FAILED: {e!r} ==')   # one bad spec doesn't stop the rest
