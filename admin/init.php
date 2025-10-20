<?php
declare(strict_types=1);

// *** Hallintapaneelin alustukset ***

ini_set('default_charset', 'UTF-8');
mb_internal_encoding('UTF-8');

require_once __DIR__ . '/save.php';

if (session_status() === PHP_SESSION_NONE) {
    session_set_cookie_params([
        'httponly' => true,
        'secure' => isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off',
        'samesite' => 'Strict',
        'path' => dirname($_SERVER['SCRIPT_NAME'] ?? '/') ?: '/',
    ]);
    session_start();
}

// Luodaan CSRF-token välittömästi, jotta se on lomakkeissa käytettävissä.
admin_get_csrf_token();

