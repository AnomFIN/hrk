// hrk — Torque meets telemetry.
import { createStorefrontViewState } from './storefront-view.js';
const siteShell = document.querySelector('[data-site-shell]');
const navElements = Array.from(document.querySelectorAll('.nav'));
const navControllers = navElements
    .map((navElement) => {
        const toggle = navElement.querySelector('.nav__toggle');
        const links = navElement.querySelector('.nav__links');

        if (!toggle || !links) {
            return null;
        }

        const setState = (isOpen) => {
            links.classList.toggle('nav__links--open', isOpen);
            toggle.classList.toggle('nav__toggle--active', isOpen);
            toggle.setAttribute('aria-expanded', String(isOpen));
        };

        setState(false);

        toggle.addEventListener('click', () => {
            setState(!links.classList.contains('nav__links--open'));
        });

        links.addEventListener('click', (event) => {
            if (!event.target.matches('a, button')) {
                return;
            }

            setState(false);

            if (!navElement.closest('[data-storefront-layer]')) {
                toggle.focus();
            }
        });

        return {
            element: navElement,
            toggle,
            links,
            setState,
            isOpen: () => links.classList.contains('nav__links--open'),
        };
    })
    .filter(Boolean);

const primaryNavController =
    navControllers.find(({ element }) => element.closest('[data-site-shell]')) ?? navControllers[0] ?? null;

const nav = primaryNavController?.element ?? null;
const navToggle = primaryNavController?.toggle ?? null;
const navLinks = primaryNavController?.links ?? null;
const navAnchorLinks = nav ? nav.querySelectorAll('.nav__link[data-scroll]') : [];
const revealElements = document.querySelectorAll('[data-reveal]');
const floatingCta = document.querySelector('[data-floating-cta]');
const floatingOrigin = document.querySelector('[data-floating-origin]');
const navCartCounters = document.querySelectorAll('[data-cart-count]');
const storeElements = document.querySelectorAll('[data-store]');
const addToCartButtons = document.querySelectorAll('[data-add-to-cart]');
const counterElements = document.querySelectorAll('[data-counter]');
const calculatorForm = document.querySelector('[data-calculator]');
const calculatorResult = document.querySelector('[data-calculator-result]');
const yearEl = document.getElementById('year');

const CART_STORAGE_KEY = 'helsinki-ebike-cart';

const prefersReducedMotion = window.matchMedia
    ? window.matchMedia('(prefers-reduced-motion: reduce)')
    : { matches: false };

const isNavOpen = () => primaryNavController?.isOpen() ?? false;

const setNavState = (isOpen) => {
    primaryNavController?.setState(isOpen);
};

const closeNav = () => setNavState(false);

const $ = window.jQuery ?? null;
const storeRoot = document.querySelector('[data-storefront-root]');
const storeTabs = document.querySelectorAll('[data-storefront-tab]');
const storeViewElements = document.querySelectorAll('[data-storefront-view]');
const storeSteps = document.querySelectorAll('.storefront__step');
const storeBackButtons = document.querySelectorAll('[data-storefront-back]');
const storeLayer = document.querySelector('[data-storefront-layer]');
const storeSurface = storeLayer?.querySelector('.storefront-layer__surface');
const storeOpeners = document.querySelectorAll('[data-storefront-open]');
const storeClosers = document.querySelectorAll('[data-storefront-close]');
const storeTriggers = document.querySelectorAll('[data-storefront-trigger]');
const storeCheckoutForm = document.querySelector('[data-checkout-form]');
const checkoutErrorBox = storeCheckoutForm?.querySelector('[data-form-errors]') ?? null;
const checkoutConfirmation = document.querySelector('[data-checkout-confirmation]');
const checkoutSummary = document.querySelector('[data-checkout-summary]');
const checkoutAutoFocusField = storeCheckoutForm?.querySelector('[data-auto-focus]') ?? null;

let restoreFocusElement = null;
let selectStoreProduct = null;
let storefrontViewController = null;

const viewTargets = {
    mallisto: 'storefront-mallisto',
    checkout: 'storefront-checkout',
};

const viewNameOrder = Object.keys(viewTargets);

const updateStorefrontSteps = (activeView) => {
    viewNameOrder.forEach((viewName, index) => {
        const stepElement = storeSteps[index];
        if (stepElement) {
            stepElement.classList.toggle('storefront__step--active', viewName === activeView);
        }
    });
};

const renderCheckoutErrors = (messages) => {
    if (!checkoutErrorBox) {
        return;
    }

    checkoutErrorBox.classList.toggle('is-visible', Boolean(messages.length));

    if (!messages.length) {
        checkoutErrorBox.innerHTML = '';
        return;
    }

    const title = document.createElement('strong');
    title.textContent = 'Korjaa seuraavat tiedot:';

    const list = document.createElement('ul');
    messages.forEach((message) => {
        const item = document.createElement('li');
        item.textContent = message;
        list.appendChild(item);
    });

    checkoutErrorBox.innerHTML = '';
    checkoutErrorBox.append(title, list);
};

const handleStorefrontViewChange = (view) => {
    updateStorefrontSteps(view);

    if (view === 'checkout') {
        window.requestAnimationFrame(() => {
            checkoutAutoFocusField?.focus({ preventScroll: true });
        });
    } else {
        renderCheckoutErrors([]);
    }
};

if (storeRoot) {
    storefrontViewController = createStorefrontViewState({
        root: storeRoot,
        tabs: storeTabs,
        views: storeViewElements,
        defaultView: 'mallisto',
        onViewChange: handleStorefrontViewChange,
    });

    storefrontViewController?.init();
} else {
    handleStorefrontViewChange('mallisto');
}

const syncStorefrontViewForTarget = (targetId) => {
    if (!targetId) {
        return;
    }

    if (targetId === viewTargets.checkout) {
        storefrontViewController?.setView('checkout');
    } else if (targetId === viewTargets.mallisto) {
        storefrontViewController?.setView('mallisto');
    }
};

