#!/usr/bin/env python3
"""Live patch 2026-11-26-ahrefs1 (DRAFT for review), on top of 2026-11-26-sectors1 (which carries seo4, seo3 and bing1).

From the Ahrefs Site Audit of 26 November 2026 (crawl 05:55 UTC, health score 93, 16 issues). Most of the issues are already
fixed by the patches waiting for upload, belong to the host, or are kept by the studio's own decisions; see
docs/PATCH-2026-11-26-AHREFS.md. The code change here:

  1. Structured data (2 errors, /awards/ and /work/peace-pavilion/): the organizer of each exhibition (Cooper Hewitt;
     Museum of Craft and Design) is typed Organization. schema.org allows only Organization or Person for "organizer";
     the museum stays a Museum as the exhibition's location.
  2. The logo on phones (Mujib, 26 November 2026: "Follow the footer size and proportions throughout the site for mobile"):
     up to 700 px wide, the header logo takes the footer logo's size and proportions (64 px mark, 14 px gap, 17 px name at
     line height 1.1) at the top of a page and when the bar turns solid; the bar grows to 84 px to hold it (option A). The
     Design Snippet page's header does the same on phones, with the studio's name shown. Tablets and desktop are unchanged.

Built like sectors1: an exact substitution in the search module, then every page rendered with the old and the new scripts; only
the differences are carried onto the pages whose render changes.

Usage: make_patch_ahrefs1.py <sectors1 full site> <sectors1 patch dir> <folder with more pictures> <out dir>"""
import sys, os, re, json, shutil, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sectors1'))
from render import render, normalize, sizes_of, carry, carry_lines
base, prev, pub, out = sys.argv[1:5]
full = os.path.join(out, 'full'); shutil.rmtree(out, ignore_errors=True); shutil.copytree(base, full)
rd = lambda p: open(p, encoding='utf-8', newline='').read()
def wr(p, t): os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w', encoding='utf-8', newline='').write(t)
h12 = lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest()[:12]
def sub(t, a, b, n=1, what=''):
    c = t.count(a)
    if c != n: raise SystemExit(f'{what}: expected {n} of {a[:100]!r}, found {c}')
    return t.replace(a, b)
def asset(prefix, ext):
    f = [x for x in os.listdir(os.path.join(full, 'assets')) if x.startswith(prefix) and x.endswith(ext)]
    assert len(f) == 1, (prefix, f); return 'assets/' + f[0]
OLD = {k: asset(k + '.', '.js') for k in ['site-6', 'load']}; OLD['site-1'] = asset('site-1.', '.css'); NEW = {}
SITE = 'https://collaborativearchitecture.com'

# 1. the organizer of an exhibition is an Organization (schema.org: Organization or Person)
s6 = rd(os.path.join(full, OLD['site-6']))
s6 = sub(s6, 'organizer:{"@type":"Museum",name:t.venue,url:t.venueUrl}', 'organizer:{"@type":"Organization",name:t.venue,url:t.venueUrl}', 1, 'organizer')
NEW['site-6'] = f'assets/site-6.{h12(s6)}.js'; wr(os.path.join(full, NEW['site-6']), s6)
# 2. the logo on phones: the header takes the footer's logo (added last, so it follows every earlier rule)
LOGO = ('@media(max-width:700px){:root{--hdr:84px}.hdr.solid{--hdr:84px}.brand{gap:14px;line-height:1.1;letter-spacing:normal}'
        '.brand img,.hdr.solid .brand img{width:64px;height:64px}}\n')
css = rd(os.path.join(full, OLD['site-1'])); assert LOGO.strip() not in css
css = css + LOGO if css.endswith('\n') else css + '\n' + LOGO
NEW['site-1'] = f'assets/site-1.{h12(css)}.css'; wr(os.path.join(full, NEW['site-1']), css)
ds = rd(os.path.join(full, 'design-snippet', 'index.html'))
i = ds.find('</style>'); assert i > 0 and ds.count('@media screen and (max-width:900px){') == 1 and ds.find('@media screen and (max-width:900px){') < i
ds = ds[:i] + ('/* 26 November 2026 (Mujib): on phones the header logo takes the main site footer logo\'s size and proportions, with the name */\n'
              '@media screen and (max-width:700px){.top .w{height:84px}.brand{gap:14px;font:600 17px/1.1 var(--body)}.brand img{width:64px;height:64px}.brand span{display:block}}\n') + ds[i:]
wr(os.path.join(full, 'design-snippet', 'index.html'), ds)
load = sub(rd(os.path.join(full, OLD['load'])), '"/' + OLD['site-6'] + '"', '"/' + NEW['site-6'] + '"', 1, 'load')
NEW['load'] = f'assets/load.{h12(load)}.js'; wr(os.path.join(full, NEW['load']), load)
for k in OLD: os.remove(os.path.join(full, OLD[k]))
NEWS = {'/' + OLD['load']: '/' + NEW['load'], '/' + OLD['site-1']: '/' + NEW['site-1']}
PAGES = []
for d, _, fs in os.walk(full):
    for f in fs:
        if not f.endswith('.html'): continue
        p = os.path.join(d, f); t = rd(p)
        if '/' + OLD['load'] in t:
            t = sub(t, '/' + OLD['load'], '/' + NEW['load'], 1, p)
            if '/' + OLD['site-1'] in t: t = sub(t, '/' + OLD['site-1'], '/' + NEW['site-1'], 1, p)
            wr(p, t)
            if f == 'index.html': PAGES.append(re.sub(r'^//', '/', '/' + os.path.relpath(d, full).replace(os.sep, '/').strip('.') + '/'))
