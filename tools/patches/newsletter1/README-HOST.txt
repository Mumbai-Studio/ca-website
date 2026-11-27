Collaborative Architecture website, patch 2026-11-27-newsletter1: the newsletter's Mailchimp connection and Cloudflare's check
on the server

Two files only, both in api/. No page, script, style or picture changes, and nothing outside api/. This patch is independent of
patch 2026-11-26-gsc1 (that one does not touch api/); they can go up in either order.

1. Upload the two files in upload/api/ to the site's api/ folder (for example public_html/api/), overwriting the ones there:
     api/mailchimp.php   (the Mailchimp API key, the audience and press@'s app password for the sign-up emails)
     api/security.php    (the Cloudflare Turnstile secret key)
   The studio has pasted three secret values into them. Do not open them in a shared screen and do not keep copies elsewhere.
   Do not change api/config.php, the other api/ files or the _private/ folder.

2. Check that both answer 403 (Forbidden) in a browser:
     https://collaborativearchitecture.com/api/mailchimp.php
     https://collaborativearchitecture.com/api/security.php

3. Test in a normal browser (a private window), with the console open (F12):
   - https://collaborativearchitecture.com/lab/newsletters/ : enter a spare address you can read, tick the Cloudflare box if it
     shows, and press "Subscribe to the Newsletter". The panel must answer:
       "Thank you. Please check your inbox and confirm your subscription."
     A confirmation email from Mailchimp arrives at that address within a few minutes, and newsletter@ (delivered to press@)
     receives "Newsletter sign-up · <the address>" saying that Mailchimp has added it.
     If the panel answers "Thank you. You will receive the next edition." instead, Mailchimp refused the sign-up: open the
     server's PHP error log, find the line that starts "CA subscribe: Mailchimp answered", and send it to the studio.
     If it answers "The security check did not pass", the secret key is not from the same Turnstile widget as the site key.
   - https://collaborativearchitecture.com/contact/ : send one test inquiry and check that it reaches enquiry@.

4. Reply to the studio that patch 2026-11-27-newsletter1 is on the server. The studio then runs its own checks.
