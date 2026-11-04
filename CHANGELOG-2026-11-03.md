# DoolittleScuba.com — update of 2026-11-03

## Added — a seventh shirt line: Aquatic Comic (59 designs, six subsets)
- **Home, shirts deck:** six deck lines, one per subset, after 1N73LL1G3NC3 — **Boat Banter** (20, as they are), **Self-Logged** (10, the wearer's name in the joke), **Buddy Check** (10, the dive buddy's name, made to give), **Buddy System** (10, two names, a matching pair), **Till Surface Do Us Part** (6, husband and wife), **Master Class** (3, two Master Scuba Divers). Every card opens on the back (the joke), with the front (DS mark over the slogan, left chest) and the watermarked chest-and-back preview; the panel lists Front / Back / Shirt / Ink / Price ($42 / $45 as they are, $47 / $50 with names). Mockups of the personalized designs carry sample names (Sam, Alex, Mike and Lisa).
- **Garments (dark palette, all stocked at Printful at $15.60 S–XL):** Boat Banter alternates True navy (odd) and Black (even); Self-Logged Graphite; Buddy Check True navy; Buddy System Black; Till Surface Do Us Part Graphite; Master Class Black. Chosen as the three Printful darks where PMS 485 red still reads (Black 3.5:1, True navy 2.9:1, Graphite 2.4:1 against Printful's swatches); white is 12–17:1 on all three.
- **Collection tile** "Jokes told on the dive deck" (Aquatic Comic · 59 designs) after the 1N73LL1G3NC3 tile, with a link per subset; collections intro now "Five lines, one hand."; shirts and designs intros mention the line.
- **Designs grid:** 59 "Art finished" cards (`data-line="aquatic"`), chip **Aquatic Comic**; counts recomputed (All 161 · Coming soon 6 · Art finished 153 · In progress 2).
- **Files:** `tools/aquatic_designs.json` (the 59 designs, red words marked `*…*`, name slots `{N}` `{A}` `{B}` `{H}` `{W}`), `tools/aquatic_print.py` (the 300-dpi Printful masters, and one customer's files: `order W03 <out> --name Sam`), `tools/aquatic_render.py` (mockups on the Off-World blank, previews), `tools/aquatic.py` (this patch, idempotent; run `tools/bust.py` after). Images `img/aquatic/` (236 files, 2.4 MB), `img/designs/ac-*.webp`, `img/lines/aquatic-tile.webp`. The print masters are not in the repo.

## Shopify and Printful
- **59 Draft products** in Shopify, one per design. SKU `DS-AC<code>-TD-<size>`, prices $42 / $45 (Boat Banter) and $47 / $50 (personalized). Each has the site's back, front and preview images.
- **Seven smart collections:** Aquatic Comic plus one per subset.
- **Name fields:** the personalized tees use the `product.personalized` template on the unpublished theme "Horizon — Doolittle Scuba". It shows the required name fields (one name, two buddies, or husband / wife), which ride the order as line-item properties.
- **Print masters:** the 40 Boat Banter masters (AC-S01…S20 front and back, 3600 × 4800, 300 dpi) are in Shopify Files.
- **New `tools/printful_aquatic.py`:** the Printful plan and cost table. `tools/printful_link.py` gains an `aquatic` plan that links S01–S20, front and back at full area.
- **Personalized orders** are made by hand: `tools/aquatic_print.py order <code> <out> --name … [--name2 …]`, then a Printful order.
- **Self-locating scripts:** `aquatic_print.py`, `aquatic_render.py` and `printful_aquatic.py` find the design list (and `assets/`) next to themselves, so the copies in the print package run on their own.
- **New `tools/aquatic_order.py`:** one command per personalized order. It goes from the Shopify order to a Printful draft through Printful API v2: names from the line-item properties, masters rendered, uploaded to Shopify Files, draft order created, costs printed. `--dry-run` shows the plan, and `--confirm-id` confirms a checked draft.
- **`tools/printful_link.py --only aquatic`:** now also marks the personalized products' sync variants ignored.
