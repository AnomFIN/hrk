<?php
declare(strict_types=1);

$paths = [
    __DIR__ . '/../data' => 'data/',
    __DIR__ . '/../uploads' => 'uploads/',
    __DIR__ . '/../logs' => 'logs/',
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
