# The organic line — 13 Nov 2026

Eric (13 Nov): *"Add beanie to the 'system' (DoolittleScuba.com, Shopify and the Printful pipeline). Create organic options for all the series as well as caps and beanies. Then add them into the system."*

## Decisions
- **Blank (tees):** Stanley/Stella STTU169 Creator 2.0, 100% organic cotton (Printful 456): $13.95 S–XL, $15.25 2XL, $16.75 3XL. That's $1.65–2.85 less than the Comfort Colors 1717. Same placements: front, back +$5.95, sleeves +$2.49.
- **Caps:** Econscious EC7000 organic baseball cap (491), $16.92 (+$0.41 vs the 6277). Black / Charcoal / Pacific / Jungle, one size, the same embroidery files.
- **Beanie:** Atlantis organic rib (449), 100% organic, $17.94, Black / Oxford Navy, the same cuff file. (The STAU295 "The Mark" beanie stays the regular one; it is 90% organic.)
- **Price:** the same as the regular item. A per-sale donation (ocean conservation or schools) is under discussion; no donation claim is made anywhere until it is decided.
- **Colours:** for each design, the nearest organic colour within its ink group (CIEDE2000 on Printful swatches). Only the eight colours Printful stocks in S–3XL are used. Watermelon goes to Cotton Pink to keep the colour family.
- **Kept separate:** each organic edition is its own product (tag `organic-line`, `eco`, `organic:<series>`), on its own page, `/organic/`. That page is listed first in the collections switcher and the home collections deck.

## Colour map (tees)
| Ink | Regular colour (Comfort Colors) | Organic colour (STTU169) | Designs |
|---|---|---|---|
| black | Blossom | Cotton Pink | 2 (signature 1, certifiedish 1) |
| black | Crunchberry | Cotton Pink | 1 (signature 1) |
| black | Orchid | Cotton Pink | 1 (signature 1) |
| black | Watermelon | Cotton Pink | 2 (signature 1, certifiedish 1) |
| black | Butter | Desert Dust | 12 (signature 1, certifiedish 7, offworld 4) |
| black | Ivory | Desert Dust | 6 (signature 1, offworld 4, n73 1) |
| black | Terracotta | Desert Dust | 1 (signature 1) |
| black | Bay | Heather Grey | 8 (signature 1, offworld 7) |
| black | Flo Blue | Heather Grey | 1 (signature 1) |
| black | Granite | Heather Grey | 6 (signature 1, offworld 4, n73 1) |
| black | Lagoon Blue | Heather Grey | 11 (certifiedish 5, offworld 6) |
| black | Seafoam | Heather Grey | 1 (signature 1) |
| black | Chalky Mint | White | 1 (signature 1) |
| black | Chambray | White | 12 (signature 1, certifiedish 6, offworld 5) |
| black | Island Reef | White | 1 (signature 1) |
| white | Black | Black | 37 (signature 1, offworld 4, n73 9, aquatic 23) |
| white | Graphite | Black | 28 (signature 1, offworld 4, n73 7, aquatic 16) |
| white | Grape | French Navy | 5 (signature 1, certifiedish 4) |
| white | Midnight | French Navy | 8 (signature 1, offworld 4, n73 3) |
| white | Navy | French Navy | 1 (signature 1) |
| white | True Navy | French Navy | 31 (signature 1, offworld 5, n73 5, aquatic 20) |
| white | Blue Spruce | Khaki | 7 (signature 1, offworld 2, n73 4) |
| white | Espresso | Khaki | 6 (signature 1, certifiedish 5) |
| white | Moss | Khaki | 10 (signature 1, certifiedish 1, offworld 7, n73 1) |
| white | Pepper | Khaki | 10 (signature 1, offworld 4, n73 5) |
| white | Sage | Khaki | 1 (signature 1) |
| white | Wine | Khaki | 1 (signature 1) |
| white | Yam | Khaki | 6 (certifiedish 6) |
| white | Denim | Stargazer | 1 (signature 1) |
| white | Emerald | Stargazer | 2 (signature 1, certifiedish 1) |
| white | Violet | Stargazer | 3 (certifiedish 3) |
Caps: Black → Black · Dark Navy, Royal Blue → Pacific · Dark Grey → Charcoal · Olive → Jungle.

