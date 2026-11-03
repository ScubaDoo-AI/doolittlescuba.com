#!/usr/bin/env python3
"""The 1N73LL1G3NC3 art from the Design canvas artboards, as transparent 12 x 16 in print masters.

Each artboard (project/<Name>.dc.html in the "1N73LL1G3NC3 Shirt Line" Design artifact) is a 560 x 660 board: a flat
shirt drawn in SVG and the art laid over its chest in a 260 px wide block. That block is the 11.5 in print, so
1 CSS px = 11.5 / 260 in and the board is rendered at 13.27 px per CSS px for 300 dpi. The drawn shirt and the board
colour are dropped; the templates ({{path}}, <sc-for>, <sc-if>) are expanded here from the values each board's script
computes at the default settings (T = 7, cipher level 1), re-done below in Python rather than run; Google Fonts (Jost,
JetBrains Mono) load as on the canvas; the ink is screenshotted on transparency.

Usage: tools/n73_art.py <artboard dir> <out dir> [slug ...]
  <out dir>/<slug>.png   3600 x 4800 RGBA, 300 dpi: the ink at true size (fitted to 11.5 x 15 in where the board's
                         block would run taller), horizontally where the board put it, its top one inch above where it
                         sits under the collar (the first inch of Printful's front area is that collar gap), and
                         <out dir>/_boxes.json with the measurements.
"""
import os, re, sys, json, math
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(f'{ROOT}/tools/n73_designs.json'))
PX = 300 * 11.5 / 260            # device px per CSS px at 300 dpi
COLLAR, CENTRE = 100, 280        # the board's collar bottom and centre line, CSS px
IN = 260 / 11.5                  # CSS px per inch
BOARD = {'n73-never-hold-your-breath': 'Main', 'n73-plan-your-dive': 'Plan-Dive', 'n73-breathe': 'Bubble-Morse',
         'n73-explore-safely': 'Dive-Computer', 'n73-find-your-depth': 'Word-Search', 'n73-dive-pixel': 'Pixel-Dive',
         'n73-keep-the-pulse': 'Pulse-Meter', 'n73-steady-under-load': 'Steady-Load', 'n73-trust-but-test': 'Meter-Dials',
         'n73-in-phase': 'Phasor', 'n73-ride-the-wave': 'Scope-Wave', 'n73-root-cause': 'Root-Cause',
         'n73-stay-curious': 'Stay-Curious', 'n73-wander': 'Constellation', 'n73-original': 'Barcode',
         'n73-do-the-hard-thing': 'Redacted', 'n73-keep-going': 'Hex-Dump', 'n73-grit-growth': 'Crossword',
         'n73-altitude': 'Attitude', 'n73-depth-to-altitude': 'Flight-Path', 'n73-the-sky-is-open': 'Drone-HUD',
         'n73-find-your-north': 'Compass', 'n73-cleared-for-takeoff': 'Runway', 'n73-send-it': 'Phonetic',
         'n73-shipped': 'Terminal', 'n73-commit-to-it': 'Git-Log', 'n73-404-quit-not-found': 'Not-Found',
         'n73-loading-wisdom': 'Loading', 'n73-infinite-loop': 'Code-Loop', 'n73-reboot': 'Keycaps',
         'n73-full-throttle-no-brakes': 'RC-Throttle', 'n73-one-more-pack': 'RC-Battery', 'n73-mesh-matters': 'RC-Gears',
         'n73-in-control': 'RC-Radio', 'n73-worth-it': 'RC-Receipt', 'n73-brake-late': 'RC-Track'}


def cx(v):
    """The boards' cipher at level 1 with T = 7: only the ~ placeholder changes."""
    return str(v).replace('~', '7')


def gear(gx, gy, n, r0, r1, phase):
    p = math.pi * 2 / n; pts = []
    at = lambda a, r: pts.append(f'{gx + r * math.cos(a):.1f},{gy + r * math.sin(a):.1f}')
    for k in range(n):
        a = phase + k * p
        at(a, r0); at(a + 0.18 * p, r1); at(a + 0.5 * p, r1); at(a + 0.68 * p, r0)
    return ' '.join(pts)


