#!/usr/bin/env python3
"""The store's four policies, linked from every footer and reachable at short site paths.

Shopify holds the policies (Settings → Policies). The storefront is password-protected, so the public copies are the
checkout-hosted pages; this script keeps four tiny redirect pages on the site — /privacy/, /terms/, /shipping/,
/returns/ — pointing at them, and a footer line (between POLICIES markers) on every page. Re-run after adding a page
or when a policy URL changes; it is idempotent.

  tools/policies.py            # write the redirect pages, patch every footer
"""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOP = 'https://checkout.shopify.com/78733508794/policies/'
POLICIES = [  # path, label, Shopify policy page (ids from shop.shopPolicies, 13 Nov 2026)
    ('privacy',  'Privacy',  SHOP + '43085070522.html?locale=en'),
    ('terms',    'Terms',    SHOP + '43703533754.html?locale=en'),
    ('shipping', 'Shipping', SHOP + '43703566522.html?locale=en'),
    ('returns',  'Returns',  SHOP + '43703435450.html?locale=en'),   # Shopify calls it the refund policy
]
START, END = '<!-- POLICIES:START -->', '<!-- POLICIES:END -->'
ANCHOR = '<p class="mono">hello@doolittlescuba.com &middot; orders@doolittlescuba.com</p>'

REDIRECT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{label} — Doolittle Scuba</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace({url!r});</script>
</head>
<body><a href="{url}">Doolittle Scuba — {label} policy</a></body>
</html>
"""


def nav():
    links = ' &middot; '.join(f'<a href="/{p}/" data-umami-event="policy" data-umami-event-doc="{p}">{l}</a>' for p, l, _ in POLICIES)
    return f'{START}<nav class="policies mono" aria-label="Store policies">{links}</nav>{END}'


def patch(path):
    h = open(path, encoding='utf-8').read()
    if '<footer' not in h or ANCHOR not in h: return False
    new = nav()
    if START in h:
        out = re.sub(re.escape(START) + '.*?' + re.escape(END), lambda m: new, h, flags=re.S)
    else:
        out = h.replace(ANCHOR, ANCHOR + '\n      ' + new, 1)
    if out != h: open(path, 'w', encoding='utf-8').write(out)
    return out != h


def main():
    for p, l, url in POLICIES:
        d = os.path.join(ROOT, p); os.makedirs(d, exist_ok=True)
        f = os.path.join(d, 'index.html'); s = REDIRECT.format(label=l, url=url)
        if not os.path.exists(f) or open(f, encoding='utf-8').read() != s: open(f, 'w', encoding='utf-8').write(s); print('redirect', p + '/')
    n = 0
    for f in sorted(glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)):
        if patch(f): n += 1; print('footer', os.path.relpath(f, ROOT))
    print(n, 'footers changed')


if __name__ == '__main__':
    main()
