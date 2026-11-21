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

## Certified-ish dark: no more orange and brown (Eric 11:44 "Not a fan of the orange and brown", 11:59 "go")
11 of the 20 dark tees were Yam (6) or Espresso (5). All moved to Comfort Colors 1717 colours in US stock at Printful in every size (catalog API 21 Nov); white ink unchanged.

| Tee | Was | Now |
|---|---|---|
| Altitude | Yam | Mystic Blue |
| Boat | Yam | True Navy |
| Buoyancy | Yam | Blue Spruce |
| Drift | Yam | Midnight |
| Fish ID | Yam | Emerald |
| Underwater Photographer | Yam | Black |
| Cave | Espresso | Graphite |
| Deep | Espresso | True Navy |
| Ice | Espresso | Denim |
| Night | Espresso | Black |
| Search and Recovery | Espresso | Hemp |

- **Printful:** `printful_certifiedish.py` (colours + variant ids); link run 44927750902, 66 variants, 0 failed. Mockups: read run 44928564468 (front, back, right sleeve).
- **Organic twins unchanged** (still Khaki): `organic.py` PIN keeps them off the regular colour.
- **Shopify:** 11 products: descriptions, `colour:` tags, back/front images replaced in place.
- **Shop theme (live, Doolittle Scuba — Deck):** `ds-deck-cards.liquid` spine colours for Mystic Blue and Hemp; `ds-organic-map.json` (cart converter) shows the new regular colours.
- **Site:** `certified-ish/` dark cards (colour, swatch, captions, Shopify image versions, sleeves), organic notes ("Mystic Blue → Khaki" …), Make it yours gains Mystic blue and Hemp (`custom/`, `custom_tee.py`), `certdark.py` data so a rebuild keeps them. Safeguard recaptured.
- Price & stock watch afterwards: no change for Certified-ish; open items are the Side Mark cap prices (another session) and the sticker packs' stock tracking.

## Shop: pairs off the cap lineup, on their own tab
Eric: *"Remove bundles from the cap lineup and place under its own tab."*

- **Hats collection:** its rule (tagged `cap`) now also excludes anything tagged `pair`. It went from 86 products to 58, all caps. The 28 cap-and-tee pairs stay in the **Pairs** collection.
- **Deck theme ("Doolittle Scuba — Deck", live):** a new **Cap & tee pairs** tab right after Caps & beanies, on the home page and on collection pages (and in the section's default tab list). The change is saved to the theme and goes in front of visitors when the theme is published.

## Shop: new home-page hero (17:23–17:32 ET) — on a theme copy, not published
Eric: *"Push the new home page hero … test on a copy of the live theme first. Send me desktop and mobile screenshots before publishing."* Per Design's `Branding\Webpage\Hero\HERO_PUSH_HANDOFF.md`.

- **Files:** `DS_hero_B_bluewater_desktop_2400x1200.jpg` (2400×1200) and `DS_hero_B_bluewater_mobile_1080x1350.jpg` (1080×1350) uploaded to Shopify Files (staged upload → `fileCreate`). Shopify appended a suffix to both names on the CDN, so the theme references are `DS_hero_B_bluewater_desktop_2400x1200_6668c5ae-b65c-441b-9eb0-963aca42f7d7.jpg` and `DS_hero_B_bluewater_mobile_1080x1350_3795946c-edf8-4f49-9ba9-7ad65937fd2b.jpg`. `GOPR0150_Copy_Copy.jpg` is still in Files for rollback.
- **Theme copy:** "Deck + Pairs tab — hero B bluewater (test 21 Nov)" (`OnlineStoreTheme/161866514618`), duplicated from the live "Doolittle Scuba — Deck + Pairs tab". In `templates/index.json` section `hero_jVaWmY`: `image_1` → desktop file, `custom_mobile_media` → true, `media_type_1_mobile` = image, `image_1_mobile` → mobile file; `overlay_color` `#0C182973` (45%) → `#0C182940` (25%, Eric's pick from the side-by-side); `brand_overlay` custom liquid: arc width `clamp(340px,46vw,700px)` → `clamp(340px,38vw,580px)` (both occurrences, incl. the padding calc) so the arc clears the divers at every width — at 1440 the old width put the end of LITTLE on Eric's fin (the raised hand was already clear). Saved as one version.
- **Checked at 1440 / 390:** arc and headline in the open water top-left (desktop) / top-centre (mobile); sub-text on water; button bottom-right on water (desktop); mobile button over the right diver's legs, legible.
- **Not published.** Eric: "Not yet." Publish = `theme_publish` on the copy; the current live theme stays in the store unpublished. Anything changed on the live theme after 17:25 today is not in the copy.
