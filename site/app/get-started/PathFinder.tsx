"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { submitLead } from "../lead-client";
import { secureApplicationUrl } from "../site-components";

type Goal = "purchase" | "refinance" | "equity" | "research";

type AnswerKey =
  | "goal"
  | "purchaseType"
  | "financingProfile"
  | "purchaseTimeline"
  | "priceRange"
  | "refinanceGoal"
  | "currentLoan"
  | "propertyHorizon"
  | "refinanceTimeline"
  | "equityUse"
  | "equityPriority"
  | "equityAmount"
  | "equityTimeline"
  | "researchStatus"
  | "researchFocus"
  | "researchTimeline";

type Answers = Partial<Record<AnswerKey, string>> & { goal?: Goal };

type Choice = {
  label: string;
  detail: string;
  value: string;
};

type QuizStep = {
  id: string;
  key: AnswerKey;
  eyebrow: string;
  title: string;
  choices: Choice[];
};

const goalStep: QuizStep = {
  id: "goal",
  key: "goal",
  eyebrow: "Choose the conversation you actually need",
  title: "What are you trying to accomplish?",
  choices: [
    { label: "Buy a property", detail: "First home, next home, relocation, second home, or investment", value: "purchase" },
    { label: "Refinance my mortgage", detail: "Change the payment, term, loan type, or access cash", value: "refinance" },
    { label: "Use my home equity", detail: "Compare a HELOC, home-equity loan, and cash-out refinance", value: "equity" },
    { label: "Understand my options", detail: "I am still learning and want the right starting point", value: "research" },
  ],
};

const purchaseSteps: QuizStep[] = [
  {
    id: "purchase-type",
    key: "purchaseType",
    eyebrow: "Purchase path",
    title: "What kind of purchase are you planning?",
    choices: [
      { label: "My first home", detail: "I have not owned a primary home recently", value: "first-home" },
      { label: "My next home", detail: "I own now, may need to sell, or want to move up", value: "next-home" },
      { label: "Relocation or second home", detail: "A move, seasonal home, or additional residence", value: "second-home" },
      { label: "Investment property", detail: "Rental, DSCR, fix and flip, or portfolio strategy", value: "investment" },
    ],
  },
  {
    id: "purchase-profile",
    key: "financingProfile",
    eyebrow: "Financing profile",
    title: "Which financing detail deserves the closest review?",
    choices: [
      { label: "VA eligibility", detail: "Veteran, active military, Reserve, Guard, or eligible spouse", value: "va" },
      { label: "Traditional income", detail: "Salary, hourly, retirement, or other documented income", value: "traditional" },
      { label: "Self-employed income", detail: "Business owner, 1099, commission, or complex income", value: "self-employed" },
      { label: "Cash-to-close support", detail: "Low-down-payment or assistance options matter", value: "assistance" },
      { label: "Investment cash flow", detail: "Property income and reserves may drive the strategy", value: "investor" },
    ],
  },
  {
    id: "purchase-timeline",
    key: "purchaseTimeline",
    eyebrow: "Purchase timing",
    title: "Where are you in the buying process?",
    choices: [
      { label: "Under contract", detail: "I need an immediate financing review", value: "under-contract" },
      { label: "Actively shopping", detail: "I want a payment and approval strategy now", value: "shopping" },
      { label: "Within 1 to 3 months", detail: "I am preparing before making offers", value: "1-3-months" },
      { label: "More than 3 months", detail: "I have time to strengthen the plan", value: "later" },
    ],
  },
  {
    id: "purchase-range",
    key: "priceRange",
    eyebrow: "Planning range",
    title: "What purchase-price range are you considering?",
    choices: [
      { label: "Under $300,000", detail: "Build the complete payment and cash-to-close estimate", value: "under-300" },
      { label: "$300,000 to $450,000", detail: "Compare payment and down-payment combinations", value: "300-450" },
      { label: "$450,000 to $700,000", detail: "Review move-up, sale timing, or larger-loan strategy", value: "450-700" },
      { label: "$700,000 or more", detail: "Review jumbo and higher-balance options", value: "700-plus" },
      { label: "I need help finding the range", detail: "Start with a comfortable monthly payment", value: "unknown" },
    ],
  },
];

