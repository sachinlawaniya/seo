<?php
// Database Connection Helper for Hostinger MySQL
function get_db_pdo() {
    static $pdo = null;
    if ($pdo !== null) {
        return $pdo;
    }

    $config_file = __DIR__ . '/../db_config.json';
    if (!file_exists($config_file)) {
        return null;
    }

    $config = json_decode(file_get_contents($config_file), true);
    if (!$config || empty($config['password'])) {
        return null;
    }

    $host = $config['host'] ?? 'localhost';
    $db   = $config['database'] ?? 'u565670229_seo_dashboard';
    $user = $config['user'] ?? 'u565670229_seo_dashboard';
    $pass = $config['password'] ?? '';
    $port = $config['port'] ?? 3306;
    $charset = 'utf8mb4';

    $dsn = "mysql:host=$host;port=$port;dbname=$db;charset=$charset";
    $options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
        PDO::ATTR_TIMEOUT            => 5
    ];

    try {
        $pdo = new PDO($dsn, $user, $pass, $options);
        return $pdo;
    } catch (PDOException $e) {
        error_log("DB Connection Failed: " . $e->getMessage());
        return null;
    }
}
