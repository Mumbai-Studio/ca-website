/* Collaborative Architecture · copy protection for the published site (13 November 2026)

   Mujib (13 November 2026): site-copying and cloning tools (Craft Anything and the like) must not be able to map or clone the
   published site, and nothing here may hamper search engines, AI crawlers and assistants, or SEO tools.
   The review copy on claude.ai is not touched: all of this is written by tools/build.js into the published site only.

   Three layers, one list:
   1. The server (.htaccess for Apache and LiteSpeed, nginx.conf) refuses site-copying tools and hidden (headless) browsers with
      403 and a page that shows only the studio's name and addresses.
   2. Every page starts with a small check (in boot.js): a browser driven by a program (navigator.webdriver, the way Craft Anything,
      Puppeteer, Playwright and Selenium run Chrome) stops loading at once and shows only the studio's name and addresses, as the
      printed page does (the no-PDF rule of 9 November 2026). Nothing of the design, the pictures or the films reaches it.
   3. robots.txt asks the copying tools that read it (HTTrack and Wget do, by default) to stay out.

   Always let through, at every layer (the GOOD list below):
   - search engines and their page renderers (Google, Bing, Yandex, Baidu, Apple, Petal, Coc Coc, Seznam, Naver, …);
   - every AI crawler and assistant the site welcomes (the source's own AI_BOTS list is added at build time, so the two never drift
     apart), and AI agents that sign their requests (Web Bot Auth: a Signature-Agent header, sent by ChatGPT's cloud browser and
     Google's agent);
   - SEO, speed and validation tools (PageSpeed Insights and Lighthouse, WebPageTest, GTmetrix, Semrush, Ahrefs, Screaming Frog,
     Sitebulb, Moz, Majestic, the W3C validators, uptime checks);
   - link previews (Instagram and Facebook, LinkedIn, X, Pinterest, WhatsApp, Slack, Telegram, Discord, iMessage).
   - The text channels stay open to every reader: robots.txt, sitemap.xml, llms.txt, llms-full.txt, the feeds, the IndexNow key and
     the Markdown copy of every page. Text alone does not let anyone clone the site's design.

   What it cannot do: a copying tool built to pass as an ordinary visitor (a normal browser, hand-driven, or one that lies about
   itself) cannot be told apart from a visitor; anything a visitor's screen shows can be captured. This stops the automatic tools.
   The GOOD list matches names (user agents), which a determined copier could fake; a CDN that verifies bots (Cloudflare's verified
   bots and signed agents) closes that gap (HOST-GUIDE, 6.1). */
'use strict';

/* ---------- the lists ---------- */
// never blocked: search, AI, SEO and speed tools, link previews (matched anywhere in the user agent, any case)
const GOOD = [
  // search engines and their renderers
  'Googlebot', 'Google-InspectionTool', 'GoogleOther', 'Google-Extended', 'Storebot-Google', 'AdsBot-Google', 'Mediapartners-Google',
  'FeedFetcher-Google', 'Google-Read-Aloud', 'Google-Site-Verification', 'Google-CloudVertexBot', 'APIs-Google', 'Google-Safety',
  'bingbot', 'BingPreview', 'MicrosoftPreview', 'msnbot', 'adidxbot', 'DuckDuckBot', 'DuckAssistBot', 'YandexBot', 'YandexRenderResourcesBot',
  'YandexImages', 'Baiduspider', 'Sogou', '360Spider', 'PetalBot', 'coccocbot', 'Applebot', 'SeznamBot', 'Yeti', 'NaverBot', 'Qwantbot',
  'MojeekBot', 'archive.org_bot', 'ia_archiver',
  // AI crawlers and assistants (the source's AI_BOTS are added at build time)
  'GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-User', 'Claude-SearchBot', 'anthropic-ai', 'PerplexityBot', 'Perplexity-User',
  'meta-externalagent', 'meta-externalfetcher', 'FacebookBot', 'Amazonbot', 'CCBot', 'Bytespider', 'GrokBot', 'xAI-Grok', 'Grok-DeepSearch',
  'cohere-ai', 'MistralAI-User', 'YouBot',
  // SEO, speed and validation tools
  'Chrome-Lighthouse', 'PTST', 'GTmetrix', 'Pingdom', 'SemrushBot', 'SiteAuditBot', 'AhrefsBot', 'AhrefsSiteAudit', 'Screaming Frog',
  'Sitebulb', 'rogerbot', 'dotbot', 'MJ12bot', 'DataForSeoBot', 'serpstatbot', 'BLEXBot', 'Seobility', 'Lumar', 'deepcrawl', 'ContentKing',
  'OncrawlBot', 'botify', 'W3C_Validator', 'W3C-checklink', 'Validator.nu', 'UptimeRobot', 'StatusCake',
  // link previews
  'facebookexternalhit', 'Facebot', 'LinkedInBot', 'Twitterbot', 'Pinterest', 'Slackbot', 'Discordbot', 'WhatsApp', 'TelegramBot',
  'SkypeUriPreview', 'redditbot', 'Embedly', 'Iframely'
];
// refused: site-copying tools, and hidden (headless) or program-driven browsers that do not say who they are
const COPIERS = [
  'HTTrack', 'Wget', 'WebCopier', 'Cyotek', 'WebCopy', 'Teleport', 'Offline Explorer', 'OfflineExplorer', 'SiteSucker', 'WebZIP', 'WebStripper',
  'WebReaper', 'BlackWidow', 'SiteSnagger', 'WebWhacker', 'Website Extractor', 'Website Downloader', 'Web Downloader', 'WebSauger', 'PageNest',
  'Scrapy', 'craft-anything', 'CraftAnything',
  'HeadlessChrome', 'PhantomJS', 'SlimerJS', 'Puppeteer', 'Playwright', 'Selenium'
];
// the copying tools that read robots.txt (HTTrack and Wget obey it by default)
const ROBOTS_NAMES = ['HTTrack', 'Wget', 'WebCopier', 'WebZIP', 'Offline Explorer', 'Teleport', 'TeleportPro', 'SiteSnagger', 'WebStripper', 'WebReaper', 'BlackWidow', 'SiteSucker', 'Scrapy'];

