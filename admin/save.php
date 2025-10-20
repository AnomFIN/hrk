<?php
declare(strict_types=1);

// *** Yleiset apufunktiot JSON-tiedostopohjaiseen datavarastoon ***

const ADMIN_DATA_DIR = __DIR__ . '/../data';
const ADMIN_LOG_FILE = __DIR__ . '/../logs/admin.log';
const ADMIN_SESSION_KEY = 'hrk_admin_user';
const ADMIN_SESSION_TIMEOUT = 1800; // 30 minuuttia

/**
 * Palautetaan sallittujen tiedostojen lista, jotta path traversal estyy.
 */
function admin_allowed_files(): array
{
    return [
        'products' => 'products.json',
        'categories' => 'categories.json',
        'settings' => 'settings.json',
        'pages' => 'pages.json',
        'orders' => 'orders.json',
        'users' => 'users.json',
    ];
}

/**
 * Lasketaan turvallinen tiedostopolku halutulle avaimelle.
 */
function admin_data_path(string $key): string
{
    $allowed = admin_allowed_files();
    if (!isset($allowed[$key])) {
        throw new InvalidArgumentException('Tuntematon tietotunniste: ' . $key);
    }

    return ADMIN_DATA_DIR . '/' . $allowed[$key];
}

/**
 * Luetaan JSON ja palautetaan oletusarvo virhetilanteissa.
 */
function admin_read_json(string $key, $default)
{
    $path = admin_data_path($key);
    if (!file_exists($path)) {
        return $default;
    }

    $json = file_get_contents($path);
    if ($json === false) {
        return $default;
    }

    $data = json_decode($json, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        return $default;
    }

    return $data;
}

/**
 * Kirjoitetaan JSON atomisesti ja lukitaan kirjoitusoperaation ajaksi.
 */
function admin_write_json(string $key, $data): bool
{
    $path = admin_data_path($key);
    $tmpPath = $path . '.tmp';
    $encoded = json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    if ($encoded === false) {
        return false;
    }

    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0750, true)) {
        return false;
    }

    $fp = fopen($tmpPath, 'wb');
    if ($fp === false) {
        return false;
    }

    // Käytetään tiedostolukkoa kilpailutilanteiden ehkäisemiseksi.
    if (!flock($fp, LOCK_EX)) {
        fclose($fp);
        return false;
    }

    $result = fwrite($fp, $encoded);
    fflush($fp);
    flock($fp, LOCK_UN);
    fclose($fp);

    if ($result === false) {
        @unlink($tmpPath);
        return false;
    }

    if (!rename($tmpPath, $path)) {
        @unlink($tmpPath);
        return false;
    }

    return true;
}

/**
 * Kirjataan audit-logiin hallintatoiminto aikaleiman ja käyttäjätiedon kanssa.
 */
function admin_log_action(string $username, string $action, string $target, array $metadata = []): void
{
    $dir = dirname(ADMIN_LOG_FILE);
    if (!is_dir($dir) && !mkdir($dir, 0750, true)) {
        return;
    }

    $entry = [
        'timestamp' => gmdate('c'),
        'user' => $username,
        'action' => $action,
        'target' => $target,
        'meta' => $metadata,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
    ];

    $line = json_encode($entry, JSON_UNESCAPED_UNICODE);
    if ($line === false) {
        return;
    }

    file_put_contents(ADMIN_LOG_FILE, $line . PHP_EOL, FILE_APPEND | LOCK_EX);
}

/**
 * Palautetaan kirjautunut käyttäjä tai null.
 */
function admin_current_user(): ?array
{
    if (!isset($_SESSION[ADMIN_SESSION_KEY])) {
        return null;
    }

    $user = $_SESSION[ADMIN_SESSION_KEY];
    if (!is_array($user)) {
        return null;
    }

    return $user;
}

/**
 * Varmistetaan session aikakatkaisu.
 */
function admin_enforce_session_timeout(): void
{
    if (!isset($_SESSION['last_activity'])) {
        $_SESSION['last_activity'] = time();
        return;
    }

    if (time() - (int)$_SESSION['last_activity'] > ADMIN_SESSION_TIMEOUT) {
        session_unset();
        session_destroy();
        throw new RuntimeException('Session aikakatkaisu');
    }

    $_SESSION['last_activity'] = time();
}

/**
 * Vaaditaan kirjautuminen ja heitetään poikkeus, jos sitä ei ole.
 */
function admin_require_login(): array
{
    $user = admin_current_user();
    if ($user === null) {
        throw new RuntimeException('Kirjautuminen vaaditaan');
    }

    return $user;
}

/**
 * Generoidaan CSRF-token session sisälle.
 */
function admin_get_csrf_token(): string
{
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }

    return $_SESSION['csrf_token'];
}

/**
 * Tarkistetaan CSRF-token ja palautetaan true/false ilman poikkeuksia.
 */
function admin_verify_csrf_token(?string $token): bool
{
    if (!isset($_SESSION['csrf_token'])) {
        return false;
    }

    if (!is_string($token)) {
        return false;
    }

    return hash_equals($_SESSION['csrf_token'], $token);
}

/**
 * Palautetaan turvallinen vastaus JSON-formaatissa.
 */
function admin_json_response(int $status, array $payload): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

/**
 * Luodaan URL-ystävällinen slugi.
 */
function admin_slugify(string $text): string
{
    $text = iconv('UTF-8', 'ASCII//TRANSLIT//IGNORE', $text);
    $text = preg_replace('~[^\pL\d]+~u', '-', $text);
    $text = trim($text, '-');
    $text = strtolower($text);
    $text = preg_replace('~[^-a-z0-9]+~', '', $text);
    if ($text === '') {
        $text = bin2hex(random_bytes(4));
    }
    return $text;
}

/**
 * Luodaan uniikki tunniste annetun prefiksin perusteella.
 */
function admin_generate_id(string $prefix): string
{
    return sprintf('%s-%s', $prefix, bin2hex(random_bytes(4)));
}

/**
 * Suodatetaan käyttäjän syöttämä HTML turvallisesti sallien vain tietyt tagit.
 */
function admin_sanitize_html(string $input): string
{
    $allowed = '<p><h1><h2><h3><h4><h5><h6><strong><em><ul><ol><li><a><br><span><div><img><blockquote>'; // perus tagit
    return strip_tags($input, $allowed);
}

/**
 * Suojataan tulostettava teksti (lyhyt helperi).
 */
function admin_e(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

