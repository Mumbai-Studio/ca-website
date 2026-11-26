Collaborative Architecture website, patch 2026-11-26-gsc1: fixes for Google Search Console's Pages report (old addresses
and the news feeds), together with everything in patch 2026-11-26-ahrefs1 (the Ahrefs fixes, the logo size on phones, the sector
pages under Expertise, the practice in figures, the 2026 awards and the enhanced 50th Cross Road films).

This patch goes on top of whatever is live now: 2026-11-26-sectors1 (live today) or 2026-11-26-ahrefs1 if that was uploaded. It
INCLUDES patch 2026-11-26-ahrefs1 (and so sectors1, seo4, seo3 and bing1), so upload this one only and discard ahrefs1. The pages,
scripts, styles, pictures and films are exactly those of ahrefs1: only version.txt and the three server files below are new.

1. Upload the CONTENTS of the folder "upload" to the site's web folder (for example public_html/), keeping the folders and
   overwriting the existing files. Besides the ahrefs1 files it holds three server files:
     .htaccess    (a hidden file: in cPanel's File Manager, turn on Settings > Show hidden files)
     _headers
     _redirects
   They are the files now on the server (from patch 2026-11-23-seo2) with a few lines added; the security policy is unchanged.
   Before you overwrite .htaccess: open the one on the server. If it has a block that begins
     # php -- BEGIN cPanel-generated handler, do not edit
   (cPanel writes it when the PHP version is set), copy that block, from BEGIN to END, to the end of the new .htaccess, or set
   the PHP version again in cPanel > MultiPHP Manager after the upload. Nothing else in the old file needs keeping.
   README-HOST.txt, DELETE.txt, indexnow-urls.txt and nginx.conf are not for the web folder.

2. Do not upload anything into api/ and do not replace site-config.js: they hold the studio's keys. One change is asked of you
   in site-config.js (step 5).

3. nginx servers only: replace the server's nginx.conf with the nginx.conf in this zip (set root, the certificate lines and the
   PHP socket as before), then run  nginx -t && systemctl reload nginx

4. In Cloudflare, purge the cache after the upload: Caching > Configuration > Purge Cache > Purge Everything.

5. site-config.js (from patch seo4, if not done yet): minify it in place without changing what it holds (keep a copy of the
   original), for example
     npx terser site-config.js --compress --format comments=false -o site-config.min.js
   check that the contact form and the newsletter form still send, then put it in place under the name site-config.js.

6. Cloudflare and AI search (from patch seo4, if not done yet): under Security > Bots (and AI Crawl Control, where the account has
   it), make sure "Block AI bots" is off and that GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot and
   Bingbot are allowed.

7. Cache the pages at Cloudflare's edge (from patch seo4, if not done yet). In Cloudflare add
     Caching > Cache Rules > Create rule
       When:  Hostname equals collaborativearchitecture.com
              AND URI Path does not start with /api/
              AND URI Path does not start with /admin
       Then:  Eligible for cache; Edge TTL: ignore cache-control header, 4 hours; Browser TTL: respect origin
              (keep "Serve stale content while revalidating" on)
   Do not cache /api/ (the forms). After every later upload, Purge Everything as in step 4.
   Check: open https://collaborativearchitecture.com/contact/ twice; the response header cf-cache-status reads HIT the second time.
   Then send the contact form once as a test, to confirm the forms still work.

