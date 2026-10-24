<?php
/* Collaborative Architecture · the newsletter sign-up (Lab page)
   With a Mailchimp API key and audience ID in config.php, the address joins the audience as "pending": Mailchimp sends the
   confirmation email, and the address is subscribed when the reader confirms. Without them, the sign-up is emailed to the studio
   (newsletter_to in config.php) and kept in the private folder, to be added to the list by hand. */

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
if ($mc['api_key'] !== '' && $mc['list_id'] !== '') {
    $dc = substr(strrchr($mc['api_key'], '-') ?: '-us1', 1);
    $url = 'https://' . preg_replace('/[^a-z0-9]/', '', $dc) . '.api.mailchimp.com/3.0/lists/' . rawurlencode($mc['list_id']) . '/members/' . md5(strtolower($email));
    $status = $mc['double_opt_in'] ? 'pending' : 'subscribed';
    // PUT with status_if_new: a new address is added; an address already on the list is left as it is
    $body = json_encode(['email_address' => $email, 'status_if_new' => $status]);
    $res = ca_put($url, $body, 'ca:' . $mc['api_key']);
    ca_keep('newsletter', ['email' => $email, 'mailchimp' => $res['code']]);
    if ($res['code'] >= 200 && $res['code'] < 300) ca_json(200, ['ok' => true, 'pending' => $mc['double_opt_in']]);
    error_log('CA subscribe: Mailchimp answered ' . $res['code'] . ' ' . substr($res['body'], 0, 300));
    // fall through: the studio still hears of the sign-up by email
}

$sent = ca_mail([$cfg['newsletter_to']], 'Newsletter sign-up · ' . $email, "A reader asked to receive the studio's newsletter:\n\n" . $email . "\n\nSigned up on collaborativearchitecture.com on " . gmdate('j F Y, H:i') . " UTC. Add the address to the newsletter list in Mailchimp.", $email);
ca_keep('newsletter', ['email' => $email, 'emailed' => $sent]);
if (!$sent) ca_json(502, ['ok' => false, 'error' => 'The sign-up could not be saved just now. Please try again later.']);
ca_json(200, ['ok' => true, 'pending' => false]);

function ca_put(string $url, string $body, string $userpwd): array {
    if (function_exists('curl_init')) {
        $c = curl_init($url);
        curl_setopt_array($c, [CURLOPT_CUSTOMREQUEST => 'PUT', CURLOPT_POSTFIELDS => $body, CURLOPT_HTTPHEADER => ['Content-Type: application/json'], CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_USERPWD => $userpwd]);
        $out = curl_exec($c); $code = (int) curl_getinfo($c, CURLINFO_HTTP_CODE); curl_close($c);
        return ['code' => $code, 'body' => is_string($out) ? $out : ''];
    }
    $ctx = stream_context_create(['http' => ['method' => 'PUT', 'header' => "Content-Type: application/json\r\nAuthorization: Basic " . base64_encode($userpwd), 'content' => $body, 'timeout' => 15, 'ignore_errors' => true]]);
    $out = @file_get_contents($url, false, $ctx);
    $code = 0; foreach ($http_response_header ?? [] as $h) if (preg_match('#^HTTP/\S+\s+(\d+)#', $h, $m)) $code = (int) $m[1];
    return ['code' => $code, 'body' => is_string($out) ? $out : ''];
}
