# DoolittleScuba.com — update of 2026-10-24

## Changed
- **Signature Series back prints.** Each dive-site plate now has a watermarked preview of the whole back print — the plate with its Facts / Species / Water block — made from the print files, with the same treatment as the Certified-ish finals: `img/designs/<slug>-back.webp` (900×1240, diagonal credit watermark and footer) and `custom/art/<slug>-back.webp` (alpha line art, watermark baked in). The plate-only previews (`img/designs/<slug>.webp`) stay as they were; the plate drawing in the back print is identical to them.
- **Home, the designs grid:** every card with artwork opens in the shirt viewer. A plate opens its full back print; a Certified-ish card opens its full design. Thumbnails unchanged; intro line says so. Umami event `design-open` with the design slug.
- **Site guides, "On the shirt":** the back print sits beside the two shirt photos, captioned; stacks under them on a phone.
- **Make it yours:** a plate at "full back" now shows the full back print (plate, facts, species, water) scaled to the torso, as the shirts are printed; "upper back, smaller" keeps the plate alone. Certified-ish backs unchanged.

- **Make it yours — prices.** A personalized tee is priced on the page as you build it: $43 each (the $38 tee + $5) for your design and colour, $44 (+ $6) once a line of your own or your logo goes on the shirt; $3 more in 2XL and 3XL, as the catalog. The price box above the sizes shows the per-item price, why, and the running total; the request email carries the same line. Caps follow the same rule on the $32 cap: $37, or $38 with your line or logo. The intro says the prices up front.
- Fix: the Caps quantity box no longer shows in shirt mode (`.field{display:flex}` was overriding `hidden`).

## Added
- `tools/backs.py` — builds the two back-print derivatives from the 3600×4800 print pages.
- `tools/bust.py` — the cache-busting stamp (`?v=<sha1[:8]>` on every local asset reference, plus the `v` map in the Make it yours data); the script referenced in the 2026-10-23 log, now in the repo. Run last.
- `workshop/index.html` picked up hashes on its `data-full` photo links (the lightbox had been loading unhashed URLs).

## Shopify (recorded in `SHOPIFY-STORE.md`)
- New draft product **Make it yours — personalized cap** (`make-it-yours-cap`): one size, Personalization "Your design and colour" $37 / "With your line or logo" $38, SKUs `DS-MYA-C` / `DS-MYB-C`, untracked.
- New draft product **Make it yours — personalized tee** (`make-it-yours-tee`): options Size × Personalization ("Your design and colour" $43/$46, "With your line or logo" $44/$47), 12 variants, SKUs `DS-MYA-T-<size>` / `DS-MYB-T-<size>`, inventory untracked (made to order), image `img/og/custom.jpg`. The mockup link goes in the order note at checkout.
- The 14 Signature Series tees carry the back-print preview as their third image (front photo, back photo, back print, plate close-up), imported under the new hashed URLs.
