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
