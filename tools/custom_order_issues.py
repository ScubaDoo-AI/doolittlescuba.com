#!/usr/bin/env python3
"""One GitHub issue per custom order that became a Printful draft or was held (run by the Custom orders workflow).
An issue is opened once per order and status: the title carries both, and existing titles are checked first."""
import json, subprocess, sys

reps = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else []
todo = [r for r in reps if r['status'] in ('draft', 'held')]
if not todo: sys.exit(0)
have = subprocess.run(['gh', 'issue', 'list', '--state', 'all', '--limit', '300', '--search', 'Custom order in:title',
                       '--json', 'title', '--jq', '.[].title'], capture_output=True, text=True, check=True).stdout.splitlines()
for r in todo:
    title = f'Custom order {r["order"]}: {"draft ready to confirm" if r["status"] == "draft" else "HELD"}'
    if title in have: continue
    # Public repo: no buyer names, lines of text, addresses or mockup links here. Details are in Shopify and Printful.
    body = [f'**{r["order"]}** · {r["status"]} · {r["lines"]} custom line(s)', '']
    if r['status'] == 'draft':
        c = r.get('costs') or {}
        body += [f'Printful draft **{r["printful_id"]}** (external id {r["external_id"]}), not charged. Printful total {c.get("total")} {c.get("currency")}.',
                 f'Check the mockup and files: {r["dashboard"]}',
                 f'Then confirm in Printful, or Actions → Custom orders → mode **confirm**, printful_id **{r["printful_id"]}**.']
    else:
        why = {'logo': 'wholesale / dive shop logo order: quote by quantity (DS mark on the sleeve, no shark signature)', 'home-port': 'Home Port chest block (made by hand)',
               'no-address': 'no shipping address visible to the app', 'no-design': 'a Make it yours line without a design'}.get(r.get('reason_kind'), 'see the order in Shopify')
        body += [f'Held: {why}.', 'Nothing was sent to Printful. Open the order in Shopify admin for the details.']
    subprocess.run(['gh', 'issue', 'create', '--title', title, '--body', '\n'.join(body)], check=True)
    print('opened:', title)
