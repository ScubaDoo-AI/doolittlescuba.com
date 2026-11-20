# Changelog — 20 Nov 2026

## Organic cards: the whole shirt in frame
Eric: *"Organic Thistlegorm back looks bad on the website."*

- The organic page showed its Printful mockups (`img/organic/`, replaced 19 Nov) with the old zoom-and-crop (cover at 118%), so the back print lost its right edge (the Egypt block), the collar and both sleeves. `css/site.css` now gives `img/organic/` the same treatment as the other Printful images: the whole square shot in frame (contain, 125%). Affects every organic card (front, sleeve, back), not just the Thistlegorm.

## Price & stock watch (Eric 13:06: "Yes, emphasis on price changes")
New daily job, **Actions → Price & stock watch** (`tools/price_stock_watch.py`, 07:41 New York). It changes nothing on its own.
- **Prices first** → issue *"Price changes need a look"*:
  - Shopify selling or compare-at price ≠ the approved price in `tools/data/price_baseline.json`, with old → new, when it changed, and whether Printful's retail matches (= Printful's sync pushed it, as with the beanie on 14 Nov).
  - Printful retail ≠ Shopify on a linked variant: caught before the next sync can push it.
  - Printful's cost for a blank went up or down, with how many SKUs it touches.
  - Variants with no approved price yet (added since the baseline).
- **Stock** → issue *"Stock watch"*: sold-out variants with suggestions (nearest in-stock colour of the same blank and size, organic edition from the cart map, other Printful regions, pair/bulk notes); blanks Printful says are out in the US before Shopify shows 0; low bulk stock; bulk-printed items that don't track stock.
- **Fixes, by hand only:** mode **accept** (today's price becomes the approved one) or **restore** + apply ✔ (approved price back in Shopify *and* Printful retail, Printful first so its sync can't undo it). SKUs: `flagged`, `new`, `all`, or prefixes like `DS-MRK-BN`.
- First run writes the baseline from today's prices and lists the price per line to check once (Certified-ish is $40 / $43, Signature $42 / $45).
- An issue is only commented when the findings change, and closes itself when everything is clean.
