#!/usr/bin/env python3
"""Live patch 2026-11-27-forms1, on top of 2026-11-26-gsc1 (which carries ahrefs1, sectors1, seo4, seo3 and bing1), so the host
uploads one package.

  1. Career on the Contact page (Mujib, 27 November 2026, draft approved the same day): instead of the form, the careers note of
     the Studio page (with "email a portfolio" for "select Career in the contact form and submit a portfolio") with its
     Design-Snippet link, then studio@collaborativearchitecture.com as a mailto link. The other inquiry types keep the form.
     Built at run time when Career is chosen, so no page's HTML changes: only site-7 (script) and site-1 (style), and the
     script loader, get new names.
  2. The forms' email (patch mail1): api/lib.php, api/subscribe.php, api/mail-check.php, api/mail.php, api/.htaccess.
  3. gsc1's server files (.htaccess, _headers, _redirects, nginx.conf), with nginx.conf's api lines for mail1.

Every page is rendered with the old and the new scripts; the patch asserts that no page's render changes.

Usage: make_patch_forms1.py <ahrefs1 full site> <gsc1 package dir> <public folder> <mail1 api folder> <out dir>"""
import sys, os, re, json, shutil, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sectors1'))
from render import render, normalize, sizes_of
base, prev, pub, api, out = sys.argv[1:6]
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
OLD = {k: asset(k + '.', '.js') for k in ['site-7', 'load']}; OLD['site-1'] = asset('site-1.', '.css'); NEW = {}

# 1. Career on the Contact page
s7 = rd(os.path.join(full, OLD['site-7']))
s7 = sub(s7, 's=()=>{const r=C.inq.find(d=>d.v===e.value);F("[data-extra]").forEach(d=>d.hidden=!r||r.extra!==d.dataset.extra),t.dataset.team=r&&r.team||""}',
         's=()=>{const r=C.inq.find(d=>d.v===e.value);F("[data-extra]").forEach(d=>d.hidden=!r||r.extra!==d.dataset.extra),t.dataset.team=r&&r.team||"",caCr(e,r)}', 1, 'contact upd')
CR = ('function caCr(e,r){const f=e.closest("form"),w=e.closest(".fld"),on=!!r&&r.v==="Career";if(!f||!w)return;w.classList.toggle("fld-t",on);'
      'let c=f.querySelector("[data-cr]");if(on&&!c){c=document.createElement("div"),c.className="fld full cr-p",c.setAttribute("data-cr",""),'
      'c.innerHTML=`<p>${Qt(C.careers).replace("select “Career” in the contact form and submit a portfolio","email a portfolio").replace("<b><i>Design-Snippet</i></b>",\'<a class="chl" href="/design-snippet/" target="_self"><b><i>Design-Snippet</i></b></a>\')}</p><p class="cr-m"><a href="mailto:${p(r.to)}">${p(r.to)}</a></p>`,w.after(c)}'
      'c&&(c.hidden=!on),f.classList.toggle("cr",on)}')
assert 'function caCr(' not in s7 and 'Qt=e=>p(e)' in s7
s7 = sub(s7, 'function vr(){', CR + 'function vr(){', 1, 'contact init')
NEW['site-7'] = f'assets/site-7.{h12(s7)}.js'; wr(os.path.join(full, NEW['site-7']), s7)
CSS = ('/* 27 November 2026: Career on the Contact page */\n.frm.cr>:not(.fld-t):not([data-cr]){display:none!important}.frm.cr>.fld-t{grid-column:1/-1}'
       '.cr-p p{margin:0}.cr-p .cr-m{margin-top:22px;font:600 clamp(19px,1.6vw,24px)/1.3 var(--body)}'
       '.cr-p .cr-m a{color:var(--ink);text-decoration:underline;text-decoration-thickness:1.5px;text-underline-offset:5px;overflow-wrap:anywhere}'
       '.cr-p .cr-m a:hover{color:var(--crimson)}\n')
css = rd(os.path.join(full, OLD['site-1'])); assert '.cr-p' not in css
css = css + CSS if css.endswith('\n') else css + '\n' + CSS
NEW['site-1'] = f'assets/site-1.{h12(css)}.css'; wr(os.path.join(full, NEW['site-1']), css)
load = sub(rd(os.path.join(full, OLD['load'])), '"/' + OLD['site-7'] + '"', '"/' + NEW['site-7'] + '"', 1, 'load')
NEW['load'] = f'assets/load.{h12(load)}.js'; wr(os.path.join(full, NEW['load']), load)
for k in OLD: os.remove(os.path.join(full, OLD[k]))
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
old, e1 = render(base, PAGES, [pub], feeds=True)
new, e2 = render(full, PAGES, [pub], feeds=True)
assert not e1 and not e2, (e1[:3], e2[:3])
So, Sn = sizes_of(base), sizes_of(full)
def as_new(t):
    for k in OLD: t = t.replace('/' + OLD[k], '/' + NEW[k])
    return t
