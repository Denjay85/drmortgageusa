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
    headline: "Start with the payment you can live with, not the maximum someone will approve.",
    body: "Build the complete payment and cash-to-close plan whether this is your first purchase, a move-up home, a relocation, or a purchase that depends on selling your current property.",
    questions: ["Comfortable payment", "Current home and timing", "Cash, proceeds, and program fit"],
    primary: { label: "Explore purchase options", href: "/mortgage-options#first-time" },
    secondary: { label: "Check affordability", href: "/tools#affordability" },
  },
  {
    id: "va",
    code: "VA",
    tab: "VA benefit",
    title: "Using my VA benefit",
    eyebrow: "Veteran strategy",
    headline: "Your benefit is powerful. The offer still needs a complete property and payment plan.",
    body: "Review entitlement, funding-fee status, taxes, insurance, appraisal questions, property condition, and offer timing with someone who understands the military path.",
    questions: ["Entitlement and fee", "Complete payment", "Property and offer"],
    primary: { label: "Explore VA financing", href: "/mortgage-options#va" },
    secondary: { label: "Run the VA calculator", href: "/tools#va-purchase" },
  },
  {
    id: "specialty",
    code: "SE",
    tab: "Complex income",
    title: "Self-employed or investing",
    eyebrow: "Income-path review",
    headline: "The tax return is part of the story. It is not always the only path worth reviewing.",
    body: "Compare conventional, bank-statement, DSCR, and other specialty routes around how income is documented, what the property earns, and what liquidity the plan requires.",
    questions: ["Income documentation", "Reserves and liquidity", "Property cash flow"],
    primary: { label: "See specialty options", href: "/mortgage-options#specialty" },
    secondary: { label: "Model a DSCR scenario", href: "/tools#dscr" },
  },
  {
    id: "equity",
    code: "EQ",
    tab: "Home equity",
    title: "Using my home equity",
    eyebrow: "Equity comparison",
    headline: "Protecting a good first mortgage can matter, but so can variable-rate risk.",
    body: "Compare a HELOC, fixed home-equity loan, cash-out refinance, and rate-and-term refinance around access, payment changes, total cost, and the time you expect to carry the balance.",
    questions: ["Available equity", "First-mortgage tradeoff", "Payment and rate risk"],
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
