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
