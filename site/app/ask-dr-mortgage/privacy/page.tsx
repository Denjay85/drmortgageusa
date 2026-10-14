import type { Metadata } from "next";
import { PageHero, PageShell } from "../../site-components";
import "../ask.css";

export const metadata: Metadata = {
  title: "Ask Dr. Mortgage Privacy",
  alternates: { canonical: "/ask-dr-mortgage/privacy" },
  description: "How Ask Dr. Mortgage saves questions, resumes conversations and handles deletion. Guidance from Dennis Ross’s mortgage library.",
};

export default function AskPrivacyPage() {
  return <PageShell>
    <PageHero eyebrow="Ask Dr. Mortgage" title="Your questions and privacy" body="The answer tool searches Dennis’s guides. It is not a live conversation with Dennis, a loan application, an approval, or a rate quote." />
    <section className="section"><div className="shell ask-privacy-copy">
      <h2>What is saved</h2>
      <p>The interface is hosted on DR. Mortgage USA. Questions are processed by the same guide-backed answer service used by the original Ask Dr. Mortgage tool. Questions, answers, article links, feedback and article clicks are stored by that service to improve the library. This release does not send your questions to an external AI answer service.</p>
      <p>Please do not enter names, account numbers, Social Security numbers or documents. Common email addresses, phone numbers and account-number patterns are removed before questions are stored. This automatic filter cannot identify every private detail.</p>
      <h2>Returning to a conversation</h2>
      <p>A secure browser cookie gives this browser access to its conversation for seven days. Someone using the same browser may see that conversation. The cookie is not an advertising tracker.</p>
      <h2>Deleting and keeping records</h2>
      <p>Use “Delete conversation” in the question panel to remove the current conversation, its feedback and associated activity from the live answer-service database. Starting a new conversation does not delete earlier records. The delete control works while this browser still has access.</p>
      <p>Raw questions and activity have a 90-day retention period. Expired records are removed when the answer service next processes a question or opens the research desk. Editorial briefs, reviewed wording and anonymous topic summaries may be kept separately to maintain the blog; deleting a conversation does not remove those editorial materials.</p>
      <p>Dennis’s research and wording tools require owner access. Owner testing is separated from visitor traffic in research reports.</p>
      <p>For a privacy question, use the Call Dennis link in the site header. See the <a href="/privacy">DR. Mortgage USA privacy policy</a> for the main website.</p>
      <p><a href="/ask-dr-mortgage">Back to Ask Dr. Mortgage →</a></p>
    </div></section>
  </PageShell>;
}
