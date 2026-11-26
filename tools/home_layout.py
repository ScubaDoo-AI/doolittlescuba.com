#!/usr/bin/env python3
"""The home page as a short guided path (26 Nov 2026, review item #3).

Order after this:  hero → Start here (8 picks) → The collections + search → Shop by dive site (the map) → Make it yours
                   → Every mark by hand → About → Logbook → Wear it where you dove → Topside
Moved off the home page onto pages of their own (built here from the home page's own markup, the first time):
  /caps/      the hats deck (site caps, brand caps, the beanie) with its deck config
  /jackets/   the two jackets
The sticker strip left the home page too; /stickers/ already has every pack (tools/stickers_page.py now skips the home
page when it has no #stickers section). The Start here picks include the Achievement Unlocked set.

Re-running is safe: pages are only built from the home page while it still holds #hats / #jackets; the Start here and
Make it yours blocks sit between markers (PICKS, MAKE) and are rewritten from js/catalog.json and the cards on the
other pages, so prices and photos follow the store. Then tools/site_nav.py and tools/bust.py.
"""
import html as H, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import line_pages as LP
from pairs import SHOP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda p: open(os.path.join(ROOT, p), encoding='utf-8').read()
wr = lambda p, s: open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)
CAT = json.load(open(os.path.join(ROOT, 'js/catalog.json')))
RG = json.load(open(os.path.join(ROOT, 'tools/rashguards.json')))['items']


def absolutise(s):
    return re.sub(r'\b(src|data-front|data-back|data-sleeve|data-full|data-art)="img/', r'\1="/img/', s)


def section(src, sid):
    i = src.index(f'<section id="{sid}"'); j = src.index('</section>', i) + len('</section>')
    return i, j


# ------------------------------------------------------------------------------------------------ pages of their own
CAPS_DESC = ('Embroidered caps from Doolittle Scuba: a cap for every dive site we have drawn, the brand caps, the Home Port cap '
             'with your own coordinates, and The Mark beanie. Flexfit 6277, S/M and L/XL.')
JACKETS_DESC = ('Two shells for the boat ride home, Black or Navy, with the DS mark embroidered on the left chest: '
                'the Champion packable anorak and the SOL\'S windbreaker.')


def shell(slug, title, desc, og_alt):
    """Head and tail from the towels page (same shell every generated page uses), re-pointed at /<slug>/."""
    src = rd('towels/index.html')
    head, rest = src.split('<main>', 1); tail = rest.split('</main>', 1)[1]
    E = lambda s: H.escape(s, quote=True)
    head = re.sub(r'<title>.*?</title>', f'<title>{E(title)}</title>', head)
    head = re.sub(r'(<meta (?:name|property)="(?:og:)?description" content=")[^"]*', lambda m: m.group(1) + E(desc), head)
    head = head.replace('https://doolittlescuba.com/towels/', f'https://doolittlescuba.com/{slug}/')
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(title.split(' · ')[0]), head)
    head = re.sub(r'(<meta property="og:image" content=")[^"]*', r'\1https://doolittlescuba.com/img/og/home.jpg', head)
    head = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + E(og_alt), head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>',
                  lambda m: '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": title,
                                                                                "url": f"https://doolittlescuba.com/{slug}/", "description": desc}, ensure_ascii=False) + '</script>',
                  head, count=1, flags=re.S)
    head = re.sub(r'<style>\n/\* Water Hazard.*?</style>\n?', '', head, flags=re.S)   # the towels page's own colours
    return head, tail


def hero(eyebrow, h1, lede, coord, img, alt, anchor, label):
    return f'''<main>
  <div class="deep hero-band"><div class="wrap">
    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Doolittle Scuba &middot; {eyebrow}</p>
        <h1>{h1}</h1>
        <p class="lede">{lede}</p>
        <div class="cta"><a class="btn" href="#{anchor}" data-umami-event="hero-{anchor}">{label}</a><a class="btn ghost" href="/custom/" data-umami-event="hero-custom">Make it yours</a></div>
      </div>
      <figure class="sheet" style="margin:0">
        <div class="coord mono">{coord}</div>
        <img src="{img}" alt="{alt}" width="1200" height="1200" style="aspect-ratio:1;object-fit:cover;background:#EEF2F5">
      </figure>
    </div>
  </div></div>
  <div class="wrap">
'''


