# Changelog — 15 Nov 2026

## Footer contact line (from the Doolittle Scuba L.L.C. contact card)
- Every page footer now reads **shop@doolittlescuba.com · (770) 828-8899**, both tappable (mailto / tel). It replaces `hello@ · orders@`.
- Clicks are tracked in Umami as `contact` events (`via` = email / phone).
- The page generators (`tools/line_pages.py`, `tools/stickers_page.py`) and the policies footer anchor (`tools/policies.py`) carry the new line, so regenerated pages keep it.
- Home page Organization JSON-LD: email → shop@, telephone added.
- Social links already matched the card (Instagram, Facebook, TikTok, X). No change.

## Still open
- Other spots on the site still use hello@ (home page forms and the "Email us your photo" links) and sales@ (custom orders). Change them only if the inboxes are being consolidated.
- The card's mailing address (8735 Dunwoody Place, Ste N, Atlanta) already appears in the refund policy. The footer still reads "Based in Newnan, Georgia".
