# Changelog — 4 Nov 2026

## Shop-status flag
- New strip across the top of every page (home, About, Workshop, Make it yours, all 15 dive-site guides): **Shop status · Proofing** — physical samples are being spot-proofed for print, colour and fit before the shop opens; designs stay "Coming soon" until they pass.
- Links to sales@doolittlescuba.com ("Get word when it opens"); dismissible per visitor, and reappears when the status `id` changes.
- Umami events: `status-flag-notify`, `status-flag-dismiss`.
- Managed by `tools/status_flag.py` — edit `STATUS` and run it to update every page; `--off` removes the flag at launch.

## Status flag — bolder, scales with the screen
- Strip is now brand red with white text, a white "● PROOFING" pill (gentle pulse, off for reduced-motion), bolder link and close button.
- All sizes scale with the window (about 15px text on a laptop up to about 21px on a 2560-wide monitor) and the content widens to fill large screens instead of sitting in a narrow line.

## Wide-screen scaling (every page)
- Big monitors at 100% browser zoom now scale the whole page up instead of showing a narrow column with tiny type: 1.15× from 1800px wide, 1.3× from 2100px, 1.5× from 2400px, 1.75× from 3000px, 2× from 3600px. Phones, tablets and laptops are unchanged.
- Managed by `tools/wide_screen.py` (edit `STEPS`, re-run; `--off` removes it). The status flag compensates so it doesn't double-scale.