## Built (all in the repo)
| Piece | What |
|---|---|
| `tools/organic.py` | The plan: 242 products / 1,358 variants (223 tees, of which 39 are personalized Aquatic, plus 18 caps and 1 beanie). SKU = regular key + `O` (`DS-THI-TO-M`, `DS-THI-TDO-M`, `DS-BAL-CO`, `DS-MRK-BNO-BLK`). |
| `tools/printful_link.py` | Line `organic` (job choice `organic`). Tees, caps and the beanie link by SKU; the 234 personalized variants are set to ignored. |
| `tools/aquatic_order.py` | `DS-AC…-TDO-<size>` orders go on the organic blank (same files and price). |
| `tools/organic_redye.py`, `organic_mockups.py` | 241 re-dyed mockups in `img/organic/<line>/` + `manifest.json`; the beanie is rendered (`img/organic/beanie/`). |
| `tools/organic_site.py` | `/organic/`; `DS.organicCfg` in `js/deck.js`; Organic first in every collections switcher (also in `line_pages.py`); the organic tile first on the home page. |
| `tools/organic_shopify.py` | The productSet batches for the store (Draft, `<regular handle>-organic`, same prices, mockups from the live site) and the "The organic line" collection. |

## Still to do
1. **Shopify:** the connector failed to connect on 13 Nov. When it is back: query the regular products by key, run `organic_shopify.py`, push the 25 batches, then create the collection. Update the 14 "<Site>, organic tee" drafts from 12 Nov in place.
2. **Printful:** the link job with lines `organic`, dry run first, then apply. Expect 1,124 linked and 234 ignored.
3. **Samples:** one organic light tee and one dark tee, plus an EC7000 cap, before anything goes Active.

## Status — 13 Nov (end of session)
- 14 Signature organic tees are live in Shopify as DRAFT. These are the 12 Nov drafts, converted in place with productSet (`identifier:{id}`). Each has 6 variants (DS-<code>-TO-S…3XL) and 2 media, both READY.
- The other 228 products are in `tools/organic_products_import.csv`: draft, Published FALSE. The connector blocks bulk mutations, so Eric imports this file in Shopify admin (Products → Import).
- After the import:
  - Create the smart collection "The organic line" (tag `organic-line`, handle `organic`).
  - Run the Printful link workflow with `lines=organic`: dry run first, then `--apply`.
- No donation or charity wording anywhere, per Eric ("Hold off on claim yet").

## 13 Nov (later): no pastels, colour changes called out, cart converter
- **No pastels.** Cotton Pink is gone from the organic palette. Blossom, Crunchberry, Orchid and Watermelon now go to Heather Grey, the nearest remaining colour (CIEDE2000 15.6–32.6). Six designs moved:
  - Signature: Thistlegorm, Rainbow Reef, Somosomo Strait, Vuna Reef.
  - Certified-ish: Open Water, Advanced Open Water.
  - Their mockups were re-rendered. `organic_redye.py` now keeps skin out of the fabric mask, which matters for red and pink garments. The 4 Signature drafts were updated in Shopify (media READY), and the CSV was regenerated (`tools/organic_csv.py`).
  - Organic palette now: light Desert Dust, White, Heather Grey; dark Black, French Navy, Khaki, Stargazer. Caps: Black, Charcoal, Pacific, Jungle. Beanie: Black, Oxford Navy.
- **Colour changes are called out.** Every card on /organic/ says "Colour changes: X → Y" (198 cards) or "Same colour as the regular" (44). The hero has a note: no pastels; convert the whole order or just some pieces in the cart.
- **Cart converter** (`shopify-theme/`):
  - `assets/ds-organic-map.json` comes from `tools/organic_cart_map.py`. It covers 243 regular SKU keys, and for each one gives the organic key, the organic handle, the from-colour + hex, the to-colour + hex, and the size rule. All 1,356 variant connections were tested.
  - `assets/ds-organic.js` adds a panel under the items on the cart page and in the cart drawer:
    - Each convertible line gets a checkbox and from→to swatches. Lines that change colour get a red "Colour changes" badge.
    - Two buttons: "Convert whole order to organic" and "Convert selected (n)".
    - If any colour changes, a confirm box lists them before anything happens.
    - It adds the organic lines first and then removes the regular ones, so nothing is lost if a step fails. Line properties (Aquatic names) carry over, plus a hidden `_organic_from` with the original SKU. It skips items with no organic edition and says so.
  - `snippets/ds-organic.liquid` holds the config + styles. `snippets/view-transition-opt-in.liquid` (rendered once in <head>) gains `{% render 'ds-organic' %}`.
  - **Not installed yet:** the theme-file write to "Horizon — Doolittle Scuba" (unpublished) was refused by the session's permission check. Install it in admin → Online Store → Themes → … → Edit code, or approve the upload.
  - It only works once the organic products are Active, because draft products aren't visible to `/products/<handle>.js`.
