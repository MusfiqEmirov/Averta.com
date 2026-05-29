(function () {
    'use strict';

    function initBookingRoot(root) {
        if (!root) return;

        var i18n = {
            package: root.getAttribute('data-i18n-package') || 'Paket',
            service: root.getAttribute('data-i18n-service') || 'Xidmət',
            adults: root.getAttribute('data-i18n-adults') || 'Böyük',
            children: root.getAttribute('data-i18n-children') || 'Uşaq',
        };

        var form = root.querySelector('.hb-form');
        if (!form) return;

        var typeInput = form.querySelector('[name="booking_type"]');
        var tabs = root.querySelectorAll('[data-booking-tab]');
        var panels = root.querySelectorAll('[data-booking-panel]');
        var limits = { adults: { min: 1, max: 100 }, children: { min: 0, max: 100 } };
        var pickers = root.querySelectorAll('[data-hb-picker]');
        var menus = root.querySelectorAll('[data-hb-picker-menu]');

        function closeAllPickers() {
            pickers.forEach(function (btn) {
                btn.setAttribute('aria-expanded', 'false');
            });
            menus.forEach(function (menu) {
                menu.hidden = true;
            });
        }

        function openPicker(kind) {
            closeAllPickers();
            var btn = root.querySelector('[data-hb-picker="' + kind + '"]');
            var menu = root.querySelector('[data-hb-picker-menu="' + kind + '"]');
            if (!btn || !menu) return;
            btn.setAttribute('aria-expanded', 'true');
            menu.hidden = false;
        }

        function togglePicker(kind) {
            var btn = root.querySelector('[data-hb-picker="' + kind + '"]');
            if (!btn) return;
            if (btn.getAttribute('aria-expanded') === 'true') closeAllPickers();
            else openPicker(kind);
        }

        function updatePickerLabel(kind) {
            var valueEl = root.querySelector('[data-hb-picker-value="' + kind + '"]');
            var panel = root.querySelector('[data-booking-panel="' + kind + '"]');
            if (!valueEl || !panel) return;

            var selected = panel.querySelectorAll('input[type="checkbox"]:checked');
            if (!selected.length) {
                valueEl.textContent = kind === 'package' ? i18n.package : i18n.service;
                return;
            }

            var names = [];
            selected.forEach(function (cb) {
                var span = cb.closest('label') && cb.closest('label').querySelector('span');
                var text = span && (span.textContent || '').trim();
                if (text) names.push(text);
            });

            var isMobile = window.matchMedia && window.matchMedia('(max-width: 767.98px)').matches;
            var maxNames = isMobile ? 2 : 5;
            var head = names.slice(0, maxNames).join(', ');
            var rest = names.length - maxNames;
            valueEl.textContent = rest > 0 ? (head + ' +' + rest) : head;
        }

        function setType(type) {
            if (typeInput) typeInput.value = type;

            tabs.forEach(function (tab) {
                var active = tab.getAttribute('data-booking-tab') === type;
                tab.classList.toggle('hb-tab--active', active);
                tab.setAttribute('aria-selected', active ? 'true' : 'false');
            });

            panels.forEach(function (panel) {
                var show = panel.getAttribute('data-booking-panel') === type;
                panel.classList.toggle('d-none', !show);
                panel.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
                    cb.disabled = !show;
                    if (!show) cb.checked = false;
                });
            });

            closeAllPickers();
            updatePickerLabel('package');
            updatePickerLabel('service');
        }

        tabs.forEach(function (tab) {
            tab.addEventListener('click', function () {
                setType(tab.getAttribute('data-booking-tab'));
            });
        });

        setType((typeInput && typeInput.value) || 'package');

        pickers.forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                togglePicker(btn.getAttribute('data-hb-picker'));
            });
        });

        root.querySelectorAll('[data-booking-panel] input[type="checkbox"]').forEach(function (cb) {
            cb.addEventListener('change', function () {
                var panel = cb.closest('[data-booking-panel]');
                if (panel) updatePickerLabel(panel.getAttribute('data-booking-panel'));
            });
        });

        document.addEventListener('click', function (e) {
            if (root.contains(e.target)) {
                if (e.target.closest('[data-hb-picker]') || e.target.closest('[data-hb-picker-menu]')) return;
            }
            closeAllPickers();
        });

        function getHidden(name) {
            return form.querySelector('input[name="' + name + '_count"]');
        }

        function getDisplay(name) {
            return root.querySelector('[data-counter-display="' + name + '"]');
        }

        function setCount(name, value) {
            var cfg = limits[name];
            var next = Math.min(cfg.max, Math.max(cfg.min, value));
            var inp = getHidden(name);
            var disp = getDisplay(name);
            if (inp) inp.value = String(next);
            if (disp) disp.textContent = String(next);
        }

        root.querySelectorAll('[data-counter-action]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var name = btn.getAttribute('data-counter');
                var inp = getHidden(name);
                var current = parseInt(inp && inp.value, 10);
                if (isNaN(current)) current = name === 'adults' ? 1 : 0;
                setCount(name, current + (btn.getAttribute('data-counter-action') === 'plus' ? 1 : -1));
            });
        });

        ['adults', 'children'].forEach(function (name) {
            var inp = getHidden(name);
            var disp = getDisplay(name);
            if (inp && disp) disp.textContent = inp.value || (name === 'adults' ? '1' : '0');
        });

        var guestsModal = root.querySelector('[data-guests-modal]');
        var guestsOpenBtn = root.querySelector('[data-guests-open]');
        var guestsAnimMs = 180;
        var guestsSkipOutsideClose = false;

        function isGuestsOpen() {
            return guestsModal && !guestsModal.hidden && guestsModal.classList.contains('is-open');
        }

        function updateGuestsSummary() {
            var aInp = getHidden('adults');
            var cInp = getHidden('children');
            var a = parseInt(aInp && aInp.value, 10);
            if (isNaN(a)) a = 1;
            var c = parseInt(cInp && cInp.value, 10);
            if (isNaN(c)) c = 0;
            var el = root.querySelector('[data-guests-summary]');
            if (el) el.textContent = i18n.adults + ': ' + a + ' \u2022 ' + i18n.children + ': ' + c;
        }

        function openGuestsModal() {
            if (!guestsModal) return;
            guestsModal.hidden = false;
            guestsModal.removeAttribute('hidden');
            guestsModal.setAttribute('aria-hidden', 'false');
            guestsModal.classList.add('is-open');
            if (guestsOpenBtn) {
                guestsOpenBtn.classList.add('is-open');
                guestsOpenBtn.setAttribute('aria-expanded', 'true');
            }
            updateGuestsSummary();
        }

        function closeGuestsModal() {
            if (!guestsModal) return;
            guestsModal.classList.remove('is-open');
            if (guestsOpenBtn) {
                guestsOpenBtn.classList.remove('is-open');
                guestsOpenBtn.setAttribute('aria-expanded', 'false');
            }
            window.setTimeout(function () {
                if (!guestsModal.classList.contains('is-open')) {
                    guestsModal.hidden = true;
                    guestsModal.setAttribute('aria-hidden', 'true');
                }
            }, guestsAnimMs);
            updateGuestsSummary();
        }

        if (guestsOpenBtn) {
            guestsOpenBtn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                if (isGuestsOpen()) {
                    closeGuestsModal();
                } else {
                    guestsSkipOutsideClose = true;
                    openGuestsModal();
                }
            });
        }

        root.querySelectorAll('[data-guests-close]').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                closeGuestsModal();
            });
        });

        document.addEventListener('click', function (e) {
            if (guestsSkipOutsideClose) {
                guestsSkipOutsideClose = false;
                return;
            }
            if (!isGuestsOpen()) return;
            if (!root.contains(e.target)) {
                closeGuestsModal();
                return;
            }
            if (e.target.closest('[data-guests-open]') || e.target.closest('[data-guests-modal]')) return;
            closeGuestsModal();
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && isGuestsOpen()) closeGuestsModal();
        });

        root.addEventListener('click', function (e) {
            if (e.target && e.target.closest && e.target.closest('[data-counter-action]')) {
                updateGuestsSummary();
            }
        });

        updateGuestsSummary();

        if (root.id === 'contact-booking-form-root') {
            try {
                var sp = new URLSearchParams(window.location.search || '');
                var serviceId = (sp.get('service') || '').trim();
                if (serviceId) {
                    setType('service');
                    var sPanel = root.querySelector('[data-booking-panel="service"]');
                    var cb = sPanel && sPanel.querySelector('input[type="checkbox"][value="' + serviceId + '"]');
                    if (cb) {
                        cb.checked = true;
                        cb.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    openPicker('service');
                }
            } catch (err) {
                /* ignore */
            }
        }
    }

    function boot() {
        initBookingRoot(document.getElementById('hero-booking'));
        initBookingRoot(document.getElementById('contact-booking-form-root'));
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
