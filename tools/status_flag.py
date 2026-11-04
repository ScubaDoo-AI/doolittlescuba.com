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
.ds-status{--sz:clamp(.95rem,.5rem + .5vw,1.5rem);position:relative;z-index:5;margin-inline:calc(-1 * var(--gut,0px));background:#C8202A;background-image:linear-gradient(90deg,#B01B24,#C8202A 45%,#D22A33);color:#fff;border-bottom:.2em solid #0E2147;box-shadow:0 .15em .6em rgba(8,18,40,.35);font-family:var(--f-body,system-ui,sans-serif);font-size:var(--sz);line-height:1.4}
.ds-status[hidden]{display:none}
.ds-status__in{max-width:90em;margin:0 auto;padding:.7em clamp(16px,4vw,3em);display:flex;align-items:center;gap:.6em 1.2em;flex-wrap:wrap}
.ds-status__tag{display:inline-flex;align-items:center;gap:.6em;font-family:var(--f-data,ui-monospace,Menlo,monospace);font-size:.85em;font-weight:600;letter-spacing:.1em;text-transform:uppercase;white-space:nowrap}
.ds-status__tag svg{width:1.9em;height:1.3em;flex:none;display:block;outline:.12em solid #fff;outline-offset:0;border-radius:1px}
.ds-status__state{display:inline-flex;align-items:center;gap:.45em;color:#B01B24;background:#fff;border-radius:.3em;padding:.2em .6em;font-weight:700}
.ds-status__state::before{content:"";width:.55em;height:.55em;border-radius:50%;background:#C8202A;box-shadow:0 0 0 0 rgba(200,32,42,.6);animation:ds-pulse 2s ease-out infinite}
@keyframes ds-pulse{0%{box-shadow:0 0 0 0 rgba(200,32,42,.6)}70%{box-shadow:0 0 0 .5em rgba(200,32,42,0)}100%{box-shadow:0 0 0 0 rgba(200,32,42,0)}}
@media (prefers-reduced-motion:reduce){.ds-status__state::before{animation:none}}
.ds-status__msg{flex:1 1 20em;margin:0;color:#fff;font-weight:500}
.ds-status__msg a{color:#fff;font-weight:700;text-decoration-thickness:.08em;text-underline-offset:.2em;white-space:nowrap}
.ds-status__msg a:hover{text-decoration-thickness:.14em}
.ds-status__when{font-family:var(--f-data,ui-monospace,Menlo,monospace);font-size:.78em;color:#FFE3E4;white-space:nowrap}
.ds-status__x{background:none;border:0;color:#fff;font:inherit;font-size:1.4em;line-height:1;padding:.2em .35em;margin:-.2em -.35em -.2em 0;cursor:pointer;border-radius:.2em;opacity:.85}
.ds-status__x:hover,.ds-status__x:focus-visible{opacity:1;outline:2px solid #fff;outline-offset:1px}
@media (max-width:560px){.ds-status__in{padding-right:44px}.ds-status__x{position:absolute;top:.35em;right:.4em;margin:0}}
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
