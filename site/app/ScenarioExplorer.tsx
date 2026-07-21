"use client";

import Link from "next/link";
import { useState } from "react";

const scenarios = [
  {
    id: "purchase",
    code: "01",
    tab: "Buy a home",
    title: "First home, next home, or relocation",
    eyebrow: "Purchase roadmap",
    headline: "Let's start with the payment you can live with, not the maximum someone will approve.",
    body: "Whether this is your first home, your next home, or a relocation, we will look at the monthly payment, cash needed, and timing of the move together.",
    questions: ["Your comfortable payment", "Your current home and timing", "Your cash and loan options"],
    primary: { label: "Explore purchase options", href: "/mortgage-options#first-time" },
    secondary: { label: "Check affordability", href: "/tools#affordability" },
  },
  {
    id: "va",
    code: "VA",
    tab: "VA benefit",
    title: "Using my VA benefit",
    eyebrow: "Veteran strategy",
    headline: "You earned the benefit. Let's make sure you know how to use it well.",
    body: "I will help you review entitlement, the possible funding fee, the full payment, appraisal questions, property condition, and offer timing from one veteran to another.",
    questions: ["Your entitlement", "Your full payment", "The property and offer"],
    primary: { label: "Explore VA financing", href: "/mortgage-options#va" },
    secondary: { label: "Run the VA calculator", href: "/tools#va-purchase" },
  },
  {
    id: "specialty",
    code: "SE",
    tab: "Complex income",
    title: "Self-employed or investing",
    eyebrow: "Income-path review",
    headline: "Your tax return is part of the story, but it may not be the whole story.",
    body: "We can compare conventional, bank-statement, DSCR, and other options based on how you earn, what the property earns, and how much cash you want to keep available.",
    questions: ["How you show income", "Cash you want to keep", "What the property earns"],
    primary: { label: "See specialty options", href: "/mortgage-options#specialty" },
    secondary: { label: "Model a DSCR scenario", href: "/tools#dscr" },
  },
  {
    id: "equity",
    code: "EQ",
    tab: "Home equity",
    title: "Using my home equity",
    eyebrow: "Equity comparison",
    headline: "You may be able to use your equity without replacing a good first mortgage.",
    body: "We will compare a HELOC, fixed home-equity loan, cash-out refinance, and traditional refinance based on the money you need, the payment you want, and how long you expect to carry it.",
    questions: ["How much equity is available", "Whether to keep the first mortgage", "Payment and rate changes"],
    primary: { label: "Review equity options", href: "/mortgage-options#equity" },
    secondary: { label: "Open the HELOC calculator", href: "/heloc-calculator" },
  },
];

export default function ScenarioExplorer() {
  const [activeId, setActiveId] = useState(scenarios[0].id);
  const active = scenarios.find((scenario) => scenario.id === activeId) || scenarios[0];

  return (
    <div className="scenario-explorer" data-interaction="scenario-explorer">
      <div className="scenario-tabs" role="tablist" aria-label="Choose a mortgage conversation">
        <p>Choose your conversation</p>
        {scenarios.map((scenario) => (
          <button
            type="button"
            role="tab"
            aria-selected={active.id === scenario.id}
            aria-controls="scenario-stage"
            className={active.id === scenario.id ? "active" : ""}
            onClick={() => setActiveId(scenario.id)}
            key={scenario.id}
          >
            <span>{scenario.code}</span>
            <strong>{scenario.tab}</strong>
            <i aria-hidden="true">→</i>
          </button>
        ))}
      </div>

      <div className="scenario-stage" id="scenario-stage" role="tabpanel" key={active.id}>
        <div className="scenario-visual" aria-hidden="true">
          <span className="scenario-orbit scenario-orbit-outer" />
          <span className="scenario-orbit scenario-orbit-inner" />
          <span className="scenario-axis scenario-axis-horizontal" />
          <span className="scenario-axis scenario-axis-vertical" />
          <div className="scenario-signal">
            <small>Active path</small>
            <strong>{active.code}</strong>
            <span>{active.title}</span>
          </div>
          <div className="scenario-pulse scenario-pulse-one" />
          <div className="scenario-pulse scenario-pulse-two" />
        </div>

        <div className="scenario-copy">
          <p className="eyebrow">{active.eyebrow}</p>
          <h3>{active.headline}</h3>
          <p>{active.body}</p>
          <div className="scenario-questions">
            {active.questions.map((question, index) => (
              <div key={question}>
                <span>0{index + 1}</span>
                <strong>{question}</strong>
              </div>
            ))}
          </div>
          <div className="scenario-actions">
            <Link className="button button-gold" href={active.primary.href}>{active.primary.label}</Link>
            <Link className="button button-outline-light" href={active.secondary.href}>{active.secondary.label}</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
