import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell } from "../site-components";
import FaqLibrary from "./FaqLibrary";

export const metadata: Metadata = {
  title: "Florida Mortgage FAQ",
  description:
    "Search clear Florida mortgage answers about payments, cash to close, credit, VA, FHA, USDA, self-employment, closing, HELOCs, and investing.",
};

export default function FaqPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Mortgage FAQ"
        title="The question should get easier before the application gets longer."
        body="Search practical answers, understand what depends on the actual file, and move to a calculator or conversation only when it helps."
      >
        <Link className="button button-gold" href="#faq-library">Search the answers</Link>
        <Link className="button button-outline-light" href="/contact">Ask Dennis directly</Link>
      </PageHero>
      <section className="section section-cream faq-library-section anchor-target" id="faq-library">
        <div className="shell">
          <FaqLibrary />
        </div>
      </section>
      <FinalCTA
        title="The FAQ can explain the framework. Your numbers determine the path."
        body="Organize the basics first, then decide whether a human review or secure application makes sense."
      />
    </PageShell>
  );
}
