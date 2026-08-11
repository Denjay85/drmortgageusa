#!/usr/bin/env node

import { readdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(scriptDirectory, "..");
const blogDirectory = path.join(projectRoot, "blog_posts");

const author = {
  "@type": "Person",
  "@id": "https://drmortgageusa.com/about#dennis-ross",
  name: "Dennis Ross",
  url: "https://drmortgageusa.com/about",
  jobTitle: "Mortgage Loan Originator and Mortgage Broker",
  identifier: {
    "@type": "PropertyValue",
    propertyID: "NMLS",
    value: "2018381",
  },
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

const jsonLdPattern = /(<script\s+type="application\/ld\+json">\s*)(\{[\s\S]*?\})(\s*<\/script>)/g;
const files = (await readdir(blogDirectory))
  .filter((name) => name.endsWith(".html"))
  .sort();

let updatedSchemas = 0;

for (const fileName of files) {
  const filePath = path.join(blogDirectory, fileName);
  const source = await readFile(filePath, "utf8");
  let fileChanged = false;

  const next = source.replace(jsonLdPattern, (full, before, jsonText, after) => {
    let schema;
    try {
      schema = JSON.parse(jsonText);
    } catch {
      return full;
    }

    if (schema["@type"] !== "BlogPosting") {
      return full;
    }

    schema.author = author;
    schema.publisher = publisher;
    schema.mainEntityOfPage = {
      "@type": "WebPage",
      "@id": schema.url,
    };

    updatedSchemas += 1;
    fileChanged = true;
    return `${before}${JSON.stringify(schema, null, 4)}${after}`;
  });

  if (fileChanged && next !== source) {
    await writeFile(filePath, next, "utf8");
  }
}

if (updatedSchemas < 50) {
  throw new Error(`Expected at least 50 BlogPosting schemas, found ${updatedSchemas}`);
}

console.log(`Normalized ${updatedSchemas} BlogPosting author entities.`);
