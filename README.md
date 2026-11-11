# doolittlescuba.com

Source of the Doolittle Scuba L.L.C. website, published by Porkbun static hosting straight from the `main` branch (GitHub Connect). Plain HTML/CSS/JS, no build step.

## Pages

- `index.html` — the home page: hero, the five collection tiles with a search across every design, dive map, hats, stickers, the craft, about, logbook, contact.
- The collections, one themed page per line (since 9 Nov 2026), each holding that line's shirt cards, its designs grid and its story:
  `/signature/` (Signature Series, light + dark), `/certified-ish/` (light + dark), `/off-world/` (Off-World Hunt Club, light + dark), `/1n73ll1g3nc3/`, `/aquatic-comic/` (six subsets).
  `tools/line_pages.py` rebuilds their shells and themes around the cards they already hold; the cards are patched in place by the line tools (`tools/offworld.py`, `tools/n73.py`, `tools/aquatic.py`) between the `<!-- SH:END -->` and `<!-- DZ:END -->` markers.
- `/stickers/` (since 10 Nov 2026): the 37 three-sticker packs by line (themed / classic / brand, from `tools/packs.json`) and the single-sticker sheets that used to sit on the home page. `tools/stickers_page.py` rebuilds it; the home page keeps a six-proof teaser. The pack print masters are in Shopify Files only; `tools/printful_packs.py` is their Printful plan (one kiss-cut sheet each) and `tools/printful_link.py --only packs` attaches them. Check the sheet size against Printful's current template before the first real order.
- `/about/`, `/workshop/`, `/custom/` (Make it yours), `/sites/<slug>/` (site guides).
- Shared: `css/site.css` (the page styles; each collection page adds its own theme inline), `js/deck.js` (`DS.lightbox`, `DS.deck` + `DS.shirtsCfg`, `DS.designs`: the photo viewer, the shirts/hats deck, the designs grid filter and search), `js/designs.json` (the search index, built by `tools/line_pages.py` from the collection pages, `tools/design_subjects.json` — words OCR'd off the artwork by `tools/design_subjects.py` — and the site guides).
- Images live under `img/`, `about/img/` and `workshop/img/`. Print masters are not in the repo (Shopify Files; see `SHOPIFY-STORE.md`).

## Routine

- After changing any asset: `python3 tools/bust.py` (cache-busting `?v=` on every reference; the CDN caches by URL for 30 days).
- The shop-status banner on every page: edit `STATUS` in `tools/status_flag.py`, run it.
- Wide-screen scaling block on every page: `tools/wide_screen.py`.

Change log: `CHANGELOG-2026-10-18.md`, `CHANGELOG-2026-10-20.md`, … `CHANGELOG-2026-11-09.md`, `CHANGELOG-2026-11-10.md`, then the commit history. Status report: `STATUS-2026-11-04.md`.
