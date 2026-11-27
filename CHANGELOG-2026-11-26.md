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
- **Store footer** (`sections/footer-group.json`): "Surface interval" → **"Get launch news"**.
- Theme committed 21:3x; **waiting for publish**. Checked by screenshot at 1440 and 390 px.
