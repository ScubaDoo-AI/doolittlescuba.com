# Doolittle Scuba — Shopify store record (2026-10-23, images updated 2026-10-24)

Store `x00ytr-y9.myshopify.com` (Basic plan, USD, shop@doolittlescuba.com). Still named **"My Store"** in Shopify; nothing is published yet — every product is a **Draft** until Eric says go.

## What is in the store

| Line | Products | Price | Sizes | Images (from doolittlescuba.com) | Tag that drives the collection |
|---|---|---|---|---|---|
| Signature Series tees | 14 | $38 S–XL · **$41 2XL/3XL** | S, M, L, XL, 2XL, 3XL | on-model front + back photo, watermarked full back print (plate + Facts / Species / Water, `img/designs/<slug>-back.webp`), watermarked plate close-up | `signature-series` |
| Certified-ish tees | 20 | $38 S–XL · **$41 2XL/3XL** | S, M, L, XL, 2XL, 3XL | mockup back + front (`img/certs/`), watermarked preview of the final back print (`img/designs/`) | `certified-ish` |
| Caps | 19 (14 site + 5 brand) | $32 | One size | mockup front + back (`img/hats/`) | `cap` |

53 products, 223 variants, all with inventory tracking on and quantity 0 (set real counts when stock arrives). Vendor "Doolittle Scuba"; product types "T-shirt" and "Cap". Every product also carries `coming-soon`, `colour:<slug>` and `site:<slug>` / `cert:<slug>` / `brand` tags, and a description with the site line, the placements (Back / Chest / Sleeve / Shirt), a link to the site guide and a "Make it yours" link that opens the same set-up on `/custom/`.

SKU scheme: `DS-<code>-T-<size>` for tees, `DS-<code>-C` for caps. Site codes: BBT, BSP, BGR, BWP, DAM, BAL, RRV, NAV, DLP, THD, THI, SOM, RRF, VUN. Certified-ish codes: OWD, AOW, ALT, BOA, BUO, CAV, DEE, DPV, DRI, FSH, ICE, NGT, NTX, REB, SAR, SRD, SID, SMB, TEC, UWP. Brand caps: MRK, STK, WDM, SEA, HMP.

### Collections (smart, by tag)
- Signature Series — `gid://shopify/Collection/492282708154`, cover: Black Bart front
- Certified-ish — `gid://shopify/Collection/492283986106`, cover: Night Diver back (alphabetical)
- Hats — `gid://shopify/Collection/492284018874`, cover: The Mark
- "Home page" (Shopify default) — `gid://shopify/Collection/492282020026`, empty

### Certified-ish colours (one per design; change any of them by editing the product and re-rendering the mockup)
Open Water · Caribbean blue — Advanced Open Water · teal — Altitude · ivory — Boat · light blue — Buoyancy · aqua — Cave · terracotta — Deep · teal — DPV · mustard — Drift · mint — Fish ID · berry pink — Ice · light blue — Night · lavender — Nitrox · mustard — Rebreather · sage — Search and Recovery · butter — Self-Reliant · ivory — Sidemount · Caribbean blue — Surface Marker Buoy · coral — Tech · sage — Underwater Photographer · pink.

Signature Series and cap colours follow the catalog (Black Bart light blue, Bridge Span 14 Caribbean blue, Blue Grotto mint, Blue Water Park teal, Dampier Strait butter, Bali terracotta, Rainbow River sage, Navy LLCAT mustard, Dive Land Park aqua, Thurmond Dam ivory, Thistlegorm berry pink, Somosomo Strait coral, Rainbow Reef lavender, Vuna Reef pink); brand caps: The Mark navy, The Stack ivory, The Wordmark mint, The Seal sage, Home Port teal.

### IDs worth keeping
Location `gid://shopify/Location/88138612922` · Online Store publication `gid://shopify/Publication/226259370170` (also "Shop" 226259402938 and "Point of Sale" 226259435706).

## Checklist — things only the owner can do in Shopify admin

