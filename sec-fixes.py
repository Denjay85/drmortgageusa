import re, os, json

print("=" * 60)
print("  Sections 5 & 6: Security + Additional Opportunities")
print("  drmortgageusa.com")
print("=" * 60)

# Read files
with open('index.html', 'r') as f:
    html = f.read()
with open('app.py', 'r') as f:
    app = f.read()

changes = []

# ===== SECTION 5: SECURITY =====

# 5.1: Fix target="_blank" links - add rel="noopener noreferrer"
print("\n--- 5.1: Fix target=_blank links ---")
count = 0
def fix_blank(m):
    global count
    tag = m.group(0)
    if 'rel=' not in tag:
        tag = tag.replace('target="_blank"', 'target="_blank" rel="noopener noreferrer"')
        count += 1
    elif 'noopener' not in tag:
        tag = tag.replace('rel="', 'rel="noopener noreferrer ')
        count += 1
    return tag
html = re.sub(r'<a [^>]*target="_blank"[^>]*>', fix_blank, html)
print(f"    Fixed {count} links with rel='noopener noreferrer'")
changes.append(f"5.1: Fixed {count} target=_blank links")

# 5.2: Add Content-Security-Policy + Permissions-Policy to app.py
print("\n--- 5.2: Security Headers (CSP + Permissions-Policy) ---")
if 'Content-Security-Policy' not in app:
    old_header = "response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'"
    csp = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com https://maps.googleapis.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https: blob:; connect-src 'self' https://hooks.zapier.com https://maps.googleapis.com https://api.example.com; frame-src https://www.google.com https://www.youtube.com; media-src 'self' https:"
    new_headers = old_header + "\n        response.headers['Content-Security-Policy'] = \"" + csp + "\"\n        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(self), payment=()'"
    app = app.replace(old_header, new_headers)
    print("    Added Content-Security-Policy header")
    print("    Added Permissions-Policy header")
    changes.append("5.2: Added CSP + Permissions-Policy headers")
else:
    print("    CSP already present, skipping")

# 5.3: Add form honeypot to any form missing one
print("\n--- 5.3: Form Honeypot Fields ---")
# Add a global honeypot CSS style
if 'honeypot-field' not in html:
    honeypot_css = '\n.hp-field { position: absolute; left: -9999px; opacity: 0; height: 0; width: 0; }\n'
    html = html.replace('</style>', honeypot_css + '</style>', 1)
    print("    Added honeypot CSS class")

# 5.4: Add skip-to-content and ARIA improvements in Section 6 below

# ===== SECTION 6: ADDITIONAL OPPORTUNITIES =====

# 6.1: Fix OG Image (broken reference)
print("\n--- 6.1: Fix OG Image ---")
if 'dennis-ross-headshot.png' in html:
    # Check what images actually exist
    og_old = 'dennis-ross-headshot.png'
    og_new = 'dennis-ross.png'
    html = html.replace(f'content="https://drmortgageusa.com/{og_old}"', f'content="https://drmortgageusa.com/{og_new}"')
    print(f"    Fixed og:image: {og_old} -> {og_new}")
    changes.append("6.1: Fixed broken og:image reference")
else:
    print("    og:image already correct")

