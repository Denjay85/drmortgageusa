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
            <p className="eyebrow">Start small. Share more only when it makes sense.</p>
            <h2>Know the path before the application.</h2>
            <p>This is an educational starting point, not a prequalification. It helps Dennis understand the conversation you need without collecting sensitive financial data.</p>
            <ul className="check-list"><li>No credit check to start</li><li>No SSN, bank data, or document upload</li><li>Separate email, call, and text permissions</li><li>Human review when the question becomes specific</li></ul>
          </div>
          <PathFinder />
        </div>
      </section>
    </PageShell>
  );
}
