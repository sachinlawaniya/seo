<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Cache-Control');
header('Cache-Control: no-cache, no-store, must-revalidate, max-age=0');
header('Pragma', 'no-cache');
header('Expires: 0');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$cache_file = __DIR__ . '/../ga4_live_data.json';
if (file_exists($cache_file)) {
    echo file_get_contents($cache_file);
} else {
    echo json_encode([
        'success' => false,
        'error' => 'GA4 data not found.'
    ]);
}
