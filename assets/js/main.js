const nav = document.querySelector('.nav');
const navToggle = document.querySelector('.nav__toggle');
const navLinks = document.querySelector('.nav__links');

const isNavOpen = () => navLinks?.classList.contains('nav__links--open') ?? false;

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

window.addEventListener('scroll', updateNavOnScroll);
updateNavOnScroll();

const yearEl = document.getElementById('year');
if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
}

const trapFocus = (event) => {
    if (!isNavOpen()) {
        return;
    }

    if (!navLinks) {
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
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && isNavOpen()) {
        closeNav();
        navToggle?.focus();
    }
});

setNavState(isNavOpen());

const storeEl = document.querySelector('[data-store]');

const formatCurrency = (value) =>
    new Intl.NumberFormat('fi-FI', { style: 'currency', currency: 'EUR' }).format(value);

if (storeEl) {
    const cartItemsEl = storeEl.querySelector('[data-cart-items]');
    const cartTotalEl = storeEl.querySelector('[data-cart-total]');
    const cartEmptyEl = storeEl.querySelector('[data-cart-empty]');
    const cartCountEls = document.querySelectorAll('[data-cart-count]');
    const addToCartButtons = storeEl.querySelectorAll('[data-add-to-cart]');

    const cart = [];

    const updateCartCount = () => {
        const itemCount = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCountEls.forEach((el) => {
            el.textContent = String(itemCount);
        });
    };

    const updateCart = () => {
        if (!cartItemsEl || !cartTotalEl || !cartEmptyEl) {
            return;
        }

        cartItemsEl.innerHTML = '';

        if (!cart.length) {
            cartEmptyEl.hidden = false;
            cartTotalEl.textContent = formatCurrency(0);
        } else {
            cartEmptyEl.hidden = true;
            const fragment = document.createDocumentFragment();
            cart.forEach((item, index) => {
                const li = document.createElement('li');
                li.className = 'store__cart-item';

                const titleWrapper = document.createElement('div');
                titleWrapper.className = 'store__cart-item-title';

                const nameEl = document.createElement('span');
                nameEl.textContent = item.name;
                const priceEl = document.createElement('span');
                priceEl.textContent = `${item.displayPrice} × ${item.quantity} kpl`;

                titleWrapper.append(nameEl, priceEl);

                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'store__cart-remove';
                removeBtn.setAttribute('data-remove-item', String(index));
                removeBtn.textContent = 'Poista';

                li.append(titleWrapper, removeBtn);
                fragment.append(li);
            });

            cartItemsEl.append(fragment);
            const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
            cartTotalEl.textContent = formatCurrency(total);
        }

        updateCartCount();
    };

    addToCartButtons.forEach((button) => {
        if (!button.dataset.originalLabel) {
            button.dataset.originalLabel = button.textContent?.trim() ?? '';
        }

        button.addEventListener('click', () => {
            const productCard = button.closest('[data-product]');
            if (!productCard) {
                return;
            }

            const name = productCard.dataset.product?.trim();
            const priceValue = Number(productCard.dataset.price);
            const priceDisplay = productCard.querySelector('.store-card__price')?.textContent?.trim();

            if (!name || Number.isNaN(priceValue)) {
                return;
            }

            const existing = cart.find((item) => item.name === name);
            if (existing) {
                existing.quantity += 1;
            } else {
                cart.push({
                    name,
                    price: priceValue,
                    displayPrice: priceDisplay ?? formatCurrency(priceValue),
                    quantity: 1,
                });
            }

            updateCart();

            button.classList.add('is-added');
            button.disabled = true;
            button.textContent = 'Lisätty!';

            window.setTimeout(() => {
                button.classList.remove('is-added');
                button.disabled = false;
                button.textContent = button.dataset.originalLabel ?? 'Lisää koriin';
            }, 900);
        });
    });

    storeEl.addEventListener('click', (event) => {
        const removeBtn = event.target.closest('[data-remove-item]');
        if (!removeBtn) {
            return;
        }

        const index = Number(removeBtn.getAttribute('data-remove-item'));
        if (Number.isNaN(index) || index < 0 || index >= cart.length) {
            return;
        }

        cart.splice(index, 1);
        updateCart();
    });

    updateCart();
}
