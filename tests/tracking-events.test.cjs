const assert = require('node:assert/strict');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const { execFileSync } = require('node:child_process');

// Render the actual Flask response, never reach a production database or ad network.
const env = { ...process.env, ENABLE_RATE_UPDATER: '0', PREVIEW_MODE: 'false', IS_PULL_REQUEST: 'false',
  PYTHONDONTWRITEBYTECODE: '1', GA_MEASUREMENT_ID: 'G-LOCALTEST', GTM_CONTAINER_ID: '',
  GOOGLE_ADS_ID: 'AW-LOCALTEST', GOOGLE_ADS_APPLY_CONVERSION_LABEL: 'apply-label',
  GOOGLE_ADS_PHONE_CONVERSION_LABEL: 'phone-label', GOOGLE_ADS_LEAD_FORM_CONVERSION_LABEL: 'lead-label' };
delete env.DATABASE_URL;
const script = execFileSync(process.env.TEST_PYTHON || 'python3', ['-c',
  'import contextlib, io\nwith contextlib.redirect_stdout(io.StringIO()):\n import app\nprint(app.app.test_client().get("/site-tracking.js").get_data(as_text=True))'],
{ cwd: path.join(__dirname, '..'), env, encoding: 'utf8' });

function harness({ result = { success: true, lead_id: 42, event_id: 'server-id' }, ok = true,
  brokenCookies = false, trackingThrows = false, fetchImpl } = {}) {
  const google = [], meta = [], requests = [];
  let submitHandler, clickHandler, resets = 0;
  const message = { textContent: '', classList: { add() {}, remove() {} } };
  const button = { disabled: false, textContent: 'Send' };
  const form = { dataset: {}, reportValidity: () => true,
    addEventListener: (type, callback) => { submitHandler = callback; },
    querySelector: selector => selector.startsWith('button') ? button : message,
    reset: () => { resets += 1; } };
  const context = { URL, URLSearchParams, FormData: function () { return new Map([
    ['firstName', 'Local'], ['email', 'local@example.test'], ['source', 'legacy-form'], ['emailConsent', 'on']
  ]); }, document: { title: 'Local test', referrer: '', readyState: 'complete', body: { dataset: {} },
    addEventListener: (type, callback) => { if (type === 'click') clickHandler = callback; },
    querySelectorAll: selector => selector === 'form[data-lead-form]' ? [form] : [],
    createElement() { throw Error('No network allowed in tests'); } },
  window: { location: new URL('https://drmortgageusa.com/contact?utm_source=google&email=private%40example.test'),
    navigator: {}, sessionStorage: { getItem: () => null, setItem() {}, removeItem() {} },
    gtag: (...args) => { if (trackingThrows) throw Error('blocked'); google.push(args); },
    fbq: (...args) => { if (trackingThrows) throw Error('blocked'); meta.push(args); },
    DR_TRACKING_OPTIONS: { disableMetaInit: true, disableIntentViewTracking: true } },
  fetch: async (url, options) => {
    requests.push({ url, options });
    return fetchImpl ? fetchImpl() : { ok, json: async () => result };
  } };
  Object.defineProperty(context.document, 'cookie', { get() { if (brokenCookies) throw Error('blocked'); return ''; },
    set() { if (brokenCookies) throw Error('blocked'); } });
  vm.runInNewContext(script, context);
  return { google, meta, requests, context, button, message, form,
    get resets() { return resets; }, tracking: context.window.DrMortgageTracking,
    submit: async () => { submitHandler({ preventDefault() {} }); await new Promise(setImmediate); },
    click: event => clickHandler(event) };
}

test('application clicks are engagement, not a saved lead or completed registration', () => {
  const h = harness();
  h.tracking.trackApplyClick({ eventId: 'apply-intent', href: 'https://my1003app.com/example' });
  assert.ok(h.google.some(args => args[1] === 'application_opened'));
  assert.ok(!h.google.some(args => args[1] === 'generate_lead'));
  assert.ok(h.meta.some(args => args[0] === 'trackCustom' && args[1] === 'ApplicationOpened'));
  assert.ok(!h.meta.some(args => ['Lead', 'CompleteRegistration'].includes(args[1])));
  assert.ok(h.google.some(args => args[1] === 'conversion' && args[2].send_to === 'AW-LOCALTEST/apply-label'));
});