const isStoreOpen = () => document.body.classList.contains('store-mode');

const dimSiteShell = () => {
    if (!siteShell) {
        return;
    }

    siteShell.classList.add('is-muted');

    if ($) {
        $(siteShell).stop(true, true).animate({ opacity: 0.12 }, 260, 'swing');
    } else {
        siteShell.style.opacity = '0.12';
    }
};

const undimSiteShell = () => {
    if (!siteShell) {
        return;
    }

    const restoreOpacity = () => {
        siteShell.classList.remove('is-muted');
        siteShell.style.opacity = '';
    };

    if ($) {
        $(siteShell).stop(true, true).animate({ opacity: 1 }, 240, 'swing', restoreOpacity);
    } else {
        restoreOpacity();
    }
};

const scrollStorefrontTo = (targetId) => {
    if (!storeSurface || !targetId) {
        return;
    }

    const targetElement = document.getElementById(targetId);
    if (!targetElement) {
        return;
    }

    const offset = Math.max(targetElement.offsetTop - 24, 0);

    if ($) {
        $(storeSurface).stop(true, true).animate({ scrollTop: offset }, 360, 'swing');
    } else {
        storeSurface.scrollTo({ top: offset, behavior: 'smooth' });
    }
};

const openStorefront = ({ targetId, productId } = {}) => {
    if (!storeLayer) {
        return;
    }

    const resolvedTarget = targetId || 'storefront-mallisto';

    syncStorefrontViewForTarget(resolvedTarget);

    if (isStoreOpen()) {
        if (productId && typeof selectStoreProduct === 'function') {
            selectStoreProduct(productId);
        }
        scrollStorefrontTo(resolvedTarget);
        return;
    }

    restoreFocusElement = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    document.body.classList.add('store-mode');
    storeLayer.setAttribute('aria-hidden', 'false');
    dimSiteShell();

    const finalize = () => {
        storeSurface?.focus({ preventScroll: true });
        scrollStorefrontTo(resolvedTarget);
        if (productId && typeof selectStoreProduct === 'function') {
            selectStoreProduct(productId);
        }
    };

    if ($) {
        $(storeLayer)
            .stop(true, true)
            .css('display', 'flex')
            .hide()
            .fadeIn(320, 'swing', finalize);
    } else {
        storeLayer.style.display = 'flex';
        finalize();
    }
};

const closeStorefront = () => {
    if (!storeLayer || !isStoreOpen()) {
        return;
    }

    document.body.classList.remove('store-mode');

    const finalize = () => {
        storeLayer.setAttribute('aria-hidden', 'true');
        if (restoreFocusElement) {
            restoreFocusElement.focus({ preventScroll: true });
        }
        restoreFocusElement = null;
    };

    if ($) {
        $(storeLayer)
            .stop(true, true)
            .fadeOut(240, 'swing', () => {
                $(storeLayer).css('display', 'none');
                finalize();
            });
    } else {
        storeLayer.style.display = 'none';
        finalize();
    }

    undimSiteShell();
};

storeOpeners.forEach((opener) => {
    opener.addEventListener('click', (event) => {
        const rawTarget = opener.getAttribute('data-scroll') ?? opener.getAttribute('href');
        const productId = opener.getAttribute('data-storefront-product') ?? undefined;
        const targetId = rawTarget && rawTarget.startsWith('#') ? rawTarget.slice(1) : rawTarget;

        event.preventDefault();
        openStorefront({ targetId, productId });
    });
});

storeClosers.forEach((closer) => {
    closer.addEventListener('click', (event) => {
        event.preventDefault();
        closeStorefront();
    });
});

const updateNavOnScroll = () => {
    if (window.scrollY > 40) {
        nav?.classList.add('nav--scrolled');
    } else {
        nav?.classList.remove('nav--scrolled');
    }
};

const trackedSections = Array.from(navAnchorLinks)
    .map((link) => {
        const id = link.getAttribute('data-scroll');
        const section = id ? document.getElementById(id) : null;
        return section ? { link, section } : null;
    })
    .filter(Boolean);

const updateActiveNavLink = () => {
    if (!trackedSections.length) {
        return;
    }

    const scrollPos = window.scrollY + 160;
    let activeId = null;

    for (const { section } of trackedSections) {
        if (section.offsetTop <= scrollPos && section.offsetTop + section.offsetHeight > scrollPos) {
            activeId = section.id;
            break;
        }
    }

    trackedSections.forEach(({ link, section }) => {
        link.classList.toggle('nav__link--active', section.id === activeId);
    });
};

const updateFloatingDynamics = () => {
    const scrollY = window.scrollY;
    const ctaOffset = Math.max(-18, -scrollY * 0.08);
    const elevatorOffset = Math.min(scrollY * 0.05, 36);

    floatingCta?.style.setProperty('--cta-scroll-offset', `${ctaOffset}px`);
    floatingOrigin?.style.setProperty('--elevator-scroll-offset', `${elevatorOffset}px`);
};

const handleScroll = () => {
    updateNavOnScroll();
    updateActiveNavLink();
    updateFloatingDynamics();
};

window.addEventListener('scroll', handleScroll);
handleScroll();

if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
}

const trapFocus = (event) => {
    if (!isNavOpen() || !navLinks) {
        return;
    }

    const focusableElements = navLinks.querySelectorAll('a');
    if (!focusableElements.length) {
        return;
    }

    const first = focusableElements[0];
    const last = focusableElements[focusableElements.length - 1];

    if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
    }
};

navLinks?.addEventListener('keydown', trapFocus);

document.addEventListener('click', (event) => {
    if (!isNavOpen() || !navLinks || !navToggle) {
        return;
    }

    if (!navLinks.contains(event.target) && !navToggle.contains(event.target)) {
        closeNav();
    }
});

window.addEventListener('resize', () => {
    if (window.innerWidth > 960) {
        closeNav();
    }
    updateActiveNavLink();
});

