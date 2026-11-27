# Changelog — 26 Nov 2026

## Header menu cut from 13 links to five (Eric 13:08: "Complete #1")
- **Before:** Collections, Hats, Jackets, Rash guards, Stickers, Towels, Custom, Dive map, Logbook, About us, Workshop, Contact, Cart. Two ways of sorting (by line, by product type) and the story pages were mixed in one row.
- **Now:** **Shop ▾ · Dive sites · Custom · Our story ▾ · Cart**
  - Shop opens two columns. *By collection:* All collections, Signature Series, Certified-ish, Off-World Hunt Club, 1N73LL1G3NC3, Surface Interval, Organic. *By gear:* Rash guards, Caps, Jackets, Stickers, Towels.
  - Our story: About us, Logbook, Workshop, Contact.
  - "Dive map" is now labelled **Dive sites** (same link, `/#map`).
- The current page is lit: Shop on collection, gear and organic pages (with the page bold in the drop-down); Dive sites on every site guide; the page itself under Our story.
- The drop-downs are `<details>`, so they open without JavaScript. `js/nav.js` keeps one open at a time and closes them on an outside click, on Escape (focus back to the label) or when a link is chosen. On phones the panel spans the menu's width, and the five items fit on one line at 390 px.
- **Analytics:** inner links keep their old Umami events (nav-collections, nav-hats, nav-jackets, nav-rashguards, nav-stickers, nav-towels, nav-custom, nav-map, nav-logbook, nav-about, nav-workshop, nav-contact, nav-cart). New: nav-shop and nav-story (opening the drop-downs), and nav-signature, nav-certified-ish, nav-off-world, nav-n73, nav-surface-interval and nav-organic.
- **One source:** `tools/site_nav.py` (new). `tools/line_pages.py` `nav()` now calls it. `css/nav.css` and `js/nav.js` (new) are linked from all 28 pages with a header menu. The home page menu's label changed from "Sections" to "Site", like every other page.
- Checked locally, in Chrome at 1280 px and 390 px: home, Signature, Black Bart guide and About.
- **Not changed:** the Shopify theme's own header on shop.doolittlescuba.com; the home page sections and their order (that is item #3 of the 26 Nov review).

## Each site guide is now the place to shop that site (review item #2)
- New **"Wear <site>"** strip on all 14 site guides, right under the intro and above "The site". It shows 8 cards: light tee, dark tee, cap, rash guard (light), rash guard (dark), organic tee, organic dark tee, organic cap.
- Each card: photo, kind, name, price ("from $42", "$38", "from $39 · 5 cuts"), "Coming soon". The photo and name link to the product in the store; the rash guards link to `/rash-guards/` for the five cuts. Each card carries `data-buy`, so the site cart gives it a size picker on the page once `LIVE=true`.
- Prices come from `js/catalog.json` (Shopify, daily); photos come from the cards already on the site. Nothing is typed by hand. Tool: `tools/site_shop.py` (markers `WEAR:START/END`). Kioa Island has a guide but no products, so it has no strip.
- Umami: `guide-wear` with `item` = the SKU stem.

