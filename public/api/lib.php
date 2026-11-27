<?php
/* Collaborative Architecture · shared code of the form handlers (contact.php, subscribe.php).
   Plain PHP 7.4 or later, no libraries. Settings come from config.php beside this file (copy config.sample.php and fill it in);
   without config.php the defaults below apply and mail goes out through PHP's own mail(). */

declare(strict_types=1);

function ca_config(): array {
    static $cfg = null;
    if ($cfg !== null) return $cfg;
    $defaults = [
        'site_name'      => 'Collaborative Architecture',
        'allowed_hosts'  => ['collaborativearchitecture.com', 'www.collaborativearchitecture.com'],
        'from_email'     => 'website@collaborativearchitecture.com',
        'from_name'      => 'Collaborative Architecture website',
        'mailboxes'      => [
            'Client'      => 'enquiry@collaborativearchitecture.com',
            'Consultants' => 'enquiry@collaborativearchitecture.com',
            'Research'    => 'enquiry@collaborativearchitecture.com',
            'Career'      => 'studio@collaborativearchitecture.com',
            'Vendors'     => 'vendors@collaborativearchitecture.com',
        ],
        'riyadh_cc'      => '',
        'newsletter_to'  => 'newsletter@collaborativearchitecture.com',   // 21 November 2026: not read by subscribe.php any more (notify_to in mailchimp.php)
        'smtp'           => ['host' => '', 'port' => 465, 'secure' => 'ssl', 'user' => '', 'pass' => ''],
        'turnstile_secret' => '',
        'mailchimp'      => ['api_key' => '', 'list_id' => '', 'double_opt_in' => true],
        'storage_dir'    => dirname(__DIR__) . '/_private',
        'keep_copies'    => true,
        'rate_limit'     => ['per_10_min' => 5, 'per_day' => 20],
        'min_seconds'    => 3,
        'vitals_key'     => '',   // 9 November 2026: the key for api/vitals.php?report=YYYY-MM&key=… (empty: no report is given)
    ];
    $local = [];
    if (is_file(__DIR__ . '/config.php')) { $local = require __DIR__ . '/config.php'; if (!is_array($local)) $local = []; }
    $cfg = array_replace_recursive($defaults, $local);
    // 21 November 2026: the Cloudflare Turnstile secret can sit in api/security.php, a file of its own, so it can be put on the server
    // without touching config.php; a value filled in there wins
    if (is_file(__DIR__ . '/security.php')) { $sec = (static function (string $f) { return include $f; })(__DIR__ . '/security.php');
        if (is_array($sec) && isset($sec['turnstile_secret']) && is_string($sec['turnstile_secret']) && trim($sec['turnstile_secret']) !== '') $cfg['turnstile_secret'] = trim($sec['turnstile_secret']); }
    // 27 November 2026 (patch mail1): every form email goes out through Google with an app password, so it lands in the studio's
    // Google mailboxes. The server's own mail() handed it to the web server's mail program, which never delivered it (no SPF record,
    // and a cPanel server keeps mail for its own domain locally). api/mail.php can give each mailbox its own app password; a
    // mailbox without one sends through the fallback account: by default press@, with the app password already in mailchimp.php.
    $own = static function (string $f): array { if (!is_file($f)) return []; $v = (static function (string $f) { return include $f; })($f); return is_array($v) ? $v : []; };
    $mail = $own(__DIR__ . '/mail.php'); $mc = $own(__DIR__ . '/mailchimp.php');
    $clean = static function ($v): string { return str_replace(' ', '', trim((string) $v, " \t\r\n'\"")); };   // app passwords are shown with spaces
    $acc = [];
    foreach ((array) ($mail['accounts'] ?? []) as $addr => $pass) { $addr = strtolower(trim((string) $addr)); if (filter_var($addr, FILTER_VALIDATE_EMAIL) && $clean($pass) !== '') $acc[$addr] = $clean($pass); }
    $fbUser = trim((string) ($mail['fallback_user'] ?? '')); $fbPass = $clean($mail['fallback_pass'] ?? '');
    if ($fbUser === '' || $fbPass === '') { $fbUser = trim((string) ($mc['mail_user'] ?? 'press@collaborativearchitecture.com')); $fbPass = $clean($mc['mail_pass'] ?? ''); }
    $cfg['google'] = ['host' => trim((string) ($mail['smtp_host'] ?? '')) ?: 'smtp.gmail.com', 'accounts' => $acc,
        'fallback' => (filter_var($fbUser, FILTER_VALIDATE_EMAIL) && $fbPass !== '') ? ['user' => strtolower($fbUser), 'pass' => $fbPass] : null,
        'check_key' => trim((string) ($mail['check_key'] ?? ''))];
    return $cfg;
}

