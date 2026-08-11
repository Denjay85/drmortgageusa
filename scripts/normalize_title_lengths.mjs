import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const maximumTitleLength = 69;
const checkOnly = process.argv.includes("--check");

const titleOverrides = new Map([
  ["dpa.html", "Florida Down Payment Assistance | Orlando DPA"],
  ["first-time-homebuyer-orlando.html", "First-Time Homebuyer Orlando | Loans and DPA"],
  ["refinance-florida.html", "Florida Refinance Options | Dennis Ross"],
  ["first-time-homebuyer-florida-2026.html", "First-Time Homebuyer Guide for Florida (2026)"],
  ["mortgage-preapproval-vs-prequalification-florida.html", "Mortgage Preapproval vs Prequalification in Florida"],
  ["new-construction-builder-incentives-orlando-2026.html", "Orlando New Construction Builder Incentives (2026)"],
  ["orlando-housing-market-outlook-2026.html", "Orlando Housing Market Outlook for 2026"],
  ["va-appraisal-repairs-florida-2026.html", "VA Appraisal Repairs in Florida (2026)"],
  ["va-loan-assumability-guide-florida-2026.html", "VA Loan Assumability in Florida (2026 Guide)"],
  ["va-loan-guide-florida-veterans-2026.html", "VA Loan Guide for Florida Veterans (2026)"],
  ["va-loan-seller-concessions-florida.html", "VA Loan Seller Concessions in Florida"],
  ["what-happens-mortgage-closing-florida.html", "What Happens at a Florida Mortgage Closing"],
]);

const rootHtmlFiles = fs
  .readdirSync(repositoryRoot)
  .filter((filename) => filename.endsWith(".html"))
  .map((filename) => path.join(repositoryRoot, filename));
const blogHtmlFiles = fs
  .readdirSync(path.join(repositoryRoot, "blog_posts"))
  .filter((filename) => filename.endsWith(".html"))
  .map((filename) => path.join(repositoryRoot, "blog_posts", filename));

const changed = [];
const failures = [];
for (const filePath of [...rootHtmlFiles, ...blogHtmlFiles]) {
  const source = fs.readFileSync(filePath, "utf8");
  const match = source.match(/<title>([^<]+)<\/title>/i);
  if (!match) continue;

  const currentTitle = match[1].trim();
  if (checkOnly) {
    if (currentTitle.length > maximumTitleLength) {
      failures.push(`${path.relative(repositoryRoot, filePath)} (${currentTitle.length}): ${currentTitle}`);
    }
    continue;
  }

  if (currentTitle.length <= maximumTitleLength) continue;
  const filename = path.basename(filePath);
  const normalizedTitle =
    titleOverrides.get(filename) ??
    currentTitle.replace(/\s+\|\s+Dr\.?MortgageUSA(?:\s+Blog)?$/i, "").trim();

  if (normalizedTitle.length > maximumTitleLength) {
    failures.push(`${path.relative(repositoryRoot, filePath)} needs an explicit title override: ${normalizedTitle}`);
    continue;
  }

  let updated = source.replace(match[0], `<title>${normalizedTitle}</title>`);
  if (!filePath.includes(`${path.sep}blog_posts${path.sep}`)) {
    updated = updated
      .replace(
        /(<meta property="og:title" content=")[^"]+("\s*\/?>)/i,
        `$1${normalizedTitle}$2`,
      )
      .replace(
        /(<meta name="twitter:title" content=")[^"]+("\s*\/?>)/i,
        `$1${normalizedTitle}$2`,
      );
  }
  fs.writeFileSync(filePath, updated);
  changed.push(`${path.relative(repositoryRoot, filePath)}: ${currentTitle} -> ${normalizedTitle}`);
}

if (failures.length) {
  console.error(failures.join("\n"));
  process.exitCode = 1;
} else if (checkOnly) {
  console.log(`All public HTML titles are ${maximumTitleLength} characters or fewer.`);
} else {
  console.log(changed.length ? changed.join("\n") : "No titles needed normalization.");
}
