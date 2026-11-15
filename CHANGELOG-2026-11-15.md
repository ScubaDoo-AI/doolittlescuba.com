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

### Not live yet
- **Policies:** run Actions → **Policy push** to send the new refund and shipping text to Shopify.
- **Shopify product descriptions:** the Off-World products already in Shopify still say "printed by hand in Newnan, Georgia". The generator is fixed, but the products need a re-push.
- **Theme block:** `shopify-theme/blocks/aquatic-personalize.liquid` changes when the theme is next pushed.

## Still open
- Other spots on the site still use hello@ (home page forms and the "Email us your photo" links) and sales@ (custom orders). Change them only if the inboxes are being consolidated.
- The card's mailing address (8735 Dunwoody Place, Ste N, Atlanta) already appears in the refund policy. The footer still reads "Based in Newnan, Georgia".
