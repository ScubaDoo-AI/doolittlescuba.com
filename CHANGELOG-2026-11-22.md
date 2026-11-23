# Changelog — 22 Nov 2026

## Cart: items with nothing on sale keep "Coming soon" (Eric: "stickers outside of the uv achievements should be left as coming soon")
- The 37 Sticker Mule packs were set unsellable in Shopify this morning (stock tracked at 0, Deny). Before this change, with `LIVE=true` the cart would have put a disabled **Sold out** button on each pack and removed its *Coming soon · get launch news* button.
- `js/cart.js`: `widget()` now returns whether any variant is on sale. When none is, the card is left exactly as it was: no picker, the launch-news button stays (deck cards), the pill is not turned into "Ready to order" (loose cards). Items with stock are unchanged.
- Side effect: a product sold out in every size also stays on *Coming soon* rather than showing *Sold out*.
- `cart.js?v=` bumped to `b81e8afc` on the 23 pages that load it.
- Tested headless (Chrome, 1440 px, `?cart=preview`, catalog with the packs at 0): opened Reef Cuties pack → no picker, launch-news kept; Black Bart cap → *Add to cart*; the 12 achievement singles → *Add to cart*, "Ready to order"; no page errors.
- `js/catalog.json` still shows the packs in stock (built 13:17 UTC, before the stock change); the catalog-map run after this commit refreshes it.

## Banner updated (Eric 11:57 "Update banner", 12:03 "2")
- Status flag id `2026-11-22-stickers-ready` (re-shows to anyone who dismissed the 16 Nov one), state still **Proofing**, dated 22 Nov: the Achievement Unlocked UV stickers (full set + 12 single badges) are in stock and ready on day one; last samples due Nov 26–28; everything else stays "Coming soon". Link unchanged. Applied with `tools/status_flag.py` on all 26 pages.

## Water Hazard towels on the site (evening)
- New page **/towels/**: the twelve Water Hazard golf towels (WH01–WH12) in two sets of six, $28, each card with the Printful mockup and an *Artwork* flip, a link to its product in the shop, and the towel's specs (16 × 24 in, 80/20 poly/polyamide, sublimated front, brass grommet and clip, printed to order). Built by `tools/towels_page.py` from the stickers page shell; images in `img/towels/`, OG image `img/og/towels.jpg`.
- Cards carry `data-sku` = the Printful variant SKU, so `tools/catalog_map.py` (towels page added to its PAGES) stamps `data-buy` and the cart can add them: 12 of 12 linked. The twelve products were also published to the Headless storefront channel so the catalog map can see them.
- "Towels" added to the nav on every page (and to `tools/line_pages.py`), to `tools/status_flag.py` / `tools/wide_screen.py` page lists, and to `sitemap.xml`.

## Jackets without models (Eric 21:29 "Rerender the jackets however remove the models")
- The four jacket cards on the home page now show Printful's flat mockups (no people): Front = `<jacket>-<colour>-flat.webp`, Close-up = a new 1200 px crop of the embroidered mark from the flat mockup (`-closeup.webp`), and the anorak keeps its plain back view. The worn (`-model`, `-men`, `-women`) and model close-up (`-detail`) shots are no longer used on the site; the files stay in `img/jackets/`.
- The Shopify product images for both jackets were changed the same way (see the store record).

## "Don't call them golf towels" (Eric 21:32)
- Shopify: the twelve products are now "<Design> — Water Hazard Towel", handles `<design>-water-hazard-towel` (Shopify redirects the old `-golf-towel` handles; Today's Departures is now `todays-departures-water-hazard-towel`), product type "Towel", SEO titles and descriptions without "golf", descriptions say "for the boat rail or BC" and "hang towels for the dive boat". Collection description likewise. Shop deck tab renamed "Towels".
- Site: /towels/ copy has no golf in it (new headline "Hang one on the boat rail."), card lines rewritten from the product copy, shop links on the new handles, catalog map rebuilt.

## Complete mockups (Eric 21:36 "Make all mockups complete")
- Windbreaker: Printful flat-back mockups generated (Black, Navy) → `img/jackets/basic-windbreaker-<colour>-flat-back.webp`. Every jacket card now has Front / Back / Close-up (anorak back = its plain back view), all without models.
- Shopify: the windbreaker now carries Printful's flat front and flat back per colour (Printful's mockup step pushed these four itself, replacing the earlier flats) plus the embroidery close-ups, in the order front, close-up, back per colour; variant images = the flat fronts. The six set-one Water Hazard towels gained the back mockup (the plain white back with grommet and ring, the same Printful back image set two has), so all twelve towels have front + back.
- Theme published 22 Nov 21:46 (Eric: "Yes"): Towels tab live in the shop deck (home + collection pages); shopify-theme/snippets/ds-deck-cards.liquid mirrors the live snippet.


## Custom shirt per series, light and dark (Eric 21:54)
- Ten new shop products, one Light and one Dark per series (Signature, Certified-ish, Off-World Hunt Club, 1N73LL1G3NC3, Surface Interval · Boat Banter): any design of the series on any of 17 light / 18 dark Comfort Colors 1717 colours, the series price + $5. Picker with a live shirt preview on the product page; paid orders become Printful drafts through the custom-orders job. Details: `CUSTOM-ORDERS.md` → "Series custom tees"; code `tools/series_custom.py`.
- Site: each series page's "Wear it your way" gains an **Any design, any colour** card with Light shirt / Dark shirt buttons to the shop (`tools/line_pages.py` `series_custom_card`).
- Picker art: 240 previews in `img/custom-series/`; product images in `img/custom-series/product/`.

## Custom shirts at the end of the stacks (Eric 22:57)
- Shop deck (`snippets/ds-deck-cards.liquid`): series custom shirts are dealt in their own last passes — light, then dark — after every catalog card, and the tab's card limit never cuts them.
- `sections/ds-deck.liquid`: each tab paginates its collection by 250. Shopify gives a section only the first 50 products of a collection, and Signature Series has 58 with the hidden organic editions, so the custom shirts (the newest) were missing from the home page tab.
- Saved in the live theme; waiting for Eric's go-ahead to publish (with the series custom picker).

## Custom shirt renders at true scale (Eric 23:04 "Designs look oversized in all these renders")
- The picker preview and the ten product images drew the 12 × 16 in print area across nearly the whole drawn shirt. Now at shirt proportions (≈14 px per inch on the 600 px drawing: art box 170 × 227 at x 215, y 122 back / 132 front). Product images re-rendered as `img/custom-series/product/<ser>-<l|d>-2.jpg` and swapped in Shopify.
