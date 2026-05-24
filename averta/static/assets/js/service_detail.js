(function ($) {
    'use strict';

    $(function () {

        // ── Gallery carousel ──────────────────────────────────────
        var $carousel = $('#sdpGalleryCarousel');

        if ($carousel.length) {
            $carousel.owlCarousel({
                loop: false,
                margin: 14,
                nav: false,
                dots: true,
                dotsEach: 1,
                autoplay: false,
                smartSpeed: 430,
                responsive: {
                    0:    { items: 1, margin: 0, stagePadding: 0 },
                    768:  { items: 2, margin: 18, stagePadding: 0 },
                    1200: { items: 2, margin: 22, stagePadding: 0 },
                },
            });

            $(document).on('click', '.sdp-gallery-btn--prev', function () {
                $carousel.trigger('prev.owl.carousel');
            });

            $(document).on('click', '.sdp-gallery-btn--next', function () {
                $carousel.trigger('next.owl.carousel');
            });

            // Klaviatura dəstəyi
            $(document).on('keydown', '.sdp-gallery-card', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    $(this).trigger('click');
                }
            });
        }

        // ── Digər xidmətlər — şaquli karusel ─────────────────────
        var $relatedTrack = $('#sdpRelatedTrack');

        if ($relatedTrack.length) {
            var $navUp = $('.sdp-related-nav--up');
            var $navDown = $('.sdp-related-nav--down');

            function updateRelatedNav() {
                var el = $relatedTrack[0];
                if (!el) { return; }
                var atTop = el.scrollTop <= 4;
                var atBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 4;
                $navUp.prop('disabled', atTop);
                $navDown.prop('disabled', atBottom);
            }

            function scrollRelated(direction) {
                var el = $relatedTrack[0];
                if (!el) { return; }
                var step = Math.max(el.clientHeight * 0.75, 140);
                el.scrollBy({ top: direction * step, behavior: 'smooth' });
            }

            $relatedTrack.on('scroll', updateRelatedNav);
            $(window).on('resize', updateRelatedNav);

            $(document).on('click', '.sdp-related-nav--up', function () {
                scrollRelated(-1);
            });

            $(document).on('click', '.sdp-related-nav--down', function () {
                scrollRelated(1);
            });

            updateRelatedNav();
        }

        // ── Lightbox ──────────────────────────────────────────────
        if (typeof lightbox === 'undefined') {
            return;
        }

        // Bütün şəkilləri öncədən yüklə
        var preloaded = {};
        function preload(url) {
            if (!url || preloaded[url]) { return; }
            preloaded[url] = true;
            (new Image()).src = url;
        }

        if (window.serviceGalleryUrls && window.serviceGalleryUrls.length) {
            window.serviceGalleryUrls.forEach(preload);
        }

        lightbox.option({
            fadeDuration: 200,
            imageFadeDuration: 150,
            resizeDuration: 200,
            wrapAround: true,
            albumLabel: '%1 / %2',
            disableScrolling: true,
            alwaysShowNavOnTouchDevices: true,
        });

        // Kart klikləndikdə — indeksə görə gizli trigger-i işlət
        // (Owl klon elementi lightbox-u qarışdırmasın deyə hidden trigger yanaşması)
        $(document).on('click', '.sdp-gallery-card', function (e) {
            e.preventDefault();
            var idx = parseInt($(this).data('gallery-index')) || 0;
            var $trigger = $('.sdp-gallery__triggers a').eq(idx);
            if ($trigger.length) {
                lightbox.start($trigger);
            }
        });

    });

}(jQuery));
