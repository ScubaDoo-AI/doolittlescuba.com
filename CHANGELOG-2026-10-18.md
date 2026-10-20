# DoolittleScuba.com — rework of 2026-10-18

Baseline: the live site as served on 2026-10-18 (home, /about/, /workshop/, 15 /sites/ guides, css/js/img), not the Oct 9 zip or the Project's older index.html — both were behind production.

## Added
- **The shirts** section on the home page (`#shirts`, between The collections and The designs): 10 printed samples (one card per site + colour), each with Front/Back flip, a lightbox for the full photo, status pill (First release / Sample print) and a link to the site guide; lead tile of the folded set. 21 new images in `img/shirts/` (1200 px full + 600 px thumb, WebP, square-cropped from the studio set). Sources: `iCloudPhotos\Photos\shirt set` (Approved - Print where available; see the mapping table below). Five colourways whose front shot was not on the form at the standard framing were left out (19 Oct): Bridge Span 14 orange, Blue Grotto light blue, Dive Land Park orange and aqua, The Thistlegorm yellow; conforming alternates exist in the folder (IMG_7001, 7092, 7068/7072, 6991) if you want them back.
- "Shirts" link in the nav of every page; hero ghost button now points at the shirts.
- Social links in both `<!-- SOCIAL -->` slots on every page: Instagram, Facebook, TikTok, X (text chips, open in a new tab, `rel="me noopener"`, Umami event `social`). LinkedIn left out until the page is claimed. Same four URLs added to the Organization JSON-LD as `sameAs`.
- `favicon.ico` (16–64 px) and `apple-touch-icon.png` (180 px, navy background) generated from `img/brand/icon.png`; `<link>` tags and `theme-color` added on every page.
- Per-page Open Graph images: `img/og/about.jpg`, `img/og/workshop.jpg` (3-up composite), `img/og/site-<slug>.jpg` for the 8 site guides that have a logbook photo (others keep `og/home.jpg`). `og:image:width/height/alt` set.

## Changed
- Collection names: "Signature Dive Series" → **Signature Series**; "Certifiedish" → **Certified-ish** everywhere it is visible (headings, chips, buttons, alt text, section copy). Internal identifiers (`data-line="certifiedish"`, Umami event values, ids) unchanged so the filters and analytics keep working.
- About and Workshop nav order now matches the home page and site guides (Designs, Shirts, Dive map, Logbook, About us, Workshop, Contact).
- `width`/`height` added to every image that lacked them (hero, logbook mosaic, topside, About portraits, site-guide photos) to stop layout shift. About page image rules given `height:auto` so the CSS aspect ratios still govern.
- Logbook crops checked tile by tile at both widths: the mosaic's cover-crops were already sound; only `wall-ok.webp` got a small nudge (object-position 22% 50%) to keep the OK hand in frame.
- Phone layout: mosaic captions smaller and clamped to two lines (they covered half of the small tiles); an odd last tile now spans both columns; shirts grid is two columns with a 3:2 lead tile.

## Verified
- 0 broken internal links or asset references across all 18 pages.
- No console or page errors at 1440 px and 390 px; shirt flip + lightbox, Certified-ish filter chip and "See the dive-site plates" button all work at both widths; no horizontal overflow.
- Every image renders correctly at desktop and phone widths (screenshot pass on home, about, workshop, site guide).

## Still open (not changed in this pass)
- Launch-list form has `data-endpoint=""` so it only opens a mailto; nothing is captured server-side. A Formspree/Buttondown-style endpoint would make it real.
- 7 site guides still have no logbook photos (Bali, Blue Grotto, Blue Water Park, Dampier Strait, Navy LLCAT, Somosomo Strait, Vuna Reef) and all 15 show the "field notes are being written up" placeholder — the photo-library review will feed these once the OneDrive/iCloud folders are pinned locally.
- Workshop has no Voodoo-costume or Vehicles collections yet (named in the project brief).
- Weak logbook photos to replace from the libraries: can.webp (972×548), surface.webp (1283×677), eel.webp, eric-teal.webp; workshop: golfcart-1/2 (low-res), shelves-2/3 (backlit), habitat-1.
- Colour names in the shirts section are plain words (Light blue, Sage, Ivory…) — swap for the Comfort Colors names if you prefer.

## Shirt photo mapping (site · colour → front / back, IMG_ numbers in `shirt set`)
Black Bart · Light blue 7009/7014 · Bridge Span 14 · Ivory 7083/7085 · Blue Grotto · Aqua 7114/7120 · Dampier Strait · Yellow 7096/7103 · Rainbow River · Sage 7017/7023 · Rainbow River · Pink 7060/7061 · Thurmond Dam · Ivory 7027/7032 · The Thistlegorm · Mint 7038/7041 · Rainbow Reef · Lavender 6977/6982 · Vuna Reef · Pink 7049/7055 · set stack 7131.

## Deploy
Upload `doolittlescuba-site-2026-10-18.zip` as the site root (same structure as the Oct 9 zip). `favicon.ico` and `apple-touch-icon.png` sit at the root; everything else is under the existing folders.
