#!/usr/bin/env python3
"""Each site guide is the place to shop that site (26 Nov 2026, review item #2).

Adds a "Wear <site>" strip right under the intro of every /sites/<slug>/ guide: every product made for that site, in one row
of cards: light tee, dark tee, cap, rash guard light and dark (men's long sleeve shown; the other four cuts on /rash-guards/),
organic tees and the organic cap. Each card links to its product in the store and carries data-buy, so once the cart is
live (js/cart.js LIVE=true) it gets a size picker on the page, like every other card on the site.

Sources (nothing is typed by hand):
  products, handles, prices   js/catalog.json   (rebuilt daily from Shopify by tools/catalog_map.py)
  photos                      the cards already on signature/index.html (tees), index.html #hats (caps),
                              organic/index.html (organic), tools/rashguards.json (rash guards, flat lay front)
  sites                       tools/pairs.py SITES

Idempotent: the strip sits between <!-- WEAR:START --> and <!-- WEAR:END --> and is rewritten each run. A card whose
product or photo is missing is left out. Run after any of the sources change, then tools/bust.py.
"""
import html as H, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairs import SITES, CAP_SLUG, GUIDE, SHOP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, END = '<!-- WEAR:START -->', '<!-- WEAR:END -->'
read = lambda p: open(os.path.join(ROOT, p), encoding='utf-8').read()

CAT = json.load(open(os.path.join(ROOT, 'js/catalog.json')))
RG = json.load(open(os.path.join(ROOT, 'tools/rashguards.json')))['items']
SIG, HOME, ORG = read('signature/index.html'), read('index.html'), read('organic/index.html')

CSS = ('<style>'
       '.wear{margin-top:0}.wear .lede2{max-width:62ch;color:var(--muted,#5A6B7D);margin:-6px 0 18px}'
       '.wear-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:18px}'
       '.wear-grid figure{margin:0;display:flex;flex-direction:column}'
       '.wear-grid .ph{display:block;aspect-ratio:1;border-radius:8px;overflow:hidden;background:#EEF2F5}'
       '.wear-grid .ph img{width:100%;height:100%;object-fit:cover;transition:transform .25s}'
       '.wear-grid .ph:hover img{transform:scale(1.04)}'
       '.wear-grid figcaption{padding-top:9px;display:grid;gap:2px}'
       '.wear-grid .k{font-family:var(--f-data);font-size:.6875rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted,#5A6B7D)}'
       '.wear-grid .n{font-weight:700;line-height:1.25}.wear-grid .n a{color:inherit;text-decoration:none}.wear-grid .n a:hover{text-decoration:underline}'
       '.wear-grid .p{font-family:var(--f-data);font-size:.8125rem}'
       '.wear-grid .pill{justify-self:start;margin-top:4px}'
       '@media (max-width:520px){.wear-grid{grid-template-columns:1fr 1fr;gap:14px}}'
       '</style>')


def card_img(page, attr_pat):
    """The first <img src> inside the card whose opening tag matches attr_pat."""
    m = re.search(r'<figure class="sh"[^>]*' + attr_pat + r'[^>]*>.*?<img src="([^"]+)"', page, re.S)
    if not m: return None
    src = H.unescape(m.group(1))
    return src if src.startswith(('http', '/')) else '/' + src   # source pages sit at the root (index.html, organic/ uses absolute)


def price(stems):
    ps = [v[2] for s in stems if s in CAT for v in CAT[s]['v']]
    if not ps: return None
    lo = min(ps)
    return f'${lo:.0f}' if all(p == lo for p in ps) else f'from ${lo:.0f}'


def card(kind, name, stem, img, alt, href=None, stems=None, note=''):
    if stem not in CAT or not img: return ''
    href = href or f'{SHOP}/products/{CAT[stem]["h"]}'
    pr = price(stems or [stem])
    return (f'<figure data-buy="{stem}"><a class="ph" href="{href}" data-umami-event="guide-wear" data-umami-event-item="{stem}">'
            f'<img src="{H.escape(img)}" width="600" height="600" loading="lazy" decoding="async" alt="{H.escape(alt)}"></a>'
            f'<figcaption><span class="k">{kind}</span><span class="n"><a href="{href}" data-umami-event="guide-wear" data-umami-event-item="{stem}">{H.escape(name)}</a></span>'
            f'<span class="p">{pr}{note}</span><span class="pill available">Coming soon</span></figcaption></figure>')


