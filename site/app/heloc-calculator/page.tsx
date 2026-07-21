import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell } from "../site-components";
import HelocCalculator from "../tools/HelocCalculator";

export const metadata: Metadata = {
  title: "HELOC Calculator",
  alternates: { canonical: "/heloc-calculator" },
  description: "Estimate available home equity and model an illustrative HELOC line, draw, variable-rate payment, and repayment scenario.",
};

export default function HelocCalculatorPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="HELOC & home equity calculator"
        title="How much equity could you use, and what might the payment look like?"
        body="Enter the home value, current mortgage, amount you want to borrow, and an estimated rate. You will see the possible line, starting draw, and two ways the payment could behave."
      >
        <Link className="button button-gold" href="#calculator">Open the HELOC calculator</Link>
        <Link className="button button-outline-light" href="/mortgage-options#equity">Compare equity options</Link>
      </PageHero>
      <section className="section section-cream anchor-target" id="calculator">
        <div className="shell"><HelocCalculator /></div>
      </section>
      <FinalCTA title="A HELOC may let you keep a good first mortgage, but it is not automatically the best choice." body="I can compare the flexible line with a fixed home-equity loan and a cash-out refinance using the amount, payment, and timeline that matter to you." />
    </PageShell>
  );
}
