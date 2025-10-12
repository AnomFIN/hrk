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

const calculatorForm = document.getElementById('savings-calculator');
const calculatorResult = document.getElementById('savings-result');

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