def build_pages(home):
    if '<section id="hats"' not in home:
        return home
    # caps
    i, j = section(home, 'hats'); hats = absolutise(home[i:j])
    m = re.search(r"DS\.deck\('hats','ht-grid',\{.*?\n  \}\);", home, re.S); cfg = m.group(0).replace("'#contact'", "'/#contact'")
    head, tail = shell('caps', 'Caps · Doolittle Scuba', CAPS_DESC, 'Doolittle Scuba embroidered caps')
    cap_img = re.search(r'data-slug="cap-dark-vuna-reef".*?<img src="([^"]+)"', hats, re.S).group(1)
    body = hero('Caps', 'A cap for every site.', 'Every cap is embroidered on three sides: the site across the front, the DS mark on the side, '
                '&ldquo;Do - A - Little Scuba&rdquo; across the back. Site caps $38, brand caps $36, Home Port $48 with your own coordinates.',
                'FLEXFIT 6277 &nbsp;&middot;&nbsp; EMBROIDERED &nbsp;&middot;&nbsp; S/M &middot; L/XL', cap_img, 'The Vuna Reef cap, front', 'hats', 'The caps')
    tail = re.sub(r'<script>DS\.lightbox\(\);</script>', lambda _: '<script>\nDS.lightbox();\n' + cfg + '\n</script>', tail, count=1)
    os.makedirs(os.path.join(ROOT, 'caps'), exist_ok=True)
    wr('caps/index.html', head + body + '    ' + hats + '\n  </div>\n</main>' + tail)
    # jackets
    i, j = section(home, 'jackets'); jk = absolutise(home[i:j])
    head, tail = shell('jackets', 'Jackets · Doolittle Scuba', JACKETS_DESC, 'Doolittle Scuba jackets')
    jk_img = re.search(r'<img src="([^"]+)"', jk).group(1)
    body = hero('Jackets', 'For the boat ride home.', 'Two shells, Black or Navy, with one thing on them: the DS mark, embroidered on the left chest in white and red. '
                'The Champion packable anorak, $85, and the SOL&rsquo;S windbreaker, $45. S to 2XL.',
                'EMBROIDERED &nbsp;&middot;&nbsp; BLACK OR NAVY &nbsp;&middot;&nbsp; S&ndash;2XL', jk_img, 'The Champion packable anorak, black', 'jackets', 'The jackets')
    os.makedirs(os.path.join(ROOT, 'jackets'), exist_ok=True)
    wr('jackets/index.html', head + body + '    ' + jk + '\n  </div>\n</main>' + tail)
    print('built /caps/ and /jackets/')
    # take them (and the sticker strip) off the home page, with their deck calls
    for sid in ('hats', 'jackets', 'stickers'):
        if f'<section id="{sid}"' in home:
            i, j = section(home, sid); home = home[:i].rstrip() + '\n' + home[j:]
    home = home.replace(m.group(0) + '\n', '').replace(m.group(0), '')
    home = re.sub(r"DS\.deck\('stickers','pk-grid',[^\n]*\n", '', home)
    return home


