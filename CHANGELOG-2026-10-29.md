# DoolittleScuba.com — update of 2026-10-29

## Added — The stickers
- **Home, new section `#stickers`** (after the hats) and a **Stickers** link in the nav. 26 cards, all "Coming soon":
  - **Achievement Unlocked** — 12 stickers, 3.5 × 1.2 in, $4 each, plus the **Full Set** (all twelve on one 8.5 × 11 in kiss-cut sheet) at $15.
  - **Classic die-cuts** — 13 stickers, about 3 in on the long side, $5: Freshly Certified, Level Up, Not On My Watch, Master Diver (octopus), Master Diver (chess king), Deep Diver, Drift Diver, Perfect Buoyancy, Warm & Dry-ish, Spicy Air, Sidemount Turtle, ID Fish eye chart, Altitude Diver.
- Images in `img/stickers/` (`<slug>.webp` 1200 px and `<slug>-t.webp` 600 px, sticker on warm paper). Cards open in the existing shirt lightbox (`sk-grid` added to its grid list).
- Matching Shopify drafts: 26 products (type Sticker, tags `sticker`, `sticker-achievement` / `sticker-die-cut`, `coming-soon`, `cert:<code>`), SKUs `DS-STK-A-<code>`, `DS-STK-D-<code>`, `DS-STK-A-SET12`; collections **Stickers**, **Achievement Unlocked**, **Die-cut Stickers**. Handles match the image slugs (e.g. `achievement-high-score`, `sticker-deep-diver`).
- Cache-busting stamps refreshed (`tools/bust.py`).
