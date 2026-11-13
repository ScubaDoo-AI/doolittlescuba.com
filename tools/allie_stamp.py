#!/usr/bin/env python3
"""Allie's logbook stamp: scan the QR on her stamp -> her About section, stamped.

Her stamp's QR encodes https://doolittlescuba.com/?src=stamp-allie (the home page).
Writes two things, idempotently (safe to re-run):
  1. A one-line hand-off at the top of the home page's <head>: a visit tagged
     src=stamp-allie goes straight to /about/?src=stamp-allie#allie. Every other visit is untouched.
  2. The "Stamped by Allie" welcome card into about/index.html, between
     <!-- ALLIE-STAMP:START --> / <!-- ALLIE-STAMP:END --> markers, right above her section.
     The card stays hidden unless the visitor arrived with ?src=allie-stamp (or #stamped).

Usage (from the repo root):  python3 tools/allie_stamp.py
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ABOUT = ROOT / "about" / "index.html"

HOME = ROOT / "index.html"
# Her stamp's QR encodes https://doolittlescuba.com/?src=stamp-allie (decoded from the production art, 13 Nov 2026).
TARGET = "/about/?src=stamp-allie#allie"
HANDOFF = f"""<!-- ALLIE-STAMP-HANDOFF:START --><script>/* Allie's logbook stamp QR = /?src=stamp-allie -> her About section */if(/[?&]src=stamp-allie(&|$)/.test(location.search))location.replace('{TARGET}');</script><!-- ALLIE-STAMP-HANDOFF:END -->
"""

BLOCK = r"""<!-- ALLIE-STAMP:START -->
<style>
/* Allie's stamp: a logbook entry, stamped in pink-fin ink. Hidden unless ?src=allie-stamp */
.allie-stamp{--pink:#D6457A;position:relative;margin:clamp(28px,5vw,44px) 0 0;padding:clamp(22px,4vw,34px);background:var(--panel);border:1.5px solid var(--rule);border-left:6px solid var(--pink);border-radius:3px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px 28px;align-items:center;scroll-margin-top:16px;
  background-image:repeating-linear-gradient(transparent 0 31px,var(--contour) 31px 32px)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .allie-stamp{--pink:#F07AA3}}
:root[data-theme="dark"] .allie-stamp{--pink:#F07AA3}
.allie-stamp[hidden]{display:none}
.allie-stamp .eyebrow{color:var(--pink)}
.allie-stamp h2{font-size:var(--s3);line-height:1.1;color:var(--ink);margin:6px 0 10px}
.allie-stamp p{max-width:56ch}
.allie-stamp .log{margin-top:14px;display:grid;grid-template-columns:auto minmax(0,1fr);max-width:440px;border-top:1.5px solid var(--ink)}
.allie-stamp .log dt,.allie-stamp .log dd{margin:0;padding:8px 0;border-bottom:1px solid var(--rule)}
.allie-stamp .log dt{font-family:var(--f-data);font-size:var(--s-1);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding-right:18px}
.allie-stamp .log dd{font-family:var(--f-data);font-variant-numeric:tabular-nums}
.allie-stamp .acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.allie-stamp .acts a{font:500 var(--s0)/1 var(--f-body);text-decoration:none;padding:12px 18px;border-radius:3px}
.allie-stamp .acts .go{background:var(--brand-red);color:#fff}
.allie-stamp .acts .meet{border:1.5px solid var(--ink);color:var(--ink)}
.allie-stamp .close{position:absolute;top:8px;right:10px;background:none;border:0;font:500 1.4rem/1 var(--f-body);color:var(--muted);cursor:pointer;padding:6px}
/* the rubber stamp itself */
.allie-stamp .ink{width:clamp(150px,20vw,200px);aspect-ratio:1;border-radius:50%;border:4px double var(--pink);color:var(--pink);display:grid;place-items:center;text-align:center;transform:rotate(-12deg);font-family:var(--f-data);text-transform:uppercase;letter-spacing:.12em;line-height:1.25;padding:14px;mix-blend-mode:multiply;opacity:.92}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .allie-stamp .ink{mix-blend-mode:normal}}
:root[data-theme="dark"] .allie-stamp .ink{mix-blend-mode:normal}
.allie-stamp .ink b{display:block;font:700 clamp(2rem,3.6vw,2.6rem)/1 var(--f-display);letter-spacing:.02em;text-transform:none;margin:6px 0}
.allie-stamp .ink small{font-size:.7rem;font-weight:500;display:block}
.allie-stamp.landed .ink{animation:allie-thump .55s cubic-bezier(.2,1.6,.4,1) .25s both}
@keyframes allie-thump{0%{transform:rotate(-12deg) scale(2.2);opacity:0}100%{transform:rotate(-12deg) scale(1);opacity:.92}}
@media (prefers-reduced-motion: reduce){.allie-stamp.landed .ink{animation:none}}
/* her section, highlighted for stamped visitors */
#allie.stamped .role{color:var(--pink,#D6457A)}
@media (max-width:640px){.allie-stamp{grid-template-columns:minmax(0,1fr)}.allie-stamp .ink{order:-1;justify-self:end;width:132px;margin:-6px 18px -40px 0}.allie-stamp .ink b{font-size:1.7rem}.allie-stamp .ink small{font-size:.58rem}}
</style>
<aside class="allie-stamp" id="stamped" aria-labelledby="stamped-h" hidden>
<button class="close" type="button" aria-label="Close" data-umami-event="allie-stamp-close">&times;</button>
<div>
<p class="eyebrow">Logbook entry</p>
<h2 id="stamped-h">You&rsquo;ve been stamped by Allie</h2>
<p>That stamp in your logbook came from Allie Doolittle: Master Scuba Diver, pink fins, and the reason every Doolittle Scuba plate is right before it prints. She checks the coordinates, the spellings and the depths. Now she has checked your logbook too.</p>
<dl class="log"><dt>Stamped by</dt><dd>Allie Doolittle</dd><dt>Scanned</dt><dd data-stamp-date>&mdash;</dd><dt>Buddy</dt><dd>You</dd></dl>
<div class="acts"><a class="meet" href="#allie" data-umami-event="allie-stamp-meet">Meet Allie</a><a class="go" href="/#lines" data-umami-event="allie-stamp-designs">See the designs</a></div>
</div>
<div class="ink" aria-hidden="true"><span><small>Doolittle Scuba</small><b>Allie</b><small>&#9733; Logbook verified &#9733;</small></span></div>
</aside>
<script>
(function(){
  var q=new URLSearchParams(location.search), h=location.hash;
  var src=q.get('src'); if(src!=='stamp-allie' && src!=='allie-stamp' && h!=='#stamped') return;
  var card=document.getElementById('stamped'), sec=document.getElementById('allie');
  if(!card) return;
  card.hidden=false; card.classList.add('landed'); if(sec) sec.classList.add('stamped');
  var d=card.querySelector('[data-stamp-date]');
  if(d) d.textContent=new Date().toLocaleDateString('en-US',{day:'numeric',month:'short',year:'numeric'});
  // tidy the address bar so a refresh or a share does not re-stamp; keep the hit in Umami
  try{ history.replaceState(null,'',location.pathname+'#allie'); }catch(e){}
  addEventListener('load',function(){ try{ window.umami && umami.track('allie-stamp-scan'); }catch(e){} });
  var go=function(){ card.scrollIntoView({block:'start'}); };
  requestAnimationFrame(go); addEventListener('load',go); if(document.fonts) document.fonts.ready.then(go);
  card.querySelector('.close').addEventListener('click',function(){ card.hidden=true; if(sec) sec.scrollIntoView({block:'start'}); });
})();
</script>
<!-- ALLIE-STAMP:END -->
"""

def main():
    # 1. home page hands stamp scans straight to her section (first thing in <head>, before anything paints)
    home = HOME.read_text(encoding="utf-8")
    home = re.sub(r"<!-- ALLIE-STAMP-HANDOFF:START -->.*?<!-- ALLIE-STAMP-HANDOFF:END -->\n?", "", home, flags=re.S)
    m = re.search(r'<meta charset="utf-8">\n?', home)
    if not m:
        sys.exit("no <meta charset> in index.html")
    home = home[:m.end()] + HANDOFF + home[m.end():]
    HOME.write_text(home, encoding="utf-8")
    print("updated", HOME.relative_to(ROOT))

    # 2. welcome card into the About page
    html = ABOUT.read_text(encoding="utf-8")
    html = re.sub(r"<!-- ALLIE-STAMP:START -->.*?<!-- ALLIE-STAMP:END -->\n?", "", html, flags=re.S)
    anchor = re.search(r'<section class="person flip" id="allie"', html)
    if not anchor:
        sys.exit("Allie's section (id=\"allie\") not found in about/index.html")
    html = html[:anchor.start()] + BLOCK + html[anchor.start():]
    ABOUT.write_text(html, encoding="utf-8")
    print("updated", ABOUT.relative_to(ROOT))

if __name__ == "__main__":
    main()