document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') {
        return;
    }

    if (isStoreOpen()) {
        event.preventDefault();
        closeStorefront();
        return;
    }

    if (isNavOpen()) {
        event.preventDefault();
        closeNav();
        navToggle?.focus();
    }
});

const formatEuro = (value) =>
    new Intl.NumberFormat('fi-FI', {
        style: 'currency',
        currency: 'EUR',
        maximumFractionDigits: 0,
    }).format(Math.round(value));

const parseCartState = () => {
    if (!('localStorage' in window)) {
        return [];
    }

    try {
        const storedValue = window.localStorage.getItem(CART_STORAGE_KEY);
        if (!storedValue) {
            return [];
        }

        const parsed = JSON.parse(storedValue);
        if (!Array.isArray(parsed)) {
            return [];
        }

        return parsed
            .map((item) => ({
                name: typeof item.name === 'string' ? item.name : '',
                price: Number(item.price),
                quantity: Number(item.quantity ?? 1),
            }))
            .filter(
                (item) =>
                    Boolean(item.name) &&
                    Number.isFinite(item.price) &&
                    item.price >= 0 &&
                    Number.isFinite(item.quantity) &&
                    item.quantity > 0,
            );
    } catch {
        // Intentionally ignore parsing errors and return empty cart on invalid data
        return [];
    }
};

let cartState = parseCartState();

const saveCartState = () => {
    if (!('localStorage' in window)) {
        return;
    }

    try {
        window.localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartState));
    } catch {
        // Intentionally ignore storage errors (e.g., quota exceeded, private mode)
    }
};

const getCartItemCount = () => cartState.reduce((total, item) => total + item.quantity, 0);
const getCartSubtotal = () => cartState.reduce((total, item) => total + item.price * item.quantity, 0);

// Note: sanitizeInput only normalizes whitespace and does NOT prevent XSS attacks.
// XSS protection relies on inserting values into the DOM using textContent (not innerHTML).
const sanitizeInput = (value) => String(value ?? '').replace(/\s+/g, ' ').trim();
const normalizeBusinessId = (value) => sanitizeInput(value).replace(/[^0-9-]/g, '');
const normalizePhone = (value) => sanitizeInput(value).replace(/[^0-9+]/g, '');
const MIN_PHONE_DIGITS = 7;

const deliveryWindowLabels = {
    '2-4 weeks': '2–4 viikkoa',
    '4-6 weeks': '4–6 viikkoa',
    custom: 'Sovitaan erikseen',
};

const updateNavCartCounters = () => {
    const count = getCartItemCount();
    navCartCounters.forEach((counter) => {
        counter.textContent = String(count);
    });
};

const removeCartItem = (name) => {
    const index = cartState.findIndex((item) => item.name === name);
    if (index === -1) {
        return;
    }

    const item = cartState[index];
    if (item.quantity > 1) {
        item.quantity -= 1;
    } else {
        cartState.splice(index, 1);
    }

    saveCartState();
    updateCartDisplays();
};

const renderCartItems = (store) => {
    const itemsList = store.querySelector('[data-cart-items]');
    const emptyState = store.querySelector('[data-cart-empty]');
    const totalEl = store.querySelector('[data-cart-total]');

    if (!itemsList || !totalEl) {
        return;
    }

    itemsList.innerHTML = '';

    if (!cartState.length) {
        if (emptyState) {
            emptyState.style.display = '';
        }
        totalEl.textContent = formatEuro(0);
        return;
    }

    if (emptyState) {
        emptyState.style.display = 'none';
    }

    let subtotal = 0;

    cartState.forEach((item) => {
        subtotal += item.price * item.quantity;

        const listItem = document.createElement('li');
        listItem.className = 'store__cart-item';

        const titleWrapper = document.createElement('div');
        titleWrapper.className = 'store__cart-item-title';

        const nameSpan = document.createElement('span');
        nameSpan.textContent = item.name;

        const quantitySpan = document.createElement('span');
        quantitySpan.textContent = `${item.quantity} × ${formatEuro(item.price)}`;

        titleWrapper.append(nameSpan, quantitySpan);

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'store__cart-remove';
        removeButton.textContent = 'Poista';
        removeButton.addEventListener('click', () => removeCartItem(item.name));

        listItem.append(titleWrapper, removeButton);
        itemsList.appendChild(listItem);
    });

    totalEl.textContent = formatEuro(subtotal);
};

const updateCartDisplays = () => {
    storeElements.forEach((store) => {
        renderCartItems(store);
    });

    updateNavCartCounters();
};

const addCartItem = (name, price) => {
    if (!name || Number.isNaN(price)) {
        return;
    }

    const existing = cartState.find((item) => item.name === name);
    if (existing) {
        existing.quantity += 1;
    } else {
        cartState.push({ name, price, quantity: 1 });
    }

    saveCartState();
    updateCartDisplays();
};

const initializeStoreFilters = (store) => {
    const filterButtons = store.querySelectorAll('[data-filter]');
    const productCards = store.querySelectorAll('.store-card');

    if (!filterButtons.length || !productCards.length) {
        return;
    }

    const applyFilter = (filterValue) => {
        productCards.forEach((card) => {
            const categories = (card.dataset.category ?? '')
                .split(',')
                .map((category) => category.trim());
            const matches = filterValue === 'all' || categories.includes(filterValue);
            card.classList.toggle('is-hidden', !matches);
        });
    };

    filterButtons.forEach((button) => {
        button.addEventListener('click', () => {
            filterButtons.forEach((btn) => btn.classList.remove('is-active'));
            button.classList.add('is-active');
            applyFilter(button.dataset.filter ?? 'all');
        });
    });

    const activeFilter = store.querySelector('.store__filter.is-active');
    applyFilter(activeFilter?.dataset.filter ?? 'all');
};

