# DoolittleScuba.com — update of 2026-10-29

## Added — The stickers
- **Home, new section `#stickers`** (after the hats) and a **Stickers** link in the nav. 26 cards, all "Coming soon":
  - **Achievement Unlocked** — 12 stickers, 3.5 × 1.2 in, $4 each, plus the **Full Set** (all twelve on one 8.5 × 11 in kiss-cut sheet) at $15.
  - **Classic die-cuts** — 13 stickers, about 3 in on the long side, $5: Freshly Certified, Level Up, Not On My Watch, Master Diver (octopus), Master Diver (chess king), Deep Diver, Drift Diver, Perfect Buoyancy, Warm & Dry-ish, Spicy Air, Sidemount Turtle, ID Fish eye chart, Altitude Diver.
- Images in `img/stickers/` (`<slug>.webp` 1200 px and `<slug>-t.webp` 600 px, sticker on warm paper). Cards open in the existing shirt lightbox (`sk-grid` added to its grid list).
- Matching Shopify drafts: 26 products (type Sticker, tags `sticker`, `sticker-achievement` / `sticker-die-cut`, `coming-soon`, `cert:<code>`), SKUs `DS-STK-A-<code>`, `DS-STK-D-<code>`, `DS-STK-A-SET12`; collections **Stickers**, **Achievement Unlocked**, **Die-cut Stickers**. Handles match the image slugs (e.g. `achievement-high-score`, `sticker-deep-diver`).
- Cache-busting stamps refreshed (`tools/bust.py`).

## 2026-11-02 — heavy DS mark on the Achievement stickers
- The 12 Achievement Unlocked stickers and the Full Set sheet now carry Eric's **heavy-weight DS mark** (white D + red S, from the 25 Oct heavy master), 0.40 in tall top-right; titles stop short of it. Images in `img/stickers/achievement-*` replaced.

## 2026-11-02 — the DS Seal sticker
- New card first among the die-cuts: **The DS Seal**, 3 in round, $5, four colourways from Eric's knock-out seal masters — Classic (navy + red on white), Black, Navy and Red (white ring and mark on the coloured field; navy S on red). Images `img/stickers/sticker-ds-seal*.webp` (card shows all four). Store: one product, option *Colourway*, SKUs `DS-STK-D-SEA-CLASSIC|BLACK|NAVY|RED`.

## 2026-11-02 — brand stickers
- Five more cards after the Seal: **The DS Stacked Logo** (3.4 × 2.9 in, $5) and **The DS Horizontal Logo** (5.4 × 1.8 in, $6), each in Classic, Black, Navy and Red; **Do - A - Little Scuba Stacked** (3.4 × 2.5 in, $5) and **Dive Kit** (4.9 × 1.8 in, $6) in Classic, Navy and Black; **Do - A - Little Scuba Bumper** (7.6 × 3.2 in, $7, Classic). All rounded rectangles with a 0.06 in white cut border; every colourway of a product shares one cut shape. Card images show all colourways; per-colourway images `img/stickers/<slug>-<colourway>.webp` feed the store.
- The QR versions of the tagline boards are free handout stickers (print package `print/promo/`), not store products.
