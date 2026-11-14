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
- 17:55 — Eric: "Make the black Bart a Bali version." The sample's Black Bart light S was replaced by **Bali — Signature Series tee, Terracotta, S** (already relinked: Alpha flag + Bali + coordinates at the new 2 in height, Bali plate on the back, shark sleeve). Still 8 items, $261.26.
- 18:30 — Eric: "Add another jacket in s same design" → **Champion Packable Anorak, Black, S** built from the catalog with the same left-chest DS mark (true size, top-centre, flat, 1801 White + 1839 Red), $43.42, no new digitization. (A duplicate-then-recolour of the Navy line stalled on Printful's "Generating files…" and was removed.) Saved draft: **9 items, $310.85** (subtotal $232.46 · digitization $28.35 · shipping $28.98 · discount −$2.00 · tax $23.06), not charged.
- 21:46–22:05 — Eric: "Add 1 of each of these 7 items" (the unproofed list), then "Don't repeat shirt or hat designs", then "Since the trip to Raja Ampat is coming up, maybe use Bali and Dampier as samples." Added (all S unless one size), each mockup checked:
  - Dampier Strait — Signature Series **organic** tee, Desert Dust (STTU169) · Aquatic Comic Boat Banter — Born to Dive **organic** tee, Black (first Boat Banter sample) · Dampier Strait — **organic cap** (EC7000), Pacific · The Mark — **SOL'S Basic Windbreaker**, Navy · **Certified-ish — Nitrox** tee, Butter (light line, lowered chest) · **Off-World — Hunter** tee, Bay (light line) · **1N73LL1G3NC3 — Original** tee, Ivory (navy + red sleeve mark).
  - Dropped as repeats: Bali / Wormhole organic tees, Thurmond Dam organic cap, The Mark organic beanie (the only organic beanie design, same DS mark as the rib beanie).
  - Saved draft #sample-202611120318: **16 items, $492.36** (subtotal $382.02 · digitization $34.85 · shipping $44.49 · discount −$2.00 · tax $33.00), not charged. Printful's estimated delivery: Dec 14 (flat rate).
- 22:05–22:20 — Eric: Desert Dust and Butter to XL; Off-World jokes 27 and 3. Nitrox (Butter) changed to XL in place. Desert Dust XL is greyed out in Printful's size dialog ("default selling preferences"), so the Dampier Strait organic tee Desert Dust XL (variant 51012373315770) was added from the synced product and the S removed. Off-World Hunter (Bay S) swapped for **Out Late** (OW27, "Mothership says I can stay out late", Lagoon Blue S); Wormhole (OW03, True Navy S) kept. Saved draft and checked the order modal: **16 items, $492.34** (subtotal $382.02 · shipping $44.48 · tax $32.99), not charged.
- 22:25 — Eric: "Swap seal cap and Thurmond Dam sizes." **The Seal — Dark cap, Black → S/M**; **Thurmond Dam — Dark cap, Dark Navy → L/XL** (Flexfit 6277, size dialog). Saved and checked in the order modal: 16 items, still $492.34, not charged.
- 22:30 — Eric: "Remove Aquatic Comic." Boat Banter — Born to Dive organic tee (Black S) removed. Saved and checked: **15 items, $470.24** (subtotal $362.12 · shipping $44.48 → $42.28 · tax $32.99 as shown), not charged.

## Jackets added to the system (13 Nov, 13:00–19:10)
- **Line:** Champion Packable Anorak (CO200, Printful 399) and SOL'S Basic Windbreaker (32000, Printful 661).
  - Black and Navy, S–2XL, left chest only: the heavy DS mark at 1.50 × 1.64 in, flat, threads 1801 White and 1839 Red.
  - Plan is `tools/printful_jackets.py`. Anorak $89 / $92, windbreaker $49 / $52 (proposal).
- **Mockups:** Printful's Mockup Generator with our file (workflow `printful-mockups.yml`), saved to `img/jackets/`.
- **Site:** a "The jackets" section on the home page after the hats, with 4 cards (Worn / Close-up). **Jackets** is in the nav on every page (24 pages + `tools/line_pages.py`).
- **Shopify:** "The Mark — Champion Packable Anorak" (10432500465850) and "The Mark — SOL'S Basic Windbreaker" (10432500498618).
  - Options Colour × Size, SKUs `DS-MRK-{CHA|WND}-{BLK|NVY}-<size>`.
  - 8 / 10 images. Each variant now shows its colour's worn shot.
  - Collection **Jackets** (493648412858, tag `jacket`).
  - Active and on the Online Store channel since 20:17 (see below).
- **Printful:** linked 20 / 20 (run 43526121203). Printful set 9,999 on every variant.
- 19:20 — **Organic relink for the lowered chest:** the organic link run (43487195817) checked out before `eb4c1c5`, so the organic Signature and Certified-ish tees went to Printful with the old 0.5 in chest. Organic Off-World already had the full-area left-chest fronts (`c0395cb`).
  - Re-sent with `force`: run 43532402942, lines organic, sku = the 34 `DS-<code>-T` prefixes, 408 variants expected.
  - **Done: 408 / 408 relinked, 0 failures** (finished 01:07 UTC, 14 Nov). Every organic tee now carries its line's current chest position.
- 20:17 — Eric: *"Activate the jackets - organics as well."* **244 products → ACTIVE** (242 organic-line, 2 jackets), 0 errors.
  - Status was set by the bot app (`organic_import.py --activate`, Organic import workflow run 43540346270).
  - All 244 are published to the **Online Store** channel (`publicationUpdate` in batches of 50), as are the collections **The organic line** and **Jackets**.
  - The storefront password is still on (checked), so nothing is public — the same state as the 12 Nov pass. Launch is still Online Store → Preferences → remove the password.

## Shopify storefront hero (13 Nov, 18:06–20:20, chat session)
- **Live work is on "Horizon — Doolittle Scuba"** (`gid://shopify/OnlineStoreTheme/160959234234`, unpublished — the project's working theme with `ds-brand.css`, the organic cart script, the Aquatic personalize block). Committed 20:20 (theme commit b466d77):
  - Hero image `hero-pair-blue.jpg` → Eric + Allie underwater selfie `shopify://shop_images/GOPR0150_Copy_Copy.jpg` (in Files since 13 Nov).
  - New `assets/ds-horizontal-on-black.svg` — the Project's official `DS_horizontal_on-black_7p28in.svg` (white + red #C82026, Almendra outlined), unchanged.
  - New first block in the hero, `brand_overlay` (custom-liquid, "Brand overlay"): the lockup in the open water top-left, desktop `clamp(384px,54vw,832px)`, phones centred top `min(56vw,224px)`, soft navy drop shadow. A small script moves it into `.hero__media-wrapper` so it sits on the photo even where the hero CSS doesn't load (Shopify's screenshot tool and the Shopify app preview render hero content below the image).
  - Hero copy, button, overlay colour and height unchanged ("Dive art, drawn by hand." / subhead / "See the shirts").
- **"Horizon – Dive Hero"** (161576157370) was a first pass duplicated from the stock live Horizon; it lacks the Doolittle Scuba theme's files and is **superseded — don't publish it**; delete it in Online Store → Themes when convenient.
- Open: collection order on the home page (checklist: Signature Series · Certified-ish · Hats; the product list currently shows "all"); an organic-line mention in the hero; header logo size check on a real device.

## Product images on dark backgrounds (13 Nov, 21:00–22:10, chat session)
Eric: *"check and render all mock ups for a dark desktop theme don't lose dark apparel on dark backgrounds"* → chose **replace in place**.
- **Scope:** 1,297 product images checked; **1,020 re-rendered** (528 products) — the light studio background swapped for a navy spotlight (#3E557E centre → #162645 edge) so black/navy apparel keeps a visible edge on the #0E1B33 theme. Shadows kept (multiply ratio). White/light organic tees used their regular-line sibling's mask; on-model light shirts used rembg (u2net_human_seg).
- **Left as is (277):** print-file previews and sticker-pack sheets on white (181), images already on dark or photographic backgrounds (95), 1 noisy light image.
- **Method:** each image swapped with `fileUpdate(originalSource)` on its existing MediaImage, so URL, position and alt text are unchanged. (`bulkOperationRunMutation` is blocked by the Shopify connector; done as 11 batches of ≤100.) **Verified:** all 1,020 live CDN images compared to the local renders — 0 mismatches.
- **Undo:** originals backed up in Shopify Files as `ds-product-images-light-originals-2026-11-13-part1/2/3.zip` (GenericFile 47438979760314 / …793082 / …825850; 18.5 + 18.6 + 10.5 MB). Restore = `fileUpdate` each MediaImage from its original in the zip.
- Known flaw: one white Black Bart organic back has a small notch at the hem.

### ⚠️ TO DO — Eric, 21:57: "All item renders need to be revisited."
Every product render (the dark re-renders above and the mockups they came from) needs a full review pass before launch — look at each product page in the dark theme, flag any edge halos, lost shadows, wrong crops or colour shifts, and redo those.

## Automated custom shirts pipeline — phase 1 (13 Nov, late)
Eric: *"Let's get the automated custom shirts pipeline up."*

- **Approval and scope:**
  - Approval is by draft: Eric approves every order.
  - The three products are added one at a time, Make it yours tee first.
  - Logo orders are held.
- **What was built:**
  - /custom/ has an **Add to cart** button: tier A/B variant, design in `_design`.
  - `tools/custom_tee.py` renders the print files.
  - `tools/custom_order.py` turns paid orders into Printful v2 drafts.
  - `tools/custom_order_issues.py` opens one issue per draft or hold.
  - Workflow **Custom orders** runs every 15 min.
- **Eric's rules:**
  - When the chest is a custom logo, the DS mark goes on the sleeve and there is no shark signature.
  - Logo shirts are aimed at wholesale and dive shops. /custom/ shows "Wholesale quote" and emails sales@ instead of offering Add to cart.
- **First dry run:** run 43556984598, OK (no custom orders in 60 days). Before it, scipy was added to the workflow.
- **Details:** in `CUSTOM-ORDERS.md`, including the pre-launch checklist.

### 23:50 — custom orders phase 2: personalized Aquatic name tees
- Eric: "Aquatic tees". The 39 name tees (regular and organic) are now in the **Custom orders** job.
- How it works:
  - The names come from the product page's line properties.
  - The job renders with `aquatic_print.py`.
  - It makes one Printful draft per order, together with any Make it yours lines.
- Hold kind `name`: a missing name or a too-long name.
- Orders already sent by hand with `aquatic_order.py` are skipped.
- Local fake-order tests passed. Dry run 43558694991 OK.

### 00:05–01:30 (14 Nov) — custom orders phase 3: Make it yours cap + digitization fee
- **Eric:** pass the digitization charge to the customer, plus $0.50, once per design. 5 identical caps = 1 fee; a cap + a jacket = 2 fees.
- **His answers:**
  - Logo caps stay a wholesale quote, with the fee on the quote.
  - Text caps pay the fee at checkout.
- **Shopify:** new product "Embroidery digitization — one time per design" (`DS-DIGI-1/2/3`: $7.00 / $9.95 / $12.90), Active on the Online Store, no shipping.
- **/custom/:**
  - cap S/M and L/XL quantities, cap Add to cart, one fee line per design;
  - the fee is shown in the price;
  - a back-line limit of about 20 characters;
  - the logo-cap quote explains the fee.
- **Fixed:** the cap view showed the shirt sizes, shirt-only colours and rows. A CSS display rule beat the `hidden` attribute.
- **New `tools/custom_cap.py`:** catalog cap files reused by URL, the text line rendered at the 0.25 in floor, Printful v2 embroidery placements.
- **`custom_order.py`:** cap lines; a fee check (hold if missing, refund note if paid twice); shared uploads per design.
- **Workflow:** new `catalog` mode (Printful catalog facts only).
- Details in `CUSTOM-ORDERS.md`.
