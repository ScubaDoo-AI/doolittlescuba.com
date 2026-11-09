#!/usr/bin/env python3
"""The collection pages: one themed page per line, built from the cards that line already has.

    tools/line_pages.py            # (re)build /signature/, /certified-ish/, /off-world/, /1n73ll1g3nc3/, /aquatic-comic/
    tools/line_pages.py --og       # also redraw the img/og/<page>.jpg share images

Each page is the site shell (header, nav, shop-status flag, footer, the shared css/site.css + js/deck.js) around a theme of
its own: tokens, fonts and a hero written for that line, then the line's shirts deck (light + dark, or the Aquatic subsets),
its designs grid with status chips and a search box, Make-it-yours and launch-news pointers, and tiles for the other four.

The cards are the source of truth and live in the pages: a run harvests `figure.sh[data-line]` and `figure.dz[data-line]`
from the existing page (or, the first time, from index.html, rewriting img/ paths to /img/) and puts them back inside the
regenerated shell, so the shell and the themes can be changed here without touching the cards. The line tools
(offworld.py, n73.py, aquatic.py) patch the cards in place between the <!-- SH:END --> / <!-- DZ:END --> markers.
Also writes js/designs.json (the index behind the search box on the home page) and the sitemap entries.
Run tools/bust.py afterwards.
"""
import datetime, hashlib, html as H, json, os, re, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()
ORIGIN = 'https://doolittlescuba.com'
FONTS_BASE = 'https://fonts.googleapis.com/css2?family=Almendra:wght@400;700&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap'
AQ = json.load(open(f'{SITE}/tools/aquatic_designs.json'))
AQ_SUB = {d['slug']: d['subset'] for d in AQ['designs']}
AQ_BACK = {d['slug']: re.sub(r'[*{}]', '', d['front'] + ' ' + d['back']).replace('\n', ' ') for d in AQ['designs']}
SITES = {}
SUBJ = json.load(open(f'{SITE}/tools/design_subjects.json')) if os.path.exists(f'{SITE}/tools/design_subjects.json') else {}   # tools/design_subjects.py

LINES = [
    dict(key='signature', dir='signature', name='Signature Series', short='Signature', tab='',
         deck=[('plates', 'Light tees'), ('dark', 'Dark tees')], dz=['plates'], og_img='img/shirts/black-bart-back.webp',
         tile='img/designs/blue-grotto.webp', tile_alt='Blue Grotto plate preview, watermarked',
         title='Signature Series · dive sites, drawn by hand', desc='Fourteen wrecks, springs and reefs we have dived, drawn plate by plate with depths, landmarks and species, and screen-printed on tees: black ink on soft pastels, white on the dark line.',
         tagline='Dive sites, drawn by hand', count_note='designs',
         shirts_intro='Fourteen sites, each photographed on the shirt it ships on, and the same fourteen again as the dark line: white ink on a dark garment, shown as mockups built from those photographs. Every site has its own garment colour, so the deck is the palette of the line.',
         shirts_note='Colours are the garment colours each site was printed on; the final run may add or swap a colour per site. <a href="/#contact" data-umami-event="shirts-contact">Get the launch email</a> to hear when yours ships, or <a href="/custom/" data-umami-event="shirts-custom">make your own</a>: any design, any colour, your line or logo.',
         designs_intro='Every plate, drawn by hand from the dive itself. Tap one for the full back print, facts and all. Previews are watermarked and low resolution; the shirts carry the full art.',
         make_copy='Any plate on the garment colour you choose, with your own line on it: a date, a buddy, a boat.'),
    dict(key='certified-ish', dir='certified-ish', name='Certified-ish', short='Certified-ish', tab='certifiedish',
         deck=[('certifiedish', 'Light tees'), ('certifiedish-dark', 'Dark tees')], dz=['certifiedish'], og_img='img/designs/cert-night.webp',
         tile='img/designs/cert-night.webp', tile_alt='Night Diver Certified-ish preview, watermarked', tile_cls=' cert',
         title='Certified-ish · the courses, as they really feel', desc='One tongue-in-cheek diagram for each specialty in your logbook, from Open Water to Rebreather, printed full size on the back. Black ink on a light tee, or white ink on a dark one.',
         tagline='The courses, as they really feel', count_note='specialties',
         shirts_intro='Twenty Certified-ish backs on the tee they ship on, and the same twenty again in white ink on a dark one. The DS mark rides along the sleeve; the shark stays on the Signature Series.',
         shirts_note='Mockups, one garment colour each way; the final run may add or swap a colour. <a href="/#contact" data-umami-event="shirts-contact">Get the launch email</a> to hear when yours ships, or <a href="/custom/#tab=certifiedish" data-umami-event="shirts-custom">make your own</a>: any diagram, any colour, your line or logo.',
         designs_intro='Twenty diagrams, one per specialty, drawn by hand. Deep Diver charts narcosis one martini at a time; Night Diver labels everything that is watching you. Tap one for the full back print.',
         make_copy='Any Certified-ish diagram on the garment colour you choose, with your own line under it.'),
    dict(key='off-world', dir='off-world', name='Off-World Hunt Club', short='Off-World', tab='offworld',
         deck=[('offworld', 'Light tees'), ('offworld-dark', 'Dark tees')], dz=['offworld'], og_img='img/lines/off-world-tile.webp',
         tile='img/lines/off-world-tile.webp', tile_alt='Cloaked Off-World Hunt Club preview, watermarked',
         title='Off-World Hunt Club · a hunters’ script from somewhere else', desc='Thirty lines in an off-world script, each translated underneath with one word in red. The DS mark carries the word on the chest, in glyphs. Black and red ink on light tees; white and red on the dark line.',
         tagline='A hunters’ script from somewhere else', count_note='lines',
         shirts_intro='Thirty lines, each on a light tee and again on a dark one. The back carries the line in the script with its translation beneath, one word in red; the chest carries the DS mark with that word in glyphs.',
         shirts_note='Mockups, one garment colour each way; the final run may add or swap a colour. <a href="/#contact" data-umami-event="shirts-contact">Get the launch email</a> to hear when yours ships, or <a href="/custom/#tab=offworld" data-umami-event="shirts-custom">make your own</a>: any line, any colour.',
         designs_intro='The thirty backs: the script, the translation and the one word in red. Stealth, travel, the hunt, and Earth reviewed. Tap one for the full print.',
         make_copy='Any Off-World line on the garment colour you choose, the punch word in red.'),
    dict(key='n73', dir='1n73ll1g3nc3', name='1N73LL1G3NC3', short='1N73LL1G3NC3', tab='n73',
         deck=[('n73', 'The shirts')], dz=['n73'], og_img='img/lines/n73-tile.webp',
         tile='img/lines/n73-tile.webp', tile_alt='Trust But Test 1N73LL1G3NC3 preview, watermarked',
         title='1N73LL1G3NC3 · messages hiding in plain sight', desc='Thirty-six shirts that say something once you read them right: bold characters, meter dials, bubbles, hex. Dive, utility and power, mindset, flight, code and RC cars, each printed full front on a colour picked for its theme.',
         tagline='Messages hiding in plain sight', count_note='messages',
         shirts_intro='Thirty-six full-front prints, each on the garment colour its theme asked for. Read the bold characters, the dials or the code and it speaks.',
         shirts_note='Mockups, one garment colour each; the final run may add or swap a colour. <a href="/#contact" data-umami-event="shirts-contact">Get the launch email</a> to hear when yours ships, or <a href="/custom/#tab=n73" data-umami-event="shirts-custom">make your own</a>.',
         designs_intro='The thirty-six fronts, at full size. Dive, utility and power, mindset, flight, code, RC cars. Tap one to read it properly.',
         make_copy='Any of the thirty-six on the colour you choose.'),
    dict(key='aquatic', dir='aquatic-comic', name='Aquatic Comic', short='Aquatic Comic', tab='aquatic',
         deck=[('aquatic-boat-banter', 'Boat Banter'), ('aquatic-self-logged', 'Self-Logged'), ('aquatic-buddy-check', 'Buddy Check'),
               ('aquatic-buddy-system', 'Buddy System'), ('aquatic-till-surface', 'Till Surface Do Us Part'), ('aquatic-master-class', 'Master Class')],
         dz=['aquatic'], og_img='img/lines/aquatic-tile.webp',
         tile='img/lines/aquatic-tile.webp', tile_alt='Plan the dive, Aquatic Comic preview, watermarked',
         title='Aquatic Comic · jokes told on the dive deck', desc='The DS mark over the slogan on the left chest, the joke on the back, its punch words in red. Twenty to wear as they are, and five sets with your names in the joke.',
         tagline='Jokes told on the dive deck', count_note='jokes',
         shirts_intro='Fifty-nine jokes on dark tees: twenty to wear as they are (Boat Banter), and five sets with names in the joke: Self-Logged, about you; Buddy Check, about your dive buddy; Buddy System, two names for a pair; Till Surface Do Us Part, for a husband-and-wife team; Master Class, for the one who has heard it all.',
         shirts_note='Mockups on the dark palette; the named sets are printed with the names you give at checkout. <a href="/#contact" data-umami-event="shirts-contact">Get the launch email</a> to hear when they ship, or <a href="/custom/#tab=aquatic" data-umami-event="shirts-custom">make your own</a>.',
         designs_intro='Fifty-nine chest-and-back jokes. Pick a set, or search for the one about you. Tap a design for the chest lockup and the back print together.',
         make_copy='Any joke on the dark colour you choose; the named ones with your names.'),
]
BY_KEY = {l['key']: l for l in LINES}