Current state found in the store: name "My Store"; only the auto-generated privacy policy exists; one shipping zone (United States: Standard $8, a second Standard rate at $0, Express $15 — Shopify's defaults); billing address Newnan GA 30263 with no street/city; no custom domain; payments not visible to me.

1. **Store name** — Settings → General → Store details: "Doolittle Scuba". Then Settings → Policies → regenerate the privacy policy, since the current text says "My Store operates this store".
2. **Payments** — Settings → Payments → Shopify Payments: business details, EIN, and the payout bank account. (I don't enter banking or identity details; this one is yours.) Consider enabling Shop Pay / PayPal there too.
3. **Shipping** — Settings → Shipping and delivery → General profile. Decide the domestic rates (the $0 "Standard" rate is a default; check its condition or delete it). Add a Rest of World zone if you will ship overseas (Fiji, Indonesia, Egypt divers will find the site). Add weights to variants if you want carrier-calculated rates (a Comfort Colors 1717 is about 7–9 oz; a dad cap about 3 oz).
4. **Taxes** — Settings → Taxes and duties → United States: add Georgia (register with the GA Department of Revenue first). Shopify collects where you tell it to.
5. **Policies** — Settings → Policies: Refund/return, Shipping policy, Terms of service, Contact information. Shopify's templates are fine to start; add the made-to-order note (shirts printed by hand, allow X days).
6. **Theme and home page** — Online Store → Themes. The three collections and the product images are ready; set the collection list on the home page in the order Signature Series · Certified-ish · Hats. Branding assets are in the Project (DS_* SVGs).
7. **Domain** — Settings → Domains → Connect existing domain → `shop.doolittlescuba.com`. Then at Porkbun add a CNAME: host `shop` → `shops.myshopify.com`. Keep doolittlescuba.com itself on Porkbun static hosting; the static site links out to the shop.
8. **Inventory** — when the first run is printed, give me the counts per size and I set them (or Products → Inventory in admin).
9. **Go live** — say the word and I flip all 53 products to Active in one pass, remove the `coming-soon` tags, change the "Coming soon" pills on the static site to "Buy" buttons pointing at the Shopify product pages, and add the shop link to the nav.

## What the static site will need on launch
- Shirt and hat cards on the home page: pill → "Buy — $38" / "$32" linking to `https://shop.doolittlescuba.com/products/<handle>`; handles are the product titles slugified (e.g. `black-bart-signature-series-tee`, `certified-ish-night-diver-tee`, `black-bart-cap`, `the-mark-cap`).
- Nav: "Shop" entry; `/custom/` request email stays as is (custom orders are quoted by hand, not sold off the shelf).
- `img/certs/` (40 renders, 0.7 MB) was added to the site repo on 2026-10-23 as the image source for the Certified-ish products; it is not linked from any page yet. Rebuilt the same day from the final portrait designs.
- Image URLs given to Shopify carry `?v=<content hash>` (the site's cache-busting scheme): Porkbun's CDN caches images for 30 days by URL, so a replaced file must be re-imported under its new hashed URL (remove the old media, add the new URL). The product images are Shopify's own copies afterwards; the site URL only matters at import time.

## 2026-10-24 — Signature Series back prints
- Each of the 14 Signature Series tees gained a third image: the watermarked preview of the whole back print (plate with its Facts / Species / Water block, 900×1240), imported from `img/designs/<slug>-back.webp?v=<hash>` and moved to position 3, ahead of the plate close-up. Media ids 47018093150394 … 47018094592186.
- Also in the store, not from this session: 14 **"Signature Series Dark tee"** drafts (tags `dark-line`, `signature-series-dark`, colours graphite / navy / sage / wine / emerald / blue-spruce / midnight / moss …), created 2026-10-23 23:15 UTC with no images yet. Left untouched; they need their own mockups before launch.

## 2026-10-24 — Make it yours tee (personalized)
- Product `gid://shopify/Product/10398640242874`, handle `make-it-yours-tee`, Draft, tags `tee make-it-yours custom coming-soon personalized`. Options **Size** (S–3XL) × **Personalization**: "Your design and colour" = $43 ($46 2XL/3XL, SKU `DS-MYA-T-<size>`), "With your line or logo" = $44 ($47, SKU `DS-MYB-T-<size>`). Pricing rule: catalog tee + $5 for a design/colour/placement of the customer's choosing, + $6 when a name, a line or their logo goes on. Inventory untracked, policy CONTINUE (printed to order). Image: the four-mockup OG image.
- The customer's choices travel as the Make it yours mockup link (pasted into the order note at checkout; the logo file by email to orders@). At launch, the "Write my request email" button on `/custom/` can become "Add to cart" with a cart permalink (`/cart/<variant id>:<qty>?note=<mockup link>`); variant ids: A S 50824329199802, M 50824329232570, L 50824329265338, XL 50824329298106, 2XL 50824329330874, 3XL 50824329363642; B S 50824329396410, M 50824329429178, L 50824329461946, XL 50824329494714, 2XL 50824329527482, 3XL 50824329560250.
- Caps follow the same rule on the $32 cap: $37 for your design and colour, $38 with your line or logo (decided 2026-10-24). Product **Make it yours — personalized cap**, `make-it-yours-cap`: see below for ids.
