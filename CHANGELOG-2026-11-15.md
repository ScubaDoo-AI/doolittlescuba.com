# Changelog — 15 Nov 2026

## Footer contact line (from the Doolittle Scuba L.L.C. contact card)
- Every page footer now reads **shop@doolittlescuba.com** (tappable mailto). It replaces `hello@ · orders@`.
- **The business phone is not listed anywhere on the site (Eric, 15 Nov).** It was added briefly and removed the same day.
- Clicks are tracked in Umami as `contact` events (`via` = email).
- The page generators (`tools/line_pages.py`, `tools/stickers_page.py`) and the policies footer anchor (`tools/policies.py`) carry the new line, so regenerated pages keep it.
- Home page Organization JSON-LD: email → shop@.
- Social links already matched the card (Instagram, Facebook, TikTok, X). No change.

## Still open
- Other spots on the site still use hello@ (home page forms and the "Email us your photo" links) and sales@ (custom orders). Change them only if the inboxes are being consolidated.
- The card's mailing address (8735 Dunwoody Place, Ste N, Atlanta) already appears in the refund policy. The footer still reads "Based in Newnan, Georgia".
