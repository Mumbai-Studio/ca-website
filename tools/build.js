#!/usr/bin/env node
/* Collaborative Architecture · build the published site (25 October 2026)

   Turns the one-file source (src/ca-website.html) into the folder that goes on the server (dist/):
   - every address written as its own static HTML page (search engines and AI crawlers that do not run JavaScript read each page
     in full), with the site's scripts on top so it behaves exactly as the review copy does;
   - the published-site mode: no draft badge, review notes, flags or admin, real forms, analytics only after consent;
   - the search files (sitemap.xml, robots.txt, llms.txt, llms-full.txt, feeds, a Markdown copy of every page);
   - the server settings, from server/redirects.txt and the security headers below: .htaccess (Apache, LiteSpeed, most cPanel
     hosts), _redirects and _headers (Netlify, Cloudflare Pages), server/nginx.conf (nginx);
   - checks: no draft wording on any page, no inline script, every picture and internal link present.

   Usage:  npm run build              (the site for collaborativearchitecture.com, into dist/)
           npm run build:staging      (the same, marked noindex everywhere, for a test address)
   Needs:  Node 18+, and Playwright's Chromium (npm ci && npx playwright install chromium) */
'use strict';
const http = require('http'), fs = require('fs'), path = require('path'), crypto = require('crypto');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const argv = process.argv.slice(2);
const STAGING = argv.includes('--staging');
const OUT = path.resolve(ROOT, (argv.find(a => a.startsWith('--out=')) || '--out=dist').slice(6));
const SRC = path.join(ROOT, 'src', 'ca-website.html'), PUB = path.join(ROOT, 'public');
const ORIGIN = 'https://collaborativearchitecture.com', HOST = 'collaborativearchitecture.com';

/* ---------- the security headers and caching, the same on every kind of host ---------- */
const CSP = ["default-src 'self'", "script-src 'self' https://www.googletagmanager.com https://challenges.cloudflare.com", "style-src 'self' 'unsafe-inline'",
  "font-src 'self'", "img-src 'self' data: blob: https://www.google-analytics.com https://www.googletagmanager.com", "media-src 'self' blob:",
  "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com https://challenges.cloudflare.com",
  "frame-src https://challenges.cloudflare.com", "frame-ancestors 'self'", "base-uri 'self'", "form-action 'self'", "object-src 'none'"].join('; ');
const HEADERS = {
  'Content-Security-Policy': CSP,
  'Strict-Transport-Security': 'max-age=31536000',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'SAMEORIGIN',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=(), usb=()',
  'Cross-Origin-Opener-Policy': 'same-origin'
};
const CACHE = { page: 'public, max-age=0, must-revalidate', hashed: 'public, max-age=31536000, immutable', media: 'public, max-age=2592000', hour: 'public, max-age=3600' };

/* ---------- small helpers ---------- */
const write = (rel, text) => { const p = path.join(OUT, rel); fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, text); };
const copyDir = (from, to) => { fs.mkdirSync(to, { recursive: true }); for (const e of fs.readdirSync(from, { withFileTypes: true })) {
  if (e.name === 'config.php' || e.name === '.DS_Store') continue; // the server's own settings never come from the repository
  const a = path.join(from, e.name), b = path.join(to, e.name); e.isDirectory() ? copyDir(a, b) : fs.copyFileSync(a, b); } };
const fail = [];

