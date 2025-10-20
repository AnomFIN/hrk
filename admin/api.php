<?php
declare(strict_types=1);

require_once __DIR__ . '/init.php';

header('Cache-Control: no-store, no-cache, must-revalidate');

try {
    admin_enforce_session_timeout();
    $currentUser = admin_require_login();
} catch (RuntimeException $e) {
    admin_json_response(403, [
        'success' => false,
        'message' => 'Istunto ei ole voimassa. Kirjaudu sisään uudelleen.',
    ]);
}

$action = $_GET['action'] ?? '';

if ($action === '') {
    admin_json_response(400, [
        'success' => false,
        'message' => 'Toiminto puuttuu.'
    ]);
}

/**
 * Varmistetaan CSRF-token joko headerin tai payloadin kautta.
 */
function api_require_csrf(?array $payload = null): void
{
    $headerToken = $_SERVER['HTTP_X_CSRF_TOKEN'] ?? null;
    $payloadToken = is_array($payload) ? ($payload['csrf_token'] ?? null) : null;
    $token = $headerToken ?: $payloadToken;
    if (!admin_verify_csrf_token($token)) {
        admin_json_response(403, [
            'success' => false,
            'message' => 'CSRF-tarkistus epäonnistui.'
        ]);
    }
}

/**
 * Luetaan JSON-body ja palautetaan taulukko.
 */
function api_read_json_body(): array
{
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);
    if (!is_array($data)) {
        admin_json_response(400, [
            'success' => false,
            'message' => 'Virheellinen JSON-data.'
        ]);
    }
    return $data;
}