const refinanceSteps: QuizStep[] = [
  {
    id: "refinance-goal",
    key: "refinanceGoal",
    eyebrow: "Refinance path",
    title: "What do you want the refinance to accomplish?",
    choices: [
      { label: "Lower my monthly payment", detail: "Compare payment savings with closing costs and recapture time", value: "lower-payment" },
      { label: "Pay the mortgage off sooner", detail: "Shorter term, faster payoff, or interest-cost strategy", value: "shorter-term" },
      { label: "Remove mortgage insurance", detail: "Review equity and a possible loan-type change", value: "remove-mi" },
      { label: "Take cash out", detail: "Access equity for a specific goal", value: "cash-out" },
      { label: "Change loan type or risk", detail: "Fixed rate, adjustable rate, FHA, VA, or conventional", value: "change-type" },
    ],
  },
  {
    id: "current-loan",
    key: "currentLoan",
    eyebrow: "Current mortgage",
    title: "What type of mortgage do you have now?",
    choices: [
      { label: "Conventional", detail: "A standard conforming, high-balance, or jumbo mortgage", value: "conventional" },
      { label: "FHA", detail: "An FHA-insured mortgage with mortgage insurance", value: "fha" },
      { label: "VA", detail: "A VA mortgage that may have streamline options", value: "va" },
      { label: "USDA or another program", detail: "A rural, specialty, or less common mortgage type", value: "other" },
      { label: "I am not sure", detail: "Dennis can identify it from the mortgage statement", value: "unknown" },
    ],
  },
  {
    id: "property-horizon",
    key: "propertyHorizon",
    eyebrow: "Break-even context",
    title: "How long do you expect to keep this property?",
    choices: [
      { label: "Less than 2 years", detail: "Closing-cost recovery needs especially careful review", value: "under-2" },
      { label: "2 to 5 years", detail: "Compare recapture time with the expected ownership window", value: "2-5" },
      { label: "More than 5 years", detail: "Longer-term payment and interest costs matter", value: "5-plus" },
      { label: "I am not sure", detail: "Model more than one ownership horizon", value: "unknown" },
    ],
  },
  {
    id: "refinance-timeline",
    key: "refinanceTimeline",
    eyebrow: "Review timing",
    title: "When do you want to review the refinance numbers?",
    choices: [
      { label: "Now", detail: "I want a current side-by-side comparison", value: "now" },
      { label: "Within 30 days", detail: "I am watching pricing or preparing documents", value: "30-days" },
      { label: "Within 1 to 3 months", detail: "I want a strategy before making a decision", value: "1-3-months" },
      { label: "Later", detail: "I am researching what would make refinancing worthwhile", value: "later" },
    ],
  },
];

const equitySteps: QuizStep[] = [
  {
    id: "equity-use",
    key: "equityUse",
    eyebrow: "Home-equity path",
    title: "What would you like to use the equity for?",
    choices: [
      { label: "Home improvements", detail: "Renovation, repairs, addition, or major project", value: "renovation" },
      { label: "Debt consolidation", detail: "Compare total cost, payment, and repayment risk", value: "debt" },
      { label: "Another property or investment", detail: "Down payment, acquisition, or business purpose", value: "investment" },
      { label: "Flexible access to cash", detail: "A line available for planned or unexpected needs", value: "flexibility" },
      { label: "Another goal", detail: "Start with the amount, timing, and payment preference", value: "other" },
    ],
  },
  {
    id: "equity-priority",
    key: "equityPriority",
    eyebrow: "Payment preference",
    title: "What matters most in the equity decision?",
    choices: [
      { label: "Keep my current first mortgage", detail: "Avoid replacing the existing rate and loan terms", value: "preserve-first" },
      { label: "A fixed payment", detail: "Predictability matters more than reusable access", value: "fixed-payment" },
      { label: "Borrow only when needed", detail: "Flexible draws and repayment are important", value: "flexible-draw" },
      { label: "One combined mortgage payment", detail: "I am open to replacing the first mortgage", value: "one-payment" },
      { label: "I need a comparison", detail: "Show HELOC, home-equity loan, and cash-out paths", value: "compare" },
    ],
  },
  {
    id: "equity-amount",
    key: "equityAmount",
    eyebrow: "Estimated access",
    title: "About how much equity would you like to access?",
    choices: [
      { label: "Under $50,000", detail: "A smaller project, reserve, or targeted payoff", value: "under-50" },
      { label: "$50,000 to $100,000", detail: "Compare line, fixed-loan, and closing-cost tradeoffs", value: "50-100" },
      { label: "$100,000 to $250,000", detail: "Loan structure and first-mortgage impact matter", value: "100-250" },
      { label: "$250,000 or more", detail: "Review combined leverage, payment, and property limits", value: "250-plus" },
      { label: "I am not sure", detail: "Start with the goal and a sustainable payment", value: "unknown" },
    ],
  },
  {
    id: "equity-timeline",
    key: "equityTimeline",
    eyebrow: "Access timing",
    title: "When would you like the funds available?",
    choices: [
      { label: "As soon as possible", detail: "The need is immediate or already scheduled", value: "asap" },
      { label: "Within 30 days", detail: "I am planning a near-term use", value: "30-days" },
      { label: "Within 1 to 3 months", detail: "I have time to compare structures", value: "1-3-months" },
      { label: "I am researching", detail: "I want to understand the options first", value: "later" },
    ],
  },
];

