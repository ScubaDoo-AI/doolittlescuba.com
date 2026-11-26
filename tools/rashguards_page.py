#!/usr/bin/env python3
"""The Signature Series rash guards page, /rash-guards/ (handoff from Design & Production, 25 Nov 2026).

140 Shopify products (series:rg-sig): 14 Signature Series sites x 2 tones (Light: pastel body, deeper sleeves; Dark: deep
body, pastel sleeves) x 5 cuts, all-over printed to order by Printful. The site plate sits across the chest, the coordinates
down the right sleeve, the site name and flag down the left, the Doolittle Scuba lockup on the back.

The page: a deck of 28 cards (one per site and tone, the Light / Dark tabs as the deck's lines) whose open card has a style
picker (DS.rashCfg in js/deck.js: price, photos and shop link per cut), the five cuts with their prices, the spec, and links on.
Data: tools/rashguards.json (handles, cdn.shopify.com media, colour names, the body hex sampled from each flat lay).
Prices: PRICES below and DS.RG_PRICE in js/deck.js hold the same table; change both.
The shell (head, status banner, nav, collections bar, footer, sites data) is copied from signature/index.html, so the shared
tools keep it in step. Also adds the rash guards to js/designs.json (the home page search); tools/line_pages.py calls
index_entries() too, so its rebuild of designs.json keeps them.

  tools/rashguards_page.py      # (re)build rash-guards/index.html and the designs.json entries, then tools/bust.py
"""
import hashlib, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOP = 'https://shop.doolittlescuba.com'
E = html.escape

# style key, name, handle suffix, sizes, price line (Shopify, 25 Nov 2026)
PRICES = [
    ('mls', 'Men’s long sleeve', 'men-s-long-sleeve', 'XS–3XL', 69, '$69 · $72 in 2XL · $75 in 3XL'),
    ('wls', 'Women’s long sleeve', 'women-s-long-sleeve', 'XS–3XL', 69, '$69 · $72 in 2XL · $75 in 3XL'),
    ('mss', 'Men’s short sleeve', 'men-s-short-sleeve', '2XS–6XL', 62, '$62 · $2 more for each size above XL, up to $72'),
    ('yth', 'Youth long sleeve', 'youth-long-sleeve', '8–20', 45, '$45'),
    ('kid', 'Kids long sleeve', 'kids-long-sleeve', '2T–7', 39, '$39'),
]
# the Signature Series order (as /signature/)
ORDER = ['black-bart', 'bridge-span-14', 'blue-grotto', 'blue-water-park', 'dampier-strait', 'bali', 'rainbow-river', 'navy-llcat',
         'dive-land-park', 'thurmond-dam', 'thistlegorm', 'somosomo-strait', 'rainbow-reef', 'vuna-reef']


def data():
    d = json.load(open(f'{ROOT}/tools/rashguards.json', encoding='utf-8'))['items']
    return {(e['site'], e['tone']): e for e in d}


def sites():
    s = open(f'{ROOT}/signature/index.html', encoding='utf-8').read()
    return {x['slug']: x for x in json.loads(re.search(r'id="sites-data">(.*?)</script>', s, re.S).group(1))}


def ver(rel):
    return hashlib.sha1(open(f'{ROOT}/{rel}', 'rb').read()).hexdigest()[:8]


def colour_name(slug):
    return slug.replace('-', ' ').capitalize()


def w(url, px):
    return url + ('&' if '?' in url else '?') + f'width={px}'