PAGES.sort(); print(len(PAGES), 'pages to compare')

# 2. render every page with the old and the new scripts; carry the differences onto the pages whose render changes
old, e1 = render(base, PAGES, [pub], feeds=True)
new, e2 = render(full, PAGES, [pub], feeds=True)
assert not e1 and not e2, (e1[:3], e2[:3])
So, Sn = sizes_of(base), sizes_of(full)
def as_new(t):
    for k in OLD: t = t.replace('/' + OLD[k], '/' + NEW[k])
    return t
pf = lambda p: os.path.join(full, p.lstrip('/'), 'index.html')
rep = {'changed': {}, 'text': {}}
# the structured data of a live page can differ from a fresh render in parts this patch does not touch (Organization areaServed),
# so the organizer change is applied to the live block as a targeted substitution; the render comparison then proves it is the
# only difference
SUBS = [('"organizer":{"@type":"Museum"', '"organizer":{"@type":"Organization"')]
for p in PAGES:
    o, n = as_new(normalize(old[p], So)), normalize(new[p], Sn)
    if o == n: continue
    live0 = rd(pf(p)); live = live0
    for a_, b_ in SUBS: live, o = live.replace(a_, b_), o.replace(a_, b_)
    if o == n:
        assert live != live0, p
        wr(pf(p), live); rep['changed'][p] = [('applied', 'substitution', SUBS[0][1])]; continue
    t, r = carry(live, o, n)
    for s in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S): json.loads(s)
    wr(pf(p), t); rep['changed'][p] = r
FO, FN = old['__feeds__'], new['__feeds__']
for kind in ['md', 'files']:
    for rel in sorted(FN[kind]):
        o, n = FO[kind].get(rel), FN[kind][rel]
        if o == n or o is None: continue
        lp = os.path.join(full, rel)
        if not os.path.exists(lp): rep['text'][rel] = 'not in the site copy, left out'; continue
        live = rd(lp); wr(lp, n if live == o else carry_lines(live, o, n)); rep['text'][rel] = 'replaced' if live == o else 'carried'
TODAY = '2026-11-26'
sm = rd(os.path.join(full, 'sitemap.xml'))
for p in list(rep['changed']) + ['/design-snippet/']:
    sm = re.sub(r'(<url><loc>' + re.escape(SITE + p) + r'</loc><lastmod>)[0-9-]+(</lastmod>)', r'\g<1>' + TODAY + r'\2', sm)
wr(os.path.join(full, 'sitemap.xml'), sm)
wr(os.path.join(full, 'version.txt'), 'Collaborative Architecture website\nversion 2026-11-26-ahrefs1\n'
   'patch on top of 2026-11-23-snippet1 (includes 2026-11-26-sectors1, 2026-11-25-seo4, 2026-11-24-seo3 and 2026-11-24-bing1)\n')

# 3. the upload folder: everything sectors1 uploads, with this patch's versions, plus what changes here
pd = os.path.join(out, 'patch'); up = os.path.join(pd, 'upload')
h = lambda f: hashlib.sha256(open(f, 'rb').read()).hexdigest()
files = []
for d, _, fs in os.walk(full):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), full).replace(os.sep, '/'); b = os.path.join(base, rel)
        if os.path.isfile(os.path.join(prev, 'upload', rel)) or not os.path.isfile(b) or h(b) != h(os.path.join(d, f)): files.append(rel)
for rel in files:
    os.makedirs(os.path.dirname(os.path.join(up, rel)), exist_ok=True); shutil.copyfile(os.path.join(full, rel), os.path.join(up, rel))
dele = [l.strip() for l in open(os.path.join(prev, 'DELETE.txt')) if l.strip()] + [OLD['site-1'], OLD['site-6'], OLD['load']]
assert not any(os.path.exists(os.path.join(full, x)) for x in dele)
open(os.path.join(pd, 'DELETE.txt'), 'w', newline='\r\n').write('\n'.join(dele) + '\n')
urls = set(open(os.path.join(prev, 'indexnow-urls.txt')).read().split()) | {SITE + p for p in rep['changed']} | {SITE + '/design-snippet/'}
open(os.path.join(pd, 'indexnow-urls.txt'), 'w', newline='\n').write('\n'.join(sorted(urls)) + '\n')
json.dump({'old': OLD, 'new': NEW, 'files': sorted(files), **rep}, open(os.path.join(out, 'ahrefs1.json'), 'w'), indent=1)
print(len(files), 'files in the upload folder;', len(rep['changed']), 'changed pages'); print('assets', OLD, '->', NEW)
for p, r in rep['changed'].items(): print('  changed', p, [x[0] + ':' + x[2][:70] for x in r])
for f, r in rep['text'].items(): print('  text', f, r)
