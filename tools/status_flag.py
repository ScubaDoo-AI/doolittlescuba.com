#!/usr/bin/env python3
"""Shop-status flag: one strip across the top of every page.

Edit STATUS below, then run:
    python3 tools/status_flag.py          # stamp/refresh the flag on every page
    python3 tools/status_flag.py --off    # remove it from every page

The block sits between <!-- STATUS:START --> and <!-- STATUS:END --> right after
<body>, so re-running replaces it in place. Changing "id" re-shows the flag to
visitors who dismissed the previous one.
"""
import html, pathlib, re, sys

STATUS = {
    "id": "2026-11-04-proofing",
    "label": "Shop status",
    "state": "Proofing",
    "updated": "Updated 4 Nov 2026",
    "message": ("We're spot-proofing physical samples — checking print, colour "
                "and fit on real shirts and caps before the shop opens. Designs stay "
                "“Coming soon” until the samples pass."),
    "link_text": "Get word when it opens",
    "link_href": "mailto:sales@doolittlescuba.com?subject=Tell%20me%20when%20the%20shop%20opens",
}

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "about/index.html", "workshop/index.html", "custom/index.html",
         *sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("sites/*/index.html"))]
BLOCK_RE = re.compile(r"\n?<!-- STATUS:START -->.*?<!-- STATUS:END -->\n?", re.S)

CSS = """<style>
.ds-status{position:relative;z-index:5;margin-inline:calc(-1 * var(--gut,0px));background:#0E2147;color:#F3F6F9;border-bottom:2px solid #C8202A;font-family:var(--f-body,system-ui,sans-serif);font-size:.9375rem;line-height:1.45}
.ds-status[hidden]{display:none}
.ds-status__in{max-width:1120px;margin:0 auto;padding:9px clamp(16px,4vw,40px);display:flex;align-items:center;gap:10px 14px;flex-wrap:wrap}
.ds-status__tag{display:inline-flex;align-items:center;gap:8px;font-family:var(--f-data,ui-monospace,Menlo,monospace);font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;white-space:nowrap}
.ds-status__tag svg{width:24px;height:16px;flex:none;display:block}
.ds-status__state{color:#0E2147;background:#F3F6F9;border-radius:3px;padding:1px 6px}
.ds-status__msg{flex:1 1 320px;margin:0;color:#DCE5F0}
.ds-status__msg a{color:#F3F6F9;text-underline-offset:3px;white-space:nowrap}
.ds-status__when{font-family:var(--f-data,ui-monospace,Menlo,monospace);font-size:.75rem;color:#A9B9CF;white-space:nowrap}
.ds-status__x{background:none;border:0;color:#A9B9CF;font:inherit;font-size:1.25rem;line-height:1;padding:6px 8px;margin:-6px -8px -6px 0;cursor:pointer;border-radius:4px}
.ds-status__x:hover,.ds-status__x:focus-visible{color:#F3F6F9;outline:2px solid #C8202A;outline-offset:1px}
@media (max-width:560px){.ds-status__in{padding-right:44px}.ds-status__x{position:absolute;top:6px;right:8px;margin:0}}
</style>"""

FLAG_SVG = ('<svg viewBox="0 0 26 18" aria-hidden="true"><rect width="26" height="18" fill="#C8202A"/>'
            '<path d="M0 0h4.5L26 14.5V18h-4.5L0 3.5z" fill="#fff"/></svg>')

JS = """<script>(function(){var b=document.getElementById('ds-status');if(!b)return;var k='ds-status-dismissed',id=b.getAttribute('data-id');
try{if(localStorage.getItem(k)===id)b.hidden=true;}catch(e){}
b.querySelector('.ds-status__x').addEventListener('click',function(){b.hidden=true;try{localStorage.setItem(k,id);}catch(e){}});})();</script>"""


def block():
    s = {k: html.escape(v, quote=True) for k, v in STATUS.items()}
    return (f"<!-- STATUS:START -->{CSS}"
            f'<aside class="ds-status" id="ds-status" data-id="{s["id"]}" role="status" aria-label="{s["label"]}">'
            f'<div class="ds-status__in">'
            f'<span class="ds-status__tag">{FLAG_SVG}{s["label"]} <span class="ds-status__state">{s["state"]}</span></span>'
            f'<p class="ds-status__msg">{s["message"]} '
            f'<a href="{s["link_href"]}" data-umami-event="status-flag-notify">{s["link_text"]}</a></p>'
            f'<span class="ds-status__when">{s["updated"]}</span>'
            f'<button type="button" class="ds-status__x" aria-label="Dismiss shop status" data-umami-event="status-flag-dismiss">&times;</button>'
            f"</div></aside>{JS}<!-- STATUS:END -->")


def main(off=False):
    new = "" if off else block()
    for rel in PAGES:
        p = ROOT / rel
        src = p.read_text(encoding="utf-8")
        src = BLOCK_RE.sub("\n", src, count=1)
        if new:
            src, n = re.subn(r"<body([^>]*)>", lambda m: m.group(0) + "\n" + new, src, count=1)
            if n != 1:
                sys.exit(f"no <body> in {rel}")
        p.write_text(src, encoding="utf-8")
        print(("removed from " if off else "flag on ") + rel)


if __name__ == "__main__":
    main(off="--off" in sys.argv)