def card(e, site):
    m = e['styles']['mls']['media']           # flat lay front, flat lay back, front view (worn), ...
    tone = e['tone']; name = site['name']; col = colour_name(e['colour'])
    text = f'{name} rash guard, {tone}: {col} body. {site.get("place", "")}. Signature Series plate across the chest, coordinates down the sleeve.'
    return (f'<figure class="sh rg" data-line="rg-{tone}" data-slug="{e["site"]}" data-code="{e["code"]}" data-colour="{E(col)}" data-hex="{e["hex"]}" '
            f'data-guide="/sites/{e["site"]}/" data-custom="none" data-text="{E(text)}">'
            f'<button type="button" class="sh-img" data-front="{m[0]}" data-sleeve="{m[2]}" data-back="{m[1]}" '
            f'data-cap="{E(name)} · Signature Series rash guard · {tone} · {E(col)}" data-umami-event="rashguard-open" data-umami-event-site="{e["site"]}" '
            f'aria-label="Open: {E(name)} rash guard, {tone}">'
            f'<img src="{w(m[0], 600)}" width="600" height="600" loading="lazy" decoding="async" draggable="false" alt="{E(name)} Signature Series rash guard, {tone}: {E(col)} body, the site plate across the chest (Printful mockup)"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{E(name)}</span></span><span class="dz-s">{E(site.get("place", ""))} · {tone} · from $39</span></figcaption></figure>')


STYLE = '''<style>
/* Rash guards: the Signature Series chart theme above, plus the white Printful panels */
.hero .sheet img{width:100%;height:auto;display:block;border-radius:6px;background:#fff;border:1px solid rgba(255,255,255,.14)}
#rash .deck .dk-pic,#rash .deck .dk-pic img{background:#fff}
.sh-open .big img{background:#fff}
.rg-st{display:flex;flex-wrap:wrap;gap:6px}
.rg-st button{font:inherit;font-size:var(--s-1);padding:5px 10px;border-radius:999px;border:1px solid var(--rule);background:transparent;color:inherit;cursor:pointer}
.rg-st button .mono{opacity:.7;margin-left:2px}
.rg-st button.on{background:var(--ink,#122A55);color:#fff;border-color:var(--ink,#122A55)}
.rg-st button:focus-visible{outline:2px solid #C8202A;outline-offset:2px}
.rg-cuts{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:20px 16px}
@media (max-width:900px){.rg-cuts{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:560px){.rg-cuts{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px 12px}}
.rg-cut{margin:0}
.rg-cut a.im{display:block;aspect-ratio:1;border:1px solid var(--rule);border-radius:8px;background:#fff;overflow:hidden}
.rg-cut img{width:100%;height:100%;object-fit:cover;display:block}
.rg-cut .t{display:block;font-weight:700;margin-top:8px}
.rg-cut .p{display:block;color:#B8862B;font-weight:700}
.rg-cut .s{display:block;color:var(--muted);font-size:var(--s-1)}
.rg-specs{display:grid;grid-template-columns:max-content 1fr;gap:6px 18px;margin:0;max-width:72ch}
.rg-specs dt{font-family:var(--f-data,ui-monospace,monospace);font-size:var(--s-1);color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.rg-specs dd{margin:0}
</style>'''


