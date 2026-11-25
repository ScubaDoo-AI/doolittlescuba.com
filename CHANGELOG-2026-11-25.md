# Changelog — 25 Nov 2026

## Towels are now hanging hand towels (Eric 08:45: "Change the current 12 towels to hanging hand towels, beach towels line is in progress")
- **Shopify, all twelve Water Hazard towels:**
  - Titles are now "<Design> — Hanging Hand Towel".
  - Handles are now `<design>-hand-towel`; Shopify redirects the old `-water-hazard-towel` handles, which still redirect from the older `-golf-towel` ones.
  - Product type is "Hand Towel". Tags: `golf-towel` dropped; `hand-towel` and `hanging-hand-towel` added.
  - Descriptions and SEO now read "hanging hand towel", and each one says beach towels are in the works.
- **Collection Water Hazard:** the description and SEO were rewritten the same way. The sort order is now manual, by design code: WH01–WH06, then WH07–WH12 (before, set two was out of order).
- **Theme:** the deck tab label "Towels" is now "Hand towels" on the home page and the collection pages. Towel cards get a white photo panel, so the Printful mockup no longer sits in a white square on a dark card. The card snippet recognizes towels by their `towel` tag, so "Surface Interval — Hanging Hand Towel" is not read as the Surface Interval shirt line.
- **Site /towels/:**
  - The copy now says hanging hand towels: title, description, hero, section heads, card captions and alt text.
  - The shop links use the new handles.
  - New note under the specs: "Beach towels are in the works", with a link to get word.
  - The nav label stays "Towels", which will cover the beach line too.
  - Catalog map rebuilt: 12 of 12 linked.

## Scrolling tabs on every series view (Eric: "All collections must use the scrolling tabs when viewing a series")
- **Sub-collection pages** now light up their series tab, with a row of linked chips for the series' other parts. Before, these pages lit no tab and added an extra tab at the far right, off-screen on phones.
  - Surface Interval: Boat Banter, Self-Logged, Buddy Check, Buddy System, Till Surface Do Us Part, Master Class.
  - Caps & beanies: Site Caps, Brand Caps.
  - Stickers: Achievement Unlocked, Sticker Packs, Die-cut, Brand.
  - Eco lights Organic.
  - The map is `ds_parent_map` / `ds_children` in `sections/ds-deck.liquid`.
- **Home page deck:** the Surface Interval, Caps and Stickers tabs show the same chips as links into each part.
- **Tab bars:**
  - The current tab scrolls into view on load (on phones it was often off-screen).
  - An edge fade shows there is more to scroll.
  - A mouse wheel scrolls the bar sideways.
  - Clicking a tab on the home page centres it.
- **Product pages:** a new section, `sections/ds-series-tabs.liquid`, sits above the product on all four product templates. It shows the same scrolling tabs with the product's series lit, and a back link to its sub-collection or series (for example "← Surface Interval · Boat Banter"). Its tab list mirrors the deck tabs; keep the two in step when a tab is added.

## Card mapping fixes from the review
- Deck card line labels that came out as a bare word now read properly:
  - "Bali — Dark cap" → **Site cap** (was "Dark")
  - "… — organic cap" → **Organic cap**
  - "The Side Mark — cap" → **Brand cap**
  - "The Mark — Beanie" → **Brand beanie**
  - "Make it yours — personalized tee" → **Personalized tee**

## Theme state
- **Published 10:58 (Eric: "Publish ensuring all updates are present").** Everything in this file is live. A check of the live theme after publishing found every change in place.
- **Publish hiccup:**
  - Shopify's publish check kept refusing `templates/product.home-port.json` and `templates/product.personalized.json` as "changed on Shopify". Shopify had added its auto-generated header comment to both.
  - Both are now left exactly as Shopify has them.
  - The series tab bar now comes from `layout/theme.liquid` (`{% section 'ds-series-tabs' %}` when the template is a product page) instead of from each product template. One place covers all four product page types, with no duplicates.
  - Custom items (Home Port, personalized, series custom) link back to Custom rather than to a sub-collection such as Site Caps.
