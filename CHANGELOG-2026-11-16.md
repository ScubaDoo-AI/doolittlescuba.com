# Changelog — 16 Nov 2026

## Store domain and cart (morning, D13)
- **shop.doolittlescuba.com** is the Shopify primary domain (Porkbun CNAME `shop` → `shops.myshopify.com`; connected and set primary in Shopify by Eric). Every store, product, pair and Make-it-yours link on the site now points there instead of `doolittlescuba.myshopify.com`, which 301s to the new address. (`1ea1b73`)
- A **Cart** link (`https://shop.doolittlescuba.com/cart`) sits at the end of the top menu on all 26 pages with a menu, and in the menu generator `tools/line_pages.py`. Until the store opens it lands on the password page.
- Home page contact heading "Surface interval" → **"Topside"**, so it no longer reads as the Surface Interval line name.
- **Shop status banner** reworded for the new address and Cart link, dated 16 Nov, new id `2026-11-16-shop-address` so dismissed banners show again; the organic and Surface Interval pages were added to `tools/status_flag.py`. (`cce9221`)

## About page (morning)
- Hero photo is now the quarry-day shot of Eric and Allie; the strip's duplicate quarry photo is replaced with Allie on the dive boat off Taveuni, Fiji. (`f0442f4`)

## Review and sibling update (afternoon)
- **`STATUS-2026-11-16.md`**: full Website Building review and the update for the Company and Design & Production projects (corrections to their 16 Nov reviews, cap-colour answer, D1–D13 status, launch blockers, next steps).
- **Fix:** the `/off-gassing/` redirect stub still carried the shop-status banner, because the first rename (`7da6930`) added it to `tools/status_flag.py` and the second (`bfc8df2`) turned the page into a redirect without removing it. Removed from the generator and the stub.
- **Staged, not live:** `policies/privacy.html` — the data-sharing opt-out link now points to the relative `/pages/data-sharing-opt-out` instead of `https://x00ytr-y9.myshopify.com/…`; dated 16 Nov. Publish with Actions → **Policy push**, `privacy`, Apply on. (Company review item N5.)

## Verified live (13:00 ET)
- Site at `f0442f4`; headline, shop@-only contact, footer policy links, `/surface-interval/` with redirects, Cart link, no myshopify links.
- Shopify: 568 Active / 19 Draft / 19 Archived, 0 orders; every 15 Nov price row matches; beanie French Navy only at $32 (Printful: in stock, US); both automatic discounts Active; General shipping profile Standard $9.64 / Express $21.98 (the $0 rate is gone).
- GitHub's scheduler is running the 15-minute custom-orders job every 4–7 hours. Logged in the status report as a pre-launch decision.
