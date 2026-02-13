import re, os, json

print("=" * 60)
print("  Section 4: Content Strategy - drmortgageusa.com")
print("=" * 60)

# ============================================================
# 4.2: VISIBLE FAQ SECTION
# ============================================================
print("\n--- 4.2: Building FAQ Section ---")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

faqs = [
    ("What credit score do I need for a mortgage in Florida?",
     "It depends on the loan type. Conventional loans typically require a 620 minimum. FHA loans go as low as 580 with 3.5% down, or 500 with 10% down. VA loans have no official minimum, but most lenders want 580+. I work with borrowers across the credit spectrum and can help you find the right program for your situation."),
    ("How much down payment do I need to buy a home?",
     "Less than most people think. Conventional loans start at 3% down. FHA loans require 3.5% down. VA loans and USDA loans offer 0% down for eligible borrowers. There are also Florida-specific down payment assistance programs that can cover part or all of your down payment. I can walk you through every option."),
    ("What is the difference between FHA and conventional loans?",
     "FHA loans are government-insured, have lower credit requirements (580+), and require 3.5% down, but charge mortgage insurance for the life of the loan. Conventional loans require higher credit (620+) but let you drop mortgage insurance once you hit 20% equity. Your best choice depends on your credit score, down payment, and how long you plan to stay in the home."),
    ("Do you serve all of Florida?",
     "Yes. I am licensed to serve borrowers throughout the entire state of Florida, from Pensacola to Key West. Most of my process is digital, so we can work together regardless of where you are in the state. I am based in the Florida panhandle but serve clients in Orlando, Tampa, Miami, Jacksonville, and everywhere in between."),
    ("How long does the mortgage closing process take?",
     "Typically 30 to 45 days from contract to closing. Some loans can close faster. VA loans sometimes take a few extra days due to the VA appraisal process. The biggest factor is how quickly you provide your documentation. I give you a clear checklist upfront so there are no surprises."),
    ("What are VA loan benefits for veterans?",
     "VA loans are one of the best mortgage products available. Benefits include 0% down payment, no private mortgage insurance (PMI), competitive interest rates, and limited closing costs. As a Navy veteran myself with 15 years of service, I understand the VA loan process inside and out and can guide you through it."),
    ("How do I get pre-approved for a mortgage?",
     "Start by clicking the Apply Online button on this site or call me directly at 850-346-8514. I will review your income, assets, credit, and debts to determine how much you qualify for. Pre-approval typically takes 24 to 48 hours and gives you a letter that shows sellers you are a serious buyer."),
    ("What documents do I need to apply for a mortgage?",
     "The basics: two years of W-2s or tax returns, two months of bank statements, 30 days of pay stubs, and a valid government ID. Self-employed borrowers need two years of full tax returns including all schedules. I provide a complete checklist when we start so you know exactly what to gather."),
    ("Can I buy a home if I am self-employed?",
     "Yes. Self-employed borrowers have several loan options. Most programs require two years of tax returns to verify income. Bank statement loans are another option where we use 12 to 24 months of deposits instead of tax returns. I work with many self-employed clients and know how to present your income in the strongest way."),
    ("What is PMI and how do I avoid it?",
     "Private Mortgage Insurance (PMI) is required on conventional loans when your down payment is less than 20%. It typically costs 0.5% to 1% of the loan amount per year. You can avoid PMI by putting 20% down, using a VA loan (no PMI ever), or requesting PMI removal once you reach 20% equity. Some lender-paid PMI options are also available."),
    ("What are closing costs and how much should I expect?",
     "Closing costs typically run 2% to 5% of the loan amount. They include lender fees, appraisal, title insurance, recording fees, and prepaid taxes and insurance. On a $300,000 loan, expect roughly $6,000 to $15,000. I provide a detailed Loan Estimate within three days of application so you see every cost upfront. In some cases, sellers can contribute toward your closing costs."),
    ("What is the difference between a fixed-rate and adjustable-rate mortgage?",
     "A fixed-rate mortgage locks your interest rate for the entire loan term, usually 15 or 30 years. Your payment never changes. An adjustable-rate mortgage (ARM) starts with a lower rate for a set period (usually 5 or 7 years), then adjusts annually based on market rates. ARMs can save money if you plan to sell or refinance within that initial period."),
    ("Can I buy a home with student loan debt?",
     "Yes. Student loans do affect your debt-to-income ratio, but they do not disqualify you. FHA, VA, and conventional loans all have specific guidelines for how student loan payments are calculated. Income-driven repayment plans can help keep your ratios manageable. I have helped many borrowers with student debt become homeowners."),
    ("What is a USDA loan and do I qualify?",
     "USDA loans offer 0% down payment for homes in eligible rural and suburban areas. Many areas outside major Florida cities qualify, including parts of counties around Orlando, Tampa, and Jacksonville. Income limits apply based on household size and county. I can check your property and income eligibility in minutes."),
    ("Why should I use a mortgage broker instead of a bank?",
     "A bank offers only their own products. As a mortgage broker, I shop dozens of lenders to find you the best rate and terms. I also have access to specialty programs that banks do not offer, like bank statement loans, non-QM products, and niche VA programs. My job is to be your advocate and find the best deal, not push a single lender's products.")
]

