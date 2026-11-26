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
