(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner(0);

    // Hero banner — preload slides (deployda next/prev zamanı ağ flash azalır)
    (function () {
        var carousel = document.getElementById('carouselId');
        if (!carousel) { return; }

        function preloadSrc(src) {
            if (!src) { return; }
            var img = new Image();
            img.src = src;
        }

        carousel.querySelectorAll('.carousel-item img[src]').forEach(function (el) {
            preloadSrc(el.currentSrc || el.src);
        });

        carousel.addEventListener('slide.bs.carousel', function (e) {
            var items = carousel.querySelectorAll('.carousel-item');
            var n = items.length;
            if (!n) { return; }
            var next = e.to;
            [next, (next + 1) % n, (next - 1 + n) % n].forEach(function (idx) {
                var slide = items[idx];
                if (!slide) { return; }
                var el = slide.querySelector('img');
                if (el) { preloadSrc(el.currentSrc || el.src); }
            });
        });
    })();


    // Sticky Navbar (smooth size transition via CSS on .sticky-top)
    $(window).on('scroll', function () {
        var $navbar = $('.navbar');
        if ($(this).scrollTop() > 45) {
            $navbar.addClass('sticky-top shadow-sm navbar-scrolled');
        } else {
            $navbar.removeClass('sticky-top shadow-sm navbar-scrolled');
        }
    });


    // International Tour carousel
    $(".InternationalTour-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        center: false,
        dots: true,
        loop: true,
        margin: 25,
        nav : false,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:2
            },
            1200:{
                items:3
            }
        }
    });


    // packages carousel
    $(".packages-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        center: false,
        dots: false,
        loop: true,
        margin: 25,
        nav : true,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:2
            },
            1200:{
                items:3
            }
        }
    });

    // partners strip — auto smooth scroll + manual drag / touch / wheel
    (function () {
        var LOOP_DURATION_MS = 22000;
        var LOOP_DURATION_MOBILE_MS = 12000;
        var MOBILE_MQ = window.matchMedia('(max-width: 767.98px)');

        function getLoopDuration() {
            return MOBILE_MQ.matches ? LOOP_DURATION_MOBILE_MS : LOOP_DURATION_MS;
        }

        var RESUME_DELAY_MS = 2500;

        document.querySelectorAll('.partner-carousel.partners-strip__carousel').forEach(function (strip) {
            strip.classList.remove('owl-carousel');

            var items = Array.from(strip.children);
            if (!items.length) { return; }

            var track = document.createElement('div');
            track.className = 'partners-marquee-track';
            items.forEach(function (item) { track.appendChild(item); });

            var clone = track.cloneNode(true);
            clone.setAttribute('aria-hidden', 'true');

            strip.appendChild(track);
            strip.appendChild(clone);

            var loopWidth = 0;
            var autoPaused = false;
            var resumeTimer = null;
            var rafId = null;
            var suppressScrollPause = false;
            var activePointerId = null;
            var dragStartX = 0;
            var dragScrollLeft = 0;

            function measureLoop() {
                loopWidth = track.scrollWidth;
            }

            function autoSpeed() {
                return loopWidth / (getLoopDuration() / 16.67);
            }

            function canAutoScroll() {
                return loopWidth > strip.clientWidth + 1;
            }

            function normalizeScroll() {
                if (!loopWidth) { return; }
                while (strip.scrollLeft >= loopWidth) {
                    strip.scrollLeft -= loopWidth;
                }
                while (strip.scrollLeft < 0) {
                    strip.scrollLeft += loopWidth;
                }
            }

            function pauseAuto() {
                autoPaused = true;
                clearTimeout(resumeTimer);
            }

            function scheduleResume() {
                clearTimeout(resumeTimer);
                resumeTimer = setTimeout(function () {
                    autoPaused = false;
                }, RESUME_DELAY_MS);
            }

            function tick() {
                if (!autoPaused && canAutoScroll()) {
                    suppressScrollPause = true;
                    strip.scrollLeft += autoSpeed();
                    if (strip.scrollLeft >= loopWidth) {
                        strip.scrollLeft -= loopWidth;
                    }
                    requestAnimationFrame(function () {
                        suppressScrollPause = false;
                    });
                }
                rafId = requestAnimationFrame(tick);
            }

            strip.addEventListener('pointerdown', function (e) {
                pauseAuto();
                if (e.pointerType !== 'mouse' || e.button !== 0) { return; }
                activePointerId = e.pointerId;
                dragStartX = e.clientX;
                dragScrollLeft = strip.scrollLeft;
                strip.classList.add('is-dragging');
                strip.setPointerCapture(e.pointerId);
            });

            strip.addEventListener('pointermove', function (e) {
                if (activePointerId !== e.pointerId) { return; }
                e.preventDefault();
                strip.scrollLeft = dragScrollLeft - (e.clientX - dragStartX);
            });

            function endPointer(e) {
                if (activePointerId !== null && activePointerId !== e.pointerId) { return; }
                if (activePointerId === e.pointerId) {
                    strip.classList.remove('is-dragging');
                    if (strip.hasPointerCapture(e.pointerId)) {
                        strip.releasePointerCapture(e.pointerId);
                    }
                    activePointerId = null;
                    normalizeScroll();
                }
                scheduleResume();
            }

            strip.addEventListener('pointerup', endPointer);
            strip.addEventListener('pointercancel', endPointer);

            strip.addEventListener('touchstart', function () {
                pauseAuto();
            }, { passive: true });

            strip.addEventListener('touchend', function () {
                normalizeScroll();
                scheduleResume();
            }, { passive: true });

            strip.addEventListener('scroll', function () {
                normalizeScroll();
                if (suppressScrollPause) { return; }
                pauseAuto();
                scheduleResume();
            }, { passive: true });

            strip.querySelectorAll('img').forEach(function (img) {
                img.draggable = false;
            });

            measureLoop();
            window.addEventListener('resize', measureLoop);
            rafId = requestAnimationFrame(tick);
        });
    })();



    // Back to top
    (function () {
        var backToTop = document.querySelector('.back-to-top');
        if (!backToTop) { return; }

        var scrollingTimer = null;

        function toggleBackToTop() {
            backToTop.classList.toggle('show', window.scrollY > 300);
        }

        function scrollToTop(event) {
            event.preventDefault();
            backToTop.classList.add('back-to-top--scrolling');
            window.scrollTo({ top: 0, behavior: 'smooth' });
            clearTimeout(scrollingTimer);
            scrollingTimer = setTimeout(function () {
                backToTop.classList.remove('back-to-top--scrolling');
            }, 1200);
        }

        window.addEventListener('scroll', toggleBackToTop, { passive: true });
        toggleBackToTop();
        backToTop.addEventListener('click', scrollToTop);
    })();


    // Language switcher — hover to open (desktop topbar)
    function initLangSwitcherHover() {
        if (typeof bootstrap === 'undefined' || !window.matchMedia('(hover: hover)').matches) {
            return;
        }

        var closeDelayMs = 380;

        $('.lang-switcher-form:not(.lang-switcher-form--mobile) .lang-switcher-dropdown').each(function () {
            var $dropdown = $(this);
            var $menu = $dropdown.find('.lang-switcher-menu');
            var toggleEl = $dropdown.find('[data-bs-toggle="dropdown"]')[0];
            if (!toggleEl) {
                return;
            }

            var dd = bootstrap.Dropdown.getOrCreateInstance(toggleEl, { autoClose: true });
            var closeTimer = null;

            function openDropdown() {
                clearTimeout(closeTimer);
                closeTimer = null;
                dd.show();
            }

            function scheduleClose() {
                clearTimeout(closeTimer);
                closeTimer = setTimeout(function () {
                    dd.hide();
                }, closeDelayMs);
            }

            $dropdown.on('mouseenter', openDropdown);
            $menu.on('mouseenter', openDropdown);
            $dropdown.on('mouseleave', scheduleClose);
            $menu.on('mouseleave', scheduleClose);
        });
    }

    initLangSwitcherHover();


    // Ana səhifə bölmələrinə scroll (#packages, #testimonial)
    function scrollToHomeSectionHash() {
        var hash = window.location.hash;
        if (!hash) { return; }
        var id = hash.replace('#', '');
        if (id !== 'packages' && id !== 'testimonial') { return; }
        var section = document.getElementById(id);
        if (section) {
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    scrollToHomeSectionHash();
    setTimeout(scrollToHomeSectionHash, 300);
    $(window).on('hashchange', scrollToHomeSectionHash);

})(jQuery);

