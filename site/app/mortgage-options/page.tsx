import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell } from "../site-components";

export const metadata: Metadata = {
  title: "Mortgage Options",
  description: "Compare home purchase, move-up buyer, VA, self-employed, investor, refinance, and home-equity mortgage paths in Florida.",
};

const options = [
  {
    id: "first-time",
    eyebrow: "Home purchase",
    title: "Plan the first home or the next one around the complete move.",
    body: "The right purchase loan is not automatically the one with the smallest down payment. We compare payment, mortgage insurance, closing costs, reserves, seller credits, assistance, current-home equity, and sale timing so the entire plan works.",
    pills: ["First home", "Move-up buyer", "Relocation", "FHA", "Conventional", "Florida DPA"],
    bullets: [
      "A comfortable payment range, not only the maximum approval",
      "A complete estimate of down payment, closing costs, reserves, and sale proceeds",
      "Buy-before-sell, contingent-offer, and assistance questions reviewed early",
    ],
  },
  {
    id: "va",
    eyebrow: "VA financing",
    title: "Use the benefit with a veteran in your corner.",
    body: "Dennis reviews entitlement, Certificate of Eligibility, funding-fee exemptions, residual income, property issues, taxes, insurance, and offer strategy before you are deep in a contract.",
    pills: ["0% down for eligible buyers", "No monthly PMI", "IRRRL", "Repeat use", "VA jumbo"],
    bullets: [
      "Full or remaining entitlement review",
      "Orlando condo and property-condition questions",
      "Payment planning with taxes, insurance, and HOA included",
    ],
  },
  {
    id: "specialty",
    eyebrow: "Self-employed & investors",
    title: "A complex file deserves more than one bank box.",
    body: "Tax returns do not always tell the whole story. We can compare agency income, bank statements, 1099 income, asset depletion, DSCR, and other specialty paths across multiple wholesale lenders.",
    pills: ["Bank statement", "1099", "DSCR", "Fix & flip", "Asset-based"],
    bullets: [
      "Review the document path before a credit pull",
      "Compare rate and flexibility, not just approval",
      "Keep business and property strategy in the same conversation",
    ],
  },
  {
    id: "equity",
    eyebrow: "Refinance & home equity",
    title: "Match the tool to the reason you need the money.",
    body: "A HELOC, fixed home-equity loan, cash-out refinance, or rate-and-term refinance can produce very different costs and risks. Start with your goal, current first mortgage, timeline, and break-even point.",
    pills: ["HELOC", "Home equity loan", "Cash-out refinance", "Rate & term", "VA IRRRL"],
    bullets: [
      "Keep a strong first mortgage in place when that makes sense",
      "Compare variable-rate and fixed-payment tradeoffs",
      "Calculate break-even before changing the loan",
    ],
  },
];

export default function MortgageOptionsPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Mortgage options"
        title="The best loan is the one that fits the complete picture."
        body="Credit, income, cash, property, timeline, and monthly comfort all matter. Compare the paths first; apply when the direction is clear."
      >
        <Link className="button button-gold" href="/get-started">Find my likely path</Link>
        <Link className="button button-outline-light" href="/contact">Talk with Dennis</Link>
      </PageHero>

      <section className="content-section">
        <div className="shell">
          {options.map((option) => (
            <article className="option-row anchor-target" id={option.id} key={option.id}>
              <div>
                <p className="eyebrow">{option.eyebrow}</p>
                <h2>{option.title}</h2>
              </div>
              <div className="option-row-copy">
                <p>{option.body}</p>
                <div className="pill-list">
                  {option.pills.map((pill) => <span key={pill}>{pill}</span>)}
                </div>
                <ul className="check-list">
                  {option.bullets.map((bullet) => <li key={bullet}>{bullet}</li>)}
                </ul>
                <Link className="text-link" href="/get-started">Build a plan for this path <span>→</span></Link>
              </div>
            </article>
          ))}
        </div>
      </section>
      <FinalCTA
        title="Unsure which section is yours? That is exactly what the plan is for."
        body="Answer a few simple questions and see the likely conversation to have next."
      />
    </PageShell>
  );
}
