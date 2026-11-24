#!/usr/bin/env python3
"""Live patch 2026-11-24-seo3, on top of 2026-11-23-snippet1. It carries snippet3 (never uploaded) and adds the fixes from the
Semrush site audit of 24 November 2026 (project 32110787, 153 pages crawled). No visible text changes.

  1. hreflang (9 errors): pages whose canonical is another page (the list and map views of Work, the Media Hub) no longer carry
     hreflang links, in the static pages and in the script that rewrites them on each page change.
  2. Broken outbound links (39 of 40 warnings):
     - the WhatsApp share link of each project starts out as the project page's own address and takes its wa.me address only
       when pressed or focused (wa.me refuses link checkers, so they reported it broken on 30 pages);
     - five dead press and partner links point to their archived copies (Wayback Machine), or to the partner's current address;
     - the Notions of India submission page is gone and has no archive: the citation stays, as plain text.
  3. Orphaned pages (8 notices): the Gulf city pages (Riyadh, Jeddah, Dammam and Al Khobar, Makkah, Madinah, AlUla and NEOM,
     Abu Dhabi, Sharjah) had no link from any page. The city names already printed in the "Where we work" lists of the Saudi
     Arabia, UAE and Middle East pages now link to them, drawn exactly like the plain text around them.
  4. Sitemap dates of the pages that changed.

Usage: make_patch_seo3.py <live copy with snippet3 applied (t4)> <snippet3 upload folder> <out dir>"""
import sys, os, re, hashlib, shutil, json
src, s3up, out = sys.argv[1:4]
up = os.path.join(out, 'upload'); shutil.rmtree(out, ignore_errors=True); os.makedirs(os.path.join(up, 'assets'))
SITE = 'https://collaborativearchitecture.com'
rd = lambda p: open(os.path.join(src, p), encoding='utf-8', newline='').read()
def wr(p, t):
    q = os.path.join(up, p); os.makedirs(os.path.dirname(q), exist_ok=True); open(q, 'w', encoding='utf-8', newline='').write(t)
h12 = lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest()[:12]
def sub(t, a, b, n=1, what=''):
    c = t.count(a)
    if c != n: raise SystemExit(f'{what}: expected {n} of {a[:80]!r}, found {c}')
    return t.replace(a, b)

CSS0, LOAD0 = 'assets/site-1.45d03c4c3bb7.css', 'assets/load.d227ccda11a7.js'
S30, S60, S70, D0 = 'assets/site-3.deb25b75ebec.js', 'assets/site-6.5fec9e53747d.js', 'assets/site-7.c6f1798fe4f1.js', 'assets/data-ca-data-j.377e631666ac.js'

# --- 2. dead outbound links -----------------------------------------------------------------------------------------------
DEAD = {
    'http://architypereview.com/lalita-tharani-mujib-ahmed/': 'https://web.archive.org/web/20230924010334/https://architypereview.com/lalita-tharani-mujib-ahmed/',
    'http://inditerrain.indiaartndesign.com/2014/04/stacked-tectonics-inspiring-change.html': 'https://web.archive.org/web/20250319195706/http://inditerrain.indiaartndesign.com/2014/04/stacked-tectonics-inspiring-change.html',
    'http://www.designworxasia.com/collaborative-architecture-invited-by-cooper-hewitt-smithsonian-museum/': 'https://web.archive.org/web/20211208212238/https://www.designworxasia.com/collaborative-architecture-invited-by-cooper-hewitt-smithsonian-museum/',
    'https://www.ifj.co.in/ifj-likes/mumbai-firm-designs-for-peace/': 'https://web.archive.org/web/20220122203620/https://www.ifj.co.in/ifj-likes/mumbai-firm-designs-for-peace/',
    'https://www.jmayerh.de/': 'https://jmayerh.de/',
}
NOI = 'https://www.notionsofindia.com/exhibition/submissions/national-unity-pavillion.html'
NOI_T = 'Notions of India, competition submission'
def fix_links(t, kind):
    for a, b in DEAD.items(): t = t.replace(a, b)
    if NOI in t:
        if kind == 'html':
            t = re.sub(r'<a class="crow" href="' + re.escape(NOI) + r'"[^>]*><span class="mono">([^<]*)</span><span>([^<]*)</span><span aria-hidden="true"><i class="ne" aria-hidden="true"></i></span></a>',
                       r'<div class="crow"><span class="mono">\1</span><span>\2</span><span></span></div>', t)
            t = t.replace('"url":"' + NOI + '",', '').replace(',"url":"' + NOI + '"', '')
        elif kind == 'js':
            t = t.replace('\\"u\\":\\"' + NOI + '\\"', '\\"u\\":\\"\\"').replace('"u":"' + NOI + '"', '"u":""')
        elif kind == 'llms':
            t = t.replace('[' + NOI_T + '](' + NOI + ')', NOI_T)
            t = t.replace(NOI_T + ' (' + NOI + ')', NOI_T)
        elif kind == 'json':
            t = re.sub(r',\s*"url": "' + re.escape(NOI) + '"', '', t)
        else:
            t = t.replace(' (' + NOI + ')', '')
        if NOI in t: raise SystemExit(f'Notions of India link left in a {kind} file')
    return t

