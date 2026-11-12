# Change log — 11 November 2026

## Caps: embroidered site fronts in the store, 12 caps on Printful

Eric, 11 Nov (caps Project): *"Let's add the 14 front signature series shirt designs to the caps embroidery."* then here: *"Build the printful and Shopify embroidered caps."*

### Store — 19 cap products
- New front + back mockups on all 19 Dark caps: the site front (torn-edge dive flag over the site name and coordinates) embroidered, the DS mark on the side, "DO - A - LITTLE" arched over SCUBA on the back. The Mark's side and The Stack's side and back are plain, as the listings say. Old media deleted.
- Site-cap descriptions rewritten for the embroidered front (threads named per flag); tags `front:embroidered` + `site-cap` (brand caps `brand-cap`); the Site Caps and Brand Caps collections re-keyed on those tags (15 / 4). Prices unchanged. Home Port stays custom (`fulfil:custom`).

### Printful — 12 caps linked, 0 failures
- `tools/printful_caps.py` (new) plans the 12 caps whose Flexfit 6277 colour Printful stocks (Dark Navy, Dark Grey, Black, Olive); `tools/printful_link.py` gained the `caps` line and sends item-level options (thread colours, flat embroidery); the Printful link workflow lists `caps`.
- `tools/check_connections.py` now reads the 6277's printfile templates: front 5.90 × 2.00 in, side and back 2.00 × 1.00 in. The print masters in Shopify Files were built to those sizes — which forced a 0.92 × 1.00 in side mark and a straight two-line back on the Printful caps only. Sample before publishing.
- The renders live on the branch `caps-embroidered-2026-11-11` under `renders/caps-2026-11-11/` (the store imported them from there). The home page's `img/hats/dark/` and hats copy are still the 24 Oct DTF-style set — a separate pass.

Full ids, file names and the compromises: `SHOPIFY-STORE.md`, 2026-11-11.

## Evening — Eric's answers: sample staged, DTF option gone, coordinates corrected, merged
- **Price** stays $35 / $40. **Printful sample** staged as draft order 186447389 (Blue Water Park, Black, L/XL): $22.41 + $5.09 shipping + $12.40 one-time digitization + $3.21 tax = $43.11, unconfirmed. The Sample order job now takes the caps and has a `show` mode.
- **No more DTF caps:** `tools/hats_v3.py` put the embroidered-front renders in the home page deck and rewrote the hats copy and spec sheet; Home Port is embroidered to order (store tags and description updated).
- **Coordinates:** seven sites' website and store values were brought up to the chest blocks, which checked out against the ground; Dive Land Park moves from "Ider" to Glencoe, AL. 28 store descriptions and the site's own data, guides and plates updated.
- **Merged to main** (126d842), live. Open: the Navy LLCAT front reads "Hovercraft (LLCAT)".

Full ids and details: `SHOPIFY-STORE.md`, 11 Nov evening.

## Late — the decks roll properly on every screen

Eric: *"Stickers scroll extremely too fast and caps and shirts don't rolling scroll only click to pull forward."*

The cause: the deck mapped its **whole scroll range** onto the cards. A deck that barely overflowed the screen (the 26 themed packs on a tablet or a 1100 px desktop) flipped through all 26 within a few pixels of scroll, while a deck that fit the screen (hats, shirts) never scrolled, so a finger could not roll it at all — only a tap pulled a card forward. On desktop, hovering also jumped several cards at a time because the lifted card covered its neighbours' tabs. And on desktop the 30-card Off-World lines overflowed with no scrollbar, so the last ten were unreachable with a mouse.

`js/deck.js`, one change of model:
- **Tabs fit the width.** A line keeps its own tab width when the whole deck fits; when narrower tabs would make it fit (down to 26 px) it uses those — Off-World's 30 now sit at 28 px on a desktop, all reachable; the packs at 33 px. Only when even that overflows (phones) does the deck scroll, and then at no less than **48 px of scroll per card** so a swipe rolls at a readable pace. Re-fitted on resize.
- **Rolling is geometric.** On a deck that fits, the card under the pointer's x pulls forward — the mouse running across the tabs, or a finger dragged across them (`touch-action: pan-y`, so vertical swipes still scroll the page) — one card per tab, no jumps, in order. On a deck that scrolls, the card whose body is in the middle of the screen steps forward, one card per tab width.
- Hints say which: *run across the tabs* (mouse), *drag a finger across the tabs* (touch, fitted), *swipe the deck* (touch, scrolling).

Checked by script at 1440, iPad landscape (finger drag rolls the hats 14→0 and the packs 25→0 one by one) and iPhone (56 px per cap, 48 px per pack). No visual change to the cards themselves beyond narrower tabs where a deck now fits.

### Later — the phone deck no longer bounces

Eric: *"Sticker scroll bounces back to screen centered item can not see last couple of designs."*

