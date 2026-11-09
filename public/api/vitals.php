<?php
/* Collaborative Architecture · real visitors' speed (9 November 2026, approved by Mujib: benchmark audit P7, "own server, no cookies").

   POST, from the site's own pages only (the page sends one small report per visit, when the visitor leaves or hides it):
     {"p":"/work/the-souk/","lcp":2310,"inp":96,"cls":0.012,"fcp":1180,"ttfb":240,"d":"phone","n":"4g","l":"en-IN"}
   Each report becomes one line of _private/vitals/YYYY-MM.csv: the time (UTC, to the hour), the page, the numbers, the class of screen,
   the connection type and the browser's language. No IP address, cookie or identifier is kept. At most 50,000 lines a month.

   GET ?report=YYYY-MM&key=… (the key is "vitals_key" in config.php; without one, no report is given): the month's numbers by page and
   screen, at the 75th percentile, which is how Google judges a site (LCP ≤ 2,500 ms, INP ≤ 200 ms, CLS ≤ 0.1 are "good"). */

declare(strict_types=1);
require __DIR__ . '/lib.php';

const CA_VITALS_MAX_LINES = 50000;

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'GET') {
    $key = (string) (ca_config()['vitals_key'] ?? '');
    $given = isset($_GET['key']) && is_string($_GET['key']) ? $_GET['key'] : '';
    if ($key === '' || $given === '' || !hash_equals($key, $given)) ca_json(404, ['ok' => false]);
    $month = isset($_GET['report']) && is_string($_GET['report']) && preg_match('/^\d{4}-\d{2}$/', $_GET['report']) ? $_GET['report'] : gmdate('Y-m');
    $f = ca_storage('vitals') . '/' . $month . '.csv';
    $groups = [];
    if (is_file($f) && ($h = fopen($f, 'r'))) {
        while (($r = fgetcsv($h, 1000, ',', '"', '\\')) !== false) {
            if (count($r) < 10 || $r[0] === 'at') continue;
            [$at, $p, $lcp, $inp, $cls, $fcp, $ttfb, $d] = $r;
            foreach ([$p . ' · ' . $d, '(all pages) · ' . $d] as $g) {
                $groups[$g]['n'] = ($groups[$g]['n'] ?? 0) + 1;
                if ((int) $lcp > 0) $groups[$g]['lcp'][] = (int) $lcp;
                if ((int) $inp > 0) $groups[$g]['inp'][] = (int) $inp;
                $groups[$g]['cls'][] = (float) $cls; $groups[$g]['fcp'][] = (int) $fcp; $groups[$g]['ttfb'][] = (int) $ttfb;
            }
        }
        fclose($h);
    }
    $p75 = function (array $a): ?float { if (!$a) return null; sort($a); return $a[(int) floor(0.75 * (count($a) - 1))]; };
    $out = [];
    ksort($groups);
    foreach ($groups as $g => $v) {
        $out[$g] = ['visits' => $v['n'], 'lcp_ms_p75' => $p75($v['lcp'] ?? []), 'inp_ms_p75' => $p75($v['inp'] ?? []), 'cls_p75' => $p75($v['cls'] ?? []),
                    'fcp_ms_p75' => $p75($v['fcp'] ?? []), 'ttfb_ms_p75' => $p75($v['ttfb'] ?? [])];
    }
    ca_json(200, ['ok' => true, 'month' => $month, 'good' => ['lcp_ms' => 2500, 'inp_ms' => 200, 'cls' => 0.1], 'groups' => $out]);
}

ca_guard();   // POST only, from the site itself
$raw = (string) file_get_contents('php://input', false, null, 0, 2048);
$j = json_decode($raw, true);
if (!is_array($j)) { http_response_code(204); exit; }

$num = fn($k, $max) => isset($j[$k]) && is_numeric($j[$k]) ? max(0, min($max, $j[$k] + 0)) : 0;
$path = isset($j['p']) && is_string($j['p']) ? substr($j['p'], 0, 120) : '';
if (!preg_match('#^/[A-Za-z0-9/_.-]*$#', $path)) $path = '/';
$dev = isset($j['d']) && in_array($j['d'], ['phone', 'tablet', 'laptop'], true) ? $j['d'] : '';
$net = isset($j['n']) && is_string($j['n']) && preg_match('/^[a-z0-9-]{0,8}$/', $j['n']) ? $j['n'] : '';
$lang = isset($j['l']) && is_string($j['l']) && preg_match('/^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,4})?$/', $j['l']) ? $j['l'] : '';

if ($num('lcp', 120000) == 0 && $num('fcp', 120000) == 0) { http_response_code(204); exit; }   // a report with no paint in it (a page closed at once) says nothing
$f = ca_storage('vitals') . '/' . gmdate('Y-m') . '.csv';
$new = !is_file($f);
if (!$new && filesize($f) > CA_VITALS_MAX_LINES * 90) { http_response_code(204); exit; }   // the month's file is full
$h = fopen($f, 'a');
if ($h && flock($h, LOCK_EX)) {
    if ($new) fputcsv($h, ['at', 'page', 'lcp_ms', 'inp_ms', 'cls', 'fcp_ms', 'ttfb_ms', 'screen', 'connection', 'language'], ',', '"', '\\');
    fputcsv($h, [gmdate('Y-m-d\TH:00\Z'), $path, (int) $num('lcp', 120000), (int) $num('inp', 60000), round((float) $num('cls', 50), 4),
                 (int) $num('fcp', 120000), (int) $num('ttfb', 60000), $dev, $net, $lang], ',', '"', '\\');
    flock($h, LOCK_UN);
}
if ($h) fclose($h);
http_response_code(204);
