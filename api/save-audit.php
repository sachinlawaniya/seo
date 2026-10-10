<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Cache-Control, Authorization');
header('Cache-Control: no-cache, no-store, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Expires: 0');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

require_once __DIR__ . '/db_connect.php';

$raw_input = file_get_contents('php://input');
$data = json_decode($raw_input, true);

if (!$data || !isset($data['pages'])) {
    echo json_encode(['success' => false, 'error' => 'Invalid audit payload provided']);
    exit;
}

$saved_targets = [];

// 1. Save to audit_raw_data.json
$json_file = __DIR__ . '/../audit_raw_data.json';
if (@file_put_contents($json_file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES))) {
    $saved_targets[] = 'audit_raw_data.json';
}

// 2. Save to data.js for static fallback
$js_file = __DIR__ . '/../data.js';
$js_content = "window.AUDIT_RAW_DATA = " . json_encode($data, JSON_UNESCAPED_SLASHES) . ";\n";
if (@file_put_contents($js_file, $js_content)) {
    $saved_targets[] = 'data.js';
}

// 3. Save to Hostinger MySQL Database
$pdo = get_db_pdo();
if ($pdo) {
    try {
        $run_id = 'run_' . date('Ymd_His');
        $pages = $data['pages'] ?? [];
        $total_pages = count($pages);
        $avg_health = $data['overall_score'] ?? 85;
        $p0 = $data['p0_count'] ?? 0;
        $p1 = $data['p1_count'] ?? 0;

        $stmt = $pdo->prepare("INSERT INTO seo_audit_runs (run_id, started_at, completed_at, target_domain, total_pages, avg_health_score, critical_issues_count, warning_issues_count, status, summary_json) VALUES (?, NOW(), NOW(), 'https://gurupunvaanii.com', ?, ?, ?, ?, 'COMPLETED', ?) ON DUPLICATE KEY UPDATE completed_at=NOW(), total_pages=VALUES(total_pages), avg_health_score=VALUES(avg_health_score), summary_json=VALUES(summary_json)");
        $stmt->execute([$run_id, $total_pages, $avg_health, $p0, $p1, json_encode($data)]);

        $page_stmt = $pdo->prepare("INSERT INTO seo_page_audits (run_id, url, status_code, title, description, h1, word_count, health_score, cwv_score, lcp, inp, cls, ttfb, fcp, tbt, canonical, robots, issues_json, raw_data_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
        foreach ($pages as $p) {
            $cwv = $p['cwv'] ?? [];
            $page_stmt->execute([
                $run_id,
                $p['url'] ?? '',
                $p['status'] ?? ($p['status_code'] ?? 200),
                $p['title'] ?? '',
                $p['meta_desc'] ?? ($p['description'] ?? ''),
                is_array($p['h1s'] ?? null) ? ($p['h1s'][0] ?? '') : ($p['h1'] ?? ''),
                $p['word_count'] ?? 0,
                $p['overall_score'] ?? ($p['health_score'] ?? 80),
                $cwv['score'] ?? 100,
                $cwv['lcp'] ?? '',
                $cwv['inp'] ?? '',
                (string)($cwv['cls'] ?? ''),
                $cwv['ttfb'] ?? '',
                $cwv['fcp'] ?? '',
                $cwv['tbt'] ?? '',
                $p['canonical'] ?? '',
                $p['meta_robots'] ?? ($p['robots'] ?? ''),
                json_encode($p['issues'] ?? []),
                json_encode($p)
            ]);
        }
        $saved_targets[] = 'MySQL Database';
    } catch (Exception $e) {
        error_log("DB Save Audit Error: " . $e->getMessage());
    }
}

echo json_encode([
    'success' => true,
    'saved_to' => $saved_targets,
    'total_pages' => count($data['pages']),
    'timestamp' => date('Y-m-d H:i:s')
]);