const researchSteps: QuizStep[] = [
  {
    id: "research-status",
    key: "researchStatus",
    eyebrow: "Starting context",
    title: "Which statement is true today?",
    choices: [
      { label: "I do not own a home", detail: "I am learning what buying could look like", value: "non-owner" },
      { label: "I own my primary home", detail: "I may move, refinance, or use equity", value: "homeowner" },
      { label: "I own investment property", detail: "I want financing or portfolio guidance", value: "investor" },
      { label: "I am helping someone else", detail: "I want reliable information before referring them", value: "helper" },
    ],
  },
  {
    id: "research-focus",
    key: "researchFocus",
    eyebrow: "Learning priority",
    title: "What would you like to understand first?",
    choices: [
      { label: "Buying and affordability", detail: "Payment, cash to close, and purchase options", value: "buying" },
      { label: "Refinance savings", detail: "Payment change, costs, and break-even", value: "refinance" },
      { label: "Using home equity", detail: "HELOC, fixed home-equity loan, and cash-out comparison", value: "equity" },
      { label: "Investment financing", detail: "Rental, DSCR, bank-statement, or project financing", value: "investment" },
      { label: "Credit and readiness", detail: "What to improve before applying", value: "readiness" },
    ],
  },
  {
    id: "research-timeline",
    key: "researchTimeline",
    eyebrow: "Learning timeline",
    title: "How soon could this become a real decision?",
    choices: [
      { label: "Within 30 days", detail: "I need focused answers now", value: "30-days" },
      { label: "Within 1 to 3 months", detail: "I am preparing before taking action", value: "1-3-months" },
      { label: "More than 3 months", detail: "I have time to learn and improve the plan", value: "later" },
      { label: "No timeline yet", detail: "I only want a clear educational starting point", value: "none" },
    ],
  },
];

const branchSteps: Record<Goal, QuizStep[]> = {
  purchase: purchaseSteps,
  refinance: refinanceSteps,
  equity: equitySteps,
  research: researchSteps,
};

const goalLabels: Record<Goal, string> = {
  purchase: "Purchase",
  refinance: "Refinance",
  equity: "Home equity",
  research: "Research",
};

const allSteps = [goalStep, ...purchaseSteps, ...refinanceSteps, ...equitySteps, ...researchSteps];

function answerLabel(key: AnswerKey, value?: string) {
  if (!value) return "Not selected";
  const step = allSteps.find((item) => item.key === key);
  return step?.choices.find((choice) => choice.value === value)?.label || value;
}

