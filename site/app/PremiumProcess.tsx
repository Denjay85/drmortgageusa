"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const steps = [
  {
    id: "goal",
    number: "01",
    tab: "Set the goal",
    eyebrow: "Your starting point",
    title: "Tell us what you are trying to make possible.",
    body: "Buying your first home, moving up, relocating, refinancing, or using equity all start with a different set of useful questions.",
    detail: "About 60 seconds",
  },
  {
    id: "plan",
    number: "02",
    tab: "Build the plan",
    eyebrow: "The working model",
    title: "Watch the numbers organize into a real mortgage path.",
    body: "Payment, cash to close, loan structure, assistance, documents, and timing come together in one readable working plan.",
    detail: "Complete payment view",
  },
  {
    id: "choice",
    number: "03",
    tab: "Choose the move",
    eyebrow: "Your decision",
    title: "Move forward only when the tradeoffs make sense.",
    body: "Save the scenario, ask Dennis to review it, or continue securely when the direction is clear. The application is not the first conversation.",
    detail: "Human review available",
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
        <p>Three decisions. One clear path.</p>
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
