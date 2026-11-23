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

## Water Hazard golf towels on the site (evening)
- New page **/towels/**: the twelve Water Hazard golf towels (WH01–WH12) in two sets of six, $28, each card with the Printful mockup and an *Artwork* flip, a link to its product in the shop, and the towel's specs (16 × 24 in, 80/20 poly/polyamide, sublimated front, brass grommet and clip, printed to order). Built by `tools/towels_page.py` from the stickers page shell; images in `img/towels/`, OG image `img/og/towels.jpg`.
- Cards carry `data-sku` = the Printful variant SKU, so `tools/catalog_map.py` (towels page added to its PAGES) stamps `data-buy` and the cart can add them: 12 of 12 linked. The twelve products were also published to the Headless storefront channel so the catalog map can see them.
- "Towels" added to the nav on every page (and to `tools/line_pages.py`), to `tools/status_flag.py` / `tools/wide_screen.py` page lists, and to `sitemap.xml`.
