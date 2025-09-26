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
