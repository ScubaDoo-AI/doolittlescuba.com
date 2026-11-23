#!/usr/bin/env python3
"""The Water Hazard golf towels page, /towels/ (Eric, 22 Nov 2026: "Add towels to the website and shop").

Twelve 16 x 24 in sublimated golf towels in two sets of six, printed to order by Printful (product 1423), $28 each.
The shell (head, status banner, nav, footer, scripts) is copied from stickers/index.html so the shared tools keep it in
step; the main block is written from TOWELS below. Each card carries data-sku = the Printful variant SKU, which
tools/catalog_map.py turns into data-buy for the cart.

Images live in img/towels/: <slug>.webp (Printful mockup), <slug>-art.webp (the artwork), and -t.webp thumbnails.

  tools/towels_page.py      # (re)build towels/index.html, then tools/catalog_map.py and tools/bust.py
"""
import html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOP = 'https://shop.doolittlescuba.com'
PRICE = '$28'

# code, title, slug (handle = slug + -water-hazard-golf-towel), Printful SKU, one line about it
TOWELS = [
    ('WH01', 'Dive Boat Bingo', 'dive-boat-bingo', 'dive-boat-bingo', '4057324_44137', 'A bingo card for the boat ride: everything that happens on every dive trip, one square at a time.'),
    ('WH02', 'Mood Gauge', 'mood-gauge', 'mood-gauge', '5291045_44137', 'A pressure gauge that reads the diver instead of the tank.'),
    ('WH03', 'Today’s Departures', 'todays-departures', 'today-s-departures', '5936979_44137', 'The departures board, dive-site edition.'),
    ('WH04', 'Local Forecast', 'local-forecast', 'local-forecast', '6551131_44137', 'The forecast as a diver reads it.'),
    ('WH05', 'Approved Uses', 'approved-uses', 'approved-uses', '1633154_44137', 'Everything this towel is officially for. Golf is on the list, somewhere.'),
    ('WH06', 'Property of the Ocean', 'property-of-the-ocean', 'property-of-the-ocean', '7946276_44137', 'For the ball that went in the water hazard, and the diver who would go get it.'),
    ('WH07', 'Dive Briefing, Translated', 'dive-briefing-translated', 'dive-briefing-translated', '8396729_44137', 'What the divemaster says, and what it means. “Mild current.” You’ll see the whole reef. Quickly.'),
    ('WH08', 'Surface Interval', 'surface-interval', 'surface-interval', '1530371_44137', 'What the hour between dives is really for.'),
    ('WH09', 'Safety Stop', 'safety-stop', 'safety-stop', '1170981_44137', 'Three minutes at fifteen feet, accounted for.'),
    ('WH10', 'Where the Air Went', 'where-the-air-went', 'where-the-air-went', '7214799_44137', 'A full tank, 3,000 psi, and where every bit of it went.'),
    ('WH11', 'Signal Flags', 'signal-flags', 'signal-flags', '9875933_44137', 'The signal flags, as divers read them.'),
    ('WH12', 'House Rules', 'house-rules', 'house-rules', '6503382_44137', 'The rules of the dive boat, posted where everyone can see them.'),
]
SETS = [('set-1', 'Set one', 'The first six: bingo, the mood gauge, the departures board, the forecast, the approved uses and the lost-property tag.', TOWELS[:6]),
        ('set-2', 'Set two', 'Six more for the bag: the briefing translated, the surface interval, the safety stop, the air, the flags and the house rules.', TOWELS[6:])]

E = html.escape


def ver(rel):
    """the ?v= hash bust.py would give; bust.py rewrites it anyway"""
    import hashlib
    return hashlib.sha1(open(f'{ROOT}/{rel}', 'rb').read()).hexdigest()[:8]


