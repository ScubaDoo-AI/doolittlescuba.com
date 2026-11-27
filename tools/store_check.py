#!/usr/bin/env python3
"""Store check: crawl shop.doolittlescuba.com and report SEO and page problems.

Signed with a Shopify "Crawler access" signature (Web Bot Auth) so Shopify's bot
protection lets it through. Set as GitHub secrets (never in the repo):
  SHOPIFY_CRAWL_SIGNATURE        the "Signature" value
  SHOPIFY_CRAWL_SIGNATURE_INPUT  the "Signature-Input" value
Signature-Agent is always "https://shopify.com" (quotes included) and is set here.
Without the secrets it still runs, unsigned, and says so.

Per page: HTTP status, <title> (present, <= 70), meta description (present, <= 160),
exactly one <h1>, og:image, canonical, images with no alt, links that 4xx/5xx.
While the store is behind its password, it reports "private" and exits 0.

  python tools/store_check.py [--max-pages 60] [--base https://shop.doolittlescuba.com]
Writes store-check.md (and the GitHub job summary when run in Actions) and store-check.json.
"""
import argparse, html.parser, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from collections import Counter

UA = "DoolittleScuba-StoreCheck/1.0 (+https://doolittlescuba.com)"


def headers():
    h = {"User-Agent": UA, "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8"}
    sig, inp = os.environ.get("SHOPIFY_CRAWL_SIGNATURE"), os.environ.get("SHOPIFY_CRAWL_SIGNATURE_INPUT")
    if sig and inp:
        h.update({"Signature": sig, "Signature-Input": inp, "Signature-Agent": '"https://shopify.com"'})
    return h, bool(sig and inp)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPEN = urllib.request.build_opener(NoRedirect)
HDR, SIGNED = headers()


