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
  L.push(`  <FilesMatch "^(site-[0-9]+|data-[a-z0-9-]+|boot|load)\\.[0-9a-f]{12}\\.(js|css)$">`, `    Header set Cache-Control "${CACHE.hashed}"`, '  </FilesMatch>');
  L.push(`  <FilesMatch "^(robots\\.txt|sitemap\\.xml|llms\\.txt|llms-full\\.txt|site-config\\.js|site\\.webmanifest|ca-fonts\\.css)$">`, `    Header set Cache-Control "${CACHE.hour}"`, '  </FilesMatch>');
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
let frag = fs.readFileSync(SRC, 'utf8');
const cut = frag.indexOf('<a class="skip"');
if (cut < 0) throw new Error('the source has no skip link where the body begins');
let head = frag.slice(0, cut);
const swap = (a, b) => { if (!head.includes(a)) throw new Error('not found in the head: ' + a.slice(0, 80)); head = head.replace(a, b); };
// 5 November 2026: the source no longer connects to Google Fonts ahead of time (fonts from the site's own files since 4 November); drop the tags only when present
const swapIf = (a, b) => { if (head.includes(a)) head = head.replace(a, b); };
swap('<title>CA Website Prototype</title>', '<title>Collaborative Architecture</title>');
swapIf('<link rel="preconnect" href="https://fonts.googleapis.com">\n', '');
swapIf('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n', '');
head = head.replace(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com\/css2[^"]*">/, () =>
  '<link rel="preload" href="/fonts/archivo-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin>\n<link rel="preload" href="/fonts/instrument-sans-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin>\n<link rel="stylesheet" href="/fonts/fonts.css">');
// 5 November 2026: the page may name Google Fonts inside a script, as the fallback when its own font files cannot be read (4 November);
// what must not be left is a Google Fonts stylesheet linked in the head, which every visitor would load
if (/<link\b[^>]*fonts\.googleapis/i.test(head)) throw new Error('Google Fonts still linked: the published site uses its own copy of the fonts');
const EXTRA = '<link rel="icon" href="/favicon.ico" sizes="48x48">\n<link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n<link rel="manifest" href="/site.webmanifest">\n<meta name="theme-color" content="#A7182C">\n<script src="/site-config.js" defer></script>\n';
const NOSCRIPT = '<noscript><style>#pl{display:none!important}.hero .def,.hero .bg:first-child,.ppq{opacity:1!important;transform:none!important}.ns .sl{position:relative!important;opacity:1!important;visibility:visible!important}</style></noscript>';
// 5 November 2026 (W3C validation, Fix 1, approved by Mujib): the no-script styles go first in the head. The logo screen (div#pl) sits in the
// source ahead of the main styles so the crimson paints first, and the browser ends the head there; styles placed last would land in the body.
/* 7 November 2026 (speed): the review copy on claude.ai is held to 511 files, so the small copies (-800) of 45 pictures were retired there
   and listed in C.smallSame (cards and Work tiles then load the full picture, up to 780 KB, where the small copy is 20-130 KB). The
   published site has no such limit: wherever public/ holds a small copy at least as new as its picture, the picture leaves the list and its
   cards and tiles take the small copy again. Make the copies with tools/small800.py after the pictures are updated. */
const SMALL_KEPT = [], SMALL_USED = [];
frag = frag.replace(/C\.smallSame = \[([\s\S]*?)\];/, (all, body) => 'C.smallSame = [' + body.replace(/'(img\/[^']+)',?\s*/g, (m, f) => {
  const full = path.join(PUB, f + '.webp'), small = path.join(PUB, f + '-800.webp');
  if (fs.existsSync(full) && fs.existsSync(small) && fs.statSync(small).mtimeMs >= fs.statSync(full).mtimeMs) { SMALL_USED.push(f); return ''; }
  SMALL_KEPT.push(f); return m; }) + '];');
const DOC = '<!doctype html>\n<html lang="en" data-routing="path" data-live="1"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
  + NOSCRIPT + '\n' + EXTRA + head + '\n</head><body>\n' + frag.slice(cut) + '\n</body></html>\n';

