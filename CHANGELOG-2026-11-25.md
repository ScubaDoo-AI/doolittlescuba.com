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
- Saved as theme commit `781fd95` on the live theme; **not yet published** (waiting for Eric's yes).
- Until it is published, the live deck still says "Towels". One live card, "Surface Interval — Hanging Hand Towel", shows the series name as its line.
- Mirrors updated in `shopify-theme/` (`sections/ds-deck.liquid` and `snippets/ds-deck-cards.liquid` md5-match the theme; new `sections/ds-series-tabs.liquid`; Home Port template).

## Found in the review, not changed (needs Eric's call)
- **Gallery order:** Signature Series and the caps open on the front. Certified-ish (light and dark) and Surface Interval open on the back, while their deck cards show the front.
- **Site cap titles:** the light site caps are titled "<Site> — Dark cap" (for example "Bali — Dark cap" is a khaki cap), which reads oddly to a shopper.
- **"You may also like":** on product pages it renders empty in the theme preview tool. It loads by script, so check it on a real browser.
