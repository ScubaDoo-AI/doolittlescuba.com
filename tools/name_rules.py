#!/usr/bin/env python3
"""Name rules for printed names (Aquatic Comic name tees; Eric, 14 Nov):
  - letters and numbers only (Latin letters with accents allowed, since the IM Fell font has them)
  - hyphens inside a name (Mary-Jo, Smith-Jones), never at an end or doubled (Eric, 14 Nov)
  - at most ONE space: one or two words ("John Eric")
  - the only special character is @, and only at the start: "@name"
  - no vulgarity, profanity or slurs

The same rules run on the product page (shopify-theme/assets/ds-name-rules.json, read by the
Personalize block) and in the order job (aquatic_print.clean_name → a held order), so a name that slips past
the page is still caught before anything prints.

Word source: better-profanity 0.7.0 word list (MIT), tools/data/…_MIT.txt, curated here:
  ALLOW   real given names / surnames and harmless words in that list (Dick, Willy, Wang, god, rum, …)
  INSIDE  the few words caught even inside a longer name (no real-name clashes), after doubled letters collapse
  python3 tools/name_rules.py --build      # writes the page's asset
  python3 tools/name_rules.py "Name" ...   # checks names
"""
import os, re, sys, json, base64

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'data', 'profanity_wordlist_better-profanity-0.7.0_MIT.txt')
ASSET = os.path.join(os.path.dirname(HERE), 'shopify-theme', 'assets', 'ds-name-rules.json')

LETTERS = 'A-Za-zÀ-ÖØ-öø-ÿ0-9'
WORD = rf'[{LETTERS}]+(?:-[{LETTERS}]+)*'
FORMAT = re.compile(rf'^@?{WORD}(?: {WORD})?$')
LEET = str.maketrans({'0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b', '9': 'g'})
ALLOW = set('''
dick willy fanny paddy guido woody wang dong titi massa seaman seamen gay gays hebe randy rusty
god fat kill rum pot weed pawn organ revue maxi hemp ugly dummy moron stupid sniper murder vodka virgin wazoo omg lmao
lmfao hiv pcp pms uzi napalm foobar fubar dopey drunk lube ovum ovums ovary womb uterus thug steamy strip stroke thrust
seduce mams loin loins racy sissy vixen weirdo nimrod ninny doofus inbred herp herpy herpes valium opium ganja hooch
hootch peyote unwed tinkle toots tramp undies potty prude prig souse soused slope leper gringo homey quicky junkie junky
reefer opiate extacy extasy heroin teat teets teste testes testis testee semen menses tampon wedgie weenie weewee
peepee pee poop fart urine urinal flange facial erect stiffy hump humped organ orally oral pubis pubic scrog scrud
'''.split())
INSIDE = ['fuck', 'fuk', 'fvck', 'fxck', 'phuck', 'phuk', 'shit', 'sh1t', 'cunt', 'nigg', 'nigga', 'whore', 'bitch',
          'pussy', 'dildo', 'jizz', 'wank', 'twat', 'faggot', 'motherf', 'cocksuck', 'asshole']


def words():
    w = {l.strip().lower() for l in open(SRC, encoding='utf-8') if l.strip()}
    return sorted(w - ALLOW)


def norm(s):
    return s.lower().lstrip('@').translate(LEET)


def squash(s):   # doubled letters collapse: "fuuuck" -> "fuck"
    return re.sub(r'(.)\1+', r'\1', s)


_W = None
def problem(name):
    """'' when the name is fine, else a short reason (never echoes the name)."""
    global _W
    if _W is None: _W = set(words())
    s = re.sub(r'\s+', ' ', name or '').strip()
    if not s: return 'empty name'
    if not FORMAT.match(s):
        if s.count(' ') > 1: return 'more than one space'
        if '@' in s[1:] or s == '@': return '@ only at the start, as @name'
        if '-' in s: return 'hyphens only between letters (Mary-Jo)'
        return 'letters, numbers and hyphens only (and @ at the start)'
    toks = [norm(t) for t in re.split(r'[ -]', s)]
    cands = set(toks) | {' '.join(toks), ''.join(toks)} | {squash(t) for t in toks} | {squash(''.join(toks))}
    if cands & _W: return 'not allowed: language'
    flat = squash(''.join(toks))
    if any(squash(w) in flat for w in INSIDE): return 'not allowed: language'
    return ''


def build():
    data = {'v': 1, 'format': FORMAT.pattern, 'leet': dict(zip('0134578 9'.replace(' ', ''), 'oieastbg')),
            'w': base64.b64encode('\n'.join(words()).encode()).decode(),
            'i': base64.b64encode('\n'.join(INSIDE).encode()).decode()}
    os.makedirs(os.path.dirname(ASSET), exist_ok=True)
    json.dump(data, open(ASSET, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('wrote', ASSET, len(words()), 'words,', len(INSIDE), 'inside')


if __name__ == '__main__':
    if sys.argv[1:2] == ['--build']: build()
    else:
        for n in sys.argv[1:]: print(f'{n!r:24} {problem(n) or "ok"}')
