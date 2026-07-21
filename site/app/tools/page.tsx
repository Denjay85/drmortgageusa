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
        eyebrow="Run the numbers your way"
        title="Choose the question you are trying to answer."
        body="Buying, refinancing, using a VA benefit, comparing rent with ownership, or investing all require different math. Pick the calculator that matches your situation and put in the numbers you know."
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
      <FinalCTA title="A calculator gives you a starting point. It cannot see your full financial picture." body="Send me the scenario and I will help you check the assumptions, compare the options, and see what deserves a closer look." />
    </PageShell>
  );
}
