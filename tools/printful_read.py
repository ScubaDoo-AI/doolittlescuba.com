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
                                 headers={'Authorization': f'Bearer {TOKEN}', 'X-PF-Store-Id': STORE})
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


if __name__ == '__main__':
    for p in [a for a in sys.argv[1:] if a.startswith('/')]:
        show(p)
