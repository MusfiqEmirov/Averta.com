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

        function initPillClearButtons() {
            var clearLabel = root.getAttribute('data-i18n-clear') || 'Seçimi sil';

            root.querySelectorAll('.hb-pill').forEach(function (pill) {
                if (pill.querySelector('.hb-pill-clear')) return;

                var cb = pill.querySelector('input[type="checkbox"]');
                var span = pill.querySelector('span');
                if (!cb) return;

                var clearBtn = document.createElement('button');
                clearBtn.type = 'button';
                clearBtn.className = 'hb-pill-clear';
                clearBtn.setAttribute('aria-label', clearLabel + (span ? ': ' + span.textContent.trim() : ''));
                clearBtn.innerHTML = '&times;';
                clearBtn.hidden = !cb.checked;
                pill.appendChild(clearBtn);

                clearBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    cb.checked = false;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                });

                cb.addEventListener('change', function () {
                    clearBtn.hidden = !cb.checked;
                });
            });
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

        initPillClearButtons();
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
                var packageId = (sp.get('package') || '').trim();

                if (serviceId) {
                    setType('service');
                    var sPanel = root.querySelector('[data-booking-panel="service"]');
                    var serviceCb = sPanel && sPanel.querySelector('input[type="checkbox"][value="' + serviceId + '"]');
                    if (serviceCb) {
                        serviceCb.checked = true;
                        serviceCb.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    openPicker('service');
                } else if (packageId) {
                    setType('package');
                    var pPanel = root.querySelector('[data-booking-panel="package"]');
                    var packageCb = pPanel && pPanel.querySelector('input[type="checkbox"][value="' + packageId + '"]');
                    if (packageCb) {
                        packageCb.checked = true;
                        packageCb.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    openPicker('package');
                }
            } catch (err) {
                /* ignore */
            }
        }
    }

    /* ════════════════════════════════════
       Air Datepicker integration
       ════════════════════════════════════ */

    var AZ_LOCALE = {
        days: ['Bazar', 'Bazar ertəsi', 'Çərşənbə ax.', 'Çərşənbə', 'Cümə ax.', 'Cümə', 'Şənbə'],
        daysShort: ['Baz', 'B.e', 'Ç.a', 'Çər', 'C.a', 'Cüm', 'Şnb'],
        daysMin: ['B', 'Be', 'Ça', 'Ç', 'Ca', 'C', 'Ş'],
        months: ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'İyun', 'İyul', 'Avqust', 'Sentyabr', 'Oktyabr', 'Noyabr', 'Dekabr'],
        monthsShort: ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'İyn', 'İyl', 'Avq', 'Sen', 'Okt', 'Noy', 'Dek'],
        today: 'Bu gün',
        clear: 'Sil',
        dateFormat: 'dd-MM-yyyy',
        timeFormat: 'HH:mm',
        firstDay: 1,
    };

    var EN_LOCALE = {
        days: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        daysShort: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        daysMin: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
        months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        monthsShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        today: 'Today',
        clear: 'Clear',
        dateFormat: 'dd-MM-yyyy',
        timeFormat: 'HH:mm',
        firstDay: 0,
    };

    var RU_LOCALE = {
        days: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
        daysShort: ['Вос', 'Пон', 'Вто', 'Сре', 'Чет', 'Пят', 'Суб'],
        daysMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
        months: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
        monthsShort: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'],
        today: 'Сегодня',
        clear: 'Очистить',
        dateFormat: 'dd-MM-yyyy',
        timeFormat: 'HH:mm',
        firstDay: 1,
    };

    function getAirLocale(lang) {
        if (lang === 'ru') return RU_LOCALE;
        if (lang === 'en') return EN_LOCALE;
        return AZ_LOCALE;
    }

    function parseLang(root) {
        return (root.getAttribute('data-lang') || document.documentElement.lang || 'az').split('-')[0].toLowerCase();
    }

    function startOfToday() {
        var d = new Date();
        d.setHours(0, 0, 0, 0);
        return d;
    }

    function addDays(date, days) {
        var d = new Date(date.getTime());
        d.setDate(d.getDate() + days);
        return d;
    }

    function initDateFields(root) {
        if (typeof AirDatepicker === 'undefined') return;
        if (!root) return;

        var fromCell = root.querySelector('[data-hb-date-cell]:not([data-hb-date-to])');
        var toCell = root.querySelector('[data-hb-date-cell][data-hb-date-to]');
        if (!fromCell || !toCell) return;

        var fromInput = fromCell.querySelector('.hb-date-text') || fromCell.querySelector('input[name="date_from"]');
        var toInput = toCell.querySelector('.hb-date-text') || toCell.querySelector('input[name="date_to"]');
        if (!fromInput || !toInput) return;

        if (fromInput._airDatepicker) { fromInput._airDatepicker.destroy(); }
        if (toInput._airDatepicker) { toInput._airDatepicker.destroy(); }

        var lang = parseLang(root);
        var locale = getAirLocale(lang);
        var today = startOfToday();
        var useHeroCalendar = root.id === 'hero-booking' || root.id === 'contact-booking-form-root';
        var dpFrom, dpTo;

        function fmtDate(d) {
            if (!d) return '';
            return String(d.getDate()).padStart(2,'0') + '-' +
                   String(d.getMonth()+1).padStart(2,'0') + '-' +
                   d.getFullYear();
        }

        function syncDateFieldState(input, cell) {
            if (!input || !cell) return;
            var filled = !!(input.value || '').trim();
            cell.classList.toggle('has-value', filled);
            input.setAttribute('placeholder', filled ? ' ' : '.....');
        }

        function stripTime(d) {
            return new Date(d.getFullYear(), d.getMonth(), d.getDate());
        }

        function hidePastCells(getMinDate) {
            return function (payload) {
                if (payload.cellType !== 'day') return;
                if (stripTime(payload.date) < stripTime(getMinDate())) {
                    return { disabled: true, classes: 'hb-day-hidden' };
                }
            };
        }

        var baseOpts = {
            locale: locale,
            dateFormat: 'dd-MM-yyyy',
            minDate: today,
            startDate: today,
            autoClose: true,
            navTitles: { days: 'MMMM, yyyy' },
            classes: useHeroCalendar ? 'hb-airdp--hero' : 'hb-airdp--embed',
            position: 'bottom left',
            offset: 4,
            isMobile: false,
            onHide: function(isFinished) { return isFinished; },
            onRenderCell: hidePastCells(function () { return today; }),
        };

        dpFrom = new AirDatepicker(fromInput, Object.assign({}, baseOpts, {
            onSelect: function(opts) {
                if (!opts.date) return;
                fromInput.value = fmtDate(opts.date);
                syncDateFieldState(fromInput, fromCell);
                if (dpTo) {
                    dpTo.update({ minDate: opts.date });
                    if (typeof dpTo.setViewDate === 'function') {
                        dpTo.setViewDate(opts.date);
                    }
                    var toSel = dpTo.selectedDates[0];
                    if (toSel && toSel <= opts.date) {
                        var next = addDays(opts.date, 1);
                        dpTo.selectDate(next, { silent: false });
                        dpTo.setViewDate(next);
                        toInput.value = fmtDate(next);
                        syncDateFieldState(toInput, toCell);
                    }
                }
            },
            onShow: function() { fromCell.classList.add('is-open'); },
            onHide: function() { fromCell.classList.remove('is-open'); },
        }));

        dpTo = new AirDatepicker(toInput, Object.assign({}, baseOpts, {
            minDate: today,
            onRenderCell: hidePastCells(function () {
                return dpTo && dpTo.opts && dpTo.opts.minDate ? dpTo.opts.minDate : today;
            }),
            onSelect: function(opts) {
                if (!opts.date) return;
                toInput.value = fmtDate(opts.date);
                syncDateFieldState(toInput, toCell);
            },
            onShow: function() { toCell.classList.add('is-open'); },
            onHide: function() { toCell.classList.remove('is-open'); },
        }));

        fromInput._airDatepicker = dpFrom;
        toInput._airDatepicker = dpTo;

        function openDp(dp, otherDp) {
            if (otherDp && otherDp.visible) otherDp.hide();
            dp.show();
        }

        function toggleDp(dp, otherDp) {
            if (dp.visible) {
                dp.hide();
            } else {
                openDp(dp, otherDp);
            }
        }

        function bindCell(cell, dp, otherDp) {
            function handleToggle(e) {
                if (e.target.closest('.air-datepicker')) return;
                toggleDp(dp, otherDp);
            }

            cell.addEventListener('click', handleToggle);
            cell.addEventListener('touchend', function(e) {
                if (e.target.closest('.air-datepicker')) return;
                if (e.cancelable) e.preventDefault();
                handleToggle(e);
            }, { passive: false });
        }

        bindCell(fromCell, dpFrom, dpTo);
        bindCell(toCell, dpTo, dpFrom);

        syncDateFieldState(fromInput, fromCell);
        syncDateFieldState(toInput, toCell);
    }

    function initNoteFields(root) {
        if (!root) return;

        root.querySelectorAll('.hb-field--note[data-hb-note-field]').forEach(function (wrap) {
            var field = wrap.querySelector('input[name="note"]');
            if (!field) return;
            field.setAttribute('placeholder', ' ');
        });
    }

    function boot() {
        var hero = document.getElementById('hero-booking');
        var contact = document.getElementById('contact-booking-form-root');
        initBookingRoot(hero);
        initBookingRoot(contact);
        initDateFields(hero);
        initDateFields(contact);
        initNoteFields(hero);
        initNoteFields(contact);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
