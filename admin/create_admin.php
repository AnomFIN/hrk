<?php
declare(strict_types=1);

require_once __DIR__ . '/init.php';

try {
    admin_enforce_session_timeout();
    $currentUser = admin_require_login();
} catch (RuntimeException $e) {
    header('Location: login.php');
    exit;
}

$errors = [];
$success = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!admin_verify_csrf_token($_POST['csrf_token'] ?? null)) {
        $errors[] = 'Istuntotunnisteen varmistus epäonnistui. Yritä uudelleen.';
    }

    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';
    $role = $_POST['role'] ?? 'admin';

    if ($username === '' || $password === '') {
        $errors[] = 'Käyttäjätunnus ja salasana ovat pakollisia.';
    }

    if (strlen($password) < 12) {
        $errors[] = 'Salasanan on oltava vähintään 12 merkkiä pitkä.';
    }

    if (empty($errors)) {
        $users = admin_read_json('users', []);
        foreach ($users as $user) {
            if (isset($user['username']) && hash_equals($user['username'], $username)) {
                $errors[] = 'Käyttäjätunnus on jo käytössä.';
                break;
            }
        }
    }

    if (empty($errors)) {
        $users[] = [
            'id' => admin_generate_id('u'),
            'username' => $username,
            'passwordhash' => password_hash($password, PASSWORD_DEFAULT),
            'role' => $role,
            'created_at' => gmdate('c'),
        ];
        if (admin_write_json('users', $users)) {
            admin_log_action($currentUser['username'], 'create_user', $username, ['role' => $role]);
            $success = 'Käyttäjä luotu onnistuneesti. Tallenna tunnukset turvalliseen paikkaan.';
        } else {
            $errors[] = 'Käyttäjän tallennus epäonnistui.';
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
    <title>HRK Admin | Luo käyttäjä</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="assets/css/admin.css">
</head>
<body>
<nav class="navbar navbar-dark bg-dark">
    <div class="container-fluid">
        <a class="navbar-brand" href="index.php">HRK Admin</a>
        <a class="btn btn-outline-light" href="index.php">Takaisin hallintaan</a>
    </div>
</nav>
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-6">
            <div class="card shadow-sm">
                <div class="card-header">
                    <h1 class="h4 mb-0">Luo uusi ylläpitäjä</h1>
                </div>
                <div class="card-body">
                    <?php if (!empty($errors)): ?>
                        <div class="alert alert-danger" role="alert">
                            <ul class="mb-0">
                                <?php foreach ($errors as $error): ?>
                                    <li><?php echo admin_e($error); ?></li>
                                <?php endforeach; ?>
                            </ul>
                        </div>
                    <?php endif; ?>
                    <?php if ($success !== ''): ?>
                        <div class="alert alert-success" role="alert"><?php echo admin_e($success); ?></div>
                    <?php endif; ?>
                    <form method="post" autocomplete="off">
                        <input type="hidden" name="csrf_token" value="<?php echo admin_e($csrfToken); ?>">
                        <div class="mb-3">
                            <label class="form-label" for="username">Käyttäjätunnus</label>
                            <input class="form-control" id="username" name="username" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label" for="password">Salasana</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                            <div class="form-text">Vähintään 12 merkkiä, mielellään erikoismerkkejä käyttäen.</div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label" for="role">Rooli</label>
                            <select class="form-select" id="role" name="role">
                                <option value="admin">Ylläpitäjä</option>
                                <option value="editor">Sisältöeditori</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary">Luo käyttäjä</button>
                    </form>
                </div>
                <div class="card-footer text-muted small">
                    Huomioi tietoturva: vaihda salasana ensimmäisen kirjautumisen jälkeen ja poista tarpeettomat käyttäjät.
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>
