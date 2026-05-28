/**
 * Progressive enhancement: submit forms via fetch to avoid full page refresh.
 * Server must reply with JSON when X-Requested-With=XMLHttpRequest.
 */
(function () {
  function isAjaxForm(form) {
    return form && form.matches && form.matches('form[data-ajax="1"]');
  }

  function ensureFeedbackBox(form) {
    var box = form.querySelector('[data-ajax-feedback]');
    if (box) return box;
    box = document.createElement('div');
    box.setAttribute('data-ajax-feedback', '1');
    box.setAttribute('aria-live', 'polite');
    box.className = 'alert d-none mt-3';
    form.insertBefore(box, form.firstChild);
    return box;
  }

  function setFeedback(box, type, text) {
    if (!box) return;
    box.classList.remove('d-none', 'alert-success', 'alert-danger', 'alert-warning');
    if (type === 'success') box.classList.add('alert-success');
    else if (type === 'warning') box.classList.add('alert-warning');
    else box.classList.add('alert-danger');
    box.textContent = text || '';
  }

  function clearFeedback(box) {
    if (!box) return;
    box.className = 'alert d-none mt-3';
    box.textContent = '';
  }

  function getFirstErrorText(errors) {
    if (!errors) return '';
    // Non-field first
    if (errors.__all__ && errors.__all__.length) {
      return errors.__all__[0].message || String(errors.__all__[0]);
    }
    var keys = Object.keys(errors);
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (!errors[k] || !errors[k].length) continue;
      return errors[k][0].message || String(errors[k][0]);
    }
    return '';
  }

  function resetTurnstileIfPresent(form) {
    try {
      if (typeof turnstile === 'undefined' || !turnstile || !turnstile.reset) return;
      var widget = form.querySelector('.cf-turnstile');
      if (!widget) return;
      // Reset all widgets (safe) – Cloudflare doesn't expose per-widget id reliably in vanilla mode.
      turnstile.reset();
    } catch (e) {
      // ignore
    }
  }

  function onSubmit(e) {
    var form = e.target;
    if (!isAjaxForm(form)) return;
    e.preventDefault();

    var box = ensureFeedbackBox(form);
    clearFeedback(box);

    var fd = new FormData(form);
    var action = form.getAttribute('action') || window.location.href;

    fetch(action, {
      method: 'POST',
      body: fd,
      credentials: 'same-origin',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
      .then(function (res) {
        return res.json().then(function (data) {
          return { ok: res.ok, data: data };
        });
      })
      .then(function (r) {
        var data = r.data || {};
        if (data.ok) {
          setFeedback(box, 'success', data.message || 'OK');
          // For successful submissions, clear user-entered fields.
          form.reset();
        } else {
          var msg = data.message || getFirstErrorText(data.errors) || 'Xəta baş verdi.';
          setFeedback(box, 'danger', msg);
        }
        resetTurnstileIfPresent(form);

        // Review modal: keep it open on errors/success (no page reload anyway).
      })
      .catch(function () {
        setFeedback(box, 'danger', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
        resetTurnstileIfPresent(form);
      });
  }

  document.addEventListener('submit', onSubmit, true);
})();

