// hrk — Torque meets telemetry.
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
const storeLayer = document.querySelector('[data-storefront-layer]');
const storeSurface = storeLayer?.querySelector('.storefront-layer__surface');
const storeOpeners = document.querySelectorAll('[data-storefront-open]');
const storeClosers = document.querySelectorAll('[data-storefront-close]');
const storeTriggers = document.querySelectorAll('[data-storefront-trigger]');

let restoreFocusElement = null;
let selectStoreProduct = null;

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
    } catch (error) {
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
    } catch (error) {
        // ignore storage errors silently
    }
};

const getCartItemCount = () => cartState.reduce((total, item) => total + item.quantity, 0);

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
            id: 'tenways-cgo-one',
            name: 'Tenways CGO One',
            category: 'urban',
            categoryLabel: 'Urban',
            badge: 'Urban Launch 2024',
            price: 2899,
            lead: 'Kevyt hiilikuiturunko, hihnaveto ja 90 km kantama. Sisältää AnomFIN Launch Care 299 -palvelun.',
            tagline: 'Kevyt hiilikuiturunko • 90 km kantama',
            features: [
                'Gates CDX -hihnaveto ja hiilikuiturunko luottokäyttöön',
                'Mission Control -seuranta ja varashälytin etäkäytöllä',
                'Premium-akku 36 V / 252 Wh – vaihto 24 h palvelulupauksella',
            ],
            packages: [
                'Launch Care 10 pyörälle • 790 € / kuukausi',
                'Telematiikka & kuljettajaraportointi • 39 € / ajoneuvo',
                'Winter Ready -varustepaketti • 420 €',
            ],
            range: 'Kantama 90 km • 35 Nm vääntö',
            availability: 'Saatavuus: Helsinki Fulfillment 6 kpl',
            support: 'Launch Care 299 sisältyy • 24 h käyttöönotto',
            status: 'Urban varasto • 6 pyörää valmiina toimitukseen',
            image: 'https://images.unsplash.com/photo-1529429617124-aee711a0fb7c?auto=format&fit=crop&w=1400&q=80',
            imageAlt: 'Tenways CGO One sähköpyörä showroomissa',
        },
        {
            id: 'specialized-turbo-como',
            name: 'Specialized Turbo Como IGH',
            category: 'comfort',
            categoryLabel: 'Comfort',
            badge: 'Executive Fleet',
            price: 3990,
            lead: 'Älykäs näytöllinen ajotuki, sisäinen johdotus ja integroidut valot. Premium Pro Active 699 -huoltotaso.',
            tagline: 'Auto Shift IGH • Älykäs ajotuki',
            features: [
                'Automatisoitu IGH-vaihteisto ja 90 Nm tukimoottori',
                'Custom-tasapainotetut akkumoduulit 710 Wh kapasiteetilla',
                'Connected Service -portaali yritysflotille',
            ],
            packages: [
                'Executive Comfort -paketti (nahkasatulat & lokasuojat) • 290 €',
                'Premium Pro Active 699 • sis. 36 kk huoltosopimus',
                'Työsuhdepyörä leasing -sopimus alk. 119 € / kk',
            ],
            range: 'Kantama 130 km • 710 Wh akku',
            availability: 'Saatavuus: Euroopan keskusvarasto 12 kpl',
            support: 'Premium Pro Active 699 sisältyy • Concierge-asennus',
            status: 'Comfort toimituslinja • varmistettu 7 pv toimitus',
            image: 'https://images.unsplash.com/photo-1523419409543-0c1df022bdd9?auto=format&fit=crop&w=1400&q=80',
            imageAlt: 'Specialized Turbo Como sähköpyörä urbaanissa miljöössä',
        },
        {
            id: 'tern-gsd-performance',
            name: 'Tern GSD Performance Duo',
            category: 'cargo',
            categoryLabel: 'Cargo',
            badge: 'Logistics Workhorse',
            price: 5490,
            lead: 'Yritystason jakelupyörä kaksoisakkujärjestelmällä ja Bosch Cargo Line -moottorilla.',
            tagline: 'Bosch Cargo Line • Kaksoisakku 1000 Wh',
            features: [
                'Kantavuus 200 kg ja modulaarinen kuormateline',
                'Bosch Cargo Line Gen4 85 Nm moottori',
                'Hydrauliset Magura MT5e -jarrut 4-mäntätekniikalla',
            ],
            packages: [
                'Fleet Signature 1499 • sisältää koulutuksen & telematiikan',
                'Last Mile -lisävarustesetti • 610 €',
                'Huoltosopimus 36 kk • 49 € / kk',
            ],
            range: 'Kantama 160 km • DualBattery 1000 Wh',
            availability: 'Saatavuus: Nordic Logistics Hub 4 kpl',
            support: 'Fleet Signature 1499 sisältyy • 48 h huoltolupaus',
            status: 'Cargo fulfillment • 4 yksikköä tuotantolinjalla',
            image: 'https://images.unsplash.com/photo-1502877338535-766e1452684a?auto=format&fit=crop&w=1400&q=80',
            imageAlt: 'Tern GSD kuljetussähköpyörä ulkona',
        },
        {
            id: 'vanmoof-s5',
            name: 'VanMoof S5',
            category: 'design',
            categoryLabel: 'Design',
            badge: 'Design Icon',
            price: 3690,
            lead: 'Integroitu varashälytin ja automaattinen vaihteisto. Sisältää kahden vuoden AnomFIN-takuun.',
            tagline: 'Stealth-design • Integroitu hälytin',
            features: [
                'Halo LED -valosignatuurit ja automaattinen vaihteisto',
                'Theft Defense -palvelu ja GPS-seuranta',
                'Hydrauliset levyjarrut ja älykkäät turvamoodit',
            ],
            packages: [
                'Design Concierge -personointi • 180 €',
                'Kaupunkihuolto 24 kk • 32 € / kk',
                'Kasko & vastuuvakuutus • 19 € / kk',
            ],
            range: 'Kantama 150 km • 68 Nm automaattinen boost',
            availability: 'Saatavuus: Launch Studio Amsterdam 8 kpl',
            support: 'AnomFIN Design Guarantee 24 kk sisältyy',
            status: 'Design studio • 8 yksikköä varattavissa nyt',
            image: 'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?auto=format&fit=crop&w=1400&q=80',
            imageAlt: 'VanMoof S5 sähköpyörä minimalistisessa studiossa',
        },
        {
            id: 'riese-muller-load-75',
            name: 'Riese & Müller Load 75 Touring',
            category: 'cargo',
            categoryLabel: 'Cargo',
            badge: 'Utility Elite',
            price: 7290,
            lead: 'Saksalainen premium-lastauspyörä rohkeaan kunnalliskäyttöön. Fox Float -jousitus ja ABS-jarrut.',
            tagline: 'ABS-jarrut • Fox Float -jousitus',
            features: [
                'ABS-levyjarrut ja korkeasäiliöinen kuormatila',
                'Bosch Cargo Line Speed 85 Nm moottori',
                'High-Sided Walls -paketti ja säänkestävä kate',
            ],
            packages: [
                'Kunnalliskäyttö -konversio • 980 €',
                'Fleet Control -telemetria • 69 € / kk',
                'Huoltotakuu 48 kk • 79 € / kk',
            ],
            range: 'Kantama 120 km • DualBattery 1125 Wh',
            availability: 'Saatavuus: Saksa tehdaslinja 5 kpl',
            support: 'Concierge Logistics -paketti sisältyy',
            status: 'Tehdaslinja • 5 yksikköä varattavissa tuotannosta',
            image: 'https://images.unsplash.com/photo-1616530940355-351fabd9524b?auto=format&fit=crop&w=1400&q=80',
            imageAlt: 'Riese & Müller Load 75 Touring sähkörahtipyörä',
        },
        {
            id: 'gazelle-ultimate-c380',
            name: 'Gazelle Ultimate C380 HMB',
            category: 'comfort',
            categoryLabel: 'Comfort',
            badge: 'Commuter Premium',
            price: 3490,
            lead: 'Enviolo-vaihteisto ja hihnaveto tekevät työmatkoista saumattomia. Sisältää yritysleasing-konfiguraation.',
            tagline: 'Enviolo Trekking • Gates-hihnaveto',
            features: [
                'Enviolo-vaihteisto portaattomalla säädöllä',
                'Bosch Performance Line 75 Nm',
                'Integroitu 625 Wh akku ja Supernova-valot',
            ],
            packages: [
                'Commuter Care 24 kk • 28 € / kk',
                'Showroom-sovitus ja ajoergonomian kartoitus • sisältyy',
                'Lisäakku 500 Wh • 520 €',
            ],
            range: 'Kantama 110 km • 625 Wh akku',
            availability: 'Saatavuus: Benelux varasto 9 kpl',
            support: 'Commuter Care sisältyy • 36 h varastovaraus',
            status: 'Comfort tuotanto • 9 yksikköä heti toimitukseen',
            image: 'https://images.unsplash.com/photo-1604147495798-57beb5d6af73?auto=format&fit=crop&w=1400&q=80',
            imageAlt: 'Gazelle Ultimate C380 sähköpyörä kaupunkimaisemassa',
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

    selectStoreProduct = selectProduct;

    updateCategorySelection();
    refreshProductList();
}

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