def card(t):
    code, title, slug, handle, sku, line = t
    img = lambda n: f'/img/towels/{n}.webp?v={ver(f"img/towels/{n}.webp")}'
    url = f'{SHOP}/products/{handle}-water-hazard-golf-towel'
    return (f'<figure class="sh tw" id="t-{slug}" data-kind="towel" data-line="water-hazard" data-slug="{slug}" data-code="{code}" data-sku="{sku}" data-price="{PRICE}" data-colour="Navy" data-hex="#102A54">'
            f'<button type="button" class="sh-img" data-front="{img(slug)}" data-back="{img(slug + "-art")}" '
            f'data-cap="{E(title)} — Water Hazard golf towel · 16 × 24 in · {PRICE}" data-umami-event="towel-open" data-umami-event-towel="{code}">'
            f'<img src="{img(slug + "-t")}" width="480" height="700" loading="lazy" decoding="async" draggable="false" alt="{E(title)} Water Hazard golf towel: Printful mockup"></button>'
            f'<figcaption><span class="dz-row"><span class="dz-t">{E(title)}</span><span class="mono tw-code">{code}</span></span>'
            f'<span class="dz-s">{E(line)}</span>'
            f'<span class="tw-buy"><span class="price">{PRICE}</span><a class="txt" href="{url}" data-umami-event="towel-shop" data-umami-event-towel="{code}">In the shop &rarr;</a></span>'
            f'<span class="sh-flip" role="group" aria-label="Show the towel or the artwork"><button type="button" class="on" data-side="front" aria-pressed="true">Towel</button>'
            f'<button type="button" data-side="back" aria-pressed="false">Artwork</button></span></figcaption></figure>')


STYLE = '''<style>
/* Water Hazard towels: navy and gold, the towels' own colours */
.hero .sheet img{width:100%;height:auto;display:block;border-radius:3px;border:1px solid rgba(255,255,255,.14)}
.tw-set{margin-top:clamp(22px,3.5vw,36px)}
.tw-set h3{font-size:var(--s2);color:var(--ink);display:flex;align-items:baseline;gap:10px}
.tw-set h3 .mono{font-size:var(--s-1);color:var(--muted)}
.tw-set > p{color:var(--muted);max-width:72ch;margin:6px 0 14px}
.tw-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:26px 22px;max-width:960px}
@media (max-width:640px){.tw-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:18px 12px}}
.tw .sh-img{aspect-ratio:480/700;border:1px solid var(--rule);border-radius:8px;background:#fff;box-shadow:0 10px 22px -18px rgba(18,42,85,.5)}
.tw .sh-img img{border-radius:7px;object-fit:cover}
.tw-code{font-size:var(--s-1);color:var(--muted);margin-left:auto}
.tw-buy{display:flex;align-items:baseline;gap:12px;margin-top:4px}
.tw-buy .price{font-weight:700;color:#B8862B}
.tw-specs{display:grid;grid-template-columns:max-content 1fr;gap:6px 18px;margin:0;max-width:72ch}
.tw-specs dt{font-family:var(--f-data,ui-monospace,monospace);font-size:var(--s-1);color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.tw-specs dd{margin:0}
</style>'''


