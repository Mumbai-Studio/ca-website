# Patch 2026-11-27-newsletter1: Mailchimp and Cloudflare on the server

## Found on the live site (27 November 2026)

- A test sign-up (press@) sent with no Cloudflare token was accepted with `{"ok":true,"pending":false}`.
  `pending:false` is the fallback path: Mailchimp did not take the address, the sign-up was only emailed to newsletter@.
- The 21 Nov patch's api/mailchimp.php had `api_key` and `mail_pass` empty, and api/security.php had `turnstile_secret` empty
  (the README said the studio had filled them in). The live answers match: the server skips the Turnstile check when the
  secret is empty, and without a key subscribe.php never calls Mailchimp.
- The page side works: site-config.js carries the Turnstile site key and the widget renders under the email field.

## The patch

The same two files (api/mailchimp.php, api/security.php) with every non-secret value kept, `double_opt_in => true` written out,
and the three lines to fill marked 1, 2 and 3. The studio pastes the three values, then sends the folder to the host privately.
The files themselves are not in this repository (they hold the audience ID and, once filled, the keys); the instructions are in
tools/patches/newsletter1/. No code change: subscribe.php and lib.php are those of 21 November.

## Tests (PHP 8.3, the 21 Nov subscribe.php and lib.php, the new files)

- As shipped (all empty): same as live today, the fallback email path.
- Secret filled, no token: 400 "Please complete the security check." Fake token: 400 "The security check did not pass."
- Key filled: subscribe.php calls https://us3.api.mailchimp.com/3.0/lists/<audience>/members/... (no network in the test box,
  so it logged "CA subscribe: Mailchimp answered 0" and fell back, as designed).
- api/mailchimp.php and api/security.php answer 403 under Apache with the api/.htaccess rules.

## After the upload

Live checks: a POST without a Cloudflare token must answer 400; a real sign-up in a normal browser must answer
"Please check your inbox and confirm" and bring Mailchimp's confirmation email.
