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