def values(board, ink, dim):
    """What each board's script returns at its defaults, re-done here (the scripts are not run)."""
    s = {}
    v = {'ink': ink, 'dim': dim, 't': '7'}
    if board == 'Main':
        s = dict(title='5CU84 RUL3 #1', r1='N3V3R', r2='H0LD', r3='Y0UR', r4='BR347H', cap='-0P3N W473R RUL3')
    elif board == 'Plan-Dive':
        s = dict(plan='PL4N', your='Y0UR', dive='D1V3', cap='-3V3RY D1V3, 3V3RY 71M3')
    elif board == 'Bubble-Morse':
        s = dict(word='BR347H3')
        code = [('8', '-...'), ('R', '.-.'), ('3', '.'), ('4', '.-'), ('7', '-'), ('H', '....'), ('3', '.')]
        offs = [0, 14, 4, -8, 8, 18, 4]
        v['letters'] = [dict(label=l, off=offs[i], syms=[dict(w=12, h=12, r=6) if c == '.' else dict(w=12, h=26, r=6) for c in m]) for i, (l, m) in enumerate(code)]
    elif board == 'Dive-Computer':
        s = dict(mode='D1V3 M0D3', gas='N17R0X', big='3XPL0R3', stat='54F3LY', cap='-L0G 3V3RY D1V3')
    elif board == 'Word-Search':
        s = dict(cap='-F1ND Y0UR D3P7H')
        rows = ['K7MXA0SRW4', '3TPNH8YL1C', 'UA9D1V3M0X', 'F5RW7KB4NT', 'MD0SX8EC1W', 'Y3K7NSL0RA', 'C3W4T1PUH9', 'NPA8MXK03S', '4HTYR33F0K', 'WS1EMC7AXN']
        hot = {'2,3', '2,4', '2,5', '2,6', '4,1', '5,1', '6,1', '7,1', '4,5', '5,6', '6,7', '7,8', '8,4', '8,5', '8,6', '8,7'}
        v['cells'] = [dict(ch=ch, wt=800 if f'{y},{x}' in hot else 300, col=ink if f'{y},{x}' in hot else dim) for y, r in enumerate(rows) for x, ch in enumerate(r)]
    elif board == 'Pixel-Dive':
        s = dict(cap='-80RN 70 D1V3')
        g = {'D': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'], 'I': ['00100', '01100', '00100', '00100', '00100', '00100', '01110'],
             'V': ['10001', '10001', '10001', '10001', '10001', '01010', '00100'], 'T': ['11110', '00001', '00001', '01110', '00001', '00001', '11110']}
        word = ['D', 'I', 'V', 'T']; pix = []
        for y in range(9):
            for x in range(25):
                on = False; gy, gx = y - 1, x - 1
                if 0 <= gy < 7 and 0 <= gx < 23:
                    li, lx = gx // 6, gx % 6
                    if li < 4 and lx < 5: on = g[word[li]][gy][lx] == '1'
                h = (x * 73 + y * 151 + x * y * 7 + 17) % 100
                pix.append(dict(o=1 if on else (0.1 + (h % 4) * 0.05 if h < 42 else 0.03)))
        v['pix'] = pix
    elif board == 'Pulse-Meter':
        s = dict(cap='K33P 7H3 PUL53')
        masks = {'P': 'abefg', 'U': 'bcdef', 'L': 'def', 'S': 'acdfg', 'E': 'adefg'}
        v['chars'] = [{seg: (1 if seg in masks[ch] else 0.1) for seg in 'abcdefg'} for ch in 'PULSE']
    elif board == 'Steady-Load':
        s = dict(a='5734DY', b='UND3R', c='L04D', cap='-7H3 L1N3 CR3W')
    elif board == 'Meter-Dials':
        s = dict(unit='K1L0W477 H0UR5', main='R34D 7H3 M373R', cap='-7RU57 8U7 7357')
        reading = 7357.2; dials = []
        for i in range(4):
            pos = (reading / 10 ** (3 - i)) % 10; d = 1 if i % 2 == 0 else -1
            ticks = []
            for n in range(10):
                a = d * n * 36 * math.pi / 180
                ticks.append(dict(n=n, x=round((25.5 + 19 * math.sin(a) - 5) * 10) / 10, y=round((25.5 - 19 * math.cos(a) - 5) * 10) / 10))
            dials.append(dict(ticks=ticks, deg=d * pos * 36))
        v['dials'] = dials
    elif board == 'Phasor':
        s = dict(a='4', b='8', c='C', main='1N PH453', cap='-3 PH453, 0N3 CR3W')
    elif board == 'Scope-Wave':
        s = dict(main='R1D3 7H3 W4V3', cap='-P34K P3RF0RM4NC3')
        v['pts'] = ' '.join(f'{x},{round((85 - 52 * math.sin(x / 250 * math.pi * 4)) * 10) / 10:g}' for x in range(0, 251, 5))
    elif board == 'Root-Cause':
        s = dict(w='WHY', main='R007 C4U53', cap='-D16 D33P3R')
    elif board == 'Stay-Curious':
        s = dict(a='574Y', b='CUR10U5', cap='-D3C0D3 3V3RY7H1NG')
    elif board == 'Constellation':
        w = 'W4ND3R'; s = dict(word=w, cap='-N0 M4P N33D3D', **{f'l{i}': c for i, c in enumerate(w)})
    elif board == 'Barcode':
        s = dict(word='0R1G1N4L', cap='-N07 C0P13D')
        ws = [2, 3, 2, 5, 2, 2, 3, 6, 2, 3, 2, 4]; gs = [2, 3, 2, 2, 4, 2, 3, 2]; bars = []; total = i = 0
        while total < 236:
            w, g = ws[(i * 5 + 3) % len(ws)], gs[(i * 3 + 1) % len(gs)]; bars.append(dict(w=w, g=g)); total += w + g; i += 1
        v['bars'] = bars
    elif board == 'Redacted':
        s = dict(a='D0', b='7H3', c='H4RD', d='7H1NG', top='CL4551F13D · P4G3 1 0F 1', cap='-D3CL4551F13D')
    elif board == 'Hex-Dump':
        s = dict(k='K33P', g=' G01', ng='NG', main='K33P G01NG', cap='-R34D 7H3 50URC3')
    elif board == 'Crossword':
        s = dict(c1="1→ D0N'7 QU17", c2='1↓ 1MPR0V3', c3='2↓ 4773MP7', c4='3→ 5UCC33D', cap='-GR17 = GR0W7H')
        rows = ['GR17', 'R##R', '0##Y', 'W1N#']; nums = {'0,0': '1', '0,3': '2', '3,0': '3'}
        v['cells'] = [dict(block=ch == '#', open=ch != '#', ch='' if ch == '#' else ch, num=nums.get(f'{y},{x}', '')) for y, r in enumerate(rows) for x, ch in enumerate(r)]
    elif board == 'Attitude':
        s = dict(main='4L717UD3', p='P17CH', b='B4NK', cap='-CH0053 Y0UR5')
    elif board == 'Flight-Path':
        s = dict(w1='D3P7H', w2='CL1MB', w3='4L717', surf='SURFACE', main='D3P7H 70 4L717UD3', cap='-N0 C31L1NG')
    elif board == 'Drone-HUD':
        s = dict(rec='R3C', bat='B47', alt='4L7', ft='F7', spd='5PD', main='5KY 15 0P3N', home='H0M3 P01N7 R3C0RD3D', cap='-FLY R35P0N518LY')
    elif board == 'Compass':
        s = dict(n='N', e='3', so='5', w='W', main='F1ND Y0UR N0R7H', cap='-7RU3 N0R7H 0NLY')
    elif board == 'Runway':
        s = dict(a='CL34R3D F0R', b='74K30FF', cap='-RUNW4Y 27, G0')
    elif board == 'Phonetic':
        s = dict(main='S3ND 17', cap='-R0G3R 7H47')
        v['words'] = [dict(head=w[0], tail=w[1:]) for w in ['S13RR4', '3CH0', 'N0V3MB3R', 'D3L74', '1ND14', '74NG0']]
    elif board == 'Terminal':
        s = dict(l1='dr34m.5h', l2='c0mp1l1ng...', l3='3rr0r5: 3', l4='r37ry1ng...', ok='[ 0K ] 5H1PP3D', cap='-W0RK5 0N MY M4CH1N3')
    elif board == 'Git-Log':
        s = dict(title='C0MM17 70 17', cap='-G17 G00D')
        lst = [('7f3a91', '5H1PP3D 17', True), ('c2e04b', 'F1X3D 17', False), ('9b17d0', 'BR0K3 17', False), ('4e8f22', '7R13D 17', False), ('0a0001', '1N171AL C0MM17', False)]
        # the board fills the older commits' circles with the shirt colour; on a print that is bare garment
        v['commits'] = [dict(hash=h, msg=m, wt=800 if top else 300, fill=ink if top else 'transparent') for h, m, top in lst]
    elif board == 'Not-Found':
        s = dict(main='QU17 N07 F0UND', l1='534RCH1NG F0R G1V3 UP...', l2='0 R35UL75 · 7RY 4G41N', cap='-K33P R37RY1NG')
    elif board == 'Loading':
        s = dict(top='UPD471NG BR41N...', a='L04D1NG', b='W15D0M', sub='D0 N07 7URN 0FF Y0UR CUR10S17Y', cap='-PL34S3 W417'); v['pct'] = 87
    elif board == 'Code-Loop':
        s = dict(cond='4l1v3', eat='  347();', dive='  d1v3();', sleep='  5l33p();', rep='  r3p347();', cap='-1NF1N173 L00P')
    elif board == 'Keycaps':
        s = dict(main='R3B007', sub='7URN 17 0FF 4ND 0N 4G41N', cap='-FR35H 574R7')
        v['keys'] = [dict(label='C7RL', plus=False), dict(label='4L7', plus=True), dict(label='D3L', plus=True)]
    elif board == 'RC-Throttle':
        s = dict(a='FULL', b='7HR077L3', c='N0', d='BR4K35', cap='-B45H3R5 0NLY')
    elif board == 'RC-Battery':
        s = dict(low='! L0W V0L74G3 · 3.5V/C3LL', a='0N3 M0R3', b='P4CK', cap='-L1P0 L1F3')
    elif board == 'RC-Gears':
        s = dict(main='M35H M4773R5', cap='-P4P3R 7357')
        ps, pp = math.pi * 2 / 44, math.pi * 2 / 17
        v['spur'] = gear(98, 112, 44, 84, 92, -0.34 * ps); v['pinion'] = gear(218, 112, 17, 27, 34, math.pi - 0.84 * pp)
    elif board == 'RC-Radio':
        s = dict(model='M0D3L 03 · B45H3R', str='57R', thr='7HR', m='M070R', link='L1NK', main='1N C0N7R0L', cap='-F41L54F3 4RM3D')
    elif board == 'RC-Receipt':
        s = dict(head='B45H R3P41R L0G', sub='5UND4Y · 7R4CK D4Y', total='7074L', main='W0R7H 17', foot='N0 R3FUND5 · N0 R3GR375', cap='-BR34K. F1X. R3P347.')
        v['items'] = [dict(name=n, price=p) for n, p in [('4-4RM FR0N7 L', '12.99'), ('5H0CK 70W3R', '18.49'), ('DR1V35H4F7', '9.99'), ('B0DY P0575', '6.49'), ('5P4R3 P1N10N', '7.99'), ('C4 GLU3', '4.29')]]
    elif board == 'RC-Track':
        s = dict(lap='L4P', best='B357', main='BR4K3 L473', cap='-H17 7H3 4P3X')
    else:
        raise SystemExit('no values for ' + board)
    v['s'] = {k: cx(x) for k, x in s.items()}
    return v


