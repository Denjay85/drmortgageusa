import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell } from "../site-components";
import FaqLibrary from "./FaqLibrary";

export const metadata: Metadata = {
  title: "Florida Mortgage FAQ",
  alternates: { canonical: "/faq" },
  description:
    "Search clear Florida mortgage answers about payments, cash to close, credit, VA, FHA, USDA, self-employment, closing, HELOCs, and investing.",
};

export default function FaqPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Mortgage FAQ"
        title="Ask the question you think you should already know the answer to."
        body="You are not supposed to know all of this already. Search for a plain-language answer, see what depends on your actual situation, and reach out when the general answer is not enough."
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
        title="The FAQ can explain the general rule. Your situation gives it meaning."
        body="If the answer still leaves you wondering what to do, send me the question and I will help you find the right next step."
      />
    </PageShell>
  );
}
