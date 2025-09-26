const nav = document.querySelector('.nav');
const navToggle = document.querySelector('.nav__toggle');
const navLinks = document.querySelector('.nav__links');

const toggleNav = () => {
    navLinks.classList.toggle('nav__links--open');
    navToggle.classList.toggle('nav__toggle--active');
};

navToggle?.addEventListener('click', toggleNav);

navLinks?.addEventListener('click', (event) => {
    if (event.target.matches('a')) {
        navLinks.classList.remove('nav__links--open');
        navToggle.classList.remove('nav__toggle--active');
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

const storeFilters = document.querySelectorAll('.store__filter');
const storeCards = document.querySelectorAll('.store-card');
const storeSearchInput = document.getElementById('store-search');
const storeCount = document.querySelector('[data-store-count]');

const getActiveFilter = () => {
    return document.querySelector('.store__filter.is-active')?.dataset.filter ?? 'all';
};

const updateStoreVisibility = () => {
    const filter = getActiveFilter();
    const query = storeSearchInput?.value.trim().toLowerCase() ?? '';
    let visibleCount = 0;

    storeCards.forEach((card) => {
        const categories = (card.dataset.categories ?? '').split(/\s+/);
        const matchesFilter = filter === 'all' || categories.includes(filter);
        const textContent = card.textContent.toLowerCase();
        const matchesQuery = !query || textContent.includes(query);
        const isVisible = matchesFilter && matchesQuery;

        card.classList.toggle('is-hidden', !isVisible);
        card.setAttribute('aria-hidden', String(!isVisible));

        if (isVisible) {
            visibleCount += 1;
        }
    });

    if (storeCount) {
        storeCount.textContent = visibleCount;
    }
};

storeFilters.forEach((button) => {
    button.addEventListener('click', () => {
        if (button.classList.contains('is-active')) {
            return;
        }

        storeFilters.forEach((item) => {
            item.classList.remove('is-active');
            item.setAttribute('aria-selected', 'false');
        });

        button.classList.add('is-active');
        button.setAttribute('aria-selected', 'true');
        updateStoreVisibility();
    });
});

storeSearchInput?.addEventListener('input', () => {
    updateStoreVisibility();
});

if (storeCards.length) {
    updateStoreVisibility();
}

const trapFocus = (event) => {
    if (!navLinks?.classList.contains('nav__links--open')) {
        return;
    }

    const focusableElements = navLinks.querySelectorAll('a');
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
    if (!navLinks?.classList.contains('nav__links--open')) {
        return;
    }

    if (!navLinks.contains(event.target) && !navToggle.contains(event.target)) {
        navLinks.classList.remove('nav__links--open');
        navToggle.classList.remove('nav__toggle--active');
    }
});

window.addEventListener('resize', () => {
    if (window.innerWidth > 960) {
        navLinks?.classList.remove('nav__links--open');
        navToggle?.classList.remove('nav__toggle--active');
    }
});

const faqQuestions = document.querySelectorAll('.faq__question');

faqQuestions.forEach((question) => {
    question.addEventListener('click', () => {
        const expanded = question.getAttribute('aria-expanded') === 'true';
        const answer = question.nextElementSibling;

        question.setAttribute('aria-expanded', String(!expanded));

        if (answer instanceof HTMLElement) {
            if (expanded) {
                answer.setAttribute('hidden', '');
            } else {
                answer.removeAttribute('hidden');
            }
        }

        faqQuestions.forEach((other) => {
            if (other === question) {
                return;
            }

            other.setAttribute('aria-expanded', 'false');
            const otherAnswer = other.nextElementSibling;
            if (otherAnswer instanceof HTMLElement) {
                otherAnswer.setAttribute('hidden', '');
            }
        });
    });
});