# -- template expansion (the canvas runtime's {{path}}, <sc-for list as>, <sc-if value>) --------------------------------
def js_str(x):
    if isinstance(x, bool): return 'true' if x else 'false'
    if isinstance(x, float): return str(int(x)) if x.is_integer() else repr(x)
    return str(x)


def lookup(scope, p):
    p = p.strip()
    if p == 'true': return True
    if p == 'false': return False
    v = scope
    for k in p.split('.'):
        if v is None: return None
        v = v.get(k) if isinstance(v, dict) else None
    return v


def fill(tpl, scope):
    return re.sub(r'\{\{\s*([\w.$]+)\s*\}\}', lambda m: '' if lookup(scope, m.group(1)) is None else js_str(lookup(scope, m.group(1))), tpl)


def block(html, tag, start):
    open_ = html.index('>', start) + 1; depth = 1; i = open_
    for m in re.finditer(rf'<(/?){tag}\b', html[open_:]):
        if m.group(1) == '/':
            depth -= 1
            if depth == 0: i = open_ + m.start(); break
        else: depth += 1
    close = html.index('>', i) + 1
    return html[start:open_], html[open_:i], close


def expand(html, scope):
    while True:
        m = re.search(r'<sc-(for|if)\b', html)
        if not m: return fill(html, scope)
        tag = 'sc-' + m.group(1); attrs, inner, end = block(html, tag, m.start()); out = ''
        if tag == 'sc-for':
            lst = lookup(scope, re.search(r'list="\{\{\s*([\w.$]+)\s*\}\}"', attrs).group(1)) or []
            name = re.search(r'\bas="(\w+)"', attrs).group(1)
            out = ''.join(expand(inner, {**scope, name: item}) for item in lst)
        elif lookup(scope, re.search(r'value="\{\{\s*([\w.$]+)\s*\}\}"', attrs).group(1)):
            out = expand(inner, scope)
        html = html[:m.start()] + out + html[end:]


