#!/usr/bin/env node

import { readdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(scriptDirectory, "..");
const blogDirectory = path.join(projectRoot, "blog_posts");
const articleImage = "https://drmortgageusa.com/assets/client-collage.jpg";

const authorSameAs = [
  "https://www.nmlsconsumeraccess.org/EntityDetails.aspx/INDIVIDUAL/2018381",
  "https://myhome1st.com/dennis/",
  "https://www.google.com/maps?cid=3829412552217676351",
  "https://www.bing.com/maps?ss=ypid.YN215EB5A5FBD32023",
  "https://www.instagram.com/dr.mortgageusa/",
  "https://www.facebook.com/100084710485166",
  "https://www.linkedin.com/in/dennis-ross-87491257",
  "https://www.youtube.com/@Dr.MortgageUSA",
  "https://linktr.ee/dr.mortgageusa",
  "https://www.experience.com/reviews/dennis-14873595",
  "https://www.zillow.com/lender-profile/dennis0564/",
];

const home1stOrganization = {
  "@type": "Organization",
  "@id": "https://myhome1st.com/#organization",
  name: "Home 1st Lending, LLC",
  url: "https://myhome1st.com/",
  identifier: {
    "@type": "PropertyValue",
    propertyID: "NMLS",
    value: "1418",
  },
  sameAs: [
    "https://www.nmlsconsumeraccess.org/EntityDetails.aspx/COMPANY/1418",
    "https://www.yelp.com/biz/home-1st-lending-lake-mary-2",
  ],
};

const author = {
  "@type": "Person",
  "@id": "https://drmortgageusa.com/about#dennis-ross",
  name: "Dennis Ross",
  url: "https://drmortgageusa.com/about",
  description:
    "Navy veteran and Florida Mortgage Loan Originator helping Greater Orlando veterans, buyers, and homeowners understand VA and other mortgage options.",
  disambiguatingDescription:
    "Dennis Ross, individual NMLS 2018381, is the Navy veteran behind the DR. Mortgage USA professional brand and originates mortgage loans through Home 1st Lending, LLC, company NMLS 1418.",
  jobTitle: "Mortgage Loan Originator and Mortgage Broker",
  identifier: {
    "@type": "PropertyValue",
    propertyID: "NMLS",
    value: "2018381",
  },
  worksFor: home1stOrganization,
  sameAs: authorSameAs,
  knowsAbout: [
    "VA home loans in Greater Orlando",
    "Florida mortgages",
    "VA loan entitlement and funding fees",
    "FHA loans",
    "Down payment assistance",
    "Self-employed mortgage lending",
    "Home equity financing",
  ],
};

const publisher = {
  "@type": "Organization",
  "@id": "https://drmortgageusa.com/#organization",
  name: "DR. Mortgage USA",
  url: "https://drmortgageusa.com/",
  logo: {
    "@type": "ImageObject",
    url: "https://drmortgageusa.com/media/logo.webp",
  },
};

const floridaOffsetFormatter = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/New_York",
  timeZoneName: "longOffset",
});

function asFloridaDateTime(value) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return value;
  }

  const timezoneName = floridaOffsetFormatter
    .formatToParts(new Date(`${value}T12:00:00Z`))
    .find((part) => part.type === "timeZoneName")?.value;
  const offset = timezoneName?.startsWith("GMT")
    ? timezoneName.slice(3) || "+00:00"
    : "-05:00";
  return `${value}T09:00:00${offset}`;
}

const jsonLdPattern = /(<script\s+type="application\/ld\+json">\s*)(\{[\s\S]*?\})(\s*<\/script>)/g;
const files = (await readdir(blogDirectory))
  .filter((name) => name.endsWith(".html"))
  .sort();

let updatedSchemas = 0;

for (const fileName of files) {
  const filePath = path.join(blogDirectory, fileName);
  const source = await readFile(filePath, "utf8");
  const canonicalUrl = source.match(
    /<link\s+rel="canonical"\s+href="([^"]+)"/i,
  )?.[1];
  let fileChanged = false;

  let next = source.replace(jsonLdPattern, (full, before, jsonText, after) => {
    let schema;
    try {
      schema = JSON.parse(jsonText);
    } catch {
      return full;
    }

    if (!["Article", "BlogPosting"].includes(schema["@type"])) {
      return full;
    }

    schema.url ??= canonicalUrl;
    schema.author = author;
    schema.publisher = publisher;
    schema.mainEntityOfPage = {
      "@type": "WebPage",
      "@id": schema.url,
    };
    schema.image = [articleImage];
    schema.datePublished = asFloridaDateTime(schema.datePublished);
    schema.dateModified = asFloridaDateTime(schema.dateModified);

    updatedSchemas += 1;
    fileChanged = true;
    return `${before}${JSON.stringify(schema, null, 4)}${after}`;
  });

  if (!/<meta\s+property="og:image"/i.test(next)) {
    next = next.replace(
      /(\s*<meta\s+property="og:site_name"[^>]*>)/i,
      `$1\n    <meta property="og:image" content="${articleImage}">`,
    );
  }
  if (!/<meta\s+name="twitter:image"/i.test(next)) {
    next = next.replace(
      /(\s*<meta\s+name="twitter:card"[^>]*>)/i,
      `$1\n    <meta name="twitter:image" content="${articleImage}">`,
    );
  }

  if (fileChanged && next !== source) {
    await writeFile(filePath, next, "utf8");
  }
}

if (updatedSchemas < 58) {
  throw new Error(`Expected at least 58 article schemas, found ${updatedSchemas}`);
}

console.log(`Normalized ${updatedSchemas} article author entities.`);
