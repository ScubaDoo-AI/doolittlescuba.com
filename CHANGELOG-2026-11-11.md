# Change log — 11 November 2026

## Caps: embroidered site fronts in the store, 12 caps on Printful

Eric, 11 Nov (caps Project): *"Let's add the 14 front signature series shirt designs to the caps embroidery."* then here: *"Build the printful and Shopify embroidered caps."*

### Store — 19 cap products
- New front + back mockups on all 19 Dark caps: the site front (torn-edge dive flag over the site name and coordinates) embroidered, the DS mark on the side, "DO - A - LITTLE" arched over SCUBA on the back. The Mark's side and The Stack's side and back are plain, as the listings say. Old media deleted.
- Site-cap descriptions rewritten for the embroidered front (threads named per flag); tags `front:embroidered` + `site-cap` (brand caps `brand-cap`); the Site Caps and Brand Caps collections re-keyed on those tags (15 / 4). Prices unchanged. Home Port stays custom (`fulfil:custom`).

### Printful — 12 caps linked, 0 failures
- `tools/printful_caps.py` (new) plans the 12 caps whose Flexfit 6277 colour Printful stocks (Dark Navy, Dark Grey, Black, Olive); `tools/printful_link.py` gained the `caps` line and sends item-level options (thread colours, flat embroidery); the Printful link workflow lists `caps`.
- `tools/check_connections.py` now reads the 6277's printfile templates: front 5.90 × 2.00 in, side and back 2.00 × 1.00 in. The print masters in Shopify Files were built to those sizes — which forced a 0.92 × 1.00 in side mark and a straight two-line back on the Printful caps only. Sample before publishing.
- The renders live on the branch `caps-embroidered-2026-11-11` under `renders/caps-2026-11-11/` (the store imported them from there). The home page's `img/hats/dark/` and hats copy are still the 24 Oct DTF-style set — a separate pass.

Full ids, file names and the compromises: `SHOPIFY-STORE.md`, 2026-11-11.

## Evening — Eric's answers: sample staged, DTF option gone, coordinates corrected, merged
- **Price** stays $35 / $40. **Printful sample** staged as draft order 186447389 (Blue Water Park, Black, L/XL): $22.41 + $5.09 shipping + $12.40 one-time digitization + $3.21 tax = $43.11, unconfirmed. The Sample order job now takes the caps and has a `show` mode.
- **No more DTF caps:** `tools/hats_v3.py` put the embroidered-front renders in the home page deck and rewrote the hats copy and spec sheet; Home Port is embroidered to order (store tags and description updated).
- **Coordinates:** seven sites' website and store values were brought up to the chest blocks, which checked out against the ground; Dive Land Park moves from "Ider" to Glencoe, AL. 28 store descriptions and the site's own data, guides and plates updated.
- **Merged to main** (126d842), live. Open: the Navy LLCAT front reads "Hovercraft (LLCAT)".

Full ids and details: `SHOPIFY-STORE.md`, 11 Nov evening.