/* ---------- the patterns (the same in the page, Apache and nginx) ---------- */
const reTok = t => t.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&').replace(/ /g, '\\s');
const uniq = a => [...new Set(a.map(s => s.trim()).filter(Boolean))];
const goodList = (aiBots = []) => uniq([...GOOD, ...aiBots]);
const pattern = list => '(' + uniq(list).map(reTok).join('|') + ')';
// paths open to every reader: the search and AI text files, the Markdown copies, the 403 page itself, and certificate checks
const OPEN_PATHS = '\\.(txt|md|xml|json)$|^/403\\.html$|^/\\.well-known/';
const AGENT_COOKIE = 'ca-agent';

/* ---------- the studio's name and addresses, as the printed page shows them ---------- */
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
function card(cfg) {
  const country = c => { try { return new Intl.DisplayNames(['en'], { type: 'region' }).of(c); } catch (e) { return c; } };
  const office = f => [f.name, f.street, [f.locality, f.postal].filter(Boolean).join(' '), country(f.country)].filter(Boolean).map(esc).join('<br>');
  const style = 'html{background:#fff;color:#111;font:16px/1.55 system-ui,-apple-system,"Segoe UI",Arial,sans-serif}body{margin:0;padding:12vh 8vw}'
    + 'h1{margin:0 0 28px;font-size:22px;font-weight:700;color:#A7182C}p{margin:0 0 20px}';
  const body = `<h1>${esc(cfg.name)}</h1>${cfg.offices.map(f => `<p>${office(f)}</p>`).join('')}<p>${esc(cfg.email)}</p>`;
  return { head: `<meta charset="utf-8"><meta name="robots" content="noindex"><title>${esc(cfg.name)}</title><style>${style}</style>`, body };
}

/* ---------- 2. the page's check, put at the top of boot.js ---------- */
function pageGuard(cfg, aiBots) {
  const c = card(cfg);
  return `(function(){var w=window,d=document,n=navigator,ua=n.userAgent||'';
try{if(${new RegExp(pattern(goodList(aiBots)), 'i')}.test(ua))return;
if(/(?:^|;\\s*)${AGENT_COOKIE}=1/.test(d.cookie))return;
var h=d.documentElement,a=n.webdriver===true||/HeadlessChrome|PhantomJS|SlimerJS/i.test(ua)
||!!(w.callPhantom||w._phantom||w.__nightmare||w.domAutomation||w.domAutomationController||w.__webdriver_evaluate||w.__selenium_unwrapped
||w.__driver_evaluate||w.__webdriver_script_fn||w.__playwright__binding__||w.__pwInitScripts)
||h.hasAttribute('webdriver')||h.hasAttribute('selenium')||h.hasAttribute('driver');
if(!a)return;}catch(e){return;}
w.CA_HOLD=1;try{w.stop();}catch(e){}
h.className='';h.innerHTML=${JSON.stringify(`<head>${c.head}</head><body>${c.body}</body>`)};})();\n`;
}

/* ---------- the 403 page ---------- */
const page403 = cfg => { const c = card(cfg); return `<!doctype html>\n<html lang="en"><head>${c.head}</head><body>${c.body}</body></html>\n`; };