/* ---------- the redirects: server/redirects.txt ---------- */
const RULES = fs.readFileSync(path.join(ROOT, 'server', 'redirects.txt'), 'utf8').split('\n').map(l => l.replace(/#.*/, '').trim()).filter(Boolean).map(l => {
  const [from, to] = l.split(/\s+/); if (!from || !to || !from.startsWith('/')) throw new Error('redirects.txt: cannot read the line "' + l + '"');
  return { from, to, prefix: from.endsWith('*'), gone: to === '410' };
});
// exact addresses first, then the longest prefixes, so "/blog/" (moved) wins over "/blog/*" (gone)
RULES.sort((a, b) => (a.prefix - b.prefix) || (a.prefix ? b.from.length - a.from.length : 0));
const reEsc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const apacheFrom = r => { const p = r.from.replace(/^\//, ''); return r.prefix ? '^' + reEsc(p.slice(0, -1)) : '^' + reEsc(p.replace(/\/$/, '')) + (p.endsWith('/') || p === '' ? '/?$' : '$'); };

function htaccess() {
  const L = [];
  L.push('# Collaborative Architecture · server settings for Apache and LiteSpeed (cPanel and most shared hosts)');
  L.push('# Written by tools/build.js: change server/redirects.txt or tools/build.js, then build again; do not edit this copy.', '');
  L.push('Options -Indexes -MultiViews', 'DirectoryIndex index.html index.php', 'AddDefaultCharset utf-8',
    'AddType image/webp .webp', 'AddType text/markdown .md', 'AddType application/manifest+json .webmanifest', 'AddType font/woff2 .woff2',
    'AddCharset utf-8 .md .txt .xml .json .js .css', 'ErrorDocument 404 /404.html', 'ErrorDocument 410 /404.html', '');
  L.push('<IfModule mod_rewrite.c>', 'RewriteEngine On', 'RewriteBase /', '');
  L.push('# one address for search engines: https, no www (only on the real domain, so a test address keeps working)');
  L.push(`RewriteCond %{HTTP_HOST} ^www\\.${reEsc(HOST)}$ [NC]`, `RewriteRule ^ ${ORIGIN}%{REQUEST_URI} [R=301,L]`);
  L.push(`RewriteCond %{HTTP_HOST} ^${reEsc(HOST)}$ [NC]`, 'RewriteCond %{HTTPS} !=on', 'RewriteCond %{HTTP:X-Forwarded-Proto} !=https', `RewriteRule ^ ${ORIGIN}%{REQUEST_URI} [R=301,L]`, '');
  L.push('# closed to the web: the form handlers\' private folder, and hidden files (but not /.well-known/, which certificates need)');
  L.push('RewriteRule ^_private(/|$) - [F,L]', 'RewriteCond %{REQUEST_URI} !^/\\.well-known/', 'RewriteRule (^|/)\\. - [F,L]', '');
  L.push('# old addresses of the WordPress site (server/redirects.txt)');
  for (const r of RULES) L.push(`RewriteRule ${apacheFrom(r)} ${r.gone ? '- [G,L]' : r.to + ' [R=301,L]'}`);
  L.push('', '# AI assistants that ask for Markdown (Accept: text/markdown) get the page\'s Markdown copy, the same text as the page');
  L.push('RewriteCond %{HTTP_ACCEPT} text/markdown [NC]', 'RewriteCond %{REQUEST_FILENAME} -d', 'RewriteCond %{REQUEST_FILENAME}/index.md -f', 'RewriteRule ^(.*?)/?$ $1/index.md [L]');
  L.push('</IfModule>', '');
  L.push('<IfModule mod_headers.c>');
  for (const [k, v] of Object.entries(HEADERS)) L.push(`  Header always set ${k} "${v}"`);
  L.push(`  <FilesMatch "\\.(html|md)$">`, `    Header set Cache-Control "${CACHE.page}"`, '    Header merge Vary "Accept"', '  </FilesMatch>');
  L.push(`  <FilesMatch "\\.(webp|jpe?g|png|gif|svg|ico|mp4|webm|woff2?)$">`, `    Header set Cache-Control "${CACHE.media}"`, '  </FilesMatch>');
  L.push(`  <FilesMatch "^site-[0-9]+\\.[0-9a-f]{12}\\.(js|css)$">`, `    Header set Cache-Control "${CACHE.hashed}"`, '  </FilesMatch>');
  L.push(`  <FilesMatch "^(robots\\.txt|sitemap\\.xml|llms\\.txt|llms-full\\.txt|site-config\\.js|site\\.webmanifest)$">`, `    Header set Cache-Control "${CACHE.hour}"`, '  </FilesMatch>');
  L.push('  <FilesMatch "^(index|404)\\.html$">', `    Header set Link "</llms.txt>; rel=\\"describedby\\"; type=\\"text/plain\\""`, '  </FilesMatch>');
  L.push('</IfModule>', '');
  L.push('<IfModule mod_deflate.c>', '  AddOutputFilterByType DEFLATE text/html text/css text/javascript application/javascript application/json application/xml text/xml text/plain text/markdown image/svg+xml application/manifest+json application/feed+json application/rss+xml', '</IfModule>');
  return L.join('\n') + '\n';
}
function netlifyRedirects() {
  const L = ['# Collaborative Architecture · old addresses (Netlify and Cloudflare Pages). Written by tools/build.js from server/redirects.txt.',
    '# Gone addresses (410 in redirects.txt) are left out here: these hosts answer them with the 404 page.'];
  for (const r of RULES) { if (r.gone) continue;
    if (r.prefix) L.push(`${r.from} ${r.to} 301`);
    else { L.push(`${r.from} ${r.to} 301`); if (r.from.endsWith('/') && r.from !== '/') L.push(`${r.from.slice(0, -1)} ${r.to} 301`); } }
  return L.join('\n') + '\n';
}
function netlifyHeaders() {
  const L = ['# Collaborative Architecture · response headers (Netlify and Cloudflare Pages). Written by tools/build.js.', '', '/*'];
  for (const [k, v] of Object.entries(HEADERS)) L.push(`  ${k}: ${v}`);
  L.push(`  Cache-Control: ${CACHE.page}`, '  Link: </llms.txt>; rel="describedby"; type="text/plain"', '');
  for (const p of ['/assets/*']) L.push(p, `  Cache-Control: ${CACHE.hashed}`);
  for (const p of ['/img/*', '/vid/*', '/fonts/*']) L.push(p, `  Cache-Control: ${CACHE.media}`);
  for (const p of ['/robots.txt', '/sitemap.xml', '/llms.txt', '/llms-full.txt', '/site-config.js', '/feeds/*']) L.push(p, `  Cache-Control: ${CACHE.hour}`);
  L.push('/*.md', '  Content-Type: text/markdown; charset=utf-8', '/api/*', '  X-Robots-Tag: noindex');
  return L.join('\n') + '\n';
}
function nginxConf() {
  const L = [];
  L.push('# Collaborative Architecture · nginx (a VPS or a dedicated server). Written by tools/build.js; set "root", the certificate lines',
    '# and the PHP socket for your server. The folder in "root" is the contents of dist/.', '');
  L.push('map $http_accept $ca_md { default 0; "~*text/markdown" 1; }', '');
  L.push('server {', '  listen 80; listen [::]:80;', `  server_name ${HOST} www.${HOST};`, '  location /.well-known/acme-challenge/ { root /var/www/collaborativearchitecture.com; }', `  location / { return 301 ${ORIGIN}$request_uri; }`, '}');
  L.push('server {', '  listen 443 ssl; listen [::]:443 ssl; http2 on;', `  server_name www.${HOST};`, '  # ssl_certificate /etc/letsencrypt/live/collaborativearchitecture.com/fullchain.pem;', '  # ssl_certificate_key /etc/letsencrypt/live/collaborativearchitecture.com/privkey.pem;', `  return 301 ${ORIGIN}$request_uri;`, '}');
  L.push('server {', '  listen 443 ssl; listen [::]:443 ssl; http2 on;', `  server_name ${HOST};`, '  # ssl_certificate /etc/letsencrypt/live/collaborativearchitecture.com/fullchain.pem;', '  # ssl_certificate_key /etc/letsencrypt/live/collaborativearchitecture.com/privkey.pem;');
  L.push('  root /var/www/collaborativearchitecture.com;', '  index index.html;', '  charset utf-8;', '  error_page 404 410 /404.html;', '');
  for (const [k, v] of Object.entries(HEADERS)) L.push(`  add_header ${k} "${v}" always;`);
  L.push('  gzip on; gzip_types text/css text/javascript application/javascript application/json application/xml text/plain text/markdown image/svg+xml application/manifest+json;', '');
  L.push('  types { text/html html; text/css css; text/javascript js; application/json json; application/xml xml; text/plain txt; text/markdown md; image/webp webp; image/png png; image/jpeg jpg jpeg; image/x-icon ico; video/mp4 mp4; font/woff2 woff2; application/manifest+json webmanifest; }', '');
  L.push('  # old addresses of the WordPress site (server/redirects.txt)');
  for (const r of RULES) { const re = apacheFrom(r).replace(/^\^/, '^/'); L.push(r.gone ? `  location ~ ${re} { return 410; }` : `  rewrite ${re} ${r.to} permanent;`); }
  L.push('', '  location ^~ /_private/ { deny all; }', '  location ~ /\\.(?!well-known/) { deny all; }', '  location ~ ^/api/(lib|config|config\\.sample)\\.php$ { deny all; }');
  L.push('  location ~ ^/api/(contact|subscribe)\\.php$ {', '    include fastcgi_params; fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;', '    fastcgi_pass unix:/run/php/php-fpm.sock;   # the PHP-FPM socket of this server', '  }');
  L.push(`  location /assets/ { add_header Cache-Control "${CACHE.hashed}"; ${Object.entries(HEADERS).map(([k, v]) => `add_header ${k} "${v}" always;`).join(' ')} try_files $uri =404; }`);
  L.push(`  location ~* ^/(img|vid|fonts)/ { add_header Cache-Control "${CACHE.media}"; ${Object.entries(HEADERS).map(([k, v]) => `add_header ${k} "${v}" always;`).join(' ')} try_files $uri =404; }`);
  L.push('  location / {', `    add_header Cache-Control "${CACHE.page}";`, '    add_header Vary "Accept";', `    ${Object.entries(HEADERS).map(([k, v]) => `add_header ${k} "${v}" always;`).join(' ')}`,
    '    if ($ca_md) { rewrite ^(.*/)$ $1index.md last; }', '    try_files $uri $uri/index.html =404;', '  }', '}');
  return L.join('\n') + '\n';
}

/* ---------- the page: the source fragment made into a whole document, in the published-site mode ---------- */
const frag = fs.readFileSync(SRC, 'utf8');
const cut = frag.indexOf('<a class="skip"');
if (cut < 0) throw new Error('the source has no skip link where the body begins');
let head = frag.slice(0, cut);
const swap = (a, b) => { if (!head.includes(a)) throw new Error('not found in the head: ' + a.slice(0, 80)); head = head.replace(a, b); };
swap('<title>CA Website Prototype</title>', '<title>Collaborative Architecture</title>');
swap('<link rel="preconnect" href="https://fonts.googleapis.com">\n', '');
swap('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n', '');
head = head.replace(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com\/css2[^"]*">/, () =>
  '<link rel="preload" href="/fonts/archivo-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin>\n<link rel="preload" href="/fonts/instrument-sans-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin>\n<link rel="stylesheet" href="/fonts/fonts.css">');
if (/fonts\.googleapis/.test(head)) throw new Error('Google Fonts still linked: the published site uses its own copy of the fonts');
const EXTRA = '<link rel="icon" href="/favicon.ico" sizes="48x48">\n<link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n<link rel="manifest" href="/site.webmanifest">\n<meta name="theme-color" content="#A7182C">\n<script src="/site-config.js"></script>\n';
const NOSCRIPT = '<noscript><style>#pl{display:none!important}.hero .def,.hero .bg:first-child,.ppq{opacity:1!important;transform:none!important}.ns .sl{position:relative!important;opacity:1!important;visibility:visible!important}</style></noscript>';
const DOC = '<!doctype html>\n<html lang="en" data-routing="path" data-live="1"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
  + EXTRA + head + NOSCRIPT + '\n</head><body>\n' + frag.slice(cut) + '\n</body></html>\n';

let siteConfig = fs.readFileSync(path.join(PUB, 'site-config.js'), 'utf8');
if (STAGING) { if (!/indexable:\s*true/.test(siteConfig)) throw new Error('site-config.js: "indexable: true" not found'); siteConfig = siteConfig.replace(/indexable:\s*true/, 'indexable: false'); }

/* every executable inline script becomes a shared file named by its content (the security policy allows no inline script; the browser keeps
   them for a year); large style blocks too. Order and behavior are unchanged. */
const SHARED = [];
for (const m of DOC.matchAll(/<(script|style)>([\s\S]*?)<\/\1>/g)) {
  if (m[1] === 'style' && m[2].length < 2000) continue;
  const h = crypto.createHash('sha256').update(m[2]).digest('hex').slice(0, 12), ext = m[1] === 'script' ? 'js' : 'css', n = SHARED.length + 1;
  SHARED.push({ whole: m[0], file: `assets/site-${n}.${h}.${ext}`, body: m[2], tag: m[1] === 'script' ? `<script src="/assets/site-${n}.${h}.${ext}"></script>` : `<link rel="stylesheet" href="/assets/site-${n}.${h}.${ext}">` });
}
const externalize = html => { for (const x of SHARED) { const i = html.indexOf(x.whole); if (i < 0) throw new Error('shared block not found in a page: ' + x.file); html = html.slice(0, i) + x.tag + html.slice(i + x.whole.length); } return html; };

/* ---------- a local server for the build: the public files, and the page for every address ---------- */
const TYPES = { '.webp': 'image/webp', '.jpg': 'image/jpeg', '.png': 'image/png', '.ico': 'image/x-icon', '.svg': 'image/svg+xml', '.mp4': 'video/mp4', '.woff2': 'font/woff2', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.webmanifest': 'application/manifest+json' };
const server = http.createServer((req, res) => {
  const u = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (u === '/site-config.js') { res.writeHead(200, { 'content-type': 'text/javascript' }); return res.end(siteConfig); }
  const root = path.resolve(PUB), f = path.resolve(root, '.' + path.posix.normalize(u));
  if (/\.[a-z0-9]{2,11}$/i.test(u)) {
    if (f.startsWith(root + path.sep) && fs.existsSync(f) && fs.statSync(f).isFile()) { res.writeHead(200, { 'content-type': TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream' }); return fs.createReadStream(f).pipe(res); }
    res.writeHead(404); return res.end();
  }
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); res.end(DOC);
});

(async () => {
  fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await ctx.addInitScript(() => { window.__PRERENDER = true; });
  await ctx.route(/^https?:\/\/(?!127\.0\.0\.1)/, r => r.abort()); // nothing from outside while building
  const pg = await ctx.newPage(); const errors = [];
  pg.on('pageerror', e => errors.push(e.message));

  await pg.goto(base + '/'); await pg.waitForFunction(() => window.CA_SEO && document.querySelector('#app').children.length);
  const plan = await pg.evaluate(() => {
    const S = CA_SEO, files = S.feeds(), md = S.pagesMd();
    const ids = [...(files['sitemap.xml'].match(/<loc>[^<]+<\/loc>/g) || [])].map(l => new URL(l.slice(5, -6)).pathname);
    return { paths: [...new Set([...ids, '/work/list/', '/work/map/', '/cookies/', '/privacy/', '/links/'])], files, md };
  });
  for (const x of SHARED) write(x.file, x.body);
  for (const [f, t] of Object.entries(plan.files)) write(f, t);
  for (const [f, t] of Object.entries(plan.md)) write(f, t);

  const BANNED = /⚑|later draft|for review|to be supplied|to be added|to be confirmed|before launch|in this draft|this draft|Nothing was sent|Draft website|Page in a later/i;
  const report = [], links = new Set(), media = new Set();
  const capture = async p => {
    await pg.goto(base + p, { waitUntil: 'load' });
    await pg.waitForFunction(() => document.querySelector('#app').children.length && document.querySelector('script#ca-ld'));
    await pg.waitForTimeout(250);
    return pg.evaluate(BAN => {
      const pl = document.getElementById('pl'); if (pl) pl.removeAttribute('hidden');
      document.querySelectorAll('[data-lq]').forEach(el => el.removeAttribute('data-lq'));
      const html = '<!doctype html>\n' + document.documentElement.outerHTML;
      const ld = document.querySelector('script#ca-ld').textContent;
      const b = document.body.cloneNode(true); b.querySelectorAll('script, style, template').forEach(x => x.remove());
      const text = (b.textContent || '') + ' ' + [...document.querySelectorAll('[title], [alt], meta[name="description"], meta[property^="og:"]')].map(e => e.getAttribute('title') || e.getAttribute('alt') || e.getAttribute('content') || '').join(' ') + ' ' + document.title;
      const m = text.match(new RegExp(BAN.src, 'i'));
      return { html, title: document.title, h1: (document.querySelector('#app h1') || {}).textContent || '', ldOk: (() => { try { return JSON.parse(ld)['@graph'].length; } catch (e) { return 0; } })(),
        words: document.querySelector('#app').innerText.split(/\s+/).filter(Boolean).length, links: [...document.querySelectorAll('a[href^="/"]')].map(a => a.getAttribute('href')),
        imgs: document.querySelectorAll('#app img').length, noalt: document.querySelectorAll('#app img:not([alt])').length, robots: (document.querySelector('meta[name="robots"]') || {}).content || '',
        banned: m ? text.slice(Math.max(0, m.index - 60), m.index + 60).replace(/\s+/g, ' ') : '' };
    }, { src: BANNED.source });
  };
  const keep = (p, r) => {
    const html = externalize(r.html);
    const inline = [...html.matchAll(/<script(?![^>]*\bsrc=)(?![^>]*type="application\/(ld\+)?json")[^>]*>/g)].length;
    if (inline) fail.push(`${p}: ${inline} inline script(s) left`);
    if (r.banned) fail.push(`${p}: draft wording on the page: “…${r.banned}…”`);
    for (const m of html.matchAll(/\/(img|vid|fonts)\/[A-Za-z0-9_./%-]+\.(webp|jpe?g|png|mp4|webm|woff2|gif)/g)) media.add(decodeURIComponent(m[0]));
    r.links.forEach(l => links.add(l.split('#')[0].split('?')[0]));
    return html;
  };
  for (const p of plan.paths) {
    const r = await capture(p);
    write(path.join(p, 'index.html'), keep(p, r));
    report.push({ path: p, title: r.title, h1: r.h1.trim().replace(/\s+/g, ' '), words: r.words, imgs: r.imgs, noalt: r.noalt, ld: r.ldOk, robots: r.robots });
  }
  // the 404 page answers at any address: its own links to "this page" become plain anchors
  const nf = await capture('/this-address-does-not-exist/');
  nf.html = nf.html.split('href="/this-address-does-not-exist/#').join('href="#'); nf.links = nf.links.filter(l => !l.startsWith('/this-address-does-not-exist/'));
  write('404.html', keep('/404.html', nf));
  await browser.close(); server.close();

  copyDir(PUB, OUT);
  write('site-config.js', siteConfig);
  write('.htaccess', htaccess());
  write('_redirects', netlifyRedirects());
  write('_headers', netlifyHeaders());
  fs.writeFileSync(path.join(ROOT, 'server', 'nginx.conf'), nginxConf());

  // every internal link reaches a page or a file; every picture, film and font named in a page exists
  for (const l of links) { if (!l || l === '/') continue; const f = path.join(OUT, l); if (!(fs.existsSync(path.join(f, 'index.html')) || (fs.existsSync(f) && fs.statSync(f).isFile()))) fail.push('link to a missing page: ' + l); }
  for (const m of media) if (!fs.existsSync(path.join(OUT, m))) fail.push('missing file: ' + m);
  if (errors.length) fail.push(...errors.map(e => 'script error: ' + e));

  write('build-report.json', JSON.stringify({ when: new Date().toISOString(), staging: STAGING, pages: report.length, shared: SHARED.map(x => x.file), problems: fail, report }, null, 1));
  console.log(`${STAGING ? 'STAGING · ' : ''}${report.length} pages + 404, ${Object.keys(plan.md).length} Markdown copies, ${Object.keys(plan.files).length} search files, ${SHARED.length} shared files, ${RULES.length} redirect rules → ${path.relative(ROOT, OUT) || OUT}`);
  if (fail.length) { console.error(`\n${fail.length} problem(s):\n- ` + [...new Set(fail)].slice(0, 60).join('\n- ')); process.exit(1); }
  console.log('checks passed: no draft wording, no inline script, every link and file present');
})().catch(e => { console.error(e); process.exit(1); });