# Build the FAQ accordion HTML
faq_items = ""
for i, (q, a) in enumerate(faqs):
    open_class = "open" if i == 0 else ""
    display = "block" if i == 0 else "none"
    rotate = "rotate-180" if i == 0 else ""
    faq_items += f'''
            <div class="faq-item bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden transition-all duration-300 hover:shadow-md">
                <button class="faq-toggle w-full text-left px-6 py-5 flex items-center justify-between gap-4 cursor-pointer" onclick="this.parentElement.classList.toggle('open');var a=this.nextElementSibling;a.style.display=a.style.display==='block'?'none':'block';this.querySelector('svg').classList.toggle('rotate-180');">
                    <span class="font-semibold text-gray-900 text-base md:text-lg pr-4">{q}</span>
                    <svg class="w-5 h-5 text-gold flex-shrink-0 transition-transform duration-300 {rotate}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </button>
                <div class="faq-answer px-6 pb-5 text-gray-600 leading-relaxed" style="display:{display};">
                    <p>{a}</p>
                </div>
            </div>'''

faq_section = f'''
    <!-- FAQ Section -->
    <section id="faq" class="py-20 bg-gray-50">
        <div class="container mx-auto px-4 max-w-4xl">
            <div class="text-center mb-12">
                <h2 class="font-display font-bold text-3xl md:text-4xl text-gray-900 mb-4">Frequently Asked Questions</h2>
                <p class="text-gray-600 text-lg max-w-2xl mx-auto">Get answers to the most common mortgage questions Florida homebuyers ask. Still have questions? Call me at <a href="tel:+18503468514" class="text-gold font-semibold hover:underline">850-346-8514</a>.</p>
            </div>
            <div class="space-y-3">
{faq_items}
            </div>
            <div class="text-center mt-10">
                <a href="#path-finder" class="inline-block text-white font-bold py-3 px-8 rounded-full shadow-lg transition-all duration-300 hover:scale-105" style="background-color:#D4AF37;">Get Your Free Quote Today</a>
            </div>
        </div>
    </section>
'''

# Insert FAQ section after the rates section
# Find the closing tag of the rates section
rates_end = html.find('</section>', html.find('id="rates"'))
if rates_end != -1:
    insert_pos = rates_end + len('</section>')
    html = html[:insert_pos] + '\n' + faq_section + html[insert_pos:]
    print(f"  FAQ section inserted after rates section ({len(faqs)} questions)")
else:
    print("  WARNING: Could not find rates section end")

# Also add FAQ link to nav if not present
if 'href="#faq"' not in html:
    # Find the nav links area - look for the last nav link before </nav>
    nav_link = '<a href="#faq" class="text-gray-300 hover:text-gold transition-colors">FAQ</a>'
    # Insert before the About link in the nav
    if 'href="#about"' in html:
        html = html.replace('href="#about"', 'href="#faq" class="text-gray-300 hover:text-gold transition-colors">FAQ</a>\n                    <a href="#about"', 1)
        print("  FAQ link added to navigation")
    else:
        print("  Could not add FAQ nav link")

