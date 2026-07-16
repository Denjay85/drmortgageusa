"use client";

import { useEffect, useMemo, useState } from "react";
import CalculatorNumberInput from "../CalculatorNumberInput";
import { readMortgageScenario } from "../scenario-store";

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function amortizedPayment(principal: number, annualRate: number, years: number) {
  const payments = years * 12;
  const monthlyRate = annualRate / 100 / 12;
  if (!payments) return 0;
  if (!monthlyRate) return principal / payments;
  return principal * (monthlyRate * Math.pow(1 + monthlyRate, payments)) /
    (Math.pow(1 + monthlyRate, payments) - 1);
}

export default function HelocCalculator() {
  const [homeValue, setHomeValue] = useState(500000);
  const [mortgageBalance, setMortgageBalance] = useState(285000);
  const [maxCltv, setMaxCltv] = useState(80);
  const [requestedLine, setRequestedLine] = useState(75000);
  const [drawAmount, setDrawAmount] = useState(50000);
  const [rate, setRate] = useState(8.25);
  const [repaymentYears, setRepaymentYears] = useState(20);

  useEffect(() => {
    const saved = readMortgageScenario();
    if (!saved || saved.goal !== "equity") return;
    const frame = window.requestAnimationFrame(() => {
      setHomeValue(saved.homePrice);
      setRequestedLine(saved.downPayment);
      setDrawAmount(saved.downPayment);
      setRate(saved.rate);
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  const result = useMemo(() => {
    const equity = Math.max(0, homeValue - mortgageBalance);
    const lendableEquity = Math.max(0, homeValue * (maxCltv / 100) - mortgageBalance);
    const modeledLine = Math.min(Math.max(0, requestedLine), lendableEquity);
    const modeledDraw = Math.min(Math.max(0, drawAmount), modeledLine);
    const interestOnly = modeledDraw * (rate / 100) / 12;
    const amortizing = amortizedPayment(modeledDraw, rate, repaymentYears);
    const combinedBalance = mortgageBalance + modeledLine;
    const resultingCltv = homeValue ? combinedBalance / homeValue * 100 : 0;
    return { equity, lendableEquity, modeledLine, modeledDraw, interestOnly, amortizing, resultingCltv };
  }, [homeValue, mortgageBalance, maxCltv, requestedLine, drawAmount, rate, repaymentYears]);

  return (
    <div className="tool-layout heloc-layout">
      <section className="calculator-controls" aria-labelledby="heloc-inputs-title">
        <div className="tool-card-heading">
          <span>Home equity inputs</span>
          <h2 id="heloc-inputs-title">Model the available line.</h2>
          <p>Start with an estimated value and current first-mortgage balance.</p>
        </div>

        <div className="field-grid">
          <label className="field">
            <span>Estimated home value</span>
            <CalculatorNumberInput min="50000" step="5000" inputMode="numeric" value={homeValue} onValueChange={setHomeValue} />
          </label>
          <label className="field">
            <span>Mortgage balance</span>
            <CalculatorNumberInput min="0" step="5000" inputMode="numeric" value={mortgageBalance} onValueChange={setMortgageBalance} />
          </label>
          <label className="field">
            <span>Requested credit line</span>
            <CalculatorNumberInput min="0" step="5000" inputMode="numeric" value={requestedLine} onValueChange={setRequestedLine} />
          </label>
          <label className="field">
            <span>Planned initial draw</span>
            <CalculatorNumberInput min="0" step="5000" inputMode="numeric" value={drawAmount} onValueChange={setDrawAmount} />
          </label>
        </div>

        <label className="field range-field">
          <span><b>Illustrative variable rate</b><strong>{rate.toFixed(2)}%</strong></span>
          <input type="range" min="4" max="18" step="0.05" value={rate} onChange={(event) => setRate(Number(event.target.value))} />
        </label>

        <div className="field-grid">
          <label className="field">
            <span>Modeled maximum combined LTV</span>
            <select value={maxCltv} onChange={(event) => setMaxCltv(Number(event.target.value))}>
              <option value="70">70%</option>
              <option value="75">75%</option>
              <option value="80">80%</option>
              <option value="85">85%</option>
              <option value="90">90%</option>
            </select>
          </label>
          <label className="field">
            <span>Repayment illustration</span>
            <select value={repaymentYears} onChange={(event) => setRepaymentYears(Number(event.target.value))}>
              <option value="10">10 years</option>
              <option value="15">15 years</option>
              <option value="20">20 years</option>
            </select>
          </label>
        </div>
        <p className="form-note">The combined-loan-to-value limit is an editable modeling assumption, not a program promise. Property value, credit, income, lien position, and lender guidelines affect eligibility.</p>
      </section>

      <section className="calculator-result" aria-live="polite" aria-labelledby="heloc-result-title">
        <div className="result-topline">
          <span>Illustrative HELOC scenario</span>
          <small>Not a quote or approval</small>
        </div>

        <div className="heloc-available">
          <span>Modeled available line</span>
          <strong id="heloc-result-title">{money.format(result.modeledLine)}</strong>
          <small>Based on a {maxCltv}% maximum combined LTV assumption</small>
        </div>

        <div className="equity-meter" aria-label={`${result.resultingCltv.toFixed(1)} percent modeled combined loan-to-value`}>
          <span style={{ width: `${Math.min(100, result.resultingCltv)}%` }} />
        </div>

        <dl className="result-breakdown heloc-breakdown">
          <div><dt>Total estimated equity</dt><dd>{money.format(result.equity)}</dd></div>
          <div><dt>Equity inside modeled limit</dt><dd>{money.format(result.lendableEquity)}</dd></div>
          <div><dt>Modeled initial draw</dt><dd>{money.format(result.modeledDraw)}</dd></div>
          <div><dt>Interest-only payment at {rate.toFixed(2)}%</dt><dd>{money.format(result.interestOnly)}/mo</dd></div>
          <div><dt>{repaymentYears}-year amortizing illustration</dt><dd>{money.format(result.amortizing)}/mo</dd></div>
        </dl>

        <div className="heloc-caution">
          <strong>Why both payments?</strong>
          <p>Many HELOCs have a draw period followed by repayment. Rates are commonly variable, so the actual payment can change. Review the note, margin, index, fees, draw period, and repayment terms before deciding.</p>
        </div>
      </section>
    </div>
  );
}
