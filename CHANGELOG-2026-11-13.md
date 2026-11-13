# Changelog — 13 Nov 2026

### 10:33 — the four store policies, linked from every footer

Eric: *"It has no privacy, terms, shipping or returns links in the footer, even though all four policies are now in Shopify."*

- Shopify holds Privacy, Terms of service, Shipping and Refund policies (`shop.shopPolicies`). The storefront is password-protected, so `doolittlescuba.myshopify.com/policies/…` bounces to the password page; the **checkout-hosted copies** (`checkout.shopify.com/78733508794/policies/<id>.html`) are public and are what the site links.
- New `tools/policies.py`: writes four redirect pages — **/privacy/, /terms/, /shipping/, /returns/** (noindex, meta refresh + script, the same pattern as /youtube/) — and puts a footer line between `POLICIES` markers under the email line on every page with a footer (26 pages: home, the collections, about, custom, workshop, stickers, organic, the 15 site pages). Idempotent; re-run after adding a page. `line_pages.py` and `stickers_page.py` now carry the block from the home page like the social block, so regenerating keeps it.
- CSS: `.foot-meta .policies` — small mono uppercase, underlined links, right-aligned on desktop, left on phones. Checked at 1280 and 390; `/returns/` lands on the Shopify refund policy.
- README gained a *Store policies* paragraph.

### 11:30–14:15 — second Printful sample set staged; Off-World chest mark moved to the left chest

Eric asked for a sample order of everything still unproofed, then: small sizes, one Black Bart item, Wormhole for the Off-World joke, Trust But Test XL, The Seal cap L/XL and a navy waffle beanie.

- **Draft #sample-202611120318 (PF186447389), not charged, $204.65:** Blue Water Park cap S/M · The Seal cap L/XL · The Mark beanie · waffle beanie (Richardson 146R, Navy, DS mark on the cuff at 1.50 × 1.63 in — a catalog one-off, not a store product) · Black Bart light S · Off-World Dark Wormhole S · Trust But Test XL. Full table in the Project's copy of this changelog.
- **Off-World chest mark was centred, on all 60 tees.** Eric spotted it on the order's proof. Printful's v1 sync variants keep a file but not its `position` (readback: `"position": null`), so the 3.5 × 4 in chest file sent with the (1200, 300) offset printed dead centre (left 4.25 in, top 6 in).
  - Fix, the same pattern as every other tee line: the front is now a full 12 × 16 in master with the chest art placed at **left 8 in, top 2 in** (wearer's left chest, 3.75 in off centre). `tools/offworld_chest_fullarea.py` renders the 60 from the chest files and checks the ink box; uploaded to Shopify Files as `OW-<nn>_front-leftchest_12x16in_{light,dark}.png` (OW-03 dark = MediaImage 47432375861434). New workflow **Off-World chest masters** (render-only by default).
  - `printful_offworld.py` sends the new front file on the full area. `printful_link.py` gained `--show` (prints what Printful stores per variant) and the workflow gained `offworld` as a line choice and a `show` input.
  - Test relink DS-OW03-TD-S (run 43482626371): 1 / 1, Printful's new mockup shows the mark on the left chest. The full relink, lines=offworld apply force, is run 43488928528.
  - The sample order's Wormhole line was swapped for a fresh one from the fixed product.
- Printful's order editor only keeps changes when "Save as a draft" is clicked for real; a scripted click left the stored draft unchanged.
- Left out of the sample: a kiss-cut sticker — no sticker products appear in Printful's synced list any more; worth a look.

### 15:20–16:00 — Signature + Certified-ish chest lockup lowered to 2 in; sample: Thurmond Dam cap, Navy anorak
- **Chest height.** Eric on the Black Bart S proof: the chest lockup sat tight under the collar. Signature (28) and Certified-ish (40) fronts had the ink at centre 9.5 in / **top 0.5 in** of the 12 × 16 area (~1½ in below the 1717 collar seam, the same physical spot on every size). Eric: **top 2 in, centre 9.5 in** (same height as the Off-World mark).
  - `tools/chest_lower.py` moves the ink straight down (pixels copied, centre checked at 9.50 in) and writes `…_top2in.png`; all 30 masters went 0.50 → 2.00 in and are in Shopify Files (e.g. Black Bart BLACK = MediaImage 47434035232954). The masters workflow gained `what: chest-lower`.
  - `printful_signature.py` (`CHEST_POS = '_top2in'`) and `printful_certifiedish.py` send the new fronts. The organic editions reuse these plans, so the organic relink picks them up too.
  - One relink for all three tee lines: Printful link `lines=offworld,signature,certifiedish`, apply + force — run 43501433557 (replaced the Off-World-only run). Queued behind another Printful job.
- **Sample order** (draft #sample-202611120318, not charged): Blue Water Park cap → **Thurmond Dam cap, Dark Navy, S/M**; added **Champion Packable Anorak (CO200), Navy, XL** from the catalog (the jackets aren't synced yet — Shopify Draft): `DS_mark_HEAVY_PF-beanie-front` on the left chest (only placement, 4 × 4 in), true size 1.60 × 1.74 in canvas, top-centre, flat, 1801 White + 1839 Red; $43.42 + $2.95 digitization. Printful's mockup shows the mark on the wearer's left chest.
- **Still to do:** once run 43501433557 relinks DS-BBT-T-S, swap the order's Black Bart line for a fresh one (the order keeps a copy of the old file).
- 17:20 — Black Bart relinked (Printful's regenerated mockup shows the lockup ~3 in under the collar). The sample order's Black Bart line was swapped for a fresh one; the draft now carries the corrected Black Bart and Wormhole, 8 items, $261.26, not charged. Run 43501433557 was still going at 17:45 (Off-World and Signature done before Black Bart; Certified-ish last).
