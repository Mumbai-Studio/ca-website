#!/usr/bin/env python3
"""Live patch 2026-11-26-sectors1, stage 2: the pages, the search files and the upload folder.

Every page of the site is rendered twice, with the seo4 scripts and with the patched ones (same viewport, same random seed, the
prerender's settings). A page whose two renders are the same is left exactly as it is live (stage 1 already points it at the new
loader and stylesheet). For a page whose render changes, only the differences between the two renders are carried onto the live
page, so everything else in the live file stays as it is. The six sector pages are new: their render is brought to the live form
(render.normalize; the same rules reproduce the six live discipline pages byte for byte). The Markdown copies and the search files
are handled the same way, line by line.

Usage: pages_sectors1.py <seo4 full site> <stage-1 out dir> <seo4 patch dir> <folder with more pictures (repo public/)>"""
import sys, os, re, json, shutil, hashlib, html as H
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sectors1'))
from render import render, normalize, sizes_of, carry, carry_lines
base, s1, seo4, pub = sys.argv[1:5]
full = os.path.join(s1, 'full'); st1 = json.load(open(os.path.join(s1, 'stage1.json')))
SITE, TODAY, TODAY_T = 'https://collaborativearchitecture.com', '2026-11-26', '26 November 2026'
HERE = os.path.dirname(os.path.abspath(__file__))
SX = json.loads(open(os.path.join(HERE, 'sectors1', 'sectors.min.js'), encoding='utf-8').read().strip()[len('C.sectors='):-1])
NEWP = ['/expertise/' + x['k'] + '/' for x in SX]
rd = lambda p: open(p, encoding='utf-8', newline='').read()
def wr(p, t): os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w', encoding='utf-8', newline='').write(t)
pf = lambda p: os.path.join(full, p.lstrip('/'), 'index.html')

# every page that runs the site's scripts
PAGES = []
for d, _, fs in os.walk(full):
    if 'index.html' in fs:
        p = '/' + os.path.relpath(d, full).replace(os.sep, '/').strip('.') + '/'
        p = re.sub(r'^//', '/', p)
        if '/' + st1['new']['load'] in rd(os.path.join(d, 'index.html')) and p not in NEWP: PAGES.append(p)
PAGES.sort()
print(len(PAGES), 'pages to compare')

old, e1 = render(base, PAGES, [pub], feeds=True)
new, e2 = render(full, PAGES + NEWP, [pub], feeds=True)
assert not e1 and not e2, (e1[:3], e2[:3])
So, Sn = sizes_of(base), sizes_of(full)
def as_new(t):   # the old render with the new asset names, so that only content differs
    for k in st1['old']: t = t.replace('/' + st1['old'][k], '/' + st1['new'][k])
    return t

rep = {'changed': {}, 'new': {}, 'text': {}}
for p in PAGES:
    o, n = as_new(normalize(old[p], So)), normalize(new[p], Sn)
    if o == n: continue
    t, r = carry(rd(pf(p)), o, n)
    for s in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S): json.loads(s)
    wr(pf(p), t); rep['changed'][p] = r
for p in NEWP:
    t = normalize(new[p], Sn)
    bad = [x for x in ['data-shown="x"', 'visibility: hidden', 'data-fb=', 'data-nw=', '127.0.0.1'] if x in t]
    assert not bad, (p, bad)
    for s in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S): json.loads(s)
    assert f'<link rel="canonical" href="{SITE}{p}">' in t, p
    wr(pf(p), t); rep['new'][p] = {'title': H.unescape(re.search(r'<title>(.*?)</title>', t).group(1)), 'bytes': len(t)}