const markButtonAdded = (button) => {
    const originalLabel = button.dataset.originalLabel ?? button.textContent ?? '';
    if (!button.dataset.originalLabel) {
        button.dataset.originalLabel = originalLabel;
    }

    button.classList.add('is-added');
    button.textContent = 'Lisätty';

    window.setTimeout(() => {
        button.classList.remove('is-added');
        button.textContent = button.dataset.originalLabel ?? originalLabel;
    }, 1800);
};

const handleAddToCartClick = (button) => {
    const productElement = button.closest('[data-product]');
    if (!productElement) {
        return;
    }

    const productName = productElement.dataset.product;
    const price = Number(productElement.dataset.price);

    addCartItem(productName ?? '', price);
    markButtonAdded(button);
};

storeElements.forEach((store) => {
    initializeStoreFilters(store);
});

addToCartButtons.forEach((button) => {
    button.addEventListener('click', () => handleAddToCartClick(button));
});

updateCartDisplays();

const basePageTitle = document.title;
const storefrontElement = document.querySelector('[data-storefront]');
const liveStatusElement = document.querySelector('[data-live-status]');

const updateLiveStatus = (message) => {
    if (!liveStatusElement || !message) {
        return;
    }

    liveStatusElement.textContent = message;
};

if (storefrontElement) {
    const productListElement = storefrontElement.querySelector('[data-product-list]');
    const categoryButtons = storefrontElement.querySelectorAll('[data-category-button]');
    const checkoutPanel = storefrontElement.querySelector('.storefront__panel--summary');
    const checkoutButtons = storefrontElement.querySelectorAll('[data-checkout-button]');
    const detailElements = {
        badge: storefrontElement.querySelector('[data-detail-badge]'),
        image: storefrontElement.querySelector('[data-detail-image]'),
        availability: storefrontElement.querySelector('[data-detail-availability]'),
        range: storefrontElement.querySelector('[data-detail-range]'),
        category: storefrontElement.querySelector('[data-detail-category]'),
        title: storefrontElement.querySelector('[data-detail-title]'),
        lead: storefrontElement.querySelector('[data-detail-lead]'),
        features: storefrontElement.querySelector('[data-detail-features]'),
        packages: storefrontElement.querySelector('[data-detail-packages]'),
        price: storefrontElement.querySelector('[data-detail-price]'),
        support: storefrontElement.querySelector('[data-detail-support]'),
        cta: storefrontElement.querySelector('[data-product-cta]'),
    };

    const storeProducts = [
        {
            id: 'specialized-turbo-vado-igh',
            name: 'Specialized Turbo Vado 5.0 IGH',
            category: 'executive',
            categoryLabel: 'Executive',
            badge: 'Flagship Commuter',
            price: 5890,
            lead: 'Specializedin yritysflotteihin optimoitu Vado IGH. Mission Control -telemetria, automaattinen vaihde ja 710 Wh akku.',
            tagline: 'Mission Control • IGH-vaihteisto',
            features: [
                'Automatisoitu IGH-vaihteisto ja Gates Carbon Drive -hihnaveto',
                'Specialized Mission Control -telemetria ja geofencing',
                '710 Wh akku ja 4A pikalataus • 150 km toimintamatka',
            ],
            packages: [
                'Executive Fit -sovituskäynti • sisältyy',
                'Fleet Care 36 kk • 69 € / kk',
                'DualBattery-integrointi 710 Wh + 710 Wh • 1 190 €',
            ],
            range: 'Kantama 150 km • 710 Wh akku',
            availability: 'Saatavuus: Specialized Europe Hub 12 kpl',
            support: 'Fleet Care 36 kk sisältyy • Concierge käyttöönotto',
            status: 'Executive-linjasto • 12 yksikköä varattavissa',
            image: 'https://images.unsplash.com/photo-1529429617124-aee711a0fb7c?auto=format&fit=crop&w=1400&q=80',
            imageAlt: 'Specialized Turbo Vado sähköpyörä lasiseinäisessä showroomissa',
        },
        {
            id: 'trek-rail-98',
            name: 'Trek Rail 9.8 GX',
            category: 'trail',
            categoryLabel: 'Trail',
            badge: 'Carbon Trail Pro',
            price: 7690,
            lead: 'Trek Rail 9.8 GX tarjoaa hiilikuiturungon, Bosch Smart System -telemetrian ja yritysfloteille varatun toimituskiintiön.',
            tagline: 'OCLV Carbon • Bosch Smart System',
            features: [
                'OCLV Mountain Carbon -runko ja 85 Nm Performance CX -moottori',
                '160/150 mm jousitus ja AirWiz-painevalvonta tekniseen käyttöön',
                'Bosch Smart System + Trek Central -raportointi fleet-valvontaan',
            ],
            packages: [
                'Trail Support 36 kk • 89 € / kk',
                'Teknisen henkilöstön koulutuspaketti • 640 €',
                'Range Extender 750 Wh • 790 €',
            ],
            range: 'Kantama 120 km • 750 Wh akku',
            availability: 'Saatavuus: Trek Euro Distribution 7 kpl',
            support: 'Trail Support 36 kk sisältyy • 72 h varaosalogistiikka',
            status: 'Trail lineup • 7 pyörää vahvistettuna 2024 toimituksiin',
            image: 'https://images.unsplash.com/photo-1509099380898-5c9af0b64081?auto=format&fit=crop&w=1400&q=80',
            imageAlt: 'Trek Rail sähkömaastopyörä vuoristopolulla',
        },
        {
            id: 'riese-muller-load-75',
            name: 'Riese & Müller Load 75 Touring',
            category: 'cargo',
            categoryLabel: 'Cargo',
            badge: 'Utility Elite',
            price: 7890,
            lead: 'Saksalainen cargo-työjuhta kunnalliskäyttöön – ABS-jarrut, Fox Float -jousitus ja DualBattery 1125 Wh.',
            tagline: 'ABS • DualBattery 1125 Wh',
            features: [
                'Bosch Cargo Line Speed 85 Nm + ABS-levyjarrut',
                'High-Sided Walls PRO ja Weather Cover PRO -kuormaratkaisu',
                'FOX Float 34 Performance -etuhaarukka',
            ],
            packages: [
                'Municipal Duty -varustelu • 1 120 €',
                'Fleet Control telemetria • 69 € / kk',
                'Huoltotakuu 48 kk • 79 € / kk',
            ],
            range: 'Kantama 120 km • DualBattery 1125 Wh',
            availability: 'Saatavuus: Riese & Müller Werk 5 kpl',
            support: 'Concierge Logistics sisältyy • 48 h vaste',
            status: 'Tehdaslinja • 5 yksikköä varattavissa tuotannosta',
            image: 'https://images.unsplash.com/photo-1616530940355-351fabd9524b?auto=format&fit=crop&w=1400&q=80',
            imageAlt: 'Riese & Müller Load 75 cargo-sähköpyörä varustettuna',
        },
        {
            id: 'gazelle-ultimate-c380',
            name: 'Gazelle Ultimate C380 HMB',
            category: 'commuter',
            categoryLabel: 'Commuter',
            badge: 'Commuter Premium',
            price: 3490,
            lead: 'Gazellen Enviolo-hihnavetoinen commuter tekee työmatkoista saumattomia ja on valmis leasing-malliin.',
            tagline: 'Enviolo + Gates • 625 Wh',
            features: [
                'Enviolo Trekking -vaihteisto portaattomalla säädöllä',
                'Bosch Performance Line 75 Nm ja 625 Wh PowerTube',
                'Integroitu Supernova-valaistus ja MIK HD -tavarateline',
            ],
            packages: [
                'Commuter Care 24 kk • 28 € / kk',
                'Työmatkaetuprosessi ja käyttöönotto • sisältyy',
                'Lisäakku 500 Wh • 520 €',
            ],
            range: 'Kantama 110 km • 625 Wh akku',
            availability: 'Saatavuus: Gazelle Benelux varasto 9 kpl',
            support: 'Commuter Care sisältyy • 36 h varastovaraus',
            status: 'Commuter tuotanto • 9 yksikköä heti toimitukseen',
            image: 'https://images.unsplash.com/photo-1604147495798-57beb5d6af73?auto=format&fit=crop&w=1400&q=80',
            imageAlt: 'Gazelle Ultimate C380 sähköpyörä kaupunkimaisemassa',
        },
        {
            id: 'giant-stormguard-e-plus',
            name: 'Giant Stormguard E+',
            category: 'utility',
            categoryLabel: 'Utility',
            badge: 'All-Terrain Utility',
            price: 6290,
            lead: 'Giant Stormguard E+ selviytyy Suomen olosuhteista SyncDrive Pro -moottorilla ja Defender-suojauksella.',
            tagline: 'Maastovarmuus • Pro 85 Nm',
            features: [
                'SyncDrive Pro 85 Nm ja automaattinen vaihteistotuki',
                'Defender-vahvistetut lokasuojat ja MIK HD -kantavuus',
                'DualCharge-latausportit ja integroitu valosarja',
            ],
            packages: [
                'Utility Shield -suojauspaketti • 540 €',
                'Telematiikka + turvallisuusseuranta • 49 € / kk',
                'Winter Performance -kitkavarustus • 390 €',
            ],
            range: 'Kantama 140 km • 800 Wh akku',
            availability: 'Saatavuus: Giant Nordic Hub 10 kpl',
            support: 'Utility Shield sisältyy • 72 h huoltovaste',
            status: 'Utility varasto • 10 pyörää vahvistettuna',
            image: 'https://images.unsplash.com/photo-1525104698733-6fe5ce3b7291?auto=format&fit=crop&w=1400&q=80',
            imageAlt: 'Giant Stormguard E+ sähköpyörä sateisella kadulla',
        },
    ];

    let activeCategory = 'all';
    let activeProductId = storeProducts[0]?.id ?? null;
    const productButtons = new Map();

    const renderListItems = (items, element) => {
        if (!element) {
            return;
        }

        element.innerHTML = '';

        items.forEach((item) => {
            const listItem = document.createElement('li');
            listItem.textContent = item;
            element.appendChild(listItem);
        });
    };

    const updateCategorySelection = () => {
        categoryButtons.forEach((button) => {
            const buttonCategory = button.dataset.categoryButton ?? 'all';
            button.classList.toggle('is-active', buttonCategory === activeCategory);
        });
    };

    const updateActiveProductButton = () => {
        productButtons.forEach((button, id) => {
            button.classList.toggle('is-active', id === activeProductId);
        });
    };

    const selectProduct = (productId) => {
        const product = storeProducts.find((item) => item.id === productId);
        if (!product) {
            return;
        }

        activeProductId = product.id;

        if (detailElements.badge) {
            detailElements.badge.textContent = product.badge;
        }

        if (detailElements.image) {
            detailElements.image.src = product.image;
            detailElements.image.alt = product.imageAlt ?? product.name;
        }

        if (detailElements.availability) {
            detailElements.availability.textContent = product.availability;
        }

        if (detailElements.range) {
            detailElements.range.textContent = product.range;
        }

        if (detailElements.category) {
            detailElements.category.textContent = product.categoryLabel;
        }

        if (detailElements.title) {
            detailElements.title.textContent = product.name;
        }

        if (detailElements.lead) {
            detailElements.lead.textContent = product.lead;
        }

        renderListItems(product.features ?? [], detailElements.features);
        renderListItems(product.packages ?? [], detailElements.packages);

        if (detailElements.price) {
            detailElements.price.textContent = formatEuro(product.price);
        }

        if (detailElements.support) {
            detailElements.support.textContent = product.support;
        }

        if (detailElements.cta) {
            detailElements.cta.dataset.product = product.name;
            detailElements.cta.dataset.price = product.price;
        }

        updateActiveProductButton();
        updateLiveStatus(product.status);
        document.title = `${product.name} • ${basePageTitle}`;
    };

    const renderProductList = (productsToRender) => {
        if (!productListElement) {
            return;
        }

        productListElement.innerHTML = '';
        productButtons.clear();

        if (!productsToRender.length) {
            const emptyState = document.createElement('p');
            emptyState.className = 'storefront__empty';
            emptyState.textContent = 'Ei tuotteita valitulla suodatuksella.';
            productListElement.appendChild(emptyState);
            return;
        }

        productsToRender.forEach((product) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'storefront__product';
            button.dataset.productId = product.id;
            button.innerHTML = `
                <span class="storefront__product-title">${product.name}</span>
                <span class="storefront__product-meta">
                    ${formatEuro(product.price)}<br>
                    <small>${product.tagline}</small>
                </span>
            `;

            button.addEventListener('click', () => {
                selectProduct(product.id);
            });

            productListElement.appendChild(button);
            productButtons.set(product.id, button);
        });
    };

    const getProductsByCategory = (category) =>
        category === 'all' ? storeProducts : storeProducts.filter((product) => product.category === category);

    const refreshProductList = () => {
        const filteredProducts = getProductsByCategory(activeCategory);
        renderProductList(filteredProducts);

        const fallbackProduct =
            filteredProducts.find((product) => product.id === activeProductId) ??
            filteredProducts[0] ??
            storeProducts[0];

        if (fallbackProduct) {
            selectProduct(fallbackProduct.id);
        }
    };

    categoryButtons.forEach((button) => {
        button.addEventListener('click', () => {
            activeCategory = button.dataset.categoryButton ?? 'all';
            updateCategorySelection();
            refreshProductList();
        });
    });

    const highlightCheckout = () => {
        if (!checkoutPanel) {
            return;
        }

        checkoutPanel.classList.add('is-highlighted');
        window.setTimeout(() => {
            checkoutPanel.classList.remove('is-highlighted');
        }, 1400);
    };

    checkoutButtons.forEach((button) => {
        button.addEventListener('click', () => {
            highlightCheckout();
        });
    });

    const handleStorefrontTrigger = (trigger, event) => {
        const rawTarget = trigger.getAttribute('data-scroll') ?? trigger.getAttribute('href');
        const targetId = rawTarget && rawTarget.startsWith('#') ? rawTarget.slice(1) : rawTarget;
        const productId = trigger.getAttribute('data-storefront-product') ?? undefined;

        if (!targetId && !productId) {
            return;
        }

        if (!isStoreOpen()) {
            event.preventDefault();
            openStorefront({ targetId, productId });
            return;
        }

    if (productId) {
        selectProduct(productId);
    }

    if (targetId) {
        event.preventDefault();
        syncStorefrontViewForTarget(targetId);
        scrollStorefrontTo(targetId);

        if (targetId === 'storefront-checkout') {
            highlightCheckout();
        }
        }
    };

