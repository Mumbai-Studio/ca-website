<?php
/* Collaborative Architecture · Mailchimp for the newsletter form (21 November 2026)

   Copy this file to mailchimp.php in the same folder (api/) ON THE SERVER and fill in the two values; never commit mailchimp.php.
   - api_key: in Mailchimp, profile picture > Profile > Extras > API keys > Create A Key (name it "Website").
              Mailchimp shows it once. It ends in something like -us21.
   - list_id: in Mailchimp, Audience > All contacts > Settings > Audience name and defaults > Audience ID (for example a1b2c3d4e5).
   The key opens the whole Mailchimp account: send this file privately, never post it anywhere.
   This file is closed to the web (api/.htaccess) and answers 403 if it is ever opened directly. */

if (realpath((string) ($_SERVER['SCRIPT_FILENAME'] ?? '')) === __FILE__) { http_response_code(403); exit; }

return [
    'api_key' => '',
    'list_id' => '',
    'tag'     => 'Website',   // every sign-up from the site gets this tag in Mailchimp; '' = no tag
];
