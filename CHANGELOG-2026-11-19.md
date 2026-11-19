# Changelog — 19 Nov 2026

## The pulled card turns its garment in 3-D (all apparel decks)
Eric (iPad screenshot of the collections deck, the grey box round the 1N73LL1G3NC3 mockup marked, "rotating"): *"Can we make the shirts rotating 3-D model in the scrolling setup we have for all apparel?"* Then: *"Look at Printful models and Shopify, they appear better."*

- **Turn:** the card pulled forward in a deck (collections, shirts, caps, organic) shows the front, turns, holds on the back, turns back: an 8 s loop (`@keyframes dkturn`), starting 0.6 s after the card is pulled so running across the tabs doesn't flicker. The second face is a 600 px thumb (Shopify CDN `&width=600`, local `-t` file) loaded only when the card is first pulled. A card with one image sways ±18°. Sticker packs stay still (`spin:false`). Reduced motion: no turn.
- **No grey box:** `.dk-pic` lost its `#E6ECEE` fill; the Printful mockups are transparent, so the shirt sits on the card with a faint spotlight.
- **Collections deck:** each collection card now has a back face (`data-back`); the organic card uses the Printful Thistlegorm organic dark mockup from Shopify instead of the old render.
- Code: `js/deck.js` (`thumbOf`, `spinPic`, `wake`), `css/site.css` (`.dk-spin`, `.fc`). Checked by script at 1440 px, light and dark, home page and `/signature/`; no console errors.

## Still on the old renders (spin as a light tile until moved)
Certified-ish (light, dark, organic), Off-World Hunt Club, Surface Interval, caps and beanie: the same old renders in Shopify and on the site. Next: Printful read `mockup:` runs for those lines, `fileUpdate` in Shopify, site links to the CDN copies, as was done for Signature and 1N73LL1G3NC3 on 18 Nov.

## Later — the sleeve shows, caps and pairs on Printful's own mockups
Eric: *"Shoulder design should show if present. Shopify bundle images are badly done as well as some caps poor cutouts of actual photos."*

