<?php
/* Collaborative Architecture · the inquiry form (Contact page)
   Receives the form, checks it again on the server, and sends it by email to the mailbox for its type of inquiry:
   Client, Consultants and Research → enquiry@; Career → studio@; Vendors → vendors@ (set in config.php).
   Messages that look automated (the hidden field filled in, or sent within seconds of the page opening) are answered as if sent,
   and kept in the private folder marked "held" instead of being emailed. */

declare(strict_types=1);
require __DIR__ . '/lib.php';

ca_guard();
$cfg = ca_config();

$f = [
    'name'         => ca_line(ca_field('name', 120)),
    'organization' => ca_line(ca_field('organization', 160)),
    'email'        => ca_line(ca_field('email', 200)),
    'telephone'    => ca_line(ca_field('telephone', 40)),
    'country'      => ca_line(ca_field('country', 80)),
    'inquiry_type' => ca_line(ca_field('inquiry_type', 40)),
    'portfolio'    => ca_line(ca_field('portfolio', 300)),
    'message'      => ca_field('message', 5000),
    'studio'       => ca_line(ca_field('studio', 20)),
    'page'         => ca_line(ca_field('page', 200)),
];
$honeypot = ca_field('website', 200);
$elapsed = (int) ca_field('elapsed', 12);

$errors = [];
if ($f['name'] === '') $errors[] = 'your name';
if (!filter_var($f['email'], FILTER_VALIDATE_EMAIL)) $errors[] = 'a valid email address';
if ($f['country'] === '') $errors[] = 'your country';
if (mb_strlen($f['message']) < 10) $errors[] = 'a short message';
if (!isset($cfg['mailboxes'][$f['inquiry_type']])) $f['inquiry_type'] = 'Client';
if (!in_array($f['studio'], ['mumbai', 'riyadh'], true)) $f['studio'] = 'mumbai';
if ($f['portfolio'] !== '' && !preg_match('#^https?://#i', $f['portfolio'])) $f['portfolio'] = 'https://' . $f['portfolio'];
if ($errors) ca_json(422, ['ok' => false, 'error' => 'Please add ' . implode(', ', $errors) . '.']);

// automated? answer as if sent, keep it aside, send nothing
if ($honeypot !== '' || ($elapsed > 0 && $elapsed < $cfg['min_seconds'] * 1000)) {
    ca_keep('held', ['form' => 'contact', 'reason' => $honeypot !== '' ? 'hidden field' : 'too fast'] + $f);
    ca_json(200, ['ok' => true]);
}

ca_rate_limit('contact');
ca_turnstile();

$to = [$cfg['mailboxes'][$f['inquiry_type']]];
$cc = ($f['studio'] === 'riyadh' && $cfg['riyadh_cc'] !== '') ? [$cfg['riyadh_cc']] : [];
$studio = $f['studio'] === 'riyadh' ? 'Riyadh Studio' : 'Mumbai Studio';
$subject = 'Website inquiry · ' . $f['inquiry_type'] . ' · ' . $f['name'] . ($f['organization'] !== '' ? ', ' . $f['organization'] : '');
$lines = [
    'A new inquiry from collaborativearchitecture.com',
    '',
    'Type:          ' . $f['inquiry_type'],
    'For:           ' . $studio,
    'Name:          ' . $f['name'],
    'Organization:  ' . ($f['organization'] ?: '—'),
    'Email:         ' . $f['email'],
    'Telephone:     ' . ($f['telephone'] ?: '—'),
    'Country:       ' . $f['country'],
];
if ($f['portfolio'] !== '') $lines[] = 'Portfolio:     ' . $f['portfolio'];
$lines = array_merge($lines, ['', 'Message:', $f['message'], '', '—', 'Sent from ' . ($f['page'] ?: '/contact/') . ' on ' . gmdate('j F Y, H:i') . ' UTC. Reply to this email to answer ' . $f['name'] . ' directly.']);

$sent = ca_mail($to, $subject, implode("\n", $lines), $f['email'], $cc);
ca_keep('inquiries', ['sent' => $sent, 'to' => $to] + $f);

if (!$sent) ca_json(502, ['ok' => false, 'error' => 'The message could not be delivered just now.']);
ca_json(200, ['ok' => true]);
