#!/usr/bin/env python3
"""The organic line on DoolittleScuba.com. Idempotent.

  tools/organic_site.py            # after tools/organic_mockups.py (img/organic/manifest.json)

- /organic/index.html: the site shell (taken from /signature/) around its own page: hero, the organic deck (one tab per series
  plus Caps & beanie, every card the organic edition's re-dyed mockup), why organic, the other collections. Kept apart from
  the regular lines, as Eric asked for eco products, and linked first wherever the collections are listed.
- js/deck.js: DS.organicCfg (specs name the organic blank; price per card from data-price).
- The collections switcher on every line page and the home page's collections deck get an "Organic" entry, placed first.
Then run tools/bust.py.
"""
import os, re, sys, json, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import organic, organic_mockups as OM

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = json.load(open(f'{SITE}/img/organic/manifest.json'))
LINES = [('org-signature', 'Signature Series', 'signature'), ('org-certifiedish', 'Certified-ish', 'certifiedish'),
         ('org-offworld', 'Off-World Hunt Club', 'offworld'), ('org-n73', '1N73LL1G3NC3', 'n73'),
         ('org-aquatic', 'Aquatic Comic', 'aquatic'), ('org-hats', 'Caps & beanie', 'caps')]
BLANK = {'tee': 'Stanley/Stella Creator 2.0 · 100% organic cotton', 'cap': 'Econscious EC7000 · organic cotton cap',
         'beanie': 'Atlantis organic rib beanie · 100% organic cotton'}
SITES = {x['slug']: x for x in json.loads(re.search(r'<script type="application/json" id="sites-data">(.*?)</script>',
                                                   open(f'{SITE}/signature/index.html').read(), re.S).group(1))}


def title(p):
    code = p['regular_key'].split('-')[1]
    if p['line'] == 'signature':
        slug = OM.SIG[code]; s = SITES.get(slug) or SITES.get(slug.replace('the-', ''))
        return (s['name'] if s else slug.replace('-', ' ').title())
    if p['line'] == 'certifiedish': return OM.CERT[code]
    if p['line'] == 'offworld': return OM.OW[int(code[2:])]['name']
    if p['line'] == 'n73': return OM.N73[int(code[1:])]['name']
    if p['line'] == 'aquatic': return OM.AQ[code[2:]]['name']
    if p['line'] == 'caps': return OM.CAPS[code].replace('-', ' ').title().replace('Llcat', 'LLCAT')
    return 'The Mark'


def price(p):
    v = [x['price'] for x in p['variants'] if x.get('price')]
    if not v: return ''
    lo, hi = min(v), max(v)
    return f'${lo:.0f}' if lo == hi else f'${lo:.0f} · ${hi:.0f} in 2XL and 3XL'


