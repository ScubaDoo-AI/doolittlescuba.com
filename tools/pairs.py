#!/usr/bin/env python3
"""The pairs (12 Nov 2026): one set product per site and tee line — the site's Dark cap with its Signature Series tee,
light or dark — sold as a Shopify fixed bundle (productBundleCreate; the components stay the cap and tee products, so
Printful and the embroiderer see ordinary cap and tee line items on an order).

  28 products: <Site> — The pair · light tee  /  <Site> — The pair · dark tee   handle <slug>-pair-light / <slug>-pair-dark
  options  Cap size S/M · L/XL  ×  Tee size S–3XL  = 12 variants, price $69 (tee S–XL) / $72 (2XL, 3XL)  — $8 under the two apart
  SKU      DS-<code>-PR-<SM|LXL>-<size> (light) / DS-<code>-PRD-… (dark)
  image    img/pairs/<slug>-<line>.jpg: the cap render beside the tee mockup (same #F5F5F5 ground), 2000 × 1200
  tags     pair, pair:<line>, site:<slug>, cap, tee, signature, coming-soon; type Pair; vendor Doolittle Scuba; DRAFT
Home Port (custom) and the brand caps have no pair.

usage:  tools/pairs.py images                 # writes img/pairs/*.jpg
        tools/pairs.py plan [--json]          # the 28 products: ids of the components, option ids, copy
Component ids are the store's as of 12 Nov 2026 (tools/printful_caps.py has the cap variants; the tees are from the store)."""
import os, sys, json, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOP = 'https://doolittlescuba.myshopify.com'
PRICE, PRICE_XXL = '69.00', '72.00'
TEE_SIZES = ['S', 'M', 'L', 'XL', '2XL', '3XL']
# slug, code, name, cap product id, cap option id, light tee product id, light option id, dark tee product id, dark option id, cap colour, light tee colour, dark tee colour
SITES = [
    ('bali', 'BAL', 'Bali', 10398567661754, 13341400334522, 10398077943994, 13340629369018, 10398547181754, 13341363306682, 'navy', 'terracotta', 'denim'),
    ('black-bart', 'BBT', 'Black Bart', 10398567727290, 13341400367290, 10398067065018, 13340613411002, 10398547214522, 13341363339450, 'dark grey', 'light blue', 'pepper'),
    ('blue-grotto', 'BGR', 'Blue Grotto', 10398567760058, 13341400465594, 10398077026490, 13340627828922, 10398547247290, 13341363372218, 'purple', 'mint', 'grape'),
    ('blue-water-park', 'BWP', 'Blue Water Park', 10398567792826, 13341400498362, 10398077092026, 13340627927226, 10398547312826, 13341363470522, 'black', 'teal', 'black'),
    ('bridge-span-14', 'BSP', 'Bridge Span 14', 10398567825594, 13341400531130, 10398076960954, 13340627730618, 10398547345594, 13341363503290, 'brown', 'Caribbean blue', 'espresso'),
    ('dampier-strait', 'DAM', 'Dampier Strait', 10398568644794, 13341402103994, 10398077157562, 13340628025530, 10398562386106, 13341390799034, 'navy', 'butter', 'true navy'),
    ('dive-land-park', 'DLP', 'Dive Land Park', 10398568677562, 13341402136762, 10398078140602, 13340629631162, 10398562451642, 13341390897338, 'dark grey', 'aqua', 'graphite'),
    ('navy-llcat', 'NAV', 'Navy LLCAT', 10398568743098, 13341402202298, 10398078042298, 13340629500090, 10398562484410, 13341390930106, 'navy', 'granite', 'navy'),
    ('rainbow-reef', 'RRF', 'Rainbow Reef', 10398568775866, 13341402235066, 10398079058106, 13340631171258, 10398562549946, 13341391028410, 'olive', 'lavender', 'sage'),
    ('rainbow-river', 'RRV', 'Rainbow River', 10398569758906, 13341404135610, 10398078009530, 13340629467322, 10398562582714, 13341391061178, 'maroon', 'sage', 'wine'),
    ('somosomo-strait', 'SOM', 'Somosomo Strait', 10398569791674, 13341404168378, 10398078992570, 13340631072954, 10398564122810, 13341393911994, 'spruce', 'coral', 'emerald'),
    ('thistlegorm', 'THI', 'The Thistlegorm', 10398570971322, 13341406429370, 10398078927034, 13340630974650, 10398564155578, 13341393944762, 'spruce', 'berry pink', 'blue spruce'),
    ('thurmond-dam', 'THD', 'Thurmond Dam', 10398571036858, 13341406494906, 10398078173370, 13340629663930, 10398564221114, 13341394043066, 'navy', 'ivory', 'midnight'),
    ('vuna-reef', 'VUN', 'Vuna Reef', 10398571069626, 13341406527674, 10398079156410, 13340631302330, 10398564253882, 13341394075834, 'spruce', 'pink', 'moss'),
]
CAP_SLUG = {'thistlegorm': 'the-thistlegorm'}          # the cap and tee handles carry "the-"; the site slug does not
GUIDE = {'thistlegorm': 'thistlegorm'}