# --- 3. Gulf city names link to their pages ------------------------------------------------------------------------------
QC = {'Riyadh': 'riyadh', 'Jeddah': 'jeddah', 'Makkah': 'makkah', 'Madinah': 'madinah', 'Dammam': 'dammam-and-al-khobar',
      'Al Khobar': 'dammam-and-al-khobar', 'AlUla': 'alula-and-neom', 'NEOM': 'alula-and-neom', 'Abu Dhabi': 'abu-dhabi', 'Sharjah': 'sharjah'}
for k in set(QC.values()): assert os.path.exists(os.path.join(src, 'work', 'in', k, 'index.html')), k
def link_cities(t):
    def dl(m):
        def dd(n):
            parts = n.group(1).split(', ')
            parts = [f'<a class="qc" href="/work/in/{QC[x]}/">{x}</a>' if x in QC else x for x in parts]
            return '<dd>' + ', '.join(parts) + '</dd>'
        return re.sub(r'<dd>(.*?)</dd>', dd, m.group(0))
    return re.sub(r'<dl class="cities">.*?</dl>', dl, t, flags=re.S)

# --- the scripts ----------------------------------------------------------------------------------------------------------
s3 = fix_links(rd(S30), 'js'); S31 = f'assets/site-3.{h12(s3)}.js'; wr(S31, s3)
dj = fix_links(rd(D0), 'js'); D1 = f'assets/data-ca-data-j.{h12(dj)}.js'; wr(D1, dj)
s6 = sub(rd(S60), '/noindex/.test(t.robots)||[["en",t.canonical],["x-default",t.canonical]].forEach(',
         '/noindex/.test(t.robots)||document.documentElement.dataset.routing==="path"&&new URL(t.canonical,location.href).pathname!==location.pathname||[["en",t.canonical],["x-default",t.canonical]].forEach(', 1, 'site-6 hreflang')
S61 = f'assets/site-6.{h12(s6)}.js'; wr(S61, s6)
s7 = rd(S70)
s7 = sub(s7, '<a href="https://wa.me/?text=${encodeURIComponent(t.title+" by Collaborative Architecture "+Qe+"?utm_source=whatsapp&utm_medium=social&utm_campaign=share")}" target="_blank"',
         '<a href="${Qe}" data-wa="https://wa.me/?text=${encodeURIComponent(t.title+" by Collaborative Architecture "+Qe+"?utm_source=whatsapp&utm_medium=social&utm_campaign=share")}" target="_blank"', 1, 'site-7 whatsapp')
s7 = sub(s7, 'kr=e=>e.split(", ").map(t=>{const a=O.placeFor(t+", ");return a?`<a href="#in-${a.k}">${p(t)}</a>`:p(t)}).join(", ")',
         'kr=e=>e.split(", ").map(t=>{const a=O.placeFor(t+", ");if(a)return`<a href="#in-${a.k}">${p(t)}</a>`;const g=' + json.dumps(QC, separators=(',', ':')) +
         '[t];return g&&O.hub(g)?`<a class="qc" href="#in-${g}">${p(t)}</a>`:p(t)}).join(", ")', 1, 'site-7 cities')
s7 = s7.rstrip() + '\n;["pointerdown","focusin","click","auxclick","contextmenu","keydown"].forEach(v=>document.addEventListener(v,e=>{const a=e.target&&e.target.closest&&e.target.closest("a[data-wa]");a&&a.getAttribute("href")!==a.dataset.wa&&a.setAttribute("href",a.dataset.wa)},!0));\n'
S71 = f'assets/site-7.{h12(s7)}.js'; wr(S71, s7)
css = rd(CSS0) + '.cities dd a.qc,.cities dd a.qc:hover{color:inherit;text-decoration:none;cursor:auto}'
CSS1 = f'assets/site-1.{h12(css)}.css'; wr(CSS1, css)
load = rd(LOAD0)
for a, b in [(S30, S31), (S60, S61), (S70, S71), (D0, D1)]: load = sub(load, '/' + a, '/' + b, 1, 'load ' + a)
LOAD1 = f'assets/load.{h12(load)}.js'; wr(LOAD1, load)

