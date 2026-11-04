# Changelog — 4 Nov 2026

## Shop-status flag
- New strip across the top of every page (home, About, Workshop, Make it yours, all 15 dive-site guides): **Shop status · Proofing** — physical samples are being spot-proofed for print, colour and fit before the shop opens; designs stay "Coming soon" until they pass.
- Links to sales@doolittlescuba.com ("Get word when it opens"); dismissible per visitor, and reappears when the status `id` changes.
- Umami events: `status-flag-notify`, `status-flag-dismiss`.
- Managed by `tools/status_flag.py` — edit `STATUS` and run it to update every page; `--off` removes the flag at launch.

## Status flag — bolder, scales with the screen
- Strip is now brand red with white text, a white "● PROOFING" pill (gentle pulse, off for reduced-motion), bolder link and close button.
- All sizes scale with the window (about 15px text on a laptop up to about 21px on a 2560-wide monitor) and the content widens to fill large screens instead of sitting in a narrow line.
