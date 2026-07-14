"use client";

import Link from "next/link";
import { useMemo, useState, type CSSProperties } from "react";
import { saveMortgageScenario, type MortgageGoal } from "./scenario-store";

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const goals: Array<{ id: MortgageGoal; code: string; label: string; verb: string }> = [
  { id: "purchase", code: "01", label: "Buy a home", verb: "Purchase" },
  { id: "va", code: "VA", label: "Use my benefit", verb: "VA purchase" },
  { id: "fha", code: "FHA", label: "Explore FHA", verb: "FHA purchase" },
  { id: "refinance", code: "RF", label: "Refinance", verb: "Refinance" },
  { id: "equity", code: "EQ", label: "Use equity", verb: "Home equity" },
];

const pathCopy: Record<MortgageGoal, Array<{ name: string; fit: string; down: string; score: number }>> = {
  purchase: [
    { name: "Conventional", fit: "Flexible property and occupancy path", down: "3–5%+", score: 86 },
    { name: "FHA", fit: "Lower-down-payment comparison", down: "3.5%+", score: 76 },
    { name: "DPA pairing", fit: "Cash-to-close support review", down: "Varies", score: 64 },
  ],
  va: [
    { name: "VA purchase", fit: "Benefit-first financing path", down: "0% possible", score: 94 },
    { name: "VA with down payment", fit: "Funding-fee and payment tradeoff", down: "5–10%", score: 73 },
    { name: "Conventional", fit: "Useful control comparison", down: "3–5%+", score: 49 },
  ],
  fha: [
    { name: "FHA", fit: "Low-down-payment baseline", down: "3.5%+", score: 93 },
    { name: "Conventional", fit: "Compare mortgage insurance", down: "3–5%+", score: 70 },
    { name: "FHA + DPA", fit: "Layer cash-to-close assistance", down: "Varies", score: 62 },
  ],
  refinance: [
    { name: "Rate and term", fit: "Payment and break-even analysis", down: "Equity based", score: 88 },
    { name: "Cash out", fit: "Liquidity versus new payment", down: "Equity based", score: 67 },
    { name: "HELOC", fit: "Protect the first mortgage", down: "Equity based", score: 58 },
  ],
  equity: [
    { name: "HELOC", fit: "Flexible draw and repayment", down: "Equity based", score: 91 },
    { name: "Fixed equity loan", fit: "Predictable installment option", down: "Equity based", score: 72 },
    { name: "Cash-out refinance", fit: "One-loan comparison", down: "Equity based", score: 55 },
  ],
};

function payment(principal: number, annualRate: number) {
  const monthlyRate = annualRate / 100 / 12;
  const payments = 360;
  if (!monthlyRate) return principal / payments;
  return principal * (monthlyRate * Math.pow(1 + monthlyRate, payments)) /
    (Math.pow(1 + monthlyRate, payments) - 1);
}