switch ($action) {
    case 'list_products':
        $products = admin_read_json('products', []);
        $categories = admin_read_json('categories', []);
        admin_json_response(200, [
            'success' => true,
            'data' => [
                'products' => $products,
                'categories' => $categories,
            ],
        ]);
        break;

    case 'save_product':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            admin_json_response(405, ['success' => false, 'message' => 'Metodi ei ole sallittu.']);
        }
        $payload = api_read_json_body();
        api_require_csrf($payload);

        $name = trim($payload['name'] ?? '');
        $sku = trim($payload['sku'] ?? '');
        $price = isset($payload['price']) ? (float)$payload['price'] : null;

        if ($name === '' || $sku === '' || $price === null) {
            admin_json_response(422, ['success' => false, 'message' => 'Nimi, SKU ja hinta ovat pakollisia.']);
        }

        $products = admin_read_json('products', []);
        $now = gmdate('c');
        $id = $payload['id'] ?? null;
        $isNew = false;

        if ($id) {
            $found = false;
            foreach ($products as &$product) {
                if (($product['id'] ?? '') === $id) {
                    $categoryIds = is_array($payload['categoryids'] ?? null) ? array_map('trim', $payload['categoryids']) : [];
                    $imagePaths = is_array($payload['images'] ?? null) ? array_map('trim', $payload['images']) : [];
                    $product['name'] = $name;
                    $product['slug'] = $product['slug'] ?? admin_slugify($name);
                    $product['sku'] = $sku;
                    $product['price'] = $price;
                    $product['compare_at_price'] = isset($payload['compare_at_price']) && $payload['compare_at_price'] !== null ? (float)$payload['compare_at_price'] : null;
                    $product['stock'] = isset($payload['stock']) ? (int)$payload['stock'] : 0;
                    $product['weightkg'] = isset($payload['weightkg']) && $payload['weightkg'] !== null ? (float)$payload['weightkg'] : null;
                    $product['batterywh'] = isset($payload['batterywh']) && $payload['batterywh'] !== null ? (int)$payload['batterywh'] : null;
                    $product['rangekmestimate'] = isset($payload['rangekmestimate']) && $payload['rangekmestimate'] !== null ? (int)$payload['rangekmestimate'] : null;
                    $product['shortdescription'] = trim($payload['shortdescription'] ?? '');
                    $product['description'] = admin_sanitize_html($payload['description'] ?? '');
                    $product['categoryids'] = array_values(array_filter($categoryIds, fn ($value) => $value !== ''));
                    $product['images'] = array_values(array_filter($imagePaths, fn ($value) => $value !== ''));
                    $product['meta'] = [
                        'title' => trim($payload['meta_title'] ?? ''),
                        'description' => trim($payload['meta_description'] ?? ''),
                    ];
                    $product['updated_at'] = $now;
                    $found = true;
                    break;
                }
            }
            unset($product);
            if (!$found) {
                admin_json_response(404, ['success' => false, 'message' => 'Tuotetta ei löytynyt.']);
            }
        } else {
            $isNew = true;
            $id = admin_generate_id('p');
            $categoryIds = is_array($payload['categoryids'] ?? null) ? array_map('trim', $payload['categoryids']) : [];
            $imagePaths = is_array($payload['images'] ?? null) ? array_map('trim', $payload['images']) : [];
            $products[] = [
                'id' => $id,
                'name' => $name,
                'slug' => admin_slugify($name),
                'sku' => $sku,
                'description' => admin_sanitize_html($payload['description'] ?? ''),
                'shortdescription' => trim($payload['shortdescription'] ?? ''),
                'price' => $price,
                'compare_at_price' => isset($payload['compare_at_price']) && $payload['compare_at_price'] !== null ? (float)$payload['compare_at_price'] : null,
                'currency' => 'EUR',
                'stock' => isset($payload['stock']) ? (int)$payload['stock'] : 0,
                'weightkg' => isset($payload['weightkg']) && $payload['weightkg'] !== null ? (float)$payload['weightkg'] : null,
                'batterywh' => isset($payload['batterywh']) && $payload['batterywh'] !== null ? (int)$payload['batterywh'] : null,
                'rangekmestimate' => isset($payload['rangekmestimate']) && $payload['rangekmestimate'] !== null ? (int)$payload['rangekmestimate'] : null,
                'categoryids' => array_values(array_filter($categoryIds, fn ($value) => $value !== '')),
                'images' => array_values(array_filter($imagePaths, fn ($value) => $value !== '')),
                'attributes' => $payload['attributes'] ?? [],
                'meta' => [
                    'title' => trim($payload['meta_title'] ?? ''),
                    'description' => trim($payload['meta_description'] ?? ''),
                ],
                'created_at' => $now,
                'updated_at' => $now,
            ];
        }

        if (!admin_write_json('products', $products)) {
            admin_json_response(500, ['success' => false, 'message' => 'Tallennus epäonnistui.']);
        }

        admin_log_action($currentUser['username'], $isNew ? 'create_product' : 'update_product', $id, ['name' => $name]);

        admin_json_response(200, [
            'success' => true,
            'message' => $isNew ? 'Tuote luotu.' : 'Tuote päivitetty.'
        ]);
        break;

    case 'delete_product':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            admin_json_response(405, ['success' => false, 'message' => 'Metodi ei ole sallittu.']);
        }
        $payload = api_read_json_body();
        api_require_csrf($payload);
        $id = $payload['id'] ?? '';
        if ($id === '') {
            admin_json_response(422, ['success' => false, 'message' => 'Puuttuva tuotetunnus.']);
        }
        $products = admin_read_json('products', []);
        $before = count($products);
        $products = array_values(array_filter($products, fn ($item) => ($item['id'] ?? '') !== $id));
        if ($before === count($products)) {
            admin_json_response(404, ['success' => false, 'message' => 'Tuotetta ei löytynyt.']);
        }
        if (!admin_write_json('products', $products)) {
            admin_json_response(500, ['success' => false, 'message' => 'Poisto epäonnistui.']);
        }
        admin_log_action($currentUser['username'], 'delete_product', $id, []);
        admin_json_response(200, ['success' => true, 'message' => 'Tuote poistettu.']);
        break;

    case 'export_products':
        api_require_csrf();
        $products = admin_read_json('products', []);
        admin_log_action($currentUser['username'], 'export_products', 'products', ['count' => count($products)]);
        $csvLines = [];
        $headers = ['id', 'name', 'sku', 'price', 'stock', 'categories', 'updated_at'];
        $csvLines[] = implode(';', $headers);
        foreach ($products as $product) {
            $csvLines[] = implode(';', [
                $product['id'] ?? '',
                str_replace(';', ',', $product['name'] ?? ''),
                $product['sku'] ?? '',
                (string)($product['price'] ?? ''),
                (string)($product['stock'] ?? ''),
                implode(',', $product['categoryids'] ?? []),
                $product['updated_at'] ?? '',
            ]);
        }
        $csv = implode("\n", $csvLines);
        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="hrk_products.csv"');
        echo $csv;
        exit;

    case 'list_orders':
        $orders = admin_read_json('orders', []);
        admin_json_response(200, ['success' => true, 'data' => ['orders' => $orders]]);
        break;

    case 'update_order_status':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            admin_json_response(405, ['success' => false, 'message' => 'Metodi ei ole sallittu.']);
        }
        $payload = api_read_json_body();
        api_require_csrf($payload);
        $id = $payload['id'] ?? '';
        $status = $payload['status'] ?? '';
        $allowed = ['pending', 'paid', 'shipped', 'cancelled'];
        if ($id === '' || !in_array($status, $allowed, true)) {
            admin_json_response(422, ['success' => false, 'message' => 'Virheellinen tila tai tunnus.']);
        }
        $orders = admin_read_json('orders', []);
        $found = false;
        foreach ($orders as &$order) {
            if (($order['id'] ?? '') === $id) {
                $order['status'] = $status;
                $order['updated_at'] = gmdate('c');
                $found = true;
                break;
            }
        }
        unset($order);
        if (!$found) {
            admin_json_response(404, ['success' => false, 'message' => 'Tilausta ei löytynyt.']);
        }
        if (!admin_write_json('orders', $orders)) {
            admin_json_response(500, ['success' => false, 'message' => 'Tallennus epäonnistui.']);
        }
        admin_log_action($currentUser['username'], 'update_order', $id, ['status' => $status]);
        admin_json_response(200, ['success' => true, 'message' => 'Tilauksen tila päivitetty.']);
        break;

    case 'list_pages':
        $pages = admin_read_json('pages', ['home_sections' => [], 'custom_pages' => []]);
        admin_json_response(200, ['success' => true, 'data' => $pages]);
        break;

    case 'save_page':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            admin_json_response(405, ['success' => false, 'message' => 'Metodi ei ole sallittu.']);
        }
        $payload = api_read_json_body();
        api_require_csrf($payload);
        $id = $payload['id'] ?? null;
        $title = trim($payload['title'] ?? '');
        $slug = trim($payload['slug'] ?? '');
        $content = admin_sanitize_html($payload['content'] ?? '');
        if ($title === '' || $slug === '') {
            admin_json_response(422, ['success' => false, 'message' => 'Otsikko ja slug ovat pakollisia.']);
        }
        $pages = admin_read_json('pages', ['home_sections' => [], 'custom_pages' => []]);
        $isNew = false;
        if ($id) {
            $found = false;
            foreach ($pages['custom_pages'] as &$page) {
                if (($page['id'] ?? '') === $id) {
                    $page['title'] = $title;
                    $page['slug'] = $slug;
                    $page['content'] = $content;
                    $page['updated_at'] = gmdate('c');
                    $found = true;
                    break;
                }
            }
            unset($page);
            if (!$found) {
                admin_json_response(404, ['success' => false, 'message' => 'Sivua ei löytynyt.']);
            }
        } else {
            $isNew = true;
            $pages['custom_pages'][] = [
                'id' => admin_generate_id('pg'),
                'title' => $title,
                'slug' => $slug,
                'content' => $content,
                'created_at' => gmdate('c'),
                'updated_at' => gmdate('c'),
            ];
        }
        if (!admin_write_json('pages', $pages)) {
            admin_json_response(500, ['success' => false, 'message' => 'Tallennus epäonnistui.']);
        }
        admin_log_action($currentUser['username'], $isNew ? 'create_page' : 'update_page', $slug, []);
        admin_json_response(200, ['success' => true, 'message' => 'Sivu tallennettu.']);
        break;

    case 'delete_page':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            admin_json_response(405, ['success' => false, 'message' => 'Metodi ei ole sallittu.']);
        }
        $payload = api_read_json_body();
        api_require_csrf($payload);
        $id = $payload['id'] ?? '';
        if ($id === '') {
            admin_json_response(422, ['success' => false, 'message' => 'Puuttuva tunniste.']);
        }
        $pages = admin_read_json('pages', ['home_sections' => [], 'custom_pages' => []]);
        $before = count($pages['custom_pages']);
        $pages['custom_pages'] = array_values(array_filter($pages['custom_pages'], fn ($page) => ($page['id'] ?? '') !== $id));
        if ($before === count($pages['custom_pages'])) {
            admin_json_response(404, ['success' => false, 'message' => 'Sivua ei löytynyt.']);
        }
        if (!admin_write_json('pages', $pages)) {
            admin_json_response(500, ['success' => false, 'message' => 'Poisto epäonnistui.']);
        }
        admin_log_action($currentUser['username'], 'delete_page', $id, []);
        admin_json_response(200, ['success' => true, 'message' => 'Sivu poistettu.']);
        break;

    case 'get_settings':
        $settings = admin_read_json('settings', []);
        admin_json_response(200, ['success' => true, 'data' => ['settings' => $settings]]);
        break;

    case 'save_settings':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            admin_json_response(405, ['success' => false, 'message' => 'Metodi ei ole sallittu.']);
        }
        $payload = api_read_json_body();
        api_require_csrf($payload);
        $settings = admin_read_json('settings', []);
        $settings['site_title'] = trim($payload['site_title'] ?? $settings['site_title'] ?? '');
        $contact = is_array($payload['contact'] ?? null) ? $payload['contact'] : [];
        $hero = is_array($payload['hero'] ?? null) ? $payload['hero'] : [];
        $payment = is_array($payload['payment'] ?? null) ? $payload['payment'] : [];
        $seo = is_array($payload['seo_defaults'] ?? null) ? $payload['seo_defaults'] : [];

        $settings['contact'] = [
            'email' => filter_var($contact['email'] ?? '', FILTER_SANITIZE_EMAIL),
            'phone' => trim($contact['phone'] ?? ''),
            'business_id' => trim($contact['business_id'] ?? ''),
        ];
        $settings['hero'] = [
            'title' => trim($hero['title'] ?? ''),
            'subtitle' => trim($hero['subtitle'] ?? ''),
            'image' => trim($hero['image'] ?? ''),
            'cta_text' => trim($hero['cta_text'] ?? ''),
            'cta_link' => trim($hero['cta_link'] ?? ''),
        ];
        $settings['payment'] = [
            'methods' => array_values(array_filter(is_array($payment['methods'] ?? null) ? array_map('trim', $payment['methods']) : [], fn ($value) => $value !== '')),
            'show_installments' => (bool)($payment['show_installments'] ?? false),
        ];
        $settings['seo_defaults'] = [
            'meta_title' => trim($seo['meta_title'] ?? ''),
            'meta_description' => trim($seo['meta_description'] ?? ''),
        ];
        if (!admin_write_json('settings', $settings)) {
            admin_json_response(500, ['success' => false, 'message' => 'Tallennus epäonnistui.']);
        }
        admin_log_action($currentUser['username'], 'update_settings', 'settings', []);
        admin_json_response(200, ['success' => true, 'message' => 'Asetukset tallennettu.']);
        break;

    case 'list_users':
        $users = admin_read_json('users', []);
        $sanitized = array_map(fn ($user) => [
            'id' => $user['id'] ?? '',
            'username' => $user['username'] ?? '',
            'role' => $user['role'] ?? 'admin',
            'created_at' => $user['createdat'] ?? $user['created_at'] ?? '',
        ], $users);
        admin_json_response(200, ['success' => true, 'data' => ['users' => $sanitized]]);
        break;

    case 'get_logs':
        api_require_csrf();
        if (!file_exists(ADMIN_LOG_FILE)) {
            echo "Ei lokitietoja.";
            exit;
        }
        header('Content-Type: text/plain; charset=utf-8');
        readfile(ADMIN_LOG_FILE);
        exit;

    default:
        admin_json_response(404, ['success' => false, 'message' => 'Tuntematon toiminto.']);
}