# --- every page and text file ---------------------------------------------------------------------------------------------
SKIP = ('img', 'vid', 'press', 'fonts', 'api', 'assets')
changed_pages, stats = set(), {'hreflang': [], 'whatsapp': 0, 'cities': [], 'dead': set()}
for d, _, fs in os.walk(src):
    rel = os.path.relpath(d, src)
    if rel.split(os.sep)[0] in SKIP: continue
    for f in fs:
        p = os.path.normpath(os.path.join(rel, f))
        if not re.search(r'\.(html|md|txt|xml|json)$', f): continue
        t0 = t = rd(p)
        if f.endswith('.html'):
            t = fix_links(t, 'html')
            if LOAD0 in t:   # a page of the site (the standalone Design Snippet page has none of these)
                t = sub(t, '/' + CSS0, '/' + CSS1, 1, p); t = sub(t, '/' + LOAD0, '/' + LOAD1, 1, p)
                m = re.search(r'<link rel="canonical" href="([^"]+)">', t)
                own = SITE + '/' + ('' if rel == '.' else rel.replace(os.sep, '/') + '/')
                if m and m.group(1) != own and 'data-ca-hl="1"' in t:
                    t = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+" data-ca-hl="1">\n?', '', t); stats['hreflang'].append(p)
                n0 = t.count('href="https://wa.me/?text=')
                if n0:
                    assert m, p
                    t = t.replace('<a href="https://wa.me/?text=', f'<a href="{m.group(1)}" data-wa="https://wa.me/?text=')
                    stats['whatsapp'] += n0
                t2 = link_cities(t)
                if t2 != t: stats['cities'].append(p); t = t2
        elif f.endswith('.json'): t = fix_links(t, 'json')
        elif f in ('llms.txt', 'llms-full.txt'): t = fix_links(t, 'llms')
        else: t = fix_links(t, 'md')
        if t != t0:
            if any(a in t0 for a in DEAD) or NOI in t0: stats['dead'].add(p)
            wr(p, t); changed_pages.add(p)
for p in changed_pages:
    t = open(os.path.join(up, p), encoding='utf-8').read()
    bare = re.sub(r'https://web\.archive\.org/web/\d+/\S+?(?=[)"\s<\\]|$)', '', t)
    assert 'href="https://wa.me' not in t and NOI not in t and not any(a in bare for a in DEAD), p

# --- 4. sitemap dates of the pages whose content changed ----------------------------------------------------------------
sm = rd('sitemap.xml'); content_pages = sorted({os.path.dirname(p) for p in stats['dead'] | set(stats['cities']) if p.endswith('index.html')})
for d in content_pages:
    loc = SITE + '/' + (d.replace(os.sep, '/') + '/' if d else '')
    sm, n = re.subn(r'(<url><loc>' + re.escape(loc) + r'</loc><lastmod>)[0-9-]+(</lastmod>)', r'\g<1>2026-11-24\2', sm)
    assert n <= 1, loc
wr('sitemap.xml', fix_links(sm, 'xml'))

# --- carried from snippet3: the Design Snippet page, its PDF and share picture ------------------------------------------------
for p in ['design-snippet/index.html', 'design-snippet/Collaborative-Architecture-Design-Snippet.pdf', 'img/share/design-snippet-levels.jpg']:
    if not os.path.exists(os.path.join(up, p)):
        os.makedirs(os.path.dirname(os.path.join(up, p)), exist_ok=True); shutil.copyfile(os.path.join(s3up, p), os.path.join(up, p))
wr('version.txt', 'Collaborative Architecture website\nversion 2026-11-24-seo3\npatch on top of 2026-11-23-snippet1 (includes 2026-11-23-snippet3)\n')

open(os.path.join(out, 'DELETE.txt'), 'w', newline='\r\n').write('\n'.join([
    'assets/site-1.31acb541c6c9.css', 'assets/load.dc86221f3116.js', 'assets/site-7.cc372844f761.js',
    S30, S60, D0, 'img/share/design-snippet.jpg']) + '\n')
urls = sorted({SITE + '/' + (os.path.dirname(p).replace(os.sep, '/') + '/' if os.path.dirname(p) else '') for p in changed_pages if p.endswith('index.html')}
              | {f'{SITE}/work/in/{k}/' for k in set(QC.values())} | {SITE + '/llms.txt', SITE + '/sitemap.xml'})
open(os.path.join(out, 'indexnow-urls.txt'), 'w', newline='\n').write('\n'.join(urls) + '\n')
print('assets:', CSS1, LOAD1, S31, S61, S71, D1)
print('hreflang removed on', stats['hreflang']); print('whatsapp links', stats['whatsapp']); print('city links on', stats['cities'])
print('dead links fixed in', len(stats['dead']), 'files;', len(changed_pages), 'text files changed; sitemap dates', content_pages)
