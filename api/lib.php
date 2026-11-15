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
        'newsletter_to'  => 'enquiry@collaborativearchitecture.com',
        'smtp'           => ['host' => '', 'port' => 465, 'secure' => 'ssl', 'user' => '', 'pass' => ''],
        'turnstile_secret' => '',
        'mailchimp'      => ['api_key' => '', 'list_id' => '', 'double_opt_in' => true],
        'storage_dir'    => dirname(__DIR__) . '/_private',
        'keep_copies'    => true,
        'rate_limit'     => ['per_10_min' => 5, 'per_day' => 20],
        'min_seconds'    => 3,
    ];
    $local = [];
    if (is_file(__DIR__ . '/config.php')) { $local = require __DIR__ . '/config.php'; if (!is_array($local)) $local = []; }
    $cfg = array_replace_recursive($defaults, $local);
    return $cfg;
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

function ca_client_ip(): string { return (string) ($_SERVER['REMOTE_ADDR'] ?? ''); }

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
function ca_mail(array $to, string $subject, string $text, string $replyTo = '', array $cc = []): bool {
    $cfg = ca_config();
    $to = array_values(array_filter(array_map('ca_line', $to), fn($a) => filter_var($a, FILTER_VALIDATE_EMAIL)));
    $cc = array_values(array_filter(array_map('ca_line', $cc), fn($a) => filter_var($a, FILTER_VALIDATE_EMAIL)));
    if (!$to) return false;
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
    if (!empty($smtp['host'])) return ca_smtp($smtp, $from, array_merge($to, $cc), array_merge(['To: ' . implode(', ', $to), 'Subject: ' . $subject], $headers), $body);
    return @mail(implode(', ', $to), $subject, $body, implode("\r\n", $headers), '-f' . $from);
}

/* A small SMTP client: SSL on 465 or STARTTLS on 587, AUTH LOGIN */
function ca_smtp(array $s, string $from, array $rcpt, array $headers, string $body): bool {
    $host = (string) $s['host']; $port = (int) ($s['port'] ?: 465); $secure = strtolower((string) ($s['secure'] ?? 'ssl'));
    $ctx = stream_context_create(['ssl' => ['verify_peer' => true, 'verify_peer_name' => true, 'peer_name' => $host]]);
    $fp = @stream_socket_client(($secure === 'ssl' ? 'ssl://' : 'tcp://') . $host . ':' . $port, $errno, $errstr, 15, STREAM_CLIENT_CONNECT, $ctx);
    if (!$fp) { error_log("CA mail: cannot connect to $host:$port ($errstr)"); return false; }
    stream_set_timeout($fp, 15);
    $read = function () use ($fp) { $out = ''; while (($l = fgets($fp, 1024)) !== false) { $out .= $l; if (isset($l[3]) && $l[3] === ' ') break; } return $out; };
    $cmd = function (string $c, array $ok) use ($fp, $read) { if ($c !== '') fwrite($fp, $c . "\r\n"); $r = $read(); if (!in_array((int) substr($r, 0, 3), $ok, true)) { error_log('CA mail: ' . ($c === '' ? 'greeting' : explode(' ', $c)[0]) . ' answered ' . trim($r)); return false; } return true; };
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