# ============================================================
# Update FAQPage Schema with all 15 questions
# ============================================================
print("\n--- Updating FAQPage Schema ---")

schema_faqs = []
for q, a in faqs:
    schema_faqs.append({
        "@type": "Question",
        "name": q,
        "acceptedAnswer": {
            "@type": "Answer",
            "text": a
        }
    })

new_faq_schema = json.dumps({
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": schema_faqs
}, indent=2)

# Replace existing FAQPage schema
faq_pattern = r'<script type="application/ld\+json">\s*\{[^<]*"@type"\s*:\s*"FAQPage"[^<]*</script>'
match = re.search(faq_pattern, html, re.DOTALL)
if match:
    old_schema = match.group(0)
    new_schema_tag = f'<script type="application/ld+json">\n{new_faq_schema}\n</script>'
    html = html.replace(old_schema, new_schema_tag)
    print(f"  FAQPage schema updated: 6 -> {len(faqs)} questions")
else:
    print("  WARNING: Could not find existing FAQPage schema to replace")

# Save index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"  index.html saved ({len(html.encode('utf-8')):,} bytes)")

# ============================================================
# 4.1: BLOG INFRASTRUCTURE
# ============================================================
print("\n--- 4.1: Building Blog Infrastructure ---")

# Create blog directory
os.makedirs('blog_posts', exist_ok=True)