# ---------------------------------------------------------------------------------------------------------- the themes
THEME = {}
HERO = {}

THEME['signature'] = """
/* Signature Series: the chart sheet, as the home page */
.hero-band{background-image:repeating-radial-gradient(circle at 78% 130%,transparent 0 26px,rgba(255,255,255,.045) 26px 27px)}
.hero .sheet img{width:100%;height:auto;display:block;border-radius:3px;border:1px solid rgba(255,255,255,.14)}
"""
HERO['signature'] = """
    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Doolittle Scuba &middot; Signature Series</p>
        <h1>Dive sites, drawn by hand.</h1>
        <p class="lede">Fourteen wrecks, springs and reefs we have actually dived, drawn plate by plate with their depths, landmarks and species, and printed in one colour: black on soft pastel tees, white on the dark line.</p>
        <div class="cta">
          <a class="btn" data-umami-event="hero-shirts" href="#shirts">See the shirts</a>
          <a class="btn ghost" data-umami-event="hero-dark" href="#dark">The dark line</a>
          <a class="txt" data-umami-event="hero-map" href="/#map">Where we dived &rarr;</a>
        </div>
        {swatches}
      </div>
      <figure class="sheet" style="margin:0">
        <div class="coord mono" aria-label="Black Bart, Panama City Beach: 30 degrees 03.65 minutes north, 85 degrees 49.43 minutes west">BLACK BART &nbsp; 30°03.650 N &nbsp; 085°49.430 W</div>
        <img src="/img/shirts/black-bart-back.webp" alt="The Black Bart shirt worn, back view: the full site plate, facts, species and water notes in black ink on light blue" width="1200" height="1200">
      </figure>
    </div>
"""

