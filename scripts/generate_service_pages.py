#!/usr/bin/env python3
"""Generate high-intent service/location pages for DrMortgageUSA."""

from __future__ import annotations

import html
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
APPLY_URL = "https://home1st.my1003app.com/2018381/register"

COMMON_LINKS = [
    ("VA Loans Orlando", "/va-loans-orlando"),
    ("Orlando Mortgage Broker", "/orlando-mortgage-broker"),
    ("First-Time Buyer Orlando", "/first-time-homebuyer-orlando"),
    ("Refinance Florida", "/refinance-florida"),
    ("HELOC Orlando", "/heloc-orlando"),
]


PAGES = [
    {
        "slug": "va-loans-orlando",
        "title": "VA Loans Orlando | VA Mortgage Broker for Orlando Veterans | Dr.MortgageUSA",
        "description": "VA loans in Orlando for veterans and active-duty buyers. Get 0% down options, clear payment numbers, and fast VA pre-approval guidance from Dennis Ross.",
        "eyebrow": "Orlando VA Loan Help",
        "hero_title": "VA Loans in Orlando Without the Confusion",
        "hero_lead": "Dennis Ross is a Navy veteran and Florida mortgage broker who helps Orlando-area veterans use the benefit they already earned with clear numbers, fast pre-approval, and straight answers.",
        "form_heading": "Get your Orlando VA game plan",
        "form_text": "Tell me where you are in the process and I will map out your next best move.",
        "segment": "veteran",
        "source": "service-page-va-loans-orlando",
        "primary_cta": ("Start My VA Review", APPLY_URL),
        "secondary_cta": ("Call 850-346-8514", "tel:+18503468514"),
        "support_cta": ("Read the Florida VA Guide", "/blog/va-loan-guide-florida-veterans-2026"),
        "hero_stats": [("0% down", "For eligible buyers"), ("No PMI", "On VA purchase loans"), ("24-48 hrs", "Typical pre-approval timeline")],
        "sections": [
            {
                "title": "Why Orlando veterans use VA financing first",
                "body": "For many eligible buyers, VA financing is the strongest purchase loan on the board. You can often buy with no down payment, skip monthly mortgage insurance, and keep more cash for reserves, repairs, and moving costs.",
                "items": [
                    "Lower monthly payment pressure than comparable low-down-payment options",
                    "Flexible underwriting for strong borrowers who do not fit a perfect bank box",
                    "Better cash preservation when you are relocating or buying after service",
                    "Support with COE retrieval, entitlement questions, and seller strategy",
                ],
            },
            {
                "title": "What Orlando buyers need to think about",
                "body": "The Orlando market is not just about rate. Property taxes, insurance, HOA fees, condo eligibility, and seller expectations all affect what feels affordable and what gets approved.",
                "items": [
                    "Condos may need warrantability review before a VA loan works cleanly",
                    "HOA dues and insurance can change the real payment fast",
                    "Seller negotiations still matter even with a great VA benefit",
                    "A strong pre-approval letter helps veterans compete with conventional offers",
                ],
            },
        ],
        "trust_points": [
            ("Veteran-led guidance", "You are not getting generic VA talking points from someone who has never worn the uniform."),
            ("Real Orlando payment clarity", "Taxes, insurance, HOA, and concession strategy get discussed early, not after you are under contract."),
            ("Broker-level options", "Dennis can compare lenders and overlays instead of forcing every borrower into one bank product."),
        ],
        "process_points": [
            ("1", "Review eligibility and COE", "We confirm benefit status, service history, and whether you have full or partial entitlement."),
            ("2", "Build the real payment", "We run the numbers with Orlando-specific costs so you know what is comfortable, not just what is technically approvable."),
            ("3", "Issue a strong pre-approval", "You get a cleaner shopping plan, tighter expectations, and a faster path when the right house shows up."),
        ],
        "faqs": [
            ("Can I get a VA loan in Orlando with no down payment?", "Yes, if you are eligible and qualify with the lender. Many Orlando buyers use VA financing with zero down, but the payment still has to work with taxes, insurance, and HOA costs."),
            ("How fast can I get pre-approved for a VA loan?", "Most solid VA pre-approvals can move within 24 to 48 hours once documents are in. Timeline depends on income complexity and how quickly you send what is needed."),
            ("Do VA loans work for condos in Orlando?", "Sometimes. The condo has to meet approval requirements, and some buildings create financing issues. It is smart to check this before you get deep into a deal."),
            ("Can I use a VA loan more than once?", "Yes. Repeat use is possible, but entitlement and current loan status matter. Dennis can review whether you have full entitlement or need a more strategic structure."),
        ],
    },
    {
        "slug": "orlando-mortgage-broker",
        "title": "Orlando Mortgage Broker | Florida Home Loan Options | Dr.MortgageUSA",
        "description": "Looking for an Orlando mortgage broker? Compare VA, FHA, conventional, investor, and self-employed loan options with Dennis Ross at Dr.MortgageUSA.",
        "eyebrow": "Orlando Mortgage Broker",
        "hero_title": "An Orlando Mortgage Broker Who Shops the Options for You",
        "hero_lead": "If you want one bank to tell you what they sell, go to a bank. If you want Orlando loan strategy, lender comparison, and someone who can match the structure to your situation, start here.",
        "form_heading": "Get matched to the right Orlando loan path",
        "form_text": "Tell me what you are buying or refinancing and I will point you to the right next step.",
        "segment": "broker",
        "source": "service-page-orlando-mortgage-broker",
        "primary_cta": ("Compare My Options", APPLY_URL),
        "secondary_cta": ("Call 850-346-8514", "tel:+18503468514"),
        "support_cta": ("See Orlando affordability guidance", "/blog/how-much-house-afford-orlando-2026"),
        "hero_stats": [("79+ lenders", "Broker-side access"), ("Purchase + refi", "Owner-occupied and investor"), ("Florida focused", "Orlando-based guidance")],
        "sections": [
            {
                "title": "Why use a broker instead of a bank",
                "body": "The right loan is not always the one with the lowest headline rate. A broker can compare lender overlays, cost structure, documentation rules, and niche program fit before you waste time on the wrong path.",
                "items": [
                    "VA, FHA, conventional, jumbo, bank-statement, DSCR, and other specialist options",
                    "Better fit for borrowers with self-employed, commission, or layered-income scenarios",
                    "More room to solve around credit, reserves, or property-type friction",
                    "One advisor helping you compare instead of restarting with multiple institutions",
                ],
            },
            {
                "title": "What Orlando buyers and homeowners usually need",
                "body": "Most people do not need more loan jargon. They need to know which path is realistic, which costs matter, and what will hold up when they find a property.",
                "items": [
                    "First-time buyer strategy with realistic payment targets",
                    "Veteran financing that uses the VA benefit well",
                    "Refinance guidance when FHA, conventional, cash-out, or IRRRL options overlap",
                    "Investor and self-employed structuring when tax returns do not tell the whole story",
                ],
            },
        ],
        "trust_points": [
            ("Strategy before paperwork", "The call starts with what you are trying to do, not with a generic application script."),
            ("Local relevance", "Orlando taxes, insurance, condos, and HOA realities get baked into the recommendation."),
            ("Warm-traffic ready", "This page gives return visitors a clear next move instead of dropping them back on a generic homepage."),
        ],
        "process_points": [
            ("1", "Clarify the goal", "Purchase, refinance, move-up, first home, HELOC, investment, or self-employed scenario."),
            ("2", "Match the lane", "Dennis narrows the lender and program set to what actually fits your file."),
            ("3", "Move with confidence", "You get a cleaner application path and fewer surprises once the deal is live."),
        ],
        "faqs": [
            ("What does an Orlando mortgage broker actually do?", "A mortgage broker compares loan options across multiple lenders and helps match borrowers to the best fit based on goals, credit, income structure, and property type."),
            ("Is a broker only for difficult files?", "No. A broker can help straightforward borrowers too, especially when comparing cost, lender speed, and program fit matters."),
            ("Can you help first-time buyers and veterans?", "Yes. Those are two of the clearest cases for working with a broker because program choice and explanation matter a lot."),
            ("Do you only work in Orlando?", "Dennis is licensed across Florida, but Orlando and Central Florida are a major focus because local payment realities change the right strategy."),
        ],
    },
    {
        "slug": "first-time-homebuyer-orlando",
        "title": "First-Time Homebuyer Orlando | Loan Help and DPA Options | Dr.MortgageUSA",
        "description": "First-time homebuyer help in Orlando with low-down-payment loans, DPA guidance, and realistic payment planning. Speak with Dennis Ross at Dr.MortgageUSA.",
        "eyebrow": "First-Time Buyer Orlando",
        "hero_title": "First-Time Homebuyer Help for Orlando Buyers Who Want Clear Numbers",
        "hero_lead": "The first-time buyer problem is usually not motivation. It is confusion. Dennis helps Orlando buyers understand payment, down payment options, credit path, and what to do first so they can move with a real plan.",
        "form_heading": "See your first-time buyer options",
        "form_text": "Share your timeline and I will help you narrow the best starting point.",
        "segment": "first-time",
        "source": "service-page-first-time-homebuyer-orlando",
        "primary_cta": ("Check My Buying Options", APPLY_URL),
        "secondary_cta": ("Call 850-346-8514", "tel:+18503468514"),
        "support_cta": ("Review Orlando DPA programs", "/dpa"),
        "hero_stats": [("3%-3.5% down", "Common first-home paths"), ("DPA guidance", "State + local options"), ("No fluff", "Real payment planning")],
        "sections": [
            {
                "title": "What first-time buyers in Orlando usually need most",
                "body": "First-time buyers rarely need more hype. They need a realistic budget, a clean pre-approval strategy, and a way to separate useful help from noise.",
                "items": [
                    "Payment clarity with taxes, insurance, and HOA included early",
                    "A decision on FHA vs conventional vs VA if eligible",
                    "Help understanding whether DPA helps or complicates the plan",
                    "A step-by-step path that does not assume you already know the process",
                ],
            },
            {
                "title": "Where buyers lose momentum",
                "body": "A lot of first-time buyers burn weeks because the website, lender, or ad got them excited before anyone showed the real numbers. That is fixable.",
                "items": [
                    "Shopping payment by home price instead of full monthly cost",
                    "Ignoring closing costs and reserve needs",
                    "Using broad internet averages instead of Orlando-specific estimates",
                    "Waiting too long to get pre-approved before touring homes seriously",
                ],
            },
        ],
        "trust_points": [
            ("DPA conversation included", "Dennis can help you think through whether Orlando-area assistance programs actually improve your position."),
            ("Educational but direct", "This page is built for search visitors and retargeting visitors who need trust before they click apply."),
            ("Conversion clarity", "Call, apply, or ask for a plan. The next step is obvious."),
        ],
        "process_points": [
            ("1", "Set the comfort budget", "We start with a payment that fits life, not just lender max."),
            ("2", "Choose the loan lane", "FHA, conventional, VA, and assistance options get narrowed based on your actual file."),
            ("3", "Get pre-approved and shop", "You move into home search with clear expectations and cleaner leverage."),
        ],
        "faqs": [
            ("How much down payment do first-time buyers need in Orlando?", "It depends on loan type. Many first-time buyers start around 3% to 3.5% down, and some combine that with assistance programs when the math works."),
            ("Should I use down payment assistance?", "Sometimes yes, sometimes no. DPA can help with cash-to-close, but it can also affect rate, speed, and seller competitiveness. It should be reviewed as a strategy choice, not assumed."),
            ("What credit score do I need to buy my first home?", "Program rules vary, but many buyers become workable before they think they will. The bigger question is which loan type fits your score, debt, and cash position best."),
            ("How fast can a first-time buyer get pre-approved?", "A clean file can often move in a day or two once docs are in. If income or credit needs work, the better move is a game plan before trying to force a weak pre-approval."),
        ],
    },
    {
        "slug": "refinance-florida",
        "title": "Refinance Florida | Refinance Options for Florida Homeowners | Dr.MortgageUSA",
        "description": "Explore refinance options in Florida, including FHA-to-conventional, VA IRRRL, cash-out, and rate-term strategies. Get clear refinance guidance from Dr.MortgageUSA.",
        "eyebrow": "Refinance Options Florida",
        "hero_title": "Refinance Options in Florida That Start With the Math",
        "hero_lead": "A refinance should solve a problem, not just create a new payment. Dennis helps Florida homeowners look at rate-term, cash-out, FHA-to-conventional, and VA refinance paths with blunt guidance about when it actually makes sense.",
        "form_heading": "Review my refinance options",
        "form_text": "Share your timeline and whether you want lower payment, cash out, or mortgage insurance relief.",
        "segment": "repeat-buyer",
        "source": "service-page-refinance-florida",
        "primary_cta": ("Run My Refinance Review", APPLY_URL),
        "secondary_cta": ("Call 850-346-8514", "tel:+18503468514"),
        "support_cta": ("See FHA-to-conventional guidance", "/blog/refinancing-out-of-fha-to-conventional-florida"),
        "hero_stats": [("Rate-term", "Lower cost or shorter term"), ("Cash-out", "Use equity carefully"), ("VA + FHA", "Program-specific strategy")],
        "sections": [
            {
                "title": "The main refinance lanes",
                "body": "Not every refinance is about chasing rate. Sometimes the win is removing FHA mortgage insurance, changing term, accessing equity for the right reason, or simplifying debt.",
                "items": [
                    "Rate-term refinance for payment or term improvement",
                    "Cash-out refinance when the equity use is disciplined",
                    "FHA-to-conventional refinance to remove monthly MI",
                    "VA IRRRL or VA cash-out options for eligible veterans",
                ],
            },
            {
                "title": "What Florida homeowners need to watch",
                "body": "Florida refinance math is not just rate minus rate. Closing costs, break-even timing, insurance, escrow changes, and future plans all matter.",
                "items": [
                    "Break-even period relative to how long you expect to keep the loan",
                    "Whether cash-out solves a real balance-sheet problem or just moves debt around",
                    "How insurance and taxes affect the real monthly payment",
                    "Whether a HELOC is a better fit than a full refinance for the goal",
                ],
            },
        ],
        "trust_points": [
            ("Blunt refinance advice", "If the refinance does not make sense, the right move is to say that early."),
            ("Program-specific guidance", "VA, FHA, and conventional refinance lanes are not interchangeable."),
            ("Warm-traffic conversion path", "Visitors returning from Meta get a tighter refinance page instead of a general homepage."),
        ],
        "process_points": [
            ("1", "Review the current loan", "Rate, term, balance, MI, and the real reason you are considering a refinance."),
            ("2", "Compare the right structures", "Dennis looks at refinance lanes against HELOC or do-nothing options when appropriate."),
            ("3", "Move only if the math wins", "You get a clear recommendation instead of refinancing for the sake of activity."),
        ],
        "faqs": [
            ("When does refinancing in Florida make sense?", "Usually when it lowers payment meaningfully, shortens term with a real long-term win, removes mortgage insurance, or accesses equity for a disciplined purpose."),
            ("Should I refinance out of FHA into conventional?", "Often yes when equity, credit, and pricing line up well enough to remove monthly mortgage insurance without getting punished elsewhere."),
            ("Is a cash-out refinance better than a HELOC?", "Not always. A HELOC can be cleaner when you want flexibility without replacing a good first mortgage. Dennis can compare both side by side."),
            ("Can veterans refinance with a VA option?", "Yes. Eligible homeowners may use VA streamline or cash-out paths depending on the goal and the current loan."),
        ],
    },
    {
        "slug": "heloc-orlando",
        "title": "HELOC Orlando | Home Equity Line of Credit Options | Dr.MortgageUSA",
        "description": "Need a HELOC in Orlando? Compare home equity line options, payment scenarios, and next steps with Dr.MortgageUSA. Clear guidance from Dennis Ross.",
        "eyebrow": "HELOC Orlando",
        "hero_title": "HELOC Options in Orlando Without the Runaround",
        "hero_lead": "If you are trying to access equity for renovation, debt consolidation, or flexibility, the right question is not just how much you can pull. It is whether a HELOC is the best tool for the job. Dennis helps Orlando homeowners compare it honestly.",
        "form_heading": "Talk through my HELOC options",
        "form_text": "Share what you want to use the equity for and Dennis will point you to the cleanest next move.",
        "segment": "repeat-buyer",
        "source": "service-page-heloc-orlando",
        "primary_cta": ("Check My HELOC Options", APPLY_URL),
        "secondary_cta": ("Call 850-346-8514", "tel:+18503468514"),
        "support_cta": ("Use the HELOC calculator", "/heloc-calculator"),
        "hero_stats": [("Equity access", "Without replacing every loan"), ("Fast review", "Clear next-step guidance"), ("Orlando context", "Local payment realities matter")],
        "sections": [
            {
                "title": "When a HELOC makes sense",
                "body": "A HELOC can be strong when you need flexible access to equity and do not want to disturb a good first mortgage just to pull cash.",
                "items": [
                    "Renovation projects with phased draws or uncertain spend",
                    "Debt consolidation when the math is cleaner than consumer debt",
                    "Liquidity access for homeowners who want flexibility, not a full refinance",
                    "Situations where keeping a strong existing first mortgage matters",
                ],
            },
            {
                "title": "When it might not be the best fit",
                "body": "Sometimes the better answer is a home equity loan, cash-out refinance, or simply waiting. HELOCs should be matched to the actual use case, not sold as a default move.",
                "items": [
                    "If you want payment certainty and do not need a revolving line",
                    "If your first mortgage is weak enough that a full refinance could solve more problems",
                    "If the goal is debt relief but spending behavior has not changed",
                    "If property value, lien position, or credit profile makes the line expensive",
                ],
            },
        ],
        "trust_points": [
            ("Calculator plus guidance", "This page works with the existing HELOC calculator instead of leaving visitors to interpret it alone."),
            ("No equity hype", "The recommendation is about fit and risk, not just maximum draw amount."),
            ("Clear warm-traffic path", "Retargeted visitors can come back to a page built specifically for HELOC intent."),
        ],
        "process_points": [
            ("1", "Clarify the goal", "What the equity is for changes whether a HELOC is the right structure."),
            ("2", "Review equity and payment", "Dennis helps estimate access, rate range, and monthly effect."),
            ("3", "Choose the right tool", "Move forward with a HELOC only if it wins against the alternatives."),
        ],
        "faqs": [
            ("What is the difference between a HELOC and a home equity loan?", "A HELOC is a revolving line you can draw from as needed, while a home equity loan gives you a fixed lump sum with a fixed repayment structure."),
            ("Can I get a HELOC without refinancing my first mortgage?", "Yes. That is one of the main reasons homeowners choose a HELOC, especially when they already have a good first mortgage rate."),
            ("How do I know if a HELOC or cash-out refinance is better?", "The right answer depends on your current first mortgage, how much cash you need, how flexible the access should be, and how long you expect to carry the debt."),
            ("Do you also have a calculator?", "Yes. DrMortgageUSA already has a HELOC calculator, and this page is designed to turn that estimate into an actual next-step conversation."),
        ],
    },
]