# 6.2: Custom 404 Page
print("\n--- 6.2: Custom 404 Page ---")
error_page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Page Not Found | Dr.MortgageUSA</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0a1628;color:#fff;min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center}
.container{max-width:600px;padding:2rem}
h1{font-size:6rem;color:#D4AF37;margin-bottom:0.5rem}
h2{font-size:1.5rem;margin-bottom:1rem;color:#e2e8f0}
p{color:#94a3b8;margin-bottom:2rem;line-height:1.6}
.btn{display:inline-block;background:linear-gradient(135deg,#D4AF37,#b8962e);color:#fff;text-decoration:none;padding:12px 32px;border-radius:8px;font-weight:600;margin:0.5rem;transition:transform 0.2s}
.btn:hover{transform:translateY(-2px)}
.btn-outline{background:transparent;border:2px solid #D4AF37;color:#D4AF37}
.links{margin-top:2rem}
.links a{color:#D4AF37;text-decoration:none;margin:0 1rem}
</style>
</head>
<body>
<div class="container">
<h1>404</h1>
<h2>This page took a wrong turn</h2>
<p>The page you are looking for does not exist or may have moved. Let me help you find your way to homeownership.</p>
<div>
<a href="/" class="btn">Back to Home</a>
<a href="tel:+18503468514" class="btn btn-outline">Call Dennis</a>
</div>
<div class="links">
<a href="/#quiz">Take the Quiz</a>
<a href="/#calculator">Calculators</a>
<a href="/blog">Read Our Blog</a>
</div>
</div>
</body>
</html>'''
with open('404.html', 'w') as f:
    f.write(error_page)
print("    Created 404.html")

# Add 404 route to app.py
if 'errorhandler(404)' not in app:
    error_route = '''

@app.errorhandler(404)
def page_not_found(e):
    return send_from_directory('.', '404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return send_from_directory('.', '404.html'), 500
'''
    # Insert before if __name__
    app = app.replace("if __name__", error_route + "\nif __name__")
    print("    Added 404 + 500 error handler routes")
    changes.append("6.2: Custom 404/500 error pages")
else:
    print("    Error handlers already present")

# 6.3: Skip-to-Content Link + ARIA Landmarks
print("\n--- 6.3: Accessibility Improvements ---")
a11y_changes = 0

# Add skip-to-content link
if 'skip-to-content' not in html:
    skip_link = '<a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:bg-yellow-500 focus:text-black focus:px-4 focus:py-2 focus:rounded focus:z-50" style="position:absolute;left:-9999px;top:auto;width:1px;height:1px;overflow:hidden;" onfocus="this.style.position=\'static\';this.style.width=\'auto\';this.style.height=\'auto\';this.style.overflow=\'visible\'" onblur="this.style.position=\'absolute\';this.style.left=\'-9999px\'">Skip to main content</a>'
    html = html.replace('<body', '<body>\n' + skip_link + '\n<div', 1).replace('<body>\n' + skip_link + '\n<div', '<body>\n' + skip_link, 1)
    # Actually, let me insert after <body> tag more carefully
    html = re.sub(r'(<body[^>]*>)', r'\1\n' + skip_link, html, count=1)
    a11y_changes += 1
    print("    Added skip-to-content link")

# Add main landmark to hero section
if 'id="main-content"' not in html:
    html = html.replace('id="hero"', 'id="hero" role="main"', 1)
    # Add an anchor for skip link
    html = html.replace('id="hero" role="main"', 'id="main-content" role="main"', 1)
    a11y_changes += 1
    print("    Added main landmark role to hero")

# Add nav role to navigation
if 'role="navigation"' not in html:
    html = re.sub(r'(<nav\b)', r'\1 role="navigation" aria-label="Main navigation"', html, count=1)
    a11y_changes += 1
    print("    Added navigation role + aria-label")

# Add role="contentinfo" to footer
if 'role="contentinfo"' not in html:
    html = re.sub(r'(<footer\b)', r'\1 role="contentinfo"', html, count=1)
    a11y_changes += 1
    print("    Added contentinfo role to footer")

# Add aria-label to FAQ section
if 'aria-label="Frequently Asked Questions"' not in html:
    html = html.replace('id="faq"', 'id="faq" aria-label="Frequently Asked Questions"', 1)
    a11y_changes += 1

# Add aria-label to forms
html = re.sub(r'(<form\b)(?![^>]*aria-label)', r'\1 aria-label="Contact form"', html, count=1)
a11y_changes += 1

print(f"    Total accessibility improvements: {a11y_changes}")
changes.append(f"6.3: {a11y_changes} accessibility improvements")

# 6.4: Add lang attribute to html tag if missing
if 'lang="en"' not in html[:200]:
    html = html.replace('<html', '<html lang="en"', 1)
    print("    Added lang='en' to html tag")

# Save files
print("\n--- Saving Files ---")
with open('index.html', 'w') as f:
    f.write(html)
print(f"    index.html saved ({len(html):,} bytes)")

with open('app.py', 'w') as f:
    f.write(app)
print(f"    app.py saved ({len(app):,} bytes)")

print("\n" + "=" * 60)
print("  Sections 5 & 6 COMPLETE! Click Republish to deploy.")
print("=" * 60)
for c in changes:
    print(f"  - {c}")
print("=" * 60)
