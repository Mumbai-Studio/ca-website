#!/usr/bin/env node
/* Collaborative Architecture · IndexNow after each upload (1 November 2026; 9 November 2026, approved by Mujib: benchmark audit S3)

   Tells the IndexNow search engines (Bing, which also feeds ChatGPT search and Copilot, and Yandex, Seznam, Naver, Yep and the others
   that share IndexNow) which addresses are new or changed since the last upload, so they fetch them within hours instead of waiting for
   their next crawl. Google does not take part; it reads the sitemap submitted once in Search Console.

   What counts as changed: an address new in the sitemap, a page whose plain-text copy (index.md) differs from the last upload, a page
   whose <lastmod> changed, and any new PDF. Or, with --urls, exactly the addresses in an update package's CHANGED-URLS.txt.

   Usage:   node tools/indexnow.js <build folder> [--all] [--dry] [--urls CHANGED-URLS.txt]
            run it once the host has confirmed the package is live (the engines fetch the addresses straight away)
   State:   deploy/indexnow-state.json in the repository (never uploaded). Without it, the first run sends every address.
   Needs:   Node 18 or later and a connection to api.indexnow.org. */
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const args = process.argv.slice(2), OUT = args.find((a, i) => !a.startsWith('--') && args[i - 1] !== '--urls');
const ALL = args.includes('--all'), DRY = args.includes('--dry'), LIST = args.includes('--urls') ? args[args.indexOf('--urls') + 1] : '';
if (!OUT) { console.error('usage: node tools/indexnow.js <build folder> [--all] [--dry] [--urls CHANGED-URLS.txt]'); process.exit(2); }
const read = f => { try { return fs.readFileSync(path.join(OUT, f), 'utf8'); } catch (e) { return null; } };
const sm = read('sitemap.xml'); if (!sm) { console.error('no sitemap.xml in ' + OUT); process.exit(2); }
const keyFile = fs.readdirSync(OUT).find(f => /^[0-9a-f]{32}\.txt$/i.test(f)); if (!keyFile) { console.error('no IndexNow key file in ' + OUT); process.exit(2); }
const key = keyFile.slice(0, -4); if ((read(keyFile) || '').trim() !== key) { console.error('the key file does not hold its own key'); process.exit(2); }
const urls = [...sm.matchAll(/<url>([\s\S]*?)<\/url>/g)].map(m => {
  const loc = ((/<loc>([^<]+)<\/loc>/.exec(m[1]) || [])[1] || '').replace(/&amp;/g, '&'), lastmod = (/<lastmod>([^<]+)<\/lastmod>/.exec(m[1]) || [])[1] || '';
  let md = ''; try { const u = new URL(loc); if (u.pathname.endsWith('/')) { const t = read(path.join(u.pathname, 'index.md')); if (t) md = crypto.createHash('sha256').update(t).digest('hex').slice(0, 16); } } catch (e) {}
  return { loc, lastmod, md }; }).filter(x => x.loc);
if (!urls.length) { console.error('the sitemap lists no addresses'); process.exit(2); }
const host = new URL(urls[0].loc).hostname, origin = new URL(urls[0].loc).origin;
const STATE = path.join(__dirname, '..', 'deploy', 'indexnow-state.json');
let prev = {}; try { prev = JSON.parse(fs.readFileSync(STATE, 'utf8')); } catch (e) {}
const changed = LIST ? fs.readFileSync(LIST, 'utf8').split(/\r?\n/).map(s => s.trim()).filter(s => s.startsWith(origin + '/'))
  : ALL || !Object.keys(prev).length ? urls.map(x => x.loc)
  : urls.filter(x => !prev[x.loc] || prev[x.loc].lastmod !== x.lastmod || (x.md && prev[x.loc].md !== x.md)).map(x => x.loc);
(async () => {
  console.log(`${changed.length} of ${urls.length} addresses to send for ${host}${ALL ? ' (all)' : ''}`);
  changed.slice(0, 30).forEach(u => console.log('  ' + u)); if (changed.length > 30) console.log(`  … and ${changed.length - 30} more`);
  if (DRY || !changed.length) return;
  for (let i = 0; i < changed.length; i += 10000) {
    const body = { host, key, keyLocation: `${origin}/${keyFile}`, urlList: changed.slice(i, i + 10000) };
    const r = await fetch('https://api.indexnow.org/indexnow', { method: 'POST', headers: { 'content-type': 'application/json; charset=utf-8' }, body: JSON.stringify(body) });
    console.log(`IndexNow answered ${r.status} ${r.statusText} for ${body.urlList.length} addresses`);   // 200/202 received; 403 key not found; 422 wrong host; 429 too many
    if (r.status >= 400) { console.error('nothing recorded: fix the cause above and run again'); process.exit(1); }
  }
  fs.mkdirSync(path.dirname(STATE), { recursive: true });
  fs.writeFileSync(STATE, JSON.stringify(Object.fromEntries(urls.map(x => [x.loc, { lastmod: x.lastmod, md: x.md }])), null, 1));
  console.log('state kept in ' + path.relative(process.cwd(), STATE));
})().catch(e => { console.error(e); process.exit(1); });
