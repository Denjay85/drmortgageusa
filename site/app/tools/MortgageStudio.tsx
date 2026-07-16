"use client";

import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import HelocCalculator from "./HelocCalculator";
import CalculatorNumberInput from "../CalculatorNumberInput";
import { readMortgageScenario } from "../scenario-store";
import { submitLead } from "../lead-client";

type Mode =
  | "purchase"
  | "affordability"
  | "fha"
  | "refinance"
  | "rent-buy"
  | "va-purchase"
  | "va-refinance"
  | "dscr"
  | "fix-flip"
  | "heloc";

type LoanType = "Conventional" | "FHA" | "VA" | "USDA";

const modes: Array<{ id: Mode; short: string; label: string; family: string }> = [
  { id: "purchase", short: "P", label: "Purchase", family: "Homebuyer" },
  { id: "affordability", short: "A", label: "Affordability", family: "Homebuyer" },
  { id: "fha", short: "FHA", label: "FHA Purchase", family: "Homebuyer" },
  { id: "refinance", short: "R", label: "Refinance", family: "Homeowner" },
  { id: "rent-buy", short: "R/B", label: "Rent vs. Buy", family: "Planning" },
  { id: "va-purchase", short: "VA", label: "VA Purchase", family: "Veteran" },
  { id: "va-refinance", short: "IRRRL", label: "VA Refinance", family: "Veteran" },
  { id: "dscr", short: "DSCR", label: "DSCR", family: "Investor" },
  { id: "fix-flip", short: "F&F", label: "Fix & Flip", family: "Investor" },
  { id: "heloc", short: "EQ", label: "HELOC", family: "Homeowner" },
];

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function monthlyPayment(principal: number, annualRate: number, years: number) {
  const payments = Math.max(1, years * 12);
  const monthlyRate = annualRate / 100 / 12;
  if (!monthlyRate) return principal / payments;
  return principal * (monthlyRate * Math.pow(1 + monthlyRate, payments)) /
    (Math.pow(1 + monthlyRate, payments) - 1);
}

function remainingBalance(principal: number, annualRate: number, years: number, monthsPaid: number) {
  const payment = monthlyPayment(principal, annualRate, years);
  const monthlyRate = annualRate / 100 / 12;
  const months = Math.min(years * 12, Math.max(0, monthsPaid));
  if (!monthlyRate) return Math.max(0, principal - payment * months);
  return Math.max(
    0,
    principal * Math.pow(1 + monthlyRate, months) -
      payment * (Math.pow(1 + monthlyRate, months) - 1) / monthlyRate,
  );
}

function loanFeeRate(type: LoanType) {
  if (type === "FHA") return 1.75;
  if (type === "VA") return 2.15;
  if (type === "USDA") return 1;
  return 0;
}

function annualInsuranceRate(type: LoanType, ltv: number, years: number) {
  if (type === "VA") return 0;
  if (type === "USDA") return 0.35;
  if (type === "Conventional") return ltv > 80 ? 0.5 : 0;
  if (years <= 15) return ltv <= 90 ? 0.15 : 0.4;
  return ltv <= 95 ? 0.5 : 0.55;
}

function vaPurchaseFeeRate(downPercent: number, firstUse: boolean, exempt: boolean) {
  if (exempt) return 0;
  if (downPercent >= 10) return 1.25;
  if (downPercent >= 5) return 1.5;
  return firstUse ? 2.15 : 3.3;
}

function NumberField({
  label,
  value,
  onChange,
  min = 0,
  step = 1,
  help,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  step?: number;
  help?: string;
}) {
  return (
    <label className="field studio-field">
      <span>{label}</span>
      <CalculatorNumberInput
        value={value}
        min={min}
        step={step}
        inputMode={step < 1 ? "decimal" : "numeric"}
        onValueChange={onChange}
      />
      {help ? <small>{help}</small> : null}
    </label>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string | number;
  onChange: (value: string) => void;
  options: Array<{ value: string | number; label: string }>;
}) {
  return (
    <label className="field studio-field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option value={option.value} key={option.value}>{option.label}</option>
        ))}
      </select>
    </label>
  );
}

function ToggleField({
  checked,
  onChange,
  label,
  help,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  help?: string;
}) {
  return (
    <label className="studio-toggle">
      <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
      <span><strong>{label}</strong>{help ? <small>{help}</small> : null}</span>
    </label>
  );
}

