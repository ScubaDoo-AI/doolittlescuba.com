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

## Shop: new home-page hero (17:23–18:20 ET) — live
Eric: *"Push the new home page hero … test on a copy of the live theme first. Send me desktop and mobile screenshots before publishing."* Per Design's `Branding\Webpage\Hero\HERO_PUSH_HANDOFF.md`.

- **Files:** `DS_hero_B_bluewater_desktop_2400x1200.jpg` (2400×1200) and `DS_hero_B_bluewater_mobile_1080x1350.jpg` (1080×1350) uploaded to Shopify Files (staged upload → `fileCreate`). Shopify appended a suffix to both names on the CDN, so the theme references are `DS_hero_B_bluewater_desktop_2400x1200_6668c5ae-b65c-441b-9eb0-963aca42f7d7.jpg` and `DS_hero_B_bluewater_mobile_1080x1350_3795946c-edf8-4f49-9ba9-7ad65937fd2b.jpg`. `GOPR0150_Copy_Copy.jpg` is still in Files for rollback.
- **Theme copy:** "Deck + Pairs tab — hero B bluewater (test 21 Nov)" (`OnlineStoreTheme/161866514618`), duplicated from the live "Doolittle Scuba — Deck + Pairs tab". In `templates/index.json` section `hero_jVaWmY`: `image_1` → desktop file, `custom_mobile_media` → true, `media_type_1_mobile` = image, `image_1_mobile` → mobile file; `overlay_color` `#0C182973` (45%) → `#0C182940` (25%, Eric's pick from the side-by-side); `brand_overlay` custom liquid: arc width `clamp(340px,46vw,700px)` → `clamp(340px,38vw,580px)` (both occurrences, incl. the padding calc) so the arc clears the divers at every width — at 1440 the old width put the end of LITTLE on Eric's fin (the raised hand was already clear). Saved as one version.
- **Checked at 1440 / 390:** arc and headline in the open water top-left (desktop) / top-centre (mobile); sub-text on water; button bottom-right on water (desktop); mobile button over the right diver's legs, legible.
- **Re-centred (17:45–17:55 ET).** Eric: *"These images are poorly centered on us."* The hero box is wider than the 2:1 photo, so the theme cropped top and bottom and lost the heads. Fix in the `brand_overlay` CSS: `@media (min-width:750px){.hero:has([data-ds-overlay]) .hero__media{object-position:50% 0}}` — the desktop photo is pinned to its top edge, so the faces stay in frame at any screen height and short screens trim the fins instead (the hero is 80svh minus the header on desktop, so a 1080p monitor shows nearly the whole photo). `text_sub` `max_width` normal → narrow so the paragraph wraps in three lines on the water instead of across Eric's arm. Mobile unchanged (portrait photo nearly full-frame; paragraph and button sit over the divers' lower halves — Eric can ask to move them up). Second saved version.
- **Published 18:17 ET** (Eric: "The word"). The theme tools refuse to publish a theme they didn't create, and `themePublish` is blocked in the API, so it was published from Shopify admin in the browser pane (Online Store → Themes → Publish → confirm). Confirmed `MAIN` by API; storefront re-checked. The previous live theme "Doolittle Scuba — Deck + Pairs tab" stays in the store, unpublished, for rollback. Store still password-locked.

## Shop: pairs turn 360 (18:40 ET)
Eric: *"Let's see shirt and hat bundles also rotate 360."*

- **Pictures:** `tools/pairs_pf.py --views` builds a side and a back for every pair, in the same layout as the front: the tee side with the cap's left side, and the tee back with the cap back. That is 56 files, `img/pairs/<slug>-<line>-side.jpg` / `-back.jpg`. They are added to all 28 pair products as pictures 2 and 3.
- **Deck theme (live: "Deck + Pairs tab — hero B bluewater (test 21 Nov)"):** cards tagged `pair` with three pictures turn front → side → back (`n3`, 10.5 s). Every other card keeps its two-view turn. With reduced motion, the card stays on the front. Saved to the live theme; this waits on a publish.

