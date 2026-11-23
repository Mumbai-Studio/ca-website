#!/usr/bin/env python3
"""Live patch 2026-11-23-snippet3, on top of 2026-11-23-snippet1 (replaces snippet2, never uploaded):
  1. the Design Snippet in three levels (page, 12-page PDF, share picture);
  2. Related projects: no card for a project without a picture;
  3. the opening logo: the line under the T draws down as it did before logo1, on desktop and on phones;
     the site's scripts run once the line has finished, so nothing holds the animation back.
Usage: make_patch_snippet3.py <live text copy (snippet1)> <final page folder> <out dir>"""
import sys, os, re, hashlib, shutil
src, fin, out = sys.argv[1:4]
up = os.path.join(out, 'upload'); shutil.rmtree(out, ignore_errors=True); os.makedirs(os.path.join(up, 'assets'))
rd = lambda p: open(os.path.join(src, p), encoding='utf-8', newline='').read()
def wr(p, t):
    q = os.path.join(up, p); os.makedirs(os.path.dirname(q), exist_ok=True); open(q, 'w', encoding='utf-8', newline='').write(t)
def cp(a, p):
    q = os.path.join(up, p); os.makedirs(os.path.dirname(q), exist_ok=True); shutil.copyfile(a, q)
h12 = lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest()[:12]
def sub(t, a, b, n=1, what=''):
    c = t.count(a)
    if c != n: raise SystemExit(f'{what}: expected {n} of {a[:70]!r}, found {c}')
    return t.replace(a, b)

CSS0, LOAD0, S70 = 'assets/site-1.31acb541c6c9.css', 'assets/load.dc86221f3116.js', 'assets/site-7.cc372844f761.js'

# 3a. The line under the T draws down by growing its height, exactly as before patch logo1 (Mujib, 23 November 2026: since logo1 the
#     line stood still on desktop too; logo1 drew it by scaling a full-length line up from zero, which some graphics cards show only
#     once it has finished). The device's reduce-motion setting no longer stops the logo (Mujib, 5 November 2026: that setting stops
#     only the slow zoom, the parallax and smooth scrolling); with it on, a phone showed the logo standing still.
LINE_NEW = '.pl-s{position:absolute;left:65.8%;top:96%;width:max(2px,.45%);height:60vh;background:#fff;transform:scaleY(0);transform-origin:50% 0;will-change:transform}'
LINE_OLD = '.pl-s{position:absolute;left:65.8%;top:96%;width:max(2px,.45%);height:0;background:#fff}'
KF_NEW, KF_OLD = '@keyframes pls{to{transform:scaleY(1)}}', '@keyframes pls{to{height:60vh}}'
RM_FIRST = '@media (prefers-reduced-motion:reduce){html.pl-boot #pl#pl#pl .pl-in img{animation:none;opacity:1;transform:none}#pl#pl#pl .pl-s{animation:none;transform:none}.pl,.pl-in{transition:none}}'
RM_CSS = ['@media(prefers-reduced-motion:reduce){html.pl-boot #pl#pl#pl .pl-in img{animation:none;opacity:1;transform:none}#pl#pl#pl .pl-s{animation:none;transform:none}}',
          '@media(prefers-reduced-motion:reduce){.pl,.pl-in{transition:none}}']
css = rd(CSS0)
for r in RM_CSS: css = sub(css, r, '', 1, 'site-1 reduce-motion')
css = sub(css, LINE_NEW, LINE_OLD, 1, 'site-1 line'); css = sub(css, KF_NEW, KF_OLD, 1, 'site-1 keyframes'); css = sub(css, '.pl.rm .pl-s{transform:none}', '', 1, 'site-1 rm line')
assert css.count('scaleY') == 3 and LINE_OLD in css and KF_OLD in css
CSS1 = f'assets/site-1.{h12(css)}.css'; wr(CSS1, css)
def first(t, p):
    m = re.search(r'<style id="pl-first">.*?</style>', t, re.S); assert m, p
    b = sub(m.group(0), RM_FIRST, '', 1, p + ' pl-first reduce-motion')
    b = sub(b, LINE_NEW, LINE_OLD, 1, p + ' pl-first line'); b = sub(b, KF_NEW, KF_OLD, 1, p + ' pl-first keyframes')
    assert 'scaleY' not in b and 'will-change' not in b, p
    return t[:m.start()] + b + t[m.end():]

# 2. Related projects: a project with no page and no picture (Infold House, Linked House, Topography) drew a blank box; it is left out.
# 3b. The logo's hold: the site's scripts now arrive after the line has been drawn, so the shortest hold after them is 0.25 s (was 0.6 s);
#     on a desktop the logo still leaves at 3.25 s, on a slow phone it no longer waits an extra half second.
s7 = sub(rd(S70), 'return t?`<div class="card off">', 'return t&&t.img?`<div class="card off">', 1, 'site-7 stub card')
s7 = sub(s7, 'Math.max(600,3250-(performance.now()-a))', 'Math.max(250,3250-(performance.now()-a))', 1, 'site-7 hold')
S71 = f'assets/site-7.{h12(s7)}.js'; wr(S71, s7)