def card(p):
    line = {'beanie': 'org-hats', 'caps': 'org-hats'}.get(p['line'], 'org-' + p['line'])
    if p['kind'] == 'beanie':
        imgs = ['/img/organic/beanie/beanie-the-mark-organic-black.webp', '/img/organic/beanie/beanie-the-mark-organic-oxford-navy.webp']
        colour, hexc = 'Black or Oxford Navy', '#232323'
    else:
        m = MAN[p['key']]; imgs = m['images']; colour, hexc = p['colour'], m['hex']
    name = title(p); slug = re.sub(r'[^a-z0-9]+', '-', (p['key']).lower()).strip('-')
    dark = p.get('group') == 'dark' or p['kind'] in ('cap', 'beanie')
    tag = ('the beanie' if p['kind'] == 'beanie' else 'cap' if p['kind'] == 'cap' else ('dark tee, white ink' if dark else 'light tee, black ink'))
    if p.get('personalized'): tag += ' · with your names'
    t = lambda u: u.replace('.webp', '-t.webp')
    alt = f'{name}, organic edition, {colour} {"cap" if p["kind"] == "cap" else "beanie" if p["kind"] == "beanie" else "tee"}: mockup re-dyed from the regular shirt'
    return (f'<figure class="sh" data-line="{line}" data-slug="{slug}" data-code="{p["key"]}" data-colour="{H.escape(colour)}" data-hex="{hexc}" '
            f'data-price="{H.escape(price(p))}" data-kind="{p["kind"]}" data-custom="none" data-text="{H.escape(BLANK[p["kind"]])}">'
            f'<button type="button" class="sh-img" data-front="{imgs[0]}" data-back="{imgs[1] if len(imgs) > 1 else imgs[0]}" '
            f'data-cap="{H.escape(name)} · organic · {H.escape(colour)}" data-umami-event="organic-open" data-umami-event-key="{p["key"]}" '
            f'aria-label="Open mockup: {H.escape(name)}, organic, {H.escape(colour)}"><img src="{t(imgs[0])}" width="600" height="600" loading="lazy" '
            f'decoding="async" alt="{H.escape(alt)}"></button><figcaption><span class="dz-row"><span class="dz-t">{H.escape(name)}</span>'
            f'<span class="pill available">Coming soon</span></span><span class="dz-s">{H.escape(colour)} · {tag}</span>'
            f'<span class="sh-flip" role="group" aria-label="Show front or back"><button type="button" class="on" data-side="front" aria-pressed="true">'
            f'{"Black" if p["kind"] == "beanie" else "Front"}</button><button type="button" data-side="back" aria-pressed="false">'
            f'{"Oxford Navy" if p["kind"] == "beanie" else "Back"}</button></span></figcaption></figure>')


