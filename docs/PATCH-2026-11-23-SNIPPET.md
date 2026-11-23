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

# Live patch 2026-11-23-snippet3: three levels, Related projects, the opening logo

On top of 2026-11-23-snippet1. It replaces snippet2, which was built but never uploaded. Built from the live text copy with
`make_patch_snippet3.py`; the changes are mirrored here.

- **Design Snippet in three levels** (`public/design-snippet/`, built with `tools/design-snippet/build_page.py`): the opening pages are
  the same for everyone, then an Index, then the exercises by level: 01 Interns (The Rods, The Screen), 02 Junior Architects (The Kit,
  The Field), 03 Advanced (The Canopy, The Facade). One 12-page A4 PDF, printed from the page's own print styles; the studio logo is in
  the PDF only (cover, beside each page number, back cover). The Index, the cover's list and the level cards link to their sections in
  the PDF too. "No more." is gone from the word counts. Share picture `img/share/design-snippet-levels.jpg` (a new name: pictures are
  cached for 30 days).
- **Related projects:** a project with no page and no picture (Infold House, Linked House, Topography) drew a blank box; `stubCard`
  now leaves it out, and the two project pages' built HTML lost those cards.
- **Opening logo** (Mujib: since logo1 the line under the T stood still on desktop too, and the logo stood still on his phone):
  - the line draws down by growing its height again, exactly as before logo1. Logo1 scaled a full-length line up from zero; some
    graphics cards show such a line only once it has finished, so it appeared at full length without moving;
  - the device's reduce-motion setting no longer stops the logo's rise, its line or the screen's exit (Mujib, 5 November 2026: that
    setting stops only the slow zoom, the parallax and smooth scrolling). With it on, a phone showed the logo standing still with no line
    (before logo1) or a full-length line (after);
  - `load.js`: on the first page of a visit the scripts are preloaded at the usual moment but run only once the line has been drawn
    (2.35 s after the logo picture arrives, 3 s at the latest), so neither a busy phone nor a desktop holds the animation back
    (`tools/build.js`). The shortest hold after the scripts is now 0.25 s (was 0.6 s): on a desktop the logo still leaves at 3.25 s; on
    a slow phone it no longer waits an extra half second.
