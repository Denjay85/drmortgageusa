"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const steps = [
  {
    id: "goal",
    number: "01",
    tab: "Tell me the goal",
    eyebrow: "Start with what you know",
    title: "Tell me what you are trying to do, even if the plan is still fuzzy.",
    body: "First home, next home, refinance, or home equity, each conversation starts differently. A few quick answers help us start in the right place.",
    detail: "About 60 seconds",
  },
  {
    id: "plan",
    number: "02",
    tab: "See the numbers",
    eyebrow: "Make the tradeoffs visible",
    title: "See what the payment and upfront cash could really look like.",
    body: "We will bring the payment, cash needed, possible assistance, documents, and timing into one view you can actually use.",
    detail: "Your numbers in one place",
  },
  {
    id: "choice",
    number: "03",
    tab: "Decide what is next",
    eyebrow: "No pressure to apply",
    title: "Move forward when the numbers make sense to you.",
    body: "Save the scenario, ask me to review it, or open the secure application when you are ready. You do not have to apply just to ask a question.",
    detail: "Dennis can review it with you",
  },
];

export default function PremiumProcess() {
  const [activeIndex, setActiveIndex] = useState(0);
  const active = steps[activeIndex];

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const timer = window.setInterval(() => {
      setActiveIndex((current) => (current + 1) % steps.length);
    }, 6200);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="premium-process" data-interaction="premium-process">
      <div className="premium-process-tabs" role="tablist" aria-label="Mortgage planning steps">
        <p>Start simple. Build from there.</p>
        {steps.map((step, index) => (
          <button
            type="button"
            role="tab"
            aria-selected={activeIndex === index}
            aria-controls="premium-process-stage"
            className={activeIndex === index ? "active" : ""}
            onClick={() => setActiveIndex(index)}
            key={step.id}
          >
            <span>{step.number}</span>
            <strong>{step.tab}</strong>
            <i aria-hidden="true" />
          </button>
        ))}
      </div>

      <div className="premium-process-stage" id="premium-process-stage" role="tabpanel" key={active.id}>
        <div className="premium-process-copy">
          <p className="eyebrow">{active.eyebrow}</p>
          <h3>{active.title}</h3>
          <p>{active.body}</p>
          <div className="premium-process-actions">
            <Link className="button button-gold" href="/get-started">Build my mortgage plan</Link>
            <span>{active.detail}</span>
          </div>
        </div>

        <div className={`premium-process-visual visual-${active.id}`} aria-hidden="true">
          <div className="process-visual-orbit orbit-one" />
          <div className="process-visual-orbit orbit-two" />
          <div className="process-visual-core">
            <small>Active step</small>
            <strong>{active.number}</strong>
            <span>{active.tab}</span>
          </div>
          <div className="process-visual-bars">
            <i /><i /><i /><i />
          </div>
          <div className="process-visual-signal" />
        </div>
      </div>

      <div className="premium-process-progress" aria-hidden="true">
        {steps.map((step, index) => <i className={index <= activeIndex ? "active" : ""} key={step.id} />)}
      </div>
    </div>
  );
}
