<?php
/* Collaborative Architecture · a check of the website's email and form settings (27 November 2026, patch mail1)

   https://collaborativearchitecture.com/api/mail-check.php?key=KEY                 reports the settings, sends nothing
   https://collaborativearchitecture.com/api/mail-check.php?key=KEY&send=enquiry    also sends one test email to enquiry@
     send = enquiry, studio, vendors, newsletter or all
   KEY is check_key in api/mail.php. Without it, or after the date below, the page answers 404. It never shows a password or a
   key: only whether each is filled in and whether Google, Mailchimp and Cloudflare accept it. A few runs per hour at most. */

declare(strict_types=1);
require __DIR__ . '/lib.php';

const CA_CHECK_UNTIL = '2027-01-31';
$cfg = ca_config();
$key = $cfg['google']['check_key'];
if (strlen($key) < 24 || !hash_equals($key, (string) ($_GET['key'] ?? '')) || gmdate('Y-m-d') > CA_CHECK_UNTIL) { http_response_code(404); header('X-Robots-Tag: noindex'); exit; }
ca_rate_limit('mailcheck');

$own = static function (string $f): array { if (!is_file($f)) return []; $v = (static function (string $f) { return include $f; })($f); return is_array($v) ? $v : []; };
$mc = array_merge($cfg['mailchimp'], array_filter($own(__DIR__ . '/mailchimp.php'), fn($v) => $v !== '' && $v !== null));
$get = static function (string $url, string $userpwd = '', string $post = ''): array {
    $c = curl_init($url);
    curl_setopt_array($c, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15]);
    if ($userpwd !== '') curl_setopt($c, CURLOPT_USERPWD, $userpwd);
    if ($post !== '') { curl_setopt($c, CURLOPT_POST, true); curl_setopt($c, CURLOPT_POSTFIELDS, $post); }
    $out = curl_exec($c); $code = (int) curl_getinfo($c, CURLINFO_HTTP_CODE); $err = curl_error($c); curl_close($c);
    return ['code' => $code, 'json' => json_decode(is_string($out) ? $out : '', true), 'error' => $err];
};

$report = ['checked_at' => gmdate('c'), 'version' => trim((string) @file(dirname(__DIR__) . '/version.txt')[1])];

// Cloudflare Turnstile: a made-up answer tells a wrong secret ("invalid-input-secret") from a right one ("invalid-input-response")
$ts = $cfg['turnstile_secret'];
$report['cloudflare'] = ['secret' => $ts === '' ? 'empty: the server does not check the box' : 'filled in'];
if ($ts !== '') {
    $r = $get('https://challenges.cloudflare.com/turnstile/v0/siteverify', '', http_build_query(['secret' => $ts, 'response' => 'mail-check']));
    $codes = (array) ($r['json']['error-codes'] ?? []);
    $report['cloudflare']['accepted_by_cloudflare'] = in_array('invalid-input-secret', $codes, true) ? 'no: Cloudflare does not know this secret' : ($r['code'] === 200 ? 'yes' : 'could not ask Cloudflare (' . $r['code'] . ' ' . $r['error'] . ')');
}

// Mailchimp: the key and the audience, read only (nothing is added)
$apiKey = trim((string) ($mc['api_key'] ?? ''), " -\t\r\n'\""); $list = trim((string) ($mc['list_id'] ?? ''));
$report['mailchimp'] = ['api_key' => $apiKey === '' ? 'empty: sign-ups never reach Mailchimp' : 'filled in', 'audience_id' => $list === '' ? 'empty' : 'filled in',
    'double_opt_in' => !empty($mc['double_opt_in']), 'tag' => (string) ($mc['tag'] ?? '')];
if ($apiKey !== '' && $list !== '') {
    $dc = preg_replace('/[^a-z0-9]/', '', substr(strrchr($apiKey, '-') ?: '-us1', 1));
    $p = $get("https://$dc.api.mailchimp.com/3.0/ping", 'ca:' . $apiKey);
    $report['mailchimp']['key_accepted'] = $p['code'] === 200 ? 'yes' : 'no (' . $p['code'] . ' ' . ($p['json']['title'] ?? $p['error']) . ')';
    if ($p['code'] === 200) {
        $l = $get("https://$dc.api.mailchimp.com/3.0/lists/" . rawurlencode($list) . '?fields=name,stats.member_count,stats.unsubscribe_count', 'ca:' . $apiKey);
        $report['mailchimp']['audience'] = $l['code'] === 200 ? ($l['json']['name'] ?? '') . ' (' . (int) ($l['json']['stats']['member_count'] ?? 0) . ' subscribed)' : 'not found (' . $l['code'] . ')';
    }
}

// Email: where each form's email goes and how it leaves the server
$notify = filter_var((string) ($mc['notify_to'] ?? ''), FILTER_VALIDATE_EMAIL) ? (string) $mc['notify_to'] : 'newsletter@collaborativearchitecture.com';
$nlFrom = filter_var((string) ($mc['mail_from'] ?? ''), FILTER_VALIDATE_EMAIL) ? (string) $mc['mail_from'] : 'newsletter@collaborativearchitecture.com';
$boxes = ['enquiry' => [$cfg['mailboxes']['Client'], 'Contact form: Client, Consultants, Research'], 'studio' => [$cfg['mailboxes']['Career'], 'Contact form: Career'],
    'vendors' => [$cfg['mailboxes']['Vendors'], 'Contact form: Vendors'], 'newsletter' => [$notify, 'Newsletter sign-up notices']];
$send = strtolower((string) ($_GET['send'] ?? ''));
$report['google_accounts'] = ['own_app_password' => array_keys($cfg['google']['accounts']), 'fallback' => $cfg['google']['fallback']['user'] ?? 'none'];
$report['email'] = [];
foreach ($boxes as $k => [$addr, $what]) {
    $row = ['for' => $what, 'to' => $addr, 'leaves_through' => ca_mail_route($addr)];
    if ($send === 'all' || $send === $k) {
        $as = $k === 'newsletter' ? ['from_email' => $nlFrom, 'from_name' => (string) ($mc['mail_from_name'] ?? 'Collaborative Architecture newsletter')] : [];
        $ok = ca_mail([$addr], 'Website mail check · ' . $what . ' · ' . gmdate('j M Y, H:i') . ' UTC',
            "A test from collaborativearchitecture.com/api/mail-check.php: the website's email to $addr works.\n\nNo reply is needed.", '', [], $as);
        $row['test_email'] = $ok ? 'handed to the mail server' . ($GLOBALS['ca_mail_error'] ? ' (' . $GLOBALS['ca_mail_error'] . ')' : '') : 'not sent: ' . ($GLOBALS['ca_mail_error'] ?: 'see the PHP error log');
    }
    $report['email'][] = $row;
}
ca_json(200, $report);
