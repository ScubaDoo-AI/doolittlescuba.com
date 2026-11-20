#!/usr/bin/env python3
"""Daily price-and-stock watch: Shopify + Printful → two GitHub issues. Changes nothing unless asked.

Price changes come first, because a sync can quietly rewrite a price (14 Nov: The Mark beanie went $35 → $30 the
moment Printful's inventory sync ran). Each morning it checks:

  PRICES  (issue "Price changes need a look")
    1. Selling price or compare-at price in Shopify ≠ the approved price in tools/data/price_baseline.json.
       Shows old → new, when the variant last changed, and whether Printful's retail price matches the new one
       (if it does, Printful's sync most likely pushed it).
    2. Printful retail price ≠ the Shopify price on a linked variant. Not wrong yet, but the next Printful sync can
       push it into Shopify. Caught before it happens.
    3. Printful's cost for a blank went up or down vs the baseline → how many SKUs it touches, and the new cost.
    4. Products with no approved price yet (added since the baseline) → listed so they can be accepted.

  STOCK   (issue "Stock watch")
    5. Sold out: a tracked variant at 0 (Printful sets 0 when its blank runs out), with suggestions: the nearest
       in-stock colour of the same blank and size (by colour distance), the organic edition from the cart map,
       and whether the blank is in stock at another Printful region.
    6. Blanks Printful reports out of stock in the US that our variants use, even before Shopify shows 0.
    7. Bulk stock (Sticker Mule packs, Ninja Transfers sheets): low (≤ LOW_STOCK) or not tracked (can oversell).

Modes (Actions → "Price & stock watch", or locally with the env vars set)
  tools/price_stock_watch.py                   daily check → issues (first run writes the baseline from today's prices)
  tools/price_stock_watch.py --dry             print the report, no issues, no baseline write
  tools/price_stock_watch.py --accept SKUS     today's Shopify price becomes the approved price for SKUS
                                               (comma list, prefixes like DS-MRK-BN, "flagged" = every price flag, or "all")
  tools/price_stock_watch.py --restore SKUS [--apply]
                                               set Shopify (and Printful retail) back to the approved price for SKUS
                                               ("flagged" = every changed price). Without --apply it only prints the plan.
  tools/price_stock_watch.py --selftest        run the report on made-up data (no network)

Needs: SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET (Order Bot: read_products; write_products for --restore),
PRINTFUL_TOKEN (sync products read; write for --restore), GH_TOKEN for the issues. Public repo: SKUs, prices,
colours only — no buyer data.
"""
import os, sys, json, time, re, subprocess, hashlib
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
BASELINE = os.path.join(HERE, 'data', 'price_baseline.json')
ORGANIC_MAP = os.path.join(HERE, '..', 'shopify-theme', 'assets', 'ds-organic-map.json')
POD_PLACEHOLDER = 9000           # Printful shows 9,999 on stocked variants; anything below is real counted stock
LOW_STOCK = 10
BULK_TAGS = ('print:sticker-mule', 'print:ninja-transfers')
US_TWIN = {456: 818}            # Stanley/Stella STTU169 is Europe/UK only at Printful; SATU001 is the same Creator 2.0 tee made in the US
PRICE_TITLE = 'Price changes need a look'
STOCK_TITLE = 'Stock watch'
SIZES = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']


def money(x):
    return None if x in (None, '') else round(float(x), 2)


def fm(x):
    return '—' if x is None else f'${x:,.2f}'


# ---------------------------------------------------------------- data in
VARIANTS_Q = '''query($a: String) { productVariants(first: 250, after: $a,
    query: "product_status:active OR product_status:draft") {
  pageInfo { hasNextPage endCursor }
  nodes { id sku title price compareAtPrice updatedAt availableForSale inventoryPolicy %s
          inventoryItem { tracked }
          product { handle title status tags } } } }'''


