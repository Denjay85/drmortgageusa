import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell } from "../site-components";
import MortgageStudio from "./MortgageStudio";

export const metadata: Metadata = {
  title: "Mortgage Calculators & Payment Studio",
  alternates: { canonical: "/tools" },
  description: "Use ten interactive Florida mortgage calculators for purchase, affordability, FHA, refinance, rent vs. buy, VA, DSCR, fix and flip, and HELOC scenarios.",
};

export default function ToolsPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="The complete mortgage calculator studio"
        title="Choose how you want to finance it, then run that scenario."
        body="Purchase, affordability, FHA, refinance, rent vs. buy, VA purchase, VA refinance, DSCR, fix and flip, and HELOC tools are organized in one place without flattening them into the same generic calculator."
      >
        <Link className="button button-gold" href="#mortgage-studio">View all 10 calculators</Link>
        <Link className="button button-outline-light" href="#va-purchase">VA calculator</Link>
        <Link className="button button-outline-light" href="/contact">Review it with Dennis</Link>
      </PageHero>
      <section className="section calculator-suite-section anchor-target" id="calculator-suite">
        <div className="shell">
          <MortgageStudio />
        </div>
      </section>
      <FinalCTA title="A calculator answers one version of the question. A review compares the versions that fit your file." />
    </PageShell>
  );
}
