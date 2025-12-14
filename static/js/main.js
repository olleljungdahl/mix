console.log('Detta är gjort med static/js/main.js');

document.addEventListener('DOMContentLoaded', () => {
    const dashboard = document.querySelector('.robot-dashboard');
    if (!dashboard) {
        return;
    }

    const viewButtons = dashboard.querySelectorAll('.switcher-btn');
    const views = dashboard.querySelectorAll('.dashboard-view');
    const activeViewLabel = dashboard.querySelector('.active-view-label');
    const settingsPanel = dashboard.querySelector('#dashboard-settings');
    const settingsToggle = dashboard.querySelector('.settings-toggle');
    const themeRadios = dashboard.querySelectorAll('input[name="theme-mode"]');
    const speedValue = dashboard.querySelector('.speed-value');
    const gaugeNeedle = dashboard.querySelector('.gauge-needle');

    const viewNames = {
        telemetry: 'Telemetri',
        map: 'Karta',
        controls: 'Kontroller'
    };

    const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

    const mapSpeedToRotation = (value) => {
        const normalized = clamp(value, 0, 120);
        return -110 + (normalized / 120) * 220;
    };

    const setSpeed = (value) => {
        const numeric = Number.parseFloat(value);
        if (Number.isNaN(numeric)) return;
        speedValue.textContent = numeric.toFixed(0);
        const rotation = mapSpeedToRotation(numeric);
        gaugeNeedle.style.setProperty('--needle-rotation', `${rotation}deg`);
    };

    const activateView = (target) => {
        views.forEach((view) => {
            const isActive = view.dataset.view === target;
            view.hidden = !isActive;
        });

        viewButtons.forEach((btn) => {
            const isActive = btn.dataset.target === target;
            btn.classList.toggle('is-active', isActive);
            btn.setAttribute('aria-selected', String(isActive));
        });

        if (activeViewLabel && viewNames[target]) {
            activeViewLabel.textContent = viewNames[target];
        }
    };

    const resolveSystemTheme = () => (
        window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    );

    const applyTheme = (mode) => {
        const storedMode = mode === 'system' ? resolveSystemTheme() : mode;
        document.body.dataset.theme = storedMode;
        localStorage.setItem('dashboard-theme', mode);

        themeRadios.forEach((radio) => {
            radio.checked = radio.value === mode;
        });
    };

    const savedTheme = localStorage.getItem('dashboard-theme') || 'system';
    applyTheme(savedTheme);

    viewButtons.forEach((button) => {
        button.addEventListener('click', () => activateView(button.dataset.target));
    });

    themeRadios.forEach((radio) => {
        radio.addEventListener('change', (event) => {
            applyTheme(event.target.value);
        });
    });

    settingsToggle?.addEventListener('click', () => {
        const isHidden = settingsPanel.hasAttribute('hidden');
        settingsPanel.toggleAttribute('hidden', !isHidden);
        settingsToggle.setAttribute('aria-expanded', String(isHidden));
    });

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        const stored = localStorage.getItem('dashboard-theme') || 'system';
        if (stored === 'system') {
            applyTheme('system');
        }
    });

    const defaultSpeed = Number.parseFloat(dashboard.dataset.defaultSpeed || '48');
    setSpeed(defaultSpeed);
});