let siteConfig = fs.readFileSync(path.join(PUB, 'site-config.js'), 'utf8');
if (STAGING) { if (!/indexable:\s*true/.test(siteConfig)) throw new Error('site-config.js: "indexable: true" not found'); siteConfig = siteConfig.replace(/indexable:\s*true/, 'indexable: false'); }

/* every executable inline script becomes a shared file named by its content (the security policy allows no inline script; the browser keeps
   them for a year); large style blocks too. Order and behavior are unchanged. */
/* speed (25 October 2026): the shared files are minified (esbuild). Each script stays a classic script: names at the top level are kept,
   because the files share them; only local names are shortened. The target keeps every browser the site supports. */
const esbuild = require('esbuild');
const TARGET = ['chrome100', 'edge100', 'firefox100', 'safari15', 'ios15'];
const minify = (code, ext) => esbuild.transformSync(code, { loader: ext, minify: true, target: TARGET, legalComments: 'none', charset: 'utf8' }).code;
const SHARED = [];
for (const m of DOC.matchAll(/<(script|style)>([\s\S]*?)<\/\1>/g)) {
  if (m[1] === 'style' && m[2].length < 2000) continue;
  const ext = m[1] === 'script' ? 'js' : 'css', body = minify(m[2], ext);
  const h = crypto.createHash('sha256').update(body).digest('hex').slice(0, 12), n = SHARED.length + 1;
  SHARED.push({ whole: m[0], file: `assets/site-${n}.${h}.${ext}`, body, tag: m[1] === 'script' ? `<script src="/assets/site-${n}.${h}.${ext}"></script>` : `<link rel="stylesheet" href="/assets/site-${n}.${h}.${ext}">` });
}
/* speed (25 October 2026): the page paints first, then its scripts run.
   - boot.js, in the head (tiny, runs before the first paint): on the first page of a visit it marks <html class="pl-boot">, so the logo
     screen is there from the first frame (it used to wait for the scripts); it notes the time, so the logo still holds 3.25 seconds.
   - load.js, at the end of the body: puts the page's scripts in after the first frame has been painted, in their order (async=false keeps
     the order). The built page is complete without them, so the first picture and the type appear as soon as they arrive. */
// the Work page's top cell: the built page shows the first of the projects that take turns (C.leads); a returning visitor whose turn
// is another waits for the page's drawing (html.w01-wait hides that one cell for the moment), so the cell never switches before their eyes
const LEADS = (frag.match(/C\.leads = \[([^\]]*)\]/) || [, ''])[1].split(',').filter(x => x.trim()).length;
const BOOT = minify(`(function(){try{var d=document.documentElement;if(sessionStorage.getItem('ca-pl')!=='1'){d.classList.add('pl-boot');window.CA_PL_T=performance.now();}}catch(e){}
try{var n=+localStorage.getItem('ca-w01')||0;if(${LEADS}>1&&n%${LEADS}!==0)document.documentElement.classList.add('w01-wait');}catch(e){}})();`, 'js');
const bootFile = `assets/boot.${crypto.createHash('sha256').update(BOOT).digest('hex').slice(0, 12)}.js`;
/* 7 November 2026 (speed): boot.js was the one request the first paint still waited for (one round trip, 0.6 s on Lighthouse's slow 4G).
   It is now written into each page's head, and the security policy allows exactly this script by its hash; no other inline script
   runs. The file is still written (assets/boot.*.js) for anything that names it. Upload .htaccess (or _headers) with the pages. */
const BOOT_HASH = `'sha256-${crypto.createHash('sha256').update(BOOT).digest('base64')}'`;
HEADERS['Content-Security-Policy'] = HEADERS['Content-Security-Policy'].replace("script-src 'self'", `script-src 'self' ${BOOT_HASH}`);
/* 7 November 2026 (repair): the page's data. Since 4 November the source keeps the projects, the landscape line and the keywords as JSON
   blocks (type="application/json", read with JSON.parse); the build left them in every page it wrote, so each page carried some 260 KB of
   the same data (about 60 KB compressed), where the build of 3 November kept it in a shared file the browser fetches once. Each large block
   now becomes a shared file again: it puts the same block back into the page, with the same id, before the site's scripts run, so they read it
   as before. The small block of published edits (ca-edits) stays in the page. */
