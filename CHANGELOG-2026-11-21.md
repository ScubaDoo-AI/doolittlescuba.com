# Changelog — 21 Nov 2026

## Side view on every shirt
Eric: *"3d rotation is missing some hat side embroidery and the shirts are missing the side view, not all."*

- **Shirts:** the deck's turn now has a side view on Off-World Hunt Club (60, light and dark), Surface Interval (59: Boat Banter and the 39 personalized family tees) and their organic editions (119). They have no sleeve print, so the side shows the plain sleeve; it comes from Printful's own "right" mockup of the same runs as the front and back (runs #31, #32, #34, #35), saved to `img/sleeves/ow/`, `img/sleeves/si/` and `img/organic/<line>/<name>-sleeve.webp`. Every shirt card on the site now turns front → side → back. Safeguard recaptured.
- **Caps (Eric's answer):** no side DS mark on caps whose design already carries the mark (The Mark, The Stack): their plain sides are right. **The Stack gets the back tagline**: `printful_caps.py` STK back = True (cost $19.46, price $36, like The Mark); linked at Printful (Printful link run 44923525768, 2/2, on the recoloured Dark Grey plan). **Open for the recolour session:** the organic Stack (DS-STK-CO) inherits the back from the same plan but its link failed (run 44923627657: `KeyError: 'Khaki'` in `organic.py` cap colours, a new colour from the recolour), and the Stack mockups (site + Shopify) still show front only; the recolour re-render covers both. **New product requested:** a plain cap with only the DS mark on the side, any colour, optional *Do A Little Scuba* back.

## New cap: The Side Mark
Eric: *"a cap that is plain with just the DS mark on the side, make it custom to any color selectable and optional Do A Little Scuba tag line on the back."* Price: **$32 plain, $36 with the back.**

- **Shopify:** `the-side-mark-cap` (active, on all six channels; picked up by the `hats`, `brand-caps` and `pair-discount-caps` collections from its tags). Options: Colour (10: Black, Dark Navy, Dark Grey, Grey, White, Khaki, Olive, Multicam Green, Royal Blue, Red) × Size (S/M, L/XL) × Back (Plain / Do A Little Scuba) = 40 variants, SKUs `DS-SDM-<COLOUR>-<SM|LXL>[-B]`. Each variant shows its own colour: the side view for plain, the back view for the tagline option (20 Printful mockups, read run below).
- **Printful:** plan in `tools/printful_sidemark.py` (Flexfit 6277; DS mark on the left side; thread white/red, navy/red on White/Khaki/Grey, white/navy on Red; same rules as the recoloured caps). `printful_link.py` gained the `sidemark` line (and the workflow option); link run: 40/40 linked.
- **Site:** new card after The Stack in the caps deck (shown in Black, turns side → back), linking straight to the shop product to pick a colour. No "Make it yours" link: the custom builder has no plain-front option.

## Make it yours: every cap colour
Eric: *"make it yours items should allow for color changes as well."*

- **Builder (`/custom/`):** caps now offer all ten Flexfit 6277 colours. The five dark ones were there already; Grey, White, Khaki, Red and Multicam green are new. On light caps the preview stitches in navy, the way they are made.
- **Orders (`tools/custom_cap.py`):** takes the new colours.
  - On White, Khaki and Grey, every front, the side mark and the tagline switch to their navy-thread files, and a customer's own line is stitched in navy.
  - On Red, the DS-mark art uses the navy-S file.
  - Twenty new stitch files are in `renders/caps/`, made with `tools/caps_light_threads.py`. They cover every site front without one yet, The Mark, The Seal and The Stack (light versions), and The Mark, The Seal, The Stack and The Wordmark (red-cap versions).
- **The Side Mark card** now has a *Make it yours* link (plain front, DS mark left, tagline back) next to *Pick your colour*.
- **Fixed:** the builder's script had been failing since 19 Nov because of an unescaped apostrophe in the mockup note ("Eric's drawing"). The colour, design and cart steps did not load until this fix.

## Caps recoloured (Eric: "want the caps themselves recoloured", "go", "No camo")
One colour per cap, chosen between its light and dark tee, at most two site caps per colour (was 5 colours, now 10). All Flexfit 6277, every colour US in stock at Printful (catalog API 21 Nov).

| Cap | Was | Now |
|---|---|---|
| Black Bart | Dark grey | Navy |
| Bridge Span 14 | Olive | Royal blue |
| Blue Grotto | Royal blue | Grey |
| Rainbow River | Black | Olive |
| Thurmond Dam | Navy | Khaki |
| Dampier Strait | Navy | Red |
| Bali | Navy | Khaki |
| Somosomo Strait | Olive | White |
| Vuna Reef | Olive | Grey |
| The Seal | Black | Navy |
| The Stack | Black | Dark grey |
| The Wordmark | Black | Khaki |
| The Thistlegorm | Dark grey | Dark grey (Multicam tried, dropped: "No camo") |

Unchanged: Blue Water Park (Black), Navy LLCAT (Navy), Dive Land Park (Dark grey), Rainbow Reef (Olive), The Mark (Black), Home Port (Black).

- **Thread on light and red caps:** `tools/caps_light_threads.py` makes the stitch files. White, Khaki and Grey caps stitch 1966 Navy where they stitched white; the flag keeps its white centre inside a navy outline. The red cap's side mark has a navy S. Files in `renders/caps/` (served by the site). Each new stitch file is a new design at Printful: expect its digitization fee on the first order of each.
- **Printful:** `printful_caps.py` (new `assemble()`, colour per cap, thread overrides) linked: runs 44923750947 (26 variants), 44924581454 (Thistlegorm), 0 failed. Organic caps keep their own EC7000 colours (`organic.py` CAP_COLOUR, white thread); the organic Stack linked with its back (run 44924652831).
- **Mockups:** Printful read runs 44923307609 + the Thistlegorm/Stack/organic Stack run; `img/hats/pf/` (13 caps, front/side/back), `img/organic/caps/cap-the-stack-*`.
- **Site:** hats deck colours, swatches, captions, alt text, Make it yours links (four stale colour links fixed: brown, purple, maroon, spruce). Make it yours still offers the dark cap colours only, so links from light, red caps open on the nearest dark one.
- **Pairs:** 18 pair images rebuilt on Printful's mockups (`tools/pairs_pf.py`, new), `pairs.py` cap colours.
- **Shopify:** 12 caps (descriptions, `colour:` tags, front/back images in place), 18 pairs (descriptions, images), organic Stack images. Price & stock watch afterwards: no price change, nothing sold out.
