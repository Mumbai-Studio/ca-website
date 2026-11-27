Collaborative Architecture website, patch 2026-11-26-ahrefs1: fixes from the Ahrefs site audit and the logo size on phones, together
with the sector pages under Expertise, the practice in figures on the Studio page, the 2026 UltraTech IndiaNext Innovation Awards and
the enhanced 50th Cross Road films.

This patch goes on top of version 2026-11-23-snippet1 / snippet3, which is live now. It INCLUDES patch 2026-11-26-sectors1, patch
2026-11-25-seo4, patch 2026-11-24-seo3 and patch 2026-11-24-bing1, so upload this one only and discard those. It replaces or adds files only. No .htaccess,
_headers, nginx.conf or api/ file is in it, and the security policy stays as it is.

1. Upload the CONTENTS of the folder "upload" to the site's web folder (for example public_html/), keeping the folders and
   overwriting the existing files. It holds every page, six new pages in expertise/ (each with its index.md), the Markdown copies
   that changed, seven new files in assets/, three new pictures in img/uae/, five new film files in vid/, sitemap.xml, llms.txt,
   llms-full.txt, the feeds, the Design Snippet page and PDF, version.txt and one file at the root: BingSiteAuth.xml.

2. Do not upload anything into api/ and do not replace site-config.js: they hold the studio's keys. One change is asked of you
   in site-config.js (step 4).

3. In Cloudflare, purge the cache after the upload: Caching > Configuration > Purge Cache > Purge Everything.

4. site-config.js (from patch seo4, if not done yet): minify it in place without changing what it holds (keep a copy of the
   original), for example
     npx terser site-config.js --compress --format comments=false -o site-config.min.js
   check that the contact form and the newsletter form still send, then put it in place under the name site-config.js.

5. Cloudflare and AI search (from patch seo4, if not done yet): under Security > Bots (and AI Crawl Control, where the account has
   it), make sure "Block AI bots" is off and that GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot and
   Bingbot are allowed.

6. Cache the pages at Cloudflare's edge (from patch seo4, if not done yet). In Cloudflare add
     Caching > Cache Rules > Create rule
       When:  Hostname equals collaborativearchitecture.com
              AND URI Path does not start with /api/
              AND URI Path does not start with /admin
       Then:  Eligible for cache; Edge TTL: ignore cache-control header, 4 hours; Browser TTL: respect origin
              (keep "Serve stale content while revalidating" on)
   Do not cache /api/ (the forms). After every later upload, Purge Everything as in step 3.
   Check: open https://collaborativearchitecture.com/contact/ twice; the response header cf-cache-status reads HIT the second time.
   Then send the contact form once as a test, to confirm the forms still work.

7. Check:
   - https://collaborativearchitecture.com/version.txt shows: version 2026-11-26-ahrefs1
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
   - All the checks of patches seo4 and seo3 still apply.

8. Tell Bing and the other IndexNow search engines about the changed pages: submit the addresses in indexnow-urls.txt with the
   site's IndexNow key (the same way as at launch).

9. Optional, one day later: delete the unused files listed in DELETE.txt (a file in that list that is not on the server can be
   skipped). Keep the old 50th Cross Road films (vid/cross50-film.mp4 and the others without "-r2"): search engines have indexed
   their addresses, and links shared earlier may still point at them.

10. Reply to the studio that version 2026-11-26-ahrefs1 is live. The studio then completes the Bing verification and runs the
    audits again.


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