function AnimatedValue({ value }: { value: string }) {
  const match = value.match(/^([^0-9-]*)(-?[0-9,.]+)(.*)$/);
  const target = match ? Number(match[2].replace(/,/g, "")) : Number.NaN;
  const previous = useRef(Number.isFinite(target) ? target : 0);
  const [display, setDisplay] = useState(Number.isFinite(target) ? target : 0);

  useEffect(() => {
    if (!Number.isFinite(target)) return;
    const from = previous.current;
    const difference = target - from;
    const started = performance.now();
    const duration = 420;
    let frame = 0;
    const animate = (time: number) => {
      const progress = Math.min(1, (time - started) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(from + difference * eased);
      if (progress < 1) frame = window.requestAnimationFrame(animate);
      else previous.current = target;
    };
    frame = window.requestAnimationFrame(animate);
    return () => window.cancelAnimationFrame(frame);
  }, [target]);

  if (!match || !Number.isFinite(target)) return <>{value}</>;
  const decimals = match[2].includes(".") ? match[2].split(".")[1].length : 0;
  const formatted = display.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  return <>{match[1]}{formatted}{match[3]}</>;
}

function ResultPanel({
  eyebrow,
  label,
  value,
  metrics,
  note,
  badge,
}: {
  eyebrow: string;
  label: string;
  value: string;
  metrics: Array<{ label: string; value: string }>;
  note: string;
  badge?: string;
}) {
  return (
    <section className="studio-result" aria-live="polite" aria-label={`${label}: ${value}`}>
      <div className="studio-result-radar" aria-hidden="true"><i /><i /><span /></div>
      <div className="result-topline">
        <span>{eyebrow}</span>
        <small>Educational estimate</small>
      </div>
      <div className="studio-primary-result">
        <span>{label}</span>
        <strong><AnimatedValue value={value} /></strong>
        {badge ? <small className="studio-result-badge">{badge}</small> : null}
      </div>
      <dl className="studio-metrics">
        {metrics.map((metric) => (
          <div key={metric.label}><dt>{metric.label}</dt><dd><AnimatedValue value={metric.value} /></dd></div>
        ))}
      </dl>
      <p className="studio-result-note">{note}</p>
    </section>
  );
}

function ScenarioLayout({
  eyebrow,
  title,
  description,
  children,
  result,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
  result: ReactNode;
}) {
  return (
    <div className="studio-scenario-layout">
      <section className="studio-controls" aria-label={title}>
        <div className="tool-card-heading">
          <span>{eyebrow}</span>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
        <div className="studio-field-grid">{children}</div>
      </section>
      {result}
    </div>
  );
}

function PurchaseCalculator() {
  const [homePrice, setHomePrice] = useState(400000);
  const [downPayment, setDownPayment] = useState(20000);
  const [loanType, setLoanType] = useState<LoanType>("Conventional");
  const [years, setYears] = useState(30);
  const [rate, setRate] = useState(6.65);
  const [taxes, setTaxes] = useState(4800);
  const [insurance, setInsurance] = useState(2400);
  const [hoa, setHoa] = useState(0);

  useEffect(() => {
    const saved = readMortgageScenario();
    if (!saved || !["purchase", "va", "fha"].includes(saved.goal)) return;
    const frame = window.requestAnimationFrame(() => {
      setHomePrice(saved.homePrice);
      setDownPayment(saved.downPayment);
      setRate(saved.rate);
      if (saved.goal === "va") setLoanType("VA");
      if (saved.goal === "fha") setLoanType("FHA");
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  const result = useMemo(() => {
    const baseLoan = Math.max(0, homePrice - downPayment);
    const downPercent = homePrice ? downPayment / homePrice * 100 : 0;
    const feeRate = loanFeeRate(loanType);
    const financedFee = baseLoan * feeRate / 100;
    const totalLoan = baseLoan + financedFee;
    const ltv = homePrice ? baseLoan / homePrice * 100 : 0;
    const miRate = annualInsuranceRate(loanType, ltv, years);
    const pi = monthlyPayment(totalLoan, rate, years);
    const monthlyMi = baseLoan * miRate / 100 / 12;
    const total = pi + taxes / 12 + insurance / 12 + hoa + monthlyMi;
    return { baseLoan, totalLoan, downPercent, feeRate, financedFee, miRate, pi, monthlyMi, total };
  }, [homePrice, downPayment, loanType, years, rate, taxes, insurance, hoa]);

  return (
    <ScenarioLayout
      eyebrow="Purchase payment"
      title="Compare the complete monthly payment."
      description="Change the financing path and see the fee, mortgage-insurance, and payment assumptions update together."
      result={<ResultPanel
        eyebrow={`${loanType} purchase scenario`}
        label="Estimated monthly payment"
        value={money.format(result.total)}
        badge={`${result.downPercent.toFixed(1)}% down`}
        metrics={[
          { label: "Principal & interest", value: money.format(result.pi) },
          { label: "Taxes + insurance + HOA", value: money.format(taxes / 12 + insurance / 12 + hoa) },
          { label: "Estimated monthly MI / fee", value: money.format(result.monthlyMi) },
          { label: "Base loan", value: money.format(result.baseLoan) },
          { label: "Financed upfront fee", value: money.format(result.financedFee) },
          { label: "Modeled total loan", value: money.format(result.totalLoan) },
        ]}
        note="Loan-program fees and mortgage insurance are modeled from common current assumptions. Use the dedicated FHA and VA calculators for their program-specific inputs."
      />}
    >
      <NumberField label="Home price" value={homePrice} onChange={setHomePrice} step={5000} min={50000} />
      <NumberField label="Down payment" value={downPayment} onChange={setDownPayment} step={1000} />
      <SelectField label="Loan type" value={loanType} onChange={(value) => setLoanType(value as LoanType)} options={[
        { value: "Conventional", label: "Conventional" },
        { value: "FHA", label: "FHA" },
        { value: "VA", label: "VA, first-use fee assumption" },
        { value: "USDA", label: "USDA" },
      ]} />
      <SelectField label="Loan term" value={years} onChange={(value) => setYears(Number(value))} options={[
        { value: 30, label: "30 years" }, { value: 20, label: "20 years" }, { value: 15, label: "15 years" },
      ]} />
      <NumberField label="Interest rate (%)" value={rate} onChange={setRate} step={0.05} />
      <NumberField label="Property tax (annual)" value={taxes} onChange={setTaxes} step={100} />
      <NumberField label="Home insurance (annual)" value={insurance} onChange={setInsurance} step={100} />
      <NumberField label="HOA fees (monthly)" value={hoa} onChange={setHoa} step={25} />
    </ScenarioLayout>
  );
}

function AffordabilityCalculator() {
  const [income, setIncome] = useState(9000);
  const [debts, setDebts] = useState(800);
  const [targetDti, setTargetDti] = useState(43);
  const [downPercent, setDownPercent] = useState(5);
  const [loanType, setLoanType] = useState<LoanType>("Conventional");
  const [rate, setRate] = useState(6.65);
  const [years, setYears] = useState(30);
  const [taxRate, setTaxRate] = useState(1.2);
  const [insurance, setInsurance] = useState(2400);
  const [hoa, setHoa] = useState(0);

  const result = useMemo(() => {
    const maxHousing = Math.max(0, income * targetDti / 100 - debts);
    const paymentForPrice = (price: number) => {
      const down = price * downPercent / 100;
      const baseLoan = price - down;
      const totalLoan = baseLoan * (1 + loanFeeRate(loanType) / 100);
      const mi = baseLoan * annualInsuranceRate(loanType, 100 - downPercent, years) / 100 / 12;
      return monthlyPayment(totalLoan, rate, years) + price * taxRate / 100 / 12 + insurance / 12 + hoa + mi;
    };
    let low = 0;
    let high = 3000000;
    for (let index = 0; index < 70; index += 1) {
      const middle = (low + high) / 2;
      if (paymentForPrice(middle) <= maxHousing) low = middle;
      else high = middle;
    }
    const price = Math.max(0, low);
    const down = price * downPercent / 100;
    const payment = paymentForPrice(price);
    return { maxHousing, price, down, payment, backEndDti: income ? (payment + debts) / income * 100 : 0 };
  }, [income, debts, targetDti, downPercent, loanType, rate, years, taxRate, insurance, hoa]);

  return (
    <ScenarioLayout
      eyebrow="Affordability"
      title="Work backward from income and debts."
      description="Set a target debt-to-income ratio and financing path to estimate the purchase price supported by that monthly housing budget."
      result={<ResultPanel
        eyebrow={`${loanType} affordability scenario`}
        label="Modeled home price"
        value={money.format(result.price)}
        badge={`${targetDti}% target total DTI`}
        metrics={[
          { label: "Maximum housing budget", value: `${money.format(result.maxHousing)}/mo` },
          { label: "Estimated payment at result", value: `${money.format(result.payment)}/mo` },
          { label: "Estimated down payment", value: money.format(result.down) },
          { label: "Modeled total DTI", value: `${result.backEndDti.toFixed(1)}%` },
        ]}
        note="This is a planning ceiling, not an approval or a recommended comfort level. Income treatment, credit, reserves, property, taxes, insurance, and program rules can materially change the result."
      />}
    >
      <NumberField label="Gross monthly household income" value={income} onChange={setIncome} step={250} />
      <NumberField label="Monthly debts" value={debts} onChange={setDebts} step={50} help="Auto loans, cards, student loans, support, and other qualifying debts." />
      <NumberField label="Target total DTI (%)" value={targetDti} onChange={setTargetDti} step={1} />
      <NumberField label="Down payment (%)" value={downPercent} onChange={setDownPercent} step={0.5} />
      <SelectField label="Loan type" value={loanType} onChange={(value) => setLoanType(value as LoanType)} options={[
        { value: "Conventional", label: "Conventional" }, { value: "FHA", label: "FHA" },
        { value: "VA", label: "VA" }, { value: "USDA", label: "USDA" },
      ]} />
      <SelectField label="Loan term" value={years} onChange={(value) => setYears(Number(value))} options={[
        { value: 30, label: "30 years" }, { value: 15, label: "15 years" },
      ]} />
      <NumberField label="Interest rate (%)" value={rate} onChange={setRate} step={0.05} />
      <NumberField label="Property-tax assumption (%)" value={taxRate} onChange={setTaxRate} step={0.05} />
      <NumberField label="Home insurance (annual)" value={insurance} onChange={setInsurance} step={100} />
      <NumberField label="HOA fees (monthly)" value={hoa} onChange={setHoa} step={25} />
    </ScenarioLayout>
  );
}

function FhaCalculator() {
  const [price, setPrice] = useState(350000);
  const [downPercent, setDownPercent] = useState(3.5);
  const [rate, setRate] = useState(6.25);
  const [years, setYears] = useState(30);
  const [taxes, setTaxes] = useState(4200);
  const [insurance, setInsurance] = useState(2400);
  const [hoa, setHoa] = useState(0);

  useEffect(() => {
    const saved = readMortgageScenario();
    if (!saved || saved.goal !== "fha") return;
    const frame = window.requestAnimationFrame(() => {
      setPrice(saved.homePrice);
      setDownPercent(saved.homePrice ? saved.downPayment / saved.homePrice * 100 : 0);
      setRate(saved.rate);
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  const result = useMemo(() => {
    const down = price * downPercent / 100;
    const baseLoan = Math.max(0, price - down);
    const upfrontMip = baseLoan * 0.0175;
    const totalLoan = baseLoan + upfrontMip;
    const mipRate = annualInsuranceRate("FHA", 100 - downPercent, years);
    const monthlyMip = baseLoan * mipRate / 100 / 12;
    const pi = monthlyPayment(totalLoan, rate, years);
    const total = pi + monthlyMip + taxes / 12 + insurance / 12 + hoa;
    return { down, baseLoan, upfrontMip, totalLoan, mipRate, monthlyMip, pi, total };
  }, [price, downPercent, rate, years, taxes, insurance, hoa]);

  return (
    <ScenarioLayout
      eyebrow="FHA purchase"
      title="See FHA financing as its own scenario."
      description="The calculator separates the base loan, financed upfront mortgage-insurance premium, annual MIP, and complete monthly payment."
      result={<ResultPanel
        eyebrow="FHA payment scenario"
        label="Estimated monthly payment"
        value={money.format(result.total)}
        badge={`${result.mipRate.toFixed(2)}% modeled annual MIP`}
        metrics={[
          { label: "Down payment", value: money.format(result.down) },
          { label: "Base FHA loan", value: money.format(result.baseLoan) },
          { label: "Financed upfront MIP (1.75%)", value: money.format(result.upfrontMip) },
          { label: "Total modeled loan", value: money.format(result.totalLoan) },
          { label: "Principal & interest", value: `${money.format(result.pi)}/mo` },
          { label: "Estimated monthly MIP", value: `${money.format(result.monthlyMip)}/mo` },
        ]}
        note="HUD’s 1.75% upfront MIP and common annual MIP bands are modeled. High-balance loans, loan term, LTV, case timing, and program exceptions can change the premium."
      />}
    >
      <NumberField label="Home price" value={price} onChange={setPrice} step={5000} min={50000} />
      <NumberField label="Down payment (%)" value={downPercent} onChange={setDownPercent} step={0.5} />
      <NumberField label="Interest rate (%)" value={rate} onChange={setRate} step={0.05} />
      <SelectField label="Loan term" value={years} onChange={(value) => setYears(Number(value))} options={[
        { value: 30, label: "30 years" }, { value: 15, label: "15 years" },
      ]} />
      <NumberField label="Property tax (annual)" value={taxes} onChange={setTaxes} step={100} />
      <NumberField label="Home insurance (annual)" value={insurance} onChange={setInsurance} step={100} />
      <NumberField label="HOA fees (monthly)" value={hoa} onChange={setHoa} step={25} />
    </ScenarioLayout>
  );
}

function RefinanceCalculator() {
  const [propertyValue, setPropertyValue] = useState(500000);
  const [balance, setBalance] = useState(320000);
  const [currentRate, setCurrentRate] = useState(7.25);
  const [remainingYears, setRemainingYears] = useState(27);
  const [newRate, setNewRate] = useState(6.25);
  const [newYears, setNewYears] = useState(30);
  const [closingCosts, setClosingCosts] = useState(6500);
  const [cashOut, setCashOut] = useState(0);

  useEffect(() => {
    const saved = readMortgageScenario();
    if (!saved || saved.goal !== "refinance") return;
    const frame = window.requestAnimationFrame(() => {
      setPropertyValue(saved.homePrice);
      setBalance(Math.max(0, saved.homePrice - saved.downPayment));
      setNewRate(saved.rate);
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  const result = useMemo(() => {
    const currentPi = monthlyPayment(balance, currentRate, remainingYears);
    const newLoan = balance + closingCosts + cashOut;
    const newPi = monthlyPayment(newLoan, newRate, newYears);
    const monthlySavings = currentPi - newPi;
    const breakEven = monthlySavings > 0 ? closingCosts / monthlySavings : 0;
    const ltv = propertyValue ? newLoan / propertyValue * 100 : 0;
    return { currentPi, newLoan, newPi, monthlySavings, breakEven, ltv };
  }, [propertyValue, balance, currentRate, remainingYears, newRate, newYears, closingCosts, cashOut]);

  return (
    <ScenarioLayout
      eyebrow="Rate-and-term or cash-out"
      title="Compare the old loan with the proposed refinance."
      description="Model a new rate, term, financed costs, and cash out. Then see the payment change, break-even point, and resulting loan-to-value."
      result={<ResultPanel
        eyebrow="Refinance comparison"
        label={result.monthlySavings >= 0 ? "Estimated monthly savings" : "Estimated monthly increase"}
        value={money.format(Math.abs(result.monthlySavings))}
        badge={result.monthlySavings > 0 ? `${result.breakEven.toFixed(1)}-month cost break-even` : "No payment break-even"}
        metrics={[
          { label: "Modeled current P&I", value: `${money.format(result.currentPi)}/mo` },
          { label: "Modeled new P&I", value: `${money.format(result.newPi)}/mo` },
          { label: "New loan amount", value: money.format(result.newLoan) },
          { label: "Resulting LTV", value: `${result.ltv.toFixed(1)}%` },
          { label: "Cash out", value: money.format(cashOut) },
          { label: "Financed closing costs", value: money.format(closingCosts) },
        ]}
        note="A payment comparison is not a complete refinance analysis. Review interest paid over the new term, recapture period, escrow changes, mortgage insurance, taxes, and how long you expect to keep the loan."
      />}
    >
      <NumberField label="Estimated property value" value={propertyValue} onChange={setPropertyValue} step={5000} />
      <NumberField label="Current principal balance" value={balance} onChange={setBalance} step={5000} />
      <NumberField label="Current interest rate (%)" value={currentRate} onChange={setCurrentRate} step={0.05} />
      <NumberField label="Years remaining" value={remainingYears} onChange={setRemainingYears} step={1} min={1} />
      <NumberField label="Proposed interest rate (%)" value={newRate} onChange={setNewRate} step={0.05} />
      <SelectField label="Proposed loan term" value={newYears} onChange={(value) => setNewYears(Number(value))} options={[
        { value: 30, label: "30 years" }, { value: 20, label: "20 years" }, { value: 15, label: "15 years" },
      ]} />
      <NumberField label="Financed closing costs" value={closingCosts} onChange={setClosingCosts} step={500} />
      <NumberField label="Cash out" value={cashOut} onChange={setCashOut} step={5000} />
    </ScenarioLayout>
  );
}

function RentVsBuyCalculator() {
  const [rent, setRent] = useState(2400);
  const [price, setPrice] = useState(400000);
  const [downPercent, setDownPercent] = useState(5);
  const [rate, setRate] = useState(6.65);
  const [years, setYears] = useState(30);
  const [taxes, setTaxes] = useState(4800);
  const [insurance, setInsurance] = useState(2400);
  const [hoa, setHoa] = useState(0);
  const [horizon, setHorizon] = useState(7);
  const [appreciation, setAppreciation] = useState(3);
  const [rentGrowth, setRentGrowth] = useState(3);
  const [maintenanceRate, setMaintenanceRate] = useState(1);
  const [sellingCost, setSellingCost] = useState(6);

  const result = useMemo(() => {
    const down = price * downPercent / 100;
    const loan = price - down;
    const pi = monthlyPayment(loan, rate, years);
    const monthlyOwner = pi + taxes / 12 + insurance / 12 + hoa + price * maintenanceRate / 100 / 12;
    const months = horizon * 12;
    const balance = remainingBalance(loan, rate, years, months);
    const futureValue = price * Math.pow(1 + appreciation / 100, horizon);
    const netEquity = futureValue * (1 - sellingCost / 100) - balance;
    const ownerCashOut = down + monthlyOwner * months;
    const netBuyCost = ownerCashOut - netEquity;
    let rentCost = 0;
    for (let year = 0; year < horizon; year += 1) rentCost += rent * 12 * Math.pow(1 + rentGrowth / 100, year);
    const difference = rentCost - netBuyCost;
    return { down, loan, pi, monthlyOwner, balance, futureValue, netEquity, netBuyCost, rentCost, difference };
  }, [rent, price, downPercent, rate, years, taxes, insurance, hoa, horizon, appreciation, rentGrowth, maintenanceRate, sellingCost]);

  return (
    <ScenarioLayout
      eyebrow="Rent vs. buy"
      title="Compare a time horizon, not just two monthly payments."
      description="Model rent growth, maintenance, appreciation, principal reduction, and selling costs over the years you expect to stay."
      result={<ResultPanel
        eyebrow={`${horizon}-year comparison`}
        label={result.difference >= 0 ? "Modeled buying advantage" : "Modeled renting advantage"}
        value={money.format(Math.abs(result.difference))}
        badge={`After ${horizon} years`}
        metrics={[
          { label: "Starting owner payment + maintenance", value: `${money.format(result.monthlyOwner)}/mo` },
          { label: "Modeled cumulative rent", value: money.format(result.rentCost) },
          { label: "Modeled net buying cost", value: money.format(result.netBuyCost) },
          { label: "Future home value", value: money.format(result.futureValue) },
          { label: "Net equity after modeled sale", value: money.format(result.netEquity) },
          { label: "Remaining mortgage balance", value: money.format(result.balance) },
        ]}
        note="This planning model excludes tax benefits, investment returns on cash, rent deposits, major repairs, transaction-specific costs, and uncertainty in appreciation. Small assumption changes can reverse the result."
      />}
    >
      <NumberField label="Current monthly rent" value={rent} onChange={setRent} step={50} />
      <NumberField label="Home price" value={price} onChange={setPrice} step={5000} />
      <NumberField label="Down payment (%)" value={downPercent} onChange={setDownPercent} step={0.5} />
      <NumberField label="Interest rate (%)" value={rate} onChange={setRate} step={0.05} />
      <SelectField label="Loan term" value={years} onChange={(value) => setYears(Number(value))} options={[
        { value: 30, label: "30 years" }, { value: 15, label: "15 years" },
      ]} />
      <NumberField label="Property tax (annual)" value={taxes} onChange={setTaxes} step={100} />
      <NumberField label="Home insurance (annual)" value={insurance} onChange={setInsurance} step={100} />
      <NumberField label="HOA fees (monthly)" value={hoa} onChange={setHoa} step={25} />
      <NumberField label="Years before moving" value={horizon} onChange={setHorizon} step={1} min={1} />
      <NumberField label="Annual appreciation (%)" value={appreciation} onChange={setAppreciation} step={0.25} />
      <NumberField label="Annual rent growth (%)" value={rentGrowth} onChange={setRentGrowth} step={0.25} />
      <NumberField label="Maintenance (% of value/year)" value={maintenanceRate} onChange={setMaintenanceRate} step={0.25} />
      <NumberField label="Selling costs (%)" value={sellingCost} onChange={setSellingCost} step={0.5} />
    </ScenarioLayout>
  );
}

function VaPurchaseCalculator() {
  const [price, setPrice] = useState(450000);
  const [downPercent, setDownPercent] = useState(0);
  const [rate, setRate] = useState(6.25);
  const [years, setYears] = useState(30);
  const [taxes, setTaxes] = useState(5400);
  const [insurance, setInsurance] = useState(3000);
  const [hoa, setHoa] = useState(0);
  const [firstUse, setFirstUse] = useState(true);
  const [exempt, setExempt] = useState(false);

  useEffect(() => {
    const saved = readMortgageScenario();
    if (!saved || saved.goal !== "va") return;
    const frame = window.requestAnimationFrame(() => {
      setPrice(saved.homePrice);
      setDownPercent(saved.homePrice ? saved.downPayment / saved.homePrice * 100 : 0);
      setRate(saved.rate);
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  const result = useMemo(() => {
    const down = price * downPercent / 100;
    const baseLoan = price - down;
    const feeRate = vaPurchaseFeeRate(downPercent, firstUse, exempt);
    const fundingFee = baseLoan * feeRate / 100;
    const totalLoan = baseLoan + fundingFee;
    const pi = monthlyPayment(totalLoan, rate, years);
    const total = pi + taxes / 12 + insurance / 12 + hoa;
    return { down, baseLoan, feeRate, fundingFee, totalLoan, pi, total };
  }, [price, downPercent, rate, years, taxes, insurance, hoa, firstUse, exempt]);

  return (
    <ScenarioLayout
      eyebrow="VA purchase"
      title="Run the VA benefit as a VA scenario."
      description="Model zero-down or partial-down financing, first or subsequent use, a potential funding-fee exemption, and the complete payment."
      result={<ResultPanel
        eyebrow="VA purchase scenario"
        label="Estimated monthly payment"
        value={money.format(result.total)}
        badge={exempt ? "Funding-fee exemption modeled" : `${result.feeRate.toFixed(2)}% funding fee`}
        metrics={[
          { label: "Down payment", value: money.format(result.down) },
          { label: "Base VA loan", value: money.format(result.baseLoan) },
          { label: "Financed funding fee", value: money.format(result.fundingFee) },
          { label: "Total modeled loan", value: money.format(result.totalLoan) },
          { label: "Principal & interest", value: `${money.format(result.pi)}/mo` },
          { label: "Monthly mortgage insurance", value: "$0" },
        ]}
        note="VA eligibility, entitlement, reasonable value, residual income, credit, occupancy, property requirements, and lender guidelines still apply. Verify exemption status on the Certificate of Eligibility."
      />}
    >
      <NumberField label="Home price" value={price} onChange={setPrice} step={5000} />
      <NumberField label="Down payment (%)" value={downPercent} onChange={setDownPercent} step={0.5} />
      <NumberField label="Interest rate (%)" value={rate} onChange={setRate} step={0.05} />
      <SelectField label="Loan term" value={years} onChange={(value) => setYears(Number(value))} options={[
        { value: 30, label: "30 years" }, { value: 15, label: "15 years" },
      ]} />
      <NumberField label="Property tax (annual)" value={taxes} onChange={setTaxes} step={100} />
      <NumberField label="Home insurance (annual)" value={insurance} onChange={setInsurance} step={100} />
      <NumberField label="HOA fees (monthly)" value={hoa} onChange={setHoa} step={25} />
      <div className="studio-toggle-stack">
        <ToggleField checked={firstUse} onChange={setFirstUse} label="First use of VA home-loan benefit" help="Subsequent use can change the funding fee when down payment is under 5%." />
        <ToggleField checked={exempt} onChange={setExempt} label="Model a funding-fee exemption" help="The final exemption must be verified by VA documentation." />
      </div>
    </ScenarioLayout>
  );
}

function VaRefinanceCalculator() {
  const [refiType, setRefiType] = useState<"IRRRL" | "Cash-out">("IRRRL");
  const [propertyValue, setPropertyValue] = useState(500000);
  const [balance, setBalance] = useState(350000);
  const [currentRate, setCurrentRate] = useState(7);
  const [remainingYears, setRemainingYears] = useState(27);
  const [newRate, setNewRate] = useState(6);
  const [newYears, setNewYears] = useState(30);
  const [closingCosts, setClosingCosts] = useState(5000);
  const [cashOut, setCashOut] = useState(0);
  const [firstUse, setFirstUse] = useState(true);
  const [exempt, setExempt] = useState(false);

  const result = useMemo(() => {
    const feeRate = exempt ? 0 : refiType === "IRRRL" ? 0.5 : firstUse ? 2.15 : 3.3;
    const amountBeforeFee = balance + closingCosts + (refiType === "Cash-out" ? cashOut : 0);
    const fundingFee = amountBeforeFee * feeRate / 100;
    const newLoan = amountBeforeFee + fundingFee;
    const currentPi = monthlyPayment(balance, currentRate, remainingYears);
    const newPi = monthlyPayment(newLoan, newRate, newYears);
    const savings = currentPi - newPi;
    const recapture = savings > 0 ? (closingCosts + fundingFee) / savings : 0;
    const ltv = propertyValue ? newLoan / propertyValue * 100 : 0;
    return { feeRate, fundingFee, newLoan, currentPi, newPi, savings, recapture, ltv };
  }, [refiType, propertyValue, balance, currentRate, remainingYears, newRate, newYears, closingCosts, cashOut, firstUse, exempt]);

  return (
    <ScenarioLayout
      eyebrow="VA refinance / IRRRL"
      title="Separate the streamline from the cash-out scenario."
      description="Switch between an IRRRL and a VA cash-out refinance to see how the funding-fee assumption, new loan, payment, and recapture period change."
      result={<ResultPanel
        eyebrow={`${refiType} scenario`}
        label={result.savings >= 0 ? "Estimated monthly savings" : "Estimated monthly increase"}
        value={money.format(Math.abs(result.savings))}
        badge={result.savings > 0 ? `${result.recapture.toFixed(1)}-month modeled recapture` : "No payment recapture"}
        metrics={[
          { label: "Current modeled P&I", value: `${money.format(result.currentPi)}/mo` },
          { label: "New modeled P&I", value: `${money.format(result.newPi)}/mo` },
          { label: "Funding fee", value: money.format(result.fundingFee) },
          { label: "New loan amount", value: money.format(result.newLoan) },
          { label: "Resulting LTV", value: `${result.ltv.toFixed(1)}%` },
          { label: "Cash out", value: refiType === "Cash-out" ? money.format(cashOut) : "$0" },
        ]}
        note="IRRRLs have their own seasoning, recoupment, payment-benefit, occupancy, and existing-VA-loan rules. A VA cash-out refinance requires a different analysis and underwriting path."
      />}
    >
      <SelectField label="VA refinance type" value={refiType} onChange={(value) => setRefiType(value as "IRRRL" | "Cash-out")} options={[
        { value: "IRRRL", label: "IRRRL / VA streamline" }, { value: "Cash-out", label: "VA cash-out refinance" },
      ]} />
      <NumberField label="Estimated property value" value={propertyValue} onChange={setPropertyValue} step={5000} />
      <NumberField label="Current principal balance" value={balance} onChange={setBalance} step={5000} />
      <NumberField label="Current interest rate (%)" value={currentRate} onChange={setCurrentRate} step={0.05} />
      <NumberField label="Years remaining" value={remainingYears} onChange={setRemainingYears} step={1} min={1} />
      <NumberField label="Proposed interest rate (%)" value={newRate} onChange={setNewRate} step={0.05} />
      <SelectField label="Proposed loan term" value={newYears} onChange={(value) => setNewYears(Number(value))} options={[
        { value: 30, label: "30 years" }, { value: 20, label: "20 years" }, { value: 15, label: "15 years" },
      ]} />
      <NumberField label="Financed closing costs" value={closingCosts} onChange={setClosingCosts} step={500} />
      {refiType === "Cash-out" ? <NumberField label="Cash out" value={cashOut} onChange={setCashOut} step={5000} /> : null}
      <div className="studio-toggle-stack">
        {refiType === "Cash-out" ? <ToggleField checked={firstUse} onChange={setFirstUse} label="First use for cash-out fee modeling" /> : null}
        <ToggleField checked={exempt} onChange={setExempt} label="Model a funding-fee exemption" />
      </div>
    </ScenarioLayout>
  );
}

function DscrCalculator() {
  const [price, setPrice] = useState(350000);
  const [downPercent, setDownPercent] = useState(25);
  const [rate, setRate] = useState(7.5);
  const [years, setYears] = useState(30);
  const [rent, setRent] = useState(3200);
  const [taxes, setTaxes] = useState(4200);
  const [insurance, setInsurance] = useState(2400);
  const [hoa, setHoa] = useState(0);
  const [operating, setOperating] = useState(300);

  const result = useMemo(() => {
    const down = price * downPercent / 100;
    const loan = price - down;
    const pi = monthlyPayment(loan, rate, years);
    const pitia = pi + taxes / 12 + insurance / 12 + hoa;
    const ratio = pitia ? rent / pitia : 0;
    const cashFlow = rent - pitia - operating;
    const noiCoverage = pi ? (rent - taxes / 12 - insurance / 12 - hoa - operating) / pi : 0;
    return { down, loan, pi, pitia, ratio, cashFlow, noiCoverage };
  }, [price, downPercent, rate, years, rent, taxes, insurance, hoa, operating]);

  const badge = result.ratio >= 1.25 ? "At or above 1.25 modeled coverage" : result.ratio >= 1 ? "Above 1.00 modeled coverage" : "Below 1.00 modeled coverage";

  return (
    <ScenarioLayout
      eyebrow="DSCR investor"
      title="Measure rental income against the property payment."
      description="Model rent, PITIA, operating costs, leverage, and cash flow. See both a rent-to-PITIA ratio and an NOI-style coverage view."
      result={<ResultPanel
        eyebrow="Rental coverage scenario"
        label="Modeled rent-to-PITIA ratio"
        value={`${result.ratio.toFixed(2)}×`}
        badge={badge}
        metrics={[
          { label: "Monthly market rent", value: money.format(rent) },
          { label: "Modeled PITIA", value: `${money.format(result.pitia)}/mo` },
          { label: "Cash flow after added operating costs", value: `${money.format(result.cashFlow)}/mo` },
          { label: "NOI-style debt-service coverage", value: `${result.noiCoverage.toFixed(2)}×` },
          { label: "Loan amount", value: money.format(result.loan) },
          { label: "Cash down", value: money.format(result.down) },
        ]}
        note="DSCR definitions, minimum ratios, vacancy treatment, operating-expense treatment, appraisal rent, reserves, prepayment penalties, and pricing vary by lender and program."
      />}
    >
      <NumberField label="Purchase price" value={price} onChange={setPrice} step={5000} />
      <NumberField label="Down payment (%)" value={downPercent} onChange={setDownPercent} step={1} />
      <NumberField label="Interest rate (%)" value={rate} onChange={setRate} step={0.05} />
      <SelectField label="Loan term" value={years} onChange={(value) => setYears(Number(value))} options={[
        { value: 30, label: "30 years" }, { value: 15, label: "15 years" },
      ]} />
      <NumberField label="Monthly market rent" value={rent} onChange={setRent} step={50} />
      <NumberField label="Property tax (annual)" value={taxes} onChange={setTaxes} step={100} />
      <NumberField label="Insurance (annual)" value={insurance} onChange={setInsurance} step={100} />
      <NumberField label="HOA fees (monthly)" value={hoa} onChange={setHoa} step={25} />
      <NumberField label="Other operating costs (monthly)" value={operating} onChange={setOperating} step={25} help="Maintenance, management, vacancy reserve, and other modeled expenses." />
    </ScenarioLayout>
  );
}

function FixFlipCalculator() {
  const [purchasePrice, setPurchasePrice] = useState(250000);
  const [rehab, setRehab] = useState(75000);
  const [arv, setArv] = useState(425000);
  const [downPercent, setDownPercent] = useState(20);
  const [rehabFinanced, setRehabFinanced] = useState(90);
  const [rate, setRate] = useState(10.5);
  const [months, setMonths] = useState(9);
  const [points, setPoints] = useState(2);
  const [closingCosts, setClosingCosts] = useState(6000);
  const [holdingMonthly, setHoldingMonthly] = useState(1000);
  const [sellingCost, setSellingCost] = useState(6);

  const result = useMemo(() => {
    const purchaseLoan = purchasePrice * (1 - downPercent / 100);
    const rehabLoan = rehab * rehabFinanced / 100;
    const loan = purchaseLoan + rehabLoan;
    const monthlyInterest = loan * rate / 100 / 12;
    const totalInterest = monthlyInterest * months;
    const pointCost = loan * points / 100;
    const holding = holdingMonthly * months;
    const selling = arv * sellingCost / 100;
    const projectCost = purchasePrice + rehab + totalInterest + pointCost + closingCosts + holding + selling;
    const profit = arv - projectCost;
    const cashInvested = purchasePrice - purchaseLoan + rehab - rehabLoan + totalInterest + pointCost + closingCosts + holding;
    const roi = cashInvested ? profit / cashInvested * 100 : 0;
    const loanToCost = purchasePrice + rehab ? loan / (purchasePrice + rehab) * 100 : 0;
    return { purchaseLoan, rehabLoan, loan, monthlyInterest, totalInterest, pointCost, holding, selling, projectCost, profit, cashInvested, roi, loanToCost };
  }, [purchasePrice, rehab, arv, downPercent, rehabFinanced, rate, months, points, closingCosts, holdingMonthly, sellingCost]);

  return (
    <ScenarioLayout
      eyebrow="Fix & flip"
      title="Pressure-test the whole project."
      description="Combine acquisition, rehab, financing, points, carrying costs, selling costs, and after-repair value into one project view."
      result={<ResultPanel
        eyebrow={`${months}-month project scenario`}
        label="Modeled net profit"
        value={money.format(result.profit)}
        badge={`${result.roi.toFixed(1)}% modeled cash ROI`}
        metrics={[
          { label: "Total project loan", value: money.format(result.loan) },
          { label: "Modeled cash invested", value: money.format(result.cashInvested) },
          { label: "Interest-only payment", value: `${money.format(result.monthlyInterest)}/mo` },
          { label: "Total financing interest", value: money.format(result.totalInterest) },
          { label: "Selling costs", value: money.format(result.selling) },
          { label: "Loan-to-cost", value: `${result.loanToCost.toFixed(1)}%` },
        ]}
        note="This model does not include taxes, permit overruns, draw timing, inspection fees, extension fees, contingency, lender reserves, or changes in sale price. A negative result means modeled costs exceed ARV."
      />}
    >
      <NumberField label="Purchase price" value={purchasePrice} onChange={setPurchasePrice} step={5000} />
      <NumberField label="Rehab budget" value={rehab} onChange={setRehab} step={5000} />
      <NumberField label="After-repair value (ARV)" value={arv} onChange={setArv} step={5000} />
      <NumberField label="Down payment (%)" value={downPercent} onChange={setDownPercent} step={1} />
      <NumberField label="Rehab financed (%)" value={rehabFinanced} onChange={setRehabFinanced} step={5} />
      <NumberField label="Interest rate (%)" value={rate} onChange={setRate} step={0.25} />
      <NumberField label="Project term (months)" value={months} onChange={setMonths} step={1} min={1} />
      <NumberField label="Lender points (%)" value={points} onChange={setPoints} step={0.25} />
      <NumberField label="Closing and lender costs" value={closingCosts} onChange={setClosingCosts} step={500} />
      <NumberField label="Holding costs (monthly)" value={holdingMonthly} onChange={setHoldingMonthly} step={100} />
      <NumberField label="Selling costs (%)" value={sellingCost} onChange={setSellingCost} step={0.5} />
    </ScenarioLayout>
  );
}

function ScenarioOptIn({ activeMode }: { activeMode: Mode }) {
  const [saved, setSaved] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const label = modes.find((mode) => mode.id === activeMode)?.label || "Mortgage";

  return (
    <section className="studio-optin">
      <div>
        <p className="eyebrow">Keep the scenario</p>
        <h2>Save the numbers or ask Dennis to review the assumptions.</h2>
        <p>Email this {label.toLowerCase()} setup to yourself, or ask Dennis for a one-time review without adding an automatic marketing-text opt-in.</p>
      </div>
      {!saved ? (
        <form onSubmit={async (event) => {
          event.preventDefault();
          setSubmitting(true);
          setError("");
          const form = new FormData(event.currentTarget);
          const scenarioInputs = Array.from(document.querySelectorAll<HTMLInputElement | HTMLSelectElement>("#studio-workspace input, #studio-workspace select")).map((input) => ({
            name: input.name || input.closest("label")?.querySelector("span")?.textContent || input.type,
            value: input.value,
          }));
          try {
            await submitLead({
              email: String(form.get("email") || ""),
              segment: `${label} calculator scenario`,
              scenarioMode: activeMode,
              scenarioInputs: JSON.stringify(scenarioInputs),
              reviewRequested: form.get("reviewRequested") === "on",
              emailConsent: form.get("emailConsent") === "on",
              source: "redesign-calculator-save",
            });
            setSaved(true);
          } catch (caught) {
            setError(caught instanceof Error ? caught.message : "The scenario could not be sent.");
          } finally {
            setSubmitting(false);
          }
        }}>
          <label className="field"><span>Email</span><input name="email" type="email" required placeholder="you@example.com" /></label>
          <label className="checkbox-field"><input name="emailConsent" type="checkbox" required /><span>Email this scenario and allow a reply about this request. I acknowledge the Privacy Policy.</span></label>
          <label className="checkbox-field"><input name="reviewRequested" type="checkbox" /><span>Optional: ask Dennis for a one-time review of this scenario.</span></label>
          {error ? <p className="form-error" role="alert">{error}</p> : null}
          <button className="button button-gold" type="submit" disabled={submitting}>{submitting ? "Sending..." : `Save this ${label} scenario`}</button>
          <p className="form-note">Consent is not a condition of obtaining services.</p>
        </form>
      ) : (
        <div className="success-message success-message-dark" role="status">
          <strong>Your scenario was sent.</strong>
          <span>The calculator mode, current inputs, and review preference were included.</span>
          <button className="button button-gold" type="button" onClick={() => setSaved(false)}>Save another</button>
        </div>
      )}
    </section>
  );
}

export default function MortgageStudio() {
  const [activeMode, setActiveMode] = useState<Mode>("purchase");

  useEffect(() => {
    const syncFromHash = () => {
      const hash = window.location.hash.replace("#", "") as Mode;
      if (modes.some((mode) => mode.id === hash)) {
        setActiveMode(hash);
        window.requestAnimationFrame(() => {
          document.getElementById("studio-workspace")?.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      }
    };
    syncFromHash();
    window.addEventListener("hashchange", syncFromHash);
    return () => window.removeEventListener("hashchange", syncFromHash);
  }, []);

  const chooseMode = (mode: Mode) => {
    setActiveMode(mode);
    window.history.replaceState(null, "", `#${mode}`);
    document.getElementById("studio-workspace")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="mortgage-studio" id="mortgage-studio">
      <div className="studio-navigation" aria-label="Mortgage calculator choices">
        <div className="studio-navigation-heading">
          <div>
            <p className="eyebrow">Choose a calculator</p>
            <h2>Ten financing questions. Ten purpose-built tools.</h2>
          </div>
          <p>Switch scenarios without leaving the studio. Your inputs remain available while that calculator stays open.</p>
        </div>
        <div className="studio-mode-grid" role="tablist" aria-label="Calculator suite">
          {modes.map((mode, index) => (
            <button
              type="button"
              role="tab"
              aria-selected={activeMode === mode.id}
              aria-controls="studio-workspace"
              className={activeMode === mode.id ? "active" : ""}
              onClick={() => chooseMode(mode.id)}
              key={mode.id}
            >
              <span>{String(index + 1).padStart(2, "0")}</span>
              <i>{mode.short}</i>
              <strong>{mode.label}</strong>
              <small>{mode.family}</small>
            </button>
          ))}
        </div>
      </div>

      <div className="studio-workspace anchor-target" id="studio-workspace" role="tabpanel" key={activeMode}>
        {activeMode === "purchase" ? <PurchaseCalculator /> : null}
        {activeMode === "affordability" ? <AffordabilityCalculator /> : null}
        {activeMode === "fha" ? <FhaCalculator /> : null}
        {activeMode === "refinance" ? <RefinanceCalculator /> : null}
        {activeMode === "rent-buy" ? <RentVsBuyCalculator /> : null}
        {activeMode === "va-purchase" ? <VaPurchaseCalculator /> : null}
        {activeMode === "va-refinance" ? <VaRefinanceCalculator /> : null}
        {activeMode === "dscr" ? <DscrCalculator /> : null}
        {activeMode === "fix-flip" ? <FixFlipCalculator /> : null}
        {activeMode === "heloc" ? <HelocCalculator /> : null}
      </div>

      <ScenarioOptIn activeMode={activeMode} />

      <aside className="studio-methodology">
        <strong>Methodology & source notes</strong>
        <p>Every result is an educational illustration, not a quote, approval, commitment, tax opinion, or investment recommendation. Default rates are editable assumptions, not advertised pricing.</p>
        <div>
          <a href="https://answers.hud.gov/FHA/s/article/What-is-the-FHA-Mortgage-Insurance-Premium-structure-for-forward-mortgage-loans">HUD FHA mortgage-insurance structure</a>
          <a href="https://www.va.gov/housing-assistance/home-loans/funding-fee-and-closing-costs/">VA funding-fee chart</a>
          <a href="https://www.rd.usda.gov/programs-services/single-family-housing-programs/single-family-housing-guaranteed-loan-program">USDA guaranteed-loan overview</a>
        </div>
        <small>Program assumptions reviewed July 10, 2026. Verify all guidelines, fees, premiums, and eligibility for the actual file before relying on a result.</small>
      </aside>
    </div>
  );
}
