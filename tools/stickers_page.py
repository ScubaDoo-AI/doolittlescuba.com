#!/usr/bin/env python3
"""The stickers page: /stickers/ — the 37 three-sticker packs by line, then the singles (the three kiss-cut sheets).

    tools/stickers_page.py        # (re)build stickers/index.html and the pack strip on the home page

Packs come from tools/packs.json (built from the print package's Pack_Index.csv; proofs in img/packs/<slug>.webp);
the single-sticker sheets are harvested from the page itself (or, the first time, from the home page's #stickers
section) and put back unchanged, so this can be re-run after a copy or theme change. The home page's #stickers
section carries the same packs deck between <!-- PACKS:START --> and <!-- PACKS:END --> (rebuilt every run; the first
run converts the old sheets / teaser section). Both pages show the packs as a stacked deck (js/deck.js, DS.packsCfg:
run across the tabs, open a card for the sheet and what is on it); the figures under #pk-grid are the no-JS fallback
and what the deck is built from. Shell pieces (shop-status flag, wide-screen block, social links, nav) are shared with
tools/line_pages.py. Run tools/bust.py afterwards.
"""
import html as H, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import line_pages as LP

SITE = LP.SITE
P = json.load(open(f'{SITE}/tools/packs.json'))
PRICE = P['price']
LINE_NAME = {'set': 'The Achievement set', 'themed': 'Themed packs', 'classic': 'Classic die-cut packs', 'brand': 'Brand packs'}
LINE_COPY = {
    'set': 'The opener: all twelve Achievement Unlocked badges on one sheet, with the Achievement Hunter and 100% Complete badges and three DS marks to go with them. $15.',
    'themed': 'Twenty-six sets of three, drawn for the pack: reef cuties, puns, what the dive computer says, retro patches, wrecks, the deep and the weird, bucket-list seas, ocean masterpieces and dive science.',
    'classic': 'Five sets from the classic die-cuts: the courses and specialties, three to a sheet.',
    'brand': 'Six sets of the DS marks: the seal, the stacked and horizontal logos, the tagline and the dive kit, by colourway.',
}
LINE_LABEL = {'set': 'The opener', 'themed': 'Themed pack', 'classic': 'Classic die-cut pack', 'brand': 'Brand pack'}
LINE_BLURB = {
    'set': 'Every course as a game achievement — all twelve on one sheet — plus the Achievement Hunter and 100% Complete badges and three DS marks. The one to start with.',
    'themed': 'One of the twenty-six themed sets: three stickers drawn for the pack, cut as one sheet.',
    'classic': 'Three of the classic die-cuts — the courses and specialties — on one sheet.',
    'brand': 'Three of the DS marks on one sheet, in one colourway or across three.',
}
# single-sticker titles for the pack contents, from the sticker plan
STK = {}
for l in open(f'{SITE}/tools/printful_stickers.py', encoding='utf-8').read().split('ROWS = [l.split(\'|\') for l in """', 1)[1].split('"""', 1)[0].splitlines():
    sku, title, colour = l.split('|')[:3]
    t = re.sub(r' — .*$| Sticker$', '', title)
    STK[sku] = t + (f', {colour}' if colour else '')


def price(p): return float(p.get('price', PRICE))


def contents(pack):
    if pack.get('contents'): return pack['contents']
    names = [STK.get(s) for s in pack['stickers']]
    if all(names): return ' · '.join(names)
    return 'three stickers'


def card(p):
    what = 'the full set · seventeen kiss-cut stickers on one 5.83 × 8.27 in sheet' if p['line'] == 'set' else ('sticker pack · three kiss-cut stickers' + (' and small fillers' if p.get('fillers') else '') + ' on one 5.83 × 8.27 in sheet')
    cap = f'{p["name"]} — {what} · ${price(p):.0f}'
    inner = contents(p)
    return (f'<figure class="sh pk" data-sku="{p["sku"]}" data-line="{p["line"]}" data-slug="{p["slug"]}" data-code="{"" if p["line"] == "set" else p["sku"][-3:]}" data-price="${price(p):.0f}" '
            f'data-colour="{LINE_LABEL[p["line"]]}" data-hex="{p.get("hex", "#122A55")}" data-text="{H.escape(LINE_BLURB[p["line"]], quote=True)}">'
            f'<button type="button" class="sh-img" data-front="/img/packs/{p["slug"]}.webp" data-cap="{H.escape(cap, quote=True)}" data-umami-event="pack-open" data-umami-event-pack="{p["sku"]}">'
            f'<img src="/img/packs/{p["slug"]}-t.webp" width="360" height="540" loading="lazy" decoding="async" draggable="false" alt="{H.escape(p["name"])} sticker pack: {H.escape(inner)}"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{H.escape(p["name"])}</span></span>'
            f'<span class="dz-s">{H.escape(inner) if inner != "three stickers" else ("Three stickers + fillers" if p.get("fillers") else "Three stickers")} &middot; ${price(p):.0f}</span></figcaption></figure>')