changed = [p for p in PAGES if as_new(normalize(old[p], So)) != normalize(new[p], Sn)]
if changed:   # a page can differ by timing alone: render those once more, both ways
    old2, _ = render(base, changed, [pub]); new2, _ = render(full, changed, [pub])
    changed = [p for p in changed if as_new(normalize(old2[p], So)) != normalize(new2[p], Sn)]
assert not changed, ('pages whose render changed', changed)
FO, FN = old['__feeds__'], new['__feeds__']
assert all(FO[k] == FN[k] for k in ['md', 'files']), 'search files changed'
wr(os.path.join(full, 'version.txt'), 'Collaborative Architecture website\nversion 2026-11-27-forms1\n'
   'patch on top of 2026-11-23-snippet1 (includes 2026-11-27-mail1, 2026-11-26-gsc1, 2026-11-26-ahrefs1, 2026-11-26-sectors1, '
   '2026-11-25-seo4, 2026-11-24-seo3 and 2026-11-24-bing1)\n')

# 2. the upload folder: gsc1's, with this patch's pages and assets, the forms' api files, and gsc1's server files
pd = os.path.join(out, 'patch'); up = os.path.join(pd, 'upload'); shutil.copytree(os.path.join(prev, 'upload'), up)
for k in OLD:
    if os.path.exists(os.path.join(up, OLD[k])): os.remove(os.path.join(up, OLD[k]))
for d, _, fs in os.walk(full):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), full).replace(os.sep, '/')
        if os.path.exists(os.path.join(up, rel)) or rel in [NEW[k] for k in NEW]:
            os.makedirs(os.path.dirname(os.path.join(up, rel)), exist_ok=True); shutil.copyfile(os.path.join(full, rel), os.path.join(up, rel))
os.makedirs(os.path.join(up, 'api'), exist_ok=True)
for f in ['lib.php', 'subscribe.php', 'mail-check.php', 'mail.php']: shutil.copyfile(os.path.join(api, f), os.path.join(up, 'api', f))
shutil.copyfile(os.path.join(api, 'htaccess.txt'), os.path.join(up, 'api', '.htaccess'))
for f in ['.htaccess', '_headers', '_redirects']: assert os.path.isfile(os.path.join(up, f)), f
ng = rd(os.path.join(prev, 'nginx.conf'))
ng = sub(ng, 'location ~ ^/api/(lib|config|config\\.sample|mailchimp|mailchimp\\.sample|security|security\\.sample)\\.php$ { deny all; }',
         'location ~ ^/api/(lib|config|config\\.sample|mailchimp|mailchimp\\.sample|security|security\\.sample|mail|mail\\.sample)\\.php$ { deny all; }', 1, 'nginx deny')
ng = sub(ng, 'location ~ ^/api/(contact|subscribe|vitals)\\.php$ {', 'location ~ ^/api/(contact|subscribe|vitals|mail-check)\\.php$ {', 1, 'nginx php')
wr(os.path.join(pd, 'nginx.conf'), ng)
# nothing in the upload folder that the full site would not serve, apart from the server and api files
for d, _, fs in os.walk(up):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), up).replace(os.sep, '/')
        if rel.startswith('api/') or rel in ('.htaccess', '_headers', '_redirects'): continue
        assert os.path.isfile(os.path.join(full, rel)), ('stale file in upload', rel)
dele = [l.strip() for l in open(os.path.join(prev, 'DELETE.txt')) if l.strip()] + [OLD['site-1'], OLD['site-7'], OLD['load']]
assert not any(os.path.exists(os.path.join(full, x)) for x in dele)
open(os.path.join(pd, 'DELETE.txt'), 'w', newline='\r\n').write('\n'.join(dele) + '\n')
shutil.copyfile(os.path.join(prev, 'indexnow-urls.txt'), os.path.join(pd, 'indexnow-urls.txt'))
n = sum(len(fs) for _, _, fs in os.walk(up))
json.dump({'old': OLD, 'new': NEW, 'pages_compared': len(PAGES)}, open(os.path.join(out, 'forms1.json'), 'w'), indent=1)
print(n, 'files in the upload folder; assets', OLD, '->', NEW)
