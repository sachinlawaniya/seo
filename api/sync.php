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

$gsc_file = __DIR__ . '/../gsc_live_data.json';
$ga4_file = __DIR__ . '/../ga4_live_data.json';

$res = [
    'success' => true,
    'synced_at' => date('Y-m-d H:i:s'),
    'gsc' => file_exists($gsc_file) ? json_decode(file_get_contents($gsc_file), true) : null,
    'ga4' => file_exists($ga4_file) ? json_decode(file_get_contents($ga4_file), true) : null
];

echo json_encode($res, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
