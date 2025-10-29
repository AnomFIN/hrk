// hrk — From dirt to data dashboard.
const DEFAULT_VIEW = 'mallisto';

const toElementArray = (collection) =>
    Array.from(collection ?? []).filter((item) => item instanceof HTMLElement);

const applyHiddenState = (element, isHidden) => {
    element.hidden = isHidden;
    element.setAttribute('aria-hidden', String(isHidden));
};

export const createStorefrontViewState = ({
    root,
    tabs = [],
    views = [],
    defaultView = DEFAULT_VIEW,
    onViewChange,
} = {}) => {
    if (!(root instanceof HTMLElement)) {
        throw new Error('createStorefrontViewState requires a root HTMLElement');
    }

    const tabElements = toElementArray(tabs).filter((tab) => tab.dataset.storefrontTab);
    const viewElements = toElementArray(views).filter((view) => view.dataset.storefrontView);

    const tabMap = new Map();
    tabElements.forEach((tab) => {
        tabMap.set(tab.dataset.storefrontTab, tab);
    });

    const viewMap = new Map();
    viewElements.forEach((view) => {
        viewMap.set(view.dataset.storefrontView, view);
    });

    let currentView = null;

    const availableViews = Array.from(viewMap.keys());
    const fallbackView = availableViews.includes(defaultView) ? defaultView : availableViews[0] ?? null;

    const emitChange = (view) => {
        if (typeof onViewChange === 'function') {
            onViewChange(view);
        }
    };

    const updateRootAttributes = (view) => {
        root.dataset.storefrontActiveView = view ?? '';
        root.classList.toggle('storefront--mallisto', view === 'mallisto');
        root.classList.toggle('storefront--checkout', view === 'checkout');
    };

    const updateTabs = (view) => {
        tabMap.forEach((tab, viewName) => {
            const isActive = viewName === view;
            tab.classList.toggle('is-active', isActive);
            tab.setAttribute('aria-selected', String(isActive));
            tab.setAttribute('tabindex', isActive ? '0' : '-1');
        });
    };

    const updateViews = (view) => {
        viewMap.forEach((element, viewName) => {
            const isActive = viewName === view;
            applyHiddenState(element, !isActive);
            element.classList.toggle('is-active-view', isActive);
        });
    };

    const setView = (nextView) => {
        if (!viewMap.has(nextView)) {
            return currentView;
        }

        if (currentView === nextView) {
            return currentView;
        }

        currentView = nextView;
        updateViews(currentView);
        updateTabs(currentView);
        updateRootAttributes(currentView);
        emitChange(currentView);

        return currentView;
    };

    const getView = () => currentView;

    const init = () => {
        if (!fallbackView) {
            return null;
        }

        updateViews(fallbackView);
        updateTabs(fallbackView);
        updateRootAttributes(fallbackView);
        currentView = fallbackView;
        emitChange(currentView);

        return currentView;
    };

    return {
        init,
        setView,
        getView,
        views: () => new Set(viewMap.keys()),
    };
};

export default createStorefrontViewState;