storeTriggers.forEach((trigger) => {
    trigger.addEventListener('click', (event) => {
        handleStorefrontTrigger(trigger, event);
    });
});

storeBackButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const targetView = button.getAttribute('data-storefront-back') ?? 'mallisto';
        const resolvedTarget = viewTargets[targetView] ?? viewTargets.mallisto;

        storefrontViewController?.setView(targetView);
        scrollStorefrontTo(resolvedTarget);
    });
});

selectStoreProduct = selectProduct;

    updateCategorySelection();
    refreshProductList();
}

const logCheckoutIntent = ({ company, city, deliveryWindow }, subtotal) => {
    try {
        window.console?.info?.('storefront.checkout.intent', {
            company,
            city,
            deliveryWindow,
            subtotal,
            cartSize: cartState.length,
            timestamp: new Date().toISOString(),
        });
    } catch {
        // Intentionally ignore logging failures to prevent disrupting checkout flow
    }
};

storeCheckoutForm?.addEventListener('submit', (event) => {
    event.preventDefault();

    const formData = new FormData(storeCheckoutForm);
    const payload = {
        company: sanitizeInput(formData.get('company')), 
        businessId: normalizeBusinessId(formData.get('businessId')),
        contact: sanitizeInput(formData.get('contact')),
        email: sanitizeInput(formData.get('email')).toLowerCase(),
        phone: normalizePhone(formData.get('phone')),
        city: sanitizeInput(formData.get('city')),
        deliveryWindow: sanitizeInput(formData.get('deliveryWindow')),
        notes: sanitizeInput(formData.get('notes')),
        consent: formData.get('consent') === 'yes',
    };

    const errors = [];
    const businessIdPattern = /^[0-9]{7}-[0-9]$/;

    if (!payload.company) {
        errors.push('Anna yrityksen tai organisaation nimi.');
    }

    if (!businessIdPattern.test(payload.businessId)) {
        errors.push('Syötä Y-tunnus muodossa 1234567-8.');
    }

    if (!payload.contact) {
        errors.push('Lisää yhteyshenkilön nimi.');
    }

    // Email validation is handled by HTML5 input type="email"
    if (!payload.email) {
        errors.push('Syötä validi sähköpostiosoite.');
    }

    if (payload.phone.replace(/[^0-9]/g, '').length < MIN_PHONE_DIGITS) {
        errors.push('Lisää toimiva puhelinnumero kansainvälisessä muodossa.');
    }

    if (!payload.city) {
        errors.push('Lisää toimituskunta.');
    }

    if (!payload.deliveryWindow) {
        errors.push('Valitse toimitusaikatoive.');
    }

    if (!payload.consent) {
        errors.push('Hyväksy tietojen tallennus tilausta varten.');
    }

    if (!cartState.length) {
        errors.push('Lisää vähintään yksi malli ostoskoriin ennen tilauksen lähettämistä.');
    }

    if (errors.length) {
        renderCheckoutErrors(errors);
        if (checkoutConfirmation) {
            checkoutConfirmation.setAttribute('hidden', '');
        }
        if (checkoutSummary) {
            checkoutSummary.innerHTML = '';
        }
        return;
    }

    renderCheckoutErrors([]);

    const subtotal = getCartSubtotal();
    const deliveryLabel = deliveryWindowLabels[payload.deliveryWindow] ?? payload.deliveryWindow;
    const summaryEntries = [
        ['Mallisto', cartState.map((item) => `${item.quantity} × ${item.name}`).join(', ') || 'Ei tuotteita'],
        ['Yritys', payload.company],
        ['Y-tunnus', payload.businessId],
        ['Yhteyshenkilö', payload.contact],
        ['Sähköposti', payload.email],
        ['Puhelin', payload.phone],
        ['Toimituskunta', payload.city],
        ['Toimitusaika', deliveryLabel],
        ['Tilausarvo', formatEuro(subtotal)],
    ];

    if (payload.notes) {
        summaryEntries.push(['Lisätiedot', payload.notes]);
    }

    if (checkoutSummary) {
        checkoutSummary.innerHTML = '';
        summaryEntries.forEach(([label, value]) => {
            const dt = document.createElement('dt');
            dt.textContent = label;
            const dd = document.createElement('dd');
            dd.textContent = value;
            checkoutSummary.append(dt, dd);
        });
    }

    if (checkoutConfirmation) {
        checkoutConfirmation.removeAttribute('hidden');
    }

    logCheckoutIntent({ company: payload.company, city: payload.city, deliveryWindow: deliveryLabel }, subtotal);

    storeCheckoutForm.reset();
    storefrontViewController?.setView('checkout');
    window.requestAnimationFrame(() => {
        checkoutAutoFocusField?.focus({ preventScroll: true });
    });

    scrollStorefrontTo(viewTargets.checkout);
});