# Create blog post template
blog_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Dr.MortgageUSA Blog</title>
    <meta name="description" content="{description}">
    <meta name="author" content="Dennis Ross">
    <link rel="canonical" href="https://drmortgageusa.com/blog/{slug}">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:url" content="https://drmortgageusa.com/blog/{slug}">
    <meta property="og:site_name" content="Dr.MortgageUSA">
    <meta name="twitter:card" content="summary_large_image">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .bg-navy {{ background-color: #1a1a2e; }}
        .text-gold {{ color: #D4AF37; }}
        .bg-gold {{ background-color: #D4AF37; }}
        .prose h2 {{ font-size: 1.5rem; font-weight: 700; margin-top: 2rem; margin-bottom: 1rem; color: #1a1a2e; }}
        .prose h3 {{ font-size: 1.25rem; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem; color: #1a1a2e; }}
        .prose p {{ margin-bottom: 1rem; line-height: 1.8; color: #374151; }}
        .prose ul {{ list-style-type: disc; padding-left: 1.5rem; margin-bottom: 1rem; }}
        .prose li {{ margin-bottom: 0.5rem; color: #374151; }}
        .prose strong {{ color: #1a1a2e; }}
    </style>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": "{title}",
        "description": "{description}",
        "author": {{
            "@type": "Person",
            "name": "Dennis Ross",
            "jobTitle": "Mortgage Broker",
            "url": "https://drmortgageusa.com"
        }},
        "publisher": {{
            "@type": "Organization",
            "name": "Dr.MortgageUSA"
        }},
        "datePublished": "{date}",
        "dateModified": "{date}",
        "url": "https://drmortgageusa.com/blog/{slug}"
    }}
    </script>
</head>
<body class="bg-gray-50">
    <!-- Nav -->
    <nav class="bg-navy text-white py-4 sticky top-0 z-50">
        <div class="container mx-auto px-4 flex items-center justify-between">
            <a href="/" class="text-xl font-bold">Dr.MortgageUSA</a>
            <div class="flex items-center gap-6">
                <a href="/blog" class="text-gray-300 hover:text-white transition-colors">Blog</a>
                <a href="/#rates" class="text-gray-300 hover:text-white transition-colors">Rates</a>
                <a href="/#faq" class="text-gray-300 hover:text-white transition-colors">FAQ</a>
                <a href="tel:+18503468514" class="bg-gold text-navy font-bold py-2 px-5 rounded-full text-sm hover:scale-105 transition-transform">Call Now</a>
            </div>
        </div>
    </nav>

    <!-- Article -->
    <article class="py-12">
        <div class="container mx-auto px-4 max-w-3xl">
            <div class="mb-8">
                <a href="/blog" class="text-gold hover:underline text-sm font-semibold">&larr; Back to Blog</a>
            </div>
            <h1 class="font-bold text-3xl md:text-4xl text-gray-900 mb-4 leading-tight">{title}</h1>
            <div class="flex items-center gap-3 text-sm text-gray-500 mb-8">
                <span>By Dennis Ross, NMLS #2018381</span>
                <span>|</span>
                <time datetime="{date}">{date_display}</time>
            </div>
            <div class="prose max-w-none">
                {content}
            </div>

            <!-- CTA Box -->
            <div class="mt-12 bg-navy text-white rounded-2xl p-8 text-center">
                <h3 class="text-2xl font-bold mb-3">Ready to Get Started?</h3>
                <p class="text-gray-300 mb-6">Get personalized numbers and expert guidance from a Navy veteran who has helped 600+ Florida families.</p>
                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <a href="tel:+18503468514" class="bg-gold text-navy font-bold py-3 px-8 rounded-full hover:scale-105 transition-transform">Call 850-346-8514</a>
                    <a href="/" class="border-2 border-gold text-gold font-bold py-3 px-8 rounded-full hover:bg-gold hover:text-navy transition-all">Apply Online</a>
                </div>
            </div>
        </div>
    </article>

    <!-- Footer -->
    <footer class="bg-navy text-gray-400 py-8 mt-12">
        <div class="container mx-auto px-4 text-center text-sm">
            <p>Dennis Ross | NMLS #2018381 | Powered by Home1st Lending, LLC NMLS #1418</p>
            <p class="mt-2">Licensed in Florida | Equal Housing Lender</p>
        </div>
    </footer>
</body>
</html>'''

# Save template
with open('blog_template.html', 'w') as f:
    f.write(blog_template)
print("  Blog template created")

# ============================================================
# Create Blog Posts
# ============================================================
posts = [
    {
        "slug": "va-loan-guide-florida-veterans-2026",
        "title": "VA Loan Guide for Florida Veterans: Everything You Need to Know in 2026",
        "description": "Complete guide to VA loans in Florida. Learn about 0% down payment, no PMI, eligibility requirements, and how to use your VA benefits to buy a home.",
        "date": "2026-02-13",
        "date_display": "February 13, 2026",
        "content": """
                <p>If you served in the military, the VA loan is one of the most powerful homebuying tools available to you. As a Navy veteran with 15 years of service and two combat deployments, I have used VA loans myself and helped hundreds of fellow veterans do the same.</p>

                <p>Here is everything you need to know about using a VA loan to buy a home in Florida in 2026.</p>

                <h2>What Is a VA Loan?</h2>
                <p>A VA loan is a mortgage backed by the U.S. Department of Veterans Affairs. The VA does not lend money directly. Instead, it guarantees a portion of the loan, which allows lenders to offer better terms to eligible veterans, active-duty service members, and surviving spouses.</p>

                <h2>Top VA Loan Benefits</h2>
                <ul>
                    <li><strong>Zero down payment.</strong> This is the biggest advantage. You can finance 100% of the home price.</li>
                    <li><strong>No private mortgage insurance (PMI).</strong> Conventional loans charge PMI if you put less than 20% down. VA loans never charge it.</li>
                    <li><strong>Competitive interest rates.</strong> VA rates are typically 0.25% to 0.5% lower than conventional rates.</li>
                    <li><strong>Limited closing costs.</strong> The VA caps what lenders can charge veterans in fees.</li>
                    <li><strong>No prepayment penalty.</strong> You can pay off your loan early without any fees.</li>
                    <li><strong>Easier qualification.</strong> VA loans are more flexible on credit score and debt-to-income ratio requirements.</li>
                </ul>

                <h2>Who Is Eligible for a VA Loan?</h2>
                <p>You may be eligible if you meet one of these service requirements:</p>
                <ul>
                    <li>90 consecutive days of active service during wartime</li>
                    <li>181 consecutive days of active service during peacetime</li>
                    <li>6 years in the National Guard or Reserves</li>
                    <li>You are the spouse of a service member who died in the line of duty or from a service-connected disability</li>
                </ul>
                <p>You will need a Certificate of Eligibility (COE) to prove your eligibility. I can help you obtain this quickly, often in minutes through the VA's online system.</p>

                <h2>VA Loan Limits in Florida (2026)</h2>
                <p>For veterans with full entitlement (meaning you have never used your VA loan benefit, or you have paid off and sold a previous VA-financed home), there is no loan limit. You can borrow as much as a lender will approve you for with zero down payment.</p>
                <p>If you have reduced entitlement (you still have an active VA loan), county loan limits apply. In most Florida counties, the 2026 conforming limit is $806,500.</p>

                <h2>The VA Funding Fee</h2>
                <p>VA loans do have a one-time funding fee that ranges from 1.25% to 3.3% of the loan amount, depending on your service type and down payment. This fee can be rolled into the loan. Veterans receiving VA disability compensation are exempt from the funding fee entirely.</p>

                <h2>VA Loans in Florida: What Makes It Different?</h2>
                <p>Florida is one of the most veteran-friendly states in the country. Additional state-level benefits include no state income tax, Florida property tax exemptions for disabled veterans, and a large network of VA healthcare facilities throughout the state.</p>
                <p>The Florida real estate market in 2026 continues to offer solid value compared to states like California and New York, making your VA loan benefits stretch further here.</p>

                <h2>How to Get Started</h2>
                <p>Getting started with a VA loan is simpler than most veterans expect. Call me at 850-346-8514 or click Apply Online on this site. I will pull your COE, review your finances, and have you pre-approved within 24 to 48 hours. From there, you can house-hunt with confidence knowing exactly what you can afford.</p>
        """
    },
    {
        "slug": "first-time-homebuyer-florida-2026",
        "title": "First-Time Homebuyer Guide: How to Buy Your First Home in Florida (2026)",
        "description": "Step-by-step guide for first-time homebuyers in Florida. Learn about down payment assistance, loan options, credit requirements, and how to navigate the process.",
        "date": "2026-02-13",
        "date_display": "February 13, 2026",
        "content": """
                <p>Buying your first home in Florida is one of the biggest financial decisions you will make. It can feel overwhelming, but with the right preparation and guidance, the process is very manageable. I have helped over 600 families navigate this exact process.</p>

                <p>Here is your step-by-step roadmap to homeownership in Florida.</p>

                <h2>Step 1: Check Your Credit Score</h2>
                <p>Your credit score determines which loan programs you qualify for and what interest rate you will receive. Here is the general breakdown:</p>
                <ul>
                    <li><strong>740+:</strong> Best rates on conventional loans</li>
                    <li><strong>620-739:</strong> Qualifies for conventional loans at slightly higher rates</li>
                    <li><strong>580-619:</strong> FHA loans with 3.5% down payment</li>
                    <li><strong>500-579:</strong> FHA loans with 10% down payment</li>
                </ul>
                <p>If your score is below where you want it, do not panic. I can review your credit report and give you specific steps to improve it, often by 20 to 50 points within 30 to 60 days.</p>

                <h2>Step 2: Determine How Much You Can Afford</h2>
                <p>A common rule of thumb is that your total monthly housing payment (mortgage, taxes, insurance) should not exceed 28% to 33% of your gross monthly income. On a $60,000 salary, that means a housing payment of roughly $1,400 to $1,650 per month.</p>
                <p>Use the mortgage calculator on my website to get a quick estimate, then call me for personalized numbers based on your complete financial picture.</p>

                <h2>Step 3: Get Pre-Approved</h2>
                <p>Pre-approval is different from pre-qualification. Pre-approval means a lender has verified your income, assets, and credit and is willing to lend you a specific amount. Sellers in Florida take pre-approved buyers seriously. Without it, your offers will likely be ignored.</p>

                <h2>Step 4: Choose the Right Loan Program</h2>
                <p>First-time buyers in Florida have several options:</p>
                <ul>
                    <li><strong>Conventional (3% down):</strong> Best for borrowers with 620+ credit scores and stable income</li>
                    <li><strong>FHA (3.5% down):</strong> More flexible on credit. Great for scores between 580 and 619</li>
                    <li><strong>VA (0% down):</strong> For veterans and active military. No PMI</li>
                    <li><strong>USDA (0% down):</strong> For homes in eligible rural areas. Income limits apply</li>
                </ul>

                <h2>Step 5: Florida Down Payment Assistance Programs</h2>
                <p>Florida offers several programs to help first-time buyers:</p>
                <ul>
                    <li><strong>Florida Hometown Heroes:</strong> Up to 5% of the loan amount for down payment and closing costs for workers in over 50 professions</li>
                    <li><strong>Florida Assist:</strong> Up to $10,000 as a deferred second mortgage at 0% interest</li>
                    <li><strong>HFA Preferred/Advantage:</strong> Below-market rates with grant funding for down payment</li>
                </ul>
                <p>I will check your eligibility for all available programs and stack them when possible to minimize your out-of-pocket costs.</p>

                <h2>Step 6: Find a Home and Make an Offer</h2>
                <p>Work with a local real estate agent who knows your target area. With your pre-approval letter in hand, you can make strong offers quickly. In competitive Florida markets, speed matters.</p>

                <h2>Step 7: Close on Your New Home</h2>
                <p>After your offer is accepted, the typical timeline is 30 to 45 days. During this time, I coordinate the appraisal, underwriting, title work, and insurance. I keep you updated at every step so there are no surprises at the closing table.</p>

                <h2>Get Started Today</h2>
                <p>The hardest part of buying your first home is taking the first step. Call me at 850-346-8514 or start the 60-Second Home Qualifier on my website. No credit check, no obligation. Just clear numbers and honest guidance.</p>
        """
    },
    {
        "slug": "fha-vs-conventional-loan-florida",
        "title": "FHA vs. Conventional Loan in Florida: Which One Is Right for You?",
        "description": "Compare FHA and conventional loans side by side. Learn the differences in down payment, credit score requirements, mortgage insurance, and which is better for Florida homebuyers.",
        "date": "2026-02-13",
        "date_display": "February 13, 2026",
        "content": """
                <p>This is one of the most common questions I get from Florida homebuyers: should I go FHA or conventional? The answer depends on your credit score, down payment, and long-term plans. Let me break it down clearly.</p>

                <h2>Quick Comparison</h2>
                <p>Here are the key differences at a glance:</p>
                <ul>
                    <li><strong>Minimum credit score:</strong> FHA requires 580 (or 500 with 10% down). Conventional requires 620.</li>
                    <li><strong>Down payment:</strong> FHA requires 3.5%. Conventional starts at 3%.</li>
                    <li><strong>Mortgage insurance:</strong> FHA charges it for the life of the loan. Conventional lets you drop it at 20% equity.</li>
                    <li><strong>Loan limits (2026):</strong> FHA limit in most Florida counties is $524,225. Conventional limit is $806,500.</li>
                    <li><strong>Debt-to-income ratio:</strong> FHA allows up to 57% in some cases. Conventional typically caps at 50%.</li>
                </ul>

                <h2>When FHA Is the Better Choice</h2>
                <p>Choose FHA if:</p>
                <ul>
                    <li>Your credit score is between 580 and 619</li>
                    <li>You have had a recent credit event (bankruptcy, foreclosure, short sale)</li>
                    <li>Your debt-to-income ratio is on the higher side</li>
                    <li>You need a more flexible qualification process</li>
                </ul>
                <p>FHA loans are designed to help borrowers who might not qualify for conventional financing. The tradeoff is permanent mortgage insurance, which adds to your monthly payment.</p>

                <h2>When Conventional Is the Better Choice</h2>
                <p>Choose conventional if:</p>
                <ul>
                    <li>Your credit score is 620 or higher (680+ for the best rates)</li>
                    <li>You can put 5% or more down</li>
                    <li>You plan to stay in the home long enough to build 20% equity and drop PMI</li>
                    <li>You are buying a condo (some condo complexes are not FHA-approved)</li>
                    <li>You need a higher loan amount (above FHA limits)</li>
                </ul>

                <h2>The Mortgage Insurance Factor</h2>
                <p>This is where the real cost difference lives. FHA mortgage insurance (MIP) has two parts: an upfront premium of 1.75% of the loan amount (rolled into the loan) and an annual premium of 0.55% paid monthly. On a $300,000 loan, that is about $137 per month for the life of the loan.</p>
                <p>Conventional PMI ranges from $75 to $200 per month on the same loan, but it goes away once you reach 20% equity. Over a 30-year period, dropping PMI can save you tens of thousands of dollars.</p>

                <h2>A Real Example</h2>
                <p>Let me run the numbers on a $300,000 home purchase in Florida:</p>
                <ul>
                    <li><strong>FHA (3.5% down, 580 credit):</strong> $10,500 down, ~$2,050/month total payment (includes MIP for life)</li>
                    <li><strong>Conventional (3% down, 680 credit):</strong> $9,000 down, ~$1,975/month total payment (PMI drops at 20% equity)</li>
                    <li><strong>Conventional (5% down, 740 credit):</strong> $15,000 down, ~$1,890/month total payment (lower PMI, drops at 20%)</li>
                </ul>

                <h2>My Recommendation</h2>
                <p>Do not guess. Let me run both scenarios with your actual numbers. Sometimes borrowers with a 620 credit score are better off on conventional. Sometimes borrowers with a 700 score get a better deal on FHA due to specific pricing factors. Every situation is different.</p>
                <p>Call me at 850-346-8514 or use the Apply Online button. I will compare both options side by side and show you exactly which one saves you more money.</p>
        """
    }
]

# Generate blog post HTML files
for post in posts:
    post_html = blog_template.format(**post)
    filepath = f"blog_posts/{post['slug']}.html"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(post_html)
    print(f"  Blog post created: /blog/{post['slug']}")

# Create blog index page
blog_index_cards = ""
for post in posts:
    blog_index_cards += f'''
            <a href="/blog/{post['slug']}" class="block bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
                <div class="p-6">
                    <time class="text-sm text-gold font-semibold">{post['date_display']}</time>
                    <h2 class="text-xl font-bold text-gray-900 mt-2 mb-3">{post['title']}</h2>
                    <p class="text-gray-600 text-sm leading-relaxed">{post['description']}</p>
                    <span class="inline-block mt-4 text-gold font-semibold text-sm">Read More &rarr;</span>
                </div>
            </a>'''

blog_index = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mortgage Blog | Dr.MortgageUSA - Dennis Ross</title>
    <meta name="description" content="Florida mortgage tips, guides, and advice from Dennis Ross, Navy veteran and licensed mortgage broker. Learn about VA loans, FHA, conventional, and more.">
    <link rel="canonical" href="https://drmortgageusa.com/blog">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .bg-navy {{ background-color: #1a1a2e; }}
        .text-gold {{ color: #D4AF37; }}
        .bg-gold {{ background-color: #D4AF37; }}
    </style>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "Dr.MortgageUSA Blog",
        "description": "Florida mortgage tips, guides, and advice",
        "url": "https://drmortgageusa.com/blog",
        "author": {{
            "@type": "Person",
            "name": "Dennis Ross"
        }}
    }}
    </script>
</head>
<body class="bg-gray-50">
    <nav class="bg-navy text-white py-4 sticky top-0 z-50">
        <div class="container mx-auto px-4 flex items-center justify-between">
            <a href="/" class="text-xl font-bold">Dr.MortgageUSA</a>
            <div class="flex items-center gap-6">
                <a href="/" class="text-gray-300 hover:text-white transition-colors">Home</a>
                <a href="/#rates" class="text-gray-300 hover:text-white transition-colors">Rates</a>
                <a href="/#faq" class="text-gray-300 hover:text-white transition-colors">FAQ</a>
                <a href="tel:+18503468514" class="bg-gold text-navy font-bold py-2 px-5 rounded-full text-sm hover:scale-105 transition-transform">Call Now</a>
            </div>
        </div>
    </nav>

    <div class="py-16">
        <div class="container mx-auto px-4 max-w-4xl">
            <div class="text-center mb-12">
                <h1 class="font-bold text-3xl md:text-4xl text-gray-900 mb-4">Mortgage Tips &amp; Guides</h1>
                <p class="text-gray-600 text-lg">Straight talk about mortgages in Florida. No jargon, no fluff.</p>
            </div>
            <div class="grid gap-6">
{blog_index_cards}
            </div>
        </div>
    </div>

    <footer class="bg-navy text-gray-400 py-8 mt-12">
        <div class="container mx-auto px-4 text-center text-sm">
            <p>Dennis Ross | NMLS #2018381 | Powered by Home1st Lending, LLC NMLS #1418</p>
            <p class="mt-2">Licensed in Florida | Equal Housing Lender</p>
        </div>
    </footer>
</body>
</html>'''

with open('blog_posts/index.html', 'w', encoding='utf-8') as f:
    f.write(blog_index)
print("  Blog index page created: /blog")

# ============================================================
# Add blog routes to app.py
# ============================================================
print("\n--- Adding Blog Routes to app.py ---")

with open('app.py', 'r') as f:
    app_code = f.read()

if '/blog' not in app_code:
    blog_routes = '''

# --- Blog Routes ---
@app.route('/blog')
@app.route('/blog/')
def blog_index():
    return send_from_directory('blog_posts', 'index.html')

@app.route('/blog/<slug>')
def blog_post(slug):
    filename = f"{slug}.html"
    filepath = os.path.join('blog_posts', filename)
    if os.path.exists(filepath):
        return send_from_directory('blog_posts', filename)
    return send_from_directory('.', 'index.html'), 404

'''
    # Insert before the if __name__ block or the caching middleware
    if "# --- Performance" in app_code:
        app_code = app_code.replace("# --- Performance", blog_routes + "# --- Performance")
    elif "if __name__" in app_code:
        app_code = app_code.replace("if __name__", blog_routes + "if __name__")
    else:
        app_code += blog_routes

    # Make sure os is imported
    if 'import os' not in app_code:
        app_code = 'import os\n' + app_code

    with open('app.py', 'w') as f:
        f.write(app_code)
    print("  Blog routes added to app.py:")
    print("    /blog - Blog index page")
    print("    /blog/<slug> - Individual blog posts")
else:
    print("  Blog routes already exist")

# Add blog link to main page nav
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

if 'href="/blog"' not in html:
    # Add Blog link to the nav
    if 'href="#faq"' in html:
        html = html.replace('href="#faq"', 'href="/blog" class="text-gray-300 hover:text-gold transition-colors">Blog</a>\n                    <a href="#faq"', 1)
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("  Blog link added to main page navigation")

# Update sitemap
sitemap = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://drmortgageusa.com/</loc>
    <lastmod>2026-02-13</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://drmortgageusa.com/blog</loc>
    <lastmod>2026-02-13</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
'''
for post in posts:
    sitemap += f'''  <url>
    <loc>https://drmortgageusa.com/blog/{post['slug']}</loc>
    <lastmod>{post['date']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
'''
sitemap += '</urlset>'

with open('sitemap.xml', 'w') as f:
    f.write(sitemap)
print("  Sitemap updated with blog URLs")

print(f"\n{'=' * 60}")
print("  Section 4 COMPLETE! Click Republish to deploy.")
print(f"  - FAQ section: {len(faqs)} questions with accordion UI")
print(f"  - Blog posts: {len(posts)} articles ready")
print(f"  - Blog index: /blog")
print(f"  - Sitemap: updated with all new URLs")
print(f"{'=' * 60}")