def groups():
    """The 37 cards in three groups under #pk-grid: the deck is built from them and hides them; without JS they show as grids."""
    out = []
    for line in ('set', 'themed', 'classic', 'brand'):
        packs = [p for p in P['packs'] if p['line'] == line]
        out.append(f'<div class="pk-group" id="packs-{line}"><h3>{LINE_NAME[line]} <span class="mono">{len(packs)}</span></h3><p>{LINE_COPY[line]}</p>'
                   f'<div class="sh-grid pk-grid">{"".join(card(p) for p in packs)}</div></div>')
    return '<div id="pk-grid">\n' + '\n'.join(out) + '\n</div>'


DECK_HINT = 'Run across the tabs to pull a pack forward; open it for the sheet and what is on it. Swipe the deck on a phone.'
DECK_CALL = "DS.deck('%s','pk-grid',DS.packsCfg({contact:'%s'}));"


def n_packs(): return sum(1 for p in P['packs'] if p['line'] != 'set')


def singles(home_src, page_src):
    src = page_src if page_src and '<!-- SINGLES:START -->' in page_src else home_src
    if src is page_src:
        return LP.block(src, '<!-- SINGLES:START -->', '<!-- SINGLES:END -->')
    i = src.index('<div class="sk-sheets">'); j = src.index('      </div>\n    </section>', i)
    sheets = src[i:j + len('      </div>')]
    return '<!-- SINGLES:START -->\n' + LP.absolutise(sheets) + '\n<!-- SINGLES:END -->'


def page(home_src, page_src):
    status = LP.block(home_src, '<!-- STATUS:START -->', '<!-- STATUS:END -->')
    wide = LP.block(home_src, '<!-- WIDE:START -->', '<!-- WIDE:END -->')
    social = LP.block(home_src, '<!-- SOCIAL:START -->', '<!-- SOCIAL:END -->')
    url = f'{LP.ORIGIN}/stickers/'
    desc = 'The Achievement Unlocked full set and thirty-seven packs of three kiss-cut stickers — themed sets, the classic die-cuts and the brand marks — plus the singles. Printed vinyl, waterproof, the DS mark on every one.'
    jsonld = json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Stickers · Doolittle Scuba", "url": url, "description": desc,
                         "isPartOf": {"@type": "WebSite", "name": "Doolittle Scuba", "url": LP.ORIGIN + '/'},
                         "publisher": {"@type": "Organization", "name": "Doolittle Scuba L.L.C.", "url": LP.ORIGIN + '/'}}, ensure_ascii=False)
    n = n_packs()
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Stickers · Doolittle Scuba</title>
<meta name="description" content="{H.escape(desc, quote=True)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Doolittle Scuba">
<meta property="og:title" content="Stickers · three to a sheet, or one at a time">
<meta property="og:description" content="{H.escape(desc, quote=True)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{LP.ORIGIN}/img/og/stickers.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Doolittle Scuba sticker packs: three kiss-cut stickers to a sheet">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" href="/img/brand/icon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#122A55">
<script type="application/ld+json">{jsonld}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{LP.FONTS_BASE}">
<link rel="stylesheet" href="/css/site.css">
<style>
/* Stickers: the chart-sheet look, with the packs as portrait sheets */
.hero .sheet img{{width:100%;height:auto;display:block;border-radius:3px;border:1px solid rgba(255,255,255,.14)}}
.pk-group{{margin-top:clamp(22px,3.5vw,36px)}}
.pk-group h3{{font-size:var(--s2);color:var(--ink);display:flex;align-items:baseline;gap:10px}}
.pk-group h3 .mono{{font-size:var(--s-1);color:var(--muted)}}
.pk-group > p{{color:var(--muted);max-width:72ch;margin:6px 0 14px}}
</style>
{wide}
</head>
<body>
{status}
<div class="deep">
  <div class="wrap">
    <header class="top">
      <a class="brand" data-umami-event="nav-logo" href="/" aria-label="Doolittle Scuba L.L.C., Do - A - Little Scuba, home"><img src="/img/brand/lockup-h-dark.png" alt="Doolittle Scuba L.L.C. — Do - A - Little Scuba" width="900" height="193"></a>
      {LP.nav('stickers')}
    </header>
  </div>
