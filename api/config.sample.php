<?php
/* Collaborative Architecture · settings of the form handlers
   Copy this file to config.php in the same folder (api/) ON THE SERVER, fill it in, and never commit config.php to the repository:
   it holds passwords. Anything left out keeps the default written in lib.php. */

return [
    // the addresses the site is served from; forms sent from anywhere else are refused
    'allowed_hosts' => ['collaborativearchitecture.com', 'www.collaborativearchitecture.com'],

    // who the emails come from: an address of the domain (create it in Google Workspace, or use an alias of enquiry@)
    'from_email' => 'website@collaborativearchitecture.com',
    'from_name'  => 'Collaborative Architecture website',

    // where each type of inquiry goes
    'mailboxes' => [
        'Client'      => 'enquiry@collaborativearchitecture.com',
        'Consultants' => 'enquiry@collaborativearchitecture.com',
        'Research'    => 'enquiry@collaborativearchitecture.com',
        'Career'      => 'studio@collaborativearchitecture.com',
        'Vendors'     => 'vendors@collaborativearchitecture.com',
    ],
    'riyadh_cc'     => '',   // a Riyadh studio address to copy on inquiries for the Riyadh studio
    'newsletter_to' => 'enquiry@collaborativearchitecture.com',   // who hears of newsletter sign-ups when Mailchimp is not connected

    // RECOMMENDED: send through Google Workspace, so the mail is authenticated and never lands in spam.
    // In Google Workspace, sign in as the from_email account, turn on 2-step verification, create an app password
    // (myaccount.google.com/apppasswords) and paste it below. Leave host empty to use the server's own mail().
    'smtp' => ['host' => 'smtp.gmail.com', 'port' => 465, 'secure' => 'ssl', 'user' => 'website@collaborativearchitecture.com', 'pass' => ''],

    // Cloudflare Turnstile secret key (its site key goes in site-config.js); empty = no Turnstile check
    'turnstile_secret' => '',

    // Mailchimp: Account → Extras → API keys; the audience ID is under Audience → Settings → Audience name and defaults
    'mailchimp' => ['api_key' => '', 'list_id' => '', 'double_opt_in' => true],

    // a copy of every message, one file a month, in a folder closed to the web (or set a path outside the web folder)
    'storage_dir' => dirname(__DIR__) . '/_private',
    'keep_copies' => true,
];
