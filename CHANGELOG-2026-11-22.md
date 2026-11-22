# Changelog — 22 Nov 2026

## Cart: items with nothing on sale keep "Coming soon" (Eric: "stickers outside of the uv achievements should be left as coming soon")
- The 37 Sticker Mule packs were set unsellable in Shopify this morning (stock tracked at 0, Deny). Before this change, with `LIVE=true` the cart would have put a disabled **Sold out** button on each pack and removed its *Coming soon · get launch news* button.
- `js/cart.js`: `widget()` now returns whether any variant is on sale. When none is, the card is left exactly as it was: no picker, the launch-news button stays (deck cards), the pill is not turned into "Ready to order" (loose cards). Items with stock are unchanged.
- Side effect: a product sold out in every size also stays on *Coming soon* rather than showing *Sold out*.
- `cart.js?v=` bumped to `b81e8afc` on the 23 pages that load it.
- Tested headless (Chrome, 1440 px, `?cart=preview`, catalog with the packs at 0): opened Reef Cuties pack → no picker, launch-news kept; Black Bart cap → *Add to cart*; the 12 achievement singles → *Add to cart*, "Ready to order"; no page errors.
- `js/catalog.json` still shows the packs in stock (built 13:17 UTC, before the stock change); the catalog-map run after this commit refreshes it.
