# DoolittleScuba.com — update of 2026-10-24

## Changed
- **Signature Series back prints.** Each dive-site plate now has a watermarked preview of the whole back print — the plate with its Facts / Species / Water block — made from the print files, with the same treatment as the Certified-ish finals: `img/designs/<slug>-back.webp` (900×1240, diagonal credit watermark and footer) and `custom/art/<slug>-back.webp` (alpha line art, watermark baked in). The plate-only previews (`img/designs/<slug>.webp`) stay as they were; the plate drawing in the back print is identical to them.
- **Home, the designs grid:** every card with artwork opens in the shirt viewer. A plate opens its full back print; a Certified-ish card opens its full design. Thumbnails unchanged; intro line says so. Umami event `design-open` with the design slug.
- **Site guides, "On the shirt":** the back print sits beside the two shirt photos, captioned; stacks under them on a phone.
- **Make it yours:** a plate at "full back" now shows the full back print (plate, facts, species, water) scaled to the torso, as the shirts are printed; "upper back, smaller" keeps the plate alone. Certified-ish backs unchanged.

## Added
- `tools/backs.py` — builds the two back-print derivatives from the 3600×4800 print pages.
- `tools/bust.py` — the cache-busting stamp (`?v=<sha1[:8]>` on every local asset reference, plus the `v` map in the Make it yours data); the script referenced in the 2026-10-23 log, now in the repo. Run last.
- `workshop/index.html` picked up hashes on its `data-full` photo links (the lightbox had been loading unhashed URLs).

## Shopify (recorded in `SHOPIFY-STORE.md`)
- The 14 Signature Series tees carry the back-print preview as their third image (front photo, back photo, back print, plate close-up), imported under the new hashed URLs.
