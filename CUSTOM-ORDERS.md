# Custom orders pipeline

Custom shirts bought on DoolittleScuba.com become **Printful drafts automatically**.

Two products are in the job:
- the **Make it yours tee**;
- the **personalized Aquatic Comic name tees**, regular and organic. These are the 39 designs: Self-Logged, Buddy Check, Buddy System, Till Surface Do Us Part and Master Class.

One Shopify order makes one Printful draft, whatever mix of custom lines it has. Nothing prints and nothing is charged until Eric checks and confirms a draft.

## Flow

1. A buyer designs a shirt on **/custom/** ("Make it yours") and clicks **Add to cart**. The page posts to `doolittlescuba.myshopify.com/cart/add`:
   - The variant is **tier A**, or **tier B** when the design adds a line.
     - Tier A: SKU `DS-MYA-T-<size>`.
     - Tier B: SKU `DS-MYB-T-<size>`.
   - The design goes in the line property `_design` (a query string: colour, back, chest, sleeve, upper, text…).
   - The line also carries "Your design" and "Mockup", which the buyer sees.
2. The GitHub workflow **Custom orders** runs every 15 minutes (`.github/workflows/custom-orders.yml` → `tools/custom_order.py`):
   - Reads paid orders through the Doolittle Order Bot app.
   - Skips any order Printful already has (external id `MY<order number>`).
   - Renders the print files.
     - Make it yours: `tools/custom_tee.py` (front / back / sleeves, 12 × 16 in and 3.5 × 4 in).
     - Aquatic name tees: `tools/aquatic_print.py`, with the names the product page collected ("Name on the shirt", "Diver 1/2", "Husband/Wife"). Front + back, full area.
   - Uploads them to Shopify Files.
   - Creates a **Printful v2 DRAFT**: Comfort Colors 1717, or Stanley/Stella STTU169 for organic Aquatic tees; DTG.
   - Skips an order that was already sent by hand with `aquatic_order.py`.
3. The workflow opens **one GitHub issue per draft or hold**. The issue has no buyer data, because the repo is public.
4. Eric checks the draft in Printful and confirms it. He can do this in the Printful dashboard, or with the workflow: mode `confirm` + `printful_id`.

## Holds

Some orders need a person, so the pipeline sends nothing to Printful and reports the reason (`reason_kind`) instead:

| reason_kind | When |
|---|---|
| logo | The chest is a customer logo. These are wholesale quotes, so they are never automatic. |
| home-port | A Home Port design. |
| no-design | The line has no `_design` property. |
| name | An Aquatic name tee with a missing name, or a name too long (12 characters for one name, 10 each for two). |
| no-address | No shipping address could be read. |
| other | Invalid input: a design the page doesn't offer. |

## Design rules

- **Custom logo / artwork on the chest:**
  - The **DS mark goes on the sleeve**.
  - **No shark signature** on these shirts.
  - The page enforces both rules, and so does `custom_tee.py`.
- **Logo shirts are for wholesale and dive shops:**
  - /custom/ shows "Wholesale quote" instead of a price, and asks for the shop name.
  - The request is emailed to sales@doolittlescuba.com.
  - There is no Add to cart.
  - Wholesale pricing and minimums are not set yet. Eric decides these.
- **Light shirts:** white marks are recoloured navy, and the Signature / Off-World masters use their light versions.

## Running it by hand

| Mode | What it does |
|---|---|
| `dry` (input `days`) | Renders and reports only: no upload, no Printful. |
| `run` (optional `order`) | Drafts what is new. |
| `confirm` + `printful_id` | Confirms a checked draft. **This starts production and charges the card.** |

## Phases

1. **Make it yours tee** is live (drafts only).
   - First dry run: 13 Nov, run 43556984598. It succeeded and found no custom orders in 60 days.
2. **Personalized Aquatic tees** are live (drafts only), as of 13 Nov.
   - Tested locally on fake orders: single name, two-name organic, mixed with a Make it yours tee, a missing name and a long name.
3. **Make it yours cap** comes after that. It is embroidery, so it has digitization fees.

## Before the first real order

- [ ] Place a test order through Add to cart. This needs the storefront password preview or the launch.
- [ ] Check that the order query can read the shipping address. Protected customer data may hide it; if so, the order is held as `no-address`.
- [ ] Check that Printful accepts v2 API orders on the Shopify-connected store.
- [ ] Make sure the Make it yours products' Printful sync variants are ignored. (The 39 Aquatic name tees are already ignored: `printful_link.py --only aquatic`.) If they aren't, Printful auto-imports a blank duplicate order.
