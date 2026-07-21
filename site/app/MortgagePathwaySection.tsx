"use client";

import type { PointerEvent } from "react";
import ScenarioExplorer from "./ScenarioExplorer";

export default function MortgagePathwaySection() {
  const handlePointerMove = (event: PointerEvent<HTMLElement>) => {
    const bounds = event.currentTarget.getBoundingClientRect();
    const x = Math.min(1, Math.max(0, (event.clientX - bounds.left) / bounds.width));
    const y = Math.min(1, Math.max(0, (event.clientY - bounds.top) / bounds.height));

    event.currentTarget.style.setProperty("--path-x", `${x * 100}%`);
    event.currentTarget.style.setProperty("--path-y", `${y * 100}%`);
    event.currentTarget.style.setProperty("--path-shift-x", `${(x - 0.5) * 24}px`);
    event.currentTarget.style.setProperty("--path-shift-y", `${(y - 0.5) * 18}px`);
    event.currentTarget.style.setProperty("--path-shift-x-negative", `${(0.5 - x) * 24}px`);
    event.currentTarget.style.setProperty("--path-shift-y-negative", `${(0.5 - y) * 18}px`);
    event.currentTarget.style.setProperty("--path-shift-x-soft", `${(0.5 - x) * 16}px`);
    event.currentTarget.style.setProperty("--path-shift-y-soft", `${(0.5 - y) * 12}px`);
    event.currentTarget.style.setProperty("--path-tilt-x", `${(0.5 - y) * 1.2}deg`);
    event.currentTarget.style.setProperty("--path-tilt-y", `${(x - 0.5) * 1.5}deg`);
  };

  const resetPointer = (event: PointerEvent<HTMLElement>) => {
    event.currentTarget.style.setProperty("--path-x", "50%");
    event.currentTarget.style.setProperty("--path-y", "34%");
    event.currentTarget.style.setProperty("--path-shift-x", "0px");
    event.currentTarget.style.setProperty("--path-shift-y", "0px");
    event.currentTarget.style.setProperty("--path-shift-x-negative", "0px");
    event.currentTarget.style.setProperty("--path-shift-y-negative", "0px");
    event.currentTarget.style.setProperty("--path-shift-x-soft", "0px");
    event.currentTarget.style.setProperty("--path-shift-y-soft", "0px");
    event.currentTarget.style.setProperty("--path-tilt-x", "0deg");
    event.currentTarget.style.setProperty("--path-tilt-y", "0deg");
  };

  return (
    <section
      className="section path-section path-section-live"
      onPointerMove={handlePointerMove}
      onPointerLeave={resetPointer}
    >
      <div className="path-section-atmosphere" aria-hidden="true">
        <span className="path-field-grid" />
        <span className="path-route path-route-one" />
        <span className="path-route path-route-two" />
        <span className="path-route path-route-three" />
        <span className="path-ambient-ring path-ambient-ring-one" />
        <span className="path-ambient-ring path-ambient-ring-two" />
        <span className="path-marker path-marker-one"><i /> Purchase</span>
        <span className="path-marker path-marker-two"><i /> VA</span>
        <span className="path-marker path-marker-three"><i /> Income</span>
        <span className="path-marker path-marker-four"><i /> Equity</span>
      </div>

      <div className="shell path-section-shell">
        <div className="path-section-heading">
          <div>
            <p className="eyebrow">Start where you are</p>
            <h2>What are you trying to make possible?</h2>
            <p>
              Choose the situation that sounds most like yours. I will show you
              the questions worth asking and the tools that can help you answer them.
            </p>
          </div>
          <aside className="path-section-guide">
            <span><i /> Your starting point</span>
            <strong>Pick a goal and the conversation changes with you.</strong>
            <small>Explore buying, VA financing, self-employed income, or home equity.</small>
          </aside>
        </div>

        <ScenarioExplorer />
      </div>
    </section>
  );
}
