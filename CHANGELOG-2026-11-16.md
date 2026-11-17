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

## Company reply applied (afternoon, 15:05–15:40 ET)
The Company project answered the 13:00 update (`site/siblings/COMPANY-UPDATE-2026-11-16.md` in the Project) with four new decisions, D14–D17. Website Building's part:
- **C8 — `tools/printful_*.py` prices** now match the 15 Nov table: Certified-ish $40/$43, 1N73LL1G3NC3 $36/$39, Off-World $38/$41, Surface Interval Boat Banter $38/$41 and personalised $45/$48 (`tools/aquatic_designs.json`), site caps $38, brand caps $36, jackets $85/$88 and $45/$48, beanie $32 and French Navy only (Black dropped per D6). `tools/organic.py` now prices organic tees at the line + $3, caps + $2, beanie $32; `tools/organic_shopify.py` says "a few dollars more". Signature stays $42/$45. Stickers never go to Printful (unchanged).
- **N6 — policies staged** (not live): `policies/shipping.html` and `policies/refund.html` drop the "Ready to ship / In stock", "Preorder drop" and USPS-Ground-Advantage-for-shirts tiers; everything is printed or embroidered to order (2–7 business days; custom 3–8; stickers from stock within 3), apparel ships by ground from the print partner, caps and beanies arrive separately. Refund table: no change-of-mind returns on made-to-order apparel, custom items or mailed stickers; 12-hour cancellation window for all orders. `policies/terms.html` §1 and §3 lose the preorder wording. All three dated 16 Nov. **To publish:** Actions → Policy push, `privacy shipping refund terms`, Apply on — on Eric's "push".
- **D17 — partner source tracking built:** `tools/partner_src.py` stamps a small script (SRC markers) on all 26 content pages. `?src=shop-<name>` is kept for 30 days and every link or form to shop.doolittlescuba.com gets `utm_source=shop-<name>&utm_medium=partner`, including the Make-it-yours cart form on /custom/. One Umami event `partner` per visit. Tested headless: the Cart link, pair links and custom cart form carry the UTM; without `?src=` nothing changes. Run `tools/partner_src.py` after any page generator, like `status_flag.py`.
- **D16 — custom-order trigger, finding:** Shopify can't call GitHub's `workflow_dispatch` directly (no auth header on webhooks; Flow's "Send HTTP request" is Grow-plan and up, not Basic). Relay proposal and ready code in `tools/relay/worker.js` and `CUSTOM-ORDERS.md` (Cloudflare Workers free tier, two secrets, one Shopify webhook on `orders/paid`). Needs Eric's yes; nothing is set up.
- The Design project's "Website Building — Full Review and Limitations" (16 Nov, 4 pp.) was checked line by line against the repo and Shopify: every line matches the 13:00 state.
- 20:15 — **Sample set 2 (draft #sample-202611120318):** The Mark beanie Black was flagged "Out of stock" in Printful's editor; switched to **French Navy** (the only colour sold, D6) via the colour dialog — line is now the synced "The Mark — Beanie / French Navy / One size". Saved and checked: 15 items, $470.24, not charged; Printful's flat-rate estimate is now Dec 17. Not yet sampled anywhere: Surface Interval regular tee, organic beanie, dark-grey / olive / royal-blue caps, Wordmark and Stack caps, stickers, custom products (test orders).

## D16 live (evening, 19:00–20:55 ET)
- **Shopify → GitHub relay is live.** Cloudflare Worker `doolittle-relay` (Eric's personal Cloudflare account, free plan) deployed from this repo by the new **Relay deploy** workflow; Shopify webhook "Order payment" → `https://doolittle-relay.jdoolittle212.workers.dev/shopify`. Shopify's signed test notification answered 200 "no custom lines"; unsigned calls get 401. Details and the secrets list are in `CUSTOM-ORDERS.md`.
- Cloudflare's online editor could not take pasted or typed code from the browser pane, so the Worker is deployed by GitHub Actions with wrangler (`tools/relay/wrangler.toml`), and both Worker secrets come from repo secrets. Eric added three repo secrets: `CLOUDFLARE_API_TOKEN`, `RELAY_GITHUB_TOKEN`, `SHOPIFY_WEBHOOK_SECRET`.
- Worker answers 503 "relay not configured" until both secrets exist (`75c0c2c`); workflow condition fix (`9a62a35`).
- For Company's ledger: Cloudflare free plan, $0, on Eric's personal account; a stray empty Cloudflare account under shop@ can be deleted.

## Policies published (21:13 ET)
- Actions → Policy push run 44001340812, Apply on, `privacy shipping refund terms`: all four written to Shopify and verified live (dated 16 Nov; privacy opt-out link now relative; no "in stock"/preorder/USPS-for-shirts wording). Closes Company items N5 and N6.
