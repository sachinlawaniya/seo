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
            $tasks = isset($payload['tasks']) ? $payload['tasks'] : (isset($payload[0]) ? $payload : [$payload]);
            $stmt = $pdo->prepare("INSERT INTO seo_action_tasks (task_id, title, category, priority, phase, assignee, status, verified, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE title=VALUES(title), category=VALUES(category), priority=VALUES(priority), phase=VALUES(phase), assignee=VALUES(assignee), status=VALUES(status), verified=VALUES(verified), notes=VALUES(notes)");
            
            foreach ($tasks as $t) {
                $tid = $t['id'] ?? ($t['task_id'] ?? uniqid('task_'));
                $stmt->execute([
                    $tid,
                    $t['title'] ?? 'SEO Fix Task',
                    $t['category'] ?? 'Technical',
                    $t['priority'] ?? ($t['sev'] ?? 'P1'),
                    $t['phase'] ?? 'Week 1',
                    $t['assignee'] ?? 'Web Developer',
                    $t['status'] ?? ($t['completed'] ? 'Completed' : 'Pending'),
                    !empty($t['verifiedLive']) ? 1 : 0,
                    $t['notes'] ?? ''
                ]);
            }

            echo json_encode(['success' => true, 'updated' => count($tasks)]);
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
        $stmt = $pdo->query("SELECT * FROM seo_action_tasks ORDER BY priority ASC, id ASC");
        $tasks = $stmt->fetchAll();
        if (!empty($tasks)) {
            echo json_encode(['success' => true, 'tasks' => $tasks]);
            exit;
        }
    } catch (Exception $e) {}
}

echo json_encode(['success' => true, 'tasks' => []]);
