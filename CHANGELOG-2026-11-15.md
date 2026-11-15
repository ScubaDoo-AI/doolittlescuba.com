# Changelog — 15 Nov 2026

## Footer contact line (from the Doolittle Scuba L.L.C. contact card)
- Every page footer now reads **shop@doolittlescuba.com** (tappable mailto). It replaces `hello@ · orders@`.
- **The business phone is not listed anywhere on the site (Eric, 15 Nov).** It was added briefly and removed the same day.
- Clicks are tracked in Umami as `contact` events (`via` = email).
- The page generators (`tools/line_pages.py`, `tools/stickers_page.py`) and the policies footer anchor (`tools/policies.py`) carry the new line, so regenerated pages keep it.
- Home page Organization JSON-LD: email → shop@.
- Social links already matched the card (Instagram, Facebook, TikTok, X). No change.

## "By hand" cut back across the site (Eric, 15 Nov)
The hand-made line was on nearly every page. It now appears in just a few places:
- **Kept:** the home hero ("Dive art, drawn by hand."), the Signature Series hero and share title, the Signature share-image alt text (it matches the baked image), the About line "Start from a blank sheet, do it by hand", the Workshop project notes (the hood map and the stamped tags), and the copyright footer on the print art.
- **Reworded:** "Five lines, one hand" → "one artist" (home + every collection page); "Every mark by hand" → "Every mark original"; the Signature tile is now "Dive sites, plate by plate" (new `tile` field in `tools/line_pages.py`, so the hero keeps its tagline); the meta descriptions of the 12 site guides; the About page and the Certified-ish and Signature design intros.
- **Corrected:** "printed by hand (in Newnan)" / "pressed by hand" → **"printed to order" / "pressed to order"**. Printful prints the shirts, so the old line wasn't accurate. Changed in the shirt and cap spec panels (`js/deck.js` + `tools/darkline.py`, `certdarkline.py`, `hats_v2.py`), the craft facts, Make it yours, `tools/offworld_shopify.py`, and the refund and shipping policy sources.
- "Checked by hand" lines in the policies and the Aquatic personalize block now read "we check every custom design".
- **Follow-up (Eric):** the Signature Series and Certified-ish art really was drawn by hand, so "drawn by hand" is back on those two lines: the Signature tile on every page, both design intros, the home "Every mark by hand" craft section (Signature plates) and the About line on Eric's plates. The `tile` field in `tools/line_pages.py` is gone again. **Rule from here:** "by hand" goes only on Signature Series and Certified-ish art. "Printed by hand" stays corrected to "printed to order."

### Not live yet
- **Policies:** run Actions → **Policy push** to send the new refund and shipping text to Shopify.
- **Shopify product descriptions:** the Off-World products already in Shopify still say "printed by hand in Newnan, Georgia". The generator is fixed, but the products need a re-push.
- **Theme block:** `shopify-theme/blocks/aquatic-personalize.liquid` changes when the theme is next pushed.