On a phone the deck still relied on the browser's own momentum scrolling, and the cards change layout as they step (the lifted card, its tag) — Safari answers that by snapping the scroll position back, so the end of the deck could never be reached. Native scrolling is gone from the decks now. A deck that cannot fit the screen is a **drag-rolled strip**: a finger (or a mouse, on a narrow window) dragged across it rolls the cards one per 48 px of travel, a flick carries on a little further, and the strip slides to keep the pulled card in the middle of the screen — so the last card is reached by construction. Vertical swipes still scroll the page; a tap on a tab pulls it forward and centres it; a tap on the pulled card opens it. Decks that fit the screen are unchanged (the card under the pointer or finger). Checked at iPhone width by script: 26 packs rolled end to end in three flicks, the hats likewise.

### Last thing — the filler proofs, and the Achievement set as the opener

Eric, 23:38: *"Update the sticker image files on the website match New prints with the space-filler stickers"* with 20 new proofs; then *"Achievement pack should be opener at $15"* with his render of the full set.

- **20 of the 37 packs have new proofs** with small filler stickers in the sheet's spare space: Reef Cuties, Lazy Reef, Bubble Puns, Dive Computer Says, Kit Bag, Gear Up, Reef Pros, Wreck Divers, Retro Patches, Atlantic & Red Sea, Ocean Pledge, Deep Weird, Ocean Masterpieces, Art History Dive, Pre-Dive Check, Turtle Trio, The Deep End, Specialty Mix, Classic Trio, Navy Trio. Each was matched to its pack by the name strip at the foot of the sheet (nearest-match gap ≥ 6 px of mean difference, no ambiguity). Site proofs, thumbs, the hero trio and the share image rebuilt; `fillers: true` in `tools/packs.json`; cards say *Three stickers + fillers*. The other 17 packs keep the three-sticker proofs until their new sheets arrive. **The print masters in Shopify Files are still the three-sticker sheets** — the 300 dpi masters with the fillers are needed before Printful prints them.
- **The Achievement set is the opener.** The full set (store SKU `DS-STK-A-SET12`, product `achievement-unlocked-full-set`, already $15) is now the first line of the packs deck — chip *Achievement set* — and the card the deck opens on, on `/stickers/` and the home page: tag *Achievement set · Achievement Unlocked · All twelve badges + five extras · $15 · Open*; the panel lists the twelve badges and the five extras (Achievement Hunter, 100% Complete, the seal, the horizontal logo, Do A Little Scuba). Its proof was built in the pack format from the twelve badge masters and the five header stickers cut from Eric's render (`img/packs/achievement-set.webp`). The A5 master in Shopify Files is still the twelve-badge layout; the seventeen-sticker sheet needs a new master (the two badge extras exist only in the render).
- `deck.js`: `start` and `footNote` may be given per line (`start:{set:0}`), so only the set line opens pulled forward. `stickers_page.py`: the `set` line, per-pack prices (`price` in packs.json), `og()` rebuilds the share image.
- Also received, parked at `/home/claude/stickers_in/six_sheets/` (not in the repo): nine distinct 5 × 7 in **six-sticker sheets** — Sea Critter Cafe (two versions, one with DS marks on the stickers), Vintage Dive Badges, Reef Guardians, Ocean Through Art History, Deep Weird, Wreck and Cave, Bucket List Destinations, Dive Science — with magenta kiss-cut contours. No instruction came with them; nothing on the site uses that layout yet.

### 01:11 — eight more filler sheets

Sixteen more proofs: eight new packs (Do A Little Scuba, Red Trio, Master Diver, Pun Pack, The Seal Set, Black Trio, Chill Dives, Certified) and eight repeats of earlier sheets, byte-identical to what was already in. Site and store images swapped the same way. **28 of 37 packs** now show the fillers; still on the three-sticker proofs: Diver Truths, Critter Cafe Crew, Into the Dark, Vintage Classics, Pacific Bucket List, Reef Heroes, Strange Beauty, Dive Science 101, Octopus Trio. Eric is sending the rest.

### 01:14–01:20 — the print files: every pack as a 4 × 6 kiss-cut PDF

Eric sent `DS-PK-<xx>_<Name>_4x6_kisscut.pdf` for all 37 packs (ReportLab PDFs: a 4 × 6 in page, the sheet art as one 1200 × 1800 300 dpi image with transparency — three stickers, the fillers and the pack name — plus the kiss-cut paths in a **CutContour** spot colour), and the twelve achievement badges, which were pixel-identical to the masters already on hand.

- **Site proofs**: all 37 re-rendered from the PDF art composited on white (the nine that still had three-sticker proofs — Diver Truths, Critter Cafe Crew, Into the Dark, Vintage Classics, Pacific Bucket List, Reef Heroes, Strange Beauty, Dive Science 101, Octopus Trio — now show the fillers; the other 28 differ from the JPG proofs by under 1.5 mean grey levels, i.e. the same picture from the source). Hero trio and share image rebuilt. `packs.json` records each pack's `print` file and `print_file_id`.
- **Site copy**: the pack sheet is **4 × 6 in** now (hero, packs intro, card captions, deck specs); the Achievement set still says 5.83 × 8.27 because its sheet is unknown.
- **Store**: the nine product images swapped (37 of 37 now show the fillers); the 37 PDFs are in Shopify Files as `files/DS-PK-<xx>_<Name>_4x6_kisscut.pdf` (GenericFile ids 47395530670266 → 47395531849914, +32768 per pack in B01–B06, C01–C05, T01–T26 order). Product descriptions still say 5.83 × 8.27 in — to change once the vendor is settled.
- **Open**: the 4 × 6 kiss-cut PDFs are not Printful's sheet (Printful's is 5.83 × 8.27, product 505). Which printer are they for? If Printful stays, the full-sheet masters can be rebuilt from the 4 × 6 art; `tools/printful_packs.py` carries the note.

