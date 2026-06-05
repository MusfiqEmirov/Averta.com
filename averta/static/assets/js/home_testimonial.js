(function ($) {
    'use strict';

    /* ------------------------------------------------------------------ */
    /*  Ulduz seçici                                                        */
    /* ------------------------------------------------------------------ */
    function initStars() {
        var picker = document.getElementById('starPicker');
        var input  = document.getElementById('ratingInput');
        if (!picker || !input) { return; }

        var stars   = picker.querySelectorAll('.star-btn');
        var current = parseInt(input.value, 10);
        if (isNaN(current) || current < 1) { current = 0; }

        function paint(val) {
            stars.forEach(function (star) {
                star.style.color = parseInt(star.dataset.val, 10) <= val ? '#ffc107' : '#ddd';
            });
        }

        paint(current);

        stars.forEach(function (star) {
            star.addEventListener('click', function () {
                current     = parseInt(star.dataset.val, 10);
                input.value = current;
                paint(current);
                clearFieldError('ratingError');
            });
            star.addEventListener('mouseenter', function () { paint(parseInt(star.dataset.val, 10)); });
            star.addEventListener('mouseleave', function () { paint(current); });
        });
    }

    /* ------------------------------------------------------------------ */
    /*  Client-side form validasiyası (server-ə boş sahə getməsin)         */
    /* ------------------------------------------------------------------ */
    function setFieldError(inputId, errorId, msg) {
        var el = document.getElementById(inputId);
        if (el) { el.classList.add('is-invalid'); }
        var err = document.getElementById(errorId);
        if (!err) {
            err = document.createElement('div');
            err.id        = errorId;
            err.className = 'invalid-feedback d-block';
            if (el) { el.insertAdjacentElement('afterend', err); }
        }
        err.textContent = msg;
    }

    function clearFieldError(errorId) {
        var err = document.getElementById(errorId);
        if (err) { err.textContent = ''; err.className = 'invalid-feedback'; }
    }

    function clearInputError(inputId) {
        var el = document.getElementById(inputId);
        if (el) { el.classList.remove('is-invalid'); }
    }

    function validateReviewForm() {
        var ok = true;

        /* Ad */
        var name = (document.getElementById('reviewName') || {}).value || '';
        if (!name.trim()) {
            setFieldError('reviewName', 'nameError', 'Ad mütləq doldurulmalıdır.');
            ok = false;
        } else if (name.trim().length < 2) {
            setFieldError('reviewName', 'nameError', 'Ad ən azı 2 hərf olmalıdır.');
            ok = false;
        } else if (name.length > 50) {
            setFieldError('reviewName', 'nameError', 'Ad ən çoxu 50 simvol ola bilər.');
            ok = false;
        } else {
            clearFieldError('nameError');
            clearInputError('reviewName');
        }

        /* Mobil nömrə */
        var phone = (document.getElementById('reviewPhone') || {}).value || '';
        var phoneTrim = phone.trim();
        var phoneDigits = phoneTrim.replace(/\D/g, '');

        if (!phoneTrim) {
            setFieldError('reviewPhone', 'phoneError', 'Mobil nömrə mütləq doldurulmalıdır.');
            ok = false;
        } else if (phoneDigits.length < 9) {
            setFieldError('reviewPhone', 'phoneError', 'Düzgün mobil nömrə daxil edin.');
            ok = false;
        } else {
            clearFieldError('phoneError');
            clearInputError('reviewPhone');
        }

        /* Reytinq */
        var rating = parseInt((document.getElementById('ratingInput') || {}).value, 10);
        var ratingErr = document.getElementById('ratingError');
        if (!ratingErr) {
            ratingErr = document.createElement('div');
            ratingErr.id        = 'ratingError';
            ratingErr.className = 'text-danger small mt-1';
            var picker = document.getElementById('starPicker');
            if (picker) { picker.insertAdjacentElement('afterend', ratingErr); }
        }
        if (!rating || rating < 1) {
            ratingErr.textContent = 'Ulduz reytinqi seçin.';
            ok = false;
        } else {
            ratingErr.textContent = '';
        }

        /* Xidmət / paket */
        var targetVal = (document.getElementById('reviewTarget') || {}).value || '';
        if (!targetVal) {
            setFieldError('reviewTarget', 'targetError', 'Aldığınız xidmət və ya paketi seçin.');
            ok = false;
        } else {
            clearFieldError('targetError');
            clearInputError('reviewTarget');
        }

        /* Mətn */
        var msg = (document.getElementById('reviewMessage') || {}).value || '';
        if (!msg.trim()) {
            setFieldError('reviewMessage', 'messageError', 'Rəy mətni mütləq doldurulmalıdır.');
            ok = false;
        } else if (msg.trim().length < 5) {
            setFieldError('reviewMessage', 'messageError', 'Rəy ən azı 5 hərf olmalıdır.');
            ok = false;
        } else if (msg.length > 190) {
            setFieldError('reviewMessage', 'messageError', 'Rəy ən çoxu 190 simvol ola bilər.');
            ok = false;
        } else {
            clearFieldError('messageError');
            clearInputError('reviewMessage');
        }

        return ok;
    }

    /* ------------------------------------------------------------------ */
    /*  Feedback alert — bağlama düyməsi ajax_forms.js tərəfindən idarə olunur */
    /* ------------------------------------------------------------------ */

    /* ------------------------------------------------------------------ */
    /*  Modal — server xətası varsa avtomatik aç                           */
    /* ------------------------------------------------------------------ */
    function openReviewModalIfErrors() {
        var root = document.getElementById('testimonial');
        if (!root || root.dataset.reviewFormErrors !== 'true') { return; }
        var modalEl = document.getElementById('reviewModal');
        if (modalEl && typeof bootstrap !== 'undefined') {
            bootstrap.Modal.getOrCreateInstance(modalEl).show();
        }
    }

    /* ------------------------------------------------------------------ */
    /*  Rəy carousel — eyni kart ölçüsü; az rəydə yalnız mərkəz          */
    /* ------------------------------------------------------------------ */
    var REVIEW_CAROUSEL_MANY = {
        0: 1,
        768: 2,
        1200: 3,
        1400: 4
    };

    function buildResponsive() {
        var responsive = {};
        var breakpoints = [
            [0, REVIEW_CAROUSEL_MANY[0]],
            [768, REVIEW_CAROUSEL_MANY[768]],
            [1200, REVIEW_CAROUSEL_MANY[1200]],
            [1400, REVIEW_CAROUSEL_MANY[1400]]
        ];

        breakpoints.forEach(function (bp) {
            responsive[bp[0]] = { items: bp[1] };
        });
        return responsive;
    }

    function bindFewReviewCentering($carousel, $wrap) {
        if (!$wrap.hasClass('testimonial-carousel-wrap--few')) {
            return;
        }

        function centerStage() {
            window.requestAnimationFrame(function () {
                var $outer = $carousel.find('.owl-stage-outer');
                var $stage = $carousel.find('.owl-stage');
                var $items = $stage.children('.owl-item');
                if (!$items.length) {
                    return;
                }

                var itemW = $items.first().outerWidth(true);
                var totalW = itemW * $items.length;
                var viewW = $outer.innerWidth();
                var offset = Math.max(0, Math.round((viewW - totalW) / 2));

                $stage.css({
                    transform: 'translate3d(' + offset + 'px, 0px, 0px)',
                    transition: 'none'
                });
            });
        }

        $carousel.on(
            'initialized.owl.carousel refreshed.owl.carousel resized.owl.carousel',
            centerStage
        );
        $(window).on('resize.testimonialFew', centerStage);
        centerStage();
    }

    function initTestimonialCarousel() {
        var $wrap = $('.testimonial-carousel-wrap');
        if (!$wrap.length) { return; }

        var total = parseInt($wrap.data('review-count'), 10) || 0;
        var threshold = parseInt($wrap.data('few-threshold'), 10) || 4;
        var $carousel = $wrap.find('.testimonial-carousel');
        if (!$carousel.length || total < 1) { return; }

        var few = total <= threshold;
        $wrap.toggleClass('testimonial-carousel-wrap--few', few);
        $wrap.toggleClass('testimonial-carousel-wrap--many', !few);

        $carousel.owlCarousel({
            autoplay: !few && total > 1,
            autoplayTimeout: 5000,
            smartSpeed: 650,
            center: false,
            dots: false,
            loop: !few && total > 1,
            margin: 14,
            mouseDrag: !few,
            touchDrag: !few,
            pullDrag: !few,
            nav: false,
            responsiveClass: true,
            responsive: buildResponsive()
        });

        bindFewReviewCentering($carousel, $wrap);

        var $toolbar = $wrap.find('.testimonial-carousel-toolbar');
        $toolbar.toggle(!few);

        $wrap.find('.testimonial-carousel-prev').on('click', function () {
            $carousel.trigger('prev.owl.carousel');
        });
        $wrap.find('.testimonial-carousel-next').on('click', function () {
            $carousel.trigger('next.owl.carousel');
        });
    }

    /* ------------------------------------------------------------------ */
    /*  Xidmət / paket — birləşmiş seçim                                   */
    /* ------------------------------------------------------------------ */
    function initReviewTargetSelects() {
        var targetSel = document.getElementById('reviewTarget');
        if (!targetSel) { return; }

        targetSel.addEventListener('change', function () {
            clearFieldError('targetError');
            targetSel.classList.remove('is-invalid');
        });
    }

    /* ------------------------------------------------------------------ */
    /*  Rəy mətni sayğacı (max 190)                                        */
    /* ------------------------------------------------------------------ */
    function initReviewMessageCounter() {
        var textarea = document.getElementById('reviewMessage');
        var counter = document.getElementById('reviewMessageCounter');
        if (!textarea || !counter) { return; }

        function update() {
            var len = textarea.value.length;
            counter.textContent = len + ' / 190';
            counter.classList.toggle('text-danger', len >= 190);
        }

        textarea.addEventListener('input', update);
        update();
    }

    /* ------------------------------------------------------------------ */
    /*  DOMContentLoaded                                                    */
    /* ------------------------------------------------------------------ */
    $(function () {
        initStars();
        initReviewTargetSelects();
        initTestimonialCarousel();
        initReviewMessageCounter();
        openReviewModalIfErrors();

        /* Form submit — əvvəlcə client-side yoxla */
        var form = document.getElementById('reviewForm');
        if (form) {
            form.addEventListener('submit', function (e) {
                if (!validateReviewForm()) {
                    e.preventDefault();
                }
            });
        }

        /* Input dəyişəndə xətanı sil */
        ['reviewName', 'reviewPhone', 'reviewTarget', 'reviewMessage'].forEach(function (id) {
            var el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', function () {
                    el.classList.remove('is-invalid');
                });
            }
        });
    });
})(jQuery);
