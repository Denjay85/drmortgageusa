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
for (const key of ['DATABASE_URL', 'ZAPIER_WEBHOOK_URL', 'META_CONVERSIONS_API_TOKEN', 'MANYCHAT_API_KEY']) delete env[key];
function renderScript(overrides = {}) { return execFileSync(process.env.TEST_PYTHON || 'python3', ['-c',
  'import contextlib, io\nwith contextlib.redirect_stdout(io.StringIO()):\n import app\nprint(app.app.test_client().get("/site-tracking.js").get_data(as_text=True))'],
{ cwd: path.join(__dirname, '..'), env: { ...env, ...overrides }, encoding: 'utf8' }); }
const script = renderScript();
const personalScript = renderScript({ GA_MEASUREMENT_ID: 'G-WP0F27FV60', GOOGLE_ADS_ID: '', GOOGLE_ADS_APPLY_CONVERSION_LABEL: '', GOOGLE_ADS_PHONE_CONVERSION_LABEL: '', GOOGLE_ADS_LEAD_FORM_CONVERSION_LABEL: '' });

function harness({ result = { success: true, lead_id: 42, event_id: 'server-id' }, ok = true,
  brokenCookies = false, trackingThrows = false, fetchImpl, trackingScript = script,
  pageUrl = 'https://drmortgageusa.com/contact?utm_source=google&email=private%40example.test',
  referrer = '' } = {}) {
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
  ]); }, document: { title: 'Local test', referrer, readyState: 'complete', body: { dataset: {} },
    addEventListener: (type, callback) => { if (type === 'click') clickHandler = callback; },
    querySelectorAll: selector => selector === 'form[data-lead-form]' ? [form] : [],
    createElement() { throw Error('No network allowed in tests'); } },
  window: { location: new URL(pageUrl),
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
  vm.runInNewContext(trackingScript, context);
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

test('repeated handling of one saved lead emits once per destination; distinct leads still count', () => {
  const h = harness();
  h.tracking.trackLeadSubmit({ eventId: 'saved-one' });
  h.tracking.trackLeadSubmit({ eventId: 'saved-one' });
  h.tracking.trackLeadSubmit({ eventId: 'saved-two' });
  assert.equal(h.google.filter(args => args[1] === 'generate_lead').length, 2);
  assert.equal(h.google.filter(args => args[1] === 'conversion').length, 2);
  assert.equal(h.meta.filter(args => args[1] === 'Lead').length, 2);
  assert.equal(h.context.window.dataLayer.filter(item => item.event === 'dr_lead_form_submit').length, 2);
});

test('a failed Meta handler cannot suppress Google lead measurement or duplicate successful destinations', () => {
  const h = harness();
  const fbq = h.context.window.fbq;
  h.context.window.fbq = () => { throw Error('Meta blocked'); };
  assert.doesNotThrow(() => h.tracking.trackLeadSubmit({ eventId: 'saved-retry' }));
  assert.equal(h.google.filter(args => args[1] === 'conversion').length, 1);
  h.context.window.fbq = fbq;
  h.tracking.trackLeadSubmit({ eventId: 'saved-retry' });
  assert.equal(h.meta.filter(args => args[1] === 'Lead').length, 1);
  assert.equal(h.google.filter(args => args[1] === 'generate_lead').length, 1);
  assert.equal(h.google.filter(args => args[1] === 'conversion').length, 1);
});

test('a temporarily unavailable Google tag can be retried without replaying other destinations', () => {
  const h = harness();
  const gtag = h.context.window.gtag;
  delete h.context.window.gtag;
  h.tracking.trackLeadSubmit({ eventId: 'saved-late-tag' });
  h.context.window.gtag = gtag;
  h.tracking.trackLeadSubmit({ eventId: 'saved-late-tag' });
  h.tracking.trackLeadSubmit({ eventId: 'saved-late-tag' });
  assert.equal(h.google.filter(args => args[1] === 'generate_lead').length, 1);
  assert.equal(h.google.filter(args => args[1] === 'conversion').length, 1);
  assert.equal(h.meta.filter(args => args[1] === 'Lead').length, 1);
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


test('personal stream excludes borrower/query data and keeps paid click attribution', () => {
  const h = harness({ trackingScript: personalScript,
    pageUrl: 'https://drmortgageusa.com/contact?gclid=Opaque_Google-123&gbraid=Opaque_Braid-456&wbraid=Opaque_Wbraid-789&utm_source=google&utm_medium=cpc&utm_campaign=private%40example.test&email=private%40example.test&phone=5551234567#private',
    referrer: 'https://www.google.com/search?q=private%40example.test#private' });
  const config = h.google.find(args => args[0] === 'config' && args[1] === 'G-WP0F27FV60')[2];
  assert.equal(config.page_location, 'https://drmortgageusa.com/contact?gclid=Opaque_Google-123&gbraid=Opaque_Braid-456&wbraid=Opaque_Wbraid-789');
  assert.equal(config.page_referrer, 'https://www.google.com/');
  assert.equal(config.campaign_source, 'google');
  assert.equal(config.campaign_medium, 'cpc');
  assert.equal(config.campaign_name, '');
  h.tracking.trackLeadSubmit({ eventId: 'receipt', source: 'redesign-contact', email: 'private@example.test', message: 'private message' });
  h.tracking.trackLeadSubmit({ eventId: 'receipt', source: 'redesign-contact' });
  h.tracking.trackApplyClick({ href: 'https://example.test/?email=private@example.test' });
  h.tracking.trackPhoneClick({ href: 'tel:5551234567' });
  assert.equal(h.google.filter(args => args[1] === 'generate_lead').length, 1);
  assert.ok(h.google.filter(args => args[0] === 'config').every(args => args[1] === 'G-WP0F27FV60'));
  assert.ok(!h.google.some(args => args[1] === 'conversion'));
  assert.ok(!/AW-|private|5551234567/.test(JSON.stringify(h.google)));
});

test('malformed attribution and referrers are omitted from Analytics', () => {
  const h = harness({ trackingScript: personalScript,
    pageUrl: 'https://drmortgageusa.com/contact?gclid=private%40example.test&utm_source=private%40example.test&utm_medium=private',
    referrer: 'javascript:private' });
  const config = h.google.find(args => args[0] === 'config')[2];
  assert.equal(config.page_location, 'https://drmortgageusa.com/contact');
  assert.equal(config.page_referrer, '');
  assert.equal(config.campaign_source, '');
  assert.equal(config.campaign_medium, '');
});

for (const [name, result, ok, expected] of [
  ['saved', { success: true, lead_id: 42, event_id: 'server-id' }, true, 1],
  ['HTTP failure', { success: true, lead_id: 42 }, false, 0],
  ['rejected', { success: false }, true, 0],
  ['missing receipt', { success: true }, true, 0],
  ['preview', { success: true, preview: true }, true, 0],
]) {
  test('personal GA4-only mode preserves ' + name + ' submission behavior', async () => {
    const h = harness({ trackingScript: personalScript, result, ok });
    await h.submit();
    assert.equal(h.google.filter(args => args[1] === 'generate_lead').length, expected);
    assert.ok(!h.google.some(args => args[1] === 'conversion'));
  });
}