def main_block(D, S):
    light = [D[(s, 'light')] for s in ORDER]; dark = [D[(s, 'dark')] for s in ORDER]
    cards = ''.join(card(e, S[e['site']]) for e in light + dark)
    sw = ''.join(f'<li style="--sw:{e["hex"]}"><i></i>{E(colour_name(e["colour"]))}</li>' for e in light)
    bb = D[('black-bart', 'light')]
    cuts = ''.join(
        f'<figure class="rg-cut"><a class="im" href="{SHOP}/products/black-bart-signature-series-rash-guard-{suf}" data-umami-event="rashguard-cut" data-umami-event-style="{k}">'
        f'<img src="{w(bb["styles"][k]["media"][0], 400)}" width="400" height="400" loading="lazy" decoding="async" alt="Black Bart rash guard, {E(n.lower())}, light (Printful mockup)"></a>'
        f'<figcaption><span class="t">{E(n)}</span><span class="p">${p}</span><span class="s">{E(line[line.index("·")+2:]) if "·" in line else "One price, every size"}</span><span class="s">Sizes {E(sz)}</span></figcaption></figure>'
        for k, n, suf, sz, p, line in PRICES)
    hero = f'/img/rash-guards/hero.webp?v={ver("img/rash-guards/hero.webp")}'
    return f'''<main>
  <div class="deep hero-band"><div class="wrap">

    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Doolittle Scuba &middot; Signature Series rash guards</p>
        <h1>The dive site, worn in the water.</h1>
        <p class="lede">The fourteen Signature Series plates, drawn by hand, now printed to order on rash guards: the site across the chest, its coordinates down the long sleeve. Light, with a pastel body and deeper sleeves, or Dark, the other way round. Five cuts, $39 to $75.</p>
        <div class="cta">
          <a class="btn" data-umami-event="hero-rashguards" href="#rash">See the rash guards</a>
          <a class="btn ghost" data-umami-event="hero-rashguards-shop" href="{SHOP}/collections/rash-guards">Shop the collection</a>
          <a class="txt" data-umami-event="hero-signature" href="/signature/">The tees &rarr;</a>
        </div>
        <ul class="swatches" aria-label="Light tones">{sw}</ul>
      </div>
      <figure class="sheet" style="margin:0">
        <div class="coord mono" aria-label="14 sites, light and dark, five cuts">14 SITES &nbsp;&middot;&nbsp; LIGHT + DARK &nbsp;&middot;&nbsp; 5 CUTS</div>
        <img src="{hero}" alt="Three rash guards, flat: Black Bart in light chambray, the Thistlegorm in dark mulberry and Blue Grotto in light aqua, each with its site plate across the chest (Printful mockups)" width="1800" height="600">
      </figure>
    </div>
  </div></div>
  <div class="wrap">

    <section id="rash" aria-labelledby="rash-h">
      <div class="head">
        <h2 id="rash-h">The rash guards</h2>
        <p>Fourteen sites, each in a Light and a Dark tone; every site keeps its own colour, so the deck is the palette of the line. Open one to choose the cut: the price, photos and shop link follow your choice.</p>
      </div>
      <div class="sh-grid" id="sh-grid">{cards}</div>
      <p class="dz-note">Printful&rsquo;s mockups of our print files, not photographs; sample photos will replace them when the first run arrives. <a href="/#contact" data-umami-event="rashguards-contact">Get the launch email</a> to hear when they ship.</p>
    </section>

    <section id="cuts" aria-labelledby="cuts-h">
      <div class="head">
        <h2 id="cuts-h">Five cuts</h2>
        <p>Every site comes in all five, in both tones.</p>
      </div>
      <div class="rg-cuts">{cuts}</div>
    </section>

    <section id="rg-specs" aria-labelledby="specs-h">
      <div class="head"><h2 id="specs-h">The rash guard</h2></div>
      <dl class="rg-specs">
        <dt>Front</dt><dd>The site plate, drawn by hand, across the chest</dd>
        <dt>Sleeves</dt><dd>Long sleeves: the coordinates down one sleeve, the site name and flag down the other &middot; short sleeve: the flag on the sleeve</dd>
        <dt>Back</dt><dd>The Doolittle Scuba lockup between the shoulders</dd>
        <dt>Tones</dt><dd>Light: pastel body, deeper sleeves in the same hue &middot; Dark: deep body, pastel sleeves</dd>
        <dt>Made</dt><dd>All-over print, printed to order by Printful</dd>
        <dt>Prices</dt><dd>Men&rsquo;s and women&rsquo;s long sleeve $69 &middot; men&rsquo;s short sleeve $62 &middot; youth $45 &middot; kids $39 (larger adult sizes cost a little more)</dd>
      </dl>
    </section>

    <section id="make" aria-labelledby="make-h">
      <div class="head"><h2 id="make-h">More from the shop</h2></div>
      <div class="two">
        <div class="card">
          <h3>The Signature Series tees</h3>
          <p>The same fourteen plates on the back of a tee: black ink on soft pastels, white on the dark line.</p>
          <a class="btn ghost" href="/signature/" data-umami-event="make-signature">See the tees</a>
        </div>
        <div class="card">
          <h3>Get launch news</h3>
          <p>One email when the rash guards ship. No newsletter, no sharing your address.</p>
          <a class="btn" href="/#contact" data-umami-event="make-launch-news" data-umami-event-line="rash-guards">Tell me when they ship</a>
        </div>
      </div>
    </section>

  </div>
</main>'''


