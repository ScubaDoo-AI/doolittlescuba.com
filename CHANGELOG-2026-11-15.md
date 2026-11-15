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

## Still open
- Other spots on the site still use hello@ (home page forms and the "Email us your photo" links) and sales@ (custom orders). Change them only if the inboxes are being consolidated.
- The card's mailing address (8735 Dunwoody Place, Ste N, Atlanta) already appears in the refund policy. The footer still reads "Based in Newnan, Georgia".
