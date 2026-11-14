# Custom orders pipeline

Custom shirts bought on DoolittleScuba.com become **Printful drafts automatically**.

Three products are in the job:
- the **Make it yours tee**;
- the **Make it yours cap** (Flexfit 6277, embroidered);
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

## Caps and the digitization fee

Eric's rule (14 Nov): pass the digitizing charge to the customer the first time a design is stitched.
- **The fee is Printful's own digitization charge + $0.50.** Printful charges $6.50 for the first new embroidery file and $2.95 for each further one.
- **It is charged once per design, however many caps.** 5 identical caps pay 1 fee. The same artwork on a cap and on a jacket is 2 digitizations, so 2 fees.
- **Shopify product:** "Embroidery digitization — one time per design" (handle `embroidery-digitization`, product 10434482700474). It ships nothing.

| SKU | Covers | Price |
|---|---|---|
| `DS-DIGI-1` | 1 new placement | $7.00 |
| `DS-DIGI-2` | 2 new placements | $9.95 |
| `DS-DIGI-3` | 3 new placements | $12.90 |

**What counts as new on a cap.** Only **"Your line"** creates a new stitch file. It can go on the front, the back, or both (both = 2 placements).
- These reuse existing catalog cap files, so they carry no fee:
  - site blocks;
  - The Mark, the Seal, the Stack and the Wordmark fronts;
  - the side DS mark;
  - the "DO A LITTLE / SCUBA" back;
  - a DS mark on the back (the side file).

**Cap branding (Eric, 14 Nov):**
- Every custom cap carries Doolittle Scuba branding: a DS front (The Mark, Seal, Stack or Wordmark) or the DS mark.
- **The DS mark on the side is preferred.** It is the default, and the page puts it there whenever branding is missing.
- No seal on the side; the side is the DS mark or nothing.
- A customer logo (front or back) always gets the DS mark on the side.
- The job holds a cap with no branding.

**Logo caps** stay a **wholesale quote by email**. The page and the quote state the logo's digitization (the same rule, once per design, and not again for a logo already digitized).

**On /custom/:**
- Cap quantities are entered per size, S/M and L/XL.
- **Add to cart** adds the cap lines (tier A $40, tier B $41 with a line). It also adds **one** `DS-DIGI-n` line for the design.
- A back line over about 20 characters disables Add to cart. The back is 2 in wide and letters must be at least 0.25 in tall.

**The job (`tools/custom_cap.py`):**
- Sends catalog files by their CDN URL and new text files once per design. The S/M and L/XL lines share the same upload, so Printful digitizes once.
- Uses thread colours as a layer option, flat (no 3D puff).
- Checks the fee:
  - **missing or short:** the order is held (`fee`);
  - **paid twice** (the same design added to the cart twice): the draft goes ahead, and the issue says how much to **refund**.

## Holds

Some orders need a person, so the pipeline sends nothing to Printful and reports the reason (`reason_kind`) instead:

| reason_kind | When |
|---|---|
| logo | The chest is a customer logo. These are wholesale quotes, so they are never automatic. |
| home-port | A Home Port design. |
| no-design | The line has no `_design` property. |
| name | An Aquatic name tee with a missing name, or a name too long (12 characters for one name, 10 each for two). |
| fee | A cap design with a new line but no digitization fee in the order. |
| cap-text | A cap line too long to stitch at the 0.25 in letter floor. |
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
3. **Make it yours cap** is live (drafts only), as of 14 Nov, with the digitization fee.
   - Tested locally:
     - a two-line cap in S/M + L/XL with the fee paid;
     - a missing fee (held);
     - a fee paid twice (refund flagged);
     - a site cap with no fee;
     - a cap + tee order;
     - a logo cap (held).
   - The page was tested in headless Chrome: 5 caps + $9.95 = $214.95, and one fee line is posted.

## Before the first real order

- [x] Name fields on every name tee. The live theme's `product.personalized` template carries the "Personalize (names)" block; it reads the `personalize:1 / buddy / couple` tags.
  - The 39 regular tees already used it.
  - The **39 organic twins did not**: their template suffix was empty, so no name boxes showed. All 39 were set to `personalized` on 14 Nov, 05:50.
- [ ] Name rules on the product page (Eric, 14 Nov). `shopify-theme/blocks/aquatic-personalize.liquid`:
  - **Missing names:** a name can't be missing. Every add-to-cart path is guarded with a note, and express checkout is hidden on name tees.
  - **Long names:** allowed up to 20 characters (one name) or 16 each (two names). The standard is 12 / 10.
    - Past the standard, the page explains the resize or two-line setting and what it can mean (smaller letters, a different line break, the joke sitting lower).
    - The buyer must tick to agree, which adds the property **Name fit**.
  - **Waiting on:** write access to the live theme. The chat connector is refused on the published theme. Add `write_themes` + `read_themes` to the Doolittle Order Bot app, then run Actions → **Theme push** (dry run, then apply).
- [x] **Fit and flag (job):**
  - `aquatic_print.fit_report()` compares the buyer's names with a standard-length name.
    - Front shrinks to 80 %, then the line wraps to two lines instead. Back wraps and shrinks.
    - Below 60 % the order is held for a hand edit.
  - Any change is a **design edit**: the Printful item is named **⚠ DESIGN EDIT · …** and the GitHub issue title ends **· ⚠ DESIGN EDIT**. The issue lists what changed (no names, public repo).
- [ ] One test name-tee order: check the names arrive as line properties and the job drafts it.

- [ ] Place a test order through Add to cart. This needs the storefront password preview or the launch.
- [ ] Check that the order query can read the shipping address. Protected customer data may hide it; if so, the order is held as `no-address`.
- [ ] Check that Printful accepts v2 API orders on the Shopify-connected store.
- [ ] First cap draft:
  - check that Printful places the catalog files as the synced caps do (position = file size, fitted to the area);
  - check whether reusing a catalog file's URL is charged digitization again. If it is, the fee rule needs a look.
- [ ] Make sure the Make it yours products' Printful sync variants are ignored. (The 39 Aquatic name tees are already ignored: `printful_link.py --only aquatic`.) If they aren't, Printful auto-imports a blank duplicate order.
