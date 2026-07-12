"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { clearMortgageScenario, readMortgageScenario, scenarioEventName, type SavedMortgageScenario } from "./scenario-store";

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export default function ScenarioDock() {
  const [scenario, setScenario] = useState<SavedMortgageScenario | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => setScenario(readMortgageScenario()));

    const sync = () => {
      const next = readMortgageScenario();
      setScenario(next);
      if (next) setOpen(true);
    };

    window.addEventListener(scenarioEventName, sync);
    window.addEventListener("storage", sync);
    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener(scenarioEventName, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  if (!scenario) return null;

  return (
    <aside className={`scenario-dock ${open ? "open" : ""}`} aria-label="Saved mortgage scenario">
      <button className="scenario-dock-toggle" type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open}>
        <span className="flight-live-dot" /> <strong>Your live scenario</strong><b>{open ? "×" : money.format(scenario.payment)}</b>
      </button>
      {open ? (
        <div className="scenario-dock-body">
          <span>{scenario.goal.replace("-", " ")} · {scenario.rate.toFixed(2)}% assumption</span>
          <strong>{money.format(scenario.payment)}<small>/mo</small></strong>
          <div><span>{money.format(scenario.homePrice)} value</span><span>{money.format(scenario.downPayment)} down</span></div>
          <Link className="button button-gold button-small" href={`/tools#${scenario.goal === "va" ? "va-purchase" : scenario.goal === "equity" ? "heloc" : scenario.goal}`}>Continue in calculator</Link>
          <button className="scenario-dock-clear" type="button" onClick={() => { clearMortgageScenario(); setOpen(false); }}>Clear scenario</button>
        </div>
      ) : null}
    </aside>
  );
}
