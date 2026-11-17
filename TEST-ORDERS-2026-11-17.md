# Test orders — plan and checklist (17 Nov 2026)

Seven orders through the password-protected store prove checkout, the discount, shipping rates, the name and custom flows, the Shopify → GitHub relay and the Printful drafts, without printing anything or charging a card. Eric places them; Website Building watches the plumbing and reports.

## Before the first order (Eric, ~10 minutes)

1. **Printful: hold every imported order.** Printful dashboard → Settings → Orders → set order confirmation to **manual** (orders wait for your approval; nothing prints, nothing is charged). Without this, Printful would start producing any synced tee or cap the moment Shopify marks the order paid.
2. **Shopify: a test payment gateway.** Shopify admin → Settings → Payments. Shopify Payments isn't set up yet, so under third-party providers search for **"(for testing) Bogus Gateway"** and activate it. At checkout it takes card number `1` (success), `2` (declined), `3` (error), any name, any future expiry, any CVV. *If Shopify Payments gets set up first, use its Test mode instead; Bogus Gateway disappears once a real provider is active.*
3. **Storefront password:** Online Store → Preferences shows it. Open `https://shop.doolittlescuba.com` in a normal browser window and enter it once.
4. Use a real email you can read (order confirmations will arrive) and your own address for shipping.

Nothing else needs changing. Georgia tax isn't configured yet, so no tax line will appear; that's expected.

## The seven orders

Place each as its own order. Add `test` in the order note at checkout so they're easy to find later.

| # | What to put in the cart | What it proves | What to check at checkout |
|---|---|---|---|
| 1 | **Pair:** `/products/the-thistlegorm-pair-light` — S/M cap, size M tee | Shopify bundle expands into tee + cap for Printful; pair shipping | Price **$72**; shipping **Standard $9.64** (not $0); no extra discount line |
| 2 | **Mix & match (D8):** `/products/the-thistlegorm-signature-series-tee` (M) + `/products/bali-dark-cap` (S/M) | The automatic "Mix & match: tee + cap $8 off" | Subtotal $80 → discount line **−$8**; two shipping lines or one combined Printful rate (tees and caps ship separately) |
| 3 | **Surface Interval name tee:** `/products/aquatic-comic-self-logged-camel-tee` (M), name `Eric` | Name field → line property; relay fires; custom-orders job renders and drafts | Product page refuses an empty name; the cart line shows **Name on the shirt: Eric**; express checkout is hidden on this page |
| 4 | **Make it yours tee:** design one on `https://doolittlescuba.com/custom/` and press **Add to cart** (tier B: add a line of text) | /custom/ hand-off to the store; `_design` property; relay; draft | Cart line shows "Your design" and "Mockup"; price **$48** (tier B) |
| 5 | **Make it yours cap with a line:** on /custom/, cap, your line on the front, S/M qty 1 | Digitization fee line; cap draft at Printful | Cart has the cap at **$41** and one **Embroidery digitization — one time per design** line at **$7.00** |
| 6 | **Home Port cap:** `/products/home-port-dark-cap`, pick a pin on the map | Map picker properties; the job **holds** this one for a hand-built front file (reason `home-port`) | Cart line carries the chosen coordinates; price **$48** |
| 7 | **Sticker pack:** `/products/sticker-pack-reef-cuties` ×1 | The "Stickers shipped by Doolittle Scuba" profile | Shipping **Sticker Mail $1.00**; add a second pack and it should flip to **free** |

## What happens after you pay (nothing to do, just watch)

- **Orders 1, 2 and 7:** Printful imports 1 and 2 and holds them for your confirmation (manual confirmation from step 1). Order 7 is yours to mail; nothing goes to Printful.
- **Orders 3, 4, 5, 6:** within a minute the relay starts **Custom orders** in GitHub Actions. The job uploads the print files to Shopify Files, creates a **Printful draft** for 3, 4 and 5, and opens one GitHub issue per draft (no buyer data). Order 6 is **held** with reason `home-port` and gets its own issue. Nothing is charged until you confirm a draft.
- Every morning at 07:23 ET the reminder issue lists any drafts still waiting.

Website Building checks, after each order: the Worker log (Shopify hit, signature OK, "dispatched"), the Actions run, the issue, and the Shopify order (properties, discount, shipping line). Report goes in `CHANGELOG-2026-11-17.md`.

## Cleaning up (after the checks)

- **Printful:** cancel the imported orders (1, 2) and delete or cancel the drafts (3, 4, 5). No cost.
- **Shopify:** for each test order, **Cancel** → refund (Bogus Gateway refunds instantly) → **Archive**. The store's order count goes back to showing real orders only once the password comes off.
- **Settings → Payments:** deactivate Bogus Gateway before launch (Shopify Payments replaces it).
- Keep one screenshot of each checkout for the Company project's test-order record.

## Known limits of this round

- No tax line (Georgia not set up yet) and no Shopify Payments: the money path is not being tested, only everything up to it.
- Bogus Gateway orders are real orders in Shopify's eyes: the webhook, Printful import and all emails fire exactly as they will at launch. That's the point, and also why step 1 matters.
