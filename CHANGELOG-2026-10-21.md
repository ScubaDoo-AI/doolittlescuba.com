# DoolittleScuba.com — update of 2026-10-21

Deployed from the `main` branch of `ScubaDoo-AI/doolittlescuba.com` via Porkbun GitHub Connect (no more zips).

## Added
- **Make it yours — `/custom/`**, a personalization page. A live shirt mockup (SVG tee, front and back) next to eight steps:
  1. Garment colour: the 14 catalog colours as swatches (Comfort Colors 1717).
  2. Back: any of the 14 dive-site plates or 20 Certified-ish backs, full back or upper back (smaller), or no back print.
  3. Chest: the site block (name, flag, coordinates; set in type on the mockup, hand-drawn on the shirt), the seal, the DS mark, the shark mark, your logo, or none; left chest or centre chest.
  4. Sleeve: shark mark (standard), seal, DS mark, your logo, or none; right or left sleeve.
  5. Upper back: none, DS mark, shark mark, or your logo.
  6. Your line: up to 28 characters in hand-lettered, plain or mono lettering; under the chest print, upper back, or the other sleeve.
  7. Your logo: chosen in the browser only (never uploaded); once it is on the mockup, "Your logo" unlocks in steps 3–5; the request asks for the file as an email attachment.
  8. Sizes S–3XL with quantities, name, email, notes → "Write my request email" opens a pre-filled email to orders@ (same mailto pattern as the Workshop form) with every choice listed and a link that reopens the mockup; "Copy the summary" and "Copy a link to this mockup" for people whose mail app does not open.
  - Placement rules as agreed: back designs only on the back, chest blocks only on the chest, the seal on the chest or a sleeve, DS marks anywhere.
  - Colour suggestion: when the chest carries a site block, the swatches mark the suggested tones and a note explains why — the red diver-down flag (US sites) sits better on the cooler colours, the blue alpha flag (international) on the warmer ones, ivory with either. A suggestion, not a lock.
  - Mockup art: the 34 back designs, the shark mark, the DS mark and the seal under `custom/art/` as transparent WebP (5 MB) made from the watermarked previews, so the watermark travels with the art; thumbnails under `custom/t/` (0.5 MB). The mockup carries a "not a proof" label. Umami events: `custom-colour`, `custom-back`, `custom-logo`, `custom-copy-link`, `custom-copy-summary`, `custom-send`.
- "Custom" in the nav of all 19 pages (after Shirts); the note under the shirts grid links to it ("make your own"); `img/og/custom.jpg` (four mockups); sitemap entry.

## Added later the same day
- **The hats** (`#hats` on the home page, "Hats" in the nav of all 19 pages): a line of 20 pigment-dyed dad caps built from the front designs, the marks and the tagline. 14 site caps (the site's chest block on the front panels, the shark mark on the side, "Do - A - Little Scuba" across the back arch, in the site's catalog colour) and six brand caps: The Mark (navy, DS mark in white and red), The Stack (ivory, the stacked lockup), The Wordmark (mint), The Seal (sage, DS mark on the side), The Shark (Caribbean blue, shark mark front), Home Port (teal, a Newnan block with the dive flag and the home-port coordinates). Cards flip front/back and open in the lightbox like the shirts; every card links to its own set-up on the Make it yours page. All labelled "Coming soon". Mockups, not photographs: 80 images in `img/hats/` (0.7 MB), rendered from the cap mockup.
- **Make it yours — Shirt | Cap switch.** The cap mockup (front and back) with its own steps: Front (site block, DS stack, wordmark, DS mark, seal, shark mark, your line, your logo), Side (left/right; shark, DS mark, seal, logo), Back (the tagline, your line, DS mark, shark mark, logo). Navy is a cap-only colour and switches the marks and lettering to white. Quantity instead of sizes; the request email says "cap". A "Home Port" block (Newnan, 33°22.84 N 084°47.98 W) is available on caps. New art: `stack`, `wordmark`, `lockup-h` in navy/red and in white, `mark-w`, `ds-mark-w`.
- Back print on the shirt mockup scaled to the torso (top edge ~4 in. below the collar).
- **Every piece carries the shark mark or the DS mark.** The configurator enforces it: if the last brand mark is taken off (the seal and the stacked lockup count, since the DS mark is inside them), the shark mark is placed on the sleeve, or the upper back if the sleeve is taken (on a cap: the side, then the back), with a one-line note under the mockup. The request email names where the brand mark sits. All 14 catalog shirts and all 20 caps already comply.
- **Sleeve marks sit along the arm hole**: on the shirt mockup the shark mark or DS mark now sits at the bottom of the sleeve, just inside the hem and turned to follow it, instead of the upper arm; "your line" on the other sleeve follows the same hem. The request email says "along the arm hole".

## Verified
- All 19 pages at 1440 px and 390 px: 0 broken links or assets, no console errors, no horizontal overflow. Home checks unchanged (flip, lightbox, filters 20/20 and 15); the hats grid flips and opens the lightbox.
- Custom page exercised in a headless browser at both widths: colour, design, placements, line, logo upload (enables the logo chips, lands on the chest), sizes, summary, and the mockup link restoring the same state in a fresh page.

## Still open
- The chest block on the mockup is typeset; the real hand-drawn chest art (the `DS_print_packages_v13` folders and `Apparel\Designs`) is cloud-only in iCloud — mark those folders "Always keep on this device" and I can swap the real art in.
- Requests go by email (mailto); a form endpoint would capture them server-side.
- Colour hexes on the swatches are clean approximations of the Comfort Colors shades, not calibrated.
