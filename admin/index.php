<?php
declare(strict_types=1);

require_once __DIR__ . '/init.php';

try {
    admin_enforce_session_timeout();
} catch (RuntimeException $e) {
    header('Location: login.php?timeout=1');
    exit;
}

try {
    $currentUser = admin_require_login();
} catch (RuntimeException $e) {
    header('Location: login.php');
    exit;
}

$csrfToken = admin_get_csrf_token();
$products = admin_read_json('products', []);
$orders = admin_read_json('orders', []);
$logLines = [];
if (file_exists(ADMIN_LOG_FILE)) {
    $lines = array_slice(file(ADMIN_LOG_FILE, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) ?: [], -50);
    foreach ($lines as $line) {
        $decoded = json_decode($line, true);
        if (is_array($decoded)) {
            $logLines[] = $decoded;
        }
    }
}

// Lasketaan nopeita tilastoja dashboardiin
$totalProducts = count($products);
$totalOrders = count($orders);
$pendingOrders = count(array_filter($orders, fn ($order) => ($order['status'] ?? '') === 'pending'));
$totalRevenue = array_reduce($orders, fn ($carry, $order) => $carry + (float)($order['total'] ?? 0), 0.0);
?>
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>HRK Admin | Hallintapaneeli</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="assets/css/admin.css">
    <meta name="csrf-token" content="<?php echo admin_e($csrfToken); ?>">
</head>
<body>
<nav class="navbar navbar-dark bg-dark navbar-expand-lg">
    <div class="container-fluid">
        <a class="navbar-brand" href="#">HRK Admin</a>
        <div class="d-flex align-items-center text-white">
            <span class="me-3"><?php echo admin_e('Hei ' . ($currentUser['username'] ?? 'admin')); ?></span>
            <a class="btn btn-sm btn-outline-light" href="logout.php">Kirjaudu ulos</a>
        </div>
    </div>
