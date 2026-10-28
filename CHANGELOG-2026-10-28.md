# DoolittleScuba.com — update of 2026-10-28

Apparel sync: the site, the Shopify store and the Printful edition now agree on prices and garments.

## Decisions (Eric, 28 Oct)
- Tees **$42 / $45** (2XL, 3XL) across the Signature Series and Certified-ish. Personalized tee **$47 / $48** ($50 / $51 in 2XL and 3XL).
- Garments: the plan colours wherever Printful stocks them at $15.60 (Pepper, Black, True Navy, Espresso, Moss, Violet and Ivory all are, as of the 28 Oct catalog pull); substitutes only for colours Printful does not carry — Sapphire → **Lagoon blue**, Citrus → **Butter**, China Blue → **Denim**. Signature light: Bridge Span 14 **Flo blue** and Navy LLCAT **Granite** (the Printful-edition calls of 25 Oct).
- Caps stay $35 site / $40 brand. The personalized cap moves to the **Flexfit 6277**: **$40 / $41**, S/M or L/XL.

## Changed
- **Home, the shirts deck:** price `$42 · $45 in 2XL and 3XL` (was $38 / $41). The 20 Certified-ish shirts carry the 20 Oct palette — light blue (Altitude, Boat, Buoyancy, Drift, Fish ID, Underwater Photographer), pink (Open Water), coral (Advanced Open Water), lagoon blue (Cave, Deep, Ice, Night, Search and Recovery), butter (DPV, Nitrox, SMB, Rebreather, Self-Reliant, Sidemount, Tech) — with re-dyed mockups in `img/certs/` (front, back, thumbs). Bridge Span 14 and Navy LLCAT name the garment they ship in (Flo blue, Granite) and say the photo is the sample in Caribbean blue / mustard.
- **Home, the hats deck:** default price string `$35` (was a leftover `$32`); every cap's *Make it yours* link now opens the custom page on that cap's own colour (was always navy).
- **Make it yours:** price block `base 42 · big 45 · cap 35`; intro sentence; the cap is the Flexfit 6277 fitted cap (S/M or L/XL) in its eight colours — black, navy, dark grey, brown, purple, maroon, spruce, olive — and the shirt palette gains lagoon blue, flo blue and granite. Shirts never show the cap colours, caps never show the pastels.
- Cache-busting stamps refreshed (`tools/bust.py`).

## Added
- `tools/recolour.py` — re-dyes a flat-lay shirt mockup to a new garment colour, keeping shading, the ink (black on light, white on dark) and the sleeve mark. Used for the 40 Certified-ish light mockups here and the 9 dark ones in the store.

## Not changed (open)
- Site guides for Bridge Span 14 and Navy LLCAT keep their photo captions (the photos are the sample garments).

## Later, 28 Oct — the cap mockup is the Flexfit 6277
- **Make it yours, cap mode:** the cap is redrawn as the 6277 — taller structured crown, pre-curved brim, closed fitted back with the stretch band showing (no strap, no buckle). The back tagline arch moved down to suit. Prints sit where they did.