THEME['certified-ish'] = """
/* Certified-ish: a page torn from the logbook — cream paper, ruled lines, a rubber stamp */
:root{--paper:#F5F0E4;--panel:#FCF9F2;--text:#26241F;--muted:#6B655A;--ink:#1E2F4D;--red:#B9201F;--blue:#1F4FA3;--rule:#D9D0BC;--contour:#E6DECA;
  --deep:#1E2F4D;--deep-2:#172540;--on-deep:#F5F0E4;--on-deep-muted:#B9C2D3}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--paper:#151A23;--panel:#1C2330;--text:#E8E2D6;--muted:#9BA3B1;--ink:#E8E2D6;--red:#E0535A;--blue:#7FA6E8;--rule:#2C3545;--contour:#222B3A}}
:root[data-theme="dark"]{--paper:#151A23;--panel:#1C2330;--text:#E8E2D6;--muted:#9BA3B1;--ink:#E8E2D6;--red:#E0535A;--blue:#7FA6E8;--rule:#2C3545;--contour:#222B3A}
.hero-band{background-image:repeating-linear-gradient(transparent 0 30px,rgba(255,255,255,.07) 30px 31px)}
.hero h1{font-weight:400}
.stamp{display:inline-block;align-self:flex-start;transform:rotate(-6deg);border:3px double var(--brand-red);color:#fff;background:var(--brand-red);font:700 .9rem/1 var(--f-data);letter-spacing:.16em;text-transform:uppercase;padding:9px 14px;border-radius:5px;box-shadow:inset 0 0 0 2px #fff}
.card-cert{position:relative;background:#FCF9F2;color:#26241F;border:1px solid #D9D0BC;border-radius:10px;padding:clamp(16px,2.6vw,26px);display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px 20px;box-shadow:0 24px 40px -24px rgba(0,0,0,.55);background-image:repeating-linear-gradient(transparent 0 27px,#E6DECA 27px 28px);background-origin:content-box}
.card-cert .f{font-family:var(--f-data);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:#6B655A;display:block}
.card-cert .v{font-family:var(--f-display);font-size:var(--s1);color:#1E2F4D;display:block;line-height:1.2}
.card-cert .seal{grid-column:2;grid-row:1/span 3;justify-self:end;align-self:start;width:clamp(72px,10vw,110px);height:auto;opacity:.92}
.card-cert .art{grid-column:1/-1;margin:4px 0 0;border:1px solid #D9D0BC;border-radius:4px;overflow:hidden;aspect-ratio:3/2;background:#fff}
.card-cert .art img{width:100%;height:100%;object-fit:cover;object-position:center top;display:block}
.card-cert .stamp{position:absolute;right:clamp(6px,2vw,22px);bottom:clamp(8px,1.6vw,18px);transform:rotate(-9deg);font-size:1.05rem;padding:10px 16px;opacity:.96;box-shadow:inset 0 0 0 2px #fff,0 6px 14px -8px rgba(0,0,0,.5)}
.head h2{font-weight:400}
"""
HERO['certified-ish'] = """
    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Doolittle Scuba &middot; Certified-ish</p>
        <h1>The courses, as they really feel.</h1>
        <p class="lede">One tongue-in-cheek diagram for each specialty in your logbook, from Open Water to Rebreather, printed full size on the back. Deep Diver charts narcosis one martini at a time; Night Diver labels everything that is watching you.</p>
        <div class="cta">
          <a class="btn" data-umami-event="hero-shirts" href="#shirts">See the shirts</a>
          <a class="btn ghost" data-umami-event="hero-dark" href="#certifiedish-dark">The dark line</a>
          <a class="txt" data-umami-event="hero-designs" href="#designs">All twenty diagrams &rarr;</a>
        </div>
        {swatches}
      </div>
      <div class="card-cert" aria-label="A Certified-ish card">
        <span><span class="f">Diver</span><span class="v">You, probably</span></span>
        <img class="seal" src="/img/brand/seal.png" alt="" width="220" height="220">
        <span><span class="f">Certified in</span><span class="v">Twenty specialties, give or take</span></span>
        <span><span class="f">Issued</span><span class="v">The day you wore it</span></span>
        <figure class="art" oncontextmenu="return false"><img src="/img/designs/cert-night.webp" alt="Night Diver, Certified-ish: a diver's torch beam, and everything in the dark watching it, watermarked preview" width="450" height="620" draggable="false"></figure>
        <span class="stamp">Certified-ish</span>
      </div>
    </div>
"""

