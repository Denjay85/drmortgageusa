const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

const script = fs.readFileSync(path.join(__dirname, '../assets/lead-forms.js'), 'utf8');

function harness({ result = { success: true, lead_id: 123, event_id: 'server_event' }, ok = true,
  tracking, attribution, fields = {}, fetchImpl, valid = true } = {}) {
  let handler;
  let resets = 0;
  const requests = [];
  const classes = new Set();
  const message = { textContent: '', focus() {}, classList: {
    add(value) { classes.add(value); }, remove(value) { classes.delete(value); }
  } };
  const button = { textContent: 'Request review', disabled: false };
  const form = {
    dataset: { successMessage: 'Your request was received.' },
    addEventListener(type, callback) { if (type === 'submit') handler = callback; },
    reportValidity() { return valid; },
    querySelector(selector) { return selector.startsWith('button') ? button : message; },
    setAttribute() {}, removeAttribute() {}, reset() { resets += 1; }
  };
  const data = new Map(Object.entries({ firstName: 'Local', email: 'local@example.test',
    emailConsent: 'on', source: 'service-page-va-loans-orlando', segment: 'veteran', ...fields }));
  const context = {
    window: { location: { origin: 'http://localhost', pathname: '/va-loans-orlando' },
      crypto: { randomUUID: () => 'test_uuid' }, DrMortgageTracking: tracking,
      DrMortgageLeadContext: attribution },
    document: { readyState: 'complete', title: 'Local service page', querySelectorAll: () => [form] },
    FormData: function () { return data; },
    fetch: async (url, options) => {
      requests.push({ url, options });
      return fetchImpl ? fetchImpl() : { ok, json: async () => result };
    }
  };
  vm.runInNewContext(script, context);
  return { button, message, classes, requests, form, get resets() { return resets; },
    submit: () => handler({ preventDefault() {} }) };
}

test('submits without any analytics, preserves permissions, and uses the confirmed result', async () => {
  const h = harness();
  await h.submit();
  assert.equal(h.requests.length, 1);
  assert.equal(h.requests[0].options.method, 'POST');
  const payload = JSON.parse(h.requests[0].options.body);
  assert.equal(payload.emailConsent, true);
  assert.equal(payload.callConsent, false);
  assert.equal(payload.smsConsent, false);
  assert.equal(payload.eventId, 'service_lead_test_uuid');
  assert.equal(h.resets, 1);
  assert.equal(h.message.textContent, 'Your request was received.');
});

test('analytics exceptions cannot prevent submission or turn a saved lead into an error', async () => {
  const h = harness({ tracking: { getOrCreateFbp() { throw Error('blocked'); },
    trackLeadSubmit() { throw Error('blocked'); } } });
  await h.submit();
  assert.equal(h.resets, 1);
  assert.ok(h.classes.has('is-success'));
});

test('a confirmed lead produces exactly one tracking event with the server event ID', async () => {
  const events = [];
  const h = harness({ tracking: { trackLeadSubmit: event => events.push(event) } });
  await h.submit();
  assert.equal(events.length, 1);
  assert.equal(events[0].eventId, 'server_event');
});

test('preview success does not emit a lead conversion', async () => {
  const events = [];
  const h = harness({ result: { success: true, preview: true, lead_id: null },
    tracking: { trackLeadSubmit: event => events.push(event) } });
  await h.submit();
  assert.equal(events.length, 0);
  assert.match(h.message.textContent, /No lead was saved or sent/);
});

for (const [name, options] of [
  ['HTTP failure', { ok: false }],
  ['false success response', { result: { success: false } }],
  ['missing saved lead ID', { result: { success: true } }],
  ['string preview flag without saved lead ID', { result: { success: true, preview: 'false' } }],
  ['invalid JSON', { fetchImpl: async () => ({ ok: true, json() { throw Error('HTML'); } }) }],
  ['network failure', { fetchImpl: async () => { throw Error('offline'); } }]
]) {
  test(name + ' preserves entries and never emits a lead conversion', async () => {
    const events = [];
    const h = harness({ ...options, tracking: { trackLeadSubmit: event => events.push(event) } });
    await h.submit();
    assert.equal(events.length, 0);
    assert.equal(h.resets, 0);
    assert.equal(h.button.disabled, false);
    assert.match(h.message.textContent, /could not confirm delivery/);
  });
}

test('ignores repeat submits while a request is pending', async () => {
  let resolve;
  const h = harness({ fetchImpl: () => new Promise(done => { resolve = done; }) });
  const first = h.submit();
  await h.submit();
  assert.equal(h.requests.length, 1);
  assert.equal(h.button.disabled, true);
  resolve({ ok: true, json: async () => ({ success: true, lead_id: 123 }) });
  await first;
  assert.equal(h.button.disabled, false);
});

test('call or SMS permission without a phone does not send', async () => {
  const h = harness({ fields: { smsConsent: 'on' } });
  await h.submit();
  assert.equal(h.requests.length, 0);
  assert.match(h.message.textContent, /add a phone number/);
});

test('invalid form does not send', async () => {
  const h = harness({ valid: false });
  await h.submit();
  assert.equal(h.requests.length, 0);
});

test('adds campaign context without overriding form identity', async () => {
  const h = harness({ attribution: { get: () => ({ utm_source: 'google', gclid: 'test-click',
    source: 'untrusted', email: 'wrong@example.test' }) } });
  await h.submit();
  const body = JSON.parse(h.requests[0].options.body);
  assert.equal(body.utm_source, 'google');
  assert.equal(body.gclid, 'test-click');
  assert.equal(body.email, 'local@example.test');
  assert.equal(body.source, 'service-page-va-loans-orlando');
});

test('blocked attribution is optional', async () => {
  const h = harness({ attribution: { get() { throw Error('blocked'); } } });
  await h.submit();
  assert.equal(h.resets, 1);
});
