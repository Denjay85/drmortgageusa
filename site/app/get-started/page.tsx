import type { Metadata } from "next";
import { PageShell } from "../site-components";
import PathFinder from "./PathFinder";

export const metadata: Metadata = {
  title: "Build My Mortgage Plan",
  alternates: { canonical: "/get-started" },
  description: "Answer a few simple questions and see the likely Florida mortgage conversation to have next.",
};

export default function GetStartedPage() {
  return (
    <PageShell>
      <section className="path-page">
        <div className="shell path-page-grid">
          <div className="path-page-copy">
            <p className="eyebrow">No credit check to start</p>
            <h2>You do not need to have the loan figured out before we talk.</h2>
            <p>Tell me what you are trying to do and I will point you toward the conversation that makes sense. This is not a prequalification, and I will not ask for sensitive financial information here.</p>
            <ul className="check-list"><li>No credit check to start</li><li>No Social Security number, bank data, or document upload</li><li>You choose whether I may email, call, or text</li><li>I can personally review the plan when your question becomes specific</li></ul>
          </div>
          <PathFinder />
        </div>
      </section>
    </PageShell>
  );
}
