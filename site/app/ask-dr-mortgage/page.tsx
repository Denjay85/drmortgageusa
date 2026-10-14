import type { Metadata } from "next";
import { PageHero, PageShell } from "../site-components";
import AskExperience from "./AskExperience";
import "./ask.css";

export const metadata: Metadata = {
  title: "Ask Dr. Mortgage",
  alternates: { canonical: "/ask-dr-mortgage" },
  description: "Ask Dennis Ross’s mortgage guide library a question. Find Florida homebuying, VA loan, self-employed and homeowner answers on DR. Mortgage USA.",
};

export default function AskMortgagePage() {
  return <PageShell>
    <PageHero eyebrow="The answer starts here" title="What’s on your mind?" body="Ask the mortgage question you’ve been trying to figure out." />
    <AskExperience />
  </PageShell>;
}
