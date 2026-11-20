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

## Organic tees were Sold out: moved to the SATU001 (Eric: "Yes", 12:30)
- **Found (10:50):** 223 of 242 organic products showed **Sold out** (all organic tees; organic caps and beanie fine). Printful's catalog now lists the Stanley/Stella **STTU169** (product 456) for **EU/UK only**, so every US variant synced to Shopify as 0 stock.
- **Fix:** `tools/organic.py` now uses the **Stanley/Stella SATU001** Creator 2.0 ribbed neck (product 818): US, same colours, same print areas (printfiles 1 / 130, checked with `Printful read`), 100% organic, 180 g/m²; $15.91 S–XL / $17.91 2XL / $19.91 3XL (about $1.96 more per shirt; prices unchanged, lowest margin $17.65). **Desert Dust, Khaki and Stargazer have no US 3XL**: those 3XL variants are left unlinked (ignored at Printful) and show Sold out. `printful_link.py` ignores a planned variant with no variant id; `aquatic_order.py` uses the SATU001 for organic name tees and stops with a clear message on a 3XL with no US variant.
- **Relinked:** test DS-THI-TDO (run 44784341615, 6/6, stock 9,999 on S–2XL), then all 223 organic tee keys (run 44784851072): **1,104 linked**; the 234 "failed" are the 39 personalised organic tees re-sent as ignored (Printful refuses `is_ignored` without files; they were already ignored and stay so). Shopify after: every non-personalised organic tee has 9,999 on S–2XL. The 39 personalised organic tees are untracked in Shopify (made per order), so they were never sold out.
- Product descriptions ("Stanley/Stella Creator 2.0, 100% organic ring-spun cotton, 180 g/m²") still true; mockups still show the STTU169 (similar, flat collar vs ribbed).
- **Turtle Trio sticker pack:** inventory tracking turned off (it was the only pack still tracked, so it showed Sold out).
- Sample set 2's Dampier Strait organic tee (Desert Dust XL) was ordered on the STTU169 before this; Printful accepted it.