def rash(slug, tone):
    for it in RG:
        if it['site'] == slug and it['tone'] == tone and 'mls' in it['styles']:
            m = it['styles']['mls']['media']
            return m[0] + ('&' if '?' in m[0] else '?') + 'width=600' if m else None


def strip(slug, code, name):
    h = CAP_SLUG.get(slug, slug)
    rg = lambda t: [f'DS-{code}-RG{c}-{t}' for c in ('MLS', 'WLS', 'MSS', 'YTH', 'KID')]
    cards = [
        card('Tee · light', f'{name} tee', f'DS-{code}-T', card_img(SIG, f'data-line="plates" data-slug="{slug}"'), f'{name} Signature Series tee, light'),
        card('Tee · dark', f'{name} dark tee', f'DS-{code}-TD', card_img(SIG, f'data-line="dark" data-slug="{slug}"'), f'{name} Signature Series tee, dark'),
        card('Cap', f'{name} cap', f'DS-{code}-CD', card_img(HOME, f'data-slug="cap-dark-{h}"'), f'{name} embroidered site cap'),
        card('Rash guard · light', f'{name} rash guard', f'DS-{code}-RGMLS-L', rash(slug, 'light'), f'{name} rash guard, light, flat lay',
             href='/rash-guards/', stems=rg('L'), note=' · 5 cuts'),
        card('Rash guard · dark', f'{name} dark rash guard', f'DS-{code}-RGMLS-D', rash(slug, 'dark'), f'{name} rash guard, dark, flat lay',
             href='/rash-guards/', stems=rg('D'), note=' · 5 cuts'),
        card('Organic tee', f'{name} organic tee', f'DS-{code}-TO', card_img(ORG, f'data-buy="DS-{code}-TO"'), f'{name} organic tee, light'),
        card('Organic tee · dark', f'{name} organic dark tee', f'DS-{code}-TDO', card_img(ORG, f'data-buy="DS-{code}-TDO"'), f'{name} organic tee, dark'),
        card('Organic cap', f'{name} organic cap', f'DS-{code}-CO', card_img(ORG, f'data-buy="DS-{code}-CO"'), f'{name} organic cap'),
    ]
    cards = [c for c in cards if c]
    if not cards: return None
    pair = ''
    if f'DS-{code}-PR' in CAT:
        pair = (f' Any tee with any cap is $8 off as <a href="{SHOP}/products/{h}-pair-light" data-umami-event="guide-pair-light">a pair</a>.')
    return (f'{START}{CSS}<section class="wear" aria-labelledby="wear-h"><div class="head"><h2 id="wear-h">Wear {H.escape(name)}</h2></div>'
            f'<p class="lede2">Everything we make for this site, in one place.{pair}</p>'
            f'<div class="wear-grid">{"".join(cards)}</div></section>{END}')


def main():
    n = 0
    for slug, code, name, *_ in SITES:
        p = os.path.join(ROOT, 'sites', GUIDE.get(slug, slug), 'index.html')
        if not os.path.exists(p): print('no guide:', slug); continue
        s = s0 = open(p, encoding='utf-8').read()
        block = strip(slug, code, name)
        if block is None: print('no products:', slug); continue
        if START in s:
            s = re.sub(re.escape(START) + '.*?' + re.escape(END), lambda m: block, s, flags=re.S)
        else:
            anchor = '<section aria-labelledby="site-h">'
            assert s.count(anchor) == 1, p
            s = s.replace(anchor, block + '\n    ' + anchor, 1)
        if s != s0:
            open(p, 'w', encoding='utf-8').write(s); n += 1
        print(f'{slug}: {block.count("<figure")} cards')
    print(n, 'guides changed; now run tools/bust.py')


if __name__ == '__main__':
    main()
