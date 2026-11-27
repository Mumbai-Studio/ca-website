<?php
/* Collaborative Architecture · the Google mailboxes that send the website's emails (27 November 2026, patch mail1)

   Copy this file to mail.php in the same folder (api/) ON THE SERVER; never commit mail.php.
   Every form email goes out through Google with an app password, so it lands in the studio's Google mailboxes. Nothing has to be
   filled in here for the forms to work: a mailbox without its own app password sends through the fallback account, which is
   press@ with the app password already in mailchimp.php.
   - accounts: optional. A mailbox's own app password, if that mailbox should send its own form emails (signed in to Google as that
     mailbox: 2-Step Verification on, then myaccount.google.com/apppasswords). Aliases and groups cannot have one; leave them empty.
   - check_key: the key for api/mail-check.php (any 32 or more random letters and digits).
   This file is closed to the web (api/.htaccess) and answers 403 if it is ever opened directly. */

if (realpath((string) ($_SERVER['SCRIPT_FILENAME'] ?? '')) === __FILE__) { http_response_code(403); exit; }

return [
    'accounts' => [
        'enquiry@collaborativearchitecture.com' => '',   // Contact form: Client, Consultants, Research
        'studio@collaborativearchitecture.com'  => '',   // Contact form: Career
        'vendors@collaborativearchitecture.com' => '',   // Contact form: Vendors
    ],
    'fallback_user' => '',   // empty: press@, with the app password in mailchimp.php
    'fallback_pass' => '',
    'check_key'     => '',
];