THEME['off-world'] = """
/* Off-World Hunt Club: near-black, a starfield, one word in red */
:root[data-theme="dark"]{--paper:#0B0C10;--panel:#14161D;--text:#E6E4DE;--muted:#9A9EAB;--ink:#F1EFE8;--red:#E8343E;--blue:#7FA6E8;--rule:#262933;--contour:#1B1E27;
  --deep:#050609;--deep-2:#0B0C10;--on-deep:#F1EFE8;--on-deep-muted:#9A9EAB;--brand-red:#E8343E;color-scheme:dark}
body{background-image:radial-gradient(1px 1px at 12% 18%,rgba(255,255,255,.55) 50%,transparent 51%),radial-gradient(1px 1px at 48% 72%,rgba(255,255,255,.35) 50%,transparent 51%),radial-gradient(1.5px 1.5px at 83% 36%,rgba(255,255,255,.5) 50%,transparent 51%),radial-gradient(1px 1px at 66% 9%,rgba(255,255,255,.4) 50%,transparent 51%),radial-gradient(1px 1px at 28% 88%,rgba(255,255,255,.3) 50%,transparent 51%);background-size:900px 700px;background-attachment:fixed}
.hero-band{border-bottom-color:var(--red);background-image:radial-gradient(1.5px 1.5px at 8% 30%,#fff 50%,transparent 51%),radial-gradient(1px 1px at 22% 70%,rgba(255,255,255,.8) 50%,transparent 51%),radial-gradient(2px 2px at 37% 20%,#fff 50%,transparent 51%),radial-gradient(1px 1px at 55% 85%,rgba(255,255,255,.7) 50%,transparent 51%),radial-gradient(1.5px 1.5px at 64% 40%,#fff 50%,transparent 51%),radial-gradient(1px 1px at 78% 12%,rgba(255,255,255,.8) 50%,transparent 51%),radial-gradient(2px 2px at 90% 62%,#fff 50%,transparent 51%),radial-gradient(1px 1px at 96% 88%,rgba(255,255,255,.7) 50%,transparent 51%),radial-gradient(1px 1px at 44% 55%,rgba(255,255,255,.6) 50%,transparent 51%),radial-gradient(ellipse 70% 40% at 50% 118%,rgba(232,52,62,.28),transparent 70%)}
.hero h1 em{font-style:normal;color:var(--red)}
.hero .sheet img{width:100%;height:auto;display:block;border:1px solid rgba(255,255,255,.16);border-radius:3px;filter:invert(1) hue-rotate(180deg)}  /* the light preview shown as the dark line: white ink, the word still red */
.hero .coord{border-left-color:var(--red)}
.dk{box-shadow:-10px 0 18px -12px rgba(0,0,0,.7)}
.dk.on{box-shadow:0 30px 44px -18px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}
.dk-tag,.sh-panel{box-shadow:0 14px 28px -16px rgba(0,0,0,.8)}
.head h2{letter-spacing:.01em}
.glyph-rule{height:1px;background:linear-gradient(90deg,transparent,var(--red) 20%,var(--red) 80%,transparent);margin:0 auto;max-width:420px;opacity:.7}
"""
HERO['off-world'] = """
    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Doolittle Scuba &middot; Off-World Hunt Club</p>
        <h1>Came for the trophy. Stayed for the <em>reef</em>.</h1>
        <p class="lede">Thirty lines in a hunters&rsquo; script from somewhere else, each translated underneath with one word in red. The DS mark carries that word on the chest, in glyphs. Black and red ink on the light tees; white and red on the dark line.</p>
        <div class="cta">
          <a class="btn" data-umami-event="hero-shirts" href="#shirts">See the shirts</a>
          <a class="btn ghost" data-umami-event="hero-dark" href="#offworld-dark">The dark line</a>
          <a class="txt" data-umami-event="hero-designs" href="#designs">Read all thirty &rarr;</a>
        </div>
        {swatches}
      </div>
      <figure class="sheet" style="margin:0">
        <div class="coord mono" aria-label="Off-World Hunt Club, thirty lines, stealth, travel, the hunt and Earth reviewed">STEALTH &nbsp;&middot;&nbsp; TRAVEL &nbsp;&middot;&nbsp; THE HUNT &nbsp;&middot;&nbsp; EARTH, REVIEWED</div>
        <img src="/img/lines/off-world-tile.webp" alt="Cloaked: the line in the off-world script with its translation, I'm not ignoring you, I'm cloaked, the last word in red; watermarked preview" width="800" height="600">
      </figure>
    </div>
"""

THEME['n73'] = """
/* 1N73LL1G3NC3: graphite terminal, cream phosphor, a grid behind everything */
:root[data-theme="dark"]{--paper:#141618;--panel:#1B1E21;--text:#DADFDB;--muted:#8E978F;--ink:#ECEFEA;--red:#E8343E;--blue:#8FB4FF;--rule:#2A2F33;--contour:#202427;
  --deep:#0E1012;--deep-2:#141618;--on-deep:#ECEFEA;--on-deep-muted:#8E978F;--brand-red:#E8343E;--phos:#E9DDB8;color-scheme:dark;
  --f-display:"JetBrains Mono",ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;--f-body:"Jost","Alegreya Sans",system-ui,sans-serif;--f-data:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace}
h1,h2,h3,.dz-t,.dk-tab .nm,.dk-tag .t,.sh-info h3,.more-tile .t{letter-spacing:-.01em}
.hero-band{border-bottom-color:var(--phos);background-image:linear-gradient(rgba(233,221,184,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(233,221,184,.06) 1px,transparent 1px);background-size:32px 32px;background-position:center top}
.term{font-family:var(--f-data);font-size:clamp(.85rem,1.4vw,1rem);color:var(--phos);display:flex;flex-wrap:wrap;gap:0 .6em;align-items:baseline}
.term .p{color:var(--muted)}
.term .cur{display:inline-block;width:.6em;height:1.1em;background:var(--phos);vertical-align:-.15em;animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
@media (prefers-reduced-motion:reduce){.term .cur{animation:none}}
.hero h1{font-size:clamp(2.2rem,5.4vw,3.9rem);color:var(--phos);text-transform:uppercase;letter-spacing:.02em}
.hero h1 small{display:block;font-size:.42em;letter-spacing:.14em;color:var(--on-deep-muted);margin-top:.5em;font-weight:400}
.hero .sheet img{width:100%;height:auto;display:block;border:1px solid rgba(233,221,184,.25);border-radius:3px}
.hero .coord{border-left-color:var(--phos);color:var(--phos)}
.chip.on{background:var(--phos);border-color:var(--phos);color:#141618}
.btn{background:var(--phos);color:#141618}
.btn.ghost{background:transparent;color:var(--on-deep);box-shadow:inset 0 0 0 1.5px var(--on-deep)}
.pill.completed{background:#2F3A33}
.dk{box-shadow:-10px 0 18px -12px rgba(0,0,0,.7)}
.dk.on{box-shadow:0 30px 44px -18px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}
.deck-foot,.specs,.two .card,.line{border-color:var(--phos)}
.head h2 small{display:block;font:400 var(--s-1) var(--f-data);letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-top:6px}
"""
HERO['n73'] = """
    <div class="hero">
      <div class="hero-copy">
        <p class="term" aria-hidden="true"><span class="p">&gt;</span>1N73LL1G3NC3 <span class="p">--decode</span><span class="cur"></span></p>
        <p class="eyebrow">Doolittle Scuba &middot; 1N73LL1G3NC3</p>
        <h1>R34D 17 R1GH7.<small>Read it right, and it speaks.</small></h1>
        <p class="lede">Thirty-six shirts that say something once you read them right: the bold characters, the meter dials, the bubbles, the hex. Dive, utility and power, mindset, flight, code and RC cars, each printed full front on a garment colour picked for its theme.</p>
        <div class="cta">
          <a class="btn" data-umami-event="hero-shirts" href="#shirts">See the shirts</a>
          <a class="btn ghost" data-umami-event="hero-designs" href="#designs">Read all thirty-six</a>
        </div>
        {swatches}
      </div>
      <figure class="sheet" style="margin:0">
        <div class="coord mono" aria-label="Six themes: dive, utility and power, mindset, flight, code, RC cars">D1V3 &nbsp;&middot;&nbsp; P0W3R &nbsp;&middot;&nbsp; M1ND537 &nbsp;&middot;&nbsp; FL1GH7 &nbsp;&middot;&nbsp; C0D3 &nbsp;&middot;&nbsp; RC</div>
        <img src="/img/lines/n73-tile.webp" alt="Read the meter: four kilowatt-hour dials spelling 7357, and the line Trust But Test in bold characters; watermarked preview" width="800" height="600">
      </figure>
    </div>
"""

