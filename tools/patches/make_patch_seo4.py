#!/usr/bin/env python3
"""Live patch 2026-11-25-seo4, on top of 2026-11-23-snippet1. It carries seo3 and bing1 (neither uploaded yet) and adds the
items of the SEO, AEO and GEO audit of 24 November 2026 that change nothing a visitor sees on a page:

  1. Search titles (W7, 9.1, Appendix B): the brand suffix is added only while the title stays within 60 characters (was 65);
     three titles longer than 60 on their own are shortened; the Design Snippet's title and description are shortened.
  2. Contact (W7): the lines of the heading are separated by a space before each line break, so text readers no longer
     read "MumbaiStudioBe in touch withCollaborativeStudios". The same heading in the closing band of Home and Studio.
  3. Skip link (W7): eight Gulf city pages pointed their "Skip to content" link at the Dubai page.
  4. Collaborative Lab (W3): the five strand pages name /lab/ as their canonical address and leave the sitemap.
  5. Mumbai studio (9.2): map coordinates, opening hours and map link in the structured data.
  6. llms.txt and llms-full.txt (6.3): a "Last updated" line.
  7. BingSiteAuth.xml (bing1).

Usage: make_patch_seo4.py <seo3 upload folder> <BingSiteAuth.xml> <out dir>"""
import sys, os, re, hashlib, shutil, json, html
src, bing, out = sys.argv[1:4]
up = os.path.join(out, 'upload'); shutil.rmtree(out, ignore_errors=True); shutil.copytree(src, up)
SITE = 'https://collaborativearchitecture.com'; BRAND = ' | Collaborative Architecture'; TODAY = '2026-11-25'
rd = lambda p: open(os.path.join(up, p), encoding='utf-8', newline='').read()
def wr(p, t):
    q = os.path.join(up, p); os.makedirs(os.path.dirname(q), exist_ok=True); open(q, 'w', encoding='utf-8', newline='').write(t)
h12 = lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest()[:12]
def sub(t, a, b, n=1, what=''):
    c = t.count(a)
    if c != n: raise SystemExit(f'{what}: expected {n} of {a[:90]!r}, found {c}')
    return t.replace(a, b)
def asset(prefix, ext):
    f = [x for x in os.listdir(os.path.join(up, 'assets')) if x.startswith(prefix) and x.endswith(ext)]
    assert len(f) == 1, (prefix, f); return 'assets/' + f[0]
CSS0, LOAD0, S30, S60, S70, D0 = asset('site-1.', '.css'), asset('load.', '.js'), asset('site-3.', '.js'), asset('site-6.', '.js'), asset('site-7.', '.js'), asset('data-ca-data-j.', '.js')

TITLES = {  # titles longer than 60 characters without the brand suffix
    'Reflected Topography, Bearys Global Research Triangle (BGRT), Bengaluru': 'Reflected Topography, BGRT (Bearys Global), Bengaluru',
    'Stacked Tectonics, JDT Islam primary school, Kozhikode (Calicut)': 'Stacked Tectonics, JDT Islam primary school, Kozhikode',
    'Material Cartographies: Bahrain Pavilion, Venice Biennale 2027': 'Material Cartographies: Bahrain Pavilion, Venice Biennale',
}
assert all(len(v) <= 60 for v in TITLES.values())
LAB = ['design-research', 'policy-advocacy', 'epistemologies', 'architectural-cartographies', 'newsletters']
GEO = {'lat': 18.9961356, 'lng': 72.8407838, 'map': 'https://www.google.com/maps?cid=3913782904850764747'}
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
H_OLD, H_NEW = 'Be in touch with<br>Collaborative<br>Studios', 'Be in touch with <br>Collaborative <br>Studios'

# --- the scripts ----------------------------------------------------------------------------------------------------------
s6 = rd(S60)
s6 = sub(s6, '(n+l.brandSep+l.name).length<=65?', '(n+l.brandSep+l.name).length<=60?', 1, 'site-6 title rule')
s6 = sub(s6, 'const N=we[e]||e,o=c(k(N)),', 'const N=we[e]||e,o=c(k(/^lab-/.test(e)?"lab":N)),', 1, 'site-6 lab canonical')
s6 = sub(s6, 'name:e.name,address:st(e),telephone:e.tel,',
         'name:e.name,address:st(e),geo:e.id==="mumbai"?{"@type":"GeoCoordinates",latitude:%s,longitude:%s}:void 0,'
         'openingHoursSpecification:e.id==="mumbai"?[{"@type":"OpeningHoursSpecification",dayOfWeek:%s,opens:"10:00",closes:"19:00"}]:void 0,'
         'hasMap:e.id==="mumbai"?"%s":void 0,telephone:e.tel,' % (GEO['lat'], GEO['lng'], json.dumps(DAYS, separators=(',', ':')), GEO['map']), 1, 'site-6 studio')
