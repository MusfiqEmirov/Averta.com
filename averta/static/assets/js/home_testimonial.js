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
        } else {
            clearFieldError('nameError');
            clearInputError('reviewName');
        }

        /* E-poçt */
        var email = (document.getElementById('reviewEmail') || {}).value || '';
        if (!email.trim()) {
            setFieldError('reviewEmail', 'emailError', 'E-poçt mütləq doldurulmalıdır.');
            ok = false;
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
            setFieldError('reviewEmail', 'emailError', 'Düzgün e-poçt ünvanı daxil edin.');
            ok = false;
        } else {
            clearFieldError('emailError');
            clearInputError('reviewEmail');
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

        /* Mətn */
        var msg = (document.getElementById('reviewMessage') || {}).value || '';
        if (!msg.trim()) {
            setFieldError('reviewMessage', 'messageError', 'Rəy mətni mütləq doldurulmalıdır.');
            ok = false;
        } else if (msg.trim().length < 5) {
            setFieldError('reviewMessage', 'messageError', 'Rəy ən azı 5 hərf olmalıdır.');
            ok = false;
        } else {
            clearFieldError('messageError');
            clearInputError('reviewMessage');
        }

        return ok;
    }

    /* ------------------------------------------------------------------ */
    /*  Testimonial-ə scroll (redirect-dən sonra)                          */
    /* ------------------------------------------------------------------ */
    function scrollToTestimonialIfHash() {
        if (window.location.hash !== '#testimonial') { return; }
        var section = document.getElementById('testimonial');
        if (section) { section.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    }

    /* ------------------------------------------------------------------ */
    /*  Feedback alert — 2 saniyə sonra yox olur                           */
    /* ------------------------------------------------------------------ */
    function dismissReviewFeedbackAlert() {
        var feedbackAlert = document.querySelector('.review-feedback-alert');
        if (!feedbackAlert) { return; }
        setTimeout(function () {
            feedbackAlert.style.transition = 'opacity 0.4s ease';
            feedbackAlert.style.opacity    = '0';
            setTimeout(function () { feedbackAlert.remove(); }, 400);
        }, 2000);
    }

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
    /*  DOMContentLoaded                                                    */
    /* ------------------------------------------------------------------ */
    $(function () {
        initStars();
        scrollToTestimonialIfHash();
        dismissReviewFeedbackAlert();
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
        ['reviewName', 'reviewEmail', 'reviewMessage'].forEach(function (id) {
            var el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', function () {
                    el.classList.remove('is-invalid');
                });
            }
        });
    });
})(jQuery);
