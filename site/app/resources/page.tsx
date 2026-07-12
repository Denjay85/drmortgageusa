import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell, SectionHeading } from "../site-components";
import { blogPosts } from "../blog/posts";

export const metadata: Metadata = {
  title: "Florida Mortgage Resources",
  description: "Practical Florida mortgage guides, checklists, and market explanations from Dennis Ross.",
};

const guides = [
  ["VA strategy", "What Orlando veterans should check before writing an offer", "Eligibility is only the start. Review entitlement, property condition, insurance, taxes, and offer strategy."],
  ["Cash to close", "The Florida buyer cash-to-close checklist", "Down payment, closing costs, prepaids, reserves, inspections, and moving costs in one practical list."],
  ["Payment planning", "Preapproval amount vs. comfortable home budget", "A repeatable way to decide what payment fits before you shop at the maximum."],
  ["Condo financing", "Florida condo red flags to check early", "Association budget, insurance, litigation, reserves, milestone inspections, and lender review."],
  ["Self-employed", "Documents to gather before a mortgage review", "Tax returns, bank statements, business ownership, 1099s, and the questions that determine the path."],
  ["Home equity", "HELOC vs. home-equity loan vs. refinance", "When keeping the first mortgage matters, how variable rates behave, and where break-even fits."],
  ["DPA programs", "How Florida assistance fits into the complete loan", "Income, county, household, funds, education, and availability, without promising a program before review."],
  ["Loan estimates", "How to compare two mortgage quotes", "Rate, APR, points, lender credits, fees, cash to close, and the assumptions hidden in the payment."],
  ["Insurance", "Why Florida homeowners insurance can change the approval", "Premium, deductibles, roof age, flood zones, and the payment impact buyers need early."],
];

const featuredTools = [
  ["Mortgage FAQ", "Search the questions borrowers ask before they call", "Find clear answers about credit, cash to close, loan programs, documents, property review, equity, and investing.", "/faq"],
  ["DPA fit check", "See what shapes down payment assistance eligibility", "County, household, first-time-buyer status, income, first mortgage, and funding all matter.", "/dpa"],
  ["HELOC calculator", "Model your home equity and an illustrative payment", "Adjust value, mortgage balance, combined LTV, credit line, draw amount, rate, and repayment term.", "/heloc-calculator"],
];

export default function ResourcesPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Resources"
        title="Clear explanations for decisions that are not generic."
        body="Florida mortgage guidance shaped around the questions that change a payment, an approval, or a contract."
      >
        <Link className="button button-gold" href="/blog">Search the blog</Link>
        <Link className="button button-outline-light" href="/tools">Open the calculators</Link>
      </PageHero>
      <section className="section section-cream resource-destinations">
        <div className="shell">
          <SectionHeading
            eyebrow="Start with the format you need"
            title="Read the answer, run a scenario, or check a program path."
            body="The homepage answers the first concerns. The searchable depth lives here, where each resource can do one job well."
          />
          <div className="resource-destination-grid">
            <Link href="/blog" className="resource-destination resource-destination-featured">
              <span>Mortgage blog</span>
              <h2>Search Dennis’s growing library of Florida mortgage answers.</h2>
              <p>Browse recent VA, FHA, self-employed, homebuying, insurance, equity, and market-strategy articles.</p>
              <strong>Explore the blog →</strong>
            </Link>
            <div className="resource-destination-stack">
              {featuredTools.map(([label, title, body, href]) => (
                <Link href={href} className="resource-destination" key={label}>
                  <span>{label}</span>
                  <h3>{title}</h3>
                  <p>{body}</p>
                  <strong>Open this resource →</strong>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="shell">
          <div className="resource-heading-row">
            <SectionHeading
              eyebrow="New on the blog"
              title="Fresh answers to the questions Florida buyers are asking."
              body="These articles come directly from the current DR. Mortgage USA publishing archive."
            />
            <Link className="text-link" href="/blog">View the blog library <span>→</span></Link>
          </div>
          <div className="resource-grid">
            {blogPosts.slice(0, 3).map((post, index) => (
              <a className="resource-card" href={post.url} key={post.url}>
                <span className="resource-number">0{index + 1}</span>
                <p className="card-label">{post.category} · {post.date}</p>
                <h3>{post.title}</h3>
                <p>{post.description}</p>
                <span className="resource-read">Read the article →</span>
              </a>
            ))}
          </div>
        </div>
      </section>
      <section className="section">
        <div className="shell">
          <SectionHeading
            eyebrow="Guide library"
            title="Start with the question in front of you."
            body="The complete resource library can connect every guide to its best calculator, related articles, and a clear next step."
          />
          <div className="resource-grid">
            {guides.map(([label, title, body], index) => (
              <article className="resource-card" key={title}>
                <span className="resource-number">{String(index + 1).padStart(2, "0")}</span>
                <p className="card-label">{label}</p>
                <h3>{title}</h3>
                <p>{body}</p>
                <Link className="resource-read" href="/contact">Ask Dennis about this →</Link>
              </article>
            ))}
          </div>
        </div>
      </section>
      <FinalCTA />
    </PageShell>
  );
}