def page():
    src = open(f'{SITE}/signature/index.html', encoding='utf-8').read()
    head, rest = src.split('<main>', 1)
    tail = rest.split('</main>', 1)[1]
    P = organic.plan()
    n_tees = sum(1 for p in P if p['kind'] == 'tee')
    desc = (f'Every Doolittle Scuba design, also on 100% organic cotton: {n_tees} tees across the five series, the caps and the beanie, '
            'same art, same price.')
    head = re.sub(r'<title>.*?</title>', '<title>The organic line · Doolittle Scuba</title>', head, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + H.escape(desc), head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + H.escape(desc), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>The organic line · Doolittle Scuba', head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', r'\g<1>https://doolittlescuba.com/organic/', head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*', r'\g<1>https://doolittlescuba.com/organic/', head)
    ld = '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@type': 'CollectionPage',
         'name': 'The organic line · Doolittle Scuba', 'url': 'https://doolittlescuba.com/organic/', 'description': desc}, ensure_ascii=False) + '</script>'
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: ld, head, count=1, flags=re.S)
    head = head.replace('aria-current="page" ', '')
    head = coll_nav(head, current=True)
    cards = ''.join(card(p) for p in sorted(P, key=lambda p: [l[2] for l in LINES].index('caps' if p['line'] == 'beanie' else p['line'])))
    sw = [('Cotton Pink', '#FFE9EB'), ('Desert Dust', '#DCCCB4'), ('White', '#FFFFFF'), ('Heather Grey', '#CFCBC8'),
          ('Black', '#111111'), ('French Navy', '#112537'), ('Khaki', '#6E6B4D'), ('Stargazer', '#3D737D')]
    hero_img = MAN['DS-THI-TDO']['images'][1] if 'DS-THI-TDO' in MAN else ''
    main = f'''<main>
  <div class="deep hero-band"><div class="wrap">

    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Doolittle Scuba &middot; The organic line</p>
        <h1>Every design, on organic cotton.</h1>
        <p class="lede">The whole shop again, printed on 100% organic cotton: all five tee series, the caps and the beanie. Same drawings, same placements, same price. Only the shirt changes.</p>
        <div class="cta">
          <a class="btn" data-umami-event="organic-hero-shirts" href="#shirts">See the organic line</a>
          <a class="btn ghost" data-umami-event="organic-hero-why" href="#why">Why organic</a>
        </div>
        <ul class="swatches" aria-label="Organic garment colours">{''.join(f'<li style="--sw:{h}"><i></i>{n}</li>' for n, h in sw)}</ul>
      </div>
      <figure class="sheet" style="margin:0">
        <div class="coord mono">ORGANIC &nbsp; STANLEY/STELLA CREATOR 2.0 &nbsp; 180 G/M²</div>
        <img src="{hero_img}" alt="The Thistlegorm organic edition, back view: the site plate in white ink on a khaki organic tee" width="1200" height="1200">
      </figure>
    </div>
  </div></div>
  <div class="wrap">

    <section id="shirts" aria-labelledby="shirts-h">
      <div class="head">
        <h2 id="shirts-h">The organic line</h2>
        <p>One organic edition of every design, in the organic colour closest to its regular shirt: black ink on the light ones, white on the dark. The photographs here are the regular shirts re-dyed to the organic colour; samples are on their way.</p>
      </div>
      <div class="sh-grid" id="sh-grid">{cards}</div>
    </section>

    <section id="why" aria-labelledby="why-h">
      <div class="head">
        <h2 id="why-h">Why organic</h2>
        <p>Organic cotton is grown without synthetic pesticides or fertilisers, from non-GMO seed. The tees are Stanley/Stella Creator 2.0: 100% organic ring-spun combed cotton, 180 g/m², made in a fair-wear audited factory. The caps are Econscious EC7000 organic cotton; the beanie is Atlantis 100% organic rib. Every piece is printed or embroidered to order, so nothing is made that nobody wears.</p>
        <p>The organic edition costs the same as the regular one. We would rather you chose the better shirt than paid for it.</p>
      </div>
    </section>

    <section id="more" aria-labelledby="more-h">
      <div class="head">
        <h2 id="more-h">The regular collections</h2>
        <p>The same designs on the Comfort Colors 1717 garment-dyed tee and the Flexfit 6277 cap: <a href="/signature/">Signature Series</a>, <a href="/certified-ish/">Certified-ish</a>, <a href="/off-world/">Off-World Hunt Club</a>, <a href="/1n73ll1g3nc3/">1N73LL1G3NC3</a>, <a href="/aquatic-comic/">Aquatic Comic</a>, and the <a href="/#hats">hats</a>.</p>
      </div>
    </section>
  </div>
</main>'''
    js = ("<script>\nDS.lightbox();\nDS.deck('shirts','sh-grid',DS.organicCfg({lines:" + json.dumps([[a, b] for a, b, _ in LINES], ensure_ascii=False)
          + ", contact:'/#contact'}));\n</script>")
    tail = re.sub(r'<script>\s*DS\.lightbox\(\);.*?</script>', lambda m: js, tail, count=1, flags=re.S)
    tail = re.sub(r'<!-- SITEDATA:START -->.*?<!-- SITEDATA:END -->', '', tail, flags=re.S) if 'SITEDATA:END' in tail else tail
    os.makedirs(f'{SITE}/organic', exist_ok=True)
    open(f'{SITE}/organic/index.html', 'w', encoding='utf-8').write(head + main + tail)
    print('organic/index.html', len(P), 'cards')


def coll_nav(html, current=False):
    """put Organic first in the collections switcher (nav.coll)"""
    m = re.search(r'(<nav class="coll" aria-label="Collections"><div class="wrap"><span class="lbl">The collections</span>)', html)
    if not m: return html
    html = re.sub(r'<a href="/organic/"[^>]*>Organic</a>', '', html)
    link = f'<a href="/organic/"{" aria-current=\"page\"" if current else ""} class="org" data-umami-event="coll-switch" data-umami-event-line="organic">Organic</a>'
    return html.replace(m.group(1), m.group(1) + link, 1)


