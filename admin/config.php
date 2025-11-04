<?php
declare(strict_types=1);

// Torque meets telemetry.

/**
 * Why this design
 * - Centralise environment parsing so PHP and the installer share a single contract.
 * - Allow directory overrides via .env without breaking legacy relative paths.
 * - Keep the API tiny: read values, resolve secure absolute paths, expose sane defaults.
 */

const ADMIN_ENV_FILE = __DIR__ . '/../.env';
const ADMIN_PROJECT_ROOT = __DIR__ . '/..';

/**
 * Cached environment values loaded from the .env file.
 */
function admin_env_values(): array
{
    static $cache = null;
    if ($cache !== null) {
        return $cache;
    }

    $cache = [];
    if (!is_file(ADMIN_ENV_FILE)) {
        return $cache;
    }

    $lines = file(ADMIN_ENV_FILE, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    if ($lines === false) {
        return $cache;
    }

    foreach ($lines as $line) {
        $trimmed = trim($line);
        if ($trimmed === '' || $trimmed[0] === '#') {
            continue;
        }

        $parts = explode('=', $trimmed, 2);
        if (count($parts) !== 2) {
            continue;
        }

        [$key, $value] = $parts;
        $key = trim($key);
        $value = trim($value);

        if ($value !== '' && ($value[0] === "'" || $value[0] === '"')) {
            $quote = $value[0];
            if (substr($value, -1) === $quote) {
                $value = substr($value, 1, -1);
            }
        }

        $cache[$key] = $value;
    }

    return $cache;
}

/**
 * Fetch a string from .env or system environment.
 */
function admin_env(string $key, ?string $default = null): ?string
{
    $values = admin_env_values();
    if (array_key_exists($key, $values)) {
        return $values[$key];
    }

    $value = getenv($key);
    if ($value !== false) {
        return $value;
    }

    return $default;
}

/**
 * Determine whether a path is absolute for Unix/Windows.
 */
function admin_is_absolute_path(string $path): bool
{
    if ($path === '') {
        return false;
    }

    if ($path[0] === '/' || $path[0] === '\\') {
        return true;
    }

    return preg_match('/^[A-Za-z]:[\\\\\/]/', $path) === 1;
}

/**
 * Resolve a directory path relative to project root when needed.
 */
function admin_resolve_directory(string $envKey, string $defaultRelative): string
{
    $value = admin_env($envKey);
    if ($value === null || $value === '') {
        $value = $defaultRelative;
    }

    $normalised = str_replace('\\', '/', $value);
    if (!admin_is_absolute_path($normalised)) {
        $normalised = rtrim(ADMIN_PROJECT_ROOT, '/\\') . '/' . ltrim($normalised, '/');
    }

    return rtrim($normalised, '/');
}

/**
 * Resolve a file path relative to project root when needed.
 */
function admin_resolve_file(string $envKey, string $defaultRelative): string
{
    $value = admin_env($envKey);
    if ($value === null || $value === '') {
        $value = $defaultRelative;
    }

    $normalised = str_replace('\\', '/', $value);
    if (!admin_is_absolute_path($normalised)) {
        $normalised = rtrim(ADMIN_PROJECT_ROOT, '/\\') . '/' . ltrim($normalised, '/');
    }

    return $normalised;
}

if (!defined('ADMIN_DATA_DIR')) {
    define('ADMIN_DATA_DIR', admin_resolve_directory('HRK_DATA_DIR', 'data'));
}

if (!defined('ADMIN_UPLOADS_DIR')) {
    define('ADMIN_UPLOADS_DIR', admin_resolve_directory('HRK_UPLOADS_DIR', 'uploads'));
}

if (!defined('ADMIN_UPLOAD_IMAGES_DIR')) {
    define('ADMIN_UPLOAD_IMAGES_DIR', admin_resolve_directory('HRK_UPLOAD_IMAGES_DIR', 'uploads/images'));
}

if (!defined('ADMIN_UPLOAD_THUMBS_DIR')) {
    define('ADMIN_UPLOAD_THUMBS_DIR', admin_resolve_directory('HRK_UPLOAD_THUMBS_DIR', 'uploads/images/thumbs'));
}

if (!defined('ADMIN_LOGS_DIR')) {
    define('ADMIN_LOGS_DIR', admin_resolve_directory('HRK_LOGS_DIR', 'logs'));
}

if (!defined('ADMIN_LOG_FILE')) {
    define('ADMIN_LOG_FILE', admin_resolve_file('HRK_ADMIN_LOG', 'logs/admin.log'));
}

if (!defined('ADMIN_UPLOAD_IMAGES_PUBLIC_PATH')) {
    $public = admin_env('HRK_UPLOAD_IMAGES_PUBLIC', '/uploads/images');
    define('ADMIN_UPLOAD_IMAGES_PUBLIC_PATH', rtrim($public, '/'));
}

if (!defined('ADMIN_UPLOAD_THUMBS_PUBLIC_PATH')) {
    $thumbPublic = admin_env('HRK_UPLOAD_THUMBS_PUBLIC', ADMIN_UPLOAD_IMAGES_PUBLIC_PATH . '/thumbs');
    define('ADMIN_UPLOAD_THUMBS_PUBLIC_PATH', rtrim($thumbPublic, '/'));
}

if (!defined('ADMIN_ENVIRONMENT')) {
    define('ADMIN_ENVIRONMENT', admin_env('HRK_ENVIRONMENT', 'development'));
}