def handle(slug, line): return f"{CAP_SLUG.get(slug, slug)}-pair-{line}"
def the(name): return name if name.startswith('The ') else 'the ' + name


def description(slug, code, name, line, cap_col, tee_col):
    n = the(name); tee = f"{name} — Signature Series {'Dark ' if line == 'dark' else ''}tee"
    cap_url = f"{SHOP}/products/{CAP_SLUG.get(slug, slug)}-dark-cap"
    tee_url = f"{SHOP}/products/{CAP_SLUG.get(slug, slug)}-signature-series-{'dark-' if line == 'dark' else ''}tee"
    return (f"<p><strong>The pair</strong> — {n} cap and {n} tee together, $8 under the two apart.</p>"
            f"<p>The <a href=\"{cap_url}\">{name} Dark cap</a> — Flexfit 6277 in {cap_col}, embroidered on three sides: the site front across the front panels, "
            f"the DS mark on the left side, “Do - A - Little Scuba” arched over the back — with the <a href=\"{tee_url}\">{tee}</a> in {tee_col}: "
            f"the full {name.replace('The ', '')} plate on the back, the site block on the chest, the shark mark on the sleeve.</p>"
            f"<ul>\n<li>\n<strong>Cap:</strong> Flexfit 6277 structured fitted cap, {cap_col}. S/M (6¾–7¼) or L/XL (7⅛–7⅝).</li>\n"
            f"<li>\n<strong>Tee:</strong> Comfort Colors 1717, garment-dyed, {tee_col}. S–3XL.</li>\n"
            f"<li>\n<strong>Price:</strong> $69 with the tee in S–XL, $72 in 2XL–3XL — $35 + $42 apart.</li>\n"
            f"<li>\n<strong>Mix it:</strong> want a different tee with this cap, or the light one instead of the dark? Every cap pairs with every Signature Series tee — "
            f"the other pairs are under <a href=\"{SHOP}/collections/pairs\">Pairs</a>.</li>\n</ul>"
            f"<p>Shown as mockups, not photographs: the first caps are being sampled now.</p>"
            f"<p><a href=\"https://doolittlescuba.com/sites/{GUIDE.get(slug, slug)}/\">Site guide</a></p>")


def plan():
    out = []
    for slug, code, name, cap_pid, cap_opt, lt_pid, lt_opt, dk_pid, dk_opt, cap_col, lt_col, dk_col in SITES:
        for line, tee_pid, tee_opt, tee_col in (('light', lt_pid, lt_opt, lt_col), ('dark', dk_pid, dk_opt, dk_col)):
            title = f"{name} — The pair · {line} tee"
            comps = [{'productId': f'gid://shopify/Product/{cap_pid}', 'quantity': 1,
                      'optionSelections': [{'componentOptionId': f'gid://shopify/ProductOption/{cap_opt}', 'name': 'Cap size', 'values': ['S/M', 'L/XL']}]},
                     {'productId': f'gid://shopify/Product/{tee_pid}', 'quantity': 1,
                      'optionSelections': [{'componentOptionId': f'gid://shopify/ProductOption/{tee_opt}', 'name': 'Tee size', 'values': TEE_SIZES}]}]
            sku = f"DS-{code}-{'PR' if line == 'light' else 'PRD'}"
            out.append(dict(slug=slug, code=code, name=name, line=line, title=title, handle=handle(slug, line), sku=sku,
                            image=f'img/pairs/{slug}-{line}.jpg', components=comps,
                            tags=['pair', f'pair:{line}', f'site:{slug}', 'cap', 'tee', 'signature', 'coming-soon'],
                            description=description(slug, code, name, line, cap_col, tee_col),
                            prices={s: (PRICE_XXL if s in ('2XL', '3XL') else PRICE) for s in TEE_SIZES}))
    return out


def images():
    os.makedirs(f'{ROOT}/img/pairs', exist_ok=True); n = 0
    for slug, *_ in SITES:
        cap = Image.open(f'{ROOT}/img/hats/dark/cap-dark-{CAP_SLUG.get(slug, slug)}-front.webp').convert('RGB')
        for line in ('light', 'dark'):
            tee = Image.open(f'{ROOT}/img/shirts/{"dark/" if line == "dark" else ""}{slug}-front.webp').convert('RGB')
            W, H = 2000, 1200; out = Image.new('RGB', (W, H), (245, 245, 245))
            out.paste(cap.resize((1040, 1040), Image.LANCZOS), (20, 80)); out.paste(tee.resize((1040, 1040), Image.LANCZOS), (940, 80))
            out.save(f'{ROOT}/img/pairs/{slug}-{line}.jpg', quality=90, optimize=True); n += 1
    print(n, 'pair images in img/pairs/')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    if cmd == 'images': images()
    else:
        P = plan()
        if '--json' in sys.argv: print(json.dumps(P, ensure_ascii=False, indent=1))
        else:
            for p in P: print(f"{p['sku']:12s} {p['handle']:34s} {p['title']}")
            print(f"\n{len(P)} pair products · 12 variants each · ${PRICE} / ${PRICE_XXL}")