def render_list(items: list[str], class_name: str) -> str:
    rendered = "".join(f"<li>{html.escape(item)}</li>" for item in items)
    return f'<ul class="{class_name}">{rendered}</ul>'


def render_cards(items: list[tuple[str, str]], class_name: str) -> str:
    return "".join(
        f"""
        <article class="{class_name}">
          <h3>{html.escape(title)}</h3>
          <p>{html.escape(text)}</p>
        </article>
        """
        for title, text in items
    )


def render_process(items: list[tuple[str, str, str]]) -> str:
    return "".join(
        f"""
        <article class="process-step">
          <div class="step-number">{html.escape(number)}</div>
          <h3>{html.escape(title)}</h3>
          <p>{html.escape(text)}</p>
        </article>
        """
        for number, title, text in items
    )


def faq_json(page: dict) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
                for question, answer in page["faqs"]
            ],
        },
        ensure_ascii=False,
    )


def page_json(page: dict) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "FinancialService",
                    "@id": f"https://drmortgageusa.com/{page['slug']}#service",
                    "name": "Dr.MortgageUSA - Dennis Ross",
                    "url": f"https://drmortgageusa.com/{page['slug']}",
                    "telephone": "+1-850-346-8514",
                    "image": "https://drmortgageusa.com/dennis-ross-headshot.png",
                    "areaServed": [
                        {"@type": "City", "name": "Orlando"},
                        {"@type": "State", "name": "Florida"},
                    ],
                    "serviceType": page["hero_title"],
                    "sameAs": [
                        "https://www.instagram.com/dr.mortgageusa/",
                        "https://www.facebook.com/DrMortgageUSA",
                    ],
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://drmortgageusa.com/"},
                        {"@type": "ListItem", "position": 2, "name": page["hero_title"], "item": f"https://drmortgageusa.com/{page['slug']}"},
                    ],
                },
            ],
        },
        ensure_ascii=False,
    )


