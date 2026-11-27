
## Banner updated (Eric 12:42 "Let's update the banner, first check doolittlescuba@ gmail.com email")
- Inbox check: sample set 2's last part (The Seal dark cap) shipped 26 Nov; proof order 4 (Water Hazard towels, USPS) due 30 Nov–1 Dec; proof order 3 (DHL) due 2–7 Dec.
- Status flag id `2026-11-27-samples-en-route`, state **Proofing**, "Updated 27 Nov 2026": new rash guards, Water Hazard towels and the dive-site guides; last samples by early December; items stay "Coming soon"; Achievement Unlocked UV stickers in stock for day one.
- `tools/status_flag.py` now also covers `caps/`, `jackets/` and `rash-guards/` (they were missing and still showed the 22 Nov flag). Applied on all 30 pages.

## Store check job, staged for launch (Eric 13:20: "may need to be completed in prep or at least staged")
- **New:** Actions → **Store check** (`store-check.yml`), daily 12:41 UTC and on demand. Report in the run summary and the `store-check` artifact (30 days).
  1. `tools/store_seo_audit.py` (admin API; works while the store is private): per active product, images with no alt, search title > 70, missing/too-long search description (or falling back to body text), duplicate titles; collections without description or image alt.
  2. `tools/store_check.py` (storefront crawl): sitemap + links, up to 60 pages: status, title, meta description, one h1, og:image, canonical, images without alt, broken links. Signed with the Shopify crawler signature from secrets `SHOPIFY_CRAWL_SIGNATURE` / `SHOPIFY_CRAWL_SIGNATURE_INPUT` (Signature-Agent set in code). While the store has its password it reports "private" and passes.
- **First run** (46049094608, success): 735 active products, 30 collections. 0 images without alt. 0 duplicate titles. 7 dark rash guards (women's LS, men's SS) have search titles of 71–72 chars. 723 products have no search description of their own, so Google would show the start of the body (site name, place, coordinates). Collections `frontpage`, `pair-discount-tees`, `pair-discount-caps` have no description. Crawl: store private.
- **Found:** the Signature Series collection description still says "screen-printed" (against the 15 Nov no-screen-printing rule). Not changed yet.
- **Eric:** create the crawler signature (Online Store → Preferences → Crawler access; name "GitHub store check", domain shop.doolittlescuba.com, longest expiry) and paste Signature and Signature-Input into GitHub → repo Settings → Secrets and variables → Actions as the two secrets above.