CFG = r'''
  // The organic line (/organic/): one tab per series + Caps & beanie; the card carries its own price and blank.  [organic_site.py]
  DS.organicCfg=function(o){ o=o||{}; var lines=o.lines||[], step={}; lines.forEach(function(l){ step[l[0]]=44; });
   var NAME={'org-signature':'Signature Series','org-certifiedish':'Certified-ish','org-offworld':'Off-World Hunt Club','org-n73':'1N73LL1G3NC3','org-aquatic':'Aquatic Comic','org-hats':'Caps & beanie'};
   return {
    lines:lines, step:step, noun:'piece', price:'', openEvent:'organic-open', contact:o.contact||'#contact', custom:false,
    footNote:'100% organic cotton &middot; same art, same price', facts:false,
    eyebrow:function(it){ return (NAME[it.line]||'Organic')+' · organic'; },
    sub:function(it){ return it.sub; },
    blurb:function(it){ return 'The organic edition: the same design on '+esc(it.text)+'. Printed or embroidered to order.'; },
    views:function(it){ return it.slug==='ds-mrk-bno'?[['front','Black'],['back','Oxford Navy']]:null; },
    defaultView:function(it){ return it.line==='org-signature'||it.line==='org-hats'||it.line==='org-n73'?'front':'back'; },
    caption:function(it,v){ return esc(it.cap)+(v==='back'?' · back':''); },
    specs:function(it){ return [['Blank',esc(it.text)],['Colour','<span class="sw"></span>'+esc(it.colour)],['Art','The same files as the regular edition'],['Price',esc(it.price||'')]]; }
   };
  };
'''


def deck_js():
    p = f'{SITE}/js/deck.js'; s = open(p, encoding='utf-8').read()
    s = re.sub(r'\n  // The organic line \(/organic/\).*?\n  };\n', '\n', s, flags=re.S)
    anchor = '\n  // The sticker packs deck'
    s = s.replace(anchor, CFG.rstrip('\n') + '\n' + anchor, 1)
    open(p, 'w', encoding='utf-8').write(s); print('deck.js: organicCfg')


def home():
    """the organic tile, first in the home page's collections deck, and a green Organic link style"""
    p = f'{SITE}/index.html'; s = open(p, encoding='utf-8').read()
    s = re.sub(r'<figure class="sh" data-line="coll" data-slug="organic".*?</figure>', '', s, flags=re.S)
    img = MAN['DS-THI-TDO']['images'][1]
    n = sum(1 for p_ in organic.plan() if p_['kind'] == 'tee')
    tile = (f'<figure class="sh" data-line="coll" data-slug="organic" data-colour="{n} tees, caps, beanie" data-hex="#6E6B4D" data-guide="/organic/" '
            f'data-text="Every design again on 100% organic cotton, same art and same price: all five tee series, the caps and the beanie." hidden>'
            f'<button type="button" class="sh-img" data-front="{img}" data-cap="The organic line · the collection" aria-label="Open the organic line">'
            f'<img src="{img.replace(".webp", "-t.webp")}" width="600" height="600" loading="lazy" decoding="async" '
            f'alt="The Thistlegorm organic edition, back view: the site plate in white ink on a khaki organic tee"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">The organic line</span></span><span class="dz-s">{n} tees, caps and a beanie · '
            f'<a href="/organic/">the page</a></span></figcaption></figure>')
    s = s.replace('<div class="sh-grid" id="co-grid">', '<div class="sh-grid" id="co-grid">' + tile, 1)
    open(p, 'w', encoding='utf-8').write(s); print('index.html: organic tile first')
    c = f'{SITE}/css/site.css'; css = open(c, encoding='utf-8').read()
    if '.coll a.org' not in css:
        css += '\n/* the organic line link, first in the collections switcher (organic_site.py) */\n.coll a.org{color:#3E6B3A}.coll a.org::before{content:"\\2618\\FE0E\\00a0"}\n'
        open(c, 'w', encoding='utf-8').write(css)


def nav_everywhere():
    for rel in ('signature', 'certified-ish', 'off-world', '1n73ll1g3nc3', 'aquatic-comic'):
        p = f'{SITE}/{rel}/index.html'; s = open(p, encoding='utf-8').read(); s2 = coll_nav(s)
        if s2 != s: open(p, 'w', encoding='utf-8').write(s2); print('nav:', rel)


if __name__ == '__main__':
    deck_js(); page(); nav_everywhere(); home()
