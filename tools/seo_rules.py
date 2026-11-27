"""Search-description rules for tools/seo_fill.py (one per product group, ≤ 160 characters).

House rules kept: no screen-printing words, no "made by hand", no "available"/"Coming soon"
(meta text outlives launch), no donation claims for organic. Facts only from the product's own copy.
"""
import re

MAX_D, MAX_T = 160, 70
_PLACE = {}  # site name -> "Panama City Beach, Florida", filled from the Signature tees


def _c(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def colour(p):
    for t in p['tags']:
        if t.startswith('colour:'):
            return t.split(':', 1)[1].replace('-', ' ').title().replace('Of', 'of')
    return ''


def site_place(p):
    name = p['title'].split(' — ')[0].strip()
    m = re.search(r'^' + re.escape(name) + r'(?: cap)? — ([^·]+?) ·', _c(p['description']).replace('Dark line — ', ''))
    if not m:
        m = re.search(re.escape(name) + r'(?: cap)? — ([^·]+?) ·', _c(p['description']))
    if m:
        _PLACE.setdefault(name, m.group(1).strip())
    return name, _PLACE.get(name, '')


def fit(*options):
    for o in options:
        o = _c(o)
        if o and len(o) <= MAX_D:
            return o
    o = _c(options[-1])
    return o[:MAX_D - 1].rsplit(' ', 1)[0].rstrip(',;:') + '.'


ONE_OFF = {
    'the-mark-dark-cap': "The Mark brand cap: the Doolittle Scuba DS mark embroidered in white and red on a black Flexfit 6277 fitted cap, tagline across the back.",
    'the-seal-dark-cap': "The Seal brand cap: the round Doolittle Scuba seal embroidered on the front of a navy Flexfit 6277 fitted cap, DS mark on the side.",
    'the-stack-dark-cap': "The Stack brand cap: the stacked Doolittle Scuba lockup embroidered on a dark grey Flexfit 6277 fitted cap, DS mark on the side.",
    'the-wordmark-dark-cap': "The Wordmark brand cap: Doolittle Scuba in type, embroidered across a khaki Flexfit 6277 fitted cap, DS mark on the side.",
    'make-it-yours-tee': "Make it yours: any Doolittle Scuba design on any of fourteen tee colours, placed where you want it, with your own line or logo if you like.",
    'make-it-yours-cap': "Make it yours: a Flexfit 6277 fitted cap with your pick of front, side and back: a dive-site block, the DS mark, the seal, or your own line.",
    'the-mark-beanie': "The Mark beanie: the Doolittle Scuba DS mark embroidered in white and red on the cuff of an organic-cotton rib beanie in French Navy.",
    'the-mark-organic-cap': "The Mark organic cap: the DS mark embroidered on an Econscious organic cotton twill cap in black, one size, adjustable strap.",
    'the-seal-organic-cap': "The Seal organic cap: the round Doolittle Scuba seal embroidered on an Econscious organic cotton twill cap in black, adjustable strap.",
    'the-stack-organic-cap': "The Stack organic cap: the stacked Doolittle Scuba lockup embroidered on an Econscious organic cotton twill cap in black, adjustable.",
    'the-wordmark-organic-cap': "The Wordmark organic cap: Doolittle Scuba in type, embroidered on an Econscious organic cotton twill cap in black, adjustable strap.",
    'the-mark-organic-beanie': "The Mark organic beanie: the DS mark embroidered on a 100% organic cotton rib beanie, one size, in Black or Oxford Navy.",
    'embroidery-digitization': "One-time embroidery digitizing fee for a new custom design: your artwork or line of text is turned into stitches once and reused after.",
    'the-side-mark-cap': "The Side Mark cap: the plainest cap Doolittle Scuba makes, just the DS mark embroidered on the left side. Pick any cap colour.",
    'the-mark-cuffed-beanie': "The Mark cuffed beanie: the Doolittle Scuba DS mark, 1.5 in, embroidered on the folded cuff of a 12 in knit beanie. Five colours.",
    'the-mark-under-armour-dad-hat': "The Mark Under Armour dad hat: the DS mark embroidered on the front and DO A LITTLE SCUBA across the back. Thread matched to the hat.",
    'do-a-little-scuba-visor-embroidered': "Do A Little Scuba visor: a Flexfit visor embroidered with the DS mark and DO A LITTLE arced over SCUBA. Adjustable, for sun on the boat.",
    'the-mark-champion-packable-anorak': "The Mark anorak: a Champion packable quarter-zip with hood and kangaroo pocket, the Doolittle Scuba DS mark embroidered on the left chest.",
    'the-mark-basic-windbreaker': "The Mark windbreaker: a SOL'S lightweight windbreaker with the Doolittle Scuba DS mark embroidered on the left chest. Nothing else on it.",
    'doolittle-scuba-embroidered-under-armour-backpack': "Doolittle Scuba Under Armour backpack: the DS mark, DOOLITTLE SCUBA and the Do-A-Little Scuba tagline embroidered on the front.",
}


def describe(p):
    t, tags, h = p['title'], set(p['tags']), p['handle']
    d = _c(p['description'])
    col = colour(p)
    eco = bool(tags & {'organic', 'eco', 'organic-line'}) or ' organic ' in t
    dark = 'dark-line' in tags
    if h in ONE_OFF:
        return ONE_OFF[h]
    if 'series-custom' in ''.join(tags) or 'Make it yours' in t:
        line = t.split(' — ')[0]
        tone = 'dark' if 'dark tee' in t else 'light'
        return fit(f"Make it yours: any {line} design on any {tone} Comfort Colors 1717 tee. Pick the design, the colour and the size.")
    if 'pair' in tags:
        s, _ = site_place(p)
        kind = 'dark' if 'dark tee' in t else 'light'
        return fit(f"The {s} pair: the {s} Dive Site cap and the {s} Signature Series {kind} tee together, for $8 less than buying the two apart.")
    if 'rash-guard' in tags:
        s, place = site_place(p)
        cut = t.split(' · ')[-1].lower().replace("men's", "men's").replace("women's", "women's")
        ed = 'Signature Series Dark' if dark else 'Signature Series'
        w = f" from {place}" if place else ''
        return fit(f"{s} {ed} rash guard, {cut}: the {s} dive-site map{w} wraps the front, site name and GPS run down the sleeve.",
                   f"{s} {ed} rash guard, {cut}: the {s} dive-site map wraps the front, site name and GPS down the sleeve.")
    if 'site-cap' in tags:
        s, place = site_place(p)
        if eco:
            return fit(f"{s} Dive Site organic cap: the {s} site front embroidered on an Econscious organic cotton twill cap in {col}, adjustable strap.",
                       f"{s} Dive Site organic cap: the {s} site front embroidered on an Econscious organic cotton twill cap, adjustable strap.")
        return fit(f"{s} Dive Site cap: a {col.lower()} Flexfit 6277 fitted cap embroidered with the {s} site front, the DS mark and the Do - A - Little Scuba tagline.",
                   f"{s} Dive Site cap: a {col.lower()} Flexfit 6277 fitted cap embroidered with the {s} site front, DS mark and tagline.")
    if 'signature-series' in tags or 'signature-series-dark' in tags:
        s, place = site_place(p)
        w = f" at {place}" if place else ''
        if eco:
            return fit(f"{s} Signature Series organic tee: the dive-site map{w} on the back, site name and GPS on the chest. {col}, organic cotton.",
                       f"{s} Signature Series organic tee: the dive-site map on the back, site name and GPS on the chest. {col}, organic cotton.")
        ink = ' in white ink' if dark else ''
        return fit(f"{s} Signature Series tee: the dive-site map{w} on the back{ink}, site name and GPS on the chest. {col} Comfort Colors 1717.",
                   f"{s} Signature Series tee: the dive-site map on the back{ink}, site name and GPS on the chest. {col} Comfort Colors 1717.")
    if 'certified-ish' in tags or 'certified-ish-dark' in tags:
        cert = re.sub(r'^Certified-ish(?: Dark)? — ', '', t).replace(' organic tee', '').replace(' tee', '')
        if eco:
            return fit(f"Certified-ish {cert} organic tee: the {cert} card divers earn, redrawn with a wink, full back. {col}, organic cotton.",
                       f"Certified-ish {cert} organic tee: the {cert} card, redrawn with a wink, full back. {col}, organic cotton.")
        ink = 'in white ink on' if dark else 'on'
        return fit(f"Certified-ish {cert} tee: the {cert} card divers earn, redrawn with a wink, full back {ink} {col} Comfort Colors 1717.",
                   f"Certified-ish {cert} tee: the {cert} card, redrawn with a wink, full back {ink} {col} Comfort Colors.")
    if '1n73ll1g3nc3' in tags:
        name = re.sub(r'^1N73LL1G3NC3(?: Dark)? — ', '', t).replace(' organic tee', '').replace(' tee', '')
        blank = 'organic cotton' if eco else 'Comfort Colors 1717'
        return fit(f"1N73LL1G3NC3 {name} tee: a message hidden in a grid of characters; read the bold ones to find it. {col}, {blank}.",
                   f"1N73LL1G3NC3 {name} tee: a hidden message in a grid of characters; read the bold ones. {col}, {blank}.",
                   f"1N73LL1G3NC3 {name} tee: a hidden message; read the bold characters to find it. {col}.")
    if 'off-world-hunt-club' in tags or 'off-world-hunt-club-dark' in tags:
        name = re.sub(r'^Off-World Hunt Club(?: Dark)? — ', '', t).replace(' organic tee', '').replace(' tee', '')
        m = re.search(r'This one reads (.+?)\. (?:Full|Left|On|Front|Back)', d)
        line = m.group(1).strip() if m else ''
        blank = 'organic cotton' if eco else 'Comfort Colors 1717'
        return fit(f"Off-World Hunt Club {name} tee: a line in the hunters' script, translated: “{line}.” {col}, {blank}." if line else '',
                   f"Off-World Hunt Club {name} tee: “{line}.” A line in the hunters' script, translated. {col}." if line else '',
                   f"Off-World Hunt Club {name} tee: one line in the hunters' script, translated underneath. {col}, {blank}.")
    if 'aquatic-comic' in tags:
        head, _, rest = t.partition(' — ')
        name = rest.replace(' organic tee', '').replace(' tee', '')
        quotes = re.findall(r'“([^”]{3,90})”', d)
        q = quotes[0].strip() if quotes else ''
        blank = 'organic cotton' if eco else 'Comfort Colors 1717'
        head = head.replace(' Dark', '')
        return fit(f"{head} {name} tee: “{q}” on the chest, the rest of the joke on the back. {col}, {blank}." if q else '',
                   f"{head} {name} tee: “{q}” on the chest, the joke on the back. {col}." if q else '',
                   f"{head} {name} tee: a dive-deck one-liner on the chest, the rest of the joke on the back. {col}, {blank}.")
    if 'sticker-achievement' in tags:
        name = t.split(' — ')[0]
        m = re.search(r'Achievement Unlocked: [^.]+\. ([^.]+\.)', d)
        crit = m.group(1) if m else ''
        if 'set' in t.lower() and not crit:
            return fit("Achievement Unlocked: all twelve Doolittle Scuba achievement stickers, from Freshly Certified up, in waterproof die-cut vinyl.")
        return fit(f"{name} achievement sticker: {crit} Waterproof 3.5 × 1.2 in die-cut vinyl from the Achievement Unlocked set.",
                   f"{name} achievement sticker: {crit} Waterproof die-cut vinyl, Achievement Unlocked set.")
    if 'sticker-pack' in tags:
        name = t.split(' — ')[0]
        return fit(f"{name} sticker pack from Doolittle Scuba: three kiss-cut stickers plus fillers on one 4 × 6 in sheet, for the tank, dive box, laptop and logbook.",
                   f"{name} sticker pack: three kiss-cut stickers plus fillers on one 4 × 6 in sheet, for the tank, dive box, laptop and logbook.",
                   f"{name} sticker pack: three kiss-cut stickers plus fillers on one 4 × 6 in sheet.")
    if 'sticker' in tags:
        name = t.split(' — ')[0]
        return fit(f"{name} sticker from Doolittle Scuba, die-cut vinyl for the tank, the dive box or the laptop.")
    return None


def short_title(p):
    t = _c(p['seo']['title']) or _c(p['title'])
    if len(t) <= MAX_T:
        return None
    for a, b in [('Signature Series Dark rash guard', 'Signature Dark rash guard'), ('Signature Series rash guard', 'Signature rash guard'),
                 (' long sleeve', ' LS'), (' short sleeve', ' SS')]:
        t = t.replace(a, b)
        if len(t) <= MAX_T:
            return t
    return t[:MAX_T]


def plan(p):
    out = {'id': p['id'], 'handle': p['handle']}
    if not _c(p['seo']['description']):
        d = describe(p)
        if d:
            out['description'] = d
    st = short_title(p)
    if st:
        out['title'] = st
    return out if len(out) > 2 else None


def prime(products):
    """Fill the site -> place map from every product before planning."""
    for p in products:
        if 'signature-series' in p['tags'] or 'signature-series-dark' in p['tags'] or 'site-cap' in p['tags']:
            site_place(p)
