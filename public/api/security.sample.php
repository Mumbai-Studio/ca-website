<?php
/* Collaborative Architecture · the Cloudflare Turnstile security check on the inquiry and newsletter forms (21 November 2026)

   Copy this file to security.php in the same folder (api/) ON THE SERVER and paste the widget's SECRET key; never commit security.php.
   Cloudflare dashboard > Turnstile > the collaborativearchitecture.com widget > Settings: "Secret Key".
   (The public Site Key goes in site-config.js; the patch already carries it.)
   Leave it empty and the forms rely on their own checks, as before. Never post this key anywhere.
   This file is closed to the web (api/.htaccess) and answers 403 if it is ever opened directly. */

if (realpath((string) ($_SERVER['SCRIPT_FILENAME'] ?? '')) === __FILE__) { http_response_code(403); exit; }

return [
    'turnstile_secret' => '',
];