/* 27 November 2026 (patch mail1): the Google account that sends an email to $to: the mailbox's own, else the fallback, else none */
function ca_google_account(string $to): ?array {
    $g = ca_config()['google']; $to = strtolower(trim($to));
    if (isset($g['accounts'][$to])) return ['user' => $to, 'pass' => $g['accounts'][$to]];
    return $g['fallback'];
}
/* How an email to $to would leave the server, for api/mail-check.php (no password in it) */
function ca_mail_route(string $to): string {
    $a = ca_google_account($to); if ($a) return 'Google (' . ca_config()['google']['host'] . ') as ' . $a['user'];
    return !empty(ca_config()['smtp']['host']) ? 'SMTP server in config.php (' . ca_config()['smtp']['host'] . ')' : "the web server's own mail() (does not reach Google mailboxes)";
}

function ca_json(int $status, array $body): void {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    header('X-Robots-Tag: noindex');
    echo json_encode($body, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

/* Only POST, only from the site itself */
function ca_guard(): void {
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { header('Allow: POST'); ca_json(405, ['ok' => false, 'error' => 'Only POST is accepted.']); }
    $cfg = ca_config();
    $origin = $_SERVER['HTTP_ORIGIN'] ?? ($_SERVER['HTTP_REFERER'] ?? '');
    if ($origin !== '') {
        $host = strtolower((string) parse_url($origin, PHP_URL_HOST));
        $self = strtolower(preg_replace('/:\d+$/', '', (string) ($_SERVER['HTTP_HOST'] ?? '')));
        if ($host !== $self && !in_array($host, array_map('strtolower', $cfg['allowed_hosts']), true)) ca_json(403, ['ok' => false, 'error' => 'This form can only be sent from the website.']);
    }
}

function ca_field(string $k, int $max = 500): string {
    $v = isset($_POST[$k]) && is_string($_POST[$k]) ? $_POST[$k] : '';
    $v = str_replace("\0", '', $v);
    $v = preg_replace('/[^\P{C}\n\t]/u', '', $v) ?? '';   // control characters out, line breaks kept
    $v = trim($v);
    return mb_substr($v, 0, $max);
}
function ca_line(string $v): string { return trim(preg_replace('/[\r\n]+/', ' ', $v) ?? ''); }   // for anything that goes into a mail header

function ca_storage(string $sub = ''): string {
    $dir = rtrim(ca_config()['storage_dir'], '/');
    if (!is_dir($dir)) {
        @mkdir($dir, 0750, true);
        @file_put_contents($dir . '/.htaccess', "Require all denied\nDeny from all\n");
        @file_put_contents($dir . '/index.html', '');
    }
    if ($sub !== '') { $dir .= '/' . $sub; if (!is_dir($dir)) @mkdir($dir, 0750, true); }
    return $dir;
}

/* 19 November 2026 (final publish): behind Cloudflare every request reaches the server from a Cloudflare address, so all visitors would
   share one rate limit. When the request comes from Cloudflare's own network (the ranges it publishes at cloudflare.com/ips), the
   visitor's address is the one Cloudflare passes in CF-Connecting-IP; from anywhere else that header is ignored, so it cannot be faked. */
const CA_CLOUDFLARE = ['173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22', '103.31.4.0/22', '141.101.64.0/18', '108.162.192.0/18',
    '190.93.240.0/20', '188.114.96.0/20', '197.234.240.0/22', '198.41.128.0/17', '162.158.0.0/15', '104.16.0.0/13', '104.24.0.0/14',
    '172.64.0.0/13', '131.0.72.0/22', '2400:cb00::/32', '2606:4700::/32', '2803:f800::/32', '2405:b500::/32', '2405:8100::/32',
    '2a06:98c0::/29', '2c0f:f248::/32'];
function ca_in_range(string $ip, string $cidr): bool {
    [$net, $bits] = explode('/', $cidr); $a = @inet_pton($ip); $b = @inet_pton($net);
    if ($a === false || $b === false || strlen($a) !== strlen($b)) return false;
    $bits = (int) $bits; $whole = intdiv($bits, 8); $rest = $bits % 8;
    if (strncmp($a, $b, $whole) !== 0) return false;
    if ($rest === 0) return true;
    $mask = (0xFF << (8 - $rest)) & 0xFF;
    return (ord($a[$whole]) & $mask) === (ord($b[$whole]) & $mask);
}
function ca_client_ip(): string {
    $ip = (string) ($_SERVER['REMOTE_ADDR'] ?? ''); $cf = trim((string) ($_SERVER['HTTP_CF_CONNECTING_IP'] ?? ''));
    if ($cf !== '' && filter_var($cf, FILTER_VALIDATE_IP)) { foreach (CA_CLOUDFLARE as $r) { if (ca_in_range($ip, $r)) return $cf; } }
    return $ip;
}

/* A few messages per address in ten minutes and per day; the address is kept only as a one-way hash */
function ca_rate_limit(string $what): void {
    $cfg = ca_config();
    $f = ca_storage('rate') . '/' . $what . '-' . hash('sha256', ca_client_ip() . '|' . __DIR__) . '.json';
    $now = time(); $hits = [];
    if (is_file($f)) { $hits = json_decode((string) @file_get_contents($f), true) ?: []; }
    $hits = array_values(array_filter($hits, fn($t) => is_int($t) && $t > $now - 86400));
    $recent = count(array_filter($hits, fn($t) => $t > $now - 600));
    if ($recent >= $cfg['rate_limit']['per_10_min'] || count($hits) >= $cfg['rate_limit']['per_day']) {
        ca_json(429, ['ok' => false, 'error' => 'Too many messages from this connection. Please try again later, or write to us directly.']);
    }
    $hits[] = $now;
    @file_put_contents($f, json_encode($hits), LOCK_EX);
}

/* Cloudflare Turnstile, when a secret key is set in config.php */
function ca_turnstile(): void {
    $secret = ca_config()['turnstile_secret'];
    if ($secret === '') return;
    // 21 November 2026: a secret on the server while site-config.js has no site key would refuse every form (no visitor could
    // pass a check that is never shown), so the check waits until the site key is there too
    $sc = @file_get_contents(dirname(__DIR__) . '/site-config.js');
    if (is_string($sc) && preg_match("/turnstileSiteKey:\s*'([^']*)'/", $sc, $m) && (trim($m[1]) === '' || strpos($m[1], 'PASTE') !== false)) { error_log('CA forms: Turnstile secret set but no site key in site-config.js; the check is skipped'); return; }
    $token = ca_field('cf-turnstile-response', 4096);
    if ($token === '') ca_json(400, ['ok' => false, 'error' => 'Please complete the security check.']);
    $res = ca_post('https://challenges.cloudflare.com/turnstile/v0/siteverify', http_build_query(['secret' => $secret, 'response' => $token, 'remoteip' => ca_client_ip()]), ['Content-Type: application/x-www-form-urlencoded']);
    $j = json_decode($res['body'] ?? '', true);
    if (!is_array($j) || empty($j['success'])) ca_json(400, ['ok' => false, 'error' => 'The security check did not pass. Please try again.']);
}

function ca_post(string $url, string $body, array $headers = [], string $userpwd = ''): array {
    if (function_exists('curl_init')) {
        $c = curl_init($url);
        curl_setopt_array($c, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => $body, CURLOPT_HTTPHEADER => $headers, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15]);
        if ($userpwd !== '') curl_setopt($c, CURLOPT_USERPWD, $userpwd);
        $out = curl_exec($c); $code = (int) curl_getinfo($c, CURLINFO_HTTP_CODE); curl_close($c);
        return ['code' => $code, 'body' => is_string($out) ? $out : ''];
    }
    if ($userpwd !== '') $headers[] = 'Authorization: Basic ' . base64_encode($userpwd);
    $ctx = stream_context_create(['http' => ['method' => 'POST', 'header' => implode("\r\n", $headers), 'content' => $body, 'timeout' => 15, 'ignore_errors' => true]]);
    $out = @file_get_contents($url, false, $ctx);
    $code = 0; foreach ($http_response_header ?? [] as $h) if (preg_match('#^HTTP/\S+\s+(\d+)#', $h, $m)) $code = (int) $m[1];
    return ['code' => $code, 'body' => is_string($out) ? $out : ''];
}

/* A copy of each message in the private folder, one JSON line per message, a file per month */
function ca_keep(string $kind, array $record): void {
    if (!ca_config()['keep_copies']) return;
    $record = ['at' => gmdate('c')] + $record;
    @file_put_contents(ca_storage($kind) . '/' . gmdate('Y-m') . '.jsonl', json_encode($record, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n", FILE_APPEND | LOCK_EX);
}

function ca_mime(string $s): string { return preg_match('/[^\x20-\x7E]/', $s) ? '=?UTF-8?B?' . base64_encode($s) . '?=' : $s; }

/* Send one plain-text message: through SMTP when config.php gives a server (recommended: Google Workspace), else PHP mail() */
/* 21 November 2026: $as sends with another sender and mail account than config.php's: the newsletter's own (newsletter@ through press@),
   so newsletter mail never goes through enquiry@. Keys: from_email, from_name, smtp (as in config.php). */
function ca_mail(array $to, string $subject, string $text, string $replyTo = '', array $cc = [], array $as = []): bool {
    $noServer = isset($as['smtp']) && empty($as['smtp']['host']);   // the caller gives no account and does not want config.php's server
    if ($noServer) unset($as['smtp']);
    $cfg = array_merge(ca_config(), array_intersect_key($as, ['from_email' => 1, 'from_name' => 1, 'smtp' => 1]));
    $to = array_values(array_filter(array_map('ca_line', $to), fn($a) => filter_var($a, FILTER_VALIDATE_EMAIL)));
    $cc = array_values(array_filter(array_map('ca_line', $cc), fn($a) => filter_var($a, FILTER_VALIDATE_EMAIL)));
    if (!$to) return false;
    $GLOBALS['ca_mail_error'] = '';
    // 27 November 2026 (patch mail1): through Google, as the receiving mailbox or the fallback account; it sends as itself (Google
    // would rewrite any other From address), the newsletter's own sender (newsletter@, an alias of press@) excepted
    if (!isset($as['smtp']) && ($acct = ca_google_account($to[0]))) {
        $cfg['smtp'] = ['host' => ca_config()['google']['host'], 'port' => 465, 'secure' => 'ssl', 'user' => $acct['user'], 'pass' => $acct['pass']];
        if (!isset($as['from_email'])) $cfg['from_email'] = $acct['user'];
    } elseif ($noServer) $cfg['smtp'] = ['host' => ''];
    $from = ca_line($cfg['from_email']); $fromName = ca_line($cfg['from_name']);
    $replyTo = filter_var(ca_line($replyTo), FILTER_VALIDATE_EMAIL) ? ca_line($replyTo) : '';
    $headers = [
        'From: ' . ca_mime($fromName) . ' <' . $from . '>',
        'Date: ' . date('r'),
        'Message-ID: <' . bin2hex(random_bytes(12)) . '@' . (explode('@', $from)[1] ?? 'localhost') . '>',
        'MIME-Version: 1.0',
        'Content-Type: text/plain; charset=UTF-8',
        'Content-Transfer-Encoding: base64',
        'X-Mailer: CA-website',
    ];
    if ($replyTo !== '') $headers[] = 'Reply-To: ' . $replyTo;
    if ($cc) $headers[] = 'Cc: ' . implode(', ', $cc);
    $body = chunk_split(base64_encode(str_replace("\n", "\r\n", str_replace("\r\n", "\n", $text))));
    $subject = ca_mime(ca_line($subject));
    $smtp = $cfg['smtp'];
    if (!empty($smtp['host'])) {
        $ok = ca_smtp($smtp, $from, array_merge($to, $cc), array_merge(['To: ' . implode(', ', $to), 'Subject: ' . $subject], $headers), $body);
        // 27 November 2026 (patch mail1): a mailbox whose own app password fails sends through the fallback account instead
        $fb = ca_config()['google']['fallback'];
        if (!$ok && isset($acct) && $fb && $acct['user'] !== $fb['user']) {
            $first = $GLOBALS['ca_mail_error']; error_log('CA mail: ' . $acct['user'] . ' could not send (' . $first . '); trying ' . $fb['user']);
            $smtp = ['user' => $fb['user'], 'pass' => $fb['pass']] + $smtp; $from = $fb['user'];
            $headers[0] = 'From: ' . ca_mime($fromName) . ' <' . $from . '>';
            $ok = ca_smtp($smtp, $from, array_merge($to, $cc), array_merge(['To: ' . implode(', ', $to), 'Subject: ' . $subject], $headers), $body);
            if ($ok) $GLOBALS['ca_mail_error'] = 'sent through ' . $fb['user'] . ' because ' . $acct['user'] . ' failed: ' . $first;
        }
        return $ok;
    }
    return @mail(implode(', ', $to), $subject, $body, implode("\r\n", $headers), '-f' . $from);
}

/* A small SMTP client: SSL on 465 or STARTTLS on 587, AUTH LOGIN */
function ca_smtp(array $s, string $from, array $rcpt, array $headers, string $body): bool {
    $host = (string) $s['host']; $port = (int) ($s['port'] ?: 465); $secure = strtolower((string) ($s['secure'] ?? 'ssl'));
    $ctx = stream_context_create(['ssl' => ['verify_peer' => true, 'verify_peer_name' => true, 'peer_name' => $host]]);
    $fp = @stream_socket_client(($secure === 'ssl' ? 'ssl://' : 'tcp://') . $host . ':' . $port, $errno, $errstr, 15, STREAM_CLIENT_CONNECT, $ctx);
    // 27 November 2026 (patch mail1): some hosts close port 465; Google also takes 587 with STARTTLS
    if (!$fp && $secure === 'ssl' && $port === 465) { $first = $errstr; $secure = 'tls'; $port = 587;
        $fp = @stream_socket_client('tcp://' . $host . ':587', $errno, $errstr, 15, STREAM_CLIENT_CONNECT, $ctx);
        if (!$fp) $errstr = "465: $first; 587: $errstr"; }
    if (!$fp) { error_log("CA mail: cannot connect to $host:$port ($errstr)"); $GLOBALS['ca_mail_error'] = "cannot connect to $host ($errstr)"; return false; }
    stream_set_timeout($fp, 15);
    $read = function () use ($fp) { $out = ''; while (($l = fgets($fp, 1024)) !== false) { $out .= $l; if (isset($l[3]) && $l[3] === ' ') break; } return $out; };
    $cmd = function (string $c, array $ok) use ($fp, $read) { if ($c !== '') fwrite($fp, $c . "\r\n"); $r = $read(); if (!in_array((int) substr($r, 0, 3), $ok, true)) { $v = strtoupper((string) strtok($c, ' ')); $e = ($c === '' ? 'greeting' : (in_array($v, ['EHLO', 'STARTTLS', 'AUTH', 'MAIL', 'RCPT', 'DATA'], true) ? $v : (strpos($c, "\r\n") !== false ? 'message' : 'AUTH (user name or app password)'))) . ' answered ' . trim(preg_replace('/\s+/', ' ', $r)); error_log('CA mail: ' . $e); $GLOBALS['ca_mail_error'] = $e; return false; } return true; };
    $me = ca_line($_SERVER['SERVER_NAME'] ?? 'localhost');
    $ok = $cmd('', [220]) && $cmd('EHLO ' . $me, [250]);
    if ($ok && $secure === 'tls') { $ok = $cmd('STARTTLS', [220]) && stream_socket_enable_crypto($fp, true, STREAM_CRYPTO_METHOD_TLS_CLIENT) && $cmd('EHLO ' . $me, [250]); }
    if ($ok && !empty($s['user'])) $ok = $cmd('AUTH LOGIN', [334]) && $cmd(base64_encode((string) $s['user']), [334]) && $cmd(base64_encode((string) $s['pass']), [235]);
    $ok = $ok && $cmd('MAIL FROM:<' . $from . '>', [250]);
    foreach ($rcpt as $r) $ok = $ok && $cmd('RCPT TO:<' . $r . '>', [250, 251]);
    $ok = $ok && $cmd('DATA', [354]) && $cmd(implode("\r\n", $headers) . "\r\n\r\n" . $body . "\r\n.", [250]);
    @fwrite($fp, "QUIT\r\n"); fclose($fp);
    return $ok;
}