8. Check:
   - https://collaborativearchitecture.com/version.txt shows: version 2026-11-26-gsc1
   - The new rules (open each address in a browser; the address bar shows where it lands):
       https://collaborativearchitecture.com/news/press/feeds/press.xml   lands on /feeds/press.xml
       https://collaborativearchitecture.com/en/                          lands on the home page
       https://collaborativearchitecture.com/portfolio/                   lands on /work/
       https://collaborativearchitecture.com/wp-content/uploads/2020/12/2015-JUL-FX.pdf   opens the FX (UK) feature, July 2015,
                                                                          at /press/features/2015-07-fx-reflected-topography.pdf
       https://collaborativearchitecture.com/?s=test                      lands on the home page, without "?s=test"
   - The feeds carry a header for search engines. In a terminal:
       curl -sI https://collaborativearchitecture.com/feeds/news.xml | grep -i x-robots
     prints  x-robots-tag: noindex, follow   (a page such as https://collaborativearchitecture.com/work/ prints nothing).
   - Unchanged: https://collaborativearchitecture.com/elements/counters/ answers 410 (gone), https://collaborativearchitecture.com/abc/
     answers 404, https://collaborativearchitecture.com/portfolio-item/bamboo/ lands on /work/, and http://www. addresses still
     go to https://collaborativearchitecture.com/.
   - https://collaborativearchitecture.com/expertise/ shows the six disciplines as before and, below them, "Sectoral expertise"
     with six sectors: Workplace and Research, Residential, Civic and Cultural, Hospitality, Educational, Real Estate and
     Developers. Each opens its own page, for example https://collaborativearchitecture.com/expertise/hospitality/
   - The home page shows the same six sectors below the six disciplines in its Expertise block.
   - https://collaborativearchitecture.com/studio/ has "The practice in figures" and "Selected honors" above Key facts.
   - https://collaborativearchitecture.com/awards/ opens with 2026: The Iconic Gateway, shortlisted, and Project Alpha,
     longlisted, UltraTech IndiaNext Innovation Awards.
   - https://collaborativearchitecture.com/work/50th-cross-road/ : the walkthrough film plays (it is the studio's enhanced film).
   - On a phone, the logo at the top of every page is the same size as the logo in the footer, also after scrolling, and on the
     Design Snippet page it shows with the studio's name. On a laptop the header looks exactly as before.
   - https://collaborativearchitecture.com/BingSiteAuth.xml opens (status 200, no redirect, no security check in front of it).
     Keep this file on the site; a later full upload must not remove it.
   - Open the home page and one sector page with the browser console open (F12). They may not show a red error.
   - Open the home page and one sector page with the browser console open (F12). They may not show a red error.
   - All the checks of patches seo4 and seo3 still apply.

9. Tell Bing and the other IndexNow search engines about the changed pages and addresses: submit the addresses in
   indexnow-urls.txt with the site's IndexNow key (the same way as at launch).

10. Optional, one day later: delete the unused files listed in DELETE.txt (a file in that list that is not on the server can be
    skipped). Keep the old 50th Cross Road films (vid/cross50-film.mp4 and the others without "-r2"): search engines have indexed
    their addresses, and links shared earlier may still point at them.

11. Reply to the studio that version 2026-11-26-gsc1 is live. The studio then checks Search Console and completes the Bing
    verification.


What gsc1 adds to ahrefs1 (for the record). Server rules only; no page, script, style or picture changes.
- Feed addresses that an earlier page linked without the leading slash (/news/press/feeds/press.xml and the same for logs, news
  and projects) now move permanently (301) to /feeds/...; Search Console listed three of them as Not found.
- /en/ moves to the home page and /portfolio/ to /work/ (both were Not found or gone).
- Four press features that the old WordPress site kept under /wp-content/uploads/ move to the same features on this site:
  MGS Architecture, August 2020 (Designing Peace); Architecture + Design, February 2019; Inside Outside, July 2016 (interview
  with the principals); FX (UK), July 2015. The other old WordPress files stay gone (410).
- The old WordPress search: /search/... answers 410 (gone), and the home page with ?s=... moves to the home page without it.
- The RSS feeds (/feeds/) send "X-Robots-Tag: noindex, follow": feed readers and search engines still read them, but search
  engines do not list the feed files themselves as pages.
- .htaccess (Apache, LiteSpeed), _redirects and _headers (Netlify, Cloudflare Pages) and nginx.conf carry the same rules.

What ahrefs1 adds to sectors1 (for the record).
- Structured data: on the Awards and Peace Pavilion pages, the organizer of each Designing Peace exhibition is typed Organization,
  as schema.org requires (it said Museum). Ahrefs reported this as an error on those two pages.
- The logo on phones (up to 700 px wide): the header logo takes the footer logo's size and proportions, also when the bar turns
  solid on scroll, and the header bar grows from 72 px to 84 px to hold it. The Design Snippet page's header does the same. Tablets
  and laptops are unchanged.

What sectors1 adds to seo4 (for the record).
- Six sector pages under Expertise, at /expertise/workplace-and-research/, /expertise/residential/, /expertise/civic-and-cultural/,
  /expertise/hospitality/, /expertise/educational/ and /expertise/real-estate-and-developers/. Each has its introduction, its
  projects, four perspectives, the press on those projects and links to the other sectors. They are listed below the disciplines
  on the Expertise page and on the home page; the disciplines and their wording are unchanged.
- Studio: the practice in figures (2004, 2 studios, 6 disciplines, 60 awards, 30 international, 150+ publications) and selected
  honors, above Key facts.
- Awards, The Iconic Gateway and Project Alpha: 2026, shortlisted and longlisted for the UltraTech IndiaNext Innovation Awards.
- The Barn: its area (510 m²), scope and sector in the fact panel.
- 50th Cross Road: the studio's enhanced walkthrough film and teaser replace the earlier encodes, under new file names ending in "-r2", so
  that browsers and Cloudflare do not keep serving the old films from their caches.
- The Measured City: a new picture for its card on the Civic and Cultural page.
- sitemap.xml, llms.txt, llms-full.txt and the Markdown copies list the new pages. Nothing else on the site changes: every other
  page differs only in the address of its script loader and stylesheet.
