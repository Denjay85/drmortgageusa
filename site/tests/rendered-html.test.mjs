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
  assert.match(html, /Today&#x27;s national mortgage rate index/);
  assert.match(html, /Checking Mortgage News Daily/);
  assert.match(html, /Verifying today&#x27;s index/);
  assert.doesNotMatch(html, /USDA 30-year/);
  assert.doesNotMatch(html, /6\.65%/);
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
  if (process.env.NEXT_PUBLIC_INDEXABLE === "false") {
    assert.match(html, /name="robots" content="noindex, nofollow"/);
  } else {
    assert.match(html, /name="robots" content="index, follow"/);
  }
  assert.match(html, /rel="canonical" href="https:\/\/drmortgageusa\.com\/"/);
  assert.match(html, /property="og:title" content="DR\. Mortgage USA"/);
  assert.match(html, /property="og:url" content="https:\/\/drmortgageusa\.com"/);
  assert.match(html, /property="og:image" content="https:\/\/drmortgageusa\.com\/dennis-ross-headshot\.png"/);
  assert.match(html, /property="og:image:width" content="1000"/);
  assert.match(html, /property="og:image:height" content="1000"/);
  assert.match(html, /name="twitter:image" content="https:\/\/drmortgageusa\.com\/dennis-ross-headshot\.png"/);
  assert.match(
    html,
    /name="msvalidate\.01" content="5CC872A1985FD683E724A7CBF0779BB1"/,
  );
  assert.match(
    html,
    /name="google-site-verification" content="Q8StPrmafCxwpofzJV9Mizb1x32yYo2JE8Gyqa_sFlM"/,
  );
  const entityMatch = html.match(/<script type="application\/ld\+json">(.*?)<\/script>/);
  assert.ok(entityMatch, "homepage entity graph should render");
  const entityGraph = JSON.parse(entityMatch[1]);
  const brand = entityGraph["@graph"].find(
    (entity) => entity["@id"] === "https://drmortgageusa.com/#brand",
  );
  const person = entityGraph["@graph"].find(
    (entity) => entity["@id"] === "https://drmortgageusa.com/about#dennis-ross",
  );
  const home1st = entityGraph["@graph"].find(
    (entity) => entity["@id"] === "https://myhome1st.com/#organization",
  );
  const website = entityGraph["@graph"].find(
    (entity) => entity["@id"] === "https://drmortgageusa.com/#website",
  );
  assert.equal(brand["@type"], "Brand");
  assert.equal(brand.name, "DR. Mortgage USA");
  assert.match(brand.description, /not a separate lender or mortgage company/);
  assert.match(brand.disambiguatingDescription, /does not identify Dr\. Mortgage, LLC/);
  assert.equal(brand.owner["@id"], "https://drmortgageusa.com/about#dennis-ross");
  assert.equal(brand.address, undefined);
  assert.equal(brand.telephone, undefined);
  assert.equal(brand.parentOrganization, undefined);
  assert.equal(
    person.brand["@id"],
    "https://drmortgageusa.com/#brand",
  );
  assert.equal(
    website.publisher["@id"],
    "https://drmortgageusa.com/about#dennis-ross",
  );
  assert.ok(
    !entityGraph["@graph"].some(
      (entity) => entity["@id"] === "https://drmortgageusa.com/#organization",
    ),
  );
  assert.equal(person.identifier.value, "2018381");
  assert.ok(person.sameAs.includes("https://myhome1st.com/dennis/"));
  assert.ok(person.sameAs.includes("https://www.bing.com/maps?ss=ypid.YN215EB5A5FBD32023"));
  assert.ok(person.sameAs.includes("https://www.facebook.com/100084710485166"));
  assert.ok(!person.sameAs.some((url) => url.includes("facebook.com/p/Dennis-Ross-")));
  assert.ok(person.sameAs.includes("https://www.youtube.com/@Dr.MortgageUSA"));
  assert.ok(person.sameAs.includes("https://linktr.ee/dr.mortgageusa"));
  assert.ok(person.sameAs.includes("https://www.experience.com/reviews/dennis-14873595"));
  assert.ok(person.sameAs.includes("https://www.zillow.com/lender-profile/dennis0564/"));
  assert.ok(home1st.sameAs.includes("https://www.nmlsconsumeraccess.org/EntityDetails.aspx/COMPANY/1418"));
  assert.ok(home1st.sameAs.includes("https://www.yelp.com/biz/home-1st-lending-lake-mary-2"));
  assert.ok(!person.sameAs.includes("https://www.yelp.com/biz/home-1st-lending-lake-mary-2"));
  assert.match(html, /Independent profile evidence:/);
  assert.match(html, /Experience\.com(?:&apos;|&#x27;)'?s public Dennis Ross Jr\. profile/);
  assert.match(html, /identifies NMLS #2018381 and Dr MortgageUSA in Lake Mary/);
  assert.match(html, /lists VA\s*Home Loan among the services/);
  assert.match(html, /5\.0 average across 16\s*reviews aggregated from Google and Zillow/);
  assert.match(html, /alt="DR\. Mortgage USA logo"/);
  assert.match(html, /rel="me" href="https:\/\/www\.linkedin\.com\/in\/dennis-ross-87491257"/);
  assert.match(html, /rel="me" href="https:\/\/linktr\.ee\/dr\.mortgageusa"/);
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
  const blogEntityMatch = blogHtml.match(/<script type="application\/ld\+json">(.*?)<\/script>/);
  assert.ok(blogEntityMatch, "blog entity graph should render");
  const blogEntityGraph = JSON.parse(blogEntityMatch[1]);
  const collection = blogEntityGraph["@graph"].find(
    (entity) => entity["@id"] === "https://drmortgageusa.com/blog#collection",
  );
  const blogAuthor = blogEntityGraph["@graph"].find(
    (entity) => entity["@id"] === "https://drmortgageusa.com/about#dennis-ross",
  );
  assert.equal(collection["@type"], "CollectionPage");
  assert.match(collection.description, /Navy veteran Dennis Ross/);
  assert.ok(collection.about.some((topic) => topic.name === "VA home loans in Greater Orlando"));
  assert.ok(blogAuthor.sameAs.includes("https://www.bing.com/maps?ss=ypid.YN215EB5A5FBD32023"));
  assert.ok(blogAuthor.sameAs.includes("https://www.facebook.com/100084710485166"));
  assert.ok(blogAuthor.sameAs.includes("https://linktr.ee/dr.mortgageusa"));
  assert.ok(blogAuthor.sameAs.includes("https://www.experience.com/reviews/dennis-14873595"));
  assert.ok(blogAuthor.sameAs.includes("https://www.zillow.com/lender-profile/dennis0564/"));

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
  assert.match(html, /<title>Dennis Ross, NMLS 2018381 \| Orlando VA Mortgage Broker<\/title>/);
  assert.match(html, /Dennis Ross: Navy veteran and Greater Orlando mortgage broker/);
  assert.match(html, /VA home loan guidance across Greater Orlando/);
  assert.match(html, /NMLS Consumer Access/);
  assert.match(html, /official Home 1st Lending profile/);
  assert.match(html, /Google Business Profile/);
  assert.match(html, /claimed Yelp business profile/);
  assert.match(html, /VA loan as a service verified by the business/);
  assert.match(html, /Experience\.com profile/);
  assert.match(html, /explicitly lists VA Home Loan among my services/);
  assert.match(html, /16 verified reviews/);
  assert.match(html, /display name contains the text USMC-VET/);
  assert.match(html, /does not identify which loan program was used/);
  assert.match(html, /DR\. Mortgage USA is my professional brand and educational website/);
  assert.match(html, /does not refer to Dr\. Mortgage, LLC/);
  const personMatch = html.match(/<script type="application\/ld\+json">(.*?)<\/script>/);
  assert.ok(personMatch, "about profile page structured data should render");
  const schema = JSON.parse(personMatch[1]);
  const profilePage = schema["@graph"].find((node) => node["@type"] === "ProfilePage");
  const person = schema["@graph"].find((node) => node["@id"] === profilePage.mainEntity["@id"]);
  const brand = schema["@graph"].find((node) => node["@id"] === person.brand["@id"]);
  assert.equal(profilePage["@type"], "ProfilePage");
  assert.equal(person["@type"], "Person");
  assert.equal(person.name, "Dennis Ross");
  assert.equal(person.identifier.value, "2018381");
  assert.match(person.disambiguatingDescription, /NMLS 2018381/);
  assert.match(person.disambiguatingDescription, /Home 1st Lending, LLC/);
  assert.match(person.description, /Known publicly as DR\. Mortgage USA/);
  assert.ok(person.sameAs.includes("https://www.google.com/maps?cid=3829412552217676351"));
  assert.ok(person.sameAs.includes("https://www.linkedin.com/in/dennis-ross-87491257"));
  assert.ok(person.sameAs.includes("https://www.facebook.com/100084710485166"));
  assert.ok(person.sameAs.includes("https://linktr.ee/dr.mortgageusa"));
  assert.ok(person.worksFor.sameAs.includes("https://www.yelp.com/biz/home-1st-lending-lake-mary-2"));
  assert.ok(!person.sameAs.includes("https://www.yelp.com/biz/home-1st-lending-lake-mary-2"));
  assert.equal(brand["@type"], "Brand");
  assert.equal(brand.name, "DR. Mortgage USA");
  assert.equal(brand.owner["@id"], person["@id"]);
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