function recommendation(answers: Answers) {
  if (answers.goal === "refinance") {
    if (answers.currentLoan === "va" && answers.refinanceGoal === "lower-payment") {
      return {
        title: "VA refinance and IRRRL review",
        body: "Compare the current VA loan with IRRRL and full-refinance options, including payment benefit, allowable costs, recoupment, seasoning, and how long you expect to keep the property.",
        toolHref: "/tools#va-refinance",
        toolLabel: "Run the VA refinance calculator",
      };
    }
    if (answers.currentLoan === "fha" && answers.refinanceGoal === "remove-mi") {
      return {
        title: "FHA-to-conventional comparison",
        body: "Review the property value, estimated equity, current FHA mortgage insurance, new closing costs, and break-even point before assuming a conventional refinance is better.",
        toolHref: "/tools#refinance",
        toolLabel: "Compare refinance scenarios",
      };
    }
    if (answers.refinanceGoal === "cash-out") {
      return {
        title: "Cash-out refinance and equity review",
        body: "Compare replacing the entire first mortgage with using a second-lien equity product. The right answer depends on the current loan, cash needed, payment change, costs, and ownership horizon.",
        toolHref: "/tools#refinance",
        toolLabel: "Model the cash-out refinance",
      };
    }
    return {
      title: "Refinance break-even review",
      body: "Build a side-by-side comparison of the current mortgage and proposed loan using payment change, closing costs, recapture time, total interest, and the expected ownership horizon.",
      toolHref: "/tools#refinance",
      toolLabel: "Run the refinance calculator",
    };
  }

  if (answers.goal === "equity") {
    if (answers.equityPriority === "preserve-first" || answers.equityPriority === "flexible-draw") {
      return {
        title: "HELOC and second-lien review",
        body: "Start by preserving the current first mortgage, then compare a HELOC with a fixed home-equity loan using draw flexibility, variable-rate exposure, payment, fees, and payoff plan.",
        toolHref: "/heloc-calculator",
        toolLabel: "Open the HELOC calculator",
      };
    }
    return {
      title: "Complete home-equity comparison",
      body: "Compare a HELOC, fixed home-equity loan, and cash-out refinance around the amount needed, payment preference, current first mortgage, closing costs, and timing.",
      toolHref: "/heloc-calculator",
      toolLabel: "Compare the equity paths",
    };
  }

  if (answers.goal === "purchase") {
    if (answers.financingProfile === "va") {
      return {
        title: "VA purchase and payment review",
        body: "Review entitlement, funding-fee status, complete payment, property questions, cash to close, and offer timing before opening the full application.",
        toolHref: "/tools#va-purchase",
        toolLabel: "Run the VA purchase calculator",
      };
    }
    if (answers.financingProfile === "self-employed") {
      return {
        title: "Self-employed purchase strategy",
        body: "Map the income documents, business history, liquidity, and lender paths before choosing a price range or assuming the tax return is the only available route.",
        toolHref: "/mortgage-options#specialty",
        toolLabel: "Review specialty loan options",
      };
    }
    if (answers.financingProfile === "assistance") {
      return {
        title: "Purchase and DPA fit review",
        body: "Compare eligible assistance with a standard purchase option using the first-mortgage rate, payment, cash to close, income limits, property rules, and repayment terms.",
        toolHref: "/dpa",
        toolLabel: "Explore DPA programs",
      };
    }
    if (answers.purchaseType === "investment" || answers.financingProfile === "investor") {
      return {
        title: "Investment-property financing strategy",
        body: "Compare conventional, DSCR, bank-statement, and project-specific options around property cash flow, reserves, down payment, occupancy, and the investment plan.",
        toolHref: "/tools#dscr",
        toolLabel: "Run the DSCR calculator",
      };
    }
    return {
      title: "Florida purchase roadmap",
      body: "Build the comfortable payment, complete cash-to-close estimate, financing paths, and timing plan before shopping at the maximum someone might approve.",
      toolHref: "/tools#affordability",
      toolLabel: "Check affordability",
    };
  }

  const researchLinks: Record<string, { title: string; body: string; toolHref: string; toolLabel: string }> = {
    refinance: {
      title: "Refinance learning path",
      body: "Start with the refinance break-even guide and calculator so rate, payment, closing costs, and ownership horizon stay in the same comparison.",
      toolHref: "/tools#refinance",
      toolLabel: "Explore refinance numbers",
    },
    equity: {
      title: "Home-equity learning path",
      body: "Start with the HELOC comparison, then review how fixed home-equity loans and cash-out refinances change payment, rate risk, and closing costs.",
      toolHref: "/heloc-calculator",
      toolLabel: "Explore home-equity options",
    },
    investment: {
      title: "Investor learning path",
      body: "Start with property cash flow, reserves, down payment, and the difference between conventional, DSCR, and specialty financing.",
      toolHref: "/tools#dscr",
      toolLabel: "Explore investor calculators",
    },
    readiness: {
      title: "Mortgage readiness path",
      body: "Start with credit, monthly obligations, stable income, available cash, and a comfortable payment before deciding whether an application makes sense.",
      toolHref: "/faq",
      toolLabel: "Read the mortgage FAQ",
    },
  };

  return researchLinks[answers.researchFocus || ""] || {
    title: "Purchase learning path",
    body: "Start with affordability, complete payment, cash to close, and the differences among conventional, FHA, VA, and assistance options.",
    toolHref: "/resources",
    toolLabel: "Browse buyer resources",
  };
}

