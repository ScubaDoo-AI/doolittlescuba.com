# Changelog — 13 Nov 2026

### 10:33 — the four store policies, linked from every footer

Eric: *"It has no privacy, terms, shipping or returns links in the footer, even though all four policies are now in Shopify."*

- Shopify holds Privacy, Terms of service, Shipping and Refund policies (`shop.shopPolicies`). The storefront is password-protected, so `doolittlescuba.myshopify.com/policies/…` bounces to the password page; the **checkout-hosted copies** (`checkout.shopify.com/78733508794/policies/<id>.html`) are public and are what the site links.
- New `tools/policies.py`: writes four redirect pages — **/privacy/, /terms/, /shipping/, /returns/** (noindex, meta refresh + script, the same pattern as /youtube/) — and puts a footer line between `POLICIES` markers under the email line on every page with a footer (26 pages: home, the collections, about, custom, workshop, stickers, organic, the 15 site pages). Idempotent; re-run after adding a page. `line_pages.py` and `stickers_page.py` now carry the block from the home page like the social block, so regenerating keeps it.
- CSS: `.foot-meta .policies` — small mono uppercase, underlined links, right-aligned on desktop, left on phones. Checked at 1280 and 390; `/returns/` lands on the Shopify refund policy.
- README gained a *Store policies* paragraph.