# 3c. On the first page of a visit, while the logo screen is up, the site's scripts (about 900 KB) are downloaded at the usual moment
#     (preload) but run only once the line has finished drawing (2.35 s after the logo picture arrives; 3 s at the latest if it never
#     does), so neither a busy phone nor a desktop can hold the animation back. Later pages of the visit, and a refresh, run them at once.
load = sub(rd(LOAD0), '/' + S70, '/' + S71, 1, 'load site-7')
OLD = 'window.requestAnimationFrame&&requestAnimationFrame(function(){setTimeout(i,0)}),setTimeout(i,400)})();'
NEW = ('var h=document.documentElement,b=h.classList.contains("pl-boot"),k=!b,g=!1,q=!1;'
       'function u(){if(!q){q=!0;for(var e=0;e<a.length;e++){var l=document.createElement("link");l.rel="preload",l.as="script",l.href=a[e],document.head.appendChild(l)}}}'
       'function s(){k?i():u()}'
       'function o(){if(!g){g=!0;var t=window.CA_PL_T,w=typeof t=="number"?Math.max(0,t+2350-performance.now()):0;setTimeout(function(){k=!0,i()},w)}}'
       'if(b){addEventListener("ca-pl-ready",o);setTimeout(o,3000);var c=function(){var p=document.getElementById("pl");p&&p.classList.contains("ready")&&o()};c();document.addEventListener("DOMContentLoaded",c)}'
       'window.requestAnimationFrame&&requestAnimationFrame(function(){setTimeout(s,0)}),setTimeout(s,400)})();')
load = sub(load, OLD, NEW, 1, 'load defer')
LOAD1 = f'assets/load.{h12(load)}.js'; wr(LOAD1, load)
# every page: the new file names and the logo's first rules; the two project pages lose their blank cards
BLANK = re.compile(r'<div class="card off"><div class="im none"><span>[^<]*</span></div><b>[^<]*</b><span>[^<]*</span>(?:<span class="soon mono">[^<]*</span>)?</div>')
n, gone = 0, {}
for d, _, fs in os.walk(src):
    if os.path.relpath(d, src).split(os.sep)[0] in ('img', 'vid', 'press', 'fonts', 'api', 'design-snippet'): continue
    for f in fs:
        if not f.endswith('.html'): continue
        p = os.path.relpath(os.path.join(d, f), src); t = rd(p)
        if LOAD0 not in t: continue
        t = sub(t, '/' + CSS0, '/' + CSS1, 1, p); t = sub(t, '/' + LOAD0, '/' + LOAD1, 1, p); t = first(t, p)
        k = len(BLANK.findall(t))
        if k: t = BLANK.sub('', t); gone[p] = k
        assert 'class="im none"' not in t, p
        wr(p, t); n += 1
assert gone == {os.path.join('work', 'house-of-cantilevers', 'index.html'): 2, os.path.join('work', 'inverted-topography', 'index.html'): 1}, gone

# 1. the Design Snippet page, its PDF and the new share picture (a new name: pictures are cached for 30 days)
for p in ['design-snippet/index.html', 'design-snippet/Collaborative-Architecture-Design-Snippet.pdf', 'img/share/design-snippet-levels.jpg']:
    cp(os.path.join(fin, p), p)
sm = rd('sitemap.xml')
sm = sub(sm, '<url><loc>https://collaborativearchitecture.com/design-snippet/</loc><lastmod>2026-11-23</lastmod><priority>0.5</priority>'
             '<image:image><image:loc>https://collaborativearchitecture.com/img/share/design-snippet.jpg</image:loc></image:image></url>',
         '<url><loc>https://collaborativearchitecture.com/design-snippet/</loc><lastmod>2026-11-23</lastmod><priority>0.5</priority>'
         '<image:image><image:loc>https://collaborativearchitecture.com/img/share/design-snippet-levels.jpg</image:loc></image:image></url>', 1, 'sitemap')
wr('sitemap.xml', sm)
ll = sub(rd('llms.txt'), "the studio's design challenge for career and internship applicants (two Rhino and Grasshopper snippets, The Kit and The Field)",
         "the studio's design challenge for career and internship applicants, in three levels: Interns (The Rods, The Screen), "
         "Junior Architects (The Kit, The Field) and Advanced (The Canopy, The Facade)", 1, 'llms')
wr('llms.txt', ll)
wr('version.txt', 'Collaborative Architecture website\nversion 2026-11-23-snippet3\npatch on top of 2026-11-23-snippet1 (replaces snippet2)\n')
open(os.path.join(out, 'DELETE.txt'), 'w', newline='\r\n').write('\n'.join([CSS0, LOAD0, S70, 'img/share/design-snippet.jpg']) + '\n')
print(n, 'pages;', CSS1, LOAD1, S71, '; blank cards removed:', gone)
