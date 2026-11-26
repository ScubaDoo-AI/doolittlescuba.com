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
- Published 10:58 with the rest. The file lives in the theme only and is not mirrored in `shopify-theme/`.

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

## Photo order and cap names (Eric 11:22: "Certified ish should open on the back, Surface interval should open on the fronts as the joke setup is on the front. Signature series is good same for caps. 2. Use suggested")
- **Surface Interval:** the 59 regular Surface Interval tees (Boat Banter, Self-Logged, Buddy Check, Buddy System, Till Surface Do Us Part, Master Class) now open on the front, where the setup line is. The front photo was moved to first place (`productReorderMedia`). The organic editions already led with the front; the custom tees have one image. Their deck cards already showed the front.
- **Certified-ish:** the product pages already opened on the back. The deck cards and the Discover/You may also like cards now lead with the back too (theme: `snippets/ds-deck-cards.liquid`, `sections/ds-discover.liquid`), so the card matches the page.
- **Signature Series and caps:** front first, unchanged.
- **Cap names:**
  - The 14 site caps are now "<Site> — Dive Site cap" and their 14 organic editions "<Site> — Dive Site organic cap". These were "Dark cap" and "organic cap".
  - Handles are unchanged (`<site>-dark-cap`), so no links moved.
  - Home Port ("Home Port — Dark cap") and the brand caps (The Mark, The Seal, The Stack, The Wordmark) keep their names.
  - Card labels read "Dive Site cap" / "Dive Site organic cap". The brand caps' "Dark" label now reads "Brand cap", and Home Port's reads "Custom cap".
- **Pair descriptions:** the 28 cap & tee pairs link to "<Site> Dive Site cap". The two Thistlegorm pairs' "The The Thistlegorm" typo is fixed.
- **Tools:** `tools/pairs.py` and `tools/organic_shopify.py` now write the new names.
- **Theme:** published 11:59 with the "You may also like" fix (Eric: "Publish changes but ensure designs changes are included"); a check of the live theme found every design change in place. The photo order on the product pages and the new names are already live, since they are product data.

## "You may also like" on product pages fixed (Eric 11:00: "Fixit")
- **Cause:** the stock section uses Shopify's automatic "related products". These learn from shop traffic and orders, so before launch they return nothing, and the section showed empty placeholder boxes.
- **Fix:** the Discover section (`sections/ds-discover.liquid`) has a new setting, "related". On a product page it draws a random set from the product's own collections (its series and parts) and leaves out the product itself. A product with fewer than 8 related items to choose from also draws from the standard lines. Organic products get organic suggestions.
- `templates/product.json`: the section, headed "You may also like", replaces Shopify's recommendations. The old section stays in the template, disabled.
- Checked on the Boat Banter Nitrogen tee: four other Boat Banter tees, with rotating photos and the Shuffle button.
- Published 11:59.

## Last "Dark cap" names (Eric 12:51: "Rename")
- **Renamed:** "Home Port — Dark cap" → **"Home Port — Custom cap"**; The Mark, The Seal, The Stack and The Wordmark "— Dark cap" → **"— Brand cap"**.
- **Unchanged:** the handles (`…-dark-cap`), so links and redirects are unaffected. The order tools match by SKU, not title.
- **Card labels:** `snippets/ds-deck-cards.liquid` maps "Brand" → "Brand cap" and "Custom" → "Custom cap", so the cards read the same as before. Published 12:52 (Eric: "Publish").
- No product in the shop is titled "Dark cap" any more.

## Rash guards on the website (Design & Production handoff, 25 Nov; Eric 21:06: "Retry")
- **Shopify:** new smart collection **Rash Guards** (`/collections/rash-guards`, gid 494356463802), rule `tag = series:rg-sig`, sorted A–Z. It holds all 140 rash guards (14 sites × Light/Dark × 5 cuts), all Active. They stay in Signature Series too. Created 12:35. No style or tone sub-collections yet (the `style:*` and `tone:*` tags are in place if wanted).
- **Faire:** Eric took the rash guards off the Faire channel (15:30).
- **New page `/rash-guards/`**, built by `tools/rashguards_page.py` from `tools/rashguards.json` (handles, cdn.shopify.com media, colour names, body hex sampled from each flat lay):
  - Hero: "The dive site, worn in the water." Copy follows the rules: the plates are "drawn by hand", the rash guards are "printed to order"; no screen printing, no UPF claim.
  - Deck of 28 cards, one per site and tone, with **Light / Dark** tabs. Each card turns flat lay front → worn → back. Status "Coming soon", like the rest of the site.
  - The open card has a **style picker**: men's long sleeve $69, women's long sleeve $69, men's short sleeve $62, youth $45, kids $39. The price line (2XL/3XL and short-sleeve steps), sizes, photos, sleeve note and "Shop the …" link follow the chosen cut. The site's place, flag and coordinates come from the sites data.
  - "Five cuts" (prices and sizes), the spec, and links to the Signature tees and launch news.
  - Share image `img/og/rash-guards.jpg`; hero `img/rash-guards/hero.webp`.
- **Prices in the data:** `DS.RG_PRICE` / `DS.RG_STYLES` / `DS.rashCfg` in `js/deck.js`; `PRICES` in `tools/rashguards_page.py`. Change both together.
- **Nav:** "Rash guards" after Jackets on every page (28 pages) and in `tools/line_pages.py` `nav()`.
- **Home page:** a Rash guards tile in the collections deck, after Signature Series (7 collections now).
- **Signature Series page:** an "On a rash guard →" chip in the designs bar (also in `line_pages.py` `chips()`).
- **Search:** 14 entries (`rg-<site>`) in `js/designs.json`; "rash guard bali" finds Bali. `line_pages.py` now adds them on its rebuild through `rashguards_page.index_entries()`.
- **Sitemap:** `/rash-guards/` added.
- **Checked** in headless Chrome, desktop and phone: deck tabs, opening a card, switching cut (price, photo, back view, shop link), no script errors. Home, Signature, Towels and Custom load with no errors. All 140 shop links match real Shopify handles.
- **Not run:** a full `tools/line_pages.py` rebuild. It would undo hand edits on the five collection pages (for example the Signature hero photo), so the new nav link and chip were patched into those pages directly.
- **Still open:** real sample photos replace the Printful mockups when samples arrive (none ordered yet). Eric revokes the Printful token "Claude rash guard setup Nov 2026" (expires 30 Nov). The Shopify theme has no Rash guards deck tab yet.
