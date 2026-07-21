import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}-${path}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request(`http://localhost${path}`, {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the DR. Mortgage USA homepage and key resource paths", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /DR\. Mortgage USA/);
  assert.doesNotMatch(html, /Dr\. Mortgage USA/);
  assert.match(html, /Hundreds/);
  assert.doesNotMatch(html, /600\+/);
  assert.match(html, /make the mortgage make sense before you make a move/);
  assert.match(html, /class="brand-mark"/);
  assert.match(html, /href="\/blog"/);
  assert.match(html, /href="\/dpa"/);
  assert.match(html, /href="\/dpa" class="nav-dpa">DPA programs/);
  assert.match(html, /href="\/heloc-calculator"/);
  assert.match(html, /Today&#x27;s mortgage rate ranges/);
  assert.match(html, /A quick market snapshot/);
  assert.match(html, /Conventional 15-year/);
  assert.match(html, /Jumbo 30-year/);
  assert.match(html, /Create Rate Watch/);
  assert.match(html, /id="rates"/);
  assert.ok(
    html.indexOf('class="hero-rates-panel') > html.indexOf('class="hero-portrait"'),
    "the rate strip should follow the main hero row in document flow",
  );
  assert.match(html, /Questions before the call/);
  assert.match(html, /Can I explore my mortgage options without a credit check/);
  assert.match(html, /href="\/faq"/);
  assert.match(html, /Choose your conversation/);
  assert.match(html, /Active path/);
  assert.match(html, /start with the payment you can live with/i);
  assert.match(html, /First home, next home, or relocation/);
  assert.match(html, /current home and timing/i);
  assert.match(html, /Try your numbers/);
  assert.match(html, /Put in the numbers you know/);
  assert.match(html, /Open the secure application/);
  assert.match(html, /home1st\.my1003app\.com\/2018381\/register/);
  assert.match(html, /aria-label="Home or property value"/);
  assert.match(html, /aria-label="Interest rate assumption"/);
  assert.doesNotMatch(html, /type="range"/);
  assert.doesNotMatch(html, /class="flag-wave-sheen"/);
  assert.match(html, /class="client-motion-wall"/);
  assert.equal((html.match(/class="client-motion-tile\b/g) ?? []).length, 16);
  assert.doesNotMatch(html, /Closing\s+\d+/i);
  assert.match(html, /Start simple\. Build from there/);
  assert.match(html, /class="premium-process"/);
  if (process.env.NEXT_PUBLIC_INDEXABLE === "true") {
    assert.match(html, /name="robots" content="index, follow"/);
  } else {
    assert.match(html, /name="robots" content="noindex, nofollow"/);
  }
  assert.match(html, /rel="canonical" href="https:\/\/drmortgageusa\.com\/"/);
  assert.match(html, /property="og:title" content="DR\. Mortgage USA"/);
  assert.match(html, /property="og:url" content="https:\/\/drmortgageusa\.com"/);
  assert.match(html, /property="og:image" content="https:\/\/drmortgageusa\.com\/dennis-ross-headshot\.png"/);
  assert.match(html, /property="og:image:width" content="1000"/);
  assert.match(html, /property="og:image:height" content="1000"/);
  assert.match(html, /name="twitter:image" content="https:\/\/drmortgageusa\.com\/dennis-ross-headshot\.png"/);
  const organizationMatch = html.match(/<script type="application\/ld\+json">(.*?)<\/script>/);
  assert.ok(organizationMatch, "homepage organization structured data should render");
  const organization = JSON.parse(organizationMatch[1]);
  assert.equal(organization["@type"], "Organization");
  assert.equal(organization.name, "DR. Mortgage USA");
  assert.equal(organization.telephone, "+1-850-346-8514");
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);
});

test("renders the blog, DPA, and HELOC destinations", async () => {
  const cases = [
    ["/blog", /Search the library/, /Publishing since February 2026/],
    ["/dpa", /major assistance programs are pricing today/, /Have Dennis review my options/],
    ["/heloc-calculator", /How much equity could you use/, /Modeled available line/],
  ];

  for (const [path, heading, capability] of cases) {
    const response = await render(path);
    assert.equal(response.status, 200, path);
    const html = await response.text();
    assert.match(html, heading, path);
    assert.match(html, capability, path);
    const canonicalPath = path === "/dpa" ? "/dpa" : path;
    assert.match(
      html,
      new RegExp(`rel="canonical" href="https://drmortgageusa\\.com${canonicalPath}"`),
      path,
    );
  }

  const blogResponse = await render("/blog");
  const blogHtml = await blogResponse.text();
  assert.equal((blogHtml.match(/class="blog-card"/g) ?? []).length, 48);
  assert.match(blogHtml, /VA Loan Guide for Florida Veterans/);

  const dpaResponse = await render("/dpa");
  const dpaHtml = await dpaResponse.text();
  assert.match(dpaHtml, /Standard Bond/);
  assert.match(dpaHtml, /Hometown Heroes Bond/);
  assert.match(dpaHtml, /Connected to the official source|Last verified program snapshot/);
  assert.match(dpaHtml, /Program lock rates are not ordinary retail rate quotes/);
});

test("renders the complete ten-calculator mortgage studio", async () => {
  const response = await render("/tools");
  assert.equal(response.status, 200);
  const html = await response.text();

  for (const label of [
    "Purchase",
    "Affordability",
    "FHA Purchase",
    "Refinance",
    "Rent vs. Buy",
    "VA Purchase",
    "VA Refinance",
    "DSCR",
    "Fix &amp; Flip",
    "HELOC",
  ]) {
    assert.match(html, new RegExp(label));
  }

  assert.match(html, /What could the full monthly payment look like/);
  assert.match(html, /HUD FHA mortgage-insurance structure/);
  assert.match(html, /VA funding-fee chart/);
});

test("renders the About portrait in a proportion-controlled frame", async () => {
  const response = await render("/about");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /class="about-photo-frame"/);
  assert.match(html, /class="about-portrait-caption"/);
  assert.doesNotMatch(html, /class="flag-wave-sheen"/);
  assert.match(html, /Dennis Ross, DR\. Mortgage USA/);
  const personMatch = html.match(/<script type="application\/ld\+json">(.*?)<\/script>/);
  assert.ok(personMatch, "about page person structured data should render");
  const person = JSON.parse(personMatch[1]);
  assert.equal(person["@type"], "Person");
  assert.equal(person.name, "Dennis Ross");
  assert.equal(person.identifier.value, "2018381");
});

test("keeps purchase-only questions out of refinance and equity quiz branches", async () => {
  const source = await readFile(new URL("../app/get-started/PathFinder.tsx", import.meta.url), "utf8");
  const refinanceBranch = source.slice(source.indexOf("const refinanceSteps"), source.indexOf("const equitySteps"));
  const equityBranch = source.slice(source.indexOf("const equitySteps"), source.indexOf("const researchSteps"));

  assert.match(refinanceBranch, /What do you want the refinance to accomplish/);
  assert.match(refinanceBranch, /What type of mortgage do you have now/);
  assert.doesNotMatch(refinanceBranch, /First-time buyer|My first home|purchase-price/i);
  assert.match(equityBranch, /What would you like to use the equity for/);
  assert.doesNotMatch(equityBranch, /First-time buyer|My first home|purchase-price/i);
});

test("renders a searchable, categorized mortgage FAQ", async () => {
  const response = await render("/faq");
  assert.equal(response.status, 200);
  const html = await response.text();

  assert.match(html, /Search mortgage questions/);
  assert.match(html, /Payment &amp; cash/);
  assert.match(html, /Does FHA mortgage insurance always remain for the life of the loan/);
  assert.match(html, /Does a VA appraisal automatically make the loan close more slowly/);
  assert.match(html, /If my mortgage rate is fixed, can my total monthly payment still change/);
  assert.match(html, /CFPB home-loan resources/);
  assert.match(html, /Ask Dennis/);
});

test("renders every public route without em dashes", async () => {
  const forbiddenCharacter = String.fromCodePoint(0x2014);
  const forbiddenEntities = [
    "&" + "mdash;",
    "&" + "#8212;",
    "&" + "#x2014;",
  ];
  const routes = [
    "/",
    "/about",
    "/blog",
    "/contact",
    "/down-payment-assistance",
    "/dpa",
    "/faq",
    "/get-started",
    "/heloc-calculator",
    "/legal",
    "/mortgage-options",
    "/resources",
    "/tools",
  ];

  for (const path of routes) {
    const response = await render(path);
    assert.equal(response.status, 200, path);
    const html = await response.text();
    assert.ok(!html.includes(forbiddenCharacter), path);
    for (const entity of forbiddenEntities) {
      assert.ok(!html.toLowerCase().includes(entity.toLowerCase()), path);
    }
  }
});
