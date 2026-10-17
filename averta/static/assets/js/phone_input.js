(function () {
    "use strict";

    // true edirsən: nömrənin əvvəlində bir "+" yazmağa icazə verilir (xarici nömrələr üçün)
    var ALLOW_PLUS = false;

    function clean(value) {
        var plus = ALLOW_PLUS && value.charAt(0) === '+' ? '+' : '';
        return plus + value.replace(/\D/g, '');
    }

    function bind(input) {
        if (input.dataset.phoneBound) { return; }
        input.dataset.phoneBound = '1';

        // Hərf/simvol yazılmağa başlayanda dərhal bloklanır (desktop + mobil)
        input.addEventListener('beforeinput', function (e) {
            if (e.data && e.inputType && e.inputType.indexOf('insert') === 0) {
                var ok = ALLOW_PLUS && e.data === '+' && this.selectionStart === 0
                    ? true
                    : /^\d+$/.test(e.data);
                if (!ok) { e.preventDefault(); }
            }
        });

        // Paste, avto-doldurma və digər hallar üçün son təmizləmə
        input.addEventListener('input', function () {
            var cleaned = clean(this.value);
            if (cleaned !== this.value) { this.value = cleaned; }
        });

        input.addEventListener('blur', function () {
            this.value = clean(this.value);
        });

        input.value = clean(input.value);
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