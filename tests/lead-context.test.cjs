const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const script = fs.readFileSync(path.join(__dirname, '../assets/lead-context.js'), 'utf8');
const key = 'dr_lead_context_v1';

function visit({ url = 'https://drmortgageusa.com/blog/guide', referrer = '', storage = new Map(),
  blocked = false, navigator = {}, now = 1791477000000 } = {}) {
  const context = { URL, URLSearchParams, Date: class extends Date { static now() { return now; } },
    document: { referrer }, window: { location: new URL(url), navigator,
      sessionStorage: {
        getItem: name => { if (blocked) throw Error('blocked'); return storage.get(name); },
        setItem: (name, value) => { if (blocked) throw Error('blocked'); storage.set(name, value); },
        removeItem: name => { if (blocked) throw Error('blocked'); storage.delete(name); }
      } } };
  vm.runInNewContext(script, context);
  return { context, storage, get: () => JSON.parse(JSON.stringify(context.window.DrMortgageLeadContext.get())) };
}

test('paid article entry survives internal navigation to the inquiry form', () => {
  const first = visit({ url: 'https://drmortgageusa.com/blog/guide?utm_source=google&utm_medium=cpc&utm_campaign=va&gclid=test-click',
    referrer: 'https://www.google.com/search?q=private-term#fragment' });
  const next = visit({ url: 'https://drmortgageusa.com/va-loans-orlando', storage: first.storage, now: 1791477060000 });
  const result = next.get();
  assert.equal(result.gclid, 'test-click');
  assert.equal(result.utm_campaign, 'va');
  assert.equal(JSON.parse(result.firstTouch).landing_path, '/blog/guide');
  assert.equal(JSON.parse(result.firstTouch).referrer_origin, 'https://www.google.com');
  assert.deepEqual(JSON.parse(result.firstTouch), JSON.parse(result.lastTouch));
  assert.ok(!JSON.stringify(result).includes('private-term'));
});

test('a new campaign changes last touch but preserves first touch', () => {
  const first = visit({ url: 'https://drmortgageusa.com/?utm_source=google&gclid=first' });
  const next = visit({ url: 'https://drmortgageusa.com/contact?utm_source=instagram&utm_campaign=fall', storage: first.storage });
  const result = next.get();
  assert.equal(JSON.parse(result.firstTouch).gclid, 'first');
  assert.equal(JSON.parse(result.lastTouch).utm_source, 'instagram');
  assert.equal(result.gclid, undefined);
});

test('blocked storage keeps page-local campaign context without throwing', () => {
  const result = visit({ blocked: true, url: 'https://drmortgageusa.com/contact?gclid=local-only' }).get();
  assert.equal(result.gclid, 'local-only');
});

for (const navigator of [{ globalPrivacyControl: true }, { doNotTrack: '1' }]) {
  test('browser privacy signal disables and clears the new campaign context: ' + JSON.stringify(navigator), () => {
    const first = visit();
    assert.ok(first.storage.has(key));
    const next = visit({ storage: first.storage, navigator, url: 'https://drmortgageusa.com/?gclid=ignored' });
    assert.deepEqual(next.get(), {});
    assert.equal(first.storage.has(key), false);
  });
}

test('unknown parameters and obvious contact values are not retained', () => {
  const result = visit({ url: 'https://drmortgageusa.com/contact?email=private%40example.test&utm_source=private%40example.test&utm_campaign=valid&gclid=%3Cscript%3E#private',
    referrer: 'https://example.test/private?email=sensitive' }).get();
  assert.equal(result.utm_campaign, 'valid');
  assert.equal(result.utm_source, undefined);
  assert.equal(result.gclid, undefined);
  assert.ok(!JSON.stringify(result).includes('sensitive'));
  assert.ok(!JSON.stringify(result).includes('private'));
});

for (const value of ['{broken', JSON.stringify({ expiresAt: 1, first: { gclid: 'old' }, last: { gclid: 'old' } }),
  JSON.stringify({ expiresAt: 9999999999999, first: {}, last: {} })]) {
  test('malformed, expired, or far-future storage is ignored: ' + value.slice(0, 45), () => {
    const result = visit({ storage: new Map([[key, value]]) }).get();
    assert.equal(result.gclid, undefined);
    assert.equal(JSON.parse(result.firstTouch).landing_path, '/blog/guide');
  });
}

test('stored context is filtered again and private routes produce no attribution', () => {
  const stored = { first: { gclid: 'valid', email: 'private@example.test', landing_path: '/?email=private',
    referrer_origin: 'https://example.test/private?q=secret', timestamp: Infinity },
    last: { utm_source: 'google', password: 'secret' }, expiresAt: 1791477100000 };
  const h = visit({ storage: new Map([[key, JSON.stringify(stored)]]) });
  assert.ok(!JSON.stringify(h.get()).includes('private'));
  assert.ok(!JSON.stringify(h.get()).includes('secret'));
  h.context.window.location = new URL('https://drmortgageusa.com/admin');
  assert.deepEqual(h.get(), {});
});

test('a second script load leaves the existing context helper intact', () => {
  const h = visit();
  const original = h.context.window.DrMortgageLeadContext;
  vm.runInNewContext(script, h.context);
  assert.equal(h.context.window.DrMortgageLeadContext, original);
});