</nav>
<div id="alert-container" class="position-fixed top-0 end-0 p-3" style="z-index: 1080;"></div>
<div class="container-fluid">
    <div class="row">
        <aside class="col-md-3 col-lg-2 bg-light sidebar py-4">
            <nav class="nav flex-column">
                <a class="nav-link active" href="#" data-section="dashboard">Dashboard</a>
                <a class="nav-link" href="#" data-section="products">Tuotteet</a>
                <a class="nav-link" href="#" data-section="orders">Tilaukset</a>
                <a class="nav-link" href="#" data-section="pages">Sivut</a>
                <a class="nav-link" href="#" data-section="settings">Asetukset</a>
                <a class="nav-link" href="#" data-section="users">Käyttäjät</a>
                <a class="nav-link" href="#" data-section="logs">Lokit</a>
            </nav>
        </aside>
        <main class="col-md-9 col-lg-10 ms-sm-auto px-4 py-4">
            <section id="section-dashboard" class="section-view">
                <div class="row g-3">
                    <div class="col-md-3">
                        <div class="card shadow-sm">
                            <div class="card-body">
                                <h2 class="h6 text-muted">Tuotteet</h2>
                                <p class="h3 mb-0"><?php echo admin_e((string)$totalProducts); ?></p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card shadow-sm">
                            <div class="card-body">
                                <h2 class="h6 text-muted">Tilaukset</h2>
                                <p class="h3 mb-0"><?php echo admin_e((string)$totalOrders); ?></p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card shadow-sm">
                            <div class="card-body">
                                <h2 class="h6 text-muted">Avoimet tilaukset</h2>
                                <p class="h3 mb-0"><?php echo admin_e((string)$pendingOrders); ?></p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card shadow-sm">
                            <div class="card-body">
                                <h2 class="h6 text-muted">Kertynyt liikevaihto</h2>
                                <p class="h3 mb-0">€<?php echo admin_e(number_format($totalRevenue, 2, ',', ' ')); ?></p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row g-3 mt-4">
                    <div class="col-lg-7">
                        <div class="card shadow-sm h-100">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h2 class="h5 mb-0">Viimeisimmät tuotteet</h2>
                                <button class="btn btn-sm btn-primary" id="btn-open-product-modal">Lisää tuote</button>
                            </div>
                            <div class="card-body">
                                <div id="recent-products"></div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-5">
                        <div class="card shadow-sm h-100">
                            <div class="card-header">
                                <h2 class="h5 mb-0">Viimeisimmät toimet</h2>
                            </div>
                            <div class="card-body">
                                <ul class="list-unstyled recent-actions" id="recent-actions">
                                    <?php if (empty($logLines)): ?>
                                        <li class="text-muted">Ei kirjattuja tapahtumia.</li>
                                    <?php else: ?>
                                        <?php foreach (array_reverse($logLines) as $entry): ?>
                                            <li>
                                                <strong><?php echo admin_e($entry['user'] ?? 'tuntematon'); ?></strong>
                                                <span class="text-muted"><?php echo admin_e($entry['action'] ?? ''); ?></span>
                                                <div class="small text-muted"><?php echo admin_e($entry['timestamp'] ?? ''); ?></div>
                                            </li>
                                        <?php endforeach; ?>
                                    <?php endif; ?>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section id="section-products" class="section-view d-none">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h2>Tuotteet</h2>
                        <p class="text-muted mb-0">Hallitse verkkokaupan tuotteita ja vie listauksia CSV-muotoon.</p>
                    </div>
                    <div>
                        <button class="btn btn-primary" id="btn-add-product">Lisää tuote</button>
                        <button class="btn btn-outline-secondary" id="btn-export-products">Vie CSV</button>
                    </div>
                </div>
                <div class="card shadow-sm">
                    <div class="card-body">
                        <div class="row g-3 mb-3">
                            <div class="col-md-3">
                                <label for="filter-category" class="form-label">Kategoria</label>
                                <select id="filter-category" class="form-select">
                                    <option value="">Kaikki</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label for="filter-stock" class="form-label">Varastosaldo</label>
                                <select id="filter-stock" class="form-select">
                                    <option value="">Kaikki</option>
                                    <option value="in_stock">Varastossa</option>
                                    <option value="out_of_stock">Loppu</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label for="filter-price" class="form-label">Hinta</label>
                                <select id="filter-price" class="form-select">
                                    <option value="">Kaikki</option>
                                    <option value="lt1000">Alle 1000 €</option>
                                    <option value="btw1000and3000">1000–3000 €</option>
                                    <option value="gt3000">Yli 3000 €</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label" for="search-products">Hakusana</label>
                                <input type="search" id="search-products" class="form-control" placeholder="Etsi nimellä tai SKU:lla">
                            </div>
                        </div>
                        <div class="table-responsive">
                            <table class="table table-striped align-middle" id="products-table">
                                <thead>
                                    <tr>
                                        <th>Nimi</th>
                                        <th>SKU</th>
                                        <th>Hinta</th>
                                        <th>Varasto</th>
                                        <th>Kategoriat</th>
                                        <th>Päivitetty</th>
                                        <th></th>
                                    </tr>
                                </thead>
                                <tbody>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </section>

            <section id="section-orders" class="section-view d-none">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h2>Tilaukset</h2>
                        <p class="text-muted mb-0">Seuraa tilauksia ja päivitä tilaa.</p>
                    </div>
                    <div class="d-flex gap-2">
                        <select id="filter-order-status" class="form-select form-select-sm">
                            <option value="">Kaikki tilat</option>
                            <option value="pending">Odottaa maksua</option>
                            <option value="paid">Maksettu</option>
                            <option value="shipped">Toimitettu</option>
                            <option value="cancelled">Peruttu</option>
                        </select>
                        <button class="btn btn-outline-secondary btn-sm" id="btn-refresh-orders">Päivitä</button>
                    </div>
                </div>
                <div class="card shadow-sm">
                    <div class="table-responsive">
                        <table class="table table-hover mb-0" id="orders-table">
                            <thead>
                                <tr>
                                    <th>Tilaus</th>
                                    <th>Asiakas</th>
                                    <th>Kokonaishinta</th>
                                    <th>Tila</th>
                                    <th>Luotu</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </section>

            <section id="section-pages" class="section-view d-none">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h2>Sivut</h2>
                        <p class="text-muted mb-0">Muokkaa kotisivun osioita ja vapaamuotoisia sivuja.</p>
                    </div>
                    <button class="btn btn-primary" id="btn-add-page">Lisää sivu</button>
                </div>
                <div class="row g-3">
                    <div class="col-lg-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header">
                                <h3 class="h5 mb-0">Kotisivun osiot</h3>
                            </div>
                            <div class="card-body" id="home-sections"></div>
                        </div>
                    </div>
                    <div class="col-lg-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header">
                                <h3 class="h5 mb-0">Mukautetut sivut</h3>
                            </div>
                            <div class="card-body" id="custom-pages"></div>
                        </div>
                    </div>
                </div>
            </section>

            <section id="section-settings" class="section-view d-none">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h2>Asetukset</h2>
                        <p class="text-muted mb-0">Yrityksen perustiedot, hero-osio ja SEO-asetukset.</p>
                    </div>
                    <button class="btn btn-primary" id="btn-save-settings">Tallenna asetukset</button>
                </div>
                <form id="settings-form" class="card shadow-sm p-3">
                    <h3 class="h5">Yleiset</h3>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label" for="settings-site-title">Sivuston otsikko</label>
                            <input class="form-control" id="settings-site-title" name="site_title" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label" for="settings-contact-email">Sähköposti</label>
                            <input type="email" class="form-control" id="settings-contact-email" name="contact[email]" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label" for="settings-contact-phone">Puhelin</label>
                            <input class="form-control" id="settings-contact-phone" name="contact[phone]">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label" for="settings-business-id">Y-tunnus</label>
                            <input class="form-control" id="settings-business-id" name="contact[business_id]">
                        </div>
                    </div>
                    <hr>
                    <h3 class="h5">Hero-osio</h3>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label" for="hero-title">Otsikko</label>
                            <input class="form-control" id="hero-title" name="hero[title]">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label" for="hero-subtitle">Alaotsikko</label>
                            <input class="form-control" id="hero-subtitle" name="hero[subtitle]">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label" for="hero-image">Kuva</label>
                            <input class="form-control" id="hero-image" name="hero[image]">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label" for="hero-cta-text">CTA-teksti</label>
                            <input class="form-control" id="hero-cta-text" name="hero[cta_text]">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label" for="hero-cta-link">CTA-linkki</label>
                            <input class="form-control" id="hero-cta-link" name="hero[cta_link]">
                        </div>
                    </div>
                    <hr>
                    <h3 class="h5">Maksutavat</h3>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label" for="payment-methods">Maksutavat (pilkulla erotettuna)</label>
                            <input class="form-control" id="payment-methods" name="payment[methods]">
                        </div>
                        <div class="col-md-6 form-check form-switch mt-4">
                            <input class="form-check-input" type="checkbox" role="switch" id="payment-installments" name="payment[show_installments]">
                            <label class="form-check-label" for="payment-installments">Näytä osamaksuvaihtoehdot</label>
                        </div>
                    </div>
                    <hr>
                    <h3 class="h5">SEO-oletukset</h3>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label" for="seo-title">Meta title</label>
                            <input class="form-control" id="seo-title" name="seo_defaults[meta_title]">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label" for="seo-description">Meta description</label>
                            <textarea class="form-control" id="seo-description" name="seo_defaults[meta_description]" rows="3"></textarea>
                        </div>
                    </div>
                </form>
            </section>

            <section id="section-users" class="section-view d-none">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h2>Käyttäjät</h2>
                        <p class="text-muted mb-0">Ylläpitäjät ja käyttöoikeudet.</p>
                    </div>
                    <a class="btn btn-outline-secondary" href="create_admin.php">Luo uusi käyttäjä</a>
                </div>
                <div class="card shadow-sm">
                    <div class="table-responsive">
                        <table class="table mb-0" id="users-table">
                            <thead>
                                <tr>
                                    <th>Käyttäjä</th>
                                    <th>Rooli</th>
                                    <th>Luotu</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </section>

            <section id="section-logs" class="section-view d-none">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h2>Audit-logi</h2>
                    <button class="btn btn-outline-secondary" id="btn-refresh-logs">Päivitä</button>
                </div>
                <div class="card shadow-sm">
                    <div class="card-body">
                        <pre class="small" id="logs-view" aria-live="polite"></pre>
                    </div>
                </div>
            </section>
        </main>
    </div>