function summaryFor(answers: Answers) {
  if (answers.goal === "refinance") {
    return [
      ["Goal", "Refinance"],
      ["Objective", answerLabel("refinanceGoal", answers.refinanceGoal)],
      ["Current mortgage", answerLabel("currentLoan", answers.currentLoan)],
      ["Ownership horizon", answerLabel("propertyHorizon", answers.propertyHorizon)],
    ];
  }
  if (answers.goal === "equity") {
    return [
      ["Goal", "Home equity"],
      ["Intended use", answerLabel("equityUse", answers.equityUse)],
      ["Priority", answerLabel("equityPriority", answers.equityPriority)],
      ["Estimated amount", answerLabel("equityAmount", answers.equityAmount)],
    ];
  }
  if (answers.goal === "purchase") {
    return [
      ["Goal", "Purchase"],
      ["Purchase type", answerLabel("purchaseType", answers.purchaseType)],
      ["Financing profile", answerLabel("financingProfile", answers.financingProfile)],
      ["Price range", answerLabel("priceRange", answers.priceRange)],
    ];
  }
  return [
    ["Goal", "Research"],
    ["Current status", answerLabel("researchStatus", answers.researchStatus)],
    ["Learning focus", answerLabel("researchFocus", answers.researchFocus)],
    ["Timeline", answerLabel("researchTimeline", answers.researchTimeline)],
  ];
}