/* ---------- 1. the server ---------- */
function apacheRules(aiBots, host) {
  return [
    '# copy protection (13 November 2026, tools/guard.js): site-copying tools and hidden (headless) browsers get 403 and the studio\'s',
    '# name and addresses; search engines, AI crawlers and assistants (also any agent that signs its requests), SEO and speed tools',
    '# and link previews always pass; the text files (robots.txt, sitemap.xml, llms.txt, feeds, Markdown copies) stay open to all',
    'RewriteCond %{HTTP:Signature-Agent} .',
    `RewriteRule ^ - [CO=${AGENT_COOKIE}:1:${host}:1440:/:true:false]`,
    `RewriteCond %{REQUEST_URI} !(${OPEN_PATHS})`,
    'RewriteCond %{HTTP:Signature-Agent} ^$',
    `RewriteCond %{HTTP_USER_AGENT} !${pattern(goodList(aiBots))} [NC]`,
    `RewriteCond %{HTTP_USER_AGENT} ${pattern(COPIERS)} [NC]`,
    'RewriteRule ^ - [F,L]',
    ''
  ];
}
function nginxMaps(aiBots) {
  return [
    '# copy protection (13 November 2026, tools/guard.js): site-copying tools and hidden (headless) browsers get 403 and the studio\'s',
    '# name and addresses; search engines, AI crawlers and assistants (also any agent that signs its requests), SEO and speed tools',
    '# and link previews always pass; the text files (robots.txt, sitemap.xml, llms.txt, feeds, Markdown copies) stay open to all',
    `map $http_user_agent $ca_good { default 0; "~*${pattern(goodList(aiBots))}" 1; }`,
    `map $http_user_agent $ca_copier { default 0; "~*${pattern(COPIERS)}" 1; }`,
    'map $http_signature_agent $ca_signed { default 1; "" 0; }',
    // refused: not good, not signed, a copier, and not one of the open paths (the same as OPEN_PATHS, after "001:")
    'map "$ca_good$ca_signed$ca_copier:$uri" $ca_refuse { default 0; "~^001:(?!/403\\.html$|/\\.well-known/|.*\\.(txt|md|xml|json)$)" 1; }',
    `map $http_signature_agent $ca_agent_cookie { default "${AGENT_COOKIE}=1; Path=/; Max-Age=86400; Secure; SameSite=Lax"; "" ""; }`,
    ''
  ];
}

/* ---------- 3. robots.txt ---------- */
const robotsAddendum = () => '\n# Site-copying tools (13 November 2026): this site may not be mirrored or cloned\n'
  + ROBOTS_NAMES.map(n => `User-agent: ${n}`).join('\n') + '\nDisallow: /\n';

/* ---------- a check the build runs: who passes and who does not ---------- */
function selfTest(aiBots) {
  const good = new RegExp(pattern(goodList(aiBots)), 'i'), bad = new RegExp(pattern(COPIERS), 'i');
  const refused = ua => !good.test(ua) && bad.test(ua);
  const PASS = [
    'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (compatible; Google-InspectionTool/1.0;)',
    'Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36 Chrome-Lighthouse',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/142.0.0.0 Safari/537.36 Chrome-Lighthouse',
    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/116.0.1938.76 Safari/537.36',
    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.2; +https://openai.com/gptbot',
    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)',
    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)',
    'Mozilla/5.0 (compatible; SemrushBot/7~bl; +http://www.semrush.com/bot.html)', 'Mozilla/5.0 (compatible; AhrefsBot/7.0; +http://ahrefs.com/robot/)',
    'Screaming Frog SEO Spider/22.0', 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)', 'LinkedInBot/1.0 (compatible; Mozilla/5.0)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1',
    'curl/8.5.0'
  ];
  const REFUSE = [
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/142.0.0.0 Safari/537.36',
    'Mozilla/4.5 (compatible; HTTrack 3.0x; Windows 98)', 'Wget/1.21.4', 'SiteSucker/3.2.7', 'Scrapy/2.11.2 (+https://scrapy.org)', 'Offline Explorer/8.5'
  ];
  const problems = [];
  for (const ua of PASS) if (refused(ua)) problems.push('copy protection would refuse a good reader: ' + ua);
  for (const ua of REFUSE) if (!refused(ua)) problems.push('copy protection would let a copying tool through: ' + ua);
  for (const b of aiBots) if (!good.test(b)) problems.push('an AI crawler of the source is not on the copy protection\'s good list: ' + b);
  return problems;
}

module.exports = { GOOD, COPIERS, ROBOTS_NAMES, OPEN_PATHS, AGENT_COOKIE, goodList, pattern, card, pageGuard, page403, apacheRules, nginxMaps, robotsAddendum, selfTest };