def render_page(page: dict) -> str:
    quicklink_parts = []
    for label, href in COMMON_LINKS:
        active_class = ' class="active"' if href == "/" + page["slug"] else ""
        quicklink_parts.append(f'<a href="{href}"{active_class}>{label}</a>')
    quicklinks = "".join(quicklink_parts)
    sections = "".join(
        f"""
        <article class="section-card">
          <h2>{html.escape(section['title'])}</h2>
          <p>{html.escape(section['body'])}</p>
          {render_list(section['items'], 'checklist')}
        </article>
        """
        for section in page["sections"]
    )
    faq_cards = render_cards(page["faqs"], "faq-item")
    trust_cards = render_cards(page["trust_points"], "trust-card")
    process_cards = render_process(page["process_points"])
    stat_cards = "".join(
        f'<div class="stat"><strong>{html.escape(stat)}</strong><span>{html.escape(text)}</span></div>'
        for stat, text in page["hero_stats"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(page['title'])}</title>
  <meta name="description" content="{html.escape(page['description'])}">
  <meta name="author" content="Dennis Ross, NMLS #2018381">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="https://drmortgageusa.com/{page['slug']}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{html.escape(page['title'])}">
  <meta property="og:description" content="{html.escape(page['description'])}">
  <meta property="og:url" content="https://drmortgageusa.com/{page['slug']}">
  <meta property="og:image" content="https://drmortgageusa.com/dennis-ross-headshot.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(page['title'])}">
  <meta name="twitter:description" content="{html.escape(page['description'])}">
  <link rel="icon" type="image/png" href="/favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/landing-pages.css">
  <script type="application/ld+json">{page_json(page)}</script>
  <script type="application/ld+json">{faq_json(page)}</script>
  <script src="/site-tracking.js" defer></script>
</head>
<body data-page-category="service" data-page-intent="{html.escape(page['segment'])}">
  <div class="shell">
    <header class="topbar">
      <div class="container topbar-inner">
        <a class="brand" href="/">
          <img src="/logo.png" alt="Dr.MortgageUSA logo" width="46" height="46">
          <span class="brand-copy">
            Dr.MortgageUSA
            <small>Dennis Ross | Orlando + Florida</small>
          </span>
        </a>
        <nav class="nav-links" aria-label="Primary">
          <a href="/">Home</a>
          <a href="/dpa">DPA Programs</a>
          <a href="/heloc-calculator">HELOC Calculator</a>
          <a href="/blog">Blog</a>
          <a href="{APPLY_URL}" data-track="apply" data-content-category="{page['source']}">Apply Now</a>
        </nav>
      </div>
    </header>

    <main class="container">
      <section class="hero">
        <div class="quicklinks" aria-label="Popular service pages">
          {quicklinks}
        </div>

        <div class="hero-grid">
          <div class="hero-copy">
            <div class="eyebrow">{html.escape(page['eyebrow'])}</div>
            <h1>{html.escape(page['hero_title'])}</h1>
            <p class="lead">{html.escape(page['hero_lead'])}</p>
            <div class="hero-actions">
              <a class="button" href="{page['primary_cta'][1]}" data-track="apply" data-content-category="{page['source']}">{html.escape(page['primary_cta'][0])}</a>
              <a class="button-secondary" href="{page['secondary_cta'][1]}" data-track="call" data-content-category="{page['source']}">{html.escape(page['secondary_cta'][0])}</a>
            </div>
            <a href="{page['support_cta'][1]}" style="color: var(--gold-soft); text-decoration: none; font-weight: 700;">{html.escape(page['support_cta'][0])}</a>
            <div class="microproof">
              {stat_cards}
            </div>
          </div>

          <aside class="hero-card">
            <h2>{html.escape(page['form_heading'])}</h2>
            <p>{html.escape(page['form_text'])}</p>
            <form class="lead-form" data-lead-form data-segment="{html.escape(page['segment'])}" data-source="{html.escape(page['source'])}" data-success-message="Thanks. Dennis will reach out with the right next step.">
              <div class="field-grid">
                <input type="text" name="firstName" placeholder="First name" required>
                <input type="email" name="email" placeholder="Email" required>
              </div>
              <div class="field-grid">
                <input type="tel" name="phone" placeholder="Phone number">
                <select name="timeline">
                  <option value="">Timeline</option>
                  <option value="asap">ASAP</option>
                  <option value="0-30">Within 30 days</option>
                  <option value="1-3 months">1-3 months</option>
                  <option value="3-6 months">3-6 months</option>
                  <option value="6+ months">6+ months</option>
                </select>
              </div>
              <input type="hidden" name="segment" value="{html.escape(page['segment'])}">
              <input type="hidden" name="source" value="{html.escape(page['source'])}">
              <button class="button" type="submit">{html.escape(page['form_heading'])}</button>
              <p data-form-message></p>
              <p class="form-note">No pressure. No generic call-center script. Just the right next step for your scenario.</p>
            </form>
          </aside>
        </div>
      </section>

      <section class="section">
        <div class="section-grid">
          {sections}
        </div>
      </section>

      <section class="trust">
        <h2>Why this page exists</h2>
        <div class="trust-grid">
          {trust_cards}
        </div>
      </section>

      <section class="process">
        <h2>What happens next</h2>
        <div class="process-grid">
          {process_cards}
        </div>
      </section>

      <section class="faq">
        <h2>Frequently asked questions</h2>
        <div class="faq-grid">
          {faq_cards}
        </div>
      </section>

      <section class="cta-band">
        <h2 style="margin-top: 0;">Ready for the next step?</h2>
        <p>This page is built to help both search visitors and returning retargeting traffic convert with a clearer next move.</p>
        <div class="hero-actions" style="margin-bottom: 0;">
          <a class="button" href="{APPLY_URL}" data-track="apply" data-content-category="{page['source']}">Apply Securely</a>
          <a class="button-secondary" href="tel:+18503468514" data-track="call" data-content-category="{page['source']}">Call Dennis</a>
        </div>
      </section>
    </main>

    <footer class="footer">
      <div class="container">
        <strong style="display: block; margin-bottom: 6px;">Dr.MortgageUSA | Dennis Ross | NMLS #2018381</strong>
        <div>Licensed in Florida | Powered by Home1st Lending, LLC NMLS #1418</div>
        <div class="footer-links">
          <a href="/">Home</a>
          <a href="/blog">Blog</a>
          <a href="/dpa">DPA Programs</a>
          <a href="/heloc-calculator">HELOC Calculator</a>
          <a href="tel:+18503468514">850-346-8514</a>
        </div>
      </div>
    </footer>
  </div>
</body>
</html>
"""


def main() -> None:
    for page in PAGES:
        output_path = BASE_DIR / f"{page['slug']}.html"
        output_path.write_text(render_page(page), encoding="utf-8")
        print(f"Wrote {output_path.name}")


if __name__ == "__main__":
    main()
