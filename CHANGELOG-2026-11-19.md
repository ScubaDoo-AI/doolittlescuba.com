# Changelog — 19 Nov 2026

## The pulled card turns its garment in 3-D (all apparel decks)
Eric (iPad screenshot of the collections deck, the grey box round the 1N73LL1G3NC3 mockup marked, "rotating"): *"Can we make the shirts rotating 3-D model in the scrolling setup we have for all apparel?"* Then: *"Look at Printful models and Shopify, they appear better."*

- **Turn:** the card pulled forward in a deck (collections, shirts, caps, organic) shows the front, turns, holds on the back, turns back: an 8 s loop (`@keyframes dkturn`), starting 0.6 s after the card is pulled so running across the tabs doesn't flicker. The second face is a 600 px thumb (Shopify CDN `&width=600`, local `-t` file) loaded only when the card is first pulled. A card with one image sways ±18°. Sticker packs stay still (`spin:false`). Reduced motion: no turn.
- **No grey box:** `.dk-pic` lost its `#E6ECEE` fill; the Printful mockups are transparent, so the shirt sits on the card with a faint spotlight.
- **Collections deck:** each collection card now has a back face (`data-back`); the organic card uses the Printful Thistlegorm organic dark mockup from Shopify instead of the old render.
- Code: `js/deck.js` (`thumbOf`, `spinPic`, `wake`), `css/site.css` (`.dk-spin`, `.fc`). Checked by script at 1440 px, light and dark, home page and `/signature/`; no console errors.

## Still on the old renders (spin as a light tile until moved)
Certified-ish (light, dark, organic), Off-World Hunt Club, Surface Interval, caps and beanie: the same old renders in Shopify and on the site. Next: Printful read `mockup:` runs for those lines, `fileUpdate` in Shopify, site links to the CDN copies, as was done for Signature and 1N73LL1G3NC3 on 18 Nov.