</div>
<main>
  <div class="deep hero-band"><div class="wrap">
    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Doolittle Scuba &middot; Stickers</p>
        <h1>Three to a sheet, or one at a time.</h1>
        <p class="lede">The Achievement Unlocked full set, {n} packs of three kiss-cut stickers — themed sets drawn for the pack, the classic die-cuts and the brand marks — and the singles. Printed vinyl, waterproof, the DS mark on every one.</p>
        <div class="cta">
          <a class="btn" data-umami-event="hero-packs" href="#packs">The packs</a>
          <a class="btn ghost" data-umami-event="hero-singles" href="#singles">The singles</a>
          <a class="txt" data-umami-event="hero-launch" href="/#contact">Get launch news &rarr;</a>
        </div>
      </div>
      <figure class="sheet" style="margin:0">
        <div class="coord mono" aria-label="{n} packs, three stickers each, kiss-cut, 5.83 by 8.27 inch sheet">{n} PACKS &nbsp;&middot;&nbsp; THREE STICKERS EACH &nbsp;&middot;&nbsp; KISS-CUT &nbsp;&middot;&nbsp; 5.83 &times; 8.27 IN</div>
        <img src="/img/packs/hero-trio.webp" alt="Three sticker packs side by side: Reef Cuties, Retro Patches and the Navy Trio, three stickers on each sheet" width="1800" height="900">
      </figure>
    </div>
  </div></div>
  <div class="wrap">

    <section id="packs" aria-labelledby="packs-h">
      <div class="head">
        <h2 id="packs-h">The packs</h2>
        <p>The opener is the Achievement set: all twelve badges on one sheet, $15. Then {n} packs of three on a 5.83 &times; 8.27 in kiss-cut sheet, ${PRICE:.0f} a pack, most with a few small fillers in the spare space. Peel them one at a time for the tank, the dive box, the laptop and the logbook. {DECK_HINT} All coming soon &mdash; <a href="/#contact" data-umami-event="packs-contact">get the launch email</a>.</p>
      </div>
      {groups()}
      <p class="dz-note">All artwork &copy; 2026 Doolittle Scuba L.L.C. Copying, printing or reuse of any design without written permission is prohibited.</p>
    </section>

    <section id="singles" aria-labelledby="singles-h">
      <div class="head">
        <h2 id="singles-h">The singles</h2>
        <p>One at a time: the Achievement Unlocked badges, each course as a game achievement; the classic die-cuts; and the brand set. Tap any sticker to see it large.</p>
      </div>
{singles(home_src, page_src)}
    </section>

    <section id="make" aria-labelledby="make-h">
      <div class="head">
        <h2 id="make-h">While the samples are out</h2>
        <p>Nothing ships until the sample sheets pass; the packs are drawn, proofed and waiting on the first run.</p>
      </div>
      <div class="two">
        <div class="card">
          <h3>Get launch news</h3>
          <p>One email when the stickers ship. No newsletter, no sharing your address.</p>
          <a class="btn" href="/#contact" data-umami-event="make-launch-news" data-umami-event-line="stickers">Tell me when they ship</a>
        </div>
        <div class="card">
          <h3>The shirts</h3>
          <p>Five collections, each on a page of its own: Signature Series, Certified-ish, Off-World Hunt Club, 1N73LL1G3NC3 and Aquatic Comic.</p>
          <a class="btn ghost" href="/#lines" data-umami-event="make-collections">See the collections</a>
        </div>
      </div>
    </section>

  </div>
</main>

<footer class="deep foot-band">
  <div class="wrap foot">
    <img class="foot-lockup" src="/img/brand/lockup-stack-dark.png" alt="Doolittle Scuba L.L.C. — Do - A - Little Scuba" width="760" height="485" loading="lazy">
    <div class="foot-meta">
      <p>Based in Newnan, Georgia</p>
{social}
      <p class="mono">hello@doolittlescuba.com &middot; orders@doolittlescuba.com</p>
      <p>diveplate designs &copy; 2026 Doolittle Scuba L.L.C. All rights reserved.</p>
    </div>
  </div>