# ------------------------------------------------------------------------------------------------ Start here
CSS = ('<style>'
       '.picks .lede2{max-width:62ch;color:var(--muted);margin:-6px 0 18px}'
       '.pick-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}'
       '.pick-grid figure{margin:0;display:flex;flex-direction:column}'
       '.pick-grid .ph{display:block;aspect-ratio:1;border-radius:8px;overflow:hidden;background:#EEF2F5}'
       '.pick-grid .ph img{width:100%;height:100%;object-fit:cover;transition:transform .25s}.pick-grid .ph:hover img{transform:scale(1.04)}'
       '.pick-grid figcaption{padding-top:9px;display:grid;gap:2px}'
       '.pick-grid .k{font-family:var(--f-data);font-size:.6875rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}.pick-grid .k a{color:inherit}'
       '.pick-grid .n{font-weight:700;line-height:1.25}.pick-grid .n a{color:inherit;text-decoration:none}.pick-grid .n a:hover{text-decoration:underline}'
       '.pick-grid .p{font-family:var(--f-data);font-size:.8125rem}.pick-grid .pill{justify-self:start;margin-top:4px}'
       '@media (max-width:900px){.pick-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}'
       '@media (max-width:520px){.pick-grid{gap:14px}}'
       '.make-it{display:flex;flex-wrap:wrap;gap:22px 28px;align-items:center}.make-it .cta{display:flex;flex-wrap:wrap;gap:10px}'
       '.make-it img{width:200px;height:auto;border-radius:8px;background:#EEF2F5}'
       '.make-it .btn.ghost{color:var(--ink);box-shadow:inset 0 0 0 1.5px var(--ink)}'
       '</style>')

# (collection label, its page, name, stem, page to read the photo from, attribute pattern on the card)
PICKS = [('Signature Series', '/signature/', 'Black Bart tee', 'DS-BBT-T', 'signature/index.html', 'data-line="plates" data-slug="black-bart"'),
         ('Certified-ish', '/certified-ish/', 'Night Diver tee', 'DS-NGT-T', 'certified-ish/index.html', 'data-line="certifiedish" data-slug="cert-night"'),
         ('Off-World Hunt Club', '/off-world/', 'Cloaked tee', 'DS-OW01-T', 'off-world/index.html', 'data-buy="DS-OW01-T"'),
         ('1N73LL1G3NC3', '/1n73ll1g3nc3/', 'Trust But Test tee', 'DS-N09-T', '1n73ll1g3nc3/index.html', 'data-buy="DS-N09-T"'),
         ('Surface Interval', '/surface-interval/', 'Current tee', 'DS-ACS02-TD', 'surface-interval/index.html', 'data-buy="DS-ACS02-TD"'),
         ('Rash guards', '/rash-guards/', 'Thistlegorm rash guard', 'DS-THI-RGMLS-D', None, ('thistlegorm', 'dark')),
         ('Caps', '/caps/', 'Vuna Reef cap', 'DS-VUN-CD', 'caps/index.html', 'data-slug="cap-dark-vuna-reef"'),
         ('Stickers', '/stickers/', 'Achievement Unlocked set', 'DS-STK-A-SET12', 'stickers/index.html', 'data-buy="DS-STK-A-SET12"')]


def real_photo(stem):
    """A real photo beats a mockup: img/real/<SKU stem>.webp|.jpg|.png, if one has been dropped in (README "Real photos")."""
    for ext in ('webp', 'jpg', 'jpeg', 'png'):
        if os.path.isfile(os.path.join(ROOT, 'img', 'real', f'{stem}.{ext}')):
            return f'/img/real/{stem}.{ext}'
    return None


def img_from(page, pat):
    m = re.search(r'<figure class="sh[^"]*"[^>]*' + pat + r'[^>]*>.*?<img src="([^"]+)"', rd(page), re.S)
    if not m: return None
    s = H.unescape(m.group(1)); return s if s.startswith(('http', '/')) else '/' + s


def price(stems):
    ps = [v[2] for s in stems if s in CAT for v in CAT[s]['v']]
    if not ps: return ''
    lo = min(ps); return f'${lo:.0f}' if all(p == lo for p in ps) else f'from ${lo:.0f}'


