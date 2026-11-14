#!/usr/bin/env python3
"""Daily: custom-order drafts still waiting for Eric's approval at Printful → one GitHub issue, updated each morning.

Lists Printful DRAFT orders made by the custom-orders job (external id MY<n>, or <n> from aquatic_order.py) with their
age. Opens the issue "Custom drafts waiting for approval" when there are any, comments on it each day while they
wait, and closes it when none are left. Public repo: order numbers, Printful ids and ages only.
  tools/custom_reminder.py [--dry]
"""
import os, sys, time, json, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aquatic_order as AO

TITLE = 'Custom drafts waiting for approval'
tok = os.environ.get('PRINTFUL_TOKEN') or sys.exit('PRINTFUL_TOKEN not set')
code, r = AO.http('GET', 'https://api.printful.com/orders?status=draft&limit=100',
                  {'Authorization': 'Bearer ' + tok, 'X-PF-Store-Id': AO.PF_STORE})
if code >= 300: sys.exit(f'Printful: {code} {r}')
now = time.time(); rows = []
for o in r.get('result') or []:
    ext = str(o.get('external_id') or '')
    if not re.fullmatch(r'MY\d+|\d+', ext): continue          # samples and other drafts are not customer orders
    hrs = (now - (o.get('created') or now)) / 3600
    rows.append((hrs, ext, o['id']))
rows.sort(reverse=True)
lines = [f'- **#{e.removeprefix("MY")}**: Printful draft {i}, waiting **{h:.0f} h**{" ⚠ over a day" if h >= 24 else ""} '
         f'→ https://www.printful.com/dashboard/default/orders?id={i}' for h, e, i in rows]
print(f'{len(rows)} custom draft(s) waiting' + ('' if not rows else f'; oldest {rows[0][0]:.0f} h'))
if '--dry' in sys.argv: print('\n'.join(lines)); sys.exit(0)

gh = lambda *a: subprocess.run(['gh', *a], capture_output=True, text=True, check=True).stdout
found = json.loads(gh('issue', 'list', '--state', 'open', '--search', f'"{TITLE}" in:title', '--json', 'number,title'))
issue = next((x['number'] for x in found if x['title'] == TITLE), None)
if not rows:
    if issue: gh('issue', 'close', str(issue), '--comment', 'All custom drafts are approved. Closing.')
    sys.exit(0)
body = '\n'.join([f'{len(rows)} custom order draft(s) are waiting for your check at Printful. Nothing prints until each '
                  'is confirmed (Printful dashboard, or Actions → Custom orders → mode **confirm** + printful_id).', ''] + lines
                 + ['', 'Orders marked ⚠ DESIGN EDIT in Printful had a long name fitted: check both print files first.'])
if issue: gh('issue', 'comment', str(issue), '--body', body)
else: gh('issue', 'create', '--title', TITLE, '--body', body)
