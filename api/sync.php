<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Cache-Control, Authorization');
header('Cache-Control: no-cache, no-store, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Expires: 0');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

require_once __DIR__ . '/db_connect.php';

$gsc_file = __DIR__ . '/../gsc_live_data.json';
$ga4_file = __DIR__ . '/../ga4_live_data.json';

$gsc_data = file_exists($gsc_file) ? json_decode(file_get_contents($gsc_file), true) : null;
$ga4_data = file_exists($ga4_file) ? json_decode(file_get_contents($ga4_file), true) : null;

// If files missing, try querying MySQL
$pdo = get_db_pdo();
if ($pdo) {
    if (!$gsc_data) {
        try {
            $stmt = $pdo->query("SELECT * FROM seo_gsc_performance ORDER BY id DESC LIMIT 1");
            $row = $stmt->fetch();
            if ($row && !empty($row['raw_payload'])) {
                $gsc_data = json_decode($row['raw_payload'], true);
            }
        } catch (Exception $e) {}
    }

    if (!$ga4_data) {
        try {
            $stmt = $pdo->query("SELECT * FROM seo_ga4_metrics ORDER BY id DESC LIMIT 1");
            $row = $stmt->fetch();
            if ($row && !empty($row['raw_payload'])) {
                $ga4_data = json_decode($row['raw_payload'], true);
            }
        } catch (Exception $e) {}
    }
}

$res = [
    'success' => true,
    'synced_at' => date('Y-m-d H:i:s'),
    'gsc' => $gsc_data,
    'ga4' => $ga4_data
];

echo json_encode($res, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
