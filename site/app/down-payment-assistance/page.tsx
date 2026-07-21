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
  ["Florida programs", "Some statewide programs combine a first mortgage with down payment or closing-cost help. Your income, home price, credit, education, and homeownership history can all affect the answer."],
  ["County and city programs", "Local programs can be generous, but they may open and close as funding changes. Where you buy matters just as much as how much you earn."],
  ["Programs tied to work or service", "Some options are built for eligible occupations, military service, or veterans. I will help you confirm what is actually available before you plan around it."],
];

export default function DownPaymentAssistancePage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Down payment assistance"
        title="Need help covering the down payment or closing costs?"
        body="You may have more options than you think. I will help you sort through what may actually work before you get your hopes up or rule yourself out."
      >
        <Link className="button button-gold" href="#dpa-rates">See today&apos;s DPA rates</Link>
        <Link className="button button-outline-light" href="#dpa-check">Have Dennis check my options</Link>
      </PageHero>

      <section className="section dpa-intro-section">
        <div className="shell dpa-intro-grid">
          <div>
            <SectionHeading
              eyebrow="You do not have to know the program names"
              title="Tell me about the home, the household, and the help you need."
              body="It is my job to sort through the programs. Your job is to give me the basics so I can see which options are funded, which rules matter, and which ones are worth a closer look."
            />
            <ul className="check-list dpa-factor-list">
              <li>Where in Florida you plan to buy</li>
              <li>How many people are in the household and the household income</li>
              <li>Whether you have owned a home recently</li>
              <li>Your general credit, monthly obligations, and cash available</li>
              <li>How soon you want to buy and whether the program is currently funded</li>
            </ul>
          </div>
          <aside className="dpa-reality-card">
            <p className="eyebrow">The honest comparison</p>
            <h2>The biggest assistance amount is not always the best deal.</h2>
            <p>Some programs come with a higher first-mortgage rate, a second lien, or rules about selling and refinancing. I will compare the help you receive with the payment and long-term cost so you can see the full tradeoff.</p>
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
            eyebrow="Where the help may come from"
            title="There is more than one place to look for assistance."
            body="These are the three main program families I review. None is guaranteed, and funding and rules can change."
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
            <p className="eyebrow">A quick starting point</p>
            <h2>Give me the basics. I will help you narrow it down.</h2>
            <p>This is not an application, and it will not determine approval. It simply gives me enough context to start looking in the right places.</p>
          </div>
          <div className="form-card"><DpaCheck /></div>
        </div>
      </section>
      <FinalCTA title="Do not choose a program based only on the assistance amount." body="I can compare the current program terms with a standard low-down-payment option so you can see which one leaves you in the better position." />
    </PageShell>
  );
}