THEME['aquatic'] = """
/* Aquatic Comic: warm paper, IM Fell, halftone dots, a speech bubble with the punch word in red */
:root{--paper:#F7F3EA;--panel:#FFFDF8;--text:#1B1B1B;--muted:#6A655C;--ink:#151515;--red:#C8202A;--blue:#1F4FA3;--rule:#E2DACB;--contour:#EEE7D8;
  --deep:#141414;--deep-2:#0C0C0C;--on-deep:#F7F3EA;--on-deep-muted:#B5AFA3;--f-display:"IM Fell English","Almendra",Georgia,serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--paper:#121212;--panel:#1B1B1B;--text:#ECE7DC;--muted:#A19B90;--ink:#F3EFE6;--red:#E5535A;--blue:#7FA6E8;--rule:#2C2C2C;--contour:#232323}}
:root[data-theme="dark"]{--paper:#121212;--panel:#1B1B1B;--text:#ECE7DC;--muted:#A19B90;--ink:#F3EFE6;--red:#E5535A;--blue:#7FA6E8;--rule:#2C2C2C;--contour:#232323}
h1,h2,h3,.dz-t,.dk-tag .t,.sh-info h3,.more-tile .t{font-weight:400}
.hero-band{background-image:radial-gradient(rgba(255,255,255,.09) 1.1px,transparent 1.6px);background-size:11px 11px}
.hero h1{font-size:clamp(2.6rem,6.2vw,4.6rem)}
.bubble{position:relative;margin:0;background:#fff;color:#151515;border:2px solid #151515;border-radius:18px;padding:clamp(18px,3vw,30px) clamp(20px,3.4vw,36px);font-family:var(--f-display);font-style:italic;font-size:clamp(1.25rem,2.4vw,1.8rem);line-height:1.25;box-shadow:6px 6px 0 var(--brand-red)}
.bubble em{font-style:italic;color:var(--brand-red)}
.bubble::after{content:"";position:absolute;left:14%;bottom:-20px;width:32px;height:32px;background:#fff;border-right:2px solid #151515;border-bottom:2px solid #151515;transform:skewX(32deg) rotate(45deg);border-radius:0 0 3px 0}
.bubble cite{display:block;font-style:normal;font-family:var(--f-data);font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:#6A655C;margin-top:14px}
.hero .sheet img{width:100%;height:auto;display:block;border:2px solid #151515;border-radius:3px}
.hero .coord{border-left-color:var(--brand-red)}
.dz-s em,.line-body em{color:var(--red);font-style:italic}
.chip.on{background:var(--ink);border-color:var(--ink)}
"""
HERO['aquatic'] = """
    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Doolittle Scuba &middot; Aquatic Comic</p>
        <h1>Jokes told on the dive deck.</h1>
        <blockquote class="bubble">Plan the dive. Dive the plan. Blame the <em>current</em>.<cite>Boat Banter, No. S02</cite></blockquote>
        <p class="lede">The DS mark over the slogan on the left chest, the joke on the back, its punch words in red. Twenty to wear as they are, and five sets with your names in the joke.</p>
        <div class="cta">
          <a class="btn" data-umami-event="hero-shirts" href="#shirts">See the shirts</a>
          <a class="btn ghost" data-umami-event="hero-named" href="#aquatic-self-logged">The named sets</a>
          <a class="txt" data-umami-event="hero-designs" href="#designs">Read all fifty-nine &rarr;</a>
        </div>
        {swatches}
      </div>
      <figure class="sheet" style="margin:0">
        <div class="coord mono" aria-label="Six sets: Boat Banter, Self-Logged, Buddy Check, Buddy System, Till Surface Do Us Part, Master Class">SIX SETS &nbsp;&middot;&nbsp; FIFTY-NINE JOKES &nbsp;&middot;&nbsp; YOUR NAMES, OPTIONAL</div>
        <img src="/img/lines/aquatic-tile.webp" alt="Plan the dive, dive the plan, blame the current: the DS mark over the slogan on the chest and the joke on the back, the punch word in red; watermarked preview" width="800" height="600">
      </figure>
    </div>
"""

FONTS = {
    'n73': 'https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600&family=JetBrains+Mono:wght@400;600;700&display=swap',
    'aquatic': 'https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&display=swap',
}
FIXED_DARK = {'off-world', 'n73'}


# ----------------------------------------------------------------------------------------------------------- harvesting
def home(): return open(f'{SITE}/index.html', encoding='utf-8').read()


def block(src, start, end):
    i = src.index(start); j = src.index(end, i) + len(end); return src[i:j]


def absolutise(card):
    """img/… paths in a card lifted from the home page become /img/… so they resolve from any folder."""
    return re.sub(r'\b(src|data-front|data-back|data-full|data-art)="img/', r'\1="/img/', card)


def harvest(line, page_src, home_src):
    src = page_src if page_src and '<!-- SH:END -->' in page_src else home_src
    fresh = src is home_src
    sh = []
    for key, _ in line['deck']:
        sh += re.findall(rf'<figure class="sh" data-line="{key}".*?</figure>', src, re.S)
    dz = []
    for key in line['dz']:
        dz += re.findall(rf'<figure class="dz" data-status="[a-z]+" data-line="{key}".*?</figure>', src, re.S)
    if fresh:
        sh = [absolutise(c) for c in sh]; dz = [absolutise(c) for c in dz]
    if line['key'] == 'aquatic':   # the subset chips filter on data-sub
        def sub(c):
            if 'data-sub=' in c: return c
            slug = re.search(r'data-umami-event-design="([a-z0-9-]+)"', c).group(1)
            return c.replace('data-line="aquatic"', f'data-line="aquatic" data-sub="{AQ_SUB[slug]}"', 1)
        dz = [sub(c) for c in dz]
    return sh, dz