test('phone clicks are distinct from connected calls and preserve the existing intent destination', () => {
  const h = harness();
  h.tracking.trackPhoneClick({ eventId: 'phone-intent', href: 'tel:+18503468514' });
  assert.ok(h.google.some(args => args[1] === 'phone_click'));
  assert.ok(!h.google.some(args => args[1] === 'generate_lead'));
  assert.ok(h.meta.some(args => args[0] === 'trackCustom' && args[1] === 'PhoneLinkClick'));
  assert.ok(h.google.some(args => args[1] === 'conversion' && args[2].send_to === 'AW-LOCALTEST/phone-label'));
});

test('delegated tracking covers links rendered after initialization without counting regular navigation', () => {
  const h = harness();
  const link = { href: 'https://home1st.my1003app.com/2018381/register', dataset: {},
    matches: selector => selector.includes('my1003app.com') };
  h.click({ target: { closest: () => link } });
  h.click({ target: { closest: () => ({ matches: () => false }) } });
  assert.equal(h.google.filter(args => args[1] === 'application_opened').length, 1);
  assert.equal(h.google.filter(args => args[1] === 'generate_lead').length, 0);
});

test('only lead submissions use the lead destination and no query-bearing page URL', () => {
  const h = harness();
  h.tracking.trackLeadSubmit({ eventId: 'saved-id', source: 'local-form' });
  assert.equal(h.google.filter(args => args[1] === 'generate_lead').length, 1);
  assert.equal(h.meta.filter(args => args[0] === 'track' && args[1] === 'Lead').length, 1);
  assert.ok(h.google.some(args => args[1] === 'conversion' && args[2].send_to === 'AW-LOCALTEST/lead-label'
    && args[2].transaction_id === 'saved-id'));
  assert.equal(h.context.window.dataLayer[0].page_location, 'https://drmortgageusa.com/contact');
});

test('legacy shared forms also require a saved lead before conversion', async () => {
  const h = harness();
  await h.submit();
  assert.equal(h.resets, 1);
  assert.equal(h.google.filter(args => args[1] === 'generate_lead').length, 1);
  assert.equal(JSON.parse(h.requests[0].options.body).utm_source, 'google');
  assert.equal(h.form.dataset.drLeadPending, undefined);
});

for (const [name, options] of [
  ['HTTP failure', { ok: false }], ['false success', { result: { success: false } }],
  ['missing saved lead', { result: { success: true } }],
  ['string preview flag', { result: { success: true, preview: 'false' } }],
  ['invalid JSON', { fetchImpl: async () => ({ ok: true, json: async () => { throw Error('HTML'); } }) }]
]) {
  test('legacy form ' + name + ' does not clear or count', async () => {
    const h = harness(options);
    await h.submit();
    assert.equal(h.resets, 0);
    assert.equal(h.google.filter(args => args[1] === 'generate_lead').length, 0);
    assert.equal(h.button.disabled, false);
  });
}

test('legacy preview suppresses conversion and states that nothing was sent', async () => {
  const h = harness({ result: { success: true, preview: true } });
  await h.submit();
  assert.equal(h.resets, 1);
  assert.equal(h.google.filter(args => args[1] === 'generate_lead').length, 0);
  assert.match(h.message.textContent, /No lead was saved or sent/);
});

test('legacy forms still work with blocked cookie and tracking APIs', async () => {
  const h = harness({ brokenCookies: true, trackingThrows: true });
  await h.submit();
  assert.equal(h.requests.length, 1);
  assert.equal(h.resets, 1);
});

test('legacy forms ignore repeated submissions while waiting for receipt', async () => {
  let resolve;
  const h = harness({ fetchImpl: () => new Promise(done => { resolve = done; }) });
  await h.submit();
  await h.submit();
  assert.equal(h.requests.length, 1);
  resolve({ ok: true, json: async () => ({ success: true, lead_id: 42 }) });
  await new Promise(setImmediate);
  assert.equal(h.resets, 1);
});
