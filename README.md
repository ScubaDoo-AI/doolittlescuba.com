# doolittlescuba.com

Source of the Doolittle Scuba L.L.C. website, published by Porkbun static hosting straight from the `main` branch (GitHub Connect). Plain HTML/CSS/JS, no build step.

## Pages

- `index.html` — the home page, as a short path (since 26 Nov 2026, `tools/home_layout.py`): hero, Start here (8 picks), the collection tiles with a search across every design, Shop by dive site (the map), Make it yours, the craft, about, logbook, contact.
- `/caps/` (the hats deck) and `/jackets/` (since 26 Nov 2026): moved off the home page. Tools that edit the cap figures (`pairs_site.py`, `caps_printful_colours.py`, `hats_v2/3.py`, `site_shop.py`) now read `caps/index.html`.
- The collections, one themed page per line (since 9 Nov 2026), each holding that line's shirt cards, its designs grid and its story:
  `/signature/` (Signature Series, light + dark), `/certified-ish/` (light + dark), `/off-world/` (Off-World Hunt Club, light + dark), `/1n73ll1g3nc3/`, `/surface-interval/` (six subsets).
  `tools/line_pages.py` rebuilds their shells and themes around the cards they already hold; the cards are patched in place by the line tools (`tools/offworld.py`, `tools/n73.py`, `tools/aquatic.py`) between the `<!-- SH:END -->` and `<!-- DZ:END -->` markers.
- `/stickers/` (since 10 Nov 2026): the 37 three-sticker packs by line (themed / classic / brand, from `tools/packs.json`) and the single-sticker sheets that used to sit on the home page. `tools/stickers_page.py` rebuilds it; the home page keeps a six-proof teaser. The packs are printed by Sticker Mule, not Printful (confirmed 12 Nov 2026): one 4 × 6 in kiss-cut sheet each, three stickers plus small fillers, printed in bulk from the PDFs in Shopify Files (`files/DS-PK-<xx>_<Name>_4x6_kisscut.pdf`, ids in `tools/packs.json` "print_file_id"); the print files never go in this repo. The store's product and variant ids for every pack are in `packs.json` too (`shopify_product` / `shopify_variant`). Stock is held, so turn on inventory tracking for the 37 pack variants before they go on sale. The Achievement set (`DS-STK-A-SET12`, the deck's opener) is different again: a UV DTF gang sheet from Ninja Transfers, eight sets per 22 × 24 in sheet, seventeen rub-on stickers per set (`packs.json` "print_note").
- `/towels/` (since 22 Nov 2026): the twelve Water Hazard hanging hand towels (renamed 25 Nov; a beach towel line is in progress), two sets of six, $28, printed to order by Printful. `tools/towels_page.py` rebuilds it (the towel list is in the script).
- `/rash-guards/` (since 25 Nov 2026): the Signature Series rash guards, 14 sites × Light/Dark × five cuts ($39–$75), all-over printed to order by Printful. A deck with Light/Dark tabs whose open card has a style picker (`DS.rashCfg` in `js/deck.js`). `tools/rashguards_page.py` rebuilds it from `tools/rashguards.json`; prices sit in both the script and `DS.RG_PRICE`.
- `/about/`, `/workshop/`, `/custom/` (Make it yours), `/sites/<slug>/` (site guides). Each guide opens with a "Wear <site>" strip (since 26 Nov 2026): every product for that site (tees, cap, rash guards, organic), built by `tools/site_shop.py` from `js/catalog.json` and the cards on the Signature, home and organic pages. Re-run it after those change.
- Shared: `css/site.css` (the page styles; each collection page adds its own theme inline), `js/deck.js` (`DS.lightbox`, `DS.deck` + `DS.shirtsCfg`, `DS.designs`: the photo viewer, the shirts/hats deck, the designs grid filter and search), `js/designs.json` (the search index, built by `tools/line_pages.py` from the collection pages, `tools/design_subjects.json` — words OCR'd off the artwork by `tools/design_subjects.py` — and the site guides).
- Images live under `img/`, `about/img/` and `workshop/img/`. Print masters are not in the repo (Shopify Files; see `SHOPIFY-STORE.md`).

## Routine

- After changing any asset: `python3 tools/bust.py` (cache-busting `?v=` on every reference; the CDN caches by URL for 30 days). **Never fetch a new `?v=` URL before the publish has landed**: the CDN would cache the old file under the new URL for 30 days. Probe live only with an extra `?probe=<random>` on the URL (`…/js/deck.js?v=abc&probe=123`), and if a canonical URL did get poisoned, change the file (a comment line is enough), bust again and push.
- The shop-status banner on every page: edit `STATUS` in `tools/status_flag.py`, run it.
- Wide-screen scaling block on every page: `tools/wide_screen.py`.
- Status words: anything for sale says "Coming soon"; "Art finished" / "In progress" belong to the art grids and to sites with no products. `tools/shop_status.py` enforces it after a site gets products.
- The header menu (Shop ▾, Dive sites, Custom, Our story ▾, Cart) lives in `tools/site_nav.py`, with `css/nav.css` and `js/nav.js`. Edit the link lists there, run it, then `tools/bust.py`. Re-run it after any page generator, since generators copy their shell from other pages.

Change log: `CHANGELOG-2026-10-18.md`, `CHANGELOG-2026-10-20.md`, … `CHANGELOG-2026-11-09.md`, `CHANGELOG-2026-11-10.md`, then the commit history. Status report: `STATUS-2026-11-04.md`.

**Store policies.** Privacy, Terms, Shipping and Returns live in Shopify (Settings → Policies). The storefront is password-protected, so the public copies are the checkout-hosted pages; `tools/policies.py` keeps four redirect pages on the site (`/privacy/`, `/terms/`, `/shipping/`, `/returns/`) pointing at them and the footer line between `POLICIES` markers on every page. Re-run it after adding a page or when a policy URL changes; the page generators carry the line from the home page.

## Real photos (since 26 Nov 2026)

When sample photos arrive, save each one as `img/real/<SKU stem>.webp` (or .jpg / .png), square, about 1200 px: for example `img/real/DS-BBT-T.webp` for the Black Bart light tee, `DS-VUN-CD` for the Vuna Reef cap, `DS-THI-RGMLS-D` for the dark Thistlegorm rash guard. Then run `tools/site_shop.py`, `tools/home_layout.py` and `tools/bust.py`. The site-guide "Wear" strips and the home page Start here picks use the real photo in place of the mockup. The stems are the keys of `js/catalog.json`.
