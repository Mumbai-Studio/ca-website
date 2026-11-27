# Live patch 2026-11-26-ahrefs1: Ahrefs site audit fixes and the logo size on phones

On top of 2026-11-26-sectors1, which carries seo4, seo3 and bing1; none of them uploaded yet, so the host uploads this one only.
Built with `tools/patches/make_patch_ahrefs1.py` from the sectors1 full site; the code changes are mirrored in
`src/ca-website.html` and `tools/design-snippet/build_page.py` in this commit.

## Ahrefs Site Audit, 26 November 2026 (crawl 05:55 UTC, health score 93, 16 issues)

Review report: "Ahrefs Site Audit, 26 November 2026: fixes for review" (claude.ai doc). Mujib approved the fixes on 26 November
and left out the five optional choices (Home description, two titles, extra links to Total Design and the Design Snippet, Madinah
and Makkah).

- **Fixed here:** "Structured data has schema.org validation error" on /awards/ and /work/peace-pavilion/. The organizer of each
  Designing Peace exhibition was typed Museum; schema.org allows Organization or Person, so it is now Organization. The museum
  stays a Museum as the location. The live pages' structured data differs from a fresh render elsewhere (Organization
  areaServed), so the change is a targeted substitution, and the render comparison proves it is the only difference.
- **Fixed by the waiting upload:** long titles and the Design Snippet description (seo4), the eight orphaned Gulf city pages
  (seo3), the Lab strands with one incoming link (seo4 canonical), the Reflected Topography title Google rewrote (seo4).
- **Host:** slow pages and slow responses to AI crawlers (first byte 0.8 to 1.9 s from the origin): the Cloudflare Cache Rule,
  step 6 of README-HOST.
- **Kept, by design:** noindex on Privacy; the http/www redirects and the chain (Cloudflare upgrades to HTTPS before redirect
  rules run); Article schema on two service pages; the 28 full-size photographs (studio standard WebP q85 up to 2,880 px; a q80
  test on the live files saved about 16% and left 15 still flagged); the stylesheet size.

## The logo on phones

Mujib, 26 November 2026, with a marked phone screenshot: "The logo is of different sizes on the footer and home pages. Follow the
footer size and proportions throughout the site for mobile and handheld formats; they are perfect on desktop." He chose option A
from a rendered comparison.

- Up to 700 px wide, the header logo takes the footer logo's size and proportions: a 64 px mark (was 54 at the top of a page and
  48 once the bar turns solid), 14 px gap, the name at line height 1.1 and normal letter spacing. The bar grows from 72 px (68 when
  solid) to 84 px in both states, so the logo keeps its breathing room; page content starts 12 px lower.
- The rule is appended at the end of the stylesheet, after every earlier `.brand` and `--hdr` rule. Script offsets read the
  header's actual height, so scrolling to sections adapts on its own.
- The Design Snippet page's own header does the same on phones and now shows the studio's name.
- Tablets and laptops are unchanged: the laptop header was compared pixel for pixel before and after.

## Checks

- Every page rendered with the sectors1 and the patched scripts: only Awards and Peace Pavilion change in content.
- All scripts parse. No script errors on the changed pages, Home, Studio, Contact, The Barn, a sector page and the Design Snippet
  page, on a phone and a laptop. Header hide-on-scroll, the solid bar and the phone menu behave as before.
- Speed: one CSS rule (about 200 bytes) and one changed word in the search module; no picture, script or animation changes.
