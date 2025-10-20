<?php
declare(strict_types=1);

require_once __DIR__ . '/init.php';

$errors = [];
$message = '';

// Ilmoitetaan käyttäjälle session aikakatkaisusta
if (isset($_GET['timeout'])) {
    $message = 'Istunto päättyi aikakatkaisuun. Kirjaudu uudelleen.';
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';
    $token = $_POST['csrf_token'] ?? '';

    if (!admin_verify_csrf_token($token)) {
        $errors[] = 'Istunnon varmistus epäonnistui. Yritä uudelleen.';
    }

    if ($username === '' || $password === '') {
        $errors[] = 'Käyttäjätunnus ja salasana vaaditaan.';
    }

    if (empty($errors)) {
        $users = admin_read_json('users', []);
        $userMatch = null;
        foreach ($users as $user) {
            if (isset($user['username']) && hash_equals($user['username'], $username)) {
                $userMatch = $user;
                break;
            }
        }

        if ($userMatch === null || !password_verify($password, $userMatch['passwordhash'] ?? '')) {
            $errors[] = 'Väärä käyttäjätunnus tai salasana.';
        } else {
            session_regenerate_id(true);
            $_SESSION[ADMIN_SESSION_KEY] = [
                'id' => $userMatch['id'] ?? $username,
                'username' => $userMatch['username'],
                'role' => $userMatch['role'] ?? 'admin',
            ];
            $_SESSION['last_activity'] = time();
            admin_log_action($userMatch['username'], 'login', 'auth', []);
            header('Location: index.php');
            exit;
        }
    }
}

$csrfToken = admin_get_csrf_token();
?>
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>HRK Admin | Kirjaudu sisään</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="assets/css/admin.css">
</head>
<body class="bg-light">
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="card shadow-sm">
                    <div class="card-header text-center bg-dark text-white">
                        <h1 class="h4 mb-0">HRK Admin</h1>
                        <p class="mb-0 small">Sisäänkirjautuminen</p>
                    </div>
                    <div class="card-body">
                        <?php if ($message !== ''): ?>
                            <div class="alert alert-info" role="alert"><?php echo admin_e($message); ?></div>
                        <?php endif; ?>
                        <?php if (!empty($errors)): ?>
                            <div class="alert alert-danger" role="alert">
                                <ul class="mb-0">
                                    <?php foreach ($errors as $error): ?>
                                        <li><?php echo admin_e($error); ?></li>
                                    <?php endforeach; ?>
                                </ul>
                            </div>
                        <?php endif; ?>
                        <form method="post" novalidate>
                            <input type="hidden" name="csrf_token" value="<?php echo admin_e($csrfToken); ?>">
                            <div class="mb-3">
                                <label for="username" class="form-label">Käyttäjätunnus</label>
                                <input type="text" class="form-control" id="username" name="username" required autofocus>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Salasana</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Kirjaudu sisään</button>
                        </form>
                    </div>
                    <div class="card-footer text-center small text-muted">
                        &copy; <?php echo date('Y'); ?> Harjun Raskaskone Oy | Rakennettu AnomFIN / Jugi@AnomFIN tiimin toimesta
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
