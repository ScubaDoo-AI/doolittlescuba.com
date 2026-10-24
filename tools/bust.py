#!/usr/bin/env python3
"""Cache-busting: stamp every local asset reference with ?v=<first 8 hex of the file's SHA-1>.

Porkbun's CDN caches images, CSS and JS for 30 days by URL, so a file replaced in place keeps
serving the old bytes until its URL changes. Run this last, after any asset changes.

Covers src, href, data-front, data-back, data-full and poster attributes in every *.html under the site
(relative paths resolve against the page; absolute ones against the site root), and the
`"v": {...}` map inside the Make it yours page data (custom/index.html), whose keys are paths
relative to /custom/. External URLs, anchors and mailto: links are left alone. A reference to a
file that does not exist is reported and left alone.

Usage: tools/bust.py            (from anywhere; edits the files in place, prints what changed)
"""
import hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTR = re.compile(r'\b(src|href|data-front|data-back|data-full|poster)="([^"]+)"')
SKIP = re.compile(r'^(https?:|//|mailto:|tel:|#|data:|javascript:)')
_cache = {}


def digest(path):
    if path not in _cache:
        with open(path, 'rb') as f:
            _cache[path] = hashlib.sha1(f.read()).hexdigest()[:8]
    return _cache[path]


def resolve(ref, page_dir):
    base = ref.split('?', 1)[0].split('#', 1)[0]
    if not base or base.endswith('/'):
        return None
    full = os.path.normpath(os.path.join(ROOT, base.lstrip('/')) if base.startswith('/') else os.path.join(page_dir, base))
    return full if os.path.isfile(full) else None


def bust_html(path):
    page_dir = os.path.dirname(path)
    with open(path, encoding='utf-8') as f:
        src = f.read()
    missing = []

    def sub(m):
        attr, ref = m.group(1), m.group(2)
        if SKIP.match(ref):
            return m.group(0)
        full = resolve(ref, page_dir)
        if full is None:
            if '?v=' in ref:
                missing.append(ref)
            return m.group(0)
        base = ref.split('?', 1)[0].split('#', 1)[0]
        frag = ('#' + ref.split('#', 1)[1]) if '#' in ref else ''
        return f'{attr}="{base}?v={digest(full)}{frag}"'

    out = ATTR.sub(sub, src)
    # The Make it yours data block: "v": {"art/x.webp": "hash", ...}, paths relative to the page
    m = re.search(r'"v":(\{[^}]*\})', out)
    if m:
        vmap = json.loads(m.group(1))
        new = {}
        for k in sorted(vmap):
            full = resolve(k, page_dir)
            if full:
                new[k] = digest(full)
            else:
                missing.append(k)
        # keep any art the page references but the map forgot
        for folder in ('art', 't'):
            d = os.path.join(page_dir, folder)
            if os.path.isdir(d):
                for fn in sorted(os.listdir(d)):
                    if fn.endswith('.webp'):
                        new[f'{folder}/{fn}'] = digest(os.path.join(d, fn))
        out = out[:m.start(1)] + json.dumps(new, separators=(',', ':')) + out[m.end(1):]
    if out != src:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(out)
    return out != src, missing


if __name__ == '__main__':
    changed = []
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'tools']
        for fn in files:
            if fn.endswith('.html'):
                p = os.path.join(dirpath, fn)
                did, missing = bust_html(p)
                rel = os.path.relpath(p, ROOT)
                if did:
                    changed.append(rel)
                for ref in missing:
                    print(f'  ! {rel}: {ref} not found', file=sys.stderr)
    print(f'{len(changed)} page(s) updated' + (': ' + ', '.join(changed) if changed else ''))