const startCounterAnimation = (element) => {
    const target = Number(element.dataset.target ?? element.textContent ?? '0');
    if (!Number.isFinite(target)) {
        element.textContent = `${element.dataset.target ?? element.textContent ?? ''}${element.dataset.suffix ?? ''}`;
        return;
    }

    const suffix = element.dataset.suffix ?? '';
    const duration = Number(element.dataset.duration ?? 1800);
    const startTime = performance.now();

    const step = (currentTime) => {
        const progress = Math.min((currentTime - startTime) / duration, 1);
        const eased = progress ** 0.75;
        const currentValue = Math.round(target * eased);
        element.textContent = `${currentValue}${suffix}`;

        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };

    window.requestAnimationFrame(step);
};

const counterObserver =
    'IntersectionObserver' in window
        ? new IntersectionObserver(
              (entries, observerInstance) => {
                  entries.forEach((entry) => {
                      if (entry.isIntersecting) {
                          startCounterAnimation(entry.target);
                          observerInstance.unobserve(entry.target);
                      }
                  });
              },
              {
                  threshold: 0.4,
              },
          )
        : null;

counterElements.forEach((counter) => {
    if (prefersReducedMotion.matches) {
        counter.textContent = `${counter.dataset.target ?? counter.textContent ?? ''}${counter.dataset.suffix ?? ''}`;
        return;
    }

    if (counterObserver) {
        counterObserver.observe(counter);
    } else {
        startCounterAnimation(counter);
    }
});

