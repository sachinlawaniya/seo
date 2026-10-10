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

$pdo = get_db_pdo();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $raw_input = file_get_contents('php://input');
    $payload = json_decode($raw_input, true);

    if ($pdo && is_array($payload)) {
        try {
            $links = isset($payload['links']) ? $payload['links'] : (isset($payload[0]) ? $payload : [$payload]);
            $stmt = $pdo->prepare("INSERT INTO seo_backlinks (target_url, source_url, anchor_text, domain_authority, status, notes) VALUES (?, ?, ?, ?, ?, ?)");
            foreach ($links as $l) {
                $stmt->execute([
                    $l['target_url'] ?? 'https://gurupunvaanii.com/',
                    $l['source_url'] ?? '',
                    $l['anchor_text'] ?? '',
                    $l['da'] ?? ($l['domain_authority'] ?? 30),
                    $l['status'] ?? 'ACTIVE',
                    $l['notes'] ?? ''
                ]);
            }
            echo json_encode(['success' => true, 'inserted' => count($links)]);
            exit;
        } catch (Exception $e) {
            echo json_encode(['success' => false, 'error' => $e->getMessage()]);
            exit;
        }
    }
}

// GET
if ($pdo) {
    try {
        $stmt = $pdo->query("SELECT * FROM seo_backlinks ORDER BY domain_authority DESC, id ASC");
        $links = $stmt->fetchAll();
        if (!empty($links)) {
            echo json_encode(['success' => true, 'links' => $links]);
            exit;
        }
    } catch (Exception $e) {}
}

echo json_encode(['success' => true, 'links' => []]);
