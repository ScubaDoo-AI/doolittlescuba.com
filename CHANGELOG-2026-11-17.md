# Changelog — 17 Nov 2026

## Morning
- `STATUS` check (09:40 ET): site at `9c747f2`, store 568/19/0, custom-orders schedule and reminder succeeding, relay healthy.
- `NOTE-2026-11-17-0955-to-company.md`: both "waiting on Website" items in the Company status were already done (D16 relay, C8 prices).
- `TEST-ORDERS-2026-11-17.md` (`913b411`): the seven password-preview test orders, prerequisites (Printful manual confirmation, Bogus Gateway), checks and clean-up.

## Sleeve DS mark fix (afternoon)
Sample #sample-202611040806 showed the right-sleeve DS mark at ~2 in and high on the arm on a Certified-ish tee. Design rebuilt the file as the mark alone (1.00 in); Website found the cause and applied the fix.
- **Cause:** `printful_certifiedish.py` / `printful_n73.py` sent `sleeve_right` with no position, and the old file assumed a 3.5 × 4 in portrait area. Printful's sleeve print file for both the 1717 (586) and the STTU169 (456) is printfile 130: **600 × 525 px @ 150 dpi = 4.00 × 3.50 in, landscape** (`Printful read` run 44156328270).
- **Position:** mockup templates put the area's bottom edge ~0.9–1.0 in above the hem, so the mark sits on the area's bottom edge: `{area 600×525, width 165, height 179, top 346, left 218}` — 1.00 in ink, centred, ~1 in above the hem (the lowest Printful allows; Eric asked for ½ in).
- **Scripts (`b2ff808`):** both scripts send `DS_mark_PF-sleeve-right_1.00in_{NAVYRED|WHITERED}.png` with that position; `organic.py` and `sample_order.py` inherit it.
- **Mockup first:** `mockup:certifiedish:DS-TEC-TD-XL` rendered by Printful (run 44157431781) — correct size and place.
- **One product relinked:** Certified-ish Dark — Tech Diver, 6 sizes, `--apply --force --sku DS-TEC-TD` (run 44157718932, 6 linked, 0 failed); read-back confirms the new file (run 44158076431).
- **Waiting on Eric:** the remaining 151 products / 906 variants (certifiedish, n73, organic with 41 SKU prefixes). Details in `SLEEVE-MARK-FIX-Website-steps-2026-11-17.md`.
- **New tool:** `tools/printful_read.py` + Actions → **Printful read** (read-only lookups and planned-variant mockups).
- **Flagged:** `custom_order.py` sends the Make-it-yours sleeve as 3.5 × 4 (area is 4 × 3.5) — check on the first custom test order; Signature sleeve still positionless — check on the next Signature sample.

## Make it yours sleeve (16:05 ET)
- `tools/custom_tee.py` now renders sleeve files at Printful's real area, **4.00 wide × 3.50 tall** (1200 × 1050 px @ 300 dpi), and bottom-aligns every sleeve layer on the area's bottom edge (DS mark 1.00 × 1.09 in, shark 3.0 × 1.95 in, the buyer's line), centred side to side — the same place as the catalog lines' mark, about 1 in above the hem. `tools/custom_order.py` sends the sleeve layers with the matching full-area position (4 × 3.5 in). Rendered and measured three test designs (DS mark, buyer's line, shark). First real check: the Make-it-yours tee in the test orders (its Printful draft).
