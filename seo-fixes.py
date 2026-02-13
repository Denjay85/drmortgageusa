import re, os
print("=" * 55)
print("  SEO Fixes - drmortgageusa.com")
print("=" * 55)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove noindex tags
for p in [r'<meta\s+[^>]*noindex[^>]*>', r'<meta\s+[^>]*x-robots-tag[^>]*noindex[^>]*>']:
    for m in re.findall(p, html, re.IGNORECASE):
        html = html.replace(m, '')
        print(f"  Removed: {m}")

# 2. Remove old meta tags we will replace
removed = 0
for p in [r'<meta\s+name="description"[^>]*>', r'<meta\s+name="keywords"[^>]*>',
          r'<meta\s+name="author"[^>]*>', r'<meta\s+property="og:[^"]*"[^>]*>',
          r'<meta\s+name="twitter:[^"]*"[^>]*>', r'<link\s+rel="canonical"[^>]*>',
          r'<meta\s+name="robots"[^>]*>', r'<meta\s+name="geo\.[^"]*"[^>]*>']:
    for m in re.findall(p, html, re.IGNORECASE):
        html = html.replace(m, '')
        removed += 1
print(f"  Removed {removed} old meta tags")

# 3. Build new meta + schema
meta = '''
    <meta name="description" content="Florida mortgage broker Dennis Ross helps you find the lowest rates on Conventional, FHA, VA, USDA, and Jumbo loans. Navy veteran. 600+ families served. NMLS #2018381.">
    <meta name="keywords" content="mortgage broker Florida, FHA loan Florida, VA loan Florida, conventional mortgage, jumbo loan, USDA loan, mortgage rates, Dennis Ross mortgage, Home First Lending">
    <meta name="author" content="Dennis Ross, NMLS #2018381">
    <link rel="canonical" href="https://drmortgageusa.com/">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://drmortgageusa.com/">
    <meta property="og:title" content="Florida Mortgage Broker | Dr.MortgageUSA - Dennis Ross">
    <meta property="og:description" content="Navy veteran mortgage broker. 600+ Florida families served. FHA, VA, Conventional, Jumbo, USDA loans. Get pre-approved in minutes.">
    <meta property="og:image" content="https://drmortgageusa.com/dennis-ross-headshot.png">
    <meta property="og:site_name" content="Dr.MortgageUSA">
    <meta property="og:locale" content="en_US">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Florida Mortgage Broker | Dr.MortgageUSA - Dennis Ross">
    <meta name="twitter:description" content="Navy veteran mortgage broker. 600+ families served. Get pre-approved for FHA, VA, Conventional, Jumbo, or USDA loans.">
    <meta name="twitter:image" content="https://drmortgageusa.com/dennis-ross-headshot.png">
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    <meta name="geo.region" content="US-FL">
    <meta name="geo.placename" content="Florida">
'''

# Extract rates for schema
rd = {}
for k, p in [('conv30', r'"Conventional 30-Year":\s*"([\d.]+)%"'), ('conv15', r'"Conventional 15-Year":\s*"([\d.]+)%"'),
             ('fha30', r'"FHA 30-Year":\s*"([\d.]+)%"'), ('va30', r'"VA 30-Year":\s*"([\d.]+)%"'),
             ('jumbo30', r'"Jumbo 30-Year":\s*"([\d.]+)%"')]:
    m = re.search(p, html)
    if m: rd[k] = m.group(1)

schema = '''
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"FinancialService","name":"Dr.MortgageUSA - Dennis Ross","description":"Florida mortgage broker specializing in Conventional, FHA, VA, USDA, and Jumbo home loans. Navy veteran. 600+ families served.","url":"https://drmortgageusa.com","telephone":"+1-850-346-8514","image":"https://drmortgageusa.com/dennis-ross-headshot.png","logo":"https://drmortgageusa.com/logo.png","priceRange":"$$","areaServed":{"@type":"State","name":"Florida"},"serviceType":["Mortgage Broker","FHA Loans","VA Loans","Conventional Loans","Jumbo Loans","USDA Loans"],"founder":{"@type":"Person","name":"Dennis Ross","jobTitle":"Mortgage Broker"},"sameAs":["https://www.instagram.com/dr.mortgageusa/"]}
    </script>
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"WebSite","name":"Dr.MortgageUSA","url":"https://drmortgageusa.com","description":"Florida mortgage broker helping families find the best home loan rates"}
    </script>
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"What credit score do I need for a mortgage in Florida?","acceptedAnswer":{"@type":"Answer","text":"FHA loans require a minimum 580 credit score for 3.5% down. Conventional loans typically need 620+. VA loans have no VA-set minimum, though most lenders want 620+."}},{"@type":"Question","name":"How much down payment do I need?","acceptedAnswer":{"@type":"Answer","text":"FHA: 3.5% minimum. Conventional: 3-5%. VA: 0% for eligible veterans. USDA: 0% for eligible rural areas. Jumbo: typically 10-20%."}},{"@type":"Question","name":"What is the difference between FHA and conventional loans?","acceptedAnswer":{"@type":"Answer","text":"FHA loans are government-insured with lower credit requirements (580+) and 3.5% down, but require mortgage insurance. Conventional loans need higher credit (620+) but let you drop PMI at 20% equity."}},{"@type":"Question","name":"Do you serve all of Florida?","acceptedAnswer":{"@type":"Answer","text":"Yes, Dr.MortgageUSA serves homebuyers throughout the entire state of Florida."}},{"@type":"Question","name":"How long does closing take?","acceptedAnswer":{"@type":"Answer","text":"Average 30-45 days from application. With documents ready, some closings happen in 21 days. Pre-approval speeds the process."}},{"@type":"Question","name":"What are VA loan benefits for veterans?","acceptedAnswer":{"@type":"Answer","text":"VA loans offer zero down payment, no PMI, competitive rates, and limited closing costs. Dennis Ross is a Navy veteran who specializes in helping fellow veterans."}}]}
    </script>
'''

# Add MortgageLoan schemas for current rates
for name, key, term in [("Conventional 30-Year", "conv30", 30), ("FHA 30-Year", "fha30", 30), ("VA 30-Year", "va30", 30)]:
    if key in rd:
        schema += f'''
    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"MortgageLoan","name":"{name} Fixed Mortgage","lender":{{"@type":"FinancialService","name":"Dr.MortgageUSA"}},"interestRate":{rd[key]},"loanTerm":{{"@type":"QuantitativeValue","value":{term},"unitCode":"ANN"}},"currency":"USD"}}
    </script>
'''

# Insert meta after charset
ins = re.search(r'(<meta\s+charset=[^>]*>)', html, re.IGNORECASE)
if ins:
    pos = ins.end()
    html = html[:pos] + meta + html[pos:]
    print("  Meta tags inserted")

# Insert schema before </head>
ch = html.rfind('</head>')
if ch != -1:
    html = html[:ch] + schema + "\n" + html[ch:]
    print("  Schema markup inserted")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"  index.html saved ({os.path.getsize('index.html'):,} bytes)")

# Add /health endpoint to app.py
with open('app.py', 'r') as f:
    ac = f.read()
if '/health' not in ac:
    hc = "\n@app.route('/health')\ndef health_check():\n    return jsonify({'status': 'ok', 'service': 'drmortgageusa'}), 200\n\n"
    fr = ac.find("@app.route('/')")
    if fr != -1:
        ac = ac[:fr] + hc + ac[fr:]
        with open('app.py', 'w') as f:
            f.write(ac)
        print("  /health endpoint added to app.py")
print("\nDONE! Click Republish to deploy.")
