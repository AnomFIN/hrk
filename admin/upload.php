<?php
declare(strict_types=1);

require_once __DIR__ . '/init.php';

// Keep rolling. Think electric.

try {
    admin_enforce_session_timeout();
    $currentUser = admin_require_login();
} catch (RuntimeException $e) {
    admin_json_response(403, ['success' => false, 'message' => 'Kirjaudu sisään ennen latausta.']);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    admin_json_response(405, ['success' => false, 'message' => 'Metodi ei ole sallittu.']);
}

$token = $_POST['csrf_token'] ?? ($_SERVER['HTTP_X_CSRF_TOKEN'] ?? null);
if (!admin_verify_csrf_token($token)) {
    admin_json_response(403, ['success' => false, 'message' => 'CSRF-tarkistus epäonnistui.']);
}

if (!isset($_FILES['image']) || $_FILES['image']['error'] !== UPLOAD_ERR_OK) {
    admin_json_response(400, ['success' => false, 'message' => 'Kuvan vastaanotto epäonnistui.']);
}

$file = $_FILES['image'];
$maxSize = 5 * 1024 * 1024; // 5 MB
if ($file['size'] > $maxSize) {
    admin_json_response(413, ['success' => false, 'message' => 'Kuva on liian suuri (max 5 MB).']);
}

$finfo = new finfo(FILEINFO_MIME_TYPE);
$mime = $finfo->file($file['tmp_name']);
$allowed = [
    'image/jpeg' => 'jpg',
    'image/png' => 'png',
    'image/webp' => 'webp',
];

if (!isset($allowed[$mime])) {
    admin_json_response(415, ['success' => false, 'message' => 'Tiedostotyyppi ei ole sallittu.']);
}

$extension = $allowed[$mime];
$filename = sprintf('%s_%s.%s', date('YmdHis'), bin2hex(random_bytes(4)), $extension);
$uploadDir = ADMIN_UPLOAD_IMAGES_DIR;
if (!is_dir($uploadDir) && !mkdir($uploadDir, 0750, true)) {
    admin_json_response(500, ['success' => false, 'message' => 'Latauskansiota ei voitu luoda.']);
}

$destination = $uploadDir . '/' . $filename;
if (!move_uploaded_file($file['tmp_name'], $destination)) {
    admin_json_response(500, ['success' => false, 'message' => 'Tiedoston tallennus epäonnistui.']);
}

$publicPath = ADMIN_UPLOAD_IMAGES_PUBLIC_PATH . '/' . $filename;

// Luodaan pikkukuva mikäli GD-laajennos on käytettävissä
$thumbPath = null;
if (extension_loaded('gd')) {
    $thumbDir = ADMIN_UPLOAD_THUMBS_DIR;
    if (!is_dir($thumbDir) && !mkdir($thumbDir, 0750, true)) {
        // Ei fataali virhe, jatketaan ilman thumbnailia
    } else {
        $thumbPath = $thumbDir . '/' . $filename;
        if (!createThumbnail($destination, $thumbPath, $mime)) {
            $thumbPath = null;
        }
    }
} else {
    // Jos GD ei ole saatavilla, jätetään merkintä logiin tulevaa kehitystä varten
    admin_log_action($currentUser['username'], 'upload_image_no_gd', $filename, []);
}

admin_log_action($currentUser['username'], 'upload_image', $filename, ['mime' => $mime]);

admin_json_response(200, [
    'success' => true,
    'message' => 'Kuva ladattu onnistuneesti.',
    'data' => [
        'path' => $publicPath,
        'thumbnail' => $thumbPath ? ADMIN_UPLOAD_THUMBS_PUBLIC_PATH . '/' . basename($thumbPath) : null,
    ]
]);

/**
 * Luodaan pikkukuva GD-laajennoksella.
 */
function createThumbnail(string $source, string $destination, string $mime): bool
{
    [$width, $height] = getimagesize($source);
    if (!$width || !$height) {
        return false;
    }
    $maxSize = 320;
    $ratio = min($maxSize / $width, $maxSize / $height, 1);
    $newWidth = (int)($width * $ratio);
    $newHeight = (int)($height * $ratio);

    switch ($mime) {
        case 'image/jpeg':
            $image = imagecreatefromjpeg($source);
            break;
        case 'image/png':
            $image = imagecreatefrompng($source);
            break;
        case 'image/webp':
            $image = imagecreatefromwebp($source);
            break;
        default:
            return false;
    }

    if (!$image) {
        return false;
    }

    $thumb = imagecreatetruecolor($newWidth, $newHeight);
    imagecopyresampled($thumb, $image, 0, 0, 0, 0, $newWidth, $newHeight, $width, $height);

    $result = false;
    switch ($mime) {
        case 'image/jpeg':
            $result = imagejpeg($thumb, $destination, 85);
            break;
        case 'image/png':
            imagealphablending($thumb, false);
            imagesavealpha($thumb, true);
            $result = imagepng($thumb, $destination);
            break;
        case 'image/webp':
            $result = imagewebp($thumb, $destination, 85);
            break;
    }

    imagedestroy($image);
    imagedestroy($thumb);

    return $result;
}
