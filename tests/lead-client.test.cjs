const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const ts = require('../site/node_modules/typescript');
const source = fs.readFileSync(path.join(__dirname, '../site/app/lead-client.ts'), 'utf8');
const script = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS,
  target: ts.ScriptTarget.ES2022, strict: true } }).outputText;

function harness({ result = { success: true, lead_id: 42, event_id: 'saved-id' }, ok = true, status = 200,
  tracking, attribution, rejectFetch = false, invalidJson = false } = {}) {
  const requests = [];
  const context = { exports: {}, window: {
    location: new URL('https://drmortgageusa.com/contact?email=private%40example.test#fragment'),
    DrMortgageTracking: tracking, DrMortgageLeadContext: attribution
  }, fetch: async (url, options) => {
    requests.push({ url, options });
    if (rejectFetch) throw Error('offline');
    return { ok, status, json: async () => { if (invalidJson) throw Error('HTML'); return result; } };
  } };
  vm.runInNewContext(script, context);
  return { requests, submit: (payload = {}) => context.exports.submitLead({ firstName: 'Local', email: 'local@example.test',
    source: 'redesign-contact', segment: 'contact', ...payload }) };
}

test('confirmed main-site lead sends one event with the saved event ID and no full query URL', async () => {
  const events = [];
  const h = harness({ tracking: { trackLeadSubmit: value => events.push(value) },
    attribution: { get: () => ({ utm_source: 'google', gclid: 'ad-click', email: 'wrong@example.test' }) } });
  await h.submit();
  assert.equal(events.length, 1);
  assert.equal(events[0].eventId, 'saved-id');
  const body = JSON.parse(h.requests[0].options.body);
  assert.equal(body.utm_source, 'google');
  assert.equal(body.gclid, 'ad-click');
  assert.equal(body.email, 'local@example.test');
  assert.equal(body.pageUrl, 'https://drmortgageusa.com/contact');
  assert.equal(body.referrer, undefined);
});

test('forms submit when analytics and attribution are absent', async () => {
  const result = await harness().submit();
  assert.equal(result.lead_id, 42);
});

test('blocked optional helpers and post-save tracking cannot break a saved form', async () => {
  const blocked = () => { throw Error('blocked'); };
  const h = harness({ tracking: { createEventId: blocked, getOrCreateFbp: blocked,
    getOrCreateFbc: blocked, trackLeadSubmit: blocked }, attribution: { get: blocked } });
  assert.equal((await h.submit()).success, true);
  const body = JSON.parse(h.requests[0].options.body);
  assert.equal(body.fbp, '');
  assert.equal(body.fbc, '');
});

test('preview success never sends a conversion', async () => {
  const events = [];
  const h = harness({ result: { success: true, preview: true, lead_id: null },
    tracking: { trackLeadSubmit: value => events.push(value) } });
  assert.equal((await h.submit()).preview, true);
  assert.equal(events.length, 0);
});

for (const [name, options] of [
  ['HTTP failure', { ok: false, status: 500 }],
  ['false success', { result: { success: false } }],
  ['missing ID', { result: { success: true } }],
  ['string preview', { result: { success: true, preview: 'false' } }],
  ['invalid JSON', { invalidJson: true }],
  ['network failure', { rejectFetch: true }],
  ['null JSON', { result: null }]
]) {
  test(name + ' never sends a lead event', async () => {
    const events = [];
    const h = harness({ ...options, tracking: { trackLeadSubmit: value => events.push(value) } });
    await assert.rejects(h.submit());
    assert.equal(events.length, 0);
  });
}

test('server validation is presented without leaking raw server errors', async () => {
  await assert.rejects(harness({ ok: false, status: 400,
    result: { success: false, errors: ['valid email is required'] } }).submit(), /valid email/);
  await assert.rejects(harness({ ok: false, status: 500,
    result: { error: 'private server detail', errors: ['private server detail'] } }).submit(), /could not confirm delivery/);
});

test('optional phone permissions require a phone without sending an incomplete request', async () => {
  const h = harness();
  await assert.rejects(h.submit({ smsConsent: true, phone: '' }), /add a phone number/);
  assert.equal(h.requests.length, 0);
});