def page_html(src, board, zoom):
    props = json.loads(re.search(r"data-props='([^']*)'", src).group(1))
    ink = props['ink']['default']; dim = props.get('dim', {}).get('default', '')
    helmet = re.search(r'<helmet>(.*?)</helmet>', src, re.S).group(1)
    body = re.search(r'</helmet>\s*(.*?)\s*</x-dc>', src, re.S).group(1)
    body = re.sub(r'<svg aria-hidden="true" width="560" height="660" viewBox="0 0 560 660".*?</svg>', '', body, count=1, flags=re.S)   # the drawn shirt
    body = body.replace('background: #ecebe8;', 'background: transparent;')
    body = expand(body, values(board, ink, dim))
    assert '{{' not in body, board
    return (f'<!doctype html><html><head><meta charset="utf-8">{helmet}<style>html,body{{margin:0;background:transparent}}</style></head>'
            f'<body><div id="z" style="zoom:{zoom}">{body}</div></body></html>'), ink


# a headline the canvas sets in one line must stay one line on the shirt: Jost's real metrics push a few of them
# ("QU17 N07 F0UND", "M35H M4773R5" …) past the 260 px block, so those lose letter-spacing, then a point or two of size
ONE_LINE_JS = '''() => {
  const art = document.querySelector('#z div[style*="position: absolute"]'); const fixed = [];
  for (const e of art.querySelectorAll('div')) {
    if ([...e.children].some(c => c.tagName !== 'SPAN') || e.innerHTML.includes('<br>')) continue;
    const t = e.textContent.trim(); if (!t) continue;
    const cs = getComputedStyle(e); if (cs.whiteSpace === 'pre') continue;
    const fs = parseFloat(cs.fontSize); if (fs < 20) continue;
    const lh = parseFloat(cs.lineHeight) || fs * 1.2;
    if (e.getBoundingClientRect().height <= lh * 1.6) continue;
    e.style.whiteSpace = 'nowrap';
    let ls = parseFloat(cs.letterSpacing) || 0, size = fs, n = 0;
    while (e.scrollWidth > e.clientWidth + 0.5 && n++ < 40) {
      if (ls > 0) { ls = Math.max(0, ls - 0.5); e.style.letterSpacing = ls + 'px'; }
      else { size -= 1; e.style.fontSize = size + 'px'; }
    }
    fixed.push(t + ' → ' + size + 'px / ' + ls + 'px');
  }
  return fixed;
}'''


