// Less noise. More signal. AnomFIN.
import { describe, expect, it, beforeEach } from 'vitest';
import { createStorefrontViewState } from '../assets/js/storefront-view.js';

describe('createStorefrontViewState', () => {
    let root;
    let tabs;
    let views;

    beforeEach(() => {
        document.body.innerHTML = `
            <main class="storefront storefront--mallisto" data-storefront-root>
                <nav>
                    <a data-storefront-tab="mallisto" class="nav__link nav__link--pill is-active" aria-selected="true"></a>
                    <a data-storefront-tab="checkout" class="nav__link nav__link--pill" aria-selected="false"></a>
                </nav>
                <section id="storefront-mallisto" data-storefront-view="mallisto"></section>
                <section id="storefront-checkout" data-storefront-view="checkout" hidden aria-hidden="true"></section>
            </main>
        `;

        root = document.querySelector('[data-storefront-root]');
        tabs = document.querySelectorAll('[data-storefront-tab]');
        views = document.querySelectorAll('[data-storefront-view]');
    });

    it('initializes with the default view and hides inactive panels', () => {
        const controller = createStorefrontViewState({
            root,
            tabs,
            views,
            defaultView: 'mallisto',
        });

        const initial = controller.init();

        expect(initial).toBe('mallisto');
        expect(root.classList.contains('storefront--mallisto')).toBe(true);
        expect(root.dataset.storefrontActiveView).toBe('mallisto');
        expect(views[0].hidden).toBe(false);
        expect(views[1].hidden).toBe(true);
        expect(tabs[0].classList.contains('is-active')).toBe(true);
        expect(tabs[1].classList.contains('is-active')).toBe(false);
    });

    it('switches to checkout view and updates aria state', () => {
        const controller = createStorefrontViewState({
            root,
            tabs,
            views,
        });

        controller.init();
        controller.setView('checkout');

        expect(controller.getView()).toBe('checkout');
        expect(root.classList.contains('storefront--checkout')).toBe(true);
        expect(root.dataset.storefrontActiveView).toBe('checkout');
        expect(views[0].hidden).toBe(true);
        expect(views[1].hidden).toBe(false);
        expect(tabs[1].classList.contains('is-active')).toBe(true);
        expect(tabs[1].getAttribute('aria-selected')).toBe('true');
        expect(tabs[1].getAttribute('tabindex')).toBe('0');
    });

    it('ignores unknown views and preserves the active view', () => {
        const controller = createStorefrontViewState({ root, tabs, views });

        controller.init();
        const current = controller.getView();

        controller.setView('unknown');

        expect(controller.getView()).toBe(current);
        expect(root.dataset.storefrontActiveView).toBe(current);
        expect(views[0].hidden).toBe(false);
        expect(views[1].hidden).toBe(true);
    });

    it('falls back to the first available view when the default is missing', () => {
        const controller = createStorefrontViewState({
            root,
            tabs,
            views,
            defaultView: 'non-existent',
        });

        const initial = controller.init();

        expect(initial).toBe('mallisto');
        expect(root.dataset.storefrontActiveView).toBe('mallisto');
        expect(views[0].hidden).toBe(false);
        expect(tabs[0].classList.contains('is-active')).toBe(true);
    });
});