def shopify_variants():
    import aquatic_order as O
    out, after, qty = [], None, 'inventoryQuantity'
    while True:
        try:
            d = O.shopify(VARIANTS_Q % qty, {'a': after})['productVariants']
        except SystemExit as e:
            if qty and 'inventoryQuantity' in str(e):        # app without read_inventory: fall back to availableForSale
                print('note: inventoryQuantity not readable; using availableForSale only', flush=True); qty = ''; continue
            raise
        for v in d['nodes']:
            if not v.get('sku'): continue
            p = v['product']
            out.append(dict(id=v['id'], sku=v['sku'], vtitle=v['title'], price=money(v['price']), compare=money(v['compareAtPrice']),
                            updated=v['updatedAt'], available=v['availableForSale'], policy=v['inventoryPolicy'],
                            qty=v.get('inventoryQuantity'), tracked=(v.get('inventoryItem') or {}).get('tracked'),
                            handle=p['handle'], ptitle=p['title'], status=p['status'], tags=p['tags']))
        if not d['pageInfo']['hasNextPage']: break
        after = d['pageInfo']['endCursor']
    return out


def pf_get(path):
    import aquatic_order as O
    tok = os.environ.get('PRINTFUL_TOKEN') or sys.exit('PRINTFUL_TOKEN not set')
    for k in range(5):
        code, r = O.http('GET', 'https://api.printful.com' + path, {'Authorization': 'Bearer ' + tok, 'X-PF-Store-Id': O.PF_STORE}, tries=1)
        if code == 429: time.sleep(60); continue
        time.sleep(0.55)                                       # stay under Printful's ~120 requests a minute
        return code, r
    return code, r


def printful_sync():
    """sku → {sync_id, variant_id (catalog), product_id (catalog), retail, ignored} for every linked variant."""
    items, off = [], 0
    while True:
        code, r = pf_get(f'/sync/products?offset={off}&limit=100')
        if code != 200: sys.exit(f'Printful sync list: {code} {str(r)[:300]}')
        items += r['result']; off += 100
        if off >= r['paging']['total']: break
    out = {}
    for i, sp in enumerate(items):
        code, r = pf_get(f'/sync/products/{sp["id"]}')
        if code != 200: print('skip', sp.get('name'), code, flush=True); continue
        for sv in r['result']['sync_variants']:
            key = sv.get('sku') or ''
            prod = sv.get('product') or {}
            out[key] = dict(sync_id=sv['id'], ext=str(sv.get('external_id') or ''), variant_id=sv.get('variant_id') or prod.get('variant_id'),
                            product_id=prod.get('product_id'), retail=money(sv.get('retail_price')), ignored=bool(sv.get('is_ignored')),
                            synced=bool(sv.get('synced')))
        if i % 50 == 49: print(f'  Printful: {i + 1}/{len(items)} products read', flush=True)
    return out


def printful_catalog(product_ids):
    """catalog variant id → {product_id, product, color, hex, size, cost, us, regions{}}. The catalog is public: the store
    token gets 403 on it, so these calls go without it."""
    import aquatic_order as O
    out = {}
    for pid in sorted({p for p in product_ids if p}):
        code, r = O.http('GET', f'https://api.printful.com/products/{pid}', {'User-Agent': 'doolittlescuba-tools/1.0'}); time.sleep(0.3)
        if code != 200: print('catalog skip', pid, code, flush=True); continue
        name = r['result']['product'].get('title') or r['result']['product'].get('model') or str(pid)
        for v in r['result']['variants']:
            regions = {a.get('region'): a.get('status') for a in (v.get('availability_status') or [])}
            out[v['id']] = dict(product_id=pid, product=name, color=v.get('color'), hex=v.get('color_code'), size=v.get('size'),
                                cost=money(v.get('price')), us=regions.get('US'), regions=regions, in_stock=v.get('in_stock'))
    return out


# ---------------------------------------------------------------- analysis
def load_baseline():
    if not os.path.exists(BASELINE): return None
    with open(BASELINE) as f: return json.load(f)


