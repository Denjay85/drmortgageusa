import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell, SectionHeading } from "../site-components";
import DpaCheck from "./DpaCheck";
import DpaRateTracker from "./DpaRateTracker";

export const metadata: Metadata = {
  title: "Florida Down Payment Assistance",
  alternates: { canonical: "/dpa" },
  description: "Understand the questions that shape Florida down payment assistance eligibility and prepare for a current program review.",
};

const programFamilies = [
  ["Statewide programs", "Florida Housing programs can combine an eligible first mortgage with assistance. Income, purchase price, education, credit, and first-time-buyer rules can apply."],
  ["County and city programs", "Local programs may offer forgivable, deferred, or repayable assistance. Funding windows and geographic boundaries matter."],
  ["Occupation and service paths", "Some programs are shaped around an eligible occupation, military service, or veteran status. The definition and current availability must be verified."],
];

export default function DownPaymentAssistancePage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Down payment assistance"
        title="Assistance is part of the plan, not a standalone promise."
        body="See which details determine program fit, understand how assistance can affect the first mortgage, and prepare for a current eligibility review."
      >
        <Link className="button button-gold" href="#dpa-rates">View today&apos;s DPA rates</Link>
        <Link className="button button-outline-light" href="#dpa-check">Check the starting factors</Link>
      </PageHero>

      <section className="section dpa-intro-section">
        <div className="shell dpa-intro-grid">
          <div>
            <SectionHeading
              eyebrow="What changes the answer"
              title="The program name is only the beginning."
              body="The useful question is not simply whether assistance exists. It is whether a currently funded option fits the location, household, first mortgage, timeline, and full file."
            />
            <ul className="check-list dpa-factor-list">
              <li>County or city where the home will be purchased</li>
              <li>Household size and program-specific income calculation</li>
              <li>First-time homebuyer definition and possible exceptions</li>
              <li>Credit, debt-to-income ratio, reserves, and approved first mortgage</li>
              <li>Homebuyer education, funding availability, and closing timeline</li>
            </ul>
          </div>
          <aside className="dpa-reality-card">
            <p className="eyebrow">Plan the complete cost</p>
            <h2>Assistance can reduce cash needed upfront, but it may come with a second lien or repayment rules.</h2>
            <p>Compare the interest rate, total payment, assistance terms, required cash, future sale or refinance impact, and an option without assistance.</p>
          </aside>
        </div>
      </section>

      <section className="section section-navy dpa-rate-section anchor-target" id="dpa-rates">
        <div className="shell">
          <DpaRateTracker />
        </div>
      </section>

      <section className="section section-cream">
        <div className="shell">
          <SectionHeading
            eyebrow="Program map"
            title="Three places to look, followed by one complete comparison."
            body="These are broad program families, not a list of guaranteed benefits. Details and funding can change."
          />
          <div className="dpa-program-grid">
            {programFamilies.map(([title, body], index) => (
              <article key={title}>
                <span>0{index + 1}</span>
                <h3>{title}</h3>
                <p>{body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section anchor-target" id="dpa-check">
        <div className="shell dpa-check-grid">
          <div>
            <p className="eyebrow">Quick fit check</p>
            <h2>Start with the details that narrow the search.</h2>
            <p>This is deliberately shorter than an application. It prepares a useful conversation without pretending that four answers determine approval.</p>
          </div>
          <div className="form-card"><DpaCheck /></div>
        </div>
      </section>
      <FinalCTA title="Compare assistance with a low-down-payment option before you choose." body="Dennis can review the current assistance terms alongside the complete payment and cash-to-close picture." />
    </PageShell>
  );
}