# the Markdown copies and the search files
FO, FN = old['__feeds__'], new['__feeds__']
def text(rel, o, n):
    live_p = os.path.join(full, rel)
    if o == n: return
    if o is None:
        assert any(rel == f'expertise/{x["k"]}/index.md' for x in SX), ('a search file the live site does not have', rel)
        wr(live_p, n); rep['text'][rel] = 'new'; return
    if not os.path.exists(live_p):
        # a page's Markdown copy that is not in the seo4 copy of the site: the live one is the generator's output (it reproduces
        # every live copy at hand byte for byte), so the new output replaces it
        if rel.endswith('index.md') and os.path.exists(os.path.join(full, rel[:-len('index.md')], 'index.html')):
            wr(live_p, n); rep['text'][rel] = 'generated'; return
        rep['text'][rel] = 'not on the live site, left out'; return
    live = rd(live_p)
    wr(live_p, n if live == o else carry_lines(live, o, n)); rep['text'][rel] = 'replaced' if live == o else 'carried'
for rel in sorted(FN['md']): text(rel, FO['md'].get(rel), FN['md'][rel])
for rel in sorted(FN['files']): text(rel, as_new(FO['files'].get(rel)) if FO['files'].get(rel) is not None else None, FN['files'][rel])
# sitemap: the pages that changed carry today's date
sm = rd(os.path.join(full, 'sitemap.xml'))
for p in sorted(set(rep['changed']) | set(NEWP)):
    sm, n = re.subn(r'(<url><loc>' + re.escape(SITE + p) + r'</loc><lastmod>)[0-9-]+(</lastmod>)', r'\g<1>' + TODAY + r'\2', sm)
    assert n == 1 or p not in NEWP, p
    if not n: print('  not in the sitemap:', p)
wr(os.path.join(full, 'sitemap.xml'), sm)
for f in ['llms.txt', 'llms-full.txt']:
    t = rd(os.path.join(full, f)); assert t.count('Last updated: 25 November 2026') == 1, f
    wr(os.path.join(full, f), t.replace('Last updated: 25 November 2026', 'Last updated: ' + TODAY_T))
wr(os.path.join(full, 'version.txt'), 'Collaborative Architecture website\nversion 2026-11-26-sectors1\n'
   'patch on top of 2026-11-23-snippet1 (includes 2026-11-25-seo4, 2026-11-24-seo3 and 2026-11-24-bing1)\n')

# ---------------------------------------------------------------- the upload folder -------------------------------------------------------
out = os.path.join(s1, 'patch'); up = os.path.join(out, 'upload'); shutil.rmtree(out, ignore_errors=True)
h = lambda f: hashlib.sha256(open(f, 'rb').read()).hexdigest()
files = []
for d, _, fs in os.walk(full):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), full).replace(os.sep, '/'); b = os.path.join(base, rel)
        in4 = os.path.isfile(os.path.join(seo4, 'upload', rel))
        if in4 or not os.path.isfile(b) or h(b) != h(os.path.join(d, f)): files.append(rel)
for rel in files:
    os.makedirs(os.path.dirname(os.path.join(up, rel)), exist_ok=True); shutil.copyfile(os.path.join(full, rel), os.path.join(up, rel))
old4 = [l.strip() for l in open(os.path.join(seo4, 'DELETE.txt')) if l.strip()]
dele = old4 + [st1['old'][k] for k in ['site-1', 'site-3', 'site-6', 'site-7', 'data-ca-data-j', 'sizes', 'load']]
assert not any(os.path.exists(os.path.join(full, x)) for x in dele)
open(os.path.join(out, 'DELETE.txt'), 'w', newline='\r\n').write('\n'.join(dele) + '\n')
urls = set(open(os.path.join(seo4, 'indexnow-urls.txt')).read().split()) | {SITE + p for p in list(rep['changed']) + NEWP} | {SITE + '/llms.txt', SITE + '/sitemap.xml'}
open(os.path.join(out, 'indexnow-urls.txt'), 'w', newline='\n').write('\n'.join(sorted(urls)) + '\n')
json.dump({'files': sorted(files), **rep}, open(os.path.join(s1, 'stage2.json'), 'w'), indent=1, ensure_ascii=False)
print(len(files), 'files in the upload folder;', len(rep['changed']), 'changed pages;', len(NEWP), 'new pages;', len(rep['text']), 'text files')
for p, r in rep['changed'].items(): print('  changed', p, [x[0] + ':' + x[2][:60] for x in r])
for p, r in rep['new'].items(): print('  new', p, r)
for f, r in rep['text'].items(): print('  text', f, r)