def main():
    from playwright.sync_api import sync_playwright
    art_dir, out = sys.argv[1], sys.argv[2]; only = set(sys.argv[3:]); os.makedirs(out, exist_ok=True)
    boxes = {}
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={'width': 560, 'height': 660}, device_scale_factor=1)
        for d in D['designs']:
            if only and d['slug'] not in only: continue
            src = open(f'{art_dir}/{BOARD[d["slug"]]}.dc.html', encoding='utf-8').read()
            # pass 1 at board scale: where the ink is
            html, ink = page_html(src, BOARD[d['slug']], 1)
            pg.set_content(html, wait_until='networkidle'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(120)
            fixed = pg.evaluate(ONE_LINE_JS)
            lo = f'{out}/_lo.png'; pg.screenshot(path=lo, omit_background=True)
            bb = Image.open(lo).getchannel('A').getbbox()
            x0, y0, x1, y1 = max(0, bb[0] - 4), max(0, bb[1] - 4), min(560, bb[2] + 4), min(660, bb[3] + 4)
            # pass 2 at print scale: the ink
            html, ink = page_html(src, BOARD[d['slug']], PX)
            pg.set_content(html, wait_until='networkidle'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(120)
            pg.evaluate(ONE_LINE_JS)
            hi = f'{out}/_hi.png'
            pg.screenshot(path=hi, omit_background=True, full_page=True, clip={'x': x0 * PX, 'y': y0 * PX, 'width': (x1 - x0) * PX, 'height': (y1 - y0) * PX})
            im = Image.open(hi).convert('RGBA'); b2 = im.getchannel('A').getbbox(); ink_im = im.crop(b2)
            top_css = y0 + b2[1] / PX; cx_css = x0 + (b2[0] + b2[2]) / 2 / PX
            # the boards are a layout, not a scale drawing: the tallest blocks would run past the 16 in print area at
            # 11.5 in wide, so each print fits 11.5 x 15 in, and its place under the collar scales with it
            fit = min(1.0, 3450 / ink_im.width, 4500 / ink_im.height)
            if fit < 1: ink_im = ink_im.resize((max(1, round(ink_im.width * fit)), max(1, round(ink_im.height * fit))), Image.LANCZOS)
            w_in, h_in = ink_im.width / 300, ink_im.height / 300
            top_in, off_in = (top_css - COLLAR) / IN * fit, (cx_css - CENTRE) / IN * fit
            # the master: 12 x 16 in; the ink where the board put it, one inch of collar gap taken off the top
            master = Image.new('RGBA', (3600, 4800), (0, 0, 0, 0))
            x = int(round(1800 + off_in * 300 - ink_im.width / 2)); y = int(round(max(0.0, (top_in - 1.0) * 300)))
            x = min(max(x, 0), 3600 - ink_im.width); y = max(0, min(y, 4800 - ink_im.height))
            master.alpha_composite(ink_im, (x, y))
            master.save(f'{out}/{d["slug"]}.png', dpi=(300, 300))
            boxes[d['slug']] = dict(board=BOARD[d['slug']], ink=ink, fit=round(fit, 3), one_line=fixed, w_in=round(w_in, 2), h_in=round(h_in, 2), top_under_collar_in=round(top_in, 2),
                                    centre_offset_in=round(off_in, 2), master=[x, y, ink_im.width, ink_im.height])
            print(f'{d["slug"]:30s} {BOARD[d["slug"]]:13s} {w_in:4.1f} x {h_in:4.1f} in  top {top_in:4.1f} in under the collar  ink {ink}{"" if fit == 1 else f"  (fit {fit:.2f})"}{("  one line: " + "; ".join(fixed)) if fixed else ""}', flush=True)
        br.close()
    for f in ('_lo.png', '_hi.png'):
        if os.path.exists(f'{out}/{f}'): os.remove(f'{out}/{f}')
    json.dump(boxes, open(f'{out}/_boxes.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