def main_block():
    sets = ''.join(f'<div class="tw-set" id="{sid}"><h3>{name} <span class="mono">{len(ts)}</span></h3><p>{E(blurb)}</p>'
                   f'<div class="sh-grid tw-grid">{"".join(card(t) for t in ts)}</div></div>' for sid, name, blurb, ts in SETS)
    hero = f'/img/towels/hero-trio.webp?v={ver("img/towels/hero-trio.webp")}'
    return f'''<main>
  <div class="deep hero-band"><div class="wrap">
    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Doolittle Scuba &middot; Water Hazard</p>
        <h1>For divers who also play golf. Badly.</h1>
        <p class="lede">Twelve golf towels for the bag, the cart and the dive boat: the briefing translated, where the air went, dive boat bingo and nine more. 16 &times; 24 in, printed edge to edge on navy, with a brass grommet and clip. {PRICE} each.</p>
        <div class="cta">
          <a class="btn" data-umami-event="hero-towels" href="#towels">The towels</a>
          <a class="btn ghost" data-umami-event="hero-towels-shop" href="{SHOP}/collections/water-hazard">Shop the set</a>
        </div>
      </div>
      <figure class="sheet" style="margin:0">
        <div class="coord mono" aria-label="12 golf towels, 16 by 24 inches, $28 each">12 TOWELS &nbsp;&middot;&nbsp; 16 &times; 24 IN &nbsp;&middot;&nbsp; {PRICE}</div>
        <img src="{hero}" alt="Three Water Hazard golf towels side by side: Dive Briefing Translated, Dive Boat Bingo and Signal Flags" width="1800" height="900">
      </figure>
    </div>
  </div></div>
  <div class="wrap">

    <section id="towels" aria-labelledby="towels-h">
      <div class="head">
        <h2 id="towels-h">The towels</h2>
        <p>Two sets of six, {PRICE} each. Tap a towel to see it large; switch a card to <em>Artwork</em> for the print itself.</p>
      </div>
{sets}
      <p class="dz-note">Printful&rsquo;s mockups of our print files, not photographs. All artwork &copy; 2026 Doolittle Scuba L.L.C. Copying, printing or reuse of any design without written permission is prohibited.</p>
    </section>

    <section id="towel-specs" aria-labelledby="specs-h">
      <div class="head"><h2 id="specs-h">The towel</h2></div>
      <dl class="tw-specs">
        <dt>Size</dt><dd>16 &times; 24 in</dd>
        <dt>Fabric</dt><dd>80% polyester, 20% polyamide; absorbent and quick-drying, about 4 oz</dd>
        <dt>Print</dt><dd>Sublimated on the front, edge to edge, navy ground</dd>
        <dt>Hardware</dt><dd>Brass grommet and clip in the corner, for the bag, the cart or the BCD</dd>
        <dt>Made</dt><dd>Printed to order by Printful</dd>
        <dt>Price</dt><dd>{PRICE}</dd>
      </dl>
    </section>

    <section id="make" aria-labelledby="make-h">
      <div class="head"><h2 id="make-h">More from the shop</h2></div>
      <div class="two">
        <div class="card">
          <h3>The shirts</h3>
          <p>Five collections, each on a page of its own: Signature Series, Certified-ish, Off-World Hunt Club, 1N73LL1G3NC3 and Surface Interval.</p>
          <a class="btn ghost" href="/#lines" data-umami-event="make-collections">See the collections</a>
        </div>
        <div class="card">
          <h3>The stickers</h3>
          <p>Thirty-seven packs of three, the Achievement Unlocked set and the singles.</p>
          <a class="btn ghost" href="/stickers/" data-umami-event="make-stickers">See the stickers</a>
        </div>
      </div>
    </section>

  </div>
</main>'''


HEAD_TITLE = 'Water Hazard golf towels · Doolittle Scuba'
DESC = 'Water Hazard: twelve 16 × 24 in golf towels for divers who also play golf — Dive Briefing Translated, Where the Air Went, Dive Boat Bingo and more. Printed edge to edge on navy, brass grommet and clip, $28.'


def build():
    src = open(f'{ROOT}/stickers/index.html', encoding='utf-8').read()
    head, rest = src.split('<main>', 1)
    tail = rest.split('</main>', 1)[1]
    # head: title, description, canonical, og, json-ld, page style
    head = re.sub(r'<title>.*?</title>', f'<title>{E(HEAD_TITLE)}</title>', head)
    head = re.sub(r'(<meta (?:name|property)="(?:og:)?description" content=")[^"]*', lambda m: m.group(1) + E(DESC), head)
    head = head.replace('https://doolittlescuba.com/stickers/', 'https://doolittlescuba.com/towels/')
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\1Water Hazard · golf towels for divers', head)
    head = re.sub(r'(<meta property="og:image" content=")[^"]*', r'\1https://doolittlescuba.com/img/og/towels.jpg', head)
    head = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', r'\1Three Water Hazard golf towels on navy', head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>',
                  '<script type="application/ld+json">{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Water Hazard golf towels · Doolittle Scuba", '
                  '"url": "https://doolittlescuba.com/towels/", "description": "' + DESC.replace('"', '\\"') + '"}</script>', head, flags=re.S)
    head = re.sub(r'<style>\n/\* Stickers:.*?</style>', lambda m: STYLE, head, flags=re.S)
    tail = re.sub(r"<script>DS\.lightbox\(\);.*?</script>", '<script>DS.lightbox();</script>', tail)
    out = head + main_block() + tail
    os.makedirs(f'{ROOT}/towels', exist_ok=True)
    open(f'{ROOT}/towels/index.html', 'w', encoding='utf-8').write(out)
    print('towels/index.html:', len(TOWELS), 'towels')


if __name__ == '__main__':
    build()
