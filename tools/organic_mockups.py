#!/usr/bin/env python3
"""Mockups for the organic editions: each regular mockup (same ink group) re-dyed to its organic colour by organic_redye.py.

  tools/organic_mockups.py [line ...]      -> img/organic/<line>/<name>-{front,back}.webp (1200) + -t.webp (600)
                                              img/organic/manifest.json  (product key -> image paths, colour, hex)
The beanie is rendered, not re-dyed (Atlantis organic rib: Black #232323, Oxford Navy #1E2E3E) by the caps Project's
beanie_render.py; its two images are copied in by hand and listed here.
"""
import os, sys, json, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import organic
from organic_redye import redye

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = f'{SITE}/img'
OUT = f'{IMG}/organic'
CAP_HEX = {'Black': '#0E0E0E', 'Charcoal': '#4C4746', 'Jungle': '#928355', 'Pacific': '#061226'}


def jd(name): return json.load(open(f'{SITE}/tools/{name}.json', encoding='utf-8'))


def designs(d): return d['designs'] if 'designs' in d else next(v for v in d.values() if isinstance(v, list) and v and isinstance(v[0], dict))


OW = {int(x['n']): x for x in designs(jd('offworld_designs'))}
N73 = {int(x['n']): x for x in designs(jd('n73_designs'))}
AQ = {x['code']: x for x in designs(jd('aquatic_designs'))}
SIG = {code: stem.replace('_', '-').lower() for code, stem, *_ in organic.load('printful_signature').DESIGNS}
CERT = {code: name for code, name, *_ in organic.load('printful_certifiedish').DESIGNS}
CAPS = {code: handle.replace('-dark-cap', '') for code, handle, *_ in organic.load('printful_caps').CAPS}


def sources(p):
    """(name, [front, back]) of the regular mockups for an organic product."""
    k = p['regular_key']; dark = p['group'] == 'dark' if p['kind'] == 'tee' else True
    code = k.split('-')[1]
    if p['line'] == 'signature':
        slug = SIG[code].replace('the-', '') if SIG[code].startswith('the-') else SIG[code]
        slug = {'navy-llcat': 'navy-llcat'}.get(slug, slug)
        d = f'{IMG}/shirts/dark' if k.endswith('-TD') else f'{IMG}/shirts'
        return slug, [f'{d}/{slug}-front.webp', f'{d}/{slug}-back.webp']
    if p['line'] == 'certifiedish':
        nm = CERT[code].lower().replace(' diver', '').replace('&', 'and')
        nm = {'search and recovery': 'search-recovery', 'underwater photographer': 'uw-photo', 'surface marker buoy': 'smb',
              'self-reliant': 'self-reliant'}.get(nm, nm).replace(' ', '-')
        d = f'{IMG}/certs/dark' if k.endswith('-TD') else f'{IMG}/certs'
        return f'cert-{nm}', [f'{d}/cert-{nm}-front.webp', f'{d}/cert-{nm}-back.webp']
    if p['line'] == 'offworld':
        x = OW[int(code[2:])]; d = f'{IMG}/offworld/dark' if k.endswith('-TD') else f'{IMG}/offworld'
        return x['slug'], [f'{d}/{x["slug"]}-front.webp', f'{d}/{x["slug"]}-back.webp']
    if p['line'] == 'n73':
        x = N73[int(code[1:])]; return x['slug'], [f'{IMG}/n73/{x["slug"]}-front.webp', f'{IMG}/n73/{x["slug"]}-back.webp']
    if p['line'] == 'aquatic':
        x = AQ[code[2:]]; return x['slug'], [f'{IMG}/aquatic/{x["slug"]}-front.webp', f'{IMG}/aquatic/{x["slug"]}-back.webp']
    if p['line'] == 'caps':
        s = CAPS[code]; return f'cap-{s}', [f'{IMG}/hats/dark/cap-dark-{s}-front.webp', f'{IMG}/hats/dark/cap-dark-{s}-back.webp']
    return None, []


def main(only):
    man = json.load(open(f'{OUT}/manifest.json')) if os.path.exists(f'{OUT}/manifest.json') else {}
    for p in organic.plan():
        if only and p['line'] not in only: continue
        if p['kind'] == 'beanie': continue
        name, srcs = sources(p)
        hexc = p.get('hex') or CAP_HEX[p['colour']]
        d = f'{OUT}/{p["line"]}'; os.makedirs(d, exist_ok=True)
        side = '-dark' if p['regular_key'].endswith('-TD') and p['line'] in ('signature', 'certifiedish', 'offworld') else ''
        paths = []
        for src, view in zip(srcs, ('front', 'back')):
            if not os.path.exists(src): print('MISSING', p['key'], src); continue
            dst = f'{d}/{name}{side}-{view}.webp'
            redye(src, dst, hexc, thumb=600)
            paths.append(dst.replace(SITE, ''))
        man[p['key']] = dict(line=p['line'], name=name, colour=p['colour'], hex=hexc, images=paths)
        print(p['key'], p['colour'], len(paths), flush=True)
    json.dump(man, open(f'{OUT}/manifest.json', 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1:])
