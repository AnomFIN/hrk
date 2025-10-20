/*
 * HRK Admin JavaScript | AnomFIN / Jugi@AnomFIN
 * Hallitaan näkymät, API-kutsut ja lomakkeet.
 */

(function () {
    'use strict';

    const apiUrl = 'api.php';
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    const sections = document.querySelectorAll('.section-view');
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    const alertContainer = document.getElementById('alert-container');

    const productsTableBody = document.querySelector('#products-table tbody');
    const recentProductsContainer = document.getElementById('recent-products');
    const categoriesSelect = document.getElementById('filter-category');
    const searchInput = document.getElementById('search-products');
    const filterStock = document.getElementById('filter-stock');
    const filterPrice = document.getElementById('filter-price');
    const productModalEl = document.getElementById('productModal');
    const productModal = productModalEl ? new bootstrap.Modal(productModalEl) : null;
    const productForm = document.getElementById('product-form');

    const ordersTableBody = document.querySelector('#orders-table tbody');
    const orderStatusFilter = document.getElementById('filter-order-status');

    const homeSectionsContainer = document.getElementById('home-sections');
    const customPagesContainer = document.getElementById('custom-pages');
    const pageModalEl = document.getElementById('pageModal');
    const pageModal = pageModalEl ? new bootstrap.Modal(pageModalEl) : null;
    const pageForm = document.getElementById('page-form');

    const settingsForm = document.getElementById('settings-form');
    const usersTableBody = document.querySelector('#users-table tbody');
    const logsView = document.getElementById('logs-view');

    let productCache = [];
    let categoryCache = [];
    let pageCache = { home_sections: [], custom_pages: [] };
    let ordersCache = [];

    // *** Yleiset utilit ***
    function showAlert(message, type = 'success') {
        if (!alertContainer) {
            return;
        }
        const wrapper = document.createElement('div');
        wrapper.className = `alert alert-${type} shadow-sm`; // Bootstrapin alert-luokka
        wrapper.setAttribute('role', 'alert');
        wrapper.textContent = message;
        alertContainer.appendChild(wrapper);
        setTimeout(() => {
            wrapper.remove();
        }, 5000);
    }

    async function fetchJson(params = {}, options = {}) {
        const config = { ...options };
        config.headers = {
            'Accept': 'application/json',
            'X-CSRF-Token': csrfToken,
            ...(options.headers || {})
        };

        let url = apiUrl;
        if (params && Object.keys(params).length > 0) {
            const usp = new URLSearchParams(params);
            url += `?${usp.toString()}`;
        }

        const response = await fetch(url, config);
        const isJson = response.headers.get('content-type')?.includes('application/json');
        const payload = isJson ? await response.json() : await response.text();

        if (!response.ok) {
            throw new Error(isJson ? (payload.message || 'Tuntematon virhe') : payload);
        }

        return payload;
    }

    function switchSection(section) {
        sections.forEach((sec) => {
            sec.classList.add('d-none');
        });
        navLinks.forEach((link) => link.classList.remove('active'));

        const target = document.getElementById(`section-${section}`);
        if (target) {
            target.classList.remove('d-none');
        }

        navLinks.forEach((link) => {
            if (link.dataset.section === section) {
                link.classList.add('active');
            }
        });

        if (section === 'products' && productCache.length === 0) {
            loadProducts();
        }
        if (section === 'orders' && ordersCache.length === 0) {
            loadOrders();
        }
        if (section === 'settings') {
            loadSettings();
        }
        if (section === 'pages' && pageCache.home_sections.length === 0 && pageCache.custom_pages.length === 0) {
            loadPages();
        }
        if (section === 'users') {
            loadUsers();
        }
        if (section === 'logs') {
            refreshLogs();
        }
    }

    navLinks.forEach((link) => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            const section = link.dataset.section;
            if (section) {
                switchSection(section);
            }
        });
    });

    // *** Tuotetoiminnot ***
    async function loadProducts() {
        try {
            const payload = await fetchJson({ action: 'list_products' });
            const data = payload.data || {};
            productCache = data.products || [];
            categoryCache = data.categories || [];
            renderCategoryFilters();
            renderProducts();
            renderRecentProducts();
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    }

    function renderCategoryFilters() {
        if (!categoriesSelect) return;
        categoriesSelect.innerHTML = '<option value="">Kaikki</option>';
        categoryCache.forEach((category) => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = `${category.name}`;
            categoriesSelect.appendChild(option);
        });
    }

    function getFilteredProducts() {
        const query = searchInput?.value.toLowerCase() || '';
        const category = categoriesSelect?.value || '';
        const stock = filterStock?.value || '';
        const price = filterPrice?.value || '';

        return productCache.filter((product) => {
            let matches = true;
            if (query) {
                const fields = `${product.name} ${product.sku}`.toLowerCase();
                matches = fields.includes(query);
            }
            if (matches && category) {
                matches = (product.categoryids || []).includes(category);
            }
            if (matches && stock) {
                if (stock === 'in_stock') {
                    matches = (product.stock || 0) > 0;
                } else if (stock === 'out_of_stock') {
                    matches = (product.stock || 0) <= 0;
                }
            }
            if (matches && price) {
                const p = Number(product.price || 0);
                if (price === 'lt1000') matches = p < 1000;
                if (price === 'btw1000and3000') matches = p >= 1000 && p <= 3000;
                if (price === 'gt3000') matches = p > 3000;
            }
            return matches;
        });
    }

    function renderProducts() {
        if (!productsTableBody) return;
        const filtered = getFilteredProducts();
        productsTableBody.innerHTML = '';
        filtered.forEach((product) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${escapeHtml(product.name)}</td>
                <td>${escapeHtml(product.sku)}</td>
                <td>€${Number(product.price || 0).toFixed(2)}</td>
                <td>${Number(product.stock || 0)}</td>
                <td>${(product.categoryids || []).map((id) => escapeHtml(resolveCategoryName(id))).join(', ')}</td>
                <td>${escapeHtml(product.updated_at || '')}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary me-2" data-action="edit" data-id="${product.id}">Muokkaa</button>
                    <button class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${product.id}">Poista</button>
                </td>`;
            productsTableBody.appendChild(tr);
        });
    }

    function renderRecentProducts() {
        if (!recentProductsContainer) return;
        const recent = [...productCache]
            .sort((a, b) => new Date(b.updated_at || b.created_at || 0) - new Date(a.updated_at || a.created_at || 0))
            .slice(0, 5);
        recentProductsContainer.innerHTML = '';
        if (recent.length === 0) {
            recentProductsContainer.innerHTML = '<p class="text-muted mb-0">Lisää ensimmäinen tuote aloittaaksesi.</p>';
            return;
        }
        recent.forEach((product) => {
            const div = document.createElement('div');
            div.className = 'border-bottom py-2';
            div.innerHTML = `<strong>${escapeHtml(product.name)}</strong><br><span class="text-muted small">SKU: ${escapeHtml(product.sku)} • Päivitetty ${escapeHtml(product.updated_at || '')}</span>`;
            recentProductsContainer.appendChild(div);
        });
    }

    function resolveCategoryName(id) {
        const category = categoryCache.find((cat) => cat.id === id);
        return category ? category.name : id;
    }

    function escapeHtml(str) {
        return (str || '').toString().replace(/[&<>"]+/g, (s) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[s] || s));
    }

    if (searchInput) searchInput.addEventListener('input', renderProducts);
    if (categoriesSelect) categoriesSelect.addEventListener('change', renderProducts);
    if (filterStock) filterStock.addEventListener('change', renderProducts);
    if (filterPrice) filterPrice.addEventListener('change', renderProducts);

    productsTableBody?.addEventListener('click', (event) => {
        const target = event.target.closest('button[data-action]');
        if (!target) return;
        const id = target.dataset.id;
        if (target.dataset.action === 'edit') {
            openProductModal(id);
        } else if (target.dataset.action === 'delete') {
            deleteProduct(id);
        }
    });

    document.getElementById('btn-add-product')?.addEventListener('click', () => openProductModal());
    document.getElementById('btn-open-product-modal')?.addEventListener('click', () => openProductModal());

    function openProductModal(id) {
        if (!productForm || !productModal) return;
        productForm.reset();
        productForm.querySelector('#product-id').value = id || '';
        if (id) {
            const product = productCache.find((item) => item.id === id);
            if (product) {
                productForm.querySelector('#product-name').value = product.name || '';
                productForm.querySelector('#product-sku').value = product.sku || '';
                productForm.querySelector('#product-price').value = product.price || '';
                productForm.querySelector('#product-compare').value = product.compare_at_price || '';
                productForm.querySelector('#product-stock').value = product.stock || '';
                productForm.querySelector('#product-weight').value = product.weightkg || '';
                productForm.querySelector('#product-battery').value = product.batterywh || '';
                productForm.querySelector('#product-range').value = product.rangekmestimate || '';
                productForm.querySelector('#product-short').value = product.shortdescription || '';
                productForm.querySelector('#product-description').value = product.description || '';
                productForm.querySelector('#product-categories').value = (product.categoryids || []).join(', ');
                productForm.querySelector('#product-images').value = (product.images || []).join(', ');
                productForm.querySelector('#product-meta-title').value = product.meta?.title || '';
                productForm.querySelector('#product-meta-desc').value = product.meta?.description || '';
            }
            document.getElementById('productModalLabel').textContent = 'Muokkaa tuotetta';
        } else {
            document.getElementById('productModalLabel').textContent = 'Lisää uusi tuote';
        }
        productModal.show();
    }

    productForm?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(productForm);
        const payload = Object.fromEntries(formData.entries());

        const product = {
            id: payload.id || null,
            name: payload.name?.trim() || '',
            sku: payload.sku?.trim() || '',
            price: Number(payload.price || 0),
            compare_at_price: payload.compare_at_price ? Number(payload.compare_at_price) : null,
            stock: payload.stock ? Number(payload.stock) : 0,
            weightkg: payload.weightkg ? Number(payload.weightkg) : null,
            batterywh: payload.batterywh ? Number(payload.batterywh) : null,
            rangekmestimate: payload.rangekmestimate ? Number(payload.rangekmestimate) : null,
            shortdescription: payload.shortdescription?.trim() || '',
            description: payload.description?.trim() || '',
            categoryids: payload.categoryids ? payload.categoryids.split(',').map((item) => item.trim()).filter(Boolean) : [],
            images: payload.images ? payload.images.split(',').map((item) => item.trim()).filter(Boolean) : [],
            meta_title: payload.meta_title?.trim() || '',
            meta_description: payload.meta_description?.trim() || '',
            csrf_token: csrfToken,
        };

        try {
            const response = await fetchJson({ action: 'save_product' }, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(product)
            });
            showAlert(response.message || 'Tuote tallennettu');
            productModal?.hide();
            await loadProducts();
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    });

    async function deleteProduct(id) {
        if (!id) return;
        if (!confirm('Haluatko varmasti poistaa tuotteen?')) return;
        try {
            const response = await fetchJson({ action: 'delete_product' }, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, csrf_token: csrfToken })
            });
            showAlert(response.message || 'Tuote poistettu');
            await loadProducts();
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    }

    document.getElementById('btn-export-products')?.addEventListener('click', async () => {
        try {
            const response = await fetch(`${apiUrl}?action=export_products`, {
                headers: { 'X-CSRF-Token': csrfToken }
            });
            if (!response.ok) {
                throw new Error('CSV-vienti epäonnistui');
            }
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `hrk-tuotteet-${new Date().toISOString().slice(0, 10)}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    });

    // *** Tilaukset ***
    async function loadOrders() {
        try {
            const payload = await fetchJson({ action: 'list_orders' });
            const data = payload.data || {};
            ordersCache = data.orders || [];
            renderOrders();
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    }

    function renderOrders() {
        if (!ordersTableBody) return;
        const statusFilter = orderStatusFilter?.value || '';
        ordersTableBody.innerHTML = '';
        ordersCache
            .filter((order) => (statusFilter ? order.status === statusFilter : true))
            .forEach((order) => {
                const tr = document.createElement('tr');
                const customer = order.customer || {};
                tr.innerHTML = `
                    <td>${escapeHtml(order.id)}</td>
                    <td>${escapeHtml(`${customer.name || ''} ${customer.email ? '• ' + customer.email : ''}`)}</td>
                    <td>€${Number(order.total || 0).toFixed(2)}</td>
                    <td>
                        <select class="form-select form-select-sm" data-action="status" data-id="${order.id}">
                            ${['pending', 'paid', 'shipped', 'cancelled'].map((status) => `<option value="${status}" ${order.status === status ? 'selected' : ''}>${status}</option>`).join('')}
                        </select>
                    </td>
                    <td>${escapeHtml(order.created_at || '')}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-secondary" data-action="details" data-id="${order.id}">Näytä</button>
                    </td>`;
                ordersTableBody.appendChild(tr);
            });
    }

    ordersTableBody?.addEventListener('change', async (event) => {
        const select = event.target.closest('select[data-action="status"]');
        if (!select) return;
        const id = select.dataset.id;
        const status = select.value;
        try {
            const response = await fetchJson({ action: 'update_order_status' }, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, status, csrf_token: csrfToken })
            });
            showAlert(response.message || 'Tila päivitetty');
            await loadOrders();
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    });

    ordersTableBody?.addEventListener('click', (event) => {
        const button = event.target.closest('button[data-action="details"]');
        if (!button) return;
        const id = button.dataset.id;
        const order = ordersCache.find((item) => item.id === id);
        if (!order) return;
        const items = (order.items || []).map((item) => `${item.quantity} x ${resolveProductName(item.product_id)} @ €${Number(item.unit_price || 0).toFixed(2)}`).join(' | ');
        showAlert(`Tilaus ${order.id}: ${items}`, 'info');
    });

    function resolveProductName(id) {
        const product = productCache.find((item) => item.id === id);
        return product ? product.name : id;
    }

    document.getElementById('btn-refresh-orders')?.addEventListener('click', loadOrders);
    orderStatusFilter?.addEventListener('change', renderOrders);

    // *** Sivut ***
    async function loadPages() {
        try {
            const payload = await fetchJson({ action: 'list_pages' });
            const data = payload.data || {};
            pageCache = {
                home_sections: data.home_sections || [],
                custom_pages: data.custom_pages || []
            };
            renderPages();
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    }

    function renderPages() {
        if (!homeSectionsContainer || !customPagesContainer) return;
        homeSectionsContainer.innerHTML = '';
        if (!pageCache.home_sections || pageCache.home_sections.length === 0) {
            homeSectionsContainer.innerHTML = '<p class="text-muted">Ei osioita.</p>';
        } else {
            pageCache.home_sections
                .sort((a, b) => (a.order || 0) - (b.order || 0))
                .forEach((section) => {
                    const card = document.createElement('div');
                    card.className = 'border rounded p-3 mb-2';
                    card.innerHTML = `<div class="d-flex justify-content-between align-items-start"><div><strong>${escapeHtml(section.type)}</strong><div class="small text-muted">Järjestys ${section.order}</div></div><button class="btn btn-sm btn-outline-secondary" data-action="edit-home" data-type="${escapeHtml(section.type)}">Muokkaa</button></div>`;
                    homeSectionsContainer.appendChild(card);
                });
        }

        customPagesContainer.innerHTML = '';
        if (!pageCache.custom_pages || pageCache.custom_pages.length === 0) {
            customPagesContainer.innerHTML = '<p class="text-muted">Ei mukautettuja sivuja.</p>';
        } else {
            pageCache.custom_pages.forEach((page) => {
                const card = document.createElement('div');
                card.className = 'border rounded p-3 mb-2';
                card.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <strong>${escapeHtml(page.title)}</strong>
                            <div class="small text-muted">/${escapeHtml(page.slug)}</div>
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" data-action="edit-page" data-id="${page.id}">Muokkaa</button>
                            <button class="btn btn-outline-danger" data-action="delete-page" data-id="${page.id}">Poista</button>
                        </div>
                    </div>`;
                customPagesContainer.appendChild(card);
            });
        }
    }

    document.getElementById('btn-add-page')?.addEventListener('click', () => {
        if (!pageForm || !pageModal) return;
        pageForm.reset();
        pageForm.querySelector('#page-id').value = '';
        pageModal.show();
    });

    customPagesContainer?.addEventListener('click', (event) => {
        const button = event.target.closest('button[data-action]');
        if (!button) return;
        const id = button.dataset.id;
        if (button.dataset.action === 'edit-page') {
            openPageModal(id);
        } else if (button.dataset.action === 'delete-page') {
            deletePage(id);
        }
    });

    function openPageModal(id) {
        if (!pageForm || !pageModal) return;
        pageForm.reset();
        pageForm.querySelector('#page-id').value = id || '';
        if (id) {
            const page = pageCache.custom_pages.find((item) => item.id === id);
            if (page) {
                pageForm.querySelector('#page-title').value = page.title || '';
                pageForm.querySelector('#page-slug').value = page.slug || '';
                pageForm.querySelector('#page-content').value = page.content || '';
            }
        }
        pageModal.show();
    }

    pageForm?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(pageForm);
        const payload = Object.fromEntries(formData.entries());
        const data = {
            id: payload.id || null,
            title: payload.title?.trim() || '',
            slug: payload.slug?.trim() || '',
            content: payload.content || '',
            csrf_token: csrfToken,
        };
        try {
            const response = await fetchJson({ action: 'save_page' }, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showAlert(response.message || 'Sivu tallennettu');
            pageModal?.hide();
            await loadPages();
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    });

    async function deletePage(id) {
        if (!id) return;
        if (!confirm('Poistetaanko sivu pysyvästi?')) return;
        try {
            const response = await fetchJson({ action: 'delete_page' }, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, csrf_token: csrfToken })
            });
            showAlert(response.message || 'Sivu poistettu');
            await loadPages();
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    }

    // *** Asetukset ***
    async function loadSettings() {
        if (!settingsForm) return;
        try {
            const payload = await fetchJson({ action: 'get_settings' });
            const settings = payload.data.settings || {};
            settingsForm.querySelector('#settings-site-title').value = settings.site_title || '';
            settingsForm.querySelector('#settings-contact-email').value = settings.contact?.email || '';
            settingsForm.querySelector('#settings-contact-phone').value = settings.contact?.phone || '';
            settingsForm.querySelector('#settings-business-id').value = settings.contact?.business_id || '';
            settingsForm.querySelector('#hero-title').value = settings.hero?.title || '';
            settingsForm.querySelector('#hero-subtitle').value = settings.hero?.subtitle || '';
            settingsForm.querySelector('#hero-image').value = settings.hero?.image || '';
            settingsForm.querySelector('#hero-cta-text').value = settings.hero?.cta_text || '';
            settingsForm.querySelector('#hero-cta-link').value = settings.hero?.cta_link || '';
            settingsForm.querySelector('#payment-methods').value = (settings.payment?.methods || []).join(', ');
            settingsForm.querySelector('#payment-installments').checked = Boolean(settings.payment?.show_installments);
            settingsForm.querySelector('#seo-title').value = settings.seo_defaults?.meta_title || '';
            settingsForm.querySelector('#seo-description').value = settings.seo_defaults?.meta_description || '';
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    }

    document.getElementById('btn-save-settings')?.addEventListener('click', async () => {
        if (!settingsForm) return;
        const formData = new FormData(settingsForm);
        const data = {
            csrf_token: csrfToken,
            site_title: formData.get('site_title'),
            contact: {
                email: formData.get('contact[email]'),
                phone: formData.get('contact[phone]'),
                business_id: formData.get('contact[business_id]'),
            },
            hero: {
                title: formData.get('hero[title]'),
                subtitle: formData.get('hero[subtitle]'),
                image: formData.get('hero[image]'),
                cta_text: formData.get('hero[cta_text]'),
                cta_link: formData.get('hero[cta_link]'),
            },
            payment: {
                methods: (formData.get('payment[methods]') || '').split(',').map((m) => m.trim()).filter(Boolean),
                show_installments: formData.get('payment[show_installments]') === 'on',
            },
            seo_defaults: {
                meta_title: formData.get('seo_defaults[meta_title]'),
                meta_description: formData.get('seo_defaults[meta_description]'),
            }
        };
        try {
            const response = await fetchJson({ action: 'save_settings' }, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showAlert(response.message || 'Asetukset tallennettu');
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    });

    // *** Käyttäjät ***
    async function loadUsers() {
        if (!usersTableBody) return;
        try {
            const payload = await fetchJson({ action: 'list_users' });
            const users = payload.data.users || [];
            usersTableBody.innerHTML = '';
            users.forEach((user) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${escapeHtml(user.username)}</td>
                    <td>${escapeHtml(user.role || 'admin')}</td>
                    <td>${escapeHtml(user.created_at || '')}</td>`;
                usersTableBody.appendChild(tr);
            });
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    }

    // *** Logit ***
    async function refreshLogs() {
        if (!logsView) return;
        try {
            const response = await fetch(`${apiUrl}?action=get_logs`, {
                headers: { 'X-CSRF-Token': csrfToken }
            });
            if (!response.ok) {
                throw new Error('Lokien lataus epäonnistui');
            }
            const text = await response.text();
            logsView.textContent = text;
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    }

    document.getElementById('btn-refresh-logs')?.addEventListener('click', refreshLogs);

    // Käynnistetään oletusnäkymän lataus
    switchSection('dashboard');
    loadProducts();
    loadOrders();
})();
