# Live patch 2026-11-27-forms1: one package with the forms' email, Career on the Contact page, gsc1 and ahrefs1

On top of whatever is live (2026-11-26-sectors1 on 27 Nov). Includes mail1, gsc1, ahrefs1, sectors1, seo4, seo3 and bing1.
Patch newsletter1 (api/mailchimp.php, api/security.php, with the studio's keys) stays a separate, private upload.

## Career on the Contact page (Mujib, 27 November 2026; draft reviewed and approved the same day)

"For Career, instead of the fill-up form, just show the email studio@ hyperlinked, preceded by the note mentioned in the Studio
section, with the Design Snippet link. For the rest, keep the fill-up forms."

- When Career is chosen, the form's fields, security check and Send button are hidden; the type menu stays at the top, then the
  careers note (C.careers, with "email a portfolio" for "select Career in the contact form and submit a portfolio") with its
  Design-Snippet link, then studio@collaborativearchitecture.com as a mailto link.
- Built at run time (careerPanel in src/ca-website.html; caCr in site-7), so no page's HTML changes. The Studio page is unchanged;
  its "Apply through the contact form" button opens the Career view.
- site-7 +661 bytes (+175 gzip), site-1 +415 bytes (+126 gzip). Every page rendered with the old and new scripts: no render
  differs (after one re-render of pages that differed by timing); the pages differ only in the loader and stylesheet names.
- Checked in Chrome at 1440 and 390 px: Career shows the type menu and the panel only; Vendors brings the form back; the Studio
  button lands on Career; no script error.

## Package

tools/patches/make_patch_forms1.py builds it from the ahrefs1 site copy, the gsc1 package and the mail1 api files.
nginx.conf: mail and mail.sample denied, mail-check passed to PHP. DELETE adds the replaced site-1, site-7 and load.
