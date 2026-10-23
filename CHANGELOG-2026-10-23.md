# DoolittleScuba.com — update of 2026-10-23

## Changed
- **Certified-ish finals.** The 20 Certified-ish designs are now the finished back prints (portrait, illustration plus the Facts / Side Effects / Fine Print block), replacing the landscape copyright-filing previews. Every derivative was rebuilt from the finals with the same watermark treatment: `img/designs/cert-*.webp` (900×1240, diagonal credit watermark and footer), `custom/art/cert-*.webp` (alpha line art for the mockup, watermark baked in), `custom/t/cert-*.webp` (thumbnails of the illustration), and the 40 shop mockups in `img/certs/`. The clean 3600×4800 originals are not in the site.
- Home page: Certified-ish cards and the Certified-ish collection tile crop to the top of the art (the illustration), so the grid looks as before; the designs intro no longer calls the previews "copyright filings".
- `/custom/`: the Certified-ish back print is now the full portrait design, scaled to the torso; the full-front option shows the same design on the chest.

## Added
- `img/certs/`: 40 renders of the 20 Certified-ish designs on the tee mockup (front: plain with the DS mark along the sleeve; back: the full design), one shop colour per design. Made with `certs.py` from the `/custom/` mockup, 1200 px WebP, 0.6 MB in all. Not linked from any page: they are the product images for the Shopify catalog.

## Shopify (not part of the static site; recorded in `SHOPIFY-STORE.md`)
- The catalog is loaded as drafts: 14 Signature Series tees, 20 Certified-ish tees, 19 caps; $38 tees ($41 for 2XL and 3XL), $32 caps; three smart collections by tag. Product images come from this site's `img/shirts/`, `img/designs/`, `img/hats/` and `img/certs/`, so those paths must stay where they are.
