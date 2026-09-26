(function () {
    'use strict';

    var urls = Array.isArray(window.aboutGalleryUrls) ? window.aboutGalleryUrls.slice() : [];
    if (!urls.length) return;

    var root = document.querySelector('.aglb');
    if (!root) return;

    var dialog = root.querySelector('.aglb__dialog');
    var imgEl = root.querySelector('.aglb__img');
    var figEl = root.querySelector('.aglb__figure');
    var counterEl = root.querySelector('.aglb__counter');
    var thumbsEl = root.querySelector('.aglb__thumbs');
    var btnPrev = root.querySelector('[data-aglb-prev]');
    var btnNext = root.querySelector('[data-aglb-next]');
    var closeEls = root.querySelectorAll('[data-aglb-close]');

    var state = {
        idx: 0,
        open: false,
        zoomed: false,
        lastFocus: null,
        preloaded: new Map(),
        pointer: null,
    };

    function clampIndex(i) {
        var n = urls.length;
        if (!n) return 0;
        return (i % n + n) % n;
    }

    function setRootOpen(open) {
        state.open = open;
        root.hidden = !open;
        root.setAttribute('aria-hidden', open ? 'false' : 'true');
        document.body.classList.toggle('aglb-open', open);
    }

    function setCounter() {
        counterEl.textContent = (state.idx + 1) + ' / ' + urls.length;
    }

    function buildThumbs() {
        if (!thumbsEl || thumbsEl.dataset.built) return;
        thumbsEl.dataset.built = '1';

        var frag = document.createDocumentFragment();
        for (var i = 0; i < urls.length; i++) {
            var b = document.createElement('button');
            b.type = 'button';
            b.className = 'aglb__thumb';
            b.setAttribute('role', 'tab');
            b.setAttribute('aria-selected', 'false');
            b.dataset.idx = String(i);

            var tImg = document.createElement('img');
            tImg.loading = 'lazy';
            tImg.decoding = 'async';
            tImg.alt = '';
            tImg.src = urls[i];
            tImg.className = 'aglb__thumb-img';

            b.appendChild(tImg);
            frag.appendChild(b);
        }
        thumbsEl.appendChild(frag);
    }

    function setActiveThumb() {
        if (!thumbsEl) return;
        var active = thumbsEl.querySelector('.aglb__thumb.is-active');
        if (active) {
            active.classList.remove('is-active');
            active.setAttribute('aria-selected', 'false');
        }
        var next = thumbsEl.querySelector('.aglb__thumb[data-idx="' + state.idx + '"]');
        if (next) {
            next.classList.add('is-active');
            next.setAttribute('aria-selected', 'true');
            next.scrollIntoView({ block: 'nearest', inline: 'nearest' });
        }
    }

    function preload(url) {
        if (!url) return;
        if (state.preloaded.has(url)) return;

        var im = new Image();
        im.decoding = 'async';
        im.src = url;
        state.preloaded.set(url, im);
    }

    function preloadNeighbors() {
        preload(urls[clampIndex(state.idx - 1)]);
        preload(urls[clampIndex(state.idx + 1)]);
    }

    function setZoom(zoomed, originX, originY) {
        state.zoomed = zoomed;
        root.classList.toggle('is-zoomed', zoomed);
        if (zoomed && typeof originX === 'number' && typeof originY === 'number') {
            imgEl.style.transformOrigin = originX + '% ' + originY + '%';
        } else {
            imgEl.style.transformOrigin = '';
        }
    }

    function loadImageTo(url, alt, animate) {
        setCounter();
        setActiveThumb();
        preloadNeighbors();
        setZoom(false);

        figEl.classList.remove('is-ready');
        figEl.classList.add('is-loading');

        var tmp = new Image();
        tmp.decoding = 'async';
        tmp.src = url;

        var commit = function () {
            if (animate === false) {
                // avoid long fades on first paint
                imgEl.style.transition = 'none';
                requestAnimationFrame(function () { imgEl.style.transition = ''; });
            }
            imgEl.src = url;
            imgEl.alt = alt || '';
            figEl.classList.remove('is-loading');
            figEl.classList.add('is-ready');
        };

        if (tmp.decode) {
            tmp.decode().then(commit).catch(commit);
        } else {
            tmp.onload = commit;
            tmp.onerror = commit;
        }
    }

    function goTo(i, animate) {
        state.idx = clampIndex(i);
        loadImageTo(urls[state.idx], 'Gallery image ' + (state.idx + 1), animate !== false);
    }

    function trapFocus(e) {
        if (!state.open || e.key !== 'Tab') return;
        var focusables = dialog.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (!focusables.length) return;
        var first = focusables[0];
        var last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault();
            first.focus();
        }
    }

    function onKeyDown(e) {
        if (!state.open) return;
        if (e.key === 'Escape') {
            e.preventDefault();
            close();
            return;
        }
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            goTo(state.idx - 1);
            return;
        }
        if (e.key === 'ArrowRight') {
            e.preventDefault();
            goTo(state.idx + 1);
            return;
        }
        trapFocus(e);
    }

    function open(i) {
        state.lastFocus = document.activeElement;
        buildThumbs();
        setRootOpen(true);
        goTo(i, false);

        // small warmup so first transition is smooth
        requestAnimationFrame(function () {
            dialog.focus({ preventScroll: true });
        });
        window.addEventListener('keydown', onKeyDown, { passive: false });
    }

    function close() {
        window.removeEventListener('keydown', onKeyDown);
        setZoom(false);
        setRootOpen(false);
        if (state.lastFocus && state.lastFocus.focus) {
            state.lastFocus.focus({ preventScroll: true });
        }
        state.lastFocus = null;
    }

    function onThumbClick(e) {
        var btn = e.target && e.target.closest ? e.target.closest('.aglb__thumb') : null;
        if (!btn) return;
        var i = parseInt(btn.dataset.idx, 10);
        if (!Number.isNaN(i)) goTo(i);
    }

    function onNavClick(dir) {
        goTo(state.idx + dir);
    }

    function onDocClick(e) {
        var a = e.target && e.target.closest ? e.target.closest('[data-about-gallery-item]') : null;
        if (!a) return;
        e.preventDefault();
        var i = parseInt(a.getAttribute('data-about-gallery-index'), 10);
        open(Number.isNaN(i) ? 0 : i);
    }

    function onPrewarm(e) {
        var a = e.target && e.target.closest ? e.target.closest('[data-about-gallery-item]') : null;
        if (!a) return;
        var i = parseInt(a.getAttribute('data-about-gallery-index'), 10);
        if (Number.isNaN(i)) i = 0;
        preload(urls[i]);
        preload(urls[clampIndex(i + 1)]);
        preload(urls[clampIndex(i - 1)]);
    }

    function pointerDown(e) {
        if (!state.open) return;
        state.pointer = { x: e.clientX, y: e.clientY, id: e.pointerId };
    }

    function pointerUp(e) {
        if (!state.open || !state.pointer || state.pointer.id !== e.pointerId) return;
        var dx = e.clientX - state.pointer.x;
        var dy = e.clientY - state.pointer.y;
        state.pointer = null;

        if (Math.abs(dx) < 40 || Math.abs(dx) < Math.abs(dy) * 1.2) return;
        if (dx > 0) onNavClick(-1);
        else onNavClick(1);
    }

    function onFigureClick(e) {
        if (!state.open) return;
        // toggle zoom with smooth origin
        var rect = imgEl.getBoundingClientRect();
        if (!rect.width || !rect.height) {
            setZoom(!state.zoomed);
            return;
        }
        var ox = ((e.clientX - rect.left) / rect.width) * 100;
        var oy = ((e.clientY - rect.top) / rect.height) * 100;
        setZoom(!state.zoomed, Math.max(0, Math.min(100, ox)), Math.max(0, Math.min(100, oy)));
    }

    // Wire up
    document.addEventListener('click', onDocClick);
    document.addEventListener('pointerover', onPrewarm, { passive: true });
    document.addEventListener('touchstart', onPrewarm, { passive: true });

    if (btnPrev) btnPrev.addEventListener('click', function () { onNavClick(-1); });
    if (btnNext) btnNext.addEventListener('click', function () { onNavClick(1); });
    if (thumbsEl) thumbsEl.addEventListener('click', onThumbClick);

    closeEls.forEach(function (el) {
        el.addEventListener('click', function (e) {
            e.preventDefault();
            close();
        });
    });

    if (figEl) {
        figEl.addEventListener('click', onFigureClick);
        figEl.addEventListener('pointerdown', pointerDown, { passive: true });
        figEl.addEventListener('pointerup', pointerUp, { passive: true });
    }

    // Preload first image quietly for perceived speed
    preload(urls[0]);
})();