def swatches(sh_cards):
    seen, out = set(), []
    for c in sh_cards:
        m = re.search(r'data-colour="([^"]+)" data-hex="(#[0-9A-Fa-f]{6})"', c)
        if m and m.group(2) not in seen:
            seen.add(m.group(2)); out.append(f'<li style="--sw:{m.group(2)}"><i></i>{m.group(1)}</li>')
    return f'<ul class="swatches" aria-label="Garment colours">{"".join(out)}</ul>'


# -------------------------------------------------------------------------------------------------------------- the page
def nav(line_dir):
    return ('<nav aria-label="Site"><a href="/#lines" data-umami-event="nav-collections">Collections</a><a href="/#hats" data-umami-event="nav-hats">Hats</a>'
            '<a href="/#stickers" data-umami-event="nav-stickers">Stickers</a><a href="/custom/" data-umami-event="nav-custom">Custom</a>'
            '<a href="/#map" data-umami-event="nav-map">Dive map</a><a href="/#logbook" data-umami-event="nav-logbook">Logbook</a>'
            '<a href="/about/" data-umami-event="nav-about">About us</a><a href="/workshop/" data-umami-event="nav-workshop">Workshop</a>'
            '<a href="/#contact" data-umami-event="nav-contact">Contact</a></nav>')


def switcher(cur):
    links = ''.join(f'<a href="/{l["dir"]}/"{" aria-current=\"page\"" if l is cur else ""} data-umami-event="coll-switch" data-umami-event-line="{l["key"]}">{H.escape(l["name"])}</a>' for l in LINES)
    return f'<nav class="coll" aria-label="Collections"><div class="wrap"><span class="lbl">The collections</span>{links}</div></nav>'


def chips(dz_cards, line):
    cnt = {k: sum(1 for c in dz_cards if f'data-status="{k}"' in c) for k in ('available', 'completed', 'progress')}
    label = {'available': 'Coming soon', 'completed': 'Art finished', 'progress': 'In progress'}
    out = [f'<button type="button" class="chip on" data-f="all" data-umami-event="designs-filter" data-umami-event-filter="all" aria-pressed="true">All <span class="mono">{len(dz_cards)}</span></button>']
    for k in ('available', 'completed', 'progress'):
        if cnt[k]:
            out.append(f'<button type="button" class="chip" data-f="{k}" data-umami-event="designs-filter" data-umami-event-filter="{k}" aria-pressed="false">{label[k]} <span class="mono">{cnt[k]}</span></button>')
    if line['key'] == 'aquatic':
        out.append('<span class="dz-sep" aria-hidden="true"></span>')
        for key, name in line['deck']:
            s = key[len('aquatic-'):]; n = sum(1 for c in dz_cards if f'data-sub="{s}"' in c)
            out.append(f'<button type="button" class="chip" data-s="{s}" data-umami-event="designs-subset" data-umami-event-subset="{s}" aria-pressed="false">{H.escape(name)} <span class="mono">{n}</span></button>')
    out.append('<input type="search" class="dz-q" placeholder="Search these designs" aria-label="Search the designs by word: a subject, a site, a line of the joke" autocomplete="off">')
    return '\n        '.join(out), cnt


def more_tiles(cur):
    out = []
    for l in LINES:
        if l is cur: continue
        n = COUNTS.get(l['key'], '')
        out.append(f'<a class="more-tile" href="/{l["dir"]}/" data-umami-event="coll-more" data-umami-event-line="{l["key"]}">'
                   f'<figure class="line-art{l.get("tile_cls", "")}" oncontextmenu="return false"><img src="/{l["tile"]}" width="800" height="600" loading="lazy" decoding="async" draggable="false" alt="{H.escape(l["tile_alt"])}"></figure>'
                   f'<span class="t">{H.escape(l["name"])}</span><span class="s">{n} {l["count_note"]} &middot; {H.escape(l["tagline"])}</span></a>')
    return ''.join(out)


COUNTS = {}


