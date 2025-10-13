const nav = document.querySelector('.nav');
const navToggle = document.querySelector('.nav__toggle');
const navLinks = document.querySelector('.nav__links');
const navAnchorLinks = document.querySelectorAll('.nav__link[data-scroll]');
const revealElements = document.querySelectorAll('[data-reveal]');
const floatingCta = document.querySelector('[data-floating-cta]');
const floatingOrigin = document.querySelector('[data-floating-origin]');

const prefersReducedMotion = window.matchMedia
    ? window.matchMedia('(prefers-reduced-motion: reduce)')
    : { matches: false };

const isNavOpen = () => navLinks?.classList.contains('nav__links--open') ?? false;

const setNavState = (isOpen) => {
    if (!navLinks || !navToggle) {
        return;
    }

    navLinks.classList.toggle('nav__links--open', isOpen);
    navToggle.classList.toggle('nav__toggle--active', isOpen);
    navToggle.setAttribute('aria-expanded', String(isOpen));
};

const setNavState = (isOpen) => {
    if (!navLinks || !navToggle) {
        return;
    }

    navLinks.classList.toggle('nav__links--open', isOpen);
    navToggle.classList.toggle('nav__toggle--active', isOpen);
    navToggle.setAttribute('aria-expanded', String(isOpen));
};

const toggleNav = () => {
    setNavState(!isNavOpen());
};

const closeNav = () => {
    setNavState(false);
};

const closeNav = () => setNavState(false);

setNavState(false);

navToggle?.addEventListener('click', toggleNav);

navLinks?.addEventListener('click', (event) => {
    if (event.target.matches('a')) {
        closeNav();
        navToggle?.focus();
    }
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
    if (event.key === 'Escape' && isNavOpen()) {
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