</footer>

<dialog class="lb" id="sh-lb" aria-label="Photo viewer">
  <button type="button" class="lb-x" aria-label="Close">&times;</button>
  <figure><img id="sh-lb-img" alt=""><figcaption id="sh-lb-cap"></figcaption></figure>
</dialog>

<script src="/js/deck.js"></script>
<script>DS.lightbox();{DECK_CALL % ('packs', '/#contact')}</script>

<!-- Umami visitor analytics (cookie-free). Runs only on the live domain. -->
<script defer src="https://cloud.umami.is/script.js" data-website-id="97eb29ce-9e01-43d7-8047-5d59024eeea7" data-domains="doolittlescuba.com,www.doolittlescuba.com"></script>
</body>
</html>
'''


def home_section(home_src):
    """The home page's #stickers section: intro, the packs deck (between PACKS markers) and a link to the singles. Idempotent."""
    i = home_src.index('<section id="stickers"'); j = home_src.index('</section>', i) + len('</section>')
    n = n_packs()
    sec = f'''<section id="stickers" aria-labelledby="stickers-h">
      <div class="head">
        <h2 id="stickers-h">The stickers</h2>
        <p>The Achievement Unlocked full set to start, $15, then {n} packs of three kiss-cut stickers &mdash; themed sets, the classic die-cuts and the brand marks, ${PRICE:.0f} a pack. {DECK_HINT} Printed vinyl, waterproof, the DS mark on every one. All coming soon. The singles &mdash; Achievement Unlocked badges, die-cuts and the brand set &mdash; are on <a href="/stickers/#singles" data-umami-event="stickers-singles">the stickers page</a>.</p>
      </div>
<!-- PACKS:START -->
{groups()}
<!-- PACKS:END -->
      <p class="line-links" style="margin-top:14px"><a class="btn" href="/stickers/" data-umami-event="stickers-page">The stickers page: all {n} packs and the singles</a></p>
    </section>'''
    out = home_src[:i] + sec + home_src[j:]
    if "DS.deck('stickers'" not in out:
        k = out.index("DS.deck('hats','ht-grid',{")
        out = out[:k] + DECK_CALL % ('stickers', '#contact') + "\n" + out[k:]
    return out


def og():
    """The share image: the hero trio over the page title, 1200 x 630 (img/og/stickers.jpg)."""
    from PIL import Image, ImageDraw, ImageFont
    W, Hh = 1200, 630
    im = Image.new('RGB', (W, Hh), (18, 42, 85)); d = ImageDraw.Draw(im)
    hero = Image.open(f'{SITE}/img/packs/hero-trio.webp').convert('RGB'); hero = hero.resize((904, 452), Image.LANCZOS)
    im.paste(hero, (148, 36))
    f_n = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 46)
    f_u = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 20)
    d.text((150, 512), 'Stickers \u2014 three to a sheet, or one at a time', font=f_n, fill=(255, 255, 255))
    d.text((150, 576), 'DOOLITTLESCUBA.COM/STICKERS/', font=f_u, fill=(169, 185, 207))
    os.makedirs(f'{SITE}/img/og', exist_ok=True); im.save(f'{SITE}/img/og/stickers.jpg', 'JPEG', quality=86, optimize=True)


def main():
    home_src = LP.home()
    p = f'{SITE}/stickers/index.html'
    page_src = open(p, encoding='utf-8').read() if os.path.exists(p) else None
    os.makedirs(f'{SITE}/stickers', exist_ok=True)
    open(p, 'w', encoding='utf-8').write(page(home_src, page_src))
    print(f'/stickers/  {len(P["packs"])} packs')
    open(f'{SITE}/index.html', 'w', encoding='utf-8').write(home_section(home_src)); print('index.html: #stickers = the packs deck')
    og(); print('img/og/stickers.jpg')
    # sitemap
    sp = f'{SITE}/sitemap.xml'; s = open(sp, encoding='utf-8').read()
    if f'{LP.ORIGIN}/stickers/' not in s:
        s = s.replace(f'  <url><loc>{LP.ORIGIN}/custom/</loc>', f'  <url><loc>{LP.ORIGIN}/stickers/</loc><lastmod>{LP.TODAY}</lastmod></url>\n  <url><loc>{LP.ORIGIN}/custom/</loc>', 1)
        open(sp, 'w', encoding='utf-8').write(s); print('sitemap.xml')


if __name__ == '__main__':
    main()
