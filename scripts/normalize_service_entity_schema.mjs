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

const dennisId = "https://drmortgageusa.com/about#dennis-ross";
const brandId = "https://drmortgageusa.com/#brand";
const home1stId = "https://myhome1st.com/#organization";

const home1st = {
  "@type": "Organization",
  "@id": home1stId,
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
  address: {
    "@type": "PostalAddress",
    streetAddress: "1130 Business Center Dr, Suite 1000",
    addressLocality: "Lake Mary",
    addressRegion: "FL",
    postalCode: "32746",
    addressCountry: "US",
  },
};

const brand = {
  "@type": "Brand",
  "@id": brandId,
  name: "DR. Mortgage USA",
  alternateName: ["DrMortgageUSA", "Dennis Ross, Dr.MortgageUSA"],
  url: "https://drmortgageusa.com/",
  description:
    "DR. Mortgage USA is Dennis Ross's professional brand and educational website, not a separate lender or mortgage company.",
  disambiguatingDescription:
    "The DR. Mortgage USA name on drmortgageusa.com identifies Dennis Ross, individual NMLS 2018381, and does not identify Dr. Mortgage, LLC or another separately licensed mortgage company.",
  logo: {
    "@type": "ImageObject",
    url: "https://drmortgageusa.com/media/logo.webp",
  },
  owner: { "@id": dennisId },
};

const dennisSameAs = [
  "https://www.nmlsconsumeraccess.org/EntityDetails.aspx/INDIVIDUAL/2018381",
  "https://myhome1st.com/dennis/",
  "https://www.google.com/maps?cid=3829412552217676351",
  "https://www.bing.com/maps?ss=ypid.YN215EB5A5FBD32023",
  "https://www.instagram.com/dr.mortgageusa/",
  "https://www.facebook.com/100084710485166",
  "https://www.linkedin.com/in/dennis-ross-87491257",
  "https://www.youtube.com/@Dr.MortgageUSA",
  "https://linktr.ee/dr.mortgageusa",
];

const dennis = {
  "@type": "Person",
  "@id": dennisId,
  name: "Dennis Ross",
  alternateName: ["DR. Mortgage USA", "DrMortgageUSA"],
  url: "https://drmortgageusa.com/about",
  image: "https://drmortgageusa.com/dennis-ross-headshot.png",
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
  brand: { "@id": brandId },
  worksFor: { "@id": home1stId },
  sameAs: dennisSameAs,
};

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
    service.provider = { "@id": dennisId };
    service.brand = { "@id": brandId };
    delete service.telephone;
    delete service.image;
    delete service.sameAs;
    delete service.parentOrganization;

    schema["@graph"] = schema["@graph"].filter(
      (entity) => entity["@id"] !== "https://drmortgageusa.com/#organization",
    );

    for (const entity of [dennis, home1st, brand]) {
      const entityIndex = schema["@graph"].findIndex(
        (candidate) => candidate["@id"] === entity["@id"],
      );
      if (entityIndex === -1) {
        schema["@graph"].push(entity);
      } else {
        schema["@graph"][entityIndex] = entity;
      }
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
