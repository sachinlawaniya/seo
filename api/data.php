<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Cache-Control, Authorization');
header('Cache-Control: no-cache, no-store, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Expires: 0');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

require_once __DIR__ . '/db_connect.php';

// 1. Try fetching latest audit from MySQL Database
$pdo = get_db_pdo();
if ($pdo) {
    try {
        $run_stmt = $pdo->query("SELECT * FROM seo_audit_runs ORDER BY id DESC LIMIT 1");
        $run = $run_stmt->fetch();
        if ($run && !empty($run['run_id'])) {
            $run_id = $run['run_id'];
            $page_stmt = $pdo->prepare("SELECT * FROM seo_page_audits WHERE run_id = ? ORDER BY id ASC");
            $page_stmt->execute([$run_id]);
            $page_rows = $page_stmt->fetchAll();

            if (!empty($page_rows)) {
                $pages = [];
                foreach ($page_rows as $r) {
                    if (!empty($r['raw_data_json'])) {
                        $parsed = json_decode($r['raw_data_json'], true);
                        if ($parsed) {
                            $pages[] = $parsed;
                            continue;
                        }
                    }
                    $issues = !empty($r['issues_json']) ? json_decode($r['issues_json'], true) : [];
                    $pages[] = [
                        'url' => $r['url'],
                        'status' => (int)($r['status_code'] ?? 200),
                        'final_url' => $r['url'],
                        'title' => $r['title'] ?? '',
                        'meta_desc' => $r['description'] ?? '',
                        'h1s' => [$r['h1'] ?? ''],
                        'word_count' => (int)($r['word_count'] ?? 0),
                        'overall_score' => (int)($r['health_score'] ?? 80),
                        'canonical' => $r['canonical'] ?? $r['url'],
                        'meta_robots' => $r['robots'] ?? 'index, follow',
                        'cwv' => [
                            'score' => (int)($r['cwv_score'] ?? 100),
                            'lcp' => $r['lcp'] ?? '1.8s',
                            'inp' => $r['inp'] ?? '120ms',
                            'cls' => $r['cls'] ?? 0.02,
                            'ttfb' => $r['ttfb'] ?? '150ms',
                            'fcp' => $r['fcp'] ?? '1.1s',
                            'tbt' => $r['tbt'] ?? '80ms'
                        ],
                        'issues' => $issues
                    ];
                }

                $summary = !empty($run['summary_json']) ? json_decode($run['summary_json'], true) : [];
                $res = array_merge($summary, [
                    'success' => true,
                    'source' => 'mysql_db',
                    'timestamp' => $run['completed_at'] ?? date('Y-m-d H:i:s'),
                    'overall_score' => (int)($run['avg_health_score'] ?? 85),
                    'total_scanned' => count($pages),
                    'p0_count' => (int)($run['critical_issues_count'] ?? 0),
                    'p1_count' => (int)($run['warning_issues_count'] ?? 0),
                    'pages' => $pages
                ]);

                echo json_encode($res, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
                exit;
            }
        }
    } catch (Exception $e) {
        error_log("MySQL load notice in data.php: " . $e->getMessage());
    }
}

// 2. Fallback to audit_raw_data.json
$data_file = __DIR__ . '/../audit_raw_data.json';
if (file_exists($data_file)) {
    echo file_get_contents($data_file);
} else {
    echo json_encode([
        'success' => false,
        'error' => 'Audit data file not found.'
    ]);
}
