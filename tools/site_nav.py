#!/usr/bin/env python3
"""The site menu, in one place (26 Nov 2026: 13 links cut to five: Shop, Dive sites, Custom, Our story, Cart).

Shop and Our story open a drop-down (<details>, so it works without JavaScript):
  Shop       By collection: All collections, the five lines, Organic
             By gear:       Rash guards, Caps, Jackets, Stickers, Towels
  Our story  About us, Logbook, Workshop, Contact

The inner links keep their old Umami event names (nav-collections, nav-hats, ...) so the numbers carry on.
Styles: css/nav.css. Behaviour (one open at a time, close on outside click / Escape / link): js/nav.js.

Usage: tools/site_nav.py   rewrites the header menu on every page that has one, marks the current page, adds the
       nav.css / nav.js references where missing, then run tools/bust.py. Re-run it after any page generator
       (line_pages.py, stickers_page.py, towels_page.py, rashguards_page.py, ...), since they copy shells from other pages.
       tools/line_pages.py's nav() calls html() here, so new pages start with the right menu.
"""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COLLECTIONS = [('/#lines', 'All collections', 'nav-collections'),
               ('/signature/', 'Signature Series', 'nav-signature'),
               ('/certified-ish/', 'Certified-ish', 'nav-certified-ish'),
               ('/off-world/', 'Off-World Hunt Club', 'nav-off-world'),
               ('/1n73ll1g3nc3/', '1N73LL1G3NC3', 'nav-n73'),
               ('/surface-interval/', 'Surface Interval', 'nav-surface-interval'),
               ('/organic/', 'Organic', 'nav-organic')]
GEAR = [('/rash-guards/', 'Rash guards', 'nav-rashguards'),
        ('/#hats', 'Caps', 'nav-hats'),
        ('/#jackets', 'Jackets', 'nav-jackets'),
        ('/stickers/', 'Stickers', 'nav-stickers'),
        ('/towels/', 'Towels', 'nav-towels')]
STORY = [('/about/', 'About us', 'nav-about'),
         ('/#logbook', 'Logbook', 'nav-logbook'),
         ('/workshop/', 'Workshop', 'nav-workshop'),
         ('/#contact', 'Contact', 'nav-contact')]
CART = 'https://shop.doolittlescuba.com/cart'

NAV_RE = re.compile(r'<nav aria-label="(?:Site|Sections)"[^>]*>.*?</nav>', re.S)
CSS_TAG = '<link rel="stylesheet" href="/css/nav.css">'
JS_TAG = '<script defer src="/js/nav.js"></script>'


def _a(href, label, ev, cur):
    c = ' aria-current="page"' if href == cur else ''
    return f'<a href="{href}"{c} data-umami-event="{ev}">{label}</a>'


def _dd(name, ev, cols, cur, cls=''):
    hit = any(h == cur for _, links in cols for h, _, _ in links)
    body = ''.join((f'<div class="dd-col"><p class="dd-h">{head}</p>' if head else '<div class="dd-col">')
                   + ''.join(_a(*l, cur) for l in links) + '</div>' for head, links in cols)
    two = ' dd-two' if len(cols) > 1 else ''
    return (f'<details class="dd{cls}"><summary{" class=\"cur\"" if hit else ""} data-umami-event="{ev}">{name}</summary>'
            f'<div class="dd-panel{two}">{body}</div></details>')


def html(cur=''):
    """The menu for the page at path `cur` (e.g. '/signature/'; site guides pass '/#map')."""
    return ('<nav aria-label="Site">'
            + _dd('Shop', 'nav-shop', [('By collection', COLLECTIONS), ('By gear', GEAR)], cur)
            + _a('/#map', 'Dive sites', 'nav-map', cur)
            + _a('/custom/', 'Custom', 'nav-custom', cur)
            + _dd('Our story', 'nav-story', [('', STORY)], cur, ' dd-r')
            + f'<a href="{CART}" data-umami-event="nav-cart">Cart</a></nav>')


def current(rel):
    """The menu entry a page belongs to, from its path relative to the site root."""
    d = os.path.dirname(rel).replace(os.sep, '/')
    if d == '':
        return ''                      # home: no current entry (its sections are anchors)
    if d.startswith('sites/'):
        return '/#map'                 # site guides sit under Dive sites
    return f'/{d.split("/")[0]}/'


def patch(path):
    rel = os.path.relpath(path, ROOT)
    s = open(path, encoding='utf-8').read()
    if not NAV_RE.search(s) or '<header class="top"' not in s:
        return False
    out = NAV_RE.sub(lambda m: html(current(rel)), s, count=1)
    if '/css/nav.css' not in out:
        out = out.replace('</head>', CSS_TAG + '\n</head>', 1)
    if '/js/nav.js' not in out:
        out = out.replace('</body>', JS_TAG + '\n</body>', 1)
    if out != s:
        open(path, 'w', encoding='utf-8').write(out)
    return out != s


def main():
    skip = ('renders/', 'shopify-theme/', 'tools/', 'policies/')
    n = 0
    for p in sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
        if os.path.relpath(p, ROOT).replace(os.sep, '/').startswith(skip):
            continue
        if patch(p):
            n += 1; print('menu:', os.path.relpath(p, ROOT))
    print(n, 'pages updated; now run tools/bust.py')


if __name__ == '__main__':
    main()