const formatCurrency = (value) =>
    new Intl.NumberFormat('fi-FI', {
        style: 'currency',
        currency: 'EUR',
        maximumFractionDigits: 0,
    }).format(Math.round(value));

const formatHours = (value) =>
    new Intl.NumberFormat('fi-FI', {
        maximumFractionDigits: value < 10 ? 1 : 0,
    }).format(value);

calculatorForm?.addEventListener('submit', (event) => {
    event.preventDefault();

    const formData = new FormData(calculatorForm);
    const machines = Number(formData.get('machines'));
    const downtime = Number(formData.get('downtime'));
    const hourlyCost = Number(formData.get('hourlyCost'));
    const prevented = Number(formData.get('prevented'));

    if ([machines, downtime, hourlyCost, prevented].some((value) => Number.isNaN(value) || value < 0)) {
        calculatorResult.innerHTML =
            '<p class="calculator__placeholder">Tarkista syötetyt arvot. Kaikkien lukujen tulee olla positiivisia.</p>';
        return;
    }

    const effectiveness = Math.min(Math.max(prevented, 0), 100) / 100;
    const regainedHours = machines * downtime * effectiveness;
    const monthlySavings = regainedHours * hourlyCost;
    const annualSavings = monthlySavings * 12;

    if (monthlySavings <= 0) {
        calculatorResult.innerHTML =
            '<p class="calculator__placeholder">Lisää ennakoivan kunnossapidon vaikutusta nähdäksesi säästöt. AnomFIN • AnomTools auttaa mitoittamaan tavoitteet.</p>';
        return;
    }

    calculatorResult.innerHTML = `
        <h3>Arvio säästöistä</h3>
        <p>Ennakoiva kunnossapito voi palauttaa <strong>${formatHours(regainedHours)}</strong> tuotantotuntia kuukausittain.</p>
        <ul>
            <li><span>Kuukausittainen hyöty</span><strong>${formatCurrency(monthlySavings)}</strong></li>
            <li><span>Vuosittainen hyöty</span><strong>${formatCurrency(annualSavings)}</strong></li>
        </ul>
        <p class="calculator__hint">Arvio perustuu AnomFIN • AnomTools tilannehuollon datamalliin. Räätälöidyt laskelmat saat kattavan kuntokartoituksen yhteydessä.</p>
    `;
});

const revealObserver =
    'IntersectionObserver' in window
        ? new IntersectionObserver(
              (entries, observerInstance) => {
                  entries.forEach((entry) => {
                      if (entry.isIntersecting) {
                          entry.target.classList.add('is-visible');
                          observerInstance.unobserve(entry.target);
                      }
                  });
              },
              {
                  threshold: 0.22,
                  rootMargin: '0px 0px -120px 0px',
              },
          )
        : null;

const revealImmediately = (element) => {
    element.classList.add('is-visible');
};

