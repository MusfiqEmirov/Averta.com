(function ($) {
    'use strict';

    $(function () {
        if (typeof lightbox === 'undefined') {
            return;
        }

        var preloaded = {};

        function preload(url) {
            if (!url || preloaded[url]) {
                return;
            }
            preloaded[url] = true;
            var img = new Image();
            img.src = url;
        }

        function preloadAlbum(albumName) {
            $('a[data-lightbox="' + albumName + '"]').each(function () {
                preload(this.href);
            });
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

        if (window.serviceGalleryUrls && window.serviceGalleryUrls.length) {
            window.serviceGalleryUrls.forEach(preload);
        }

        $(document).on('click', '.service-detail-gallery-card[data-lightbox]', function (e) {
            e.preventDefault();
            var album = this.getAttribute('data-lightbox');
            preloadAlbum(album);
            lightbox.start($(this));
        });
    });
}(jQuery));
