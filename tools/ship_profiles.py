#!/usr/bin/env python3
"""Shipping for custom / personalized items (Eric, 14 Nov: option B).

The custom products (78 Aquatic name tees, Make it yours tee and cap) are stocked at "Shop location" because the
custom-orders job, not Printful's sync, sends them to print, so they fell into Shopify's General profile ($8, free
over $70, $15 Express). Printful's own profiles only cover the Printful location, so the custom items can't simply
join them. Instead two profiles at Shop location charge the same US rates as Printful's profiles for regular shirts
and caps:
  Custom tees (made to order, Printful rates)   Standard $4.95 · Express $9.99   (Printful: Tshirts #PF-FRG1001)
  Custom caps (made to order, Printful rates)   Standard $4.69 · Express $11.99  (Printful: Snapbacks #PF-FRG1096)
US only, as the shipping policy says. Idempotent: creates the profiles once, then adds any custom variant not yet in.
The digitization fee ships nothing and stays where it is.
  tools/ship_profiles.py [--apply]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aquatic_order as AO

SHOP_LOC = 'gid://shopify/Location/88138612922'
PROFILES = {'tees': ('Custom tees (made to order, Printful rates)', '4.95', '9.99',
                     'tag:personalize\\:1 OR tag:personalize\\:buddy OR tag:personalize\\:couple OR handle:make-it-yours-tee'),
            'caps': ('Custom caps (made to order, Printful rates)', '4.69', '11.99', 'handle:make-it-yours-cap')}
apply = '--apply' in sys.argv


def variants(q):
    out, after = [], None
    while True:
        r = AO.shopify('query($q: String!, $a: String) { products(first: 50, after: $a, query: $q) { pageInfo { hasNextPage endCursor } '
                       'nodes { variants(first: 50) { nodes { id deliveryProfile { id name } } } } } }', {'q': q, 'a': after})['products']
        out += [v for p in r['nodes'] for v in p['variants']['nodes']]
        if not r['pageInfo']['hasNextPage']: return out
        after = r['pageInfo']['endCursor']


have = {p['name']: p['id'] for p in AO.shopify('{ deliveryProfiles(first: 50) { nodes { id name } } }')['deliveryProfiles']['nodes']}
for key, (name, std, exp, q) in PROFILES.items():
    vs = variants(q); todo = [v['id'] for v in vs if (v.get('deliveryProfile') or {}).get('name') != name]
    print(f'{name}: {len(vs)} variants, {len(todo)} to move', '(profile exists)' if name in have else '(new profile)')
    if not apply or not todo: continue
    for i in range(0, len(todo), 250):
        chunk = todo[i:i + 250]
        if name not in have:
            prof = {'name': name, 'variantsToAssociate': chunk, 'locationGroupsToCreate': [{
                'locations': [SHOP_LOC], 'zonesToCreate': [{'name': 'United States', 'countries': [{'code': 'US', 'includeAllProvinces': True}],
                'methodDefinitionsToCreate': [
                    {'name': 'Standard (USPS Ground Advantage)', 'active': True, 'rateDefinition': {'price': {'amount': std, 'currencyCode': 'USD'}}},
                    {'name': 'Express', 'active': True, 'rateDefinition': {'price': {'amount': exp, 'currencyCode': 'USD'}}}]}]}]}
            r = AO.shopify('mutation($p: DeliveryProfileInput!) { deliveryProfileCreate(profile: $p) { profile { id } userErrors { field message } } }',
                           {'p': prof})['deliveryProfileCreate']
            if r['userErrors']: sys.exit(f'{name}: {r["userErrors"]}')
            have[name] = r['profile']['id']
        else:
            r = AO.shopify('mutation($id: ID!, $p: DeliveryProfileInput!) { deliveryProfileUpdate(id: $id, profile: $p) { profile { id } userErrors { field message } } }',
                           {'id': have[name], 'p': {'variantsToAssociate': chunk}})['deliveryProfileUpdate']
            if r['userErrors']: sys.exit(f'{name}: {r["userErrors"]}')
        print(f'  moved {len(chunk)}')
if not apply: print('dry run: add --apply')
