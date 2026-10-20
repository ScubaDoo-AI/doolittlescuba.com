# DoolittleScuba.com — update of 2026-10-20

Builds on the 2026-10-18 rework (see `CHANGELOG-2026-10-18.md`). This pass pulls the day's parallel web work into one package: the on-model shirt catalog, and the About and Workshop pages rebuilt in the other chats.

## Added
- **Shirts section rebuilt from the catalog** (`#shirts` on the home page): all 14 sites with a shirt, each photographed on the shirt, front and back, from the 28-image catalog run (`DS-<code>_<site>_front/back.jpg`, 2048 px squares). Cards keep the Front/Back flip, lightbox, status pill and site-guide link. Order follows the site data (available sites first). 56 WebP files in `img/shirts/` (`<slug>-front.webp`, `<slug>-back.webp` at 1200 px, `-t` thumbs at 600 px; 2.8 MB total), a plain four-across grid. The 10 studio-set sample images and the folded-set lead tile from 10-18 were removed, so `img/shirts/` now holds only the catalog.
- **Designs grid now shows the watermarked copyright filings** (`#designs` on the home page): the ten flat-shirt photos that stood in for the dive-site plates are gone; all 14 plates (and now all 20 Certified-ish backs) use the watermarked artwork from `Apparel\Shirt Set Photos\Modeled\Catalog\plates_watermarked\` (the filed drawings with the "© 2026 John Eric Doolittle Jr. · Doolittle Scuba L.L.C." watermark). 34 previews in `img/designs/` as 4:3 WebP (1040×780, letterboxed so no labels are cropped; 2.8 MB), replacing the 28 JPEGs. Two Certified-ish designs that were in the filing but not on the site were added as cards: Cave Diver and Tech Diver (counts now All 36 · Available 6 · Art finished 28 · In progress 2; Certified-ish 20). Kioa Island keeps its "Preview coming" tile. The collection tiles (Blue Grotto, Night Diver) use the same previews, and the plate figure on all 14 site guides shows the filed plate (the four guides that had "Plate preview coming" — Bali, Blue Water Park, Navy LLCAT, Somosomo Strait — now have one). Three plate cards that read "Dive-site plate" under the name now show the location like the others.
- **Nothing says "Available" any more** (the shop is not open yet): the six first-release sites are labelled **Coming soon** everywhere — the designs grid pills and filter chip, the shirts cards (was "First release"), the site-index tags under the dive map, the map popups (`js/divemap.js`) and the six site-guide status pills; the guide button "Get the first-release email" is now "Get the launch email". Internal status keys (`available` in the filters, site data and Umami events) are unchanged, so nothing else moved. The other eight shirts keep "Sample print"; designs keep "Art finished" / "In progress".
- **Shirt photos on every site guide**: the 14 guides with a shirt now show the front and back photo at the top of "On the shirt" (`.shirt-photos`, square tiles, `srcset` 600/1200). Kioa Island (in progress) is unchanged.
- **About page**: today's rebuild merged in (`/about/`). Six new photos in `about/img/` (dive park bench hero, Fiji boat, quarry dock, Fiji village, Giza, Allie off Taveuni); the portrait webp files it reuses stay in the shared `img/`. New OG image `img/og/about.jpg` (Fiji boat deck, 2024).
- **Workshop page**: today's rebuild merged in (`/workshop/`): 12 projects, 2010 to now (Queen Anne's Revenge, reef tanks and the stone stand, skull and horn mounts, the truck, drones and FPV, fireworks, cedar slab table, dog couch, reptile habitat, live-edge shelves, family key holder, drawing) plus the custom-piece request form (mailto). 228 photos in `workshop/img/` (WebP; full-size capped at 1200 px for the lightbox, 640 px thumbs; 23 MB) replace the old 58-file set. New OG image `img/og/workshop.jpg` (cart, mounts, reef tank).

## Changed (merge details for the two artifact pages)
- Both pages were published as Claude artifacts; the merge strips the artifact wrapper and rebuilds the `<head>` to match the rest of the site: `lang`, canonical, Open Graph tags, favicon / apple-touch-icon / theme-color, fonts, then the page's own CSS. Umami loader added to both (the artifact copies had the event attributes but no loader).
- Nav links rewritten from absolute `https://doolittlescuba.com/#…` and artifact URLs to `/#designs`, `/#shirts`, `/#map`, `/#logbook`, `/about/`, `/workshop/`, `/#contact`; brand assets point at `../img/brand/`. No `claude.ai` links remain.
- Shirts intro copy and the colour note updated for the catalog. Garment colour names (plain words): Black Bart light blue · Bridge Span 14 Caribbean blue · Blue Grotto mint · Blue Water Park teal · Dampier Strait butter · Bali terracotta · Rainbow River sage · Navy LLCAT mustard · Dive Land Park aqua · Thurmond Dam ivory · The Thistlegorm berry pink · Somosomo Strait coral · Rainbow Reef lavender · Vuna Reef pink. Swap for the Comfort Colors names if you prefer.
- `sitemap.xml` lastmod set to 2026-10-20 for home, about, workshop and the 14 shirt site guides.

## Verified
- 0 broken internal links or asset references across all 18 pages; no duplicate ids; JSON-LD parses.
- No console or page errors, no horizontal overflow, no broken images on any of the 18 pages at 1440 px and 390 px.
- Shirt flip + lightbox, Certified-ish filter chip and "See the dive-site plates" button work at both widths. Shirts grid, About intro, Workshop top and a site guide's shirt block checked by screenshot at both widths.

## Still open
- Launch-list form still has no endpoint (mailto only); the Workshop request form is mailto as well.
- 7 site guides still have no logbook photos; the "field notes" placeholder is still on all 15 (photo-library review pending the pinned OneDrive/iCloud folders).
- Porkbun's zip uploader caps at 40 MB, so the Workshop full-size photos were dropped to 1200 px (lightbox only; thumbs unchanged). Beyond this, use FTP or GitHub Connect rather than shrinking photos further.
- Workshop has no Voodoo-costume or Vehicles collections yet (the truck is in).
- Umami dashboard review still needs you signed in to the browser pane.

## Deploy
Upload `doolittlescuba-site-2026-10-20.zip` as the site root (same structure as before; 431 files, 36 MB — under the 40 MB zip-uploader cap). Everything under the existing folders; `favicon.ico` and `apple-touch-icon.png` at the root.