S61 = f'assets/site-6.{h12(s6)}.js'; wr(S61, s6)
dj = rd(D0)
for a in list(TITLES)[:2]: dj = sub(dj, '\\"title\\":\\"' + a + '\\"', '\\"title\\":\\"' + TITLES[a] + '\\"', 1, 'data title')
D1 = f'assets/data-ca-data-j.{h12(dj)}.js'; wr(D1, dj)
s3 = rd(S30); a = list(TITLES)[2]; s3 = sub(s3, 'seo:{title:"' + a + '"', 'seo:{title:"' + TITLES[a] + '"', 1, 'site-3 title')
S31 = f'assets/site-3.{h12(s3)}.js'; wr(S31, s3)
s7 = rd(S70)
s7 = sub(s7, 'ei=e=>p(C.studios[e].n.split(",")[0]).replace(" ","<br>")', 'ei=e=>p(C.studios[e].n.split(",")[0]).replace(" "," <br>")+" "', 1, 'site-7 studio name')
s7 = sub(s7, H_OLD, H_NEW, 2, 'site-7 heading')
S71 = f'assets/site-7.{h12(s7)}.js'; wr(S71, s7)
load = rd(LOAD0)
for a, b in [(S30, S31), (S60, S61), (S70, S71), (D0, D1)]:
    load = sub(load, '/' + a, '/' + b, 1, 'load ' + a); os.remove(os.path.join(up, a))
LOAD1 = f'assets/load.{h12(load)}.js'; wr(LOAD1, load); os.remove(os.path.join(up, LOAD0))

# --- the pages --------------------------------------------------------------------------------------------------------------
st = {'titles': {}, 'skip': [], 'lab': [], 'h1': [], 'geo': []}
for d, _, fs in os.walk(up):
    for f in fs:
        if not f.endswith('.html'): continue
        p = os.path.relpath(os.path.join(d, f), up).replace(os.sep, '/'); t = rd(p)
        if LOAD0 not in t: continue          # the standalone Design Snippet page is handled below
        own = '/' + (p[:-len('index.html')] if p.endswith('index.html') else p)
        t = sub(t, '/' + LOAD0, '/' + LOAD1, 1, p)
        # 1. titles
        m = re.search(r'<title>(.*?)</title>', t); old = html.unescape(m.group(1)); base = old[:-len(BRAND)] if old.endswith(BRAND) else old
        base = TITLES.get(base, base); new = base + BRAND if len(base + BRAND) <= 60 else base
        if own == '/': new = old
        if new != old:
            assert len(new) <= 60, (p, new)
            eo, en = html.escape(old, quote=True), html.escape(new, quote=True); jo, jn = json.dumps(old, ensure_ascii=False)[1:-1], json.dumps(new, ensure_ascii=False)[1:-1]
            n = 0
            for a, b in [(f'<title>{m.group(1)}</title>', f'<title>{html.escape(new, quote=False)}</title>'), (f'property="og:title" content="{eo}"', f'property="og:title" content="{en}"'),
                         (f'name="twitter:title" content="{eo}"', f'name="twitter:title" content="{en}"'), (f'"name":"{jo}"', f'"name":"{jn}"')]:
                c = t.count(a); n += c; t = t.replace(a, b)
            assert n >= 4 and old not in html.unescape(t), (p, n, old)
            st['titles'][own] = (old, new)
        # 3. skip link
        m = re.search(r'<a class="skip" href="([^"]+)"', t)
        if m and p.endswith('index.html') and m.group(1) != own + '#app':
            t = t.replace(m.group(0), f'<a class="skip" href="{own}#app"'); st['skip'].append(own)
        # 4. Lab strands
        if own in [f'/lab/{k}/' for k in LAB]:
            t = sub(t, f'<link rel="canonical" href="{SITE}{own}">', f'<link rel="canonical" href="{SITE}/lab/">', 1, p)
            t = sub(t, f'<meta property="og:url" content="{SITE}{own}">', f'<meta property="og:url" content="{SITE}/lab/">', 1, p)
            t, n = re.subn(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+" data-ca-hl="1">\n?', '', t); assert n == 2, (p, n); st['lab'].append(own)
        # 2. the heading
        if H_OLD in t:
            t = t.replace(H_OLD, H_NEW); st['h1'].append(own)
            t = re.sub(r'(<span class="ct-stu"[^>]*>)([A-Za-z]+)<br>([A-Za-z]+)</span>', r'\1\2 <br>\3 </span>', t)
        # 5. Mumbai studio
        k = '{"@type":"LocalBusiness","@id":"' + SITE + '/contact/#mumbai",'
        if k in t:
            add = '"geo":{"@type":"GeoCoordinates","latitude":%s,"longitude":%s},"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":%s,"opens":"10:00","closes":"19:00"}],"hasMap":"%s",' % (
                GEO['lat'], GEO['lng'], json.dumps(DAYS, separators=(',', ':')), GEO['map'])
            t = sub(t, k, k + add, 1, p); st['geo'].append(own)
        for s in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S): json.loads(s)
        wr(p, t)