</div>

<!-- Tuotteen modaalilomake -->
<div class="modal fade" id="productModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
            <form id="product-form">
                <div class="modal-header">
                    <h5 class="modal-title" id="productModalLabel">Tuote</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Sulje"></button>
                </div>
                <div class="modal-body">
                    <input type="hidden" name="id" id="product-id">
                    <input type="hidden" name="csrf_token" value="<?php echo admin_e($csrfToken); ?>">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label" for="product-name">Nimi</label>
                            <input class="form-control" id="product-name" name="name" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label" for="product-sku">SKU</label>
                            <input class="form-control" id="product-sku" name="sku" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label" for="product-price">Hinta (€)</label>
                            <input type="number" step="0.01" class="form-control" id="product-price" name="price" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label" for="product-compare">Verrokkihinta (€)</label>
                            <input type="number" step="0.01" class="form-control" id="product-compare" name="compare_at_price">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label" for="product-stock">Varasto</label>
                            <input type="number" class="form-control" id="product-stock" name="stock" min="0">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label" for="product-weight">Paino (kg)</label>
                            <input type="number" step="0.01" class="form-control" id="product-weight" name="weightkg">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label" for="product-battery">Akku (Wh)</label>
                            <input type="number" class="form-control" id="product-battery" name="batterywh" min="0">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label" for="product-range">Toimintamatka (km)</label>
                            <input type="number" class="form-control" id="product-range" name="rangekmestimate">
                        </div>
                        <div class="col-12">
                            <label class="form-label" for="product-short">Lyhyt kuvaus</label>
                            <textarea class="form-control" id="product-short" name="shortdescription" rows="2"></textarea>
                        </div>
                        <div class="col-12">
                            <label class="form-label" for="product-description">Laaja kuvaus</label>
                            <textarea class="form-control" id="product-description" name="description" rows="4"></textarea>
                        </div>
                        <div class="col-12">
                            <label class="form-label" for="product-categories">Kategoriat (pilkulla eroteltuna)</label>
                            <input class="form-control" id="product-categories" name="categoryids">
                        </div>
                        <div class="col-12">
                            <label class="form-label" for="product-images">Kuvat (URL, pilkulla eroteltu)</label>
                            <input class="form-control" id="product-images" name="images">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label" for="product-meta-title">SEO title</label>
                            <input class="form-control" id="product-meta-title" name="meta_title">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label" for="product-meta-desc">SEO description</label>
                            <textarea class="form-control" id="product-meta-desc" name="meta_description" rows="2"></textarea>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Peruuta</button>
                    <button type="submit" class="btn btn-primary">Tallenna</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Sivun muokkausmodaali -->
<div class="modal fade" id="pageModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <form id="page-form">
                <div class="modal-header">
                    <h5 class="modal-title">Mukautettu sivu</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <input type="hidden" name="csrf_token" value="<?php echo admin_e($csrfToken); ?>">
                    <input type="hidden" id="page-id" name="id">
                    <div class="mb-3">
                        <label class="form-label" for="page-title">Otsikko</label>
                        <input class="form-control" id="page-title" name="title" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label" for="page-slug">Polku (slug)</label>
                        <input class="form-control" id="page-slug" name="slug" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label" for="page-content">Sisältö (HTML)</label>
                        <textarea class="form-control" id="page-content" name="content" rows="6"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Sulje</button>
                    <button type="submit" class="btn btn-primary">Tallenna</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="assets/js/admin.js"></script>
</body>
</html>
