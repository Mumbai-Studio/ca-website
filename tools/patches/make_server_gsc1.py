#!/usr/bin/env python3
"""Patch gsc1 (26 November 2026): Search Console Pages report. Adds rules to the LIVE server files (the 23 Nov seo2 copies,
which match what the server answers today) and changes nothing else in them.
usage: make_server_gsc1.py <folder with .htaccess, _headers, _redirects, nginx.conf>   (edits them in place)"""
import sys, os, re

D = sys.argv[1]
O = 'https://collaborativearchitecture.com'
NOTE = '# 26 November 2026 (Search Console, Pages report): old addresses Google still asks for'
PDFS = [  # the old WordPress copies of four press features, and the same features on this site
    ('wp-content/uploads/2020/11/2020-AUG-MGS-ARCHITECTURE.pdf', 'press/features/2020-mgs-architecture-designing-peace-cooper-hewitt.pdf'),
    ('wp-content/uploads/2020/11/2019-FEB-ARCHITECTURE-DESIGN.pdf', 'press/features/2019-02-architecture-and-design-global-dynamics.pdf'),
    ('wp-content/uploads/2020/11/3.-IO-July-16_Lalita-Mujib.pdf', 'press/features/2016-07-inside-outside-interview-with-the-principals.pdf'),
    ('wp-content/uploads/2020/12/2015-JUL-FX.pdf', 'press/features/2015-07-fx-reflected-topography.pdf'),
]
FEEDS = ['logs', 'news', 'press', 'projects']
esc = lambda s: re.sub(r'([.*+?^${}()|\[\]\\])', r'\\\1', s)

def rd(n): return open(os.path.join(D, n), encoding='utf-8').read()
def wr(n, t): open(os.path.join(D, n), 'w', encoding='utf-8', newline='\n').write(t)
def once(t, old, new, name):
    assert t.count(old) == 1, (name, old[:60], t.count(old)); return t.replace(old, new)

# ---- .htaccess (Apache, LiteSpeed) ----
h = rd('.htaccess'); assert 'gsc1' not in h and 'CA_FEED' not in h
anchor = '# old addresses of the WordPress site (server/redirects.txt)\n'
block = [NOTE + ' (patch gsc1)',
         '# feed links that once read "feeds/..." without the leading slash, so /news/press/ made /news/press/feeds/...',
         f'RewriteRule ^.+/feeds/({"|".join(FEEDS)})\\.xml$ {O}/feeds/$1.xml [R=301,L]',
         f'RewriteRule ^en/?$ {O}/ [R=301,L]',
         f'RewriteRule ^portfolio/?$ {O}/work/ [R=301,L]']
block += [f'RewriteRule ^{esc(a)}$ {O}/{b} [R=301,L]' for a, b in PDFS]
block += ['# the old WordPress search: /search/... is gone, and /?s=... goes to the home page without the query',
          'RewriteRule ^search/ - [G,L]',
          'RewriteCond %{QUERY_STRING} (^|&)s=',
          f'RewriteRule ^$ {O}/? [R=301,L]', '']
h = once(h, anchor, anchor + '\n'.join(block) + '\n', '.htaccess rules')
md = 'RewriteRule ^(.*/)?index\\.md$ - [E=CA_MD_PAGE:/$1]\n'
h = once(h, md, md + '# 26 November 2026 (Search Console, patch gsc1): the feeds are for feed readers; search engines may read them, not list them\n'
         'RewriteRule ^feeds/ - [E=CA_FEED:1]\n', '.htaccess feed env')
lk = '  Header set Link "<https://collaborativearchitecture.com%{CA_MD_PAGE}e>; rel=\\"canonical\\"" env=CA_MD_PAGE\n'
h = once(h, lk, lk + '  Header set X-Robots-Tag "noindex, follow" env=CA_FEED\n', '.htaccess feed header')
wr('.htaccess', h)

# ---- _redirects (Netlify, Cloudflare Pages; gone addresses are left out there, as before) ----
r = rd('_redirects'); assert 'gsc1' not in r
head = r.split('\n', 2); assert head[1].startswith('# Gone addresses')
add = [NOTE + ' (patch gsc1)']
for f in FEEDS: add += [f'/news/press/feeds/{f}.xml /feeds/{f}.xml 301', f'/news/feeds/{f}.xml /feeds/{f}.xml 301']
add += ['/en/ / 301', '/en / 301', '/portfolio/ /work/ 301', '/portfolio /work/ 301'] + [f'/{a} /{b} 301' for a, b in PDFS]
wr('_redirects', head[0] + '\n' + head[1] + '\n' + '\n'.join(add) + '\n' + head[2])

# ---- _headers ----
x = rd('_headers'); assert 'X-Robots-Tag: noindex, follow' not in x
x = once(x, '/feeds/*\n  Cache-Control: public, max-age=3600\n', '/feeds/*\n  Cache-Control: public, max-age=3600\n  X-Robots-Tag: noindex, follow\n', '_headers feeds')
wr('_headers', x)

# ---- nginx.conf ----
n = rd('nginx.conf'); assert 'gsc1' not in n
a2 = '  # old addresses of the WordPress site (server/redirects.txt)\n'
nb = ['  ' + NOTE + ' (patch gsc1)',
      f'  rewrite ^/.+/feeds/({"|".join(FEEDS)})\\.xml$ {O}/feeds/$1.xml permanent;',
      f'  rewrite ^/en/?$ {O}/ permanent;', f'  rewrite ^/portfolio/?$ {O}/work/ permanent;']
nb += [f'  rewrite ^/{esc(a)}$ {O}/{b} permanent;' for a, b in PDFS]
nb += ['  location ~ ^/search/ { return 410; }', f'  if ($args ~ "(^|&)s=") {{ rewrite ^/$ {O}/? permanent; }}', '']
n = once(n, a2, a2 + '\n'.join(nb) + '\n', 'nginx rules')
m = re.search(r'\n  location / \{\n(.*?)\n    if \(\$ca_md\)', n, re.S); assert m
body = m.group(1)  # the page headers, the same for the feeds
feed = ('\n  # 26 November 2026 (Search Console, patch gsc1): the feeds are for feed readers; search engines may read them, not list them\n'
        '  location ^~ /feeds/ {\n' + body + '\n    add_header X-Robots-Tag "noindex, follow" always;\n    try_files $uri =404;\n  }')
n = once(n, '\n  location / {\n', feed + '\n  location / {\n', 'nginx feeds')
wr('nginx.conf', n)
print('server files patched in', D)
