/**
 * Progressive enhancement: submit forms via fetch to avoid full page refresh.
 * Server must reply with JSON when X-Requested-With=XMLHttpRequest.
 */
(function () {
  function isAjaxForm(form) {
    return form && form.matches && form.matches('form[data-ajax="1"]');
  }

  function dismissFormFeedback(el) {
    if (!el) return;
    el.style.transition = 'opacity 0.25s ease';
    el.style.opacity = '0';
    setTimeout(function () {
      if (el.hasAttribute('data-ajax-feedback')) {
        clearFeedback(el);
        el.style.opacity = '';
        el.style.transition = '';
        return;
      }
      el.remove();
    }, 250);
  }

  function attachDismissButton(alertEl) {
    if (!alertEl || alertEl.querySelector('.form-feedback-alert__close')) return;
    alertEl.classList.add('form-feedback-alert');

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'form-feedback-alert__close';
    btn.setAttribute('aria-label', 'Bağla');
    btn.innerHTML = '&times;';
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      dismissFormFeedback(alertEl);
    });
    alertEl.appendChild(btn);
  }

  function initFormFeedbackDismiss(root) {
    var scope = root || document;
    scope.querySelectorAll('[data-form-feedback]').forEach(attachDismissButton);
  }

  function ensureFeedbackBox(form) {
    var box = form.querySelector('[data-ajax-feedback]');
    if (box) return box;
    box = document.createElement('div');
    box.setAttribute('data-ajax-feedback', '1');
    box.setAttribute('data-form-feedback', '1');
    box.setAttribute('aria-live', 'polite');
    box.setAttribute('role', 'alert');
    box.className = 'alert d-none mt-3 form-feedback-alert';
    form.insertBefore(box, form.firstChild);
    return box;
  }

  function setFeedback(box, type, text) {
    if (!box) return;
    box.classList.remove('d-none', 'alert-success', 'alert-danger', 'alert-warning');
    if (type === 'success') box.classList.add('alert-success');
    else if (type === 'warning') box.classList.add('alert-warning');
    else box.classList.add('alert-danger');

    box.innerHTML = '';
    var span = document.createElement('span');
    span.className = 'form-feedback-alert__text';
    span.textContent = text || '';
    box.appendChild(span);
    attachDismissButton(box);
  }

  function clearFeedback(box) {
    if (!box) return;
    box.className = 'alert d-none mt-3 form-feedback-alert';
    box.textContent = '';
  }

  function getFirstErrorText(errors) {
    if (!errors) return '';
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

  function clearInlineErrors(form) {
    form.querySelectorAll('.ajax-field-error').forEach(function (el) { el.remove(); });
    form.querySelectorAll('.hb-field--has-error').forEach(function (el) {
      el.classList.remove('hb-field--has-error');
    });
    form.querySelectorAll('[aria-invalid="true"]').forEach(function (el) {
      el.removeAttribute('aria-invalid');
    });
    form.querySelectorAll('.is-invalid').forEach(function (el) {
      el.classList.remove('is-invalid');
    });
  }

  function findFormInput(form, fieldName) {
    var inputs = form.querySelectorAll('[name="' + fieldName + '"]');
    for (var i = 0; i < inputs.length; i++) {
      if (inputs[i].type === 'hidden') continue;
      return inputs[i];
    }
    return inputs.length ? inputs[0] : null;
  }

  function errorMessageFromList(msgs) {
    if (!msgs || !msgs.length) return '';
    if (typeof msgs[0] === 'string') return msgs[0];
    return (msgs[0] && msgs[0].message) ? msgs[0].message : String(msgs[0]);
  }

  function placeFieldError(input, msg) {
    var hbField = input.closest('.hb-field');
    if (hbField) {
      hbField.classList.add('hb-field--has-error');
      var errEl = document.createElement('p');
      errEl.className = 'hb-field-err ajax-field-error';
      errEl.textContent = msg;
      if (!(input.value || '').trim()) {
        errEl.classList.add('hb-field-err--infield');
      }
      hbField.appendChild(errEl);
      input.setAttribute('aria-invalid', 'true');
      return;
    }

    var errEl = document.createElement('div');
    errEl.className = 'text-warning small mt-1 ajax-field-error';
    errEl.textContent = msg;
    var wrapper = input.closest('.form-floating')
      || input.closest('.col-md-6')
      || input.closest('.col-12')
      || input.closest('[class*="col-"]')
      || input.parentNode;
    wrapper.appendChild(errEl);
    input.setAttribute('aria-invalid', 'true');
    input.classList.add('is-invalid');
  }

  function showInlineErrors(form, errors) {
    clearInlineErrors(form);
    if (!errors) return false;
    var shown = false;
    Object.keys(errors).forEach(function (fieldName) {
      if (fieldName === '__all__') return;
      var msgs = errors[fieldName];
      var msg = errorMessageFromList(msgs);
      if (!msg) return;
      var input = findFormInput(form, fieldName);
      if (!input) return;
      shown = true;
      placeFieldError(input, msg);
    });
    return shown;
  }

  function showMessageOnEmptyField(form, message, fieldName) {
    if (!message || !fieldName) return false;
    var input = findFormInput(form, fieldName);
    if (!input || (input.value || '').trim()) return false;
    placeFieldError(input, message);
    return true;
  }

  function resetTurnstileIfPresent(form) {
    try {
      if (typeof turnstile === 'undefined' || !turnstile || !turnstile.reset) return;
      var widget = form.querySelector('.cf-turnstile');
      if (!widget) return;
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
    clearInlineErrors(form);

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
          clearInlineErrors(form);
          setFeedback(box, 'success', data.message || 'OK');
          form.reset();
        } else {
          var hasInline = showInlineErrors(form, data.errors);
          if (!hasInline && data.errors && data.errors.email) {
            hasInline = showInlineErrors(form, { email: data.errors.email });
          }
          if (!hasInline) {
            hasInline = showMessageOnEmptyField(
              form,
              data.message || getFirstErrorText(data.errors),
              'email'
            );
          }
          var nonFieldMsg = data.errors && data.errors.__all__ && data.errors.__all__.length
            ? errorMessageFromList(data.errors.__all__)
            : '';
          if (nonFieldMsg || !hasInline) {
            setFeedback(box, 'danger', nonFieldMsg || data.message || getFirstErrorText(data.errors) || 'Xəta baş verdi.');
          } else {
            clearFeedback(box);
          }
        }
        resetTurnstileIfPresent(form);
      })
      .catch(function () {
        setFeedback(box, 'danger', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
        resetTurnstileIfPresent(form);
      });
  }

  document.addEventListener('submit', onSubmit, true);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { initFormFeedbackDismiss(); });
  } else {
    initFormFeedbackDismiss();
  }

  window.initFormFeedbackDismiss = initFormFeedbackDismiss;
})();