const DATA = [];
for (const m of DOC.matchAll(/<script type="application\/json" id="([a-z0-9-]+)">([\s\S]*?)<\/script>/g)) {
  if (m[2].length < 2000) continue;
  JSON.parse(m[2]);   // the block must be valid JSON
  const body = `(function(){var s=document.createElement('script');s.type='application/json';s.id=${JSON.stringify(m[1])};s.text=${JSON.stringify(m[2])};document.body.appendChild(s);})();`;
  DATA.push({ whole: m[0], id: m[1], file: `assets/data-${m[1]}.${crypto.createHash('sha256').update(body).digest('hex').slice(0, 12)}.js`, body });
}
const SCRIPTS = SHARED.filter(x => x.file.endsWith('.js'));
/* 7 November 2026 (repair): the scripts go in only once the whole page has been read (the page's data sits in it, below this tag), so on a
   slow connection they can never start before their data has arrived. (High priority for them was tried and left out: once the built
   page stopped asking for the pictures below the first screen, they no longer queue behind them, and the laptop scores were better.) */
const LOADER = minify(`(function(){var L=${JSON.stringify([...DATA, ...SCRIPTS].map(x => '/' + x.file))},done=false,ready=false;
function go(){if(done||!ready)return;if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',go);return;}done=true;for(var i=0;i<L.length;i++){var s=document.createElement('script');s.src=L[i];s.async=false;document.body.appendChild(s);}}
function painted(){ready=true;go();}
if(window.requestAnimationFrame)requestAnimationFrame(function(){setTimeout(painted,0);});setTimeout(painted,400);})();`, 'js');
const loadFile = `assets/load.${crypto.createHash('sha256').update(LOADER).digest('hex').slice(0, 12)}.js`;
const externalize = html => {
  for (const x of SHARED) { const i = html.indexOf(x.whole); if (i < 0) throw new Error('shared block not found in a page: ' + x.file); html = html.slice(0, i) + x.tag + html.slice(i + x.whole.length); }
  for (const x of DATA) { const i = html.indexOf(x.whole); if (i < 0) throw new Error('data block not found in a page: ' + x.id); html = html.slice(0, i) + html.slice(i + x.whole.length); }
  // the scripts' own tags give way to the loader, at the place of the first one
  let first = -1;
  for (const x of SCRIPTS) { const i = html.indexOf(x.tag); if (i < 0) throw new Error('script tag not found: ' + x.file); if (first < 0) first = i; html = html.slice(0, i) + html.slice(i + x.tag.length); }
  html = html.slice(0, first) + `<script src="/${loadFile}"></script>` + html.slice(first);
  // 7 November 2026 (speed): site-config.js is deferred: nothing needs it before the page has been read (load.js brings the site's scripts
  // after that), so it no longer holds up the logo screen's first paint. boot.js stays the one script the first paint waits for.
  const c = html.search(/<script src="\/site-config\.js" defer(="")?><\/script>/); if (c < 0) throw new Error('site-config.js tag not found');   // the page as written by the browser reads defer=
  return html.slice(0, c) + `<script>${BOOT}</script>` + html.slice(c);
};

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
    return { paths: [...new Set([...ids, '/work/list/', '/work/map/', '/privacy/', '/links/'])].filter(p => !/\.[a-z0-9]{2,5}$/i.test(p)), files, md }; // 26 October 2026: the sitemap also lists the press PDFs; they are files, not pages
  });
  for (const x of SHARED) write(x.file, x.body);
  for (const x of DATA) write(x.file, x.body);
  write(bootFile, BOOT); write(loadFile, LOADER);
  for (const [f, t] of Object.entries(plan.files)) write(f, t);
  for (const [f, t] of Object.entries(plan.md)) write(f, t);

  const BANNED = /⚑|later draft|for review|to be supplied|to be added|to be confirmed|before launch|in this draft|this draft|Nothing was sent|Draft website|Page in a later/i;
  const report = [], links = new Set(), media = new Set();
  const capture = async p => {
    await pg.goto(base + p, { waitUntil: 'load' });
    await pg.waitForFunction(() => document.querySelector('#app').children.length && document.querySelector('script#ca-ld'));
    await pg.waitForTimeout(250);
    return pg.evaluate(BAN => {
      // the logo screen stays hidden in the built page: the head script (boot.js) shows it from the first frame on the first page of a visit
      const pl = document.getElementById('pl'); if (pl) { pl.setAttribute('hidden', ''); pl.classList.remove('run', 'rm', 'out'); }
      document.querySelectorAll('[data-lq]').forEach(el => el.removeAttribute('data-lq'));
      /* 7 November 2026 (repair): the source's head scripts marked data-boot (the page's own security policy, the early first picture, the
         logo's start, the font link) run in the review copy before the rest of the page. Here they have done their work: what they set up
         (the policy, the font link) stays in the page, and the scripts go, so the site's scripts are the only ones load.js brings, from the
         body, after the page's data. Their review-only pieces go too: the early picture (the page names its own) and the Google Fonts
         fallback (the published site has its own font files, and its security policy would refuse Google's). */
      document.querySelectorAll('script[data-boot], link[data-ca-early], link[href*="fonts.googleapis"]').forEach(el => el.remove());
      // 7 November 2026 (speed): the font stylesheet becomes a marker the build fills with the font faces themselves (keep(), below)
      document.querySelectorAll('link[rel="stylesheet"][href$="/fonts/ca-fonts.css"]').forEach(el => { const m = document.createElement('meta'); m.setAttribute('name', 'ca-fonts'); el.replaceWith(m); });
      /* 7 November 2026 (speed; nothing a visitor sees changes): the built page is what the browser shows until the site's scripts arrive,
         and the scripts then draw the page again with their own pictures (render). In the built page:
         - a slideshow keeps only the picture on screen: the slides behind it (Home's hero and Studio Now) had their full pictures asked for
           at high priority, 1.5-2.5 MB before anything else could load; the scripts fetch them ahead as before, well before they are seen;
         - only the first picture keeps high priority (the hero or the top tile); the others are lazy and wait their turn. */
      document.querySelectorAll('#app [data-bg].bg:not(.on) > img.bgi').forEach(im => { const box = im.parentElement; if (box.parentElement && box.parentElement.querySelectorAll(':scope > .bg').length > 1) im.remove(); });
      let firstHigh = null;
      document.querySelectorAll('#app img.bgi[fetchpriority="high"]').forEach(im => { if (!firstHigh) { firstHigh = im; return; } im.removeAttribute('fetchpriority'); im.setAttribute('loading', 'lazy'); });
      /* - pictures below the first screen are kept for search engines and for browsers without scripts (in noscript), and are not
           fetched by the built page: the site's scripts draw them and fetch them ahead, as on the review site, so they still arrive
           before they are seen. On a laptop their 2-3 MB had started before the first picture had painted. */
      scrollTo(0, 0);
      document.querySelectorAll('#app img.bgi').forEach(im => { if (im === firstHigh) return; const box = im.parentElement || im;
        if (box.getBoundingClientRect().top < innerHeight) return;
        const ns = document.createElement('noscript'); ns.textContent = im.outerHTML; im.replaceWith(ns); });
      /* - the same for pictures set as backgrounds below the first screen (Home's expertise thumbnails are full pictures, 940 KB); the
           scripts set them again when they draw the page */
      document.querySelectorAll('#app [data-bg][style*="background-image"]').forEach(el => { if (el.getBoundingClientRect().top < innerHeight) return;
        el.style.removeProperty('background-image'); el.removeAttribute('data-done'); el.removeAttribute('data-shown'); if (!el.getAttribute('style')) el.removeAttribute('style'); });
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
  /* 7 November 2026 (speed): the font faces (fonts/ca-fonts.css, 5 KB, 1 KB compressed) are written into the head of each page instead of the font link,
     with their file paths made absolute, so the first paint waits for no stylesheet: the slow-4G test showed the logo screen held back by
     this one file. The faces only name the files; the browser fetches a font when the page first uses it, as before. */
  const FONT_CSS = fs.existsSync(path.join(PUB, 'fonts', 'ca-fonts.css')) ? fs.readFileSync(path.join(PUB, 'fonts', 'ca-fonts.css'), 'utf8')
    .replace(/\/\*[\s\S]*?\*\//g, '').replace(/url\(\s*['"]?(?!\/|https?:|data:)([^'")]+)['"]?\s*\)/g, 'url(/fonts/$1)').replace(/\n+/g, '') : '';
  const keep = (p, r) => {
    if (!FONT_CSS) fail.push('fonts: public/fonts/ca-fonts.css is missing');
    r.html = r.html.replace('<meta name="ca-fonts">', '').replace('</head>', `<style id="ca-fonts">${FONT_CSS}</style></head>`);   // in the head: a style element belongs there
    /* 7 November 2026 (speed): the Work mosaic's tiles. The site's script gives phones the 800 px copy of every tile but the featured one
       (mblock, 31 October); the built page is written at laptop size, so a phone first loaded the full pictures (Peace Pavilion 650 KB,
       Project Alpha 780 KB) and then the copies. Each tile now names both: the full picture for laptops and the copy for phones. */
    r.html = r.html.replace(/(<a class="mb(?: s)?"[^>]*>\s*<div class="fr">\s*<div class="im"[^>]*>\s*)<img ([^>]*?)src="(\/img\/[^"]+?)\.webp"([^>]*)>/g, (all, pre, a, f, b) => {
      if (/srcset=/.test(a + b) || /-800$/.test(f) || !fs.existsSync(path.join(PUB, f + '-800.webp'))) return all;
      const w = +((a + b).match(/\bwidth="(\d+)"/) || [, 1920])[1];
      return `${pre}<img ${a}src="${f}.webp" srcset="${f}-800.webp 800w, ${f}.webp ${w}w" sizes="(max-width:700px) 1px, 100vw"${b}>`; });
    const html = externalize(r.html);
    const inline = [...html.matchAll(/<script(?![^>]*\bsrc=)(?![^>]*type="application\/(ld\+)?json")[^>]*>([\s\S]*?)<\/script>/g)].filter(m => m[2] !== BOOT).length;
    if (inline) fail.push(`${p}: ${inline} inline script(s) left`);
    if (r.banned) fail.push(`${p}: draft wording on the page: “…${r.banned}…”`);
    for (const m of html.matchAll(/\/(img|vid|fonts)\/[A-Za-z0-9_./%-]+\.(webp|jpe?g|png|mp4|webm|woff2|gif|css)/g)) media.add(decodeURIComponent(m[0]));
    r.links.forEach(l => links.add(l.split('#')[0].split('?')[0]));
    return html;
  };
  for (const p of plan.paths) {
    let r; try { r = await capture(p); } catch (e) { console.error('could not build ' + p + ': ' + String(e).slice(0, 160), errors.slice(-3)); fail.push('could not build the page ' + p); continue; } // 26 October 2026: a page that fails is reported with the others, and the build still fails
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

  /* 7 November 2026 (Mujib): the opening. On the first page of a visit the logo screen must cover the first frame, before the page's
     scripts arrive: the head script (boot.js) marks <html class="pl-boot">, and the rule that then shows the hidden logo screen must
     outrank the site's [hidden]{display:none!important}. The live build of 3 November had lost the !important, so the page and its
     picture showed before the logo. */
  { const home = fs.readFileSync(path.join(OUT, 'index.html'), 'utf8'), iBody = home.indexOf('<body'), iBoot = home.indexOf(`<script>${BOOT}</script>`),
      iPl = home.indexOf('id="pl"'), iHero = home.search(/class="hero\b/);
    const css = SHARED.filter(x => x.file.endsWith('.css')).map(x => x.body).join('') + ((home.match(/<style id="pl-first">([\s\S]*?)<\/style>/) || [, ''])[1]);
    const show = css.match(/html\.pl-boot #pl\[hidden\]\{display:[^}]*\}/g) || [];
    if (!(iBoot > 0 && iBoot < iBody)) fail.push('opening: the boot script is not in the head of the home page');
    if (!HEADERS['Content-Security-Policy'].includes(BOOT_HASH)) fail.push('opening: the security policy does not allow the boot script by its hash');
    if (iPl < iBody || (iHero > 0 && iPl > iHero)) fail.push('opening: the logo screen does not come before the page on the home page');
    if (!show.length || show.some(r => !/!important/.test(r))) fail.push('opening: the rule that shows the logo screen at first paint is missing or not !important, so [hidden]{display:none!important} would hide it'); }

  // every internal link reaches a page or a file; every picture, film and font named in a page exists
  for (const l of links) { if (!l || l === '/') continue; const f = path.join(OUT, l); if (!(fs.existsSync(path.join(f, 'index.html')) || (fs.existsSync(f) && fs.statSync(f).isFile()))) fail.push('link to a missing page: ' + l); }
  for (const m of media) if (!fs.existsSync(path.join(OUT, m))) fail.push('missing file: ' + m);
  /* 7 November 2026 (repair): the fonts. Every page links the site's own font stylesheet, and every font file it names is in the package
     (the build of 7 November found the stylesheet missing: the page would have fallen back to the browser's fonts) */
  { const home = fs.readFileSync(path.join(OUT, 'index.html'), 'utf8'), faces = (home.match(/<style id="ca-fonts">([\s\S]*?)<\/style>/) || [])[1] || '';
    if (!/@font-face/.test(faces)) fail.push('fonts: the home page does not carry the site\'s own font faces');
    for (const u of faces.matchAll(/url\(\s*['"]?([^'")]+)['"]?\s*\)/g)) if (!fs.existsSync(path.join(OUT, u[1]))) fail.push('fonts: a font face names a missing file: ' + u[1]);
    // the site's scripts are brought in from the body, below the page's data, and none is left in the head
    const iLoad = home.indexOf(`/${loadFile}`), iData = home.indexOf('id="ca-data-j"'), iBody = home.indexOf('<body');
    if (iData > 0) fail.push('data: the site\'s data is written into every page (ca-data-j) instead of a shared file');
    if (iLoad < iBody || (iData > 0 && iLoad < iData)) fail.push('scripts: load.js is not in the body after the page\'s data (it would run the scripts before their data)');
    if (/data-boot/.test(home)) fail.push('scripts: a review-only head script (data-boot) is left in the page'); }
  if (errors.length) fail.push(...errors.map(e => 'script error: ' + e));

  if (SMALL_KEPT.length) console.log(`note: ${SMALL_KEPT.length} picture(s) have no small copy (-800) as new as the picture, so cards and tiles load the full file: run tools/small800.py (${SMALL_KEPT.slice(0, 6).join(', ')}${SMALL_KEPT.length > 6 ? ', …' : ''})`);
  write('build-report.json', JSON.stringify({ when: new Date().toISOString(), staging: STAGING, pages: report.length, shared: SHARED.map(x => x.file), small800: { used: SMALL_USED, missing: SMALL_KEPT }, problems: fail, report }, null, 1));
  console.log(`${STAGING ? 'STAGING · ' : ''}${report.length} pages + 404, ${Object.keys(plan.md).length} Markdown copies, ${Object.keys(plan.files).length} search files, ${SHARED.length} shared files, ${RULES.length} redirect rules → ${path.relative(ROOT, OUT) || OUT}`);
  if (fail.length) { console.error(`\n${fail.length} problem(s):\n- ` + [...new Set(fail)].slice(0, 60).join('\n- ')); process.exit(1); }
  console.log('checks passed: no draft wording, no inline script, every link and file present');
})().catch(e => { console.error(e); process.exit(1); });
