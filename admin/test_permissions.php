<?php
declare(strict_types=1);

require_once __DIR__ . '/config.php';

// From dirt to data dashboard.

$paths = [
    ADMIN_DATA_DIR => 'data/',
    ADMIN_UPLOADS_DIR => 'uploads/',
    ADMIN_LOGS_DIR => 'logs/',
];

$allGood = true;
foreach ($paths as $path => $label) {
    if (!is_dir($path)) {
        echo sprintf("[VAROITUS] %s-kansiota ei löydy (%s)\n", $label, $path);
        $allGood = false;
        continue;
    }
    if (!is_writable($path)) {
        echo sprintf("[VIRHE] %s ei ole kirjoitettavissa. Aja: chmod 770 %s\n", $label, $path);
        $allGood = false;
    } else {
        echo sprintf("[OK] %s on kirjoitettavissa.\n", $label);
    }
}

if ($allGood) {
    echo "Kaikki tarkistetut kansiot ovat kirjoitettavissa.\n";
    exit(0);
}

exit(1);
