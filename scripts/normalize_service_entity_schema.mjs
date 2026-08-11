#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(scriptDirectory, "..");
const servicePages = [
  "va-loans-orlando.html",
  "orlando-mortgage-broker.html",
  "first-time-homebuyer-orlando.html",
  "refinance-florida.html",
  "heloc-orlando.html",
];

const provider = {
  "@type": "FinancialService",
  "@id": "https://drmortgageusa.com/#organization",
  name: "DR. Mortgage USA",
  url: "https://drmortgageusa.com/",
  telephone: "+1-850-346-8514",
  founder: { "@id": "https://drmortgageusa.com/about#dennis-ross" },
  parentOrganization: {
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
  },
};

const dennisSameAs = [
  "https://www.nmlsconsumeraccess.org/EntityDetails.aspx/INDIVIDUAL/2018381",
  "https://myhome1st.com/dennis/",
  "https://www.google.com/maps?cid=3829412552217676351",
  "https://www.bing.com/maps?ss=ypid.YN215EB5A5FBD32023",
  "https://www.instagram.com/dr.mortgageusa/",
  "https://www.facebook.com/p/Dennis-Ross-Mortgage-Loan-Originator-Nmls2018381-100084710485166/",
  "https://www.linkedin.com/in/dennis-ross-87491257",
  "https://www.youtube.com/@Dr.MortgageUSA",
  "https://www.experience.com/reviews/dennis-14873595",
  "https://www.zillow.com/lender-profile/dennis0564/",
];

const jsonLdPattern = /(<script\s+type="application\/ld\+json">\s*)(\{[\s\S]*?\})(\s*<\/script>)/g;
let updatedPages = 0;

for (const fileName of servicePages) {
  const filePath = path.join(projectRoot, fileName);
  const source = await readFile(filePath, "utf8");
  let pageChanged = false;

  const next = source.replace(jsonLdPattern, (full, before, jsonText, after) => {
    let schema;
    try {
      schema = JSON.parse(jsonText);
    } catch {
      return full;
    }

    const service = schema["@graph"]?.find(
      (entity) => typeof entity["@id"] === "string" && entity["@id"].endsWith("#service"),
    );
    if (!service) {
      return full;
    }

    service["@type"] = "Service";
    service.provider = provider;
    delete service.telephone;
    delete service.image;
    delete service.sameAs;
    delete service.parentOrganization;

    const dennis = schema["@graph"]?.find(
      (entity) => entity["@id"] === "https://drmortgageusa.com/about#dennis-ross",
    );
    if (dennis) {
      dennis.sameAs = dennisSameAs;
      dennis.worksFor = { "@id": "https://myhome1st.com/#organization" };
    }

    pageChanged = true;
    return `${before}${JSON.stringify(schema)}${after}`;
  });

  if (!pageChanged) {
    throw new Error(`No service entity found in ${fileName}`);
  }

  if (next !== source) {
    await writeFile(filePath, next, "utf8");
  }
  updatedPages += 1;
}

console.log(`Normalized ${updatedPages} service-page providers.`);