## Home page as a short guided path (review item #3)
- **New order:** hero → **Start here** → The collections + search → **Shop by dive site** (the map) → **Make it yours** → Every mark by hand → About → Logbook → Wear it where you dove → Topside.
- **Start here** (new): eight picks, one per line: Black Bart tee, Night Diver tee, Cloaked tee, Trust But Test tee, Current tee, Thistlegorm rash guard (dark), Vuna Reef cap, and the Achievement Unlocked set. Each card shows photo, line (linked to its page), name, price and "Coming soon", and links to the store product. `data-buy` is on each card, so the site cart adds pickers when live. Umami: `home-pick`, `home-pick-line`. To change a pick, edit `PICKS` in `tools/home_layout.py` and re-run.
- **Make it yours** (new): a short pitch, the Home Port cap photo, buttons to /custom/ and the Home Port cap ($48, from the catalog). Umami: `home-make`, `home-homeport`.
- **The dive map** is retitled **Shop by dive site**. Its line now says a site's guide holds everything made for that site.
- Hero second button: "See the collections" → **"Start shopping"** (to #start).
- **Moved off the home page:** the hats deck → **/caps/**, the jackets → **/jackets/**. Each new page has its own hero with the same cards and deck config. The sticker strip is gone (all of it is on /stickers/; the Achievement set is a Start here pick). Menu: Shop → Caps / Jackets now go to the new pages. Both new pages are in the sitemap.
- **Tools re-pointed to caps/index.html:** `pairs_site.py`, `caps_printful_colours.py`, `hats_v2.py`, `hats_v3.py`, `site_shop.py`. `stickers_page.py` skips the home page when it has no #stickers section. The organic page's link to the caps → /caps/.
- Checked locally: no script errors on /, /caps/, /jackets/, a guide and /stickers/; the caps deck builds on /caps/.

## Shop words on what you buy, workshop words on the art (review item #4)
- **Rule:** anything a visitor can buy says "Coming soon" (the cart's own label once live). "Art finished", "In progress" and "Sample print" stay only in the art grids and on a site with nothing for sale yet (Kioa Island).
- **Sites:** the 8 sites marked "finished" (Rainbow River, Navy LLCAT, Dive Land Park, Thurmond Dam, Thistlegorm, Somosomo Strait, Rainbow Reef, Vuna Reef) now read **Coming soon**. That covers the home page site list, the map pins, the guide header pills and the sites data on the Signature and rash-guard pages. All 14 sites with products now say Coming soon; Kioa Island stays "In progress".
- **Signature shirts:** the 8 shirt cards that said "Sample print" say **Coming soon**. The open card's button in `js/deck.js` no longer switches to "Sample print".
- **Collection pages** (Signature, Certified-ish, Off-World, 1N73LL1G3NC3, Surface Interval): "The designs" is now **"The art"** and sits after "Wear it your way". Order: The shirts → Wear it your way → The art → The other collections. The art grid keeps its status filter (Art finished / In progress). Search links (`#d-<slug>`) are unchanged.
- Tool: `tools/shop_status.py` (new, idempotent). `tools/line_pages.py`'s template has the new order and heading too. **Note:** re-running `line_pages.py` on today's pages is not a no-op; it rewrites the five pages (drift from later hand edits). Check its diff before committing a rebuild.

## Real photos: ready to swap in (review item #5)
- Samples are due 26–28 Nov. When photos arrive, save them as `img/real/<SKU stem>.webp` (e.g. `DS-BBT-T.webp`) and run `tools/site_shop.py`, `tools/home_layout.py`, `tools/bust.py`. The guide "Wear" strips and the Start here picks then use the real photo instead of the mockup. Details in README, "Real photos".
- The collection tiles, decks and the Shopify product photos are not covered yet; they still need their own swap.

## The store (shop.doolittlescuba.com) brought in line (Eric 15:31: "Update the shop page to be in alignment with these moves")
- **Main menu** (store data, `main-menu`, live immediately). It was Home · Shop (13 links) · Contact; it now matches the site:
  - **Shop** ▸ *By collection:* Signature Series, Certified-ish, Off-World Hunt Club, 1N73LL1G3NC3, Surface Interval, Organic, Everything ▸ *By gear:* Rash guards, Caps & beanies, Cap & tee pairs, Jackets, Stickers, Hand towels
  - **Dive sites** → doolittlescuba.com/#map
  - **Custom** → /collections/custom
  - **Our story** ▸ About us, Logbook, Workshop (all on doolittlescuba.com) and Contact (/pages/contact)
  - The theme's cart icon is the Cart. "Home" is gone; the logo goes home. "(off topic)" is dropped from the 1N73LL1G3NC3 and Off-World labels, as on the site.
- **Product pages** (theme "Live 21 Nov + three-view turn", `sections/ds-series-tabs.liquid`): every product tagged `site:<slug>` now shows **"Everything for <site> on DoolittleScuba.com →"** under the back link. It opens that site's guide, where the new Wear strip holds all its products. The text and address are section settings ("Dive-site link"), and the site name is the product title before " — ". Committed and **published 26 Nov 15:38** (Eric: "Publish").
- No workshop status words were found in the theme. The deck and series tabs already had rash guards.
- Repo mirror `shopify-theme/sections/ds-series-tabs.liquid` now matches the theme byte for byte. It had been missing the 25 Nov rash-guards tab, and it carried one comment line the theme does not have.

## Gooten added as a second fulfilment provider (Eric 16:34 / 19:14–19:19: "complete the setup", "Setup all branding options allowed", "Need a red garment label")
- **Store connected:** Gooten account (login orders@doolittlescuba.com) linked to x00ytr-y9.myshopify.com through the Gooten Shopify app, Gooten store id 102736. **Import Products was unticked**, so none of the Printful products were pulled into Gooten. Shopify now lists three fulfilment services: Manual (Shop location), Printful, **Gooten** (location "Gooten", active).
- **Order hold:** Gooten has no merchant manual-approval switch (new partners' first orders are reviewed by Gooten's own team as "Needs Manual Approval"). Set **Pending Time = 12 hours** (Settings → Fulfillment), matching the 12-hour typo window in the store policies. "Hold items for personalization" left off. Return address: business address (default).
- **Branding (Settings → Add-ons):**
  - Packing slip: store name *Doolittle Scuba*, DS mark navy + red logo (348 px square, trimmed from `DS_mark_PF-sleeve-right_3.5x4in_NAVYRED.png`), message *"Thanks for diving in with us. Do a little scuba!"*, website doolittlescuba.com, help contact **sales@doolittlescuba.com** (after-sale address, per the 17 Nov email split).
  - Neck labels (2.5 × 1 in, 750 × 300 px), built from the Shopify Files DS mark and the cap wordmark; pick the matching one per garment colour when creating Gooten apparel:
    - **DS Neck Label - Light garments**: navy + red.
    - **DS Neck Label - Dark garments**: white + red.
    - **DS Neck Label - Red garments**: all white (the red would vanish on a red shirt).
  - Profile company logo: same DS mark.
  - **Not installed:** Gooten's automated order and shipping confirmation emails. Shopify already sends both, so turning these on would send customers duplicates.
- **Still Eric's:** add a billing card in Gooten (Settings → Billing) before any order can be produced. No Gooten products created yet; the product lines for Gooten are still to be decided.
- **Note:** existing automations (`custom_fulfil.py`, the custom shipping profiles) are Printful-only. A Gooten product needs its own shipping profile at the Gooten location before it goes on sale.

## Review re-run, evening (Eric 21:13 "Rerun the overall review"; 21:18 "Go with 2-5 skip linkedin")
**Findings:**
1. Plain `doolittlescuba.com/` fetched as the old homepage (old menu, hats/jackets/stickers). With `?probe=` it is current, and guides and `/caps/` are current. So it is a cache on the root URL; Eric to check in a private window and clear Porkbun's cache if needed.
2. The store's homepage had no starting point.
3. The store's footer signup was headed "Surface interval", the same as the line.
4. Pairs were in the store menu but not on the site.
5. LinkedIn is not set up yet (skipped).
6. Kioa Island is the only dead end under Shop by dive site.
7. Real photos and the line_pages drift carry over.

**Done (2–4):**
- **Site menu:** Shop ▸ By gear now has **Cap & tee pairs** → `shop.doolittlescuba.com/collections/pairs` (Umami `nav-pairs`). Applied to all 30 menu pages via `tools/site_nav.py`.
- **Store collection "Start here"** (new, `start-here`, gid 494422327482): manual order, published to the Online Store. It holds the site's eight picks in the same order: Black Bart tee, Night Diver tee, Cloaked tee, Trust But Test tee, Current tee, Thistlegorm dark rash guard (men's LS), Vuna Reef cap, Achievement Unlocked set. Change the picks in admin under Collections → Start here.
- **Store homepage** (`templates/index.json`): order is hero → **Start here** (the old, disabled product-list section re-enabled, pointed at `start-here`, 4 across, heading in the same style as "The shirts", no View all button) → The shirts deck. The hero gets a second button, **Shop by dive site** (white) → `doolittlescuba.com/#map`, set beside "See the shirts" (hero alignment flex-start).
- **Store footer** (`sections/footer-group.json`): "Surface interval" → "Get launch news" was **not published**. Every publish that carried the footer file was refused as "changed on Shopify outside this tool". Shopify's copy (updated 22 Nov) still reads "Surface interval", and the cause of the mismatch wasn't visible, so it was not forced. **Eric:** change it in the theme editor (Customize → Footer → the "Surface interval" text block). The tool's copy was put back to "Surface interval"; it may still be listed as waiting to publish. **Update 22:23:** Eric changed it in the theme editor, so "Get launch news" is live (saved as `<h1><strong>…`). The tool's queued copy was replaced with his saved version (commit 654f16a) and is identical; the publish tool still refuses the file, so it stays queued with no effect.
- **Published 22:1x** (Eric 22:11 "Yes"): the homepage (Start here + Shop by dive site button). The first try was refused because the unused "View all" button block was still in the file but not in its block order; the block was deleted. Checked by screenshot at 1440 and 390 px before publishing.

## Kioa Island: logbook only (Eric 22:15 "Hide Kioa for now"; 22:18 "Leave photos intact only remove references to the art")
- The first pass hid the whole site (commit a0f2045). It was **reverted** (13cdfca), and then only the art came off (14de958). Kioa stays a dive site with its photos: the guide page (photo, The site, From our logbook), map pin, home site list row, guide pager and sitemap are all kept.
- **Art removed:**
  - its card in the Signature art grid ("The art")
  - its design search entry (`js/designs.json`)
  - on its guide: the "In progress" pill, the "Tell me when it's finished" button and its line about the release, the "On the shirt" section, and "drawn for the Doolittle Scuba line" in the page description (now "Photos and field notes from our logbook.")
- **New status "logbook"** in the sites data (home, Signature, rash-guard and Kioa pages). The map popup says **Logbook** (`js/divemap.js`), and the home site list row is tagged **Logbook** in the muted colour (`.tag.logbook` in `css/site.css`), not "In progress".
- **Tool:** `tools/logbook_sites.py` (new, idempotent; `LOGBOOK = {'kioa-island': 'Kioa Island'}`). To bring the art back, take the slug out and revert its commit. Re-run it after `tools/line_pages.py`.
- Checked locally: no script errors on /, /signature/, /rash-guards/, the Vuna Reef and Kioa guides; the Kioa guide checked by screenshot.

## Store: Start here page and footer heading tag (Eric 22:31 "Check heading tag and fix start here page")
- **Start here page** (`/collections/start-here`, theme `snippets/ds-deck-cards.liquid`): the deck hid rash guards everywhere but the Rash Guards collection, so the page showed 7 of the 8 picks. It now shows them on `start-here` too. The "From" price (the lowest of the five cuts) is now worked out only on the Rash Guards collection, so the Thistlegorm card here shows its own $69, not a misleading "From $69". Checked by screenshot: Start here shows 8 designs; Rash Guards still shows "From $39.00", 28 designs. **Committed, waiting for publish.**
- **Footer heading tag:** Eric's 22:23 editor save stored the heading as `<h1><strong>Get launch news</strong></h1>`, a second h1 on every store page. Recommended fix: theme editor → Footer → that text block → Heading 2, bold off. The publish tool refuses every footer edit, because the file changed on Shopify (Eric's save) after the tool loaded the theme, so this one is Eric's to make in the editor.
- To keep the footer from blocking other publishes, the tool's queued footer copy was set back to the exact copy it loaded (md5 b3833a74, the same as the 22:1x publish that went through). The tool refuses rather than overwrite a file changed on Shopify, so Eric's live footer is safe either way.
- Repo mirror `shopify-theme/snippets/ds-deck-cards.liquid` is stale (it predates the 25 Nov rash-guard deck work) and was not patched. A full re-sync from the theme is due.

## Start here fix published; every product image on the dark DS wallpaper (Eric 22:47 "Publish and update the printful images with the new backgrounds")
**Start here page live (22:50).** The publish tool still refused the whole theme over the footer file. So `snippets/ds-deck-cards.liquid` went out alone through **Actions → Theme push** (dry run, then apply; the old copy is in that run's artifact). Shopify's file now has md5 5fc02055, the fixed version. The repo mirror `shopify-theme/snippets/ds-deck-cards.liquid` was synced to it, and is no longer stale.

**Dark backgrounds** (samples approved 22:33–22:47: every product image, subtle tile, samples first):
- **Look:**
  - store navy #0E1B33 (the theme palette background)
  - DS marks tiled at about 7.5% of the image width in #1B2C4C, every other row offset
  - a soft light pool behind the product, so dark garments separate
  - a soft shadow under the product
  - same pixel size and file type as the original
- **How each image is treated:**
  - transparent mockups (the hd- tees, the caps): placed directly
  - sticker products: kept whole as a card
  - white-background mockups (rash guards, towels, polos): cut out with rembg (isnet-general-use)
  - design previews (line art, lettering) and flat sheets: kept whole as a card
  - already converted (wallpaper all round the border): skipped
- **Tool:** `tools/dark_bg.py` + `tools/dark_bg_mark.png`. **Job:** Actions → Dark backgrounds (`dark-bg.yml`), with modes inventory / dry / apply / restore, `only`, `shard i/n` and `limit`.
- **In place:** `fileUpdate(originalSource)` on each MediaImage, so the file, the products using it, its position and alt text stay the same.
- **Backups:** every original is in that run's artifact (`dark-bg-apply-…`, `backups/<MediaImage id>.<ext>`), kept 90 days, with before|after previews and `report.json`. **Undo:** put originals in `tools/dark_bg_restore/` and run mode restore.
- **Inventory:** 2,814 images on ACTIVE + DRAFT products: 1,557 tee, 728 rash guard, 260 cap, 158 other (mostly draft polos), 87 sticker, 24 towel.
- **Pilot** (8 products, 31 images, applied 22:58): all good except three design previews (the Black Bart and Boat Diver plate close-ups, and the Current lettering). They were cut out as line art, which was hard to read on navy. They were restored from backup (byte-identical), the rule was fixed (low-density cut-outs are kept whole as a card), and they were redone as cards.
- **Full run:** four parallel jobs (shards 0/4 to 3/4) started 23:04.
- **Caveats:**
  - Printful can push its own mockups again if a product is re-synced or edited there, and new products arrive on white. Re-run the job (it skips what is done).
  - The site's own local copies (e.g. the cap thumbnails under `img/hats/pf/`, the shirt deck images) are separate files. The CDN-hosted ones follow automatically.
- **Full run result:** 2,814 images, 0 errors. Transparent 1,475 · cut out 908 · card-art 295 · card 74 · already done 49 · skipped (no product found) 13.

## Site copies, and the rash guard fix (27 Nov, early)
- **Site pass** (`tools/dark_bg_site.py`, commit f8c5609): the local images in `img/hats/pf`, `img/organic/caps`, `img/organic/beanie`, `img/jackets`, `img/towels`, `img/stickers` and `img/packs` are on the wallpaper too. Heroes, banners, tiles, og- images and sheet backgrounds are skipped. Rules found along the way: a close-up photo that fills the frame is left alone; a dark product on a plain dark ground is cut out (not left as a square); a sticker is a card only if it fills over 80% of the frame; large holes in a cut-out are filled (the seal centre), small rings stay see-through. **Note:** the site's jacket photos still show models (only the store's were removed).
- **Rash guard problem:** in the store run, 74 rash guard flat lays (44 products) were wrongly kept as white cards. A rembg re-run then lost the pale torso panels (wallpaper showed through), so all 74 were put back to their originals (run 45943341309).
- **Fix:** white-ground mockups are now keyed by a **flood fill from the image edges** (near-white pixels connected to the border become transparent, 1.2 px soft edge). Pale panels survive because the garment outline encloses them. rembg is kept for plain non-white grounds. Plates and design previews stay cards (new tests: many separate pieces, or mostly white paper).
- **Re-applied** (run 45943769018, `only` = the 44 products): 74 keyed, 190 already done, 0 errors. Checked from the before/after previews. The 74 restore originals were removed from `tools/dark_bg_restore/` (commit 4e5013d); backups remain in the run artifacts for 90 days.
