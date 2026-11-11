# Change log — 10 November 2026

## The sticker packs: site, store, Printful

Eric, 10 Nov: *"Update stickers from web to printful."* with `DoolittleScuba_StickerPacks.zip` — 37 three-sticker packs, each laid out as one 5.83 × 8.27 in kiss-cut sheet with a proof image and a 300 dpi print master.

### Site — a stickers page

**New `/stickers/`** (`tools/stickers_page.py`), in every page's nav after Hats. It opens on the packs, grouped by line:

1. **Themed packs** (26) — Reef Cuties, Lazy Reef, Pun Pack, Bubble Puns, Dive Computer Says, Diver Truths, Kit Bag, Gear Up, Critter Cafe Crew, Reef Pros, Wreck Divers, Into the Dark, Retro Patches, Vintage Classics, Pacific Bucket List, Atlantic & Red Sea, Reef Heroes, Ocean Pledge, Deep Weird, Strange Beauty, Ocean Masterpieces, Art History Dive, Dive Science 101, Pre-Dive Check, Turtle Trio, Octopus Trio.
2. **Classic sets** (5) — Certified, Master Diver, The Deep End, Specialty Mix, Chill Dives: the existing die-cuts three to a sheet.
3. **Brand sets** (6) — Classic, Navy, Black and Red trios, The Seal Set, Do A Little Scuba.

Each pack is a card with its proof (`img/packs/<slug>.webp`, 600 × 900, tap for the large image), its name, its contents and **$10**. Under the packs, the three single-sticker sheets (Achievement Unlocked, the classic die-cuts, the brand set) moved here from the home page, which keeps a six-proof **teaser** linking to the page. `tools/packs.json` (from the zip's `Pack_Index.csv`) is the pack registry the page is built from; `img/og/stickers.jpg` is the share image; sitemap updated. The print masters are **not** in the repo.

### Store — 37 products

- The 37 print masters went to **Shopify Files** as `files/DS-PK-<xx>.png` (staged uploads, alt text with SKU, name, size), where Printful pulls from.
- **37 products**, `sticker-pack-<slug>`, SKU `DS-PK-<xx>`, type Sticker, **$10** each, one image = the site proof, tags `sticker sticker-pack pack-<line> uv:<sheet> coming-soon`. Active on no channel, the same arrangement as the single stickers (Printful's import needs Active; the storefront shows nothing).
- New smart collection **Sticker Packs** (tag `sticker-pack`, 37). The Stickers collection picked them up by itself (69 now).

Full ids and details: `SHOPIFY-STORE.md`, 2026-11-10.

### Printful — plan and link

- `tools/printful_packs.py`: every pack → Printful's kiss-cut sticker sheet (product 505, variant 12917, $5.15), the master as the sheet's single placement. One of each costs $190.55 against $370 retail. The Shopify product/variant ids live in the script so the link can match by either SKU or Shopify id.
- `tools/printful_link.py --only packs` and `packs` in the GitHub **Printful link** job's list. Dry run first, then apply, once Printful has imported the 37 products.

### To confirm

- **$10 a pack** is an assumption (a $4.85 margin on the $5.15 sheet, before Printful's sticker shipping). Change `price` in `tools/packs.json`, rerun `tools/stickers_page.py`, and update the 37 Shopify prices.
- Printful's sheet template: check the current size and price before the first real order, and order one pack as a sample — the printed sheet is the proof of the kiss-cut lines.

### Routine, as before

`tools/bust.py` ran last; everything committed and pushed to `main`; live checked by probe.
