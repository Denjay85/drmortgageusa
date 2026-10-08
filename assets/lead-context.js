(function () {
  'use strict';
  if (window.DrMortgageLeadContext) return;
  var key = 'dr_lead_context_v1';
  var lifetime = 30 * 60 * 1000;
  var names = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'gclid', 'gbraid', 'wbraid'];
  var context = null;

  function optedOut() {
    return window.navigator && (window.navigator.globalPrivacyControl === true || window.navigator.doNotTrack === '1');
  }

  function clean(value, limit) {
    if (typeof value !== 'string' || value.length > limit || /[@<>\x00-\x1f]|%40|%3c|%3e|%0[ad]/i.test(value)) return '';
    return value.trim();
  }

  function cleanTouch(value) {
    if (!value || typeof value !== 'object') return null;
    var touch = {};
    names.forEach(function (name) {
      var item = clean(value[name], name.indexOf('utm_') === 0 ? 256 : 512);
      if (item) touch[name] = item;
    });
    var path = clean(value.landing_path, 512);
    if (path && path[0] === '/' && path.indexOf('?') === -1 && path.indexOf('#') === -1) touch.landing_path = path;
    try {
      var referrer = new URL(value.referrer_origin);
      if (/^https?:$/.test(referrer.protocol)) touch.referrer_origin = referrer.origin;
    } catch (_) { /* No usable referring origin. */ }
    if (typeof value.timestamp === 'number' && Number.isFinite(value.timestamp) && value.timestamp > 0 && value.timestamp <= Date.now() + 60000) touch.timestamp = value.timestamp;
    return touch;
  }

  function clear() {
    context = null;
    try { window.sessionStorage.removeItem(key); } catch (_) { /* Storage is optional. */ }
  }

  function capture() {
    if (optedOut()) { clear(); return; }
    var path = window.location.pathname;
    if (/^\/(admin|api|request-review|request-received)(\/|$)/.test(path)) { context = null; return; }
    var now = Date.now();
    if (!context) {
      try {
        var saved = JSON.parse(window.sessionStorage.getItem(key) || 'null');
        if (saved && saved.expiresAt > now && saved.expiresAt <= now + lifetime) {
          context = { first: cleanTouch(saved.first), last: cleanTouch(saved.last), expiresAt: saved.expiresAt };
          if (!context.first || !context.last) context = null;
        }
      } catch (_) { /* Unavailable or malformed storage must not affect a lead form. */ }
    }
    if (context && context.expiresAt <= now) context = null;
    var params = new URLSearchParams(window.location.search);
    var touch = { landing_path: path, timestamp: now };
    names.forEach(function (name) { touch[name] = params.get(name) || ''; });
    try {
      var referrer = new URL(document.referrer);
      if (referrer.origin !== window.location.origin) touch.referrer_origin = referrer.origin;
    } catch (_) { /* Direct visit. */ }
    touch = cleanTouch(touch);
    if (!context) context = { first: touch, last: touch, expiresAt: now + lifetime };
    else if (names.some(function (name) { return touch[name] && touch[name] !== context.last[name]; })) context.last = touch;
    context.expiresAt = now + lifetime;
    try { window.sessionStorage.setItem(key, JSON.stringify(context)); } catch (_) { /* Keep page-local context. */ }
  }

  function get() {
    capture();
    if (optedOut() || !context) return {};
    var result = {};
    names.forEach(function (name) { if (context.last[name]) result[name] = context.last[name]; });
    result.firstTouch = JSON.stringify(context.first);
    result.lastTouch = JSON.stringify(context.last);
    return result;
  }

  window.DrMortgageLeadContext = { get: get };
  capture();
})();
