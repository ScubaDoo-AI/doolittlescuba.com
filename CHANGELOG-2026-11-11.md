# Change log — 11 November 2026

## Caps: embroidered site fronts in the store, 12 caps on Printful

Eric, 11 Nov (caps Project): *"Let's add the 14 front signature series shirt designs to the caps embroidery."* then here: *"Build the printful and Shopify embroidered caps."*

### Store — 19 cap products
- New front + back mockups on all 19 Dark caps: the site front (torn-edge dive flag over the site name and coordinates) embroidered, the DS mark on the side, "DO - A - LITTLE" arched over SCUBA on the back. The Mark's side and The Stack's side and back are plain, as the listings say. Old media deleted.
- Site-cap descriptions rewritten for the embroidered front (threads named per flag); tags `front:embroidered` + `site-cap` (brand caps `brand-cap`); the Site Caps and Brand Caps collections re-keyed on those tags (15 / 4). Prices unchanged. Home Port stays custom (`fulfil:custom`).

### Printful — 12 caps linked, 0 failures
- `tools/printful_caps.py` (new) plans the 12 caps whose Flexfit 6277 colour Printful stocks (Dark Navy, Dark Grey, Black, Olive); `tools/printful_link.py` gained the `caps` line and sends item-level options (thread colours, flat embroidery); the Printful link workflow lists `caps`.
- `tools/check_connections.py` now reads the 6277's printfile templates: front 5.90 × 2.00 in, side and back 2.00 × 1.00 in. The print masters in Shopify Files were built to those sizes — which forced a 0.92 × 1.00 in side mark and a straight two-line back on the Printful caps only. Sample before publishing.
- The renders live on the branch `caps-embroidered-2026-11-11` under `renders/caps-2026-11-11/` (the store imported them from there). The home page's `img/hats/dark/` and hats copy are still the 24 Oct DTF-style set — a separate pass.

Full ids, file names and the compromises: `SHOPIFY-STORE.md`, 2026-11-11.

## Evening — Eric's answers: sample staged, DTF option gone, coordinates corrected, merged
- **Price** stays $35 / $40. **Printful sample** staged as draft order 186447389 (Blue Water Park, Black, L/XL): $22.41 + $5.09 shipping + $12.40 one-time digitization + $3.21 tax = $43.11, unconfirmed. The Sample order job now takes the caps and has a `show` mode.
- **No more DTF caps:** `tools/hats_v3.py` put the embroidered-front renders in the home page deck and rewrote the hats copy and spec sheet; Home Port is embroidered to order (store tags and description updated).
- **Coordinates:** seven sites' website and store values were brought up to the chest blocks, which checked out against the ground; Dive Land Park moves from "Ider" to Glencoe, AL. 28 store descriptions and the site's own data, guides and plates updated.
- **Merged to main** (126d842), live. Open: the Navy LLCAT front reads "Hovercraft (LLCAT)".

Full ids and details: `SHOPIFY-STORE.md`, 11 Nov evening.

## Late — the decks roll properly on every screen

Eric: *"Stickers scroll extremely too fast and caps and shirts don't rolling scroll only click to pull forward."*

The cause: the deck mapped its **whole scroll range** onto the cards. A deck that barely overflowed the screen (the 26 themed packs on a tablet or a 1100 px desktop) flipped through all 26 within a few pixels of scroll, while a deck that fit the screen (hats, shirts) never scrolled, so a finger could not roll it at all — only a tap pulled a card forward. On desktop, hovering also jumped several cards at a time because the lifted card covered its neighbours' tabs. And on desktop the 30-card Off-World lines overflowed with no scrollbar, so the last ten were unreachable with a mouse.

`js/deck.js`, one change of model:
- **Tabs fit the width.** A line keeps its own tab width when the whole deck fits; when narrower tabs would make it fit (down to 26 px) it uses those — Off-World's 30 now sit at 28 px on a desktop, all reachable; the packs at 33 px. Only when even that overflows (phones) does the deck scroll, and then at no less than **48 px of scroll per card** so a swipe rolls at a readable pace. Re-fitted on resize.
- **Rolling is geometric.** On a deck that fits, the card under the pointer's x pulls forward — the mouse running across the tabs, or a finger dragged across them (`touch-action: pan-y`, so vertical swipes still scroll the page) — one card per tab, no jumps, in order. On a deck that scrolls, the card whose body is in the middle of the screen steps forward, one card per tab width.
- Hints say which: *run across the tabs* (mouse), *drag a finger across the tabs* (touch, fitted), *swipe the deck* (touch, scrolling).

Checked by script at 1440, iPad landscape (finger drag rolls the hats 14→0 and the packs 25→0 one by one) and iPhone (56 px per cap, 48 px per pack). No visual change to the cards themselves beyond narrower tabs where a deck now fits.

### Later — the phone deck no longer bounces

Eric: *"Sticker scroll bounces back to screen centered item can not see last couple of designs."*

On a phone the deck still relied on the browser's own momentum scrolling, and the cards change layout as they step (the lifted card, its tag) — Safari answers that by snapping the scroll position back, so the end of the deck could never be reached. Native scrolling is gone from the decks now. A deck that cannot fit the screen is a **drag-rolled strip**: a finger (or a mouse, on a narrow window) dragged across it rolls the cards one per 48 px of travel, a flick carries on a little further, and the strip slides to keep the pulled card in the middle of the screen — so the last card is reached by construction. Vertical swipes still scroll the page; a tap on a tab pulls it forward and centres it; a tap on the pulled card opens it. Decks that fit the screen are unchanged (the card under the pointer or finger). Checked at iPhone width by script: 26 packs rolled end to end in three flicks, the hats likewise.