export default function PathFinder() {
  const [stepIndex, setStepIndex] = useState(0);
  const [answers, setAnswers] = useState<Answers>({});
  const [complete, setComplete] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const flow = useMemo(
    () => [goalStep, ...(answers.goal ? branchSteps[answers.goal] : [])],
    [answers.goal],
  );
  const totalSteps = answers.goal ? flow.length + 1 : 6;
  const contactStep = Boolean(answers.goal) && stepIndex >= flow.length;
  const currentStep = contactStep ? null : flow[stepIndex] || goalStep;
  const progress = Math.min(100, ((stepIndex + 1) / totalSteps) * 100);

  const choose = (key: AnswerKey, value: string) => {
    if (key === "goal") {
      setAnswers({ goal: value as Goal });
    } else {
      setAnswers((current) => ({ ...current, [key]: value }));
    }
    setStepIndex((current) => current + 1);
  };

  const startOver = () => {
    setStepIndex(0);
    setAnswers({});
    setComplete(false);
    setError("");
  };

  if (complete) {
    const result = recommendation(answers);
    const summary = summaryFor(answers);
    return (
      <section className="path-result" aria-live="polite">
        <span className="result-check" aria-hidden="true">✓</span>
        <p className="eyebrow">Your focused next conversation</p>
        <h1>{result.title}</h1>
        <p className="path-result-lede">{result.body}</p>
        <div className="result-summary">
          {summary.map(([label, value]) => (
            <div key={label}><span>{label}</span><strong>{value}</strong></div>
          ))}
        </div>
        <div className="preview-note">Your answers were sent with your contact preferences so Dennis can review the same scenario you built.</div>
        <div className="hero-actions">
          <Link className="button button-gold" href="/contact">Book the human review</Link>
          <Link className="button button-outline-navy" href={result.toolHref}>{result.toolLabel}</Link>
          <a className="button button-navy" href={secureApplicationUrl} target="_blank" rel="noopener noreferrer">Continue to secure application</a>
          <button className="button button-outline-navy" type="button" onClick={startOver}>Start over</button>
        </div>
      </section>
    );
  }

  return (
    <section className="path-finder-card" aria-labelledby="path-step-title">
      <div className="path-progress-row">
        <span>Mortgage path finder</span>
        <strong>{answers.goal ? `Step ${stepIndex + 1} of ${totalSteps}` : "Choose a starting point"}</strong>
      </div>
      <div className="path-progress" aria-hidden="true"><span style={{ width: `${progress}%` }} /></div>
      {answers.goal ? (
        <div className="path-branch-context">
          <span>{goalLabels[answers.goal]} path</span>
          <small>Questions now adapt to this goal.</small>
        </div>
      ) : null}
      <div className="path-question" key={currentStep?.id || "contact"}>
        <p className="eyebrow">{contactStep ? "Your answers stay in context" : currentStep?.eyebrow}</p>
        <h1 id="path-step-title">{contactStep ? "Where should Dennis send the plan?" : currentStep?.title}</h1>
        {!contactStep && currentStep ? (
          <div className="choice-grid">
            {currentStep.choices.map((choice) => (
              <button type="button" className="choice-card" onClick={() => choose(currentStep.key, choice.value)} key={choice.value}>
                <span>{choice.label}</span>
                <small>{choice.detail}</small>
                <b aria-hidden="true">→</b>
              </button>
            ))}
          </div>
        ) : (
          <form className="path-contact" onSubmit={async (event) => {
            event.preventDefault();
            setSubmitting(true);
            setError("");
            const form = new FormData(event.currentTarget);
            try {
              await submitLead({
                firstName: String(form.get("firstName") || ""),
                email: String(form.get("email") || ""),
                phone: String(form.get("phone") || ""),
                segment: `${goalLabels[answers.goal || "research"]} mortgage plan`,
                goal: answers.goal || "research",
                timeline: answers.purchaseTimeline || answers.refinanceTimeline || answers.equityTimeline || answers.researchTimeline || "",
                priceRange: answers.priceRange || "",
                pathAnswers: JSON.stringify(answers),
                emailConsent: form.get("emailConsent") === "on",
                callConsent: form.get("callConsent") === "on",
                smsConsent: form.get("smsConsent") === "on",
                source: "redesign-build-my-plan",
              });
              setComplete(true);
            } catch (caught) {
              setError(caught instanceof Error ? caught.message : "The request could not be submitted.");
            } finally {
              setSubmitting(false);
            }
          }}>
            <div className="field-grid">
              <label className="field"><span>First name</span><input name="firstName" type="text" autoComplete="given-name" required /></label>
              <label className="field"><span>Email</span><input name="email" type="email" autoComplete="email" required /></label>
            </div>
            <label className="field"><span>Phone <small>(optional)</small></span><input name="phone" type="tel" autoComplete="tel" /></label>
            <label className="checkbox-field"><input name="emailConsent" type="checkbox" required /><span>Email my plan and allow Dennis to reply by email about this request. I acknowledge the Privacy Policy.</span></label>
            <label className="checkbox-field"><input name="callConsent" type="checkbox" /><span>Optional: Dennis may call me about this request.</span></label>
            <label className="checkbox-field"><input name="smsConsent" type="checkbox" /><span>Optional: Dennis may text me about this request. Message and data rates may apply. Reply STOP to opt out.</span></label>
            {error ? <p className="form-error" role="alert">{error} You can also call 850-346-8514.</p> : null}
            <button className="button button-gold" type="submit" disabled={submitting}>{submitting ? "Sending..." : "Show my plan"}</button>
            <p className="form-note">Consent is not a condition of obtaining services.</p>
          </form>
        )}
      </div>
      {stepIndex > 0 ? <button className="path-back" type="button" onClick={() => setStepIndex((current) => current - 1)}>← Back</button> : null}
    </section>
  );
}
