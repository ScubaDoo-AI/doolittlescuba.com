#!/usr/bin/env python3
"""Wide-screen scaling: on big monitors at 100% browser zoom, scale the whole page up
so it fills the screen instead of sitting in a narrow column with tiny type.

Uses CSS `zoom` on <html> in steps by window width, and publishes the factor as
--ds-z so vw-based pieces (the status flag) can compensate. Phones, tablets and
laptops (under 1800px wide) are untouched.

    python3 tools/wide_screen.py         # stamp/refresh on every page
    python3 tools/wide_screen.py --off   # remove it

The block sits between <!-- WIDE:START --> and <!-- WIDE:END --> just before </head>.
"""
import pathlib, re, sys

# (minimum window width in CSS px, zoom factor)
STEPS = [(1800, 1.15), (2100, 1.3), (2400, 1.5), (3000, 1.75), (3600, 2.0)]

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "about/index.html", "workshop/index.html", "custom/index.html",
         *sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("sites/*/index.html"))]
BLOCK_RE = re.compile(r"\n?<!-- WIDE:START -->.*?<!-- WIDE:END -->\n?", re.S)


def block():
    rules = "".join(f"@media (min-width:{w}px){{html{{zoom:{z};--ds-z:{z}}}}}" for w, z in STEPS)
    return f"<!-- WIDE:START --><style>{rules}</style><!-- WIDE:END -->"


def main(off=False):
    new = "" if off else block()
    for rel in PAGES:
        p = ROOT / rel
        src = BLOCK_RE.sub("\n", p.read_text(encoding="utf-8"), count=1)
        if new:
            src, n = re.subn(r"</head>", lambda m: new + "\n" + m.group(0), src, count=1)
            if n != 1:
                sys.exit(f"no </head> in {rel}")
        p.write_text(src, encoding="utf-8")
        print(("removed from " if off else "wide-screen on ") + rel)


if __name__ == "__main__":
    main(off="--off" in sys.argv)
