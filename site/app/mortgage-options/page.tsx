import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell } from "../site-components";

export const metadata: Metadata = {
  title: "Mortgage Options",
  alternates: { canonical: "/mortgage-options" },
  description: "Compare home purchase, move-up buyer, VA, self-employed, investor, refinance, and home-equity mortgage paths in Florida.",
};

const options = [
  {
    id: "first-time",
    eyebrow: "Home purchase",
    title: "Buying your first home or moving into the next one?",
    body: "The loan with the smallest down payment is not automatically the best loan. I will help you compare the monthly payment, cash needed, closing costs, seller credits, assistance options, and the timing of your move so the whole plan works together.",
    pills: ["First home", "Move-up buyer", "Relocation", "FHA", "Conventional", "Florida DPA"],
    bullets: [
      "Choose a payment that fits your life, not just the maximum approval",
      "See the down payment, closing costs, reserves, and possible sale proceeds together",
      "Talk through selling first, buying first, or making a contingent offer before you are under pressure",
    ],
  },
  {
    id: "va",
    eyebrow: "VA financing",
    title: "Using your VA benefit should feel like an advantage, not another maze.",
    body: "I am a veteran too. I will help you understand your entitlement, Certificate of Eligibility, possible funding fee exemption, full monthly payment, property questions, and offer strategy before you are deep in a contract.",
    pills: ["0% down for eligible buyers", "No monthly PMI", "IRRRL", "Repeat use", "VA jumbo"],
    bullets: [
      "Find out whether you have full or remaining entitlement",
      "Catch condo, appraisal, and property-condition questions early",
      "See the payment with taxes, insurance, and HOA included",
    ],
  },
  {
    id: "specialty",
    eyebrow: "Self-employed & investors",
    title: "Your tax return may not tell the full story of your business.",
    body: "Being self-employed does not mean you have only one way to qualify. I can compare traditional income, bank statements, 1099 income, assets, DSCR, and other specialty options across multiple wholesale lenders.",
    pills: ["Bank statement", "1099", "DSCR", "Fix & flip", "Asset-based"],
    bullets: [
      "Find out which documents tell your story best before a credit pull",
      "Compare the cost and flexibility, not just whether one lender says yes",
      "Keep the business plan and the property plan in the same conversation",
    ],
  },
  {
    id: "equity",
    eyebrow: "Refinance & home equity",
    title: "You have equity. The real question is how much of it you should use.",
    body: "A HELOC, fixed home-equity loan, cash-out refinance, and traditional refinance can solve different problems. I will help you compare them without casually giving up a good first mortgage or taking on a payment that does not fit the goal.",
    pills: ["HELOC", "Home equity loan", "Cash-out refinance", "Rate & term", "VA IRRRL"],
    bullets: [
      "See when keeping your current first mortgage makes sense",
      "Compare a flexible variable rate with a predictable fixed payment",
      "Know how long it may take to recover the cost before changing the loan",
    ],
  },
];

export default function MortgageOptionsPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Mortgage options"
        title="You do not need to know the loan name before we start."
        body="Tell me what you are trying to accomplish. I will help you compare the payment, cash, timing, and tradeoffs so the loan fits the move you are actually making."
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
                <Link className="text-link" href="/get-started">See what this could look like for me <span>→</span></Link>
              </div>
            </article>
          ))}
        </div>
      </section>
      <FinalCTA
        title="Not sure which option fits? You do not have to decide alone."
        body="Answer a few simple questions and I will help you narrow down the conversation worth having next."
      />
    </PageShell>
  );
}
