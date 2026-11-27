<?php
/* Collaborative Architecture · the newsletter sign-up (Lab page)
   With a Mailchimp API key and audience ID in config.php, the address joins the audience as "pending": Mailchimp sends the
   confirmation email, and the address is subscribed when the reader confirms. Without them, the sign-up is emailed to the studio
   (newsletter@, see notify_to below) and kept in the private folder, to be added to the list by hand.
   21 November 2026: the key and the audience ID can also be kept in api/mailchimp.php, a file of their own, so they can be put on
   the server without touching config.php (which holds the mail password); a value filled in there wins. A sign-up is also tagged
   "Website" in Mailchimp (the tag is set in mailchimp.php or config.php; empty = no tag).
   21 November 2026: the studio hears of every sign-up at notify_to (newsletter@, an alias delivered to press@), set in mailchimp.php;
   notify_every = false sends that email only when Mailchimp could not take the sign-up. */

declare(strict_types=1);
require __DIR__ . '/lib.php';

ca_guard();
$cfg = ca_config();

$email = ca_line(ca_field('email', 200));
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) ca_json(422, ['ok' => false, 'error' => 'Enter an email address in the format name@example.com.']);
if (ca_field('website', 200) !== '') ca_json(200, ['ok' => true, 'pending' => true]);

ca_rate_limit('subscribe');
ca_turnstile();

$mc = $cfg['mailchimp'];
$mcFile = __DIR__ . '/mailchimp.php'; $own = [];
if (is_file($mcFile)) {
    $own = (static function (string $f) { return include $f; })($mcFile);
    if (!is_array($own)) $own = [];
    if (is_array($own)) foreach (['api_key', 'list_id', 'tag', 'double_opt_in', 'notify_to', 'notify_every'] as $k) { if (array_key_exists($k, $own) && $own[$k] !== '' && $own[$k] !== null) $mc[$k] = $own[$k]; }
}
// tidy what was pasted: stray spaces, quotes or a trailing hyphen would otherwise break the Mailchimp address
$mc['api_key'] = trim((string) $mc['api_key'], " -\t\r\n'\"");
$mc['list_id'] = trim((string) $mc['list_id'], " \t\r\n'\"");
// 21 November 2026 (Mujib: "link only press and alias"): every newsletter email goes to newsletter@ (an alias of press@) and is sent as
// newsletter@ through press@'s Google account; never to or through enquiry@. newsletter_to and the smtp settings in config.php are not used here.
$notify = filter_var((string) ($mc['notify_to'] ?? ''), FILTER_VALIDATE_EMAIL) ? (string) $mc['notify_to'] : 'newsletter@collaborativearchitecture.com';
$nlFrom = filter_var((string) ($own['mail_from'] ?? ''), FILTER_VALIDATE_EMAIL) ? (string) $own['mail_from'] : 'newsletter@collaborativearchitecture.com';
$nlAs = ['from_email' => $nlFrom, 'from_name' => (string) ($own['mail_from_name'] ?? 'Collaborative Architecture newsletter'),
    // press@'s app password filled in: Gmail, signed in as press@; otherwise the server's own mail(), still as newsletter@
    'smtp' => trim((string) ($own['mail_pass'] ?? '')) !== ''
        // 27 November 2026 (patch mail1): the app password without the spaces Google shows it with; port 587 when 465 is closed (lib.php)
        ? ['host' => ca_config()['google']['host'], 'port' => 465, 'secure' => 'ssl', 'user' => (string) ($own['mail_user'] ?? 'press@collaborativearchitecture.com'), 'pass' => str_replace(' ', '', trim((string) $own['mail_pass']))]
        : ['host' => '', 'port' => 465, 'secure' => 'ssl', 'user' => '', 'pass' => '']];
