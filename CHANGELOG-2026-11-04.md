# Changelog — 4 Nov 2026

## Shop-status flag
- New strip across the top of every page (home, About, Workshop, Make it yours, all 15 dive-site guides): **Shop status · Proofing** — physical samples are being spot-proofed for print, colour and fit before the shop opens; designs stay "Coming soon" until they pass.
- Links to sales@doolittlescuba.com ("Get word when it opens"); dismissible per visitor, and reappears when the status `id` changes.
- Umami events: `status-flag-notify`, `status-flag-dismiss`.
- Managed by `tools/status_flag.py` — edit `STATUS` and run it to update every page; `--off` removes the flag at launch.