- Mirrors updated in `shopify-theme/` (`sections/ds-deck.liquid` and `snippets/ds-deck-cards.liquid` md5-match the theme; new `sections/ds-series-tabs.liquid`; Home Port template).

## "Discover something new" picks at random and turns its photos (Eric 08:56)
- New theme section `sections/ds-discover.liquid` ("Discover (random)"). It replaces the stock product list on the 404 page ("Discover something new"). On the cart page, the same section replaces "You may also like" under that heading. The stock product lists stay in both templates, disabled, so they can be switched back in the theme editor.
- The section writes a pool of about 16 products from each line: Signature Series, Certified-ish, Surface Interval, caps, jackets, stickers, hand towels, 1N73LL1G3NC3 and Off-World. It leaves out organic editions, custom and personalized items, sold-out items and the digitization fee.
- Pool size, the collections drawn from, cards shown (4 on desktop, 4 on mobile) and seconds per photo (3.5) are settings in the theme editor.
- **Random picks:** the browser deals a fresh set on every page view. Each card in a set comes from a different line where possible. Shopify caches the page, so the pick has to run in the browser. A **Shuffle** button deals a new set and never repeats the set just shown.
- **Rotating photos:** each card turns through its photos, front then back then side, with a fade. The cards are staggered so they don't change together. A card pauses while the pointer is on it, and turning stops for visitors who ask for reduced motion.
- Saved as theme commit `773a247`, not yet published. The file lives in the theme only and is not mirrored in `shopify-theme/`.

## "Page not found" check (Eric 10:07: "Bigger issue above is the page not found error")
- **The two 404 screenshots this morning were test addresses typed into the preview tool, not links on the site or in the shop:** `/products/surface-interval-boat-banter-nitrogen-tee` was a wrong guess (the real handle is `aquatic-comic-boat-banter-nitrogen-tee`), and `/products/no-such-thing` was made up to show the Discover section.
- **Audit run after:**
  - All 51 product links on doolittlescuba.com resolve to active products published on the Online Store. These are the 28 cap & tee pairs, the 12 hand towels, the 10 series custom tees and the Side Mark cap.
  - Both collection links resolve (`water-hazard`, `pairs`).
  - Every link the theme writes is generated from live collections (`collections/all` and the deck/tab handles).
  - Every internal link and image on the site exists, except the four below.
- **Fixed, live now:**
  - `policies/terms.html` linked to Shopify-style addresses that don't exist on the static site (`/policies/shipping-policy`, `/refund-policy`, `/privacy-policy`). It now links to `/policies/shipping.html`, `refund.html` and `privacy.html`.
  - `policies/privacy.html` linked to `/pages/data-sharing-opt-out` on the site. It now goes to that page in the shop.
  - The 12 old `-golf-towel` redirects pointed at the `-water-hazard-towel` addresses, which redirect again. They now go straight to the `-hand-towel` pages (one hop).
  - Shop main menu: the "Off topic" entry under Shop was a dead `#` link. The Shop menu now matches the deck tabs: Signature Series, Certified-ish, Surface Interval, Caps & beanies, Cap & tee pairs (new), Organic, Jackets, Stickers, Hand towels (new), Custom (new), 1N73LL1G3NC3 (off topic), Off-World Hunt Club (off topic), Everything.

## Found in the review, not changed (needs Eric's call)
- **Gallery order:** Signature Series and the caps open on the front. Certified-ish (light and dark) and Surface Interval open on the back, while their deck cards show the front.
- **Site cap titles:** the light site caps are titled "<Site> — Dark cap" (for example "Bali — Dark cap" is a khaki cap), which reads oddly to a shopper.
- **"You may also like":** on product pages it renders empty in the theme preview tool. It loads by script, so check it on a real browser.