## Cart on the site (built, behind the launch switch)
Eric: *"Cart on the site."* Browse and add to cart on DoolittleScuba.com; pay at Shopify's checkout on shop.doolittlescuba.com.

- **Product map:** `tools/catalog_map.py` reads every product through the Headless storefront (public token) and writes `js/catalog.json` (SKU stem → sizes/colours, variant ids, prices, sold-out). It stamps `data-buy` on the product cards: home 61, Signature 28, Certified-ish 40, Off-World 60, 1N73 36, Surface Interval 20, Organic 203, Stickers 50. Not linked: Make it yours, Home Port, personalized Surface Interval tees, single dark sticker variants. Actions **catalog-map** refreshes it daily (13:17 UTC) and commits if anything changed.
- **Cart (`js/cart.js`, on 23 pages):** an opened deck card gets size/colour buttons, the price and *Add to cart* (sold-out sizes struck through). *Add the pair* opens a cap size + tee size picker on the same card. Cards outside a deck (stickers, jackets, beanie) get a small *Add to cart* row. A red *Cart · n* button opens the drawer: quantities, remove, Shopify's automatic discounts (tee + cap: −$8 checked), total, *Checkout*. Links to the shop's cart or product pages open the drawer / picker on the site instead. A remembered partner `?src=` rides along as a cart attribute and on the checkout link.
- **Launch switch:** `LIVE=false`. Visitors still see *Coming soon*. Preview in any browser with `?cart=preview` (remembered; `?cart=off` ends it). At launch: set `LIVE=true` (and the store password comes off).
- **Tested (headless Chrome, desktop and phone):** Signature tee, cap, pair, sticker; drawer; checkout link goes to shop.doolittlescuba.com. No page errors.

## Three views on every card (18:45–20:00 ET)
Eric: *"All cards or products should have at least 3 images with 3 placement design."*

- **Shop audit (569 active products):** every tee (Signature, Certified-ish, Off-World, 1N73, Surface Interval, organic) already had front, back and side. Missing views were on the 18 caps and 18 organic caps (front and back only), the anorak (no side or back), the beanies, the two Make it yours products and The Side Mark (no front).
- **Printful renders:** `printful_read.py` gained two mockup modes.
  - `plainside` puts a 0.03 in dot on the left so Printful draws a cap side with no embroidery (The Mark, organic Mark and Stack).
  - `?g=<style>&o=<views>` asks for Printful's extra camera views. The anorak gets left side and back (Ghost style), the windbreaker its back, and The Side Mark its plain front.
  - The read workflow now installs pillow and numpy, so the organic plans load.
- **Shop pictures added:**
  - A side view on all 36 caps, from the site files, plus the 3 new plain sides.
  - Anorak side and back in black and navy.
  - The Side Mark's plain front.
  - A close-up of the cuff mark on both beanies.
  - Make it yours tee: an example front, side and back (Black Bart on light blue).
  - Make it yours cap: another session added navy and khaki views at the same time, so I removed my three duplicates.
- **Site:**
  - The Mark cap, the organic Mark and Stack caps, and the anorak now have a side view.
  - The windbreaker turns worn → close-up → back; Printful has no side camera for it.
  - The Side Mark turns front → side → back.
  - The six home-page line covers now use the HD front, side and back sets.
  - The beanies get the cuff close-up.
  - Live check: 30 of 69 cards on the home page and 241 of 242 on /organic/ have all three. The rest are stickers and the beanie.
- **Shop deck theme:** each card picks its front, side and back by the image alt text (front, side, then close-up, then back), so the photo order no longer matters, and turns through all three (`n3`). Saved to the live theme; this waits on a publish.
- **Not possible as three views:**
  - Stickers (52 products) are flat prints with one picture each.
  - The Mark beanie (Stanley/Stella) has only a front camera at Printful, so it shows front + close-up.