HEAD_TITLE = 'Signature Series rash guards · Doolittle Scuba'
DESC = 'The fourteen Signature Series dive-site plates, drawn by hand, printed to order on rash guards: the site across the chest, its coordinates down the sleeve. Light or dark, in men’s and women’s long sleeve, men’s short sleeve, youth and kids, $39 to $75.'


def page(D, S):
    src = open(f'{ROOT}/signature/index.html', encoding='utf-8').read()
    head, rest = src.split('<main>', 1)
    tail = rest.split('</main>', 1)[1]
    head = re.sub(r'<title>.*?</title>', f'<title>{E(HEAD_TITLE)}</title>', head)
    head = re.sub(r'(<meta (?:name|property)="(?:og:)?description" content=")[^"]*', lambda m: m.group(1) + E(DESC), head)
    head = head.replace('https://doolittlescuba.com/signature/', 'https://doolittlescuba.com/rash-guards/')
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\1Signature Series rash guards · the dive site, worn in the water', head)
    head = re.sub(r'(<meta property="og:image" content=")[^"]*', r'\1https://doolittlescuba.com/img/og/rash-guards.jpg', head)
    head = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', r'\1Two Signature Series rash guards, light and dark', head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>',
                  lambda m: '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": HEAD_TITLE,
                                                                               "url": "https://doolittlescuba.com/rash-guards/", "description": DESC}, ensure_ascii=False) + '</script>', head, flags=re.S)
    head = head.replace('</head>', STYLE + '\n</head>', 1)
    head = head.replace(' aria-current="page"', '')          # the collections bar: no line is this page
    tail = re.sub(r'<script>\nDS\.lightbox\(\);\nDS\.deck\(.*?</script>',
                  lambda m: '<script>\nDS.lightbox();\nDS.deck(\'rash\',\'sh-grid\',DS.rashCfg({contact:\'/#contact\', media:' + media_js(D) + '}));\n'
                            'if(/^#d-rg-/.test(location.hash)){ var r=document.getElementById(\'rash\'); if(r) r.scrollIntoView({block:\'start\'}); }\n</script>', tail, flags=re.S)
    return head + main_block(D, S) + tail


def media_js(D):
    return json.dumps({f'{s}|{t}': {k: v['media'] for k, v in e['styles'].items()} for (s, t), e in D.items()}, separators=(',', ':'))


def index_entries(D=None, S=None):
    """One search entry per site for js/designs.json (the home page search): 'rash guard', the site, both colours."""
    D = D or data(); S = S or sites(); out = []
    for s in ORDER:
        lt, dk = D[(s, 'light')], D[(s, 'dark')]; x = S[s]
        q = ' '.join([x['name'], 'rash guard rashguard rash guards swim surf', 'Signature Series', x.get('place', ''), x.get('water', ''),
                      colour_name(lt['colour']), colour_name(dk['colour']), 'light dark long sleeve short sleeve women men youth kids'])
        out.append(dict(slug=f'rg-{s}', name=f'{x["name"]} rash guard', sub=x.get('place', ''), line='Signature Series rash guards', page='/rash-guards/',
                        thumb=w(lt['styles']['mls']['media'][0], 520), status='available', q=re.sub(r'\s+', ' ', q).lower()))
    return out


def build():
    D, S = data(), sites()
    os.makedirs(f'{ROOT}/rash-guards', exist_ok=True)
    open(f'{ROOT}/rash-guards/index.html', 'w', encoding='utf-8').write(page(D, S))
    p = f'{ROOT}/js/designs.json'; idx = [x for x in json.load(open(p, encoding='utf-8')) if not x['slug'].startswith('rg-')] + index_entries(D, S)
    json.dump(idx, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    sm = f'{ROOT}/sitemap.xml'; s = open(sm, encoding='utf-8').read(); loc = 'https://doolittlescuba.com/rash-guards/'
    if loc not in s:
        import datetime
        s = s.replace('  <url><loc>https://doolittlescuba.com/custom/</loc>', f'  <url><loc>{loc}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>\n  <url><loc>https://doolittlescuba.com/custom/</loc>', 1)
        open(sm, 'w', encoding='utf-8').write(s)
    print('rash-guards/index.html:', len(D), 'cards; designs.json:', len(idx))


if __name__ == '__main__':
    build()
