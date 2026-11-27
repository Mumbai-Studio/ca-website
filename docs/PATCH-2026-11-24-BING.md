# Live patch 2026-11-24-bing1: Bing Webmaster Tools verification

One new file, `BingSiteAuth.xml`, at the site's root (`public/BingSiteAuth.xml`). It proves to Bing Webmaster Tools that the
studio owns collaborativearchitecture.com, which opens Bing's and Copilot's reports (search performance, AI Performance,
crawl and index checks) and lets the studio submit the sitemap there. It changes no page and nothing visible, and it does
not depend on patch 2026-11-24-seo3: it can go up before, with or after it. `version.txt` is left as it is.

The file must stay on the site for as long as the studio uses Bing Webmaster Tools; Bing re-checks it.

Checked on the live site on 24 November 2026 (version 2026-11-23-snippet3):

- robots.txt allows Bingbot, Applebot and Applebot-Extended by name; only `/admin/` is closed.
- The copy-protection check at the top of each page lets Applebot, bingbot, BingPreview and MicrosoftPreview through, and
  still stops a hidden (headless) browser. The server rules use the same list, and `.xml` files are open to every reader.
- The IndexNow key file answers 200. Patch seo3, step 7, submits the changed addresses.
- Apple has no webmaster account to connect: Applebot reads robots.txt, and Applebot-Extended (use for training) is allowed,
  as the studio decided on 21 October 2026. The studios' Apple Maps listings are claimed separately, in Apple Business Connect.

After the upload, in Bing Webmaster Tools: Verify, then Sitemaps > Submit `https://collaborativearchitecture.com/sitemap.xml`.