def fetch(url, method="GET", follow=5):
    """Return (status, final_url, body_text, location_chain)."""
    chain = []
    for _ in range(follow + 1):
        req = urllib.request.Request(url, headers=HDR, method=method)
        try:
            with OPEN.open(req, timeout=25) as r:
                body = r.read().decode("utf-8", "replace") if method == "GET" else ""
                return r.status, url, body, chain
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308) and e.headers.get("Location"):
                chain.append(url)
                url = urllib.parse.urljoin(url, e.headers["Location"])
                continue
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After") or 5))
                continue
            return e.code, url, "", chain
        except Exception as e:  # network error
            return 0, url, str(e), chain
    return 310, url, "", chain


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.in_title, self.meta, self.h1, self.imgs_noalt, self.links = "", False, {}, 0, [], set()
        self.canonical = None

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            k = (a.get("name") or a.get("property") or "").lower()
            if k:
                self.meta[k] = a.get("content") or ""
        elif tag == "h1":
            self.h1 += 1
        elif tag == "img":
            if a.get("alt") is None or (not a.get("alt").strip() and a.get("role") != "presentation"):
                if a.get("aria-hidden") != "true":
                    self.imgs_noalt.append(a.get("src") or a.get("data-src") or "?")
        elif tag == "a" and a.get("href"):
            self.links.add(a["href"])
        elif tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = a.get("href")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, d):
        if self.in_title:
            self.title += d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://shop.doolittlescuba.com")
    ap.add_argument("--max-pages", type=int, default=60)
    ap.add_argument("--check-links", type=int, default=1, help="1 = HEAD-check every link found (once each)")
    args = ap.parse_args()
    base = args.base.rstrip("/")
    host = urllib.parse.urlparse(base).netloc
    out, rep = [], {"base": base, "signed": SIGNED, "pages": [], "broken_links": [], "private": False}

    st, final, body, chain = fetch(base + "/")
    if "/password" in final:
        rep["private"] = True
        out += [f"# Store check — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}",
                f"Store **{host}** is still behind its password (/ → /password), so there is nothing public to audit yet.",
                f"Request signed: {'yes' if SIGNED else 'no (secrets not set)'}."]
        return finish(out, rep)
    if st != 200:
        out += [f"# Store check", f"Home page answered **{st}** (signed: {SIGNED}). "
                + ("Shopify's bot protection likely blocked it; add the crawler signature secrets." if st in (403, 429, 430) else "")]
        rep["home_status"] = st
        finish(out, rep)
        sys.exit(1)

    # URL list: the sitemap first, then links found on pages
    urls, seen = [base + "/"], set()
    s, _, sm, _ = fetch(base + "/sitemap.xml")
    for sub in re.findall(r"<loc>([^<]+)</loc>", sm)[:12] if s == 200 else []:
        s2, _, b2, _ = fetch(sub.replace("&amp;", "&"))
        urls += [u.replace("&amp;", "&") for u in re.findall(r"<loc>([^<]+)</loc>", b2) if "/products/" in u or "/collections/" in u or "/pages/" in u]
    links_all, title_counter = Counter(), Counter()
    while urls and len(rep["pages"]) < args.max_pages:
        u = urls.pop(0).split("#")[0]
        if u in seen:
            continue
        seen.add(u)
        st, final, body, _ = fetch(u)
        p = Page()
        try:
            p.feed(body)
        except Exception:
            pass
        title = re.sub(r"\s+", " ", p.title).strip()
        desc = p.meta.get("description", "").strip()
        probs = []
        if st != 200: probs.append(f"status {st}")
        if not title: probs.append("no title")
        elif len(title) > 70: probs.append(f"title {len(title)} chars")
        if not desc: probs.append("no meta description")
        elif len(desc) > 160: probs.append(f"description {len(desc)} chars (Google cuts ~160)")
        if p.h1 != 1: probs.append(f"{p.h1} h1")
        if not p.meta.get("og:image"): probs.append("no og:image")
        if not p.canonical: probs.append("no canonical")
        if p.imgs_noalt: probs.append(f"{len(p.imgs_noalt)} image(s) without alt")
        title_counter[title] += 1
        rep["pages"].append({"url": u, "status": st, "title": title, "description": desc, "h1": p.h1,
                             "imgs_noalt": p.imgs_noalt[:10], "problems": probs})
        for h in p.links:
            full = urllib.parse.urljoin(u, h).split("#")[0]
            if not full.startswith("http"):
                continue
            links_all[full] += 1
            if urllib.parse.urlparse(full).netloc == host and full not in seen and len(urls) < 400:
                if not re.search(r"/(cart|account|checkouts?|search|policies)\b|\?(variant|q|sort|filter)", full):
                    urls.append(full)
        time.sleep(0.3)

    if args.check_links:
        for l in sorted(links_all):
            if re.search(r"/(cart|account|checkouts?)\b|mailto:|tel:", l):
                continue
            s, _, _, _ = fetch(l, "HEAD")
            if s in (405, 403) and urllib.parse.urlparse(l).netloc != host:
                s, _, _, _ = fetch(l)
            if s >= 400 or s == 0:
                rep["broken_links"].append({"url": l, "status": s})
            time.sleep(0.15)

    dup = {t: n for t, n in title_counter.items() if n > 1 and t}
    bad = [p for p in rep["pages"] if p["problems"]]
    out += [f"# Store check — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}",
            f"**{host}** · {len(rep['pages'])} pages · signed: {'yes' if SIGNED else 'no'} · "
            f"{len(bad)} pages with problems · {len(rep['broken_links'])} broken links · {len(dup)} duplicate titles", ""]
    if rep["broken_links"]:
        out += ["## Broken links", *[f"- {b['status']} {b['url']}" for b in rep["broken_links"]], ""]
    if dup:
        out += ["## Duplicate titles", *[f"- {n}× {t}" for t, n in dup.items()], ""]
    if bad:
        out += ["## Pages with problems", "| Page | Problems |", "|---|---|",
                *[f"| {p['url'].replace(base, '') or '/'} | {'; '.join(p['problems'])} |" for p in bad]]
    rep["duplicate_titles"] = dup
    finish(out, rep)
    sys.exit(1 if rep["broken_links"] or any(p["status"] != 200 for p in rep["pages"]) else 0)


def finish(out, rep):
    md = "\n".join(out) + "\n"
    open("store-check.md", "w").write(md)
    json.dump(rep, open("store-check.json", "w"), indent=1)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        open(os.environ["GITHUB_STEP_SUMMARY"], "a").write(md)
    print(md)


if __name__ == "__main__":
    main()