assert 'Mumbai <br>Studio </span>' + H_NEW in rd('contact/index.html')

# the Design Snippet page (standalone)
t = rd('design-snippet/index.html')
t = sub(t, '<title>Design Snippet: careers at Collaborative Architecture, Mumbai and Riyadh</title>', '<title>Design Snippet: careers at Collaborative Architecture</title>', 1, 'snippet title')
DS = 'The Design Snippet: design challenges in Rhino and Grasshopper, in three levels, for interns, junior architects and advanced applicants in Mumbai or Riyadh.'
assert len(DS) <= 160
t, n = re.subn(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DS}">', t); assert n == 1
wr('design-snippet/index.html', t)

# --- sitemap, llms, Bing, version ----------------------------------------------------------------------------------------
sm = rd('sitemap.xml')
for k in LAB:
    sm, n = re.subn(r'<url><loc>' + re.escape(f'{SITE}/lab/{k}/') + r'</loc>.*?</url>\n?', '', sm, flags=re.S); assert n == 1, k
changed = sorted(set(st['titles']) | {'/contact/', '/lab/', '/design-snippet/'})
for own in changed:
    sm, n = re.subn(r'(<url><loc>' + re.escape(SITE + own) + r'</loc><lastmod>)[0-9-]+(</lastmod>)', r'\g<1>' + TODAY + r'\2', sm); assert n <= 1
wr('sitemap.xml', sm)
for f in ['llms.txt', 'llms-full.txt']:
    t = rd(f); lines = t.split('\n'); i = next(i for i, l in enumerate(lines) if l.startswith('> '))
    lines.insert(i + 1, ''); lines.insert(i + 2, 'Last updated: 25 November 2026'); wr(f, '\n'.join(lines))
shutil.copyfile(bing, os.path.join(up, 'BingSiteAuth.xml'))
wr('version.txt', 'Collaborative Architecture website\nversion 2026-11-25-seo4\npatch on top of 2026-11-23-snippet1 (includes 2026-11-24-seo3 and 2026-11-24-bing1)\n')
open(os.path.join(out, 'DELETE.txt'), 'w', newline='\r\n').write('\n'.join(
    ['assets/site-1.31acb541c6c9.css', 'assets/load.dc86221f3116.js', 'assets/site-7.cc372844f761.js', 'assets/site-3.deb25b75ebec.js',
     'assets/site-6.5fec9e53747d.js', 'assets/data-ca-data-j.377e631666ac.js', 'img/share/design-snippet.jpg', LOAD0, S30, S60, S70, D0]) + '\n')
old = set(open(os.path.join(os.path.dirname(src.rstrip('/')), 'indexnow-urls.txt')).read().split())
urls = sorted(old | {SITE + o for o in changed} | {SITE + o for o in st['skip']} | {SITE + '/llms.txt', SITE + '/sitemap.xml'})
urls = [u for u in urls if not any(u.endswith(f'/lab/{k}/') for k in LAB)]
open(os.path.join(out, 'indexnow-urls.txt'), 'w', newline='\n').write('\n'.join(urls) + '\n')
print('assets', LOAD1, S31, S61, S71, D1)
print(len(st['titles']), 'titles'); [print('  ', o, '|', a, '->', b, len(b)) for o, (a, b) in sorted(st['titles'].items())]
print('skip', st['skip']); print('lab', st['lab']); print('heading', st['h1']); print('studio data', st['geo']); print(len(urls), 'indexnow urls')
