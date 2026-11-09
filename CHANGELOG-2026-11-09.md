# Change log — 9 November 2026

## One themed page per collection

Eric, 9 Nov: *"Let's place items unrelated to diving on a separate page so not to confuse theming"*, then *"Each line should be on its own themed page."* Also: *"Update banner, add subject search to webpage for designs."*

### What changed

**Five new pages**, one per line, each with its own look, its own shirts deck, its own designs grid and its story. Light and dark versions of a line share its page (same designs, different tees); the whole 1N73LL1G3NC3 line is on its page, dive designs included, so no line is split.

| Page | Line | Theme |
|---|---|---|
| `/signature/` | Signature Series, 14 light + 14 dark | the chart sheet the site already had: navy, pastels, Almendra; hero is the Black Bart shirt worn, with coordinates up the margin |
| `/certified-ish/` | Certified-ish, 20 light + 20 dark | a page from the logbook: cream paper, ruled lines, a certification card with a red rubber stamp |
| `/off-world/` | Off-World Hunt Club, 30 light + 30 dark | near-black with a faint starfield, one word in red; the preview shown as the dark line (white ink) |
| `/1n73ll1g3nc3/` | 1N73LL1G3NC3, 36 | graphite terminal: JetBrains Mono / Jost, cream phosphor, a grid, a blinking prompt, R34D 17 R1GH7 |
| `/aquatic-comic/` | Aquatic Comic, 59 in six subsets | warm paper, IM Fell, halftone dots, a speech bubble with the punch word in red; subset chips on the deck and the designs |

Each page: the site shell (header, nav, shop-status flag, footer), a **collections switcher** under the header, a themed hero with the line's garment-colour swatches, **The shirts** (the deck: Light tees / Dark tees, or the Aquatic subsets), **The designs** (status chips, subset chips on Aquatic, a **search box**), **Wear it your way** (launch news → `/#contact`, Make it yours → `/custom/#tab=…`), **The other collections** (tiles to the other four), footer. Deep links: `/off-world/#offworld-dark` opens the dark deck, `/signature/#designs` jumps to the art, `/aquatic-comic/#d-ac-s02-current` scrolls to and marks one design. OG image per page (`img/og/<page>.jpg`), JSON-LD `CollectionPage`, sitemap entries.

**The home page is the hub.** The shirts deck and the designs grid left it (606 KB → 120 KB). The five collection tiles now link out to the pages (dark line / subset / art links deep-link into them). Under the tiles: **Search every design**, across all 160 designs, results linking into the right page at the right design. Nav on every page: *Designs* + *Shirts* → **Collections** (`/#lines`). Hero button → *See the collections*. "Hand Signals" (in progress, no line yet) is noted under the tiles rather than shown in a grid.

**Subject search.** Two boxes, one index: `js/designs.json`, built by `tools/line_pages.py` from (a) each design card's name, subtitle, alt and caption, (b) the text on its shirt card, (c) for plates, the site guide's prose (species, conditions, the story) and the sites data, (d) for Aquatic, the whole joke, (e) **the words on the artwork itself**, OCR'd from the previews by the new `tools/design_subjects.py` into `tools/design_subjects.json` (159 designs; the N73 messages also indexed decoded: "read the meter" finds R34D 7H3 M373R). So "grouper", "turtle", "manatee", "narcosis", "wormhole", "kilowatt" all land. The collection pages search the cards on the page and, once you type, the same index.

**The banner** (shop-status flag) reads: *New: every collection now has a page of its own — Signature Series, Certified-ish, Off-World Hunt Club, 1N73LL1G3NC3 and Aquatic Comic — and you can search all 160 designs from the home page. We're still spot-proofing physical samples before the shop opens; designs stay "Coming soon" until the samples pass.* State still **Proofing**, id `2026-11-09-collections` (re-shows to anyone who dismissed the 4 Nov one), link unchanged. Wording: edit `STATUS` in `tools/status_flag.py`, run it.

### Shared code (new)

- `css/site.css` — the home page's main stylesheet, moved out of `index.html` and shared by every collection page (which adds its theme inline), plus the collection-page components (`.coll`, `.swatches`, `.two`, `.more`, `.dz-q`, `.find`).
- `js/deck.js` — `window.DS`: `DS.lightbox()` (every `.sh-grid` → `#sh-lb`), `DS.deck(section, grid, cfg)` (the deck engine; now opens the line named in the URL hash), `DS.shirtsCfg({lines, contact})` (the one shirts config for every line), `DS.designs()` (status / line / subset chips, the search box, `#d-<slug>` deep links). The home page keeps its hats config inline.
- `js/designs.json`, `tools/design_subjects.json` — the search index and the OCR word bags.

### Tools

- **New** `tools/line_pages.py` — builds the five pages (shell + theme) around the cards they hold; first run harvested the cards from `index.html` and rewrote `img/` → `/img/`. Re-run after changing a theme, the shell or the copy; `--og` redraws the share images. Also writes `js/designs.json` and the sitemap entries.
- **New** `tools/design_subjects.py` — OCR of the design previews (tesseract) → `tools/design_subjects.json`; run after new designs land (only missing slugs are read; `--all` redoes everything).
- **Retargeted** `tools/offworld.py`, `tools/n73.py`, `tools/aquatic.py`: they patch their collection page (not `index.html`), write `/img/…` paths, insert before `<!-- SH:END -->` / `<!-- DZ:END -->`; the one-time home-page deck/tile patches are gone (deck config lives in `js/deck.js`). Verified: running `offworld.py` and `n73.py` against the generated pages reproduces them byte for byte (`?v=` aside). `aquatic.py` now stamps `data-sub` on its designs cards.
- `tools/status_flag.py`, `tools/wide_screen.py`: the five pages added to `PAGES`.
- Older one-shot tools that patched the home page's shirts/designs sections (`darkline.py`, `certdarkline.py`, `certifiedish_front.py`, `backs.py`, `darkset.py`) are historical; their work is in the pages.

### Routine, as before

`tools/bust.py` ran last; everything committed and pushed to `main`; live checked by probe. Shopify and Printful untouched (the Make it yours links and product data did not change).

### Decisions to confirm

- Light + dark share a page; 1N73LL1G3NC3 keeps its six dive designs. Both are one edit in `tools/line_pages.py` (`LINES`).
- Page names/URLs: `/signature/`, `/certified-ish/`, `/off-world/`, `/1n73ll1g3nc3/`, `/aquatic-comic/`. Renaming = `dir` in `LINES` + the links on the home tiles + sitemap.
- The banner text above.
