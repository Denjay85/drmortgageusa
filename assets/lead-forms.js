(function () {
  'use strict';

  function trackingValue(name) {
    try {
      var tracking = window.DrMortgageTracking;
      return tracking && tracking[name] ? tracking[name]() : '';
    } catch (_) {
      return '';
    }
  }

  function bindForms() {
    document.querySelectorAll('form[data-lead-handler="standalone"]').forEach(function (form) {
      if (form.dataset.drLeadBound) return;
      form.dataset.drLeadBound = '1';
      var pending = false;

      form.addEventListener('submit', async function (event) {
        event.preventDefault();
        if (pending || !form.reportValidity()) return;
        var fields = new FormData(form);
        var button = form.querySelector('button[type="submit"]');
        var message = form.querySelector('[data-form-message]');
        var originalText = button.textContent;
        var attribution = {};
        try { attribution = window.DrMortgageLeadContext ? window.DrMortgageLeadContext.get() : {}; } catch (_) { /* Optional. */ }
        var payload = Object.assign({}, attribution, Object.fromEntries(fields.entries()));
        ['emailConsent', 'callConsent', 'smsConsent'].forEach(function (name) {
          payload[name] = fields.get(name) === 'on';
        });
        if ((payload.callConsent || payload.smsConsent) && !String(payload.phone || '').trim()) {
          message.textContent = 'Please add a phone number for calls or texts, or leave those permissions unchecked.';
          message.classList.remove('is-success');
          message.focus();
          return;
        }
        payload.eventId = 'service_lead_' + (window.crypto && window.crypto.randomUUID
          ? window.crypto.randomUUID() : Date.now() + '_' + Math.random().toString(36).slice(2));
        payload.fbp = trackingValue('getOrCreateFbp');
        payload.fbc = trackingValue('getOrCreateFbc');
        payload.pageUrl = window.location.origin + window.location.pathname;

        pending = true;
        button.disabled = true;
        button.textContent = 'Sending...';
        form.setAttribute('aria-busy', 'true');
        message.textContent = 'Sending your request...';
        message.classList.remove('is-success');
        try {
          var response = await fetch('/api/quiz-submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          var result = await response.json();
          if (!response.ok || result.success !== true || (result.preview !== true && !result.lead_id)) {
            throw new Error('Receipt was not confirmed');
          }
          // Analytics must never change whether a successfully received form looks successful.
          if (result.preview !== true) {
            try {
              var tracking = window.DrMortgageTracking;
              if (tracking && tracking.trackLeadSubmit) tracking.trackLeadSubmit({
                eventId: result.event_id || payload.eventId,
                content_name: payload.segment || document.title,
                content_category: payload.source,
                source: payload.source
              });
            } catch (_) { /* The lead was already received. */ }
          }
          form.reset();
          message.textContent = result.preview === true
            ? 'Preview test complete. No lead was saved or sent.'
            : form.dataset.successMessage;
          message.classList.add('is-success');
        } catch (_) {
          message.textContent = 'We could not confirm delivery. Your entries are still here. Please call 850-346-8514 for help before sending again.';
        } finally {
          pending = false;
          button.disabled = false;
          button.textContent = originalText;
          form.removeAttribute('aria-busy');
          message.focus();
        }
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindForms, { once: true });
  } else {
    bindForms();
  }
})();