def page(line, sh, dz, home_src):
    status = block(home_src, '<!-- STATUS:START -->', '<!-- STATUS:END -->')
    wide = block(home_src, '<!-- WIDE:START -->', '<!-- WIDE:END -->')
    social = block(home_src, '<!-- SOCIAL:START -->', '<!-- SOCIAL:END -->')
    url = f'{ORIGIN}/{line["dir"]}/'
    fonts = f'<link rel="stylesheet" href="{FONTS_BASE}">' + (f'\n<link rel="stylesheet" href="{FONTS[line["key"]]}">' if line['key'] in FONTS else '')
    html_attr = ' data-theme="dark"' if line['key'] in FIXED_DARK else ''
    theme_color = {'off-world': '#050609', 'n73': '#0E1012', 'aquatic': '#141414', 'certified-ish': '#1E2F4D'}.get(line['key'], '#122A55')
    deck_lines = json.dumps([[k, n] for k, n in line['deck']], ensure_ascii=False)
    bar, cnt = chips(dz, line)
    jsonld = json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": f'{line["name"]} · Doolittle Scuba', "url": url,
                         "description": line['desc'], "isPartOf": {"@type": "WebSite", "name": "Doolittle Scuba", "url": ORIGIN + '/'},
                         "publisher": {"@type": "Organization", "name": "Doolittle Scuba L.L.C.", "url": ORIGIN + '/'}}, ensure_ascii=False)
    sites = block(home_src, '<!-- SITEDATA:START -->', '<!-- SITEDATA:END -->') if line['key'] == 'signature' else ''
    hero = HERO[line['key']].replace('{swatches}', swatches(sh[:len(sh) // (2 if len(line['deck']) == 2 else 1)] if line['key'] != 'aquatic' else sh))
    make_tab = f'/custom/#tab={line["tab"]}' if line['tab'] else '/custom/'
    return f'''<!doctype html>
<html lang="en"{html_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{H.escape(line["name"])} · Doolittle Scuba</title>
<meta name="description" content="{H.escape(line["desc"], quote=True)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Doolittle Scuba">
<meta property="og:title" content="{H.escape(line["title"], quote=True)}">
<meta property="og:description" content="{H.escape(line["desc"], quote=True)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{ORIGIN}/img/og/{line["dir"]}.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{H.escape(line["name"])}: {H.escape(line["tagline"])}, by Doolittle Scuba">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" href="/img/brand/icon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="{theme_color}">
<script type="application/ld+json">{jsonld}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{fonts}
<link rel="stylesheet" href="/css/site.css">
<style>{THEME[line["key"]]}</style>
{wide}
</head>
<body>
{status}
<div class="deep">
  <div class="wrap">
    <header class="top">
      <a class="brand" data-umami-event="nav-logo" href="/" aria-label="Doolittle Scuba L.L.C., Do - A - Little Scuba, home"><img src="/img/brand/lockup-h-dark.png" alt="Doolittle Scuba L.L.C. — Do - A - Little Scuba" width="900" height="193"></a>
      {nav(line["dir"])}
    </header>
  </div>
</div>
{switcher(line)}
<main>
  <div class="deep hero-band"><div class="wrap">
{hero}  </div></div>
  <div class="wrap">

    <section id="shirts" aria-labelledby="shirts-h">
      <div class="head">
        <h2 id="shirts-h">The shirts</h2>
        <p>{line["shirts_intro"]}</p>
      </div>
      <div class="sh-grid" id="sh-grid">{"".join(sh)}<!-- SH:END --></div>
      <p class="dz-note">{line["shirts_note"]}</p>
    </section>

    <section id="designs" aria-labelledby="designs-h">
      <div class="head">
        <h2 id="designs-h">The designs</h2>
        <p>{line["designs_intro"]}</p>
      </div>
      <div class="dz-bar" role="group" aria-label="Filter designs">
        {bar}
      </div>
      <div class="dz-grid" id="dz-grid">{"".join(dz)}<!-- DZ:END --></div>
      <p class="dz-none" hidden>No design matches that. Try a shorter word, or <a href="/#lines">search every collection</a>.</p>
      <p class="dz-note">All artwork &copy; 2026 Doolittle Scuba L.L.C. Copying, printing or reuse of any design without written permission is prohibited. Shops interested in a design: <a href="/#contact" data-umami-event="designs-contact">get in touch</a>.</p>
    </section>

    <section id="make" aria-labelledby="make-h">
      <div class="head">
        <h2 id="make-h">Wear it your way</h2>
        <p>Nothing ships until the samples pass; the designs are drawn, proofed and waiting on the first run.</p>
      </div>
      <div class="two">
        <div class="card">
          <h3>Get launch news</h3>
          <p>One email when the {H.escape(line["name"])} shirts ship. No newsletter, no sharing your address.</p>
          <a class="btn" href="/#contact" data-umami-event="make-launch-news" data-umami-event-line="{line["key"]}">Tell me when they ship</a>
        </div>
        <div class="card">
          <h3>Make it yours</h3>
          <p>{line["make_copy"]}</p>
          <a class="btn ghost" href="{make_tab}" data-umami-event="make-custom" data-umami-event-line="{line["key"]}">Open Make it yours</a>
        </div>
      </div>
    </section>

    <section id="more" aria-labelledby="more-h">
      <div class="head">
        <h2 id="more-h">The other collections</h2>
        <p>Five lines, one hand. Each has a page of its own.</p>
      </div>
      <div class="more">{more_tiles(line)}</div>
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

{sites}
<script src="/js/deck.js"></script>
<script>
DS.lightbox();
DS.deck('shirts','sh-grid',DS.shirtsCfg({{lines:{deck_lines}, contact:'/#contact'}}));
DS.designs();
</script>

<!-- Umami visitor analytics (cookie-free). Runs only on the live domain. -->
<script defer src="https://cloud.umami.is/script.js" data-website-id="97eb29ce-9e01-43d7-8047-5d59024eeea7" data-domains="doolittlescuba.com,www.doolittlescuba.com"></script>
</body>
</html>
'''


# ------------------------------------------------------------------------------------------------------- the search index
def strip(s): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(s))).strip()


def busted(ref):
    """/img/x.webp -> /img/x.webp?v=<sha1[:8]>, like tools/bust.py, so the CDN sees a new URL when the file changes."""
    base = ref.split('?', 1)[0]; f = f'{SITE}/{base.lstrip("/")}'
    if not os.path.isfile(f): return base
    return base + '?v=' + hashlib.sha1(open(f, 'rb').read()).hexdigest()[:8]


def index_entry(line, c, sh_text):
    slug = re.search(r'data-umami-event-design="([a-z0-9-]+)"', c)
    slug = slug.group(1) if slug else re.sub(r'[^a-z0-9]+', '-', strip(re.search(r'<span class="dz-t">(.*?)</span>', c).group(1)).lower())
    name = strip(re.search(r'<span class="dz-t">(.*?)</span>', c).group(1))
    sub = re.search(r'<span class="dz-s">(.*?)</span>', c); sub = strip(sub.group(1)) if sub else ''
    thumb = re.search(r'<img src="([^"]+)"', c); alt = re.search(r' alt="([^"]*)"', c); cap = re.search(r'data-cap="([^"]*)"', c)
    status = re.search(r'data-status="([a-z]+)"', c).group(1)
    extra = ''
    if line['key'] == 'signature' and slug in SITES: extra = ' '.join(str(SITES[slug].get(k, '')) for k in ('place', 'water', 'fact'))
    if line['key'] == 'aquatic' and slug in AQ_BACK: extra = AQ_BACK[slug]
    if line['key'] == 'signature':   # the site guide's own words: species, conditions, the story
        sp = f'{SITE}/sites/{slug}/index.html'
        if os.path.exists(sp):
            mt = re.search(r'<main.*?</main>', open(sp, encoding='utf-8').read(), re.S)
            if mt: extra += ' ' + strip(re.sub(r'<(script|style|nav)[^>]*>.*?</\1>', ' ', mt.group(0), flags=re.S))[:2500]
    extra += ' ' + SUBJ.get(slug, '')
    if line['key'] == 'n73':   # the messages are written in digits: index the decoded words too, so "read the meter" finds R34D 7H3 M373R
        extra += ' ' + (name + ' ' + SUBJ.get(slug, '')).translate(str.maketrans('0134578', 'oieastb'))
    q = ' '.join(x for x in [name, sub, line['name'], alt.group(1) if alt else '', cap.group(1) if cap else '', sh_text.get(slug, ''), extra] if x)
    return dict(slug=slug, name=name, sub=sub, line=line['name'], page=f'/{line["dir"]}/', thumb=busted(thumb.group(1)) if thumb else '', status=status,
                q=re.sub(r'\s+', ' ', H.unescape(q)).lower())


def og_image(line):
    from PIL import Image, ImageDraw, ImageFont
    W, Hh = 1200, 630
    bg = {'signature': (18, 42, 85), 'certified-ish': (30, 47, 77), 'off-world': (5, 6, 9), 'n73': (14, 16, 18), 'aquatic': (20, 20, 20)}[line['key']]
    im = Image.new('RGB', (W, Hh), bg); d = ImageDraw.Draw(im)
    art = Image.open(f'{SITE}/{line["og_img"]}').convert('RGB')
    bw, bh = 560, 470; s = min(bw / art.width, bh / art.height); art = art.resize((int(art.width * s), int(art.height * s)), Image.LANCZOS)
    x, y = 60 + (bw - art.width) // 2, 80 + (bh - art.height) // 2
    d.rectangle((x - 2, y - 2, x + art.width + 1, y + art.height + 1), outline=(255, 255, 255), width=2); im.paste(art, (x, y))
    f_e = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 22)
    f_n = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 60)
    while max(d.textlength(w, font=f_n) for w in line['name'].split()) > W - 680 - 50 and f_n.size > 36: f_n = ImageFont.truetype(f_n.path, f_n.size - 2)
    f_t = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf', 28)
    f_u = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 20)
    tx = 680; d.text((tx, 150), 'DOOLITTLE SCUBA', font=f_e, fill=(169, 185, 207))
    def wrap(text, font, width):
        lines, cur = [], ''
        for w in text.split():
            t = (cur + ' ' + w).strip()
            if d.textlength(t, font=font) > width and cur: lines.append(cur); cur = w
            else: cur = t
        return lines + [cur]
    yy = 200
    for t in wrap(line['name'], f_n, W - tx - 50): d.text((tx, yy), t, font=f_n, fill=(255, 255, 255)); yy += f_n.size + 8
    d.rectangle((tx, yy + 14, tx + 70, yy + 18), fill=(200, 32, 42)); yy += 40
    for t in wrap(line['tagline'], f_t, W - tx - 50): d.text((tx, yy), t, font=f_t, fill=(230, 235, 242)); yy += f_t.size + 10
    d.text((tx, Hh - 90), f'doolittlescuba.com/{line["dir"]}/', font=f_u, fill=(169, 185, 207))
    os.makedirs(f'{SITE}/img/og', exist_ok=True); im.save(f'{SITE}/img/og/{line["dir"]}.jpg', 'JPEG', quality=86, optimize=True)


