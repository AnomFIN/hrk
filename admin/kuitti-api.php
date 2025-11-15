<?php
/**
 * LV Electronics - Kuittitulostus API
 * PHP-backend kuitin käsittelyyn ja tulostukseen
 */

// Salli CORS pyyntöjä
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Käsittele OPTIONS pyyntö (preflight)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// ========== KONFIGURAATIO ==========
define('YRITYS_NIMI', 'LV Electronics');
define('YRITYS_OSOITE', 'Hämeentie 123, 00500 Helsinki');
define('YRITYS_PUHELIN', 'Tel: +358 50 123 4567');
define('YRITYS_Y_TUNNUS', 'Y-tunnus: 1234567-8');
define('ALV_KANTA', 0.24);

// ASCII Logo
define('ASCII_LOGO', "╔═══════════════════════════╗
║                           ║
║    ██╗     ██╗   ██╗     ║
║    ██║     ██║   ██║     ║
║    ██║     ██║   ██║     ║
║    ██║     ╚██╗ ██╔╝     ║
║    ███████╗ ╚████╔╝      ║
║    ╚══════╝  ╚═══╝       ║
║                           ║
║   LV Electronics          ║
║                           ║
╚═══════════════════════════╝");

// ========== APUFUNKTIOT ==========

/**
 * Logaa toiminnot tiedostoon
 */
function logTapahtuma($viesti) {
    $logTiedosto = __DIR__ . '/logs/kuitti_log.txt';
    
    // Varmista logs-kansio
    if (!is_dir(__DIR__ . '/logs')) {
        mkdir(__DIR__ . '/logs', 0755, true);
    }
    
    $aikaleima = date('Y-m-d H:i:s');
    $logRivi = "[$aikaleima] $viesti" . PHP_EOL;
    
    file_put_contents($logTiedosto, $logRivi, FILE_APPEND | LOCK_EX);
}

/**
 * Palauta JSON-vastaus
 */
function jsonVastaus($data, $httpKoodi = 200) {
    http_response_code($httpKoodi);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit;
}

/**
 * Palauta virheviesti
 */
function virheVastaus($viesti, $httpKoodi = 400) {
    logTapahtuma("VIRHE: $viesti");
    jsonVastaus(['success' => false, 'error' => $viesti], $httpKoodi);
}

/**
 * Validoi tuotedata
 */
function validoiTuote($tuote) {
    if (!isset($tuote['nimi']) || empty(trim($tuote['nimi']))) {
        return 'Tuotteen nimi puuttuu';
    }
    
    if (!isset($tuote['maara']) || !is_numeric($tuote['maara']) || $tuote['maara'] <= 0) {
        return 'Virheellinen määrä';
    }
    
    if (!isset($tuote['hinta']) || !is_numeric($tuote['hinta']) || $tuote['hinta'] < 0) {
        return 'Virheellinen hinta';
    }
    
    return null;
}

/**
 * Laske kuitin summat
 */
function laskeSummat($tuotteet) {
    $valisumma = 0;
    
    foreach ($tuotteet as $tuote) {
        $valisumma += $tuote['maara'] * $tuote['hinta'];
    }
    
    $alv = $valisumma * ALV_KANTA;
    $kokonaissumma = $valisumma + $alv;
    
    return [
        'valisumma' => round($valisumma, 2),
        'alv' => round($alv, 2),
        'kokonaissumma' => round($kokonaissumma, 2)
    ];
}

/**
 * Muodosta kuittiteksti
 */
function muodostaKuittiteksti($tuotteet, $kuittinumero = null) {
    $kuittinumero = $kuittinumero ?? uniqid('KU');
    $pvm = date('d.m.Y H:i:s');
    
    $kuitti = ASCII_LOGO . "\n\n";
    $kuitti .= YRITYS_NIMI . "\n";
    $kuitti .= YRITYS_OSOITE . "\n";
    $kuitti .= YRITYS_PUHELIN . "\n";
    $kuitti .= YRITYS_Y_TUNNUS . "\n\n";
    $kuitti .= str_repeat("=", 50) . "\n";
    $kuitti .= "KUITTI #{$kuittinumero} - {$pvm}\n";
    $kuitti .= str_repeat("=", 50) . "\n\n";
    
    if (!empty($tuotteet)) {
        $kuitti .= sprintf("%-25s %5s %10s %10s\n", 'Tuote', 'Määrä', 'À hinta', 'Yht.');
        $kuitti .= str_repeat("-", 50) . "\n";
        
        foreach ($tuotteet as $tuote) {
            $nimi = mb_strlen($tuote['nimi']) > 25 ? 
                    mb_substr($tuote['nimi'], 0, 22) . '...' : 
                    $tuote['nimi'];
            
            $yhteensa = $tuote['maara'] * $tuote['hinta'];
            
            $kuitti .= sprintf(
                "%-25s %5d %9.2f€ %9.2f€\n",
                $nimi,
                $tuote['maara'],
                $tuote['hinta'],
                $yhteensa
            );
        }
    }
    
    $summat = laskeSummat($tuotteet);
    
    $kuitti .= "\n" . str_repeat("-", 50) . "\n";
    $kuitti .= sprintf("%-30s %17.2f€\n", 'Välisumma (veroton):', $summat['valisumma']);
    $kuitti .= sprintf("%-30s %17.2f€\n", 'ALV 24%:', $summat['alv']);
    $kuitti .= str_repeat("=", 50) . "\n";
    $kuitti .= sprintf("%-30s %17.2f€\n", 'YHTEENSÄ:', $summat['kokonaissumma']);
    $kuitti .= str_repeat("=", 50) . "\n\n";
    $kuitti .= "Kiitos käynnistänne!\n\n";
    
    return $kuitti;
}

/**
 * Tallenna kuitti tiedostoon
 */
function tallennaKuitti($kuittiteksti, $kuittinumero) {
    $kansio = __DIR__ . '/data/kuitit';
    
    // Varmista kansio
    if (!is_dir($kansio)) {
        mkdir($kansio, 0755, true);
    }
    
    $tiedostonimi = $kansio . "/kuitti_{$kuittinumero}_" . date('Ymd_His') . ".txt";
    
    if (file_put_contents($tiedostonimi, $kuittiteksti, LOCK_EX) !== false) {
        return $tiedostonimi;
    }
    
    return false;
}

/**
 * Tulosta kuitti (Linux/Windows)
 */
function tulostaKuitti($kuittiteksti) {
    try {
        if (PHP_OS_FAMILY === 'Windows') {
            // Windows: Luo temp-tiedosto ja tulosta notepadilla
            $tempTiedosto = tempnam(sys_get_temp_dir(), 'kuitti_') . '.txt';
            file_put_contents($tempTiedosto, $kuittiteksti);
            
            $komento = "notepad /p \"$tempTiedosto\"";
            $output = [];
            $palautuskoodi = 0;
            exec($komento, $output, $palautuskoodi);
            
            // Poista temp-tiedosto hetken kuluttua
            register_shutdown_function(function() use ($tempTiedosto) {
                if (file_exists($tempTiedosto)) {
                    unlink($tempTiedosto);
                }
            });
            
            return $palautuskoodi === 0;
            
        } else {
            // Linux/Unix: Käytä lp tai lpr
            $komennot = ['lp', 'lpr'];
            
            foreach ($komennot as $komento) {
                if (shell_exec("which $komento")) {
                    $process = proc_open(
                        $komento,
                        [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']],
                        $pipes
                    );
                    
                    if (is_resource($process)) {
                        fwrite($pipes[0], $kuittiteksti);
                        fclose($pipes[0]);
                        
                        $palautuskoodi = proc_close($process);
                        return $palautuskoodi === 0;
                    }
                }
            }
            
            return false;
        }
    } catch (Exception $e) {
        logTapahtuma("Tulostusvirhe: " . $e->getMessage());
        return false;
    }
}

// ========== API-ENDPOINTIT ==========

$method = $_SERVER['REQUEST_METHOD'];
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$uri = str_replace('/kuitti-api.php', '', $uri);

switch ($method) {
    case 'POST':
        handlePost($uri);
        break;
        
    case 'GET':
        handleGet($uri);
        break;
        
    default:
        virheVastaus('Metodi ei tuettu', 405);
}

/**
 * Käsittele POST-pyynnöt
 */
function handlePost($uri) {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if ($input === null) {
        virheVastaus('Virheellinen JSON-data');
    }
    
    switch ($uri) {
        case '/tulosta':
        case '':
            // Tulosta kuitti
            if (!isset($input['tuotteet']) || !is_array($input['tuotteet'])) {
                virheVastaus('Tuotteet puuttuvat');
            }
            
            // Validoi tuotteet
            foreach ($input['tuotteet'] as $tuote) {
                $virhe = validoiTuote($tuote);
                if ($virhe) {
                    virheVastaus("Tuotevirhe: $virhe");
                }
            }
            
            if (empty($input['tuotteet'])) {
                virheVastaus('Ei tuotteita kuitilla');
            }
            
            $kuittinumero = uniqid('KU');
            $kuittiteksti = muodostaKuittiteksti($input['tuotteet'], $kuittinumero);
            
            // Tallenna kuitti
            $tiedostonimi = tallennaKuitti($kuittiteksti, $kuittinumero);
            
            // Yritä tulostaa
            $tulostusOnnistui = false;
            if (isset($input['tulosta']) && $input['tulosta'] === true) {
                $tulostusOnnistui = tulostaKuitti($kuittiteksti);
            }
            
            $summat = laskeSummat($input['tuotteet']);
            
            logTapahtuma("Kuitti luotu: $kuittinumero, tuotteita: " . count($input['tuotteet']) . 
                        ", summa: {$summat['kokonaissumma']}€" . 
                        ($tulostusOnnistui ? ', tulostettu' : ''));
            
            jsonVastaus([
                'success' => true,
                'kuittinumero' => $kuittinumero,
                'kuittiteksti' => $kuittiteksti,
                'summat' => $summat,
                'tulostettu' => $tulostusOnnistui,
                'tallennettu' => $tiedostonimi !== false,
                'tiedosto' => $tiedostonimi ? basename($tiedostonimi) : null
            ]);
            break;
            
        default:
            virheVastaus('Tuntematon endpoint', 404);
    }
}

/**
 * Käsittele GET-pyynnöt
 */
function handleGet($uri) {
    switch ($uri) {
        case '/status':
        case '':
            // Palautustila-info
            jsonVastaus([
                'success' => true,
                'yritys' => YRITYS_NIMI,
                'versio' => '1.0',
                'php_versio' => PHP_VERSION,
                'käyttöjärjestelmä' => PHP_OS_FAMILY,
                'aika' => date('Y-m-d H:i:s'),
                'tulostus_tuettu' => PHP_OS_FAMILY === 'Windows' || 
                                   shell_exec('which lp') || 
                                   shell_exec('which lpr')
            ]);
            break;
            
        case '/kuitit':
            // Listaa tallennetut kuitit
            $kansio = __DIR__ . '/data/kuitit';
            $kuitit = [];
            
            if (is_dir($kansio)) {
                $tiedostot = scandir($kansio);
                foreach ($tiedostot as $tiedosto) {
                    if (pathinfo($tiedosto, PATHINFO_EXTENSION) === 'txt') {
                        $polku = $kansio . '/' . $tiedosto;
                        $kuitit[] = [
                            'tiedosto' => $tiedosto,
                            'koko' => filesize($polku),
                            'luotu' => date('Y-m-d H:i:s', filemtime($polku))
                        ];
                    }
                }
            }
            
            jsonVastaus([
                'success' => true,
                'kuitit' => $kuitit
            ]);
            break;
            
        default:
            virheVastaus('Tuntematon endpoint', 404);
    }
}
?>