## Screen printing references removed (Eric, 15 Nov)
- The shirts are printed to order by Printful, not screen-printed. "screen-printed" → "printed to order" in the home page meta and share descriptions and the Signature Series description (meta, share card, JSON-LD, and its generator `tools/line_pages.py`).
- Left alone: the old match string in `tools/darkline.py` (a one-off patch script; it doesn't put copy on the site).

## Shopify product descriptions fixed (Eric, 15 Nov)
All 130 tee and cap descriptions that said "printed by hand in Newnan, Georgia" now say **"printed to order"**, edited directly in Shopify (Admin API, in batches). That covers Signature Series light and dark (28), Certified-ish light and dark (40), Off-World Hunt Club light and dark (60), Make it yours, and the Home Port cap ("Where the shirts are printed." → "Home port for Doolittle Scuba."). The Signature site intros now read "dived and drawn for the Doolittle Scuba line"; "drawn by hand" stays on the plate backs and the Certified-ish art. Organic, 1N73LL1G3NC3, Aquatic Comic and sticker descriptions had none of this wording.

### Policies: run Policy push
The connection can't write store policies (`write_legal_policies`), so they're staged here:
- `policies/refund.html` and `policies/shipping.html`: "pressed by hand" and "by hand" removed, dated 15 Nov.
- **New `policies/terms.html`**: a copy of the live Terms with §4 changed from "Our designs are hand-drawn and each shirt is pressed or printed individually" to "Each shirt is printed to order individually". Dated 15 Nov.
- To publish: Actions → **Policy push**, policies `refund shipping terms`, Apply on.

## Final per-series prices on the website (evening, 15 Nov)
The Company project repriced the store on 15 Nov. The site now shows the same prices. They were rebuilt here from the Company project's price table, because its patch never reached GitHub. Shopify was spot-checked and matches.
- **Tees** (S–XL; 2XL and 3XL are $3 more): Signature $42, Certified-ish $40, Off-World $38, Aquatic Comic · Boat Banter $38, 1N73LL1G3NC3 $36, personalized Aquatic Comic $45. In `js/deck.js` they live in one table, `DS.TEE_PRICE`, with the helpers `DS.teePrice` / `DS.teePriceLine`. The cards and the spec panels read the price by line.
- **Organic page:** tees are the line price + $3 (Signature $45, Certified-ish $43, Off-World $41, Boat Banter $41, 1N73LL1G3NC3 $39), organic personalized $48, organic site caps $40, organic brand caps $38, organic beanie $32. "Same price" now reads "a few dollars more" on the page, in its meta tags, on the home tile, in the deck footnote and in `tools/organic_site.py`.
- **Home page:** site caps $38, brand caps $36, Home Port cap $48, The Mark beanie $32, anorak $85, windbreaker $45 ($88 / $48 in 2XL).
- **Pairs:** $72 ($75 in 2XL–3XL) on the deck button, the 14 site guides and the search index. Updated in `tools/pairs_site.py` and `tools/pairs.py` ($38 cap + $42 tee, $8 under the two apart).
- `tools/offworld_shopify.py`: PRICE now $38 / $41.
- **Not changed:** the Printful pricing scripts (`tools/printful_*.py`), which the Company project owns. The custom page ($47 / $48 tee, $40 / $41 cap) already matched.

## Theme and Make it yours (evening, 15 Nov)
- **`shopify-theme/assets/ds-organic.js`** (and its raw copy): "same art, same price" is now "same art, a few dollars more". Not pushed yet; the repo copy matched the live theme before the edit.
- **Home Port files copied in from the live theme:** `shopify-theme/blocks/home-port-picker.liquid` (identical to the live file, md5 45c99152…) and `shopify-theme/templates/product.home-port.json` (same content; the live copy is stored a little smaller, so its md5 differs).
- **Make it yours tee (Shopify):** the description now reads $47 ($50) = the $42 catalog tee + $5, and $48 ($51) with a line or logo. Logo files go to **shop@**.
- **To publish the theme changes:** Actions → **Theme push**, files `assets/ds-organic.js blocks/aquatic-personalize.liquid`, Apply on. The live copies of both files were confirmed identical to the repo's previous versions, so nothing else gets overwritten.

## Retired name removed (Design & Production brand rule, 15 Nov)
- "diveplate" was still in customer-facing copy: the footer on 8 pages ("diveplate designs © 2026 …" → "Designs © 2026 Doolittle Scuba L.L.C.") and the home page meta description. Both are fixed, and so are the generators `tools/line_pages.py` and `tools/stickers_page.py`. Internal CSS classes and analytics names still say diveplate, as the Design & Production review allows.

## Company corrections note applied (late 15 Nov)
- **Dive rating:** the home page now uses the full title, "PADI Master Scuba Diver(s)", in the meta/share description, the hero line, the craft section, the About heading and the About blurb. The About page already used it. The sticker names "Master Diver" are product and artwork titles, so they stay. No page says "instructor" (except "We are not instructors") or "co-owner".
- **Organic pricing:** closed. Tees are the line price + $3 and caps + $2 (decided by Eric, 15 Nov). The site already matches: organic site caps $40, organic brand caps $38.

## Eric's decisions D1–D8 applied (late 15 Nov; Company "Decisions from Eric" v3)
- **D4, email:** every hello@, sales@ and **orders@** on the site is now **shop@doolittlescuba.com**. That covers the launch banner on every page (and `tools/status_flag.py`), the suggestion and launch forms, the "Wear it where you dove" link, the Dive shops card, the custom-shirt and commission forms, and the wholesale logo request. orders@ is now the vendor address (D3), so it no longer appears on the site. On Shopify, the Make it yours cap's description now sends logo files to shop@; it also drops a "$35 site cap + $5" sum that no longer added up (the prices stay $40 / $41). Theme and policies had no other addresses. The hello@ and sales@ forwards stay on at Porkbun.
- **D5, headline:** the home page now reads "Dive art and sites, drawn by hand."
- **D6, beanie:** The Mark (regular) is now French Navy only on Shopify. The Black variant and its image were deleted; the description, tags and the "sherpa jacket" mention were updated. It is now **Active** and published to the same channels as the organic beanie, at $32. On the home page the card is French Navy only, with no colour flip, and the specs say $32.
- **D8, pairs:** the 14 site guides now say "Any tee with any cap is $8 off the two apart. This site's pair: the X cap with the light tee or the dark tee, $72 ($75 in 2XL–3XL)." The home caps note adds "Any cap with any tee is $8 off the two apart." `tools/pairs_site.py` and the search index were updated to match. The 28 matched pair bundles stay as featured examples. **The mix-and-match discount itself is the Company project's to set up**: a Shopify automatic discount that excludes the bundles, with Eric's approval. Until it exists, an unmatched tee and cap get no discount at checkout. The store is still behind its password.
- The home page's Home Port blurb said "Where the shirts are printed"; it now says "Home port for Doolittle Scuba".
- D1, D2 and D3 needed no site change: the jackets on the site were already the anorak and windbreaker.

## Policy push and Theme push run (15 Nov, 18:00 ET)
- Both were dispatched through the GitHub REST API, as a dry run and then with Apply on.
- **Policy push** (`refund shipping terms`): all three written. Checked in Shopify: the live Refund, Shipping and Terms are dated 15 Nov and no longer say "by hand" or "hand-drawn".
- **Theme push** (`assets/ds-organic.js blocks/aquatic-personalize.liquid`): both written to the live theme "Horizon — Doolittle Scuba (Home Port map v2)". The organic cart converter now reads "same art, a few dollars more".

## D8 discount checked (15 Nov, 18:07 ET)
"Mix & match: tee + cap $8 off" (automatic, buy-1-get-$8-off) starts 15 Nov at 18:10 ET. It covers the "All tees (pair discount)" collection (447, every active tee) and "All caps (pair discount)" (57). None of the 28 pair bundles is in either collection, so no order gets $16 off. There is no per-order limit, so it applies once per tee + cap pair, and it combines with no other discount. The site copy ("Any tee with any cap is $8 off the two apart") now matches the store. Still to do (Company): one test order with an unmatched tee and cap.

## Still open
- Other spots on the site still use hello@ (home page forms and the "Email us your photo" links) and sales@ (custom orders). Change them only if the inboxes are being consolidated.
- The card's mailing address (8735 Dunwoody Place, Ste N, Atlanta) already appears in the refund policy. The footer still reads "Based in Newnan, Georgia".
