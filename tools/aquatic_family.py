#!/usr/bin/env python3
"""Surface Interval personalized tees with the Doolittle family as the sample names, for the site and store mockups.

Writes renders/aquatic-family/AC-<code>_{front,back}.png (Printful print masters, 12 x 16 in) and names.json.
The site serves them, so tools/printful_read.py mockup:aquaticfamily:<SKU> can hand them to Printful's mockup generator.
The family: Eric (husband), Allie (wife), Mason (son), Jade (daughter). Husband & wife shirts are Eric & Allie.
Eric is the air hog, Allie is not: the air jokes are pinned (OVERRIDE); the rest rotate the four names.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aquatic_print as AP

FAM = ['Eric', 'Allie', 'Mason', 'Jade']
PAIRS = [('Jade', 'Mason'), ('Eric', 'Mason'), ('Allie', 'Jade'), ('Mason', 'Eric'), ('Jade', 'Allie'), ('Mason', 'Jade')]
OVERRIDE = {'W01': ('Allie', None),        # breathes like a camel, surfaces at 1800
            'R02': ('Eric', None),         # the vacuum
            'B04': ('Allie', 'Mason'),     # Allie has the air, Mason has the snacks
            'B05': ('Allie', 'Eric')}      # Allie breathes slow, Eric needs a tank for the story
OUT = os.path.join(AP.ROOT, 'renders', 'aquatic-family')


def names(d, i):
    if d['code'] in OVERRIDE: return OVERRIDE[d['code']]
    sub = d['code'][0]
    if sub in 'CM': return 'Eric', 'Allie'       # {H} husband, {W} wife
    if d['names'] == 2: return PAIRS[i % len(PAIRS)]
    return FAM[(i + (2 if sub == 'R' else 0)) % 4], None


if __name__ == '__main__':
    done = {}; count = {}
    for d in AP.D['designs']:
        if not d['names']: continue
        sub = d['code'][0]; i = count.get(sub, 0); count[sub] = i + 1
        n1, n2 = names(d, i); nm = AP.names_for(d, n1, n2)
        AP.build(d, OUT, nm); done[d['code']] = nm; print(d['code'], nm, flush=True)
    json.dump(done, open(os.path.join(OUT, 'names.json'), 'w'), indent=1)