### 01:40 — Sticker Mule, confirmed; the Printful plan for the packs retires

Eric: *"Yes these were for sticker mule."* So the packs are a bulk-printed, stock-held product, not print-on-demand.

- **Store copy** on all 37 packs rewritten and tagged `print:sticker-mule-4x6`: *Three kiss-cut stickers and a few small fillers on one 4 × 6 in sheet: Name, one of the Doolittle Scuba themed packs* (classic and brand packs list their three stickers instead) · *Printed vinyl, glossy film, waterproof · the DS mark on every sticker.* "Printed on demand" and 5.83 × 8.27 are gone from the descriptions. Checked back: 37 of 37 carry the tag and the new text.
- **Printful retired for the packs.** `tools/printful_packs.py` deleted; its Shopify product and variant ids moved into `tools/packs.json` (`shopify_product` / `shopify_variant` on every pack, and on the Achievement set); `packs.json` now says who prints them (`printer`) and what `print` / `master` are. `tools/printful_link.py` lost its `packs` line (default list, name match, targets), the Printful link workflow its `packs` option, and the README its "Printful plan" sentence. The `files/DS-PK-xx.png` masters in Shopify Files are the superseded Printful layouts — left in place, sent nowhere.
- **For Eric:** (1) since the sheets are printed in bulk, the 37 pack variants should track inventory (they are "continue selling, no tracking" now, which was right for print-on-demand); say the word and the quantities, and I'll turn it on. (2) The Achievement set is still the one pack without a print file — Sticker Mule will need a 4 × 6 (or whatever size) kiss-cut PDF of the seventeen-sticker layout; only your render exists. (3) The nine six-sticker 5 × 7 sheets are still parked; nothing on the site or in the store uses them.

### 01:41 — the Achievement set is a UV DTF sheet from Ninja Transfers

Eric, with the gang sheet: *"15 on these uv stickers gang sheets were ordered from ninja transfers 8 sets each."*

- The file he sent is the print file itself: a **22 × 24 in UV DTF gang sheet** at 300 dpi (6600 × 7200, transparent ground) carrying **eight Achievement sets** in two columns of four. One set is **10.7 × 5.7 in**: the twelve badges at 3.47 × 1.08 in and the five headers 0.77 in tall (the seal round; the horizontal logo 2.36, Achievement Hunter 2.54, Do A Little Scuba 2.07, 100% Complete 2.02 in wide). Fifteen sheets = **120 sets**. So the one pack that had no print file now has one, and it is not a kiss-cut sheet at all — UV DTF stickers are rub-on transfers (peel the film, press, rub, lift; no clear border).
- **Site**: the set's card caption, deck foot note, panel caption and specs now say *seventeen UV DTF rub-on stickers on one 10¾ × 5¾ in sheet*, with a *Finish* row explaining the rub-on (`tools/stickers_page.py`, `js/deck.js`); 5.83 × 8.27 is gone from the site. Live at 01:5x (deck.js hash 15ce6946, probed after publish).
- **Store**: `achievement-unlocked-full-set` rewritten (seventeen UV DTF stickers, how to apply, badges 3½ × 1 in, headers ¾ in), tag `print:ninja-transfers-uv-dtf`. The gang sheet is in Shopify Files as `files/DS-STK-A-SET12_Achievement-Unlocked_UV-DTF-gang-22x24_8-sets.png` (MediaImage 47395653058746; `packs.json` "print" / "print_file_id" / "print_note"). The variant already tracks inventory at a placeholder 100; the real figure is 120 once the sheets arrive.
- The packs' `uv_sheet` field in `packs.json` (sheet1…) predates this and is from the print package's index — it says nothing about Ninja Transfers.

## 12 Nov, small hours — Navy LLCAT
Eric: the front reads **Navy LLCAT**. Chest print files (both inks) and the embroidered cap front rebuilt with the new title, uploaded, Printful re-linked for the 14 Navy LLCAT variants (0 failures), the cap's store image and the site's render replaced, the embroiderer pack updated. Details: `SHOPIFY-STORE.md`, 12 Nov.

## 12 Nov — The pairs
28 set products (cap + tee of the same site, light and dark tee) as Shopify fixed bundles at $69 / $72, combined mockups, a Pairs collection; the pair line on every site cap and Signature tee page; **Add the pair** on every site guide and site cap on the home page. Untested with Printful until the first pair order. Details: `SHOPIFY-STORE.md`, 12 Nov.
