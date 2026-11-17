# Sleeve DS mark fix: Website Building steps 1–2 done, one product relinked — 17 Nov 2026, 14:35 ET

**For:** Eric (decision), Company, Design & Production. Follows the Company reply (14:10) and the Website count (14:15). Repo at `b2ff808`+.

## Step 1 — what Printful actually uses (read 14:12–14:16 ET, `Printful read` runs 44156328270 / 44156603524)

| Blank | Sleeve print file | Size | Note |
|---|---|---|---|
| Comfort Colors 1717 (586) | printfile **130** | **600 × 525 px @ 150 dpi = 4.00 in wide × 3.50 in tall**, fill_mode `fit` | both sleeves |
| Stanley/Stella STTU169 (456) | printfile **130** | same | same |

So the sleeve area is **landscape 4.00 × 3.50 in**, not the portrait 3.5 × 4 in the old file assumed. Front and back use printfile 1 (1800 × 2400 @ 150 dpi = 12 × 16 in), which is why the scripts' `AREA` position already works for those.

**Stored today (before the fix), read with `--show`:** Certified-ish `DS-TEC-T-*` and Signature `DS-THI-TD-*` both carry `sleeve_right` = the 3.5 × 4 in file; Printful's read-back doesn't expose positions, so "no position" is known from the scripts, not from Printful.

## Step 2 — H and the position

- Printful's mockup templates (253304 for the 1717, 324414 for the STTU169) put the **bottom edge of the sleeve print area about 0.9–1.0 in above the hem seam** on both blanks. So H ≈ 0.9–1.0 in, above Design's 0.55 in threshold: the mark goes on the area's bottom edge and **lands about 1 in above the hem, not ½ in**. Printful cannot print lower than its area. Eric: accept 1 in, or Design/Company take it up with Printful.
- Position sent for `sleeve_right`, in printfile pixels (150 dpi): `{"area_width":600,"area_height":525,"width":165,"height":179,"top":346,"left":218}` — the 1.10 × 1.19 in file box, centred, bottom on the area's bottom edge; ink 1.00 × 1.09 in.
- Scripts changed (`b2ff808`): `tools/printful_certifiedish.py` and `tools/printful_n73.py` now send `DS_mark_PF-sleeve-right_1.00in_{NAVYRED|WHITERED}.png` with that position. `tools/organic.py` reuses those file lists, so both organic editions inherit it; `tools/sample_order.py` builds from the same plans, so a re-drafted sample set 2 gets it too.

## One product first — done

- **Mockup before touching anything** (`Printful read` run 44157431781, `mockup:certifiedish:DS-TEC-TD-XL`): Printful rendered the plan's files for Certified-ish Dark — Tech Diver, Grape, XL. Right-sleeve view: mark 1 in wide, centred, bottom about 1 in above the hem. Images: `DS-TEC-TD-XL_right_mockup.png`, `DS-TEC-TD-XL_sleeve_mockup_zoom.png`.
- **Relinked** Certified-ish Dark — Tech Diver, all 6 sizes (`Printful link` run 44157718932, `--apply --force --sku DS-TEC-TD`): 6 linked, 0 failed. Read-back (run 44158076431) shows `sleeve_right` = `DS_mark_PF-sleeve-right_1.00in_WHITERED.png` on every size.
- Nothing else in Printful has changed.

## Waiting on Eric's yes — the remaining 151 products / 906 variants

Three `Printful link` runs, all `apply` + `force`:

| Run | Input | Variants |
|---|---|---|
| 1 | `lines=certifiedish` | 240 (the 6 above are re-sent unchanged) |
| 2 | `lines=n73` | 216 |
| 3 | `lines=organic`, `sku=` the 41 prefixes `DS-<code>-TO, DS-<code>-TDO` for the 20 Certified-ish codes + `DS-N` | 456 (240 Certified-ish organic + 216 1N73LL1G3NC3 organic). The prefix list keeps the other 1,042 organic variants untouched. |

Then four check mockups (one per line and blank) and the read-back, and Company re-drafts sample set 2.

## Two things found on the way

1. **Make it yours sleeve — fixed 16:05 ET (Eric's instruction).** `tools/custom_tee.py` renders sleeve files at the real 4.00 × 3.50 in area with every sleeve layer bottom-aligned and centred (DS mark 1.00 in, shark, the buyer's line), and `tools/custom_order.py` sends the matching 4 × 3.5 in full-area position (v2 orders, inches). Test renders measured correct. Confirm on the first Make-it-yours test order's Printful draft before approving it.
2. **Signature Series sleeve** still goes without a position (3.24 in shark + signature, meant to fill the area). With a 4 × 3.5 landscape area and a portrait file, the result depends on Printful's default; check it on the next Signature sample as Design asked.

## Tools added (repo)
- `tools/printful_read.py` + Actions → **Printful read**: read-only lookups (`/mockup-generator/printfiles/<id>`, `/mockup-generator/templates/<id>`, `/products/<id>`) and `mockup:<line>:<SKU>` to render a planned variant's mockups without changing the product. The Printful token stays in repo secrets.
