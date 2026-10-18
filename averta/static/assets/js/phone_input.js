(function () {
    "use strict";

    // Nömrə inputlarında yalnız rəqəm, boşluq və ən başda bir "+" yazmaq olar.
    function clean(value, final) {
        var plus = value.charAt(0) === '+' ? '+' : '';
        var rest = value.replace(/[^\d ]/g, '').replace(/ {2,}/g, ' ').replace(/^ +/, '');
        if (final) { rest = rest.replace(/ +$/, ''); }
        return plus + rest;
    }

    function bind(input) {
        if (input.dataset.phoneBound) { return; }
        input.dataset.phoneBound = '1';

        // Hərf və digər simvollar yazılmağa başlayanda dərhal bloklanır
        input.addEventListener('beforeinput', function (e) {
            if (!e.data || !e.inputType || e.inputType.indexOf('insert') !== 0) { return; }
            if (e.data === '+') {
                var start = this.selectionStart;
                var end = this.selectionEnd;
                var hasPlusElsewhere = this.value.indexOf('+') !== -1 && !(start === 0 && end > 0);
                if (start !== 0 || hasPlusElsewhere) { e.preventDefault(); }
                return;
            }
            if (!/^[\d ]+$/.test(e.data)) { e.preventDefault(); }
        });

        // Paste, avto-doldurma və digər hallar üçün təmizləmə
        input.addEventListener('input', function () {
            var cleaned = clean(this.value, false);
            if (cleaned !== this.value) { this.value = cleaned; }
        });

        input.addEventListener('blur', function () {
            this.value = clean(this.value, true);
        });

        input.value = clean(input.value, true);
    }

    function init() {
        document.querySelectorAll('input[name="phone"], input[inputmode="tel"]').forEach(bind);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();