def make_baseline(variants, catalog, sync, old=None, only=None):
    b = old or {'note': 'Approved prices. Change with price_stock_watch.py --accept, never by hand-editing during a sync.',
                'prices': {}, 'compare': {}, 'costs': {}}
    for v in variants:
        if only is None or v['sku'] in only:
            b['prices'][v['sku']] = v['price']
            if v['compare'] is not None: b['compare'][v['sku']] = v['compare']
            else: b['compare'].pop(v['sku'], None)
    if only is None:
        for vid, c in catalog.items():
            if c['cost'] is not None: b['costs'][str(vid)] = c['cost']
    else:                                                    # accepting SKUs also accepts the cost of their blanks
        for sku in only:
            vid = (sync.get(sku) or {}).get('variant_id')
            if vid in catalog and catalog[vid]['cost'] is not None: b['costs'][str(vid)] = catalog[vid]['cost']
    b['updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    return b


def in_stock(status):
    return status in ('in_stock', 'stocked_on_demand')


def hex_dist(a, b):
    try:
        a, b = a.lstrip('#'), b.lstrip('#')
        ra, ga, ba = (int(a[i:i + 2], 16) for i in (0, 2, 4)); rb, gb, bb = (int(b[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return 1e9
    rm = (ra + rb) / 2                                       # "redmean" weighting, close enough to perception for ranking
    return ((2 + rm / 256) * (ra - rb) ** 2 + 4 * (ga - gb) ** 2 + (2 + (255 - rm) / 256) * (ba - bb) ** 2) ** .5


def nearest_colours(vid, catalog, n=2):
    me = catalog.get(vid)
    if not me: return []
    cands = [c for k, c in catalog.items() if k != vid and c['product_id'] == me['product_id'] and c['size'] == me['size']
             and in_stock(c['us']) and c['color'] != me['color']]
    cands.sort(key=lambda c: hex_dist(me['hex'] or '', c['hex'] or ''))
    return [c['color'] for c in cands[:n]]


def organic_for(sku, omap):
    e = omap.get(sku) or omap.get(sku.rsplit('-', 1)[0])    # beanie keys carry the colour; tee/cap keys drop the size
    if not e: return None
    return dict(handle=e[1], to=e[4], change=(e[2] or '').lower() != (e[4] or '').lower())


def analyse(variants, sync, catalog, base, omap):
    by_sku = {v['sku']: v for v in variants}
    R = dict(changed=[], drift=[], cost=[], new=[], soldout=[], blank_out=[], low=[], untracked=[])
    bp, bc, bcost = base['prices'], base.get('compare', {}), base.get('costs', {})
    for v in variants:
        s = sync.get(v['sku'])
        if v['sku'] not in bp:
            R['new'].append(v)
        else:
            old, oldc = bp[v['sku']], bc.get(v['sku'])
            if v['price'] != old or v['compare'] != oldc:
                R['changed'].append(dict(v=v, old=old, oldc=oldc, pf=s['retail'] if s else None))
        if s and not s['ignored'] and s['retail'] is not None and v['price'] is not None and s['retail'] != v['price']:
            R['drift'].append(dict(v=v, pf=s['retail']))
        # stock
        bulk = any(t.startswith(BULK_TAGS) for t in v['tags'])
        if v['status'] == 'ACTIVE':
            sold = v['tracked'] and v['policy'] == 'DENY' and ((v['qty'] is not None and v['qty'] <= 0) or
                                                                (v['qty'] is None and not v['available']))
            if sold:
                c = catalog.get(s['variant_id']) if s else None
                cause = ('bulk' if bulk else 'unlinked' if (not s or s['ignored'] or not s['synced'] or not s['variant_id'])
                         else 'no_us' if c and c['us'] is None else 'blank' if c and not in_stock(c['us']) else 'other')
                R['soldout'].append(dict(v=v, s=s, cause=cause))
            elif v['tracked'] and v['qty'] is not None and 0 < v['qty'] <= LOW_STOCK and v['qty'] < POD_PLACEHOLDER:
                R['low'].append(v)
        if bulk and not v['tracked'] and v['status'] == 'ACTIVE':
            R['untracked'].append(v)
        if s and not s['ignored'] and s['variant_id'] in catalog:
            c = catalog[s['variant_id']]
            if v['status'] == 'ACTIVE' and not in_stock(c['us']) and not any(x['v']['sku'] == v['sku'] for x in R['soldout']):
                R['blank_out'].append(dict(v=v, s=s))
    # Printful cost changes, grouped by blank
    users = {}
    for sku, s in sync.items():
        if s['variant_id'] and sku in by_sku: users.setdefault(s['variant_id'], []).append(sku)
    for vid, skus in users.items():
        c = catalog.get(vid); old = bcost.get(str(vid))
        if c and old is not None and c['cost'] is not None and c['cost'] != old:
            R['cost'].append(dict(c=c, old=old, skus=skus))
    return R


# ---------------------------------------------------------------- report
def group_rows(rows, key, fmt):
    """Collapse per-size rows of one product into one line."""
    g = {}
    for r in rows: g.setdefault(key(r), []).append(r)
    return [fmt(k, rs) for k, rs in g.items()]


def sizes_of(rs):
    t = [r['v']['vtitle'] if isinstance(r, dict) and 'v' in r else r['vtitle'] for r in rs]
    return ', '.join(t) if len(t) <= 6 else f'{len(t)} variants'


def soldout_line(catalog, omap):
    def f(k, rs):
        v, s = rs[0]['v'], rs[0]['s']
        line = f'- **{v["ptitle"]}**, {sizes_of(rs)}'
        tips = []
        if rs[0]['cause'] == 'no_us': return line
        if rs[0]['cause'] == 'blank' and s and s['variant_id'] in catalog:
            c = catalog[s['variant_id']]
            near = nearest_colours(s['variant_id'], catalog)
            if near: tips.append(f'nearest {c["product"]} colour in stock: {" or ".join(near)}')
            other = [r for r, st in c['regions'].items() if r != 'US' and in_stock(st)]
            if other: tips.append(f'blank in stock in {", ".join(other)} (other Printful facility, different shipping)')
        if rs[0]['cause'] in ('blank', 'other'):
            o = organic_for(v['sku'], omap)
            if o: tips.append(f'organic edition `{o["handle"]}`' + (f' in {o["to"]}' if o['change'] else ' (same colour)'))
        if any(t.startswith('pair') or t == 'bundle' for t in v['tags']): tips.append('a pair: swap the sold-out part or hide the pair')
        return line + (' → ' + ' · '.join(tips) if tips else '')
    return f


def us_twin_note(rows, catalog):
    """For blanks with no US stock: the US twin's colours and cost per size, side by side."""
    out, seen = [], set()
    for r in rows:
        c = catalog.get(r['s']['variant_id']); twin = US_TWIN.get(c['product_id']) if c else None
        if not twin or c['product_id'] in seen: continue
        seen.add(c['product_id'])
        used = {(catalog[x['s']['variant_id']]['color'], catalog[x['s']['variant_id']]['size']) for x in rows
                if catalog.get(x['s']['variant_id'], {}).get('product_id') == c['product_id']}
        tw = {(t['color'], t['size']): t for t in catalog.values() if t['product_id'] == twin}
        ok = [k for k in used if k in tw and in_stock(tw[k]['us'])]
        missing = sorted(f'{k[0]} {k[1]}' for k in used if k not in tw or not in_stock(tw[k]['us']))
        costs = {}
        for (col, size) in used:
            if (col, size) in tw:
                a = next((v['cost'] for v in catalog.values() if v['product_id'] == c['product_id'] and v['color'] == col and v['size'] == size), None)
                costs[size] = (a, tw[(col, size)]['cost'])
        name = next(t['product'] for t in tw.values()) if tw else str(twin)
        out.append(f'**Fix:** relink them to **{name}** (Printful {twin}), the same tee made in the US: '
                   f'{len(ok)} of {len(used)} colour/size combinations in stock there'
                   + (f'; not made there: {", ".join(missing[:12])}' + (' …' if len(missing) > 12 else '') if missing else '') + '.')
        if costs:
            out.append('Cost per blank, now → US twin: ' + ' · '.join(
                f'{sz} {fm(a)} → {fm(b)}' for sz, (a, b) in sorted(costs.items(), key=lambda x: SIZES.index(x[0]) if x[0] in SIZES else 99)))
    return out


def report(R, sync, catalog, omap, base):
    P, S = [], []
    if R['changed']:
        P.append(f'### 🔴 Selling price changed ({len(R["changed"])} variant{"s" * (len(R["changed"]) != 1)})')
        P.append('The price in Shopify no longer matches the approved price.')
        def f(k, rs):
            r = rs[0]; v = r['v']; when = v['updated'][:16].replace('T', ' ') + ' UTC'
            line = f'- **{v["ptitle"]}** (`{k[0]}`), {sizes_of(rs)}: {fm(r["old"])} → **{fm(v["price"])}**'
            if r['oldc'] != v['compare']: line += f' · compare-at {fm(r["oldc"])} → {fm(v["compare"])}'
            line += f' · last changed {when}'
            if r['pf'] is not None and r['pf'] == v['price']: line += ' · **Printful retail is also ' + fm(r['pf']) + ': Printful\'s sync most likely pushed it**'
            return line
        P += group_rows(R['changed'], lambda r: (r['v']['handle'], r['old'], r['v']['price'], r['oldc'], r['v']['compare']), f)
        P.append('')
        P.append('**To fix:** put it back → Actions → *Price & stock watch* → mode **restore**, SKUs `flagged` (or a SKU prefix), apply ✔. '
                 'Keep the new price → mode **accept** with the same SKUs.')
        P.append('')
    if R['drift']:
        P.append(f'### 🟠 Printful\'s retail price differs from Shopify ({len(R["drift"])})')
        P.append('Shopify is still right, but Printful\'s next sync can push its price over it. **restore** sets Printful to the approved price too.')
        P += group_rows(R['drift'], lambda r: (r['v']['handle'], r['v']['price'], r['pf']),
                        lambda k, rs: f'- **{rs[0]["v"]["ptitle"]}**, {sizes_of(rs)}: Shopify {fm(k[1])} · Printful {fm(k[2])}')
        P.append('')
    if R['cost']:
        P.append(f'### 🟡 Printful changed what a blank costs you ({len(R["cost"])})')
        for r in sorted(R['cost'], key=lambda r: -abs(r['c']['cost'] - r['old'])):
            c, d = r['c'], r['c']['cost'] - r['old']
            P.append(f'- {c["product"]} · {c["color"]} · {c["size"]}: {fm(r["old"])} → **{fm(c["cost"])}** ({"+" if d > 0 else "−"}${abs(d):.2f}) · '
                     f'{len(r["skus"])} SKU(s), e.g. `{r["skus"][0]}` — your margin moves by the same amount')
        P.append('')
        P.append('Selling prices are unchanged. **accept** with those SKUs records the new cost once you\'ve decided.')
        P.append('')
    if R['new']:
        P.append(f'### ⚪ No approved price yet ({len(R["new"])} variants, added since the baseline)')
        P += group_rows(R['new'], lambda v: (v['handle'], v['price']),
                        lambda k, vs: f'- {vs[0]["ptitle"]} (`{k[0]}`): {fm(k[1])} × {len(vs)}')[:40]
        P.append('')
        P.append('If those prices are right: mode **accept**, SKUs `new`.')
        P.append('')

    if R['soldout']:
        S.append(f'### Sold out on the store ({len(R["soldout"])} variants)')
        CAUSE = {'no_us': 'Linked to a blank Printful doesn\'t make in the US, so Printful keeps them at 0', 'blank': 'Printful\'s blank is out of stock', 'bulk': 'Bulk stock ran out: reorder',
                 'unlinked': 'Printful never stocked these: the variant isn\'t linked (or is ignored) at Printful, so buyers can\'t add it',
                 'other': 'At 0, cause unclear (check the variant\'s locations in Shopify)'}
        for cause in ('no_us', 'blank', 'bulk', 'unlinked', 'other'):
            rows = [r for r in R['soldout'] if r['cause'] == cause]
            if not rows: continue
            S.append(f'**{CAUSE[cause]}** ({len(rows)})')
            lines = group_rows(rows, lambda r: r['v']['handle'], soldout_line(catalog, omap))
            S += lines[:25] + ([f'- … and {len(lines) - 25} more products'] if len(lines) > 25 else [])
            if cause == 'no_us': S += us_twin_note(rows, catalog)
            if cause == 'unlinked': S.append('Fix: link them (Actions → Printful link, the matching line), or set them to Draft until they are.')
            S.append('')
    if R['blank_out']:
        S.append(f'### Printful says the blank is out in the US ({len(R["blank_out"])} variants, Shopify not at 0 yet)')
        S += group_rows(R['blank_out'], lambda r: r['v']['handle'],
                        lambda k, rs: f'- **{rs[0]["v"]["ptitle"]}**, {sizes_of(rs)} — '
                                      f'{catalog[rs[0]["s"]["variant_id"]]["us"]}'
                                      + (f'; nearest in stock: {" or ".join(nearest_colours(rs[0]["s"]["variant_id"], catalog))}'
                                         if nearest_colours(rs[0]["s"]["variant_id"], catalog) else ''))
        S.append('Custom (Make it yours / Home Port) orders in these colours will be held at the Printful draft step.')
        S.append('')
    if R['low']:
        S.append(f'### Low stock (≤ {LOW_STOCK})')
        S += [f'- {v["ptitle"]} {v["vtitle"]}: {v["qty"]} left' for v in R['low']]
        S.append('')
    if R['untracked']:
        S.append(f'### Bulk-printed but not tracking stock ({len(R["untracked"])} variants) — these can oversell')
        S += group_rows(R['untracked'], lambda v: v['tags'] and next((t for t in v['tags'] if t.startswith(BULK_TAGS)), ''),
                        lambda k, vs: f'- {len(vs)} variants tagged `{k}` (e.g. {vs[0]["ptitle"]}). Turn tracking on with real counts.')
        S.append('')
    return '\n'.join(P).strip(), '\n'.join(S).strip()


def first_run_summary(variants):
    lines = ['**Baseline written.** Today\'s prices are now the approved prices. Please check them once — anything wrong here '
             'would be guarded as if it were right:', '']
    g = {}
    for v in variants:
        line = next((t for t in v['tags'] if t in ('signature-series', 'certified-ish', 'organic-line', 'jacket', 'sticker-pack', 'sticker',
                                                   'brand-beanie', 'beanie', 'hat', 'pair', 'off-world', '1n73ll1g3nc3', 'tee')), 'other')
        g.setdefault(line, set()).add(v['price'])
    for k in sorted(g): lines.append(f'- {k}: ' + ', '.join(fm(p) for p in sorted(x for x in g[k] if x is not None)))
    return '\n'.join(lines)


# ---------------------------------------------------------------- issues
def gh(*a):
    return subprocess.run(['gh', *a], capture_output=True, text=True, check=True).stdout


def post(title, body, clean_note):
    found = json.loads(gh('issue', 'list', '--state', 'open', '--search', f'"{title}" in:title', '--json', 'number,title'))
    issue = next((x['number'] for x in found if x['title'] == title), None)
    if not body:
        if issue: gh('issue', 'close', str(issue), '--comment', clean_note)
        return
    tag = '<!-- watch:' + hashlib.sha1(body.encode()).hexdigest()[:12] + ' -->'
    full = body + '\n\n' + tag
    if issue:
        last = json.loads(gh('issue', 'view', str(issue), '--json', 'comments,body'))
        prev = (last['comments'][-1]['body'] if last['comments'] else last['body'])
        if tag in prev: print(f'"{title}": unchanged since the last note'); return
        gh('issue', 'comment', str(issue), '--body', full)
    else:
        gh('issue', 'create', '--title', title, '--body', full)


def commit_baseline(msg):
    if not os.environ.get('GITHUB_ACTIONS'): print('(not in Actions: baseline left uncommitted)'); return
    subprocess.run(['git', 'config', 'user.name', 'price-stock-watch'], check=True)
    subprocess.run(['git', 'config', 'user.email', 'actions@users.noreply.github.com'], check=True)
    subprocess.run(['git', 'add', BASELINE], check=True)
    if subprocess.run(['git', 'diff', '--cached', '--quiet']).returncode == 0: return
    subprocess.run(['git', 'commit', '-m', msg], check=True)
    for k in range(4):                                       # main moves often (other jobs, other sessions): rebase and retry
        if subprocess.run(['git', 'pull', '--rebase', '--quiet']).returncode == 0 and subprocess.run(['git', 'push']).returncode == 0: return
        time.sleep(10 * (k + 1))
    sys.exit('could not push the baseline after 4 tries')


def save(b):
    os.makedirs(os.path.dirname(BASELINE), exist_ok=True)
    with open(BASELINE, 'w') as f: json.dump(b, f, indent=1, sort_keys=True)


def pick(arg, variants, R):
    if arg == 'all': return {v['sku'] for v in variants}
    if arg == 'flagged': return {r['v']['sku'] for r in R['changed'] + R['drift']} | {s for r in R['cost'] for s in r['skus']}
    if arg == 'new': return {v['sku'] for v in R['new']}
    pre = tuple(x.strip() for x in arg.split(',') if x.strip())
    return {v['sku'] for v in variants if v['sku'].startswith(pre)}


# ---------------------------------------------------------------- restore
BULK_PRICE = '''mutation($p: ID!, $v: [ProductVariantsBulkInput!]!) { productVariantsBulkUpdate(productId: $p, variants: $v) {
  productVariants { sku price } userErrors { field message } } }'''
PID_Q = '''query($id: ID!) { productVariant(id: $id) { product { id } } }'''


def restore(skus, variants, sync, base, apply):
    import aquatic_order as O
    bp, bc = base['prices'], base.get('compare', {})
    todo = [v for v in variants if v['sku'] in skus and v['sku'] in bp]
    shop = [v for v in todo if v['price'] != bp[v['sku']] or v['compare'] != bc.get(v['sku'])]
    pf = [(v, sync[v['sku']]) for v in todo if v['sku'] in sync and not sync[v['sku']]['ignored']
          and sync[v['sku']]['retail'] is not None and sync[v['sku']]['retail'] != bp[v['sku']]]
    print(f'restore plan: {len(shop)} Shopify price(s), {len(pf)} Printful retail price(s)' + ('' if apply else ' — dry run, add --apply'))
    for v in shop: print(f'  Shopify {v["sku"]}: {fm(v["price"])} → {fm(bp[v["sku"]])}')
    for v, s in pf: print(f'  Printful {v["sku"]}: {fm(s["retail"])} → {fm(bp[v["sku"]])}')
    if not apply: return
    tok = os.environ['PRINTFUL_TOKEN']
    for v, s in pf:                                          # Printful first, so its sync can't undo the Shopify fix
        code, r = O.http('PUT', f'https://api.printful.com/sync/variant/{s["sync_id"]}',
                         {'Authorization': 'Bearer ' + tok, 'X-PF-Store-Id': O.PF_STORE, 'Content-Type': 'application/json'},
                         {'retail_price': f'{bp[v["sku"]]:.2f}'})
        print(f'  Printful {v["sku"]}: {"ok" if code == 200 else f"FAILED {code} {str(r)[:200]}"}', flush=True); time.sleep(0.6)
    byp = {}
    for v in shop:
        pid = O.shopify(PID_Q, {'id': v['id']})['productVariant']['product']['id']
        byp.setdefault(pid, []).append(v)
    for pid, vs in byp.items():
        d = O.shopify(BULK_PRICE, {'p': pid, 'v': [{'id': v['id'], 'price': f'{bp[v["sku"]]:.2f}',
                                                     'compareAtPrice': (f'{bc[v["sku"]]:.2f}' if v['sku'] in bc else None)} for v in vs]})
        e = d['productVariantsBulkUpdate']['userErrors']
        print(f'  Shopify {vs[0]["handle"]}: {"FAILED " + str(e) if e else f"{len(vs)} restored"}', flush=True)


# ---------------------------------------------------------------- main
def selftest():
    cat = {1: dict(product_id=9, product='Beanie', color='Black', hex='#000000', size='One size', cost=12.0, us='out_of_stock', regions={'US': 'out_of_stock', 'EU': 'in_stock'}, in_stock=False),
           2: dict(product_id=9, product='Beanie', color='French Navy', hex='#1c2541', size='One size', cost=12.0, us='in_stock', regions={'US': 'in_stock'}, in_stock=True),
           3: dict(product_id=9, product='Beanie', color='Red', hex='#cc0000', size='One size', cost=12.0, us='in_stock', regions={'US': 'in_stock'}, in_stock=True),
           4: dict(product_id=5, product='CC 1717', color='Black', hex='#111111', size='M', cost=16.10, us='in_stock', regions={'US': 'in_stock'}, in_stock=True)}
    V = lambda sku, price, qty, tags, vt, h='the-mark-beanie', t='The Mark — Beanie': dict(
        id='gid://x/' + sku, sku=sku, vtitle=vt, price=price, compare=None, updated='2026-11-14T05:45:00Z', available=qty != 0,
        policy='DENY', qty=qty, tracked=True, handle=h, ptitle=t, status='ACTIVE', tags=tags)
    vs = [V('DS-MRK-BN-BLK', 30.0, 0, ['beanie'], 'Black'), V('DS-MRK-BN-FNV', 30.0, 9999, ['beanie'], 'French Navy'),
          V('DS-THI-T-M', 42.0, 9999, ['tee'], 'M', 'the-thistlegorm-signature-series-tee', 'The Thistlegorm'),
          V('DS-PK-B01', 9.0, 8, ['print:sticker-mule-4x6'], 'Default', 'sticker-pack-b01', 'Sticker pack B01'),
          V('DS-NEW-1', 25.0, 9999, ['tee'], 'S', 'new-thing', 'New thing')]
    vs[3]['tracked'] = True
    sync = {'DS-MRK-BN-BLK': dict(sync_id=1, ext='', variant_id=1, product_id=9, retail=30.0, ignored=False, synced=True),
            'DS-MRK-BN-FNV': dict(sync_id=2, ext='', variant_id=2, product_id=9, retail=30.0, ignored=False, synced=True),
            'DS-THI-T-M': dict(sync_id=3, ext='', variant_id=4, product_id=5, retail=38.0, ignored=False, synced=True)}
    base = {'prices': {'DS-MRK-BN-BLK': 35.0, 'DS-MRK-BN-FNV': 35.0, 'DS-THI-T-M': 42.0, 'DS-PK-B01': 9.0}, 'compare': {}, 'costs': {'4': 15.60}}
    omap = {'DS-MRK-BN-BLK': ['DS-MRK-BNO-BLK', 'the-mark-organic-beanie', 'Black', '#000', 'Black', '#000', 'os']}
    R = analyse(vs, sync, cat, base, omap)
    p, s = report(R, sync, cat, omap, base)
    print(p, '\n\n----\n', s)
    assert len(R['changed']) == 2 and len(R['drift']) == 1 and len(R['cost']) == 1 and len(R['new']) == 1
    assert len(R['soldout']) == 1 and len(R['low']) == 1 and 'French Navy' in s and 'EU' in s and 'organic' in s
    print('\nselftest ok')


def main():
    a = sys.argv[1:]
    if '--selftest' in a: return selftest()
    dry = '--dry' in a
    try:
        with open(ORGANIC_MAP) as f: omap = json.load(f)['map']
    except Exception: omap = {}
    print('Shopify: reading variants…', flush=True)
    variants = shopify_variants(); print(f'  {len(variants)} variants', flush=True)
    print('Printful: reading sync products…', flush=True)
    sync = printful_sync(); print(f'  {len(sync)} sync variants', flush=True)
    used = {s['product_id'] for s in sync.values()}
    catalog = printful_catalog(used | {US_TWIN[p] for p in used if p in US_TWIN}); print(f'  {len(catalog)} catalog variants', flush=True)
    base = load_baseline()

    if base is None:
        base = make_baseline(variants, catalog, sync)
        print(first_run_summary(variants))
        if not dry:
            save(base); commit_baseline('Price watch: first baseline (approved prices = today\'s)')
        R = analyse(variants, sync, catalog, base, omap)
        p, s = report(R, sync, catalog, omap, base)
        p = first_run_summary(variants) + ('\n\n' + p if p else '')
    else:
        R = analyse(variants, sync, catalog, base, omap)
        if '--accept' in a:
            skus = pick(a[a.index('--accept') + 1], variants, R)
            print(f'accepting {len(skus)} SKU(s) at today\'s Shopify price')
            for k in sorted(skus)[:60]: print('  ', k, fm(next((v['price'] for v in variants if v['sku'] == k), None)))
            if not dry:
                save(make_baseline(variants, catalog, sync, old=base, only=skus)); commit_baseline(f'Price watch: accept {len(skus)} price(s)')
            base = load_baseline() if not dry else base
            R = analyse(variants, sync, catalog, base, omap)
        if '--restore' in a:
            skus = pick(a[a.index('--restore') + 1], variants, R)
            restore(skus, variants, sync, base, '--apply' in a and not dry)
            if '--apply' in a and not dry:
                print('re-reading after restore…'); variants = shopify_variants(); sync = printful_sync()
                R = analyse(variants, sync, catalog, base, omap)
        p, s = report(R, sync, catalog, omap, base)

    print('\n==== PRICES ====\n' + (p or 'all prices match the approved prices'))
    print('\n==== STOCK ====\n' + (s or 'nothing sold out or low'))
    if dry: return
    stamp = datetime.now(timezone.utc).strftime('%d %b %Y')
    post(PRICE_TITLE, p and f'**Price check, {stamp}.** Nothing has been changed — each fix waits for your go.\n\n' + p,
         'Every price matches the approved price again. Closing.')
    post(STOCK_TITLE, s and f'**Stock check, {stamp}.** Suggestions only; nothing has been changed.\n\n' + s,
         'Nothing sold out, low or untracked. Closing.')


if __name__ == '__main__':
    main()
