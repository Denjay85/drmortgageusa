import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell } from "../site-components";
import HelocCalculator from "../tools/HelocCalculator";

export const metadata: Metadata = {
  title: "HELOC Calculator",
  description: "Estimate available home equity and model an illustrative HELOC line, draw, variable-rate payment, and repayment scenario.",
};

export default function HelocCalculatorPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="HELOC & home equity calculator"
        title="Estimate the line and pressure-test the payment."
        body="Explore how value, the existing mortgage, a combined-loan-to-value assumption, the credit line, the draw, and a variable rate work together."
      >
        <Link className="button button-gold" href="#calculator">Open the HELOC calculator</Link>
        <Link className="button button-outline-light" href="/mortgage-options#equity">Compare equity options</Link>
      </PageHero>
      <section className="section section-cream anchor-target" id="calculator">
        <div className="shell"><HelocCalculator /></div>
      </section>
      <FinalCTA title="A HELOC can preserve your first mortgage, but that does not automatically make it the best equity option." body="Compare the variable-rate line with a home-equity loan and cash-out refinance using your complete scenario." />
    </PageShell>
  );
}
