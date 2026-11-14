#!/usr/bin/env python3
"""Push store policies from policies/*.html to Shopify through the Doolittle Order Bot app (write_legal_policies).
  tools/policy_push.py [--apply] refund shipping      # files policies/refund.html, policies/shipping.html
Dry run by default: shows whether each differs from the live policy. Before writing, the live text is saved to
policy-backups/ (an artifact of the run)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aquatic_order as AO
TYPES = {'refund': 'REFUND_POLICY', 'shipping': 'SHIPPING_POLICY', 'terms': 'TERMS_OF_SERVICE', 'privacy': 'PRIVACY_POLICY', 'contact': 'CONTACT_INFORMATION'}
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'policies')
a = sys.argv[1:]; apply = '--apply' in a; names = [x for x in a if x != '--apply'] or sys.exit(__doc__)
live = {p['type']: p['body'] for p in AO.shopify('{ shop { shopPolicies { type body } } }')['shop']['shopPolicies']}
for n in names:
    t = TYPES[n]; new = open(os.path.join(ROOT, n + '.html'), encoding='utf-8').read().strip()
    if live.get(t, '').strip() == new: print('same    ', n); continue
    print('CHANGED ', n, f'({len(live.get(t, ""))} → {len(new)} chars)')
    os.makedirs('policy-backups', exist_ok=True); open(f'policy-backups/{n}.html', 'w', encoding='utf-8').write(live.get(t, ''))
    if not apply: continue
    r = AO.shopify('mutation($p: ShopPolicyInput!) { shopPolicyUpdate(shopPolicy: $p) { shopPolicy { type updatedAt } userErrors { message } } }',
                   {'p': {'type': t, 'body': new}})['shopPolicyUpdate']
    print('  written' if not r['userErrors'] else '  ERRORS ' + str(r['userErrors']))
if not apply: print('dry run: add --apply to write')