export default function MortgageFlightDeck() {
  const [goal, setGoal] = useState<MortgageGoal>("purchase");
  const [homePrice, setHomePrice] = useState(400000);
  const [downPayment, setDownPayment] = useState(20000);
  const [rate, setRate] = useState(6.65);
  const [saved, setSaved] = useState(false);

  const result = useMemo(() => {
    const safeHomePrice = Math.max(0, homePrice);
    const safeDownPayment = Math.min(Math.max(0, downPayment), safeHomePrice);
    const downPercent = safeHomePrice ? safeDownPayment / safeHomePrice * 100 : 0;
    const principal = goal === "equity" ? safeDownPayment : Math.max(0, safeHomePrice - safeDownPayment);
    const principalInterest = goal === "equity" ? principal * rate / 100 / 12 : payment(principal, rate);
    const taxes = goal === "equity" ? 0 : safeHomePrice * 0.012 / 12;
    const insurance = goal === "equity" ? 0 : 200;
    const mortgageInsurance = goal === "equity" || goal === "va" || downPercent >= 20 ? 0 : goal === "fha" ? principal * 0.0055 / 12 : principal * 0.005 / 12;
    const total = principalInterest + taxes + insurance + mortgageInsurance;
    return { downPayment: safeDownPayment, downPercent, principal, principalInterest, taxes, insurance, mortgageInsurance, total };
  }, [goal, homePrice, downPayment, rate]);

  const activeGoal = goals.find((item) => item.id === goal) || goals[0];
  const toolHash = goal === "va" ? "va-purchase" : goal === "fha" ? "fha" : goal === "refinance" ? "refinance" : goal === "equity" ? "heloc" : "purchase";

  const keepScenario = () => {
    saveMortgageScenario({ goal, homePrice, downPayment: result.downPayment, rate, payment: result.total, savedAt: Date.now() });
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2200);
  };

  return (
    <section className={`flight-deck flight-deck-${goal}`} aria-labelledby="flight-deck-title">
      <div className="flight-deck-grid" aria-hidden="true" />
      <div className="flight-deck-heading">
        <div>
          <p className="eyebrow">Mortgage flight deck · live scenario</p>
          <h2 id="flight-deck-title">Move the numbers. Watch the financing paths reorganize.</h2>
        </div>
        <p>This is an educational planning model, not a quote or approval. It is designed to make the tradeoffs visible before a full application.</p>
      </div>

      <div className="flight-goals" role="tablist" aria-label="Choose a mortgage goal">
        {goals.map((item) => (
          <button type="button" role="tab" aria-selected={goal === item.id} className={goal === item.id ? "active" : ""} onClick={() => setGoal(item.id)} key={item.id}>
            <span>{item.code}</span><strong>{item.label}</strong>
          </button>
        ))}
      </div>

      <div className="flight-instrument-panel">
        <div className="flight-controls">
          <div className="flight-status"><span className="flight-live-dot" /> LIVE MODEL <b>{activeGoal.verb}</b></div>
          <div className="flight-number-grid">
            <label className="flight-number-field">
              <span><b>Home / property value</b><small>Enter the purchase price or current value</small></span>
              <div><i aria-hidden="true">$</i><input aria-label="Home or property value" type="number" min="0" step="1000" inputMode="numeric" value={homePrice} onChange={(event) => setHomePrice(Number(event.target.value))} /></div>
            </label>
            <label className="flight-number-field">
              <span><b>{goal === "equity" ? "Equity line / planned draw" : goal === "refinance" ? "Estimated equity position" : "Down payment"}</b><small>{result.downPercent.toFixed(1)}% of the property value</small></span>
              <div><i aria-hidden="true">$</i><input aria-label={goal === "equity" ? "Equity line or planned draw" : goal === "refinance" ? "Estimated equity position" : "Down payment"} type="number" min="0" step="1000" inputMode="numeric" value={downPayment} onChange={(event) => setDownPayment(Number(event.target.value))} /></div>
            </label>
            <label className="flight-number-field">
              <span><b>Interest-rate assumption</b><small>Use any rate you want to model</small></span>
              <div><input aria-label="Interest rate assumption" type="number" min="0" max="25" step="0.01" inputMode="decimal" value={rate} onChange={(event) => setRate(Number(event.target.value))} /><i aria-hidden="true">%</i></div>
            </label>
          </div>
          <div className="flight-actions">
            <button type="button" className="button button-gold" onClick={keepScenario}>{saved ? "Scenario saved ✓" : "Keep this scenario"}</button>
            <Link className="button button-outline-light" href={`/tools#${toolHash}`}>Open full calculator</Link>
          </div>
        </div>

        <div className="flight-result" aria-live="polite">
          <div className="flight-radar" aria-hidden="true"><i /><i /><i /><span /></div>
          <p>{goal === "equity" ? "Illustrative interest-only payment" : "Complete modeled payment"}</p>
          <strong key={Math.round(result.total)}>{money.format(result.total)}</strong>
          <small>{goal === "equity" ? "per month on the modeled initial draw · variable-rate risk applies" : "per month · principal, interest, estimated taxes, insurance and modeled MI"}</small>
          <div className="flight-payment-stack" aria-label="Payment composition">
            <span style={{ width: `${result.total ? result.principalInterest / result.total * 100 : 0}%` }} />
            <span style={{ width: `${result.total ? result.taxes / result.total * 100 : 0}%` }} />
            <span style={{ width: `${result.total ? result.insurance / result.total * 100 : 0}%` }} />
            <span style={{ width: `${result.total ? result.mortgageInsurance / result.total * 100 : 0}%` }} />
          </div>
          <div className="flight-legend"><span>P&amp;I {money.format(result.principalInterest)}</span><span>Taxes {money.format(result.taxes)}</span><span>Insurance {money.format(result.insurance)}</span><span>MI / fee {money.format(result.mortgageInsurance)}</span></div>
        </div>
      </div>

      <div className="flight-paths">
        <div className="flight-paths-intro"><span>Comparison stage</span><strong>Paths responding to your goal</strong><small>“Fit signal” is an interface guide, not underwriting or a recommendation.</small></div>
        {pathCopy[goal].map((path, index) => (
          <article style={{ "--path-score": `${path.score}%`, "--path-delay": `${index * 90}ms` } as CSSProperties} key={`${goal}-${path.name}`}>
            <div><span>0{index + 1}</span><strong>{path.name}</strong><small>{path.fit}</small></div>
            <div className="flight-path-meter"><i /></div>
            <b>{path.down}</b>
          </article>
        ))}
      </div>
    </section>
  );
}
