# Live patch 2026-11-23-snippet1: the Design Snippet page and PDF

On top of 2026-11-23-seo2, and carries 2026-11-23-logo1 (opening logo line on phones, gentler swipe on Home). Built from the
live text copy with `make_patch_snippet.py`; the changes are mirrored here.

- **New page `/design-snippet/`** (`public/design-snippet/`): the studio's design challenge for career and internship applicants,
  The Kit and The Field, in crimson, marigold and the greys. A standalone page with no scripts (the security policy is unchanged),
  a fixed PDF mark at the bottom right of the screen on this page only, and the same content as a 4-page A4 PDF
  (`Collaborative-Architecture-Design-Snippet.pdf`), printed from the page's own print styles. The only address on it is
  studio@collaborativearchitecture.com. Built with `tools/design-snippet/build_page.py`.
- **Studio, Careers:** "Design-Snippet" links to the page (`target="_self"`, so the site's own navigation does not try to draw it);
  `/studio/#careers` opens at the Careers section.
- **Search:** sitemap.xml and llms.txt name the page (edited by hand on the live copy, as in the SEO patch). Share picture
  `img/share/design-snippet.jpg`.

# Live patch 2026-11-23-snippet2: three levels, Related projects, the opening logo on phones

On top of 2026-11-23-snippet1. Built from the live text copy; the changes are mirrored here.

- **Design Snippet in three levels** (`public/design-snippet/`, built with `tools/design-snippet/build_page.py`): the opening pages are
  the same for everyone, then an Index, then the exercises by level: 01 Interns (The Rods, The Screen), 02 Junior Architects (The Kit,
  The Field), 03 Advanced (The Canopy, The Facade). One 12-page A4 PDF, printed from the page's own print styles; the studio logo is in
  the PDF only (cover, beside each page number, back cover). The Index, the cover's list and the level cards link to their sections in
  the PDF too. Share picture `img/share/design-snippet-levels.jpg` (a new name: pictures are cached for 30 days).
- **Related projects:** a project with no page and no picture (Infold House, Linked House, Topography) drew a blank box; `stubCard`
  now leaves it out, and the two project pages' built HTML lost those cards.
- **Opening logo on phones:**
  - the device's reduce-motion setting no longer stops the logo's rise, its line or the screen's exit (Mujib, 5 November 2026: that
    setting stops only the slow zoom, the parallax and smooth scrolling); with it on, the logo stood still and the line showed at full
    length;
  - the logo picture is on its own layer before it moves (`will-change`);
  - `load.js`: on the first page of a visit the scripts are preloaded at the usual moment but run only once the logo has started moving
    (`ca-pl-ready`, 1.6 s at the latest), so a busy phone cannot hold the animation back (`tools/build.js`).
