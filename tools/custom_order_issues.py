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
    edit = r.get('design_edits')
    title = f'Custom order {r["order"]}: {"draft ready to confirm" if r["status"] == "draft" else "HELD"}' + (' · ⚠ DESIGN EDIT' if edit else '')
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
               'no-address': 'no shipping address visible to the app', 'no-design': 'a Make it yours line without a design',
               'name': 'a personalized Aquatic tee whose name is missing, too long, or breaks the name rules (format or language)',
               'fee': 'a cap design with a new line of text but no embroidery digitization fee in the order',
               'cap-text': 'a cap line too long to stitch at the 0.25 in letter floor'}.get(r.get('reason_kind'), 'see the order in Shopify')
        body += [f'Held: {why}.', 'Nothing was sent to Printful. Open the order in Shopify admin for the details.']
    if edit:   # a long name was fitted: the edit is described, the names themselves stay out of this public issue
        body += ['', '**⚠ Design edit needed during approval.** The customer\'s name(s) did not fit the standard layout and were fitted automatically:']
        body += [f'- {e}' for e in edit]
        body += ['', 'The customer agreed to the resize on the product page. Check both print files in the Printful draft '
                     '(the item is marked ⚠ DESIGN EDIT) before confirming: readability, line breaks, the joke still reading right.']
    if r.get('fee_due') or r.get('fee_paid'):
        body += ['', f'Embroidery digitization: due ${r.get("fee_due", 0):.2f}, paid ${r.get("fee_paid", 0):.2f}.'
                 + (f' **Refund ${r["fee_refund"]:.2f}** of it (charged once per design).' if r.get('fee_refund') else '')]
    subprocess.run(['gh', 'issue', 'create', '--title', title, '--body', '\n'.join(body)], check=True)
    print('opened:', title)