if ($mc['api_key'] !== '' && $mc['list_id'] !== '') {
    $dc = substr(strrchr($mc['api_key'], '-') ?: '-us1', 1);
    $url = 'https://' . preg_replace('/[^a-z0-9]/', '', $dc) . '.api.mailchimp.com/3.0/lists/' . rawurlencode($mc['list_id']) . '/members/' . md5(strtolower($email));
    $status = $mc['double_opt_in'] ? 'pending' : 'subscribed';
    // PUT with status_if_new: a new address is added; an address already on the list is left as it is
    $body = json_encode(['email_address' => $email, 'status_if_new' => $status]);
    $res = ca_put($url, $body, 'ca:' . $mc['api_key']);
    ca_keep('newsletter', ['email' => $email, 'mailchimp' => $res['code']]);
    if ($res['code'] >= 200 && $res['code'] < 300) {
        // the "Website" tag, so sign-ups from the site can be told apart in Mailchimp; a failed tag never fails the sign-up
        $tag = trim((string) ($mc['tag'] ?? ''));
        if ($tag !== '') {
            $t = ca_put($url . '/tags', json_encode(['tags' => [['name' => mb_substr($tag, 0, 100), 'status' => 'active']]]), 'ca:' . $mc['api_key'], 'POST');
            if ($t['code'] < 200 || $t['code'] >= 300) error_log('CA subscribe: Mailchimp tag answered ' . $t['code'] . ' ' . substr($t['body'], 0, 300));
        }
        // the studio's copy of the sign-up (a failed email never fails the sign-up)
        if (!empty($mc['notify_every'])) ca_mail([$notify], 'Newsletter sign-up · ' . $email, "A reader signed up for the studio's newsletter:\n\n" . $email . "\n\nSigned up on collaborativearchitecture.com on " . gmdate('j F Y, H:i') . " UTC.\n" . ($mc['double_opt_in'] ? 'Mailchimp has added the address and sent its confirmation email; the reader joins the list once they confirm.' : 'Mailchimp has added the address to the list.') . ($tag !== '' ? ' Tag in Mailchimp: ' . $tag . '.' : ''), $email, [], $nlAs);
        ca_json(200, ['ok' => true, 'pending' => (bool) $mc['double_opt_in']]);
    }
    error_log('CA subscribe: Mailchimp answered ' . $res['code'] . ' ' . substr($res['body'], 0, 300));
    // fall through: the studio still hears of the sign-up by email
}

$sent = ca_mail([$notify], 'Newsletter sign-up · ' . $email, "A reader asked to receive the studio's newsletter:\n\n" . $email . "\n\nSigned up on collaborativearchitecture.com on " . gmdate('j F Y, H:i') . " UTC. Add the address to the newsletter list in Mailchimp.", $email, [], $nlAs);
ca_keep('newsletter', ['email' => $email, 'emailed' => $sent]);
if (!$sent) ca_json(502, ['ok' => false, 'error' => 'The sign-up could not be saved just now. Please try again later.']);
ca_json(200, ['ok' => true, 'pending' => false]);

function ca_put(string $url, string $body, string $userpwd, string $method = 'PUT'): array {
    if (function_exists('curl_init')) {
        $c = curl_init($url);
        curl_setopt_array($c, [CURLOPT_CUSTOMREQUEST => $method, CURLOPT_POSTFIELDS => $body, CURLOPT_HTTPHEADER => ['Content-Type: application/json'], CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_USERPWD => $userpwd]);
        $out = curl_exec($c); $code = (int) curl_getinfo($c, CURLINFO_HTTP_CODE); curl_close($c);
        return ['code' => $code, 'body' => is_string($out) ? $out : ''];
    }
    $ctx = stream_context_create(['http' => ['method' => $method, 'header' => "Content-Type: application/json\r\nAuthorization: Basic " . base64_encode($userpwd), 'content' => $body, 'timeout' => 15, 'ignore_errors' => true]]);
    $out = @file_get_contents($url, false, $ctx);
    $code = 0; foreach ($http_response_header ?? [] as $h) if (preg_match('#^HTTP/\S+\s+(\d+)#', $h, $m)) $code = (int) $m[1];
    return ['code' => $code, 'body' => is_string($out) ? $out : ''];
}
