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

## Sample set 2 re-drafted with the sleeve fix (17:15–18:25 ET)
Eric: "Create new updated proof order."
- **New draft #sample-202611172302 (Printful 187920236), not charged: 14 items, $449.60** (subtotal $344.99 · digitization $34.85 · shipping $40.28 flat, est. Dec 17 · tax $31.48).
  - Re-sent from the current plans (`b2ff808` sleeve: 1.00 in DS mark, explicit position, ~1 in above the hem): Certified-ish Nitrox Butter XL (`DS-NTX-T-XL`), 1N73LL1G3NC3 Trust But Test Pepper XL (`DS-N09-T-XL`), Original Ivory S (`DS-N15-T-S`); both anoraks from `printful_jackets.py` (`DS-MRK-CHA-NVY-XL`, `-BLK-S`, file + thread colours as linked).
  - Copied by sync variant from the old draft: The Seal cap, Thurmond Dam cap, Wormhole, Out Late, Bali, Dampier organic tee XL, Dampier organic cap, SOL'S windbreaker. The two cap sizes came across as the original sync sizes, so they were fixed in the editor (Seal S/M, Thurmond L/XL).
  - The Mark beanie French Navy: the API refused it ("out of stock", item 0) though the editor shows it in stock; added in the editor from Published products.
  - **Not carried:** the Richardson 146R waffle beanie (catalog one-off; Printful's order read-back has no placement and empty thread colours, so a copy would print wrong). Rebuild it in the editor if still wanted.
- The old draft #sample-202611120318 (186447389) is untouched.
- `tools/sample_order.py` + **Sample order** job: `from_id` / `drop` inputs (copy an order's items, leave some out, add SKUs); jackets in the SKU catalog; preview files skipped on copied one-offs.
- **Queue collisions (the `printful` concurrency group: a newer pending run cancels an older pending one):** this work cancelled two pending runs from the other session — Printful link 44180610329 (n73 relink, re-run by that session as 44191160591: 216 / 216), and 44195533024 (a Printful link run queued alongside an `n73 show` read-back; its inputs aren't visible). Relinks now complete: certifiedish 240 / 240, organic 469 / 469, n73 216 / 216.

## Sleeve DS mark: bulk relink (15:58–18:00 ET)
Eric's yes at 15:58. Three `Printful link` runs, `apply` + `force`, one after another:
- **Certified-ish** (run 44174954487): 240 linked, 0 failed.
- **Organic editions** (run 44174992726, `sku=` 41 prefixes): 469 linked, 0 failed — the intended 456 plus the Navy dive-site organic tee light/dark and organic cap (13 variants) that the `DS-N` prefix also matched, re-sent with their unchanged files. The other 1,029 organic variants untouched.
- **1N73LL1G3NC3** (run 44191160591): 216 linked, 0 failed. Its first two queued runs were cancelled by the shared `printful` Actions lane (the second by the Sample order dry run at 17:17), so it ran last.
- **Total today:** 925 linked, 0 failed (906 + the 6 Tech Diver Dark re-sent + 13 swept-in). All 152 products / 912 variants of the three lines now carry `DS_mark_PF-sleeve-right_1.00in_{NAVYRED|WHITERED}.png` at the 1-in-above-hem position.
- **Checks:** four Printful mockups (`DS-OWD-T-M`, `DS-N01-T-M`, `DS-SID-TDO-L`, `DS-N09-TO-L`; runs 44191462248 / 44195506812) — mark 1.00 in, centred, ~1 in above the hem, right ink on each; read-back of 24 variants (runs 44195527639 / 44195932920) shows the new file stored on every one.
- **Sample set 2:** re-drafted in the other session at 18:02 from the same plans (Printful 187920236, see the section above), so it carries the new sleeve.
- **Lane note:** `Printful link`, `Sample order` and `Aquatic order` share `concurrency: printful`; a newly queued run cancels any run still queued (not the one running). Queue a relink only when nothing else is waiting in that lane, or it gets bumped.
- Details: `SLEEVE-MARK-FIX-Website-steps-2026-11-17.md`.