def sitemap():
    p = f'{SITE}/sitemap.xml'; s = open(p, encoding='utf-8').read()
    for l in LINES:
        loc = f'{ORIGIN}/{l["dir"]}/'
        if loc not in s:
            s = s.replace(f'  <url><loc>{ORIGIN}/custom/</loc>', f'  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod></url>\n  <url><loc>{ORIGIN}/custom/</loc>', 1)
    s = re.sub(rf'(<loc>{re.escape(ORIGIN)}/</loc><lastmod>)[0-9-]+', rf'\g<1>{TODAY}', s)
    open(p, 'w', encoding='utf-8').write(s)


def main():
    home_src = home(); index = []
    try: SITES.update({x['slug']: x for x in json.loads(re.search(r'<script type="application/json" id="sites-data">(.*?)</script>', home_src, re.S).group(1))})
    except Exception as e: print('sites-data not read:', e)
    pages = {}
    for line in LINES:
        p = f'{SITE}/{line["dir"]}/index.html'
        page_src = open(p, encoding='utf-8').read() if os.path.exists(p) else None
        sh, dz = harvest(line, page_src, home_src)
        if not sh or not dz: sys.exit(f'{line["key"]}: no cards found ({len(sh)} shirts, {len(dz)} designs)')
        COUNTS[line['key']] = len(dz); pages[line['key']] = (sh, dz)
        sh_text = {}
        for c in sh:
            m = re.search(r'data-slug="([a-z0-9-]+)"', c); t = re.search(r'data-text="([^"]*)"', c)
            if m and t: sh_text[m.group(1)] = t.group(1)
        index += [index_entry(line, c, sh_text) for c in dz]
    for line in LINES:   # second pass so every page knows every count
        sh, dz = pages[line['key']]
        os.makedirs(f'{SITE}/{line["dir"]}', exist_ok=True)
        open(f'{SITE}/{line["dir"]}/index.html', 'w', encoding='utf-8').write(page(line, sh, dz, home_src))
        if '--og' in sys.argv or not os.path.exists(f'{SITE}/img/og/{line["dir"]}.jpg'): og_image(line)
        print(f'/{line["dir"]}/  {len(sh)} shirt cards, {len(dz)} designs')
    json.dump(index, open(f'{SITE}/js/designs.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('js/designs.json', len(index), 'designs'); sitemap(); print('sitemap.xml')


if __name__ == '__main__':
    main()
