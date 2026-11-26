# Live patch 2026-11-26-sectors1: sector pages, the practice in figures, 2026 awards, enhanced 50th Cross Road films

On top of 2026-11-23-snippet1. It carries seo4 (with seo3 and bing1), none of which was uploaded, so the host uploads this one only.
Built from the seo4 full site in two stages: `tools/patches/make_patch_sectors1.py` (scripts, stylesheet, data, media) and
`tools/patches/pages_sectors1.py` (pages, Markdown copies, search files, upload folder). The code and data changes are mirrored in
`src/ca-website.html` in this commit.

Source: Mujib's marked review of 25 November 2026 ("Sector Expertise, AI crawl" and "Pages for review" PDFs) and the approved draft
of 26 November 2026. His instructions: keep the live Expertise section as it is (structure and wording), add the sector pages after
it as sectoral expertise, add Hospitality and Educational, take every picture from the studio's folders, and do not alter anything
else, page speed and animations included.

## What changes

- **Six sector pages** at `/expertise/<sector>/`: Workplace and Research, Residential, Civic and Cultural, Hospitality, Educational,
  Real Estate and Developers. Each has its introduction, jump links, a quote where there is one (Domus, Cooper Hewitt curatorial
  note, Domus), every project in the sector, four perspectives, the press on those projects and the other sectors. Data in
  `C.sectors` (`tools/patches/sectors1/sectors.min.js`, readable in the source). Search: CollectionPage with a Service and an
  ItemList of the projects, titles within 60 characters, descriptions of 144 to 159.
- **Expertise page and Home:** "Sectoral expertise" below the six disciplines, in the same rows. The disciplines are unchanged.
- **Studio:** "The practice in figures" and "Selected honors" (`C.studioFigures`, `C.studioHonors`), above Key facts. The Home
  "Recognized internationally" list (`C.honors`) is untouched.
- **Awards register, The Iconic Gateway, Project Alpha:** 2026, shortlisted and longlisted, UltraTech IndiaNext Innovation Awards.
  The projects' `honors` counts are left as they were, so the Work filters do not change.
- **The Barn:** Area 510 m², Scope, and a Sector row linking to Workplace and Research.
- **50th Cross Road:** the studio's enhanced films (Cleaned folder, 3 November 2026) replace the 1 November encodes. They were
  remuxed without re-encoding (`-c copy -map_metadata -1 -movflags +faststart`, content credentials removed), and published as
  `vid/cross50-film-r2.mp4`, `vid/cross50-teaser-r2-1080.mp4`, `vid/cross50-teaser-r2-720.mp4` with their posters, under new
  names because films are cached for 30 days. `C.f0` maps the teaser to its own first frame.
- **The Measured City:** View 2 from the studio's folder as `img/uae/p06` (2880, 1280 and 800 wide, sRGB, no metadata), for its
  card on Civic and Cultural. Sandy Hook's card there uses `p01r2`, the picture the Work page shows.

## How the pages were made

The repository cannot rebuild the site (`tools/build.js` is behind the live pages, and 229 pictures are not in the repo), so the
patch edits the live minified bundles with exact substitutions, each checked to match once, and gives them new hashed names.

The live static pages went through a step after the prerender that is not in the repository. Its rules were read off the live
pages and are in `tools/patches/sectors1/render.py`: lazy pictures inside `<noscript>` with the full-size file, thumbnail spans
left for the scripts, the font block at the end of the head. With them, renders of the six discipline pages match the live files
byte for byte (apart from the per-render seed), so the six new pages have exactly the form of their siblings.

Every page was rendered with the seo4 scripts and with the patched ones (fixed random seed, so Home's picture order is the same in
both). Pages whose renders are identical are left as they are live, except the loader and stylesheet addresses. For the pages that
change, only the differences between the two renders were carried onto the live file. The Markdown copies, sitemap and llms files
were handled the same way, line by line.

## Checks

- All bundles parse (`node --check`). No script errors on the new and changed pages, desktop and phone.
- Animations and speed: no change to existing code paths. New styles are new classes only; the new pages use the existing
  picture loader and hover. The extra data is about 17 KB in the content bundle.