def picks():
    cards = []
    for label, coll, name, stem, page, pat in PICKS:
        if page: img = img_from(page, pat)
        else:
            it = next((x for x in RG if (x['site'], x['tone']) == pat), None)
            img = it and it['styles']['mls']['media'][0] + '&width=600'
        img = real_photo(stem) or img
        if stem not in CAT or not img: print('pick skipped:', name); continue
        stems = [f'{stem[:-6]}RG{c}-D' for c in ('MLS', 'WLS', 'MSS', 'YTH', 'KID')] if 'RGMLS' in stem else [stem]
        href = f'{SHOP}/products/{CAT[stem]["h"]}'
        cards.append(f'<figure data-buy="{stem}"><a class="ph" href="{href}" data-umami-event="home-pick" data-umami-event-item="{stem}">'
                     f'<img src="{H.escape(img)}" width="600" height="600" loading="lazy" decoding="async" alt="{H.escape(name)}"></a>'
                     f'<figcaption><span class="k"><a href="{coll}" data-umami-event="home-pick-line">{H.escape(label)}</a></span>'
                     f'<span class="n"><a href="{href}" data-umami-event="home-pick" data-umami-event-item="{stem}">{H.escape(name)}</a></span>'
                     f'<span class="p">{price(stems)}</span><span class="pill available">Coming soon</span></figcaption></figure>')
    return ('<!-- PICKS:START -->' + CSS + '<section id="start" class="picks" aria-labelledby="start-h"><div class="head"><h2 id="start-h">Start here</h2></div>'
            '<p class="lede2">One from each line, to get a feel for them. Every collection has more on its page.</p>'
            f'<div class="pick-grid">{"".join(cards)}</div></section><!-- PICKS:END -->')


def make_it():
    hp = CAT.get('DS-HMP-CD'); hp_url = f'{SHOP}/products/{hp["h"]}' if hp else '/custom/'
    img = img_from('caps/index.html', 'data-slug="cap-dark-home-port"') or ''
    pic = f'<img src="{H.escape(img)}" width="600" height="600" loading="lazy" decoding="async" alt="The Home Port cap: your own port name and coordinates on the front">' if img else ''
    return ('<!-- MAKE:START --><section id="make" aria-labelledby="make-h"><div class="head"><h2 id="make-h">Make it yours</h2>'
            '<p>Pick a shirt or a cap, then the mark, the colour and a line of your own for the back. Or put your home port on a cap: '
            'its name and coordinates across the front, embroidered.</p></div>'
            f'<div class="make-it">{pic}<div class="cta"><a class="btn" href="/custom/" data-umami-event="home-make">Make it yours</a>'
            f'<a class="btn ghost" href="{hp_url}" data-umami-event="home-homeport">Home Port cap &middot; {price(["DS-HMP-CD"]) or "$48"}</a></div></div>'
            '</section><!-- MAKE:END -->')


def place(home, start, end, block, before):
    if start in home:
        return re.sub(re.escape(start) + '.*?' + re.escape(end), lambda _: block, home, flags=re.S)
    return home.replace(before, block + '\n\n    ' + before, 1)


def main():
    home = build_pages(rd('index.html'))
    home = place(home, '<!-- PICKS:START -->', '<!-- PICKS:END -->', picks(), '<section id="lines"')
    home = place(home, '<!-- MAKE:START -->', '<!-- MAKE:END -->', make_it(), '<section id="craft"')
    # the map is where you shop by site now
    home = home.replace('<h2 id="map-h">The dive map</h2>', '<h2 id="map-h">Shop by dive site</h2>')
    home = home.replace('Every plate is a site we have dived. Tap a flag for the coordinates and one fact from the plate, or open a site guide for our photos and field notes.',
                        'Every plate is a site we have dived. Tap a flag, or open a site&rsquo;s guide: our photos, the field notes and everything we make for that site.')
    home = home.replace('href="#lines">See the collections</a>', 'href="#start">Start shopping</a>')
    wr('index.html', home)
    # sitemap
    sp = rd('sitemap.xml')
    for s in ('caps', 'jackets'):
        u = f'<loc>https://doolittlescuba.com/{s}/</loc>'
        if u not in sp:
            sp = sp.replace('</urlset>', f'  <url>{u}<changefreq>weekly</changefreq><priority>0.8</priority></url>\n</urlset>')
    wr('sitemap.xml', sp)
    print('index.html: Start here, Make it yours, Shop by dive site')


if __name__ == '__main__':
    main()