document.addEventListener('DOMContentLoaded', () => {
    const { body } = document;
    if (!body) {
        return;
    }

    body.classList.remove('is-preload');

    window.requestAnimationFrame(() => {
        body.classList.add('is-ready');
    });

    revealElements.forEach((element) => {
        if (prefersReducedMotion.matches) {
            revealImmediately(element);
            return;
        }

        const rect = element.getBoundingClientRect();
        if (rect.top <= window.innerHeight * 0.85) {
            revealImmediately(element);
        } else if (revealObserver) {
            revealObserver.observe(element);
        } else {
            revealImmediately(element);
        }
    });

    updateFloatingDynamics();
});

// ========== AWESOME JQUERY FEATURES ==========

if ($) {
    // Feature 1: Enhanced Hover Effects on Cards with jQuery
    $('.store-card, .card, .feature, .alliance-card, .experience-card').each(function() {
        const $card = $(this);
        
        $card.on('mouseenter', function() {
            $(this).stop(true, true).animate({
                'box-shadow': '0 35px 70px rgba(45, 212, 191, 0.25)'
            }, 300, 'swing');
            
            // Add a subtle rotation effect
            $(this).css('transition', 'transform 0.4s ease');
            $(this).css('transform', 'translateY(-8px) rotateX(2deg)');
        });
        
        $card.on('mouseleave', function() {
            $(this).stop(true, true).animate({
                'box-shadow': ''
            }, 300, 'swing');
            
            $(this).css('transform', '');
        });
    });

    // Feature 2: Keystroke Animation for Input Fields
    const addKeystrokeEffect = (inputElement) => {
        const $input = $(inputElement);
        let typingTimer;
        
        $input.on('keydown', function() {
            clearTimeout(typingTimer);
            
            // Add ripple effect on each keystroke
            $(this).addClass('typing-active');
            
            // Animate border color
            $(this).stop(true, true).animate({
                'border-width': '2px'
            }, 100, 'swing', function() {
                $(this).animate({
                    'border-width': '1px'
                }, 100, 'swing');
            });
        });
        
        $input.on('keyup', function() {
            const $this = $(this);
            clearTimeout(typingTimer);
            
            typingTimer = setTimeout(function() {
                $this.removeClass('typing-active');
            }, 500);
            
            // Show character count feedback for longer inputs
            if ($this.val().length > 3) {
                $this.css({
                    'background': 'linear-gradient(135deg, rgba(209, 250, 229, 0.2), rgba(241, 247, 246, 0.65))'
                });
            } else {
                $this.css('background', '');
            }
        });
    };
    
    // Apply keystroke effects to all input fields
    $('input[type="text"], input[type="email"], input[type="tel"], input[type="number"], textarea').each(function() {
        addKeystrokeEffect(this);
    });
    
    // Feature 3: Smooth Onboard Hover Effects with Tooltips
    $('.btn, .nav__link, .store-card__tag').each(function() {
        const $element = $(this);
        const originalText = $element.text();
        
        $element.on('mouseenter', function() {
            // Scale up slightly
            $(this).stop(true, true).animate({
                'padding-left': '+=5px',
                'padding-right': '+=5px'
            }, 200, 'swing');
            
            // Add a subtle glow effect
            $(this).css('position', 'relative');
            $(this).css('z-index', '10');
        });
        
        $element.on('mouseleave', function() {
            $(this).stop(true, true).animate({
                'padding-left': '-=5px',
                'padding-right': '-=5px'
            }, 200, 'swing');
            
            $(this).css('z-index', '');
        });
    });
    
    // Bonus Feature: Smooth Scroll with jQuery
    $('a[data-scroll]').on('click', function(e) {
        const targetId = $(this).attr('data-scroll');
        const $target = $('#' + targetId);
        
        if ($target.length && !isStoreOpen()) {
            e.preventDefault();
            
            $('html, body').stop(true, true).animate({
                scrollTop: $target.offset().top - 100
            }, 800, 'swing', function() {
                // Add a highlight effect when reaching the target
                $target.css('background', 'rgba(45, 212, 191, 0.1)');
                setTimeout(function() {
                    $target.animate({
                        'background': ''
                    }, 1000);
                }, 500);
            });
        }
    });
    
    // Bonus Feature: Interactive Product Cards in Storefront
    $('.storefront__product').on('click', function() {
        $('.storefront__product').removeClass('pulse-highlight');
        $(this).addClass('pulse-highlight');
        
        // Animate the selection
        $(this).stop(true, true)
            .css('transform', 'scale(0.95)')
            .animate({ dummy: 1 }, {
                duration: 100,
                step: function(now) {
                    $(this).css('transform', 'scale(' + (0.95 + (1 - 0.95) * now) + ')');
                },
                complete: function() {
                    $(this).css('transform', 'scale(1.02)');
                    setTimeout(() => {
                        $(this).css('transform', '');
                    }, 200);
                }
            });
    });
    
    // Add CSS for typing effect dynamically
    $('<style>')
        .prop('type', 'text/css')
        .html(`
            .typing-active {
                animation: inputPulse 0.3s ease-in-out !important;
            }
            
            @keyframes inputPulse {
                0%, 100% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.01);
                }
            }
            
            .pulse-highlight {
                position: relative;
            }
            
            .pulse-highlight::after {
                content: '';
                position: absolute;
                inset: -2px;
                border-radius: inherit;
                border: 2px solid rgba(45, 212, 191, 0.6);
                animation: pulseHighlight 1s ease-in-out;
                pointer-events: none;
            }
            
            @keyframes pulseHighlight {
                0% {
                    opacity: 0;
                    transform: scale(0.9);
                }
                50% {
                    opacity: 1;
                    transform: scale(1);
                }
                100% {
                    opacity: 0;
                    transform: scale(1.1);
                }
            }
        `)
        .appendTo('head');
    
    console.log('✨ Awesome jQuery features loaded successfully!');
}