- **The turn now has three views.** A pulled card swings each view in, holds it ~2 s, and swings it out as the next comes in (`dkv2` / `dkv3` in `site.css`): **front → right sleeve → back** when the garment has a sleeve or side print (`data-sleeve` on the figure's button), front ↔ back otherwise. The open panel gains a **Sleeve** (caps: **Side**) view. `data-side` was already taken by the photo grid's front/back state, hence `data-sleeve`.
- **Signature Series (28 tees, light and dark):** Printful's right-sleeve mockup, the signature shark at the bottom of the sleeve (its 18 Nov placement), in `img/sleeves/` and `img/sleeves/dark/`. Printful read runs #24, #26, #27.
- **Caps (17 of 19):** the photo cutouts and flat drawings replaced by Printful's own Flexfit 6277 mockups: front, left side (DS mark), back ("Do a little scuba"), in `img/hats/pf/`. Run #28 (Bali), #29 (the rest). Still on the old images: **The Stack** (Printful returned only the front) and **Home Port** (not in the Printful caps plan). The beanie keeps its photo.
- **Pairs (28 Shopify products):** new image per pair: the Printful tee front beside the Printful cap on the brand navy, 2000 × 1200 (`img/pairs/`, built by compositing; source for Shopify). Replaced in place with `fileUpdate` (same media ids), alt text updated. Checked on the Shopify CDN.
- **`tools/printful_read.py`:** sends the plan's embroidery options (thread colours), maps the cap front to `embroidery_front_large`, waits out the mockup generator's ~10-a-minute limit, and one failing spec no longer stops the run.

### Still to do
- Organic Signature tees (`DS-xxx-TO-M`, `-TDO-M`): same sleeve run.
- Certified-ish (its DS mark runs along the sleeve), Off-World, Surface Interval: still old renders; moving them to Printful mockups gives them the sleeve view too.

## Afternoon — 1N73LL1G3NC3 sleeves, Certified-ish on Printful, the safeguard
Eric: *"What's next in getting the system updated with the new renders from Printful"* → the plan → *"Yes"* to 1N73LL1G3NC3 sleeves and Certified-ish.

- **Printful read #30** (76 mockups, one run; the job's limit is now 30 minutes): 36 1N73LL1G3NC3 tees (right sleeve) and the 40 Certified-ish tees (front, back, right sleeve), no failures.
- **1N73LL1G3NC3:** the DS mark on the right sleeve, `img/sleeves/n73/`; the deck turns front → sleeve → back.
- **Certified-ish (light and dark, 40 tees):**
  - Shopify: the front and back image of each of the 40 regular products replaced in place with the Printful mockups (`fileUpdate`, 80 images, same media ids), alt text names the Printful garment colour. The 40 organic Certified-ish products are not touched yet.
  - Site: `certified-ish/index.html` points at the Shopify CDN copies (thumb `&width=600`), sleeves in `img/sleeves/certs/` and `certs/dark/`; the card turns back → front → sleeve (DS mark along the sleeve). The home Certified-ish collection card uses the Printful Night Diver. The old `img/certs/` zoom rule now applies only to the old renders.
- **Safeguard:** `tools/printful_images.py` + `tools/printful_images.json` (189 figures). `bust.py` now applies it before stamping (and stamps `data-sleeve`), so re-running an old builder (`n73.py`, `certdark.py`, `line_pages.py`, `hats_v3.py`, ...) can no longer put old renders back. After converting a line: `tools/printful_images.py capture`.

### Next
Off-World Hunt Club (60), Surface Interval (59), the organic line (223), the 17 caps' Shopify images, The Stack / Home Port caps and the beanie.

## Later — Off-World Hunt Club and Surface Interval on Printful
- **Printful read #31** (119 specs; the job limit is now 60 minutes): all 60 Off-World tees and the 20 Boat Banter tees rendered. The 39 personalized Surface Interval tees (Self-Logged, Buddy Check, Buddy System, Till Surface, Master Class) have no Printful sync variant (they are made to order with the buyer's names), so Printful can't mock them from the plan; they keep their current images.
- **Shopify:** 160 front/back images replaced in place (`fileUpdate`, same media ids): 60 Off-World, 20 Boat Banter. Off-World light tees got new alt text; the rest keep theirs.
- **Site:** `off-world/index.html` (60) and `surface-interval/index.html` (20 Boat Banter) point at the Shopify CDN copies; both turn back → front. The home Off-World and Surface Interval collection cards use the new images. `printful_images.json` recaptured (now covers these too).

## Later still — the family on the personalized tees, the caps in the store
Eric: *"Create these using our family names as the sample names. Allie, Eric, Jade, Mason, and the caps."* *"Married shirts husband Eric, wife Allie, son Mason, daughter Jade."* *"Eric's an air hog, Allie is not."*

- **The 39 personalized Surface Interval tees** now carry the family: Till Surface Do Us Part and Master Class are Eric & Allie; Self-Logged and Buddy Check rotate Eric, Allie, Mason, Jade; Buddy System pairs them. The air jokes are pinned: Allie breathes like a camel (W01), Eric is the vacuum (R02), Allie has the air and Mason the snacks (B04), Allie breathes slow and Eric needs a tank for the story (B05); the Octo tee already reads Allie 2000 psi, Eric don't ask. `tools/aquatic_family.py` writes the print masters to `renders/aquatic-family/` (+ `names.json`); `printful_read.py mockup:aquaticfamily:<SKU>` renders them on Printful's tee (run #32, no failures).
- **Shopify:** the 78 front/back images of those 39 products replaced in place, alt text with the family's lines. The product descriptions (how the names work) are unchanged.
- **Site:** the 39 cards on `surface-interval/` use the new images and their captions name the family. The watermarked art previews (designs grid, "The art" view) still show the old sample names.
- **Caps in the store:** the 17 dark caps' front/back images in Shopify replaced with the Printful renders (from `img/hats/pf/`). **The Stack** rendered this time (front, side, back): in Shopify and in the caps deck. **The beanie**'s Shopify image is now Printful's mockup; the site's beanie card keeps its photo. **Home Port** is still not in the Printful caps plan.
- **Art previews:** the 39 watermarked previews (`img/designs/ac-*.webp`, the designs grid and the "The art" view) rebuilt from the family print masters with `aquatic_render.preview`; the designs-grid captions now match the shirt cards. No Sam, Alex, Mike or Lisa left on `surface-interval/`. The organic Surface Interval mockups on `organic/` still carry the old names (part of the organic line move).

## Home Port cap on Printful (sample: Newnan)
- **Sample front:** `renders/caps/DS-HMP_Newnan_PF-cap-front_2.96x1.99in_white-red.png`: the site-cap layout (Rainbow River's dive flag, Almendra Bold, white + red at 300 dpi, 1.99 in tall) with Newnan, 33°22.842'N 084°47.982'W. Home Port stays made to order with the buyer's port; this is only the sample.
- **Printful read #33** (`mockup:homeport:DS-HMP-CD-SM`, new spec in `printful_read.py`: Rainbow River's black 6277 plan with the Newnan front): front, side (DS mark), back (Do a little scuba), three-quarter views.
- **Shopify (Home Port — Dark cap):** its four images replaced in place: front, left side, back, three-quarter; alt text says the Newnan front is a sample.
- **Site:** the Home Port card in the caps deck turns front → side → back (`img/hats/pf/cap-dark-home-port-*`). All 19 caps are now on Printful's mockups.

## The organic line on Printful (all 242 products)
- **Printful read #34 and #35** (121 + 122 mockups, no failures): every organic edition rendered on its own Printful blank from the plan in `organic.py` (Stanley/Stella organic tees, Econscious organic caps, the Atlantis beanie in black and oxford navy). The 39 personalized organic Surface Interval tees use the family print masters (new `mockup:organicfamily:<SKU>` spec), so they read Eric, Allie, Mason and Jade like the regular ones.
- **Site (`organic/`):** the images in `img/organic/<line>/` replaced in place (same file names, new content hashes on the cards). 120 cards gained a third view: the right sleeve on Signature, Certified-ish and 1N73LL1G3NC3, the DS mark side on the caps. The re-dyed renders (`organic_mockups.py` / `organic_redye.py`) are retired; do not rerun them.
- **Shopify:** all 484 organic product images replaced in place (`fileUpdate`, same media ids), sourced from the site copies with their hash so the Porkbun CDN can't hand Shopify a stale file. Image order kept per line (front first: Signature, 1N73LL1G3NC3, caps; back first: Certified-ish, Off-World, Surface Interval; beanie: black, then navy).
- Runs are now started from the session with `gh api .../actions/workflows/printful-read.yml/dispatches` and read back with `gh run view --log`; no browser needed.

Every apparel product on the site and in the store is now on Printful's own mockups.
- **The Mark beanie (home page caps deck):** the drawn render replaced by Printful's mockup (the same image as its Shopify listing), `img/hats/pf/beanie-the-mark-french-navy*.webp`. With that, every product card on the site shows a Printful image (the jackets were already Printful's model mockups). Live check: every line page served by doolittlescuba.com matches the repo.

## Shop (shop.doolittlescuba.com): the collection deck replaces the mixed grid
Eric: *"I dislike the mixed grid view; this needs to be easily navigable and better aesthetically."* *"Signature Series should be the first on every product stack… or use the same display we designed for DoolittleScuba.com."*

- **New theme section "Collection deck"** (`sections/ds-deck.liquid` + `snippets/ds-deck-cards.liquid`, theme *Horizon — Doolittle Scuba (Home Port map v2)*): the site's deck in Shopify. Collection tabs (Signature Series first, then Certified-ish, 1N73LL1G3NC3, Off-World Hunt Club, Surface Interval, Caps & beanies, Organic, Jackets, Stickers); each tab a stack of spines named by design and tinted by garment colour; the pulled card shows the tag (line, name, colour, price, View) and fades front ↔ back. Within every tab the Signature Series products come first. Organic editions are hidden outside the Organic tab (section setting), so each design appears once. Tabs, collections and limits are editable in the theme editor.
- **Home page:** "The shirts" grid replaced by the deck (16 cards a tab, then "All N →"). The old product list is switched off, not deleted.
- **Catalog and every collection page** (`templates/collection.json`): the deck instead of the grid; on a collection page the tabs are links and the whole collection is in the deck. The old heading and grid sections are switched off, not deleted.
- **Main menu:** "Catalog" → **Shop**, with the collections underneath in the same order, Signature Series first, and "Everything".
- Committed to the live theme; **not published yet** (waiting for Eric's yes). The publish also carries two earlier unpublished files (the Home Port picker block and its product template).
