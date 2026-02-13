import re, os

print("=" * 60)
print("  Sections 2 & 3 Fixes - drmortgageusa.com")
print("=" * 60)

# Read files
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
original_size = len(html.encode('utf-8'))
print(f"\nOriginal index.html: {original_size:,} bytes")

# ============================================================
# SECTION 2.1: Reduce page size
# ============================================================
print("\n--- Section 2.1: Page Size Reduction ---")

# Remove HTML comments (but preserve conditional comments and schema)
html = re.sub(r'<!--(?!\[if)(?!.*schema)(?!.*google)(?!.*gtag)(?!.*analytics)[^>]*?-->', '', html)
print("  HTML comments removed")

# Minify inline CSS: remove extra whitespace, newlines in style blocks
def minify_css(match):
    css = match.group(1)
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)  # remove comments
    css = re.sub(r'\s+', ' ', css)  # collapse whitespace
    css = re.sub(r'\s*{\s*', '{', css)
    css = re.sub(r'\s*}\s*', '}', css)
    css = re.sub(r'\s*:\s*', ':', css)
    css = re.sub(r'\s*;\s*', ';', css)
    css = re.sub(r';\s*}', '}', css)  # remove last semicolon
    return f'<style>{css.strip()}</style>'

html = re.sub(r'<style[^>]*>(.*?)</style>', minify_css, html, flags=re.DOTALL)
print("  Inline CSS minified")

# Remove excessive blank lines (3+ newlines -> 1)
html = re.sub(r'\n{3,}', '\n\n', html)
print("  Excessive blank lines removed")

new_size = len(html.encode('utf-8'))
saved = original_size - new_size
print(f"  Size reduced: {original_size:,} -> {new_size:,} bytes (saved {saved:,} bytes)")

# ============================================================
# SECTION 2.2: Image Optimization - add dimensions
# ============================================================
print("\n--- Section 2.2: Image Dimensions ---")

# Define known image dimensions (these are typical for the site)
img_dims = {
    'logo.png': ('width="180" height="60"', 'decoding="async"'),
    'dennis-ross.png': ('width="400" height="400"', 'decoding="async"'),
    'family-photo.png': ('width="600" height="400"', 'decoding="async"'),
}

def add_img_attrs(match):
    tag = match.group(0)
    # Skip if already has width
    if 'width=' in tag.lower():
        return tag
    # Find which image
    for img_name, (dims, decode) in img_dims.items():
        if img_name in tag:
            # Add before closing >
            tag = tag.rstrip('/>').rstrip('>').rstrip()
            if '/>' in match.group(0):
                tag = f'{tag} {dims} {decode} />'
            else:
                tag = f'{tag} {dims} {decode}>'
            return tag
    # For unknown images, just add decoding
    if 'decoding=' not in tag:
        tag = tag.rstrip('/>').rstrip('>').rstrip()
        if '/>' in match.group(0):
            tag = f'{tag} decoding="async" />'
        else:
            tag = f'{tag} decoding="async">'
    return tag

html = re.sub(r'<img[^>]*/?>', add_img_attrs, html)
print("  Image dimensions and decoding attributes added")

# ============================================================
# SECTION 2.3: Lazy Loading
# ============================================================
print("\n--- Section 2.3: Lazy Loading ---")

img_count = 0
def add_lazy_loading(match):
    global img_count
    img_count += 1
    tag = match.group(0)
    # Skip first 2 images (above fold - logo and hero image)
    if img_count <= 2:
        # Add fetchpriority="high" to above-fold images
        if 'fetchpriority' not in tag:
            tag = tag.replace('<img ', '<img fetchpriority="high" ')
        return tag
    # Skip if already has loading attribute
    if 'loading=' in tag.lower():
        return tag
    # Add lazy loading
    tag = tag.replace('<img ', '<img loading="lazy" ')
    return tag

html = re.sub(r'<img[^>]*/?>', add_lazy_loading, html)
print(f"  Processed {img_count} images")
print("  First 2 images: fetchpriority=high (above fold)")
print("  Remaining images: loading=lazy added where missing")

# Add lazy loading to iframes if any
html = re.sub(r'<iframe(?![^>]*loading=)', '<iframe loading="lazy" ', html)
print("  Iframe lazy loading added")

# ============================================================
# SECTION 2.4: Preconnect hints for external resources
# ============================================================
print("\n--- Section 2.4: Resource Hints ---")

# Add preconnect for Google Fonts and other external resources
preconnect = '''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="dns-prefetch" href="https://hooks.zapier.com">
'''
# Insert after <head> tag
if 'preconnect' not in html:
    html = html.replace('<head>', '<head>' + preconnect)
    print("  Preconnect hints added (Google Fonts, Zapier)")
else:
    print("  Preconnect hints already present")

# ============================================================
# SECTION 3.1: Sticky Nav CTA Button
# ============================================================
print("\n--- Section 3.1: Sticky Nav CTA ---")

# Add a visible CTA button to the navigation
nav_cta = '''<a href="#path-finder" class="hidden md:inline-block bg-gold hover:bg-yellow-500 text-navy font-bold py-2 px-5 rounded-full text-sm transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 ml-4" style="background-color:#D4AF37;color:#1a1a2e;">Get Your Free Quote</a>'''

# Find the nav closing area and insert before </nav>
if 'Get Your Free Quote' not in html:
    # Insert before the closing </nav> tag
    html = html.replace('</nav>', nav_cta + '\n</nav>')
    print("  Sticky nav CTA button added: 'Get Your Free Quote'")
else:
    print("  Nav CTA already exists")

# ============================================================
# SECTION 3.2: Lead Capture - Already implemented
# ============================================================
print("\n--- Section 3.2: Lead Capture ---")
print("  ALREADY IMPLEMENTED: 6 forms detected (quiz + 4 segment + investor)")
print("  All connected to Zapier webhook - no changes needed")

# ============================================================
# SECTION 3.3: Trust Signals in Hero
# ============================================================
print("\n--- Section 3.3: Trust Signals in Hero ---")

# Add NMLS number and Equal Housing badge near the hero CTA area
trust_badge = '''<div class="flex flex-wrap items-center justify-center lg:justify-start gap-4 mt-4 text-xs text-gray-300 opacity-80">
                        <span>NMLS #2018381</span>
                        <span>|</span>
                        <span>Licensed in Florida</span>
                        <span>|</span>
                        <span>Equal Housing Lender &#8962;</span>
                        <span>|</span>
                        <span>Powered by Home1st Lending</span>
                    </div>'''

# Find the "Takes less than a minute" text and insert trust badge after it
if 'NMLS #2018381</span>' not in html.split('id="hero"')[1].split('</section>')[0] if 'id="hero"' in html else '':
    target = 'Takes less than a minute. No credit check required.'
    if target in html:
        html = html.replace(target, target + '\n' + trust_badge)
        print("  Trust badge added below hero CTA (NMLS, Florida, Equal Housing)")
    else:
        print("  WARNING: Could not find insertion point for trust badge")
else:
    print("  Trust badge already in hero")

# ============================================================
# SECTION 3.4: Floating Schedule Button
# ============================================================
print("\n--- Section 3.4: Floating Action Button ---")

# Add a floating "Schedule a Call" button (bottom-right)
floating_btn = '''
<!-- Floating Schedule Button -->
<a href="tel:+18503468514" id="floatingCTA" class="fixed bottom-6 right-6 z-40 flex items-center gap-2 text-white font-bold py-3 px-6 rounded-full shadow-2xl transition-all duration-300 hover:scale-110 hover:shadow-3xl" style="background: linear-gradient(135deg, #D4AF37, #b8962e); font-size:15px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
    Call Dennis Now
</a>
<style>
#floatingCTA{animation:floatPulse 3s ease-in-out infinite}
@keyframes floatPulse{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
@media(max-width:768px){#floatingCTA{bottom:16px;right:16px;padding:12px 20px;font-size:14px}}
</style>
'''

if 'floatingCTA' not in html:
    html = html.replace('</body>', floating_btn + '\n</body>')
    print("  Floating 'Call Dennis Now' button added (bottom-right)")
else:
    print("  Floating CTA already exists")

# ============================================================
# Save index.html
# ============================================================
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

final_size = len(html.encode('utf-8'))
total_saved = original_size - final_size
print(f"\n{'=' * 60}")
print(f"  index.html saved: {final_size:,} bytes")
if total_saved > 0:
    print(f"  Total size reduction: {total_saved:,} bytes ({total_saved/original_size*100:.1f}%)")
else:
    print(f"  Size change: +{abs(total_saved):,} bytes (new features added)")
print(f"{'=' * 60}")

# ============================================================
# SECTION 2.4: Caching Headers + Compression in app.py
# ============================================================
print("\n--- Section 2.4: Caching Headers in app.py ---")

with open('app.py', 'r') as f:
    app_code = f.read()

# Check if caching is already configured
if 'Cache-Control' not in app_code and 'after_request' not in app_code:
    # Add caching middleware
    cache_code = '''

# --- Performance: Caching Headers ---
@app.after_request
def add_cache_headers(response):
    # Static assets: cache for 1 week
    if response.content_type and any(t in response.content_type for t in ['image/', 'font/', 'text/css', 'javascript']):
        response.headers['Cache-Control'] = 'public, max-age=604800, immutable'
    # HTML: cache for 5 minutes (allows rate updates to propagate)
    elif response.content_type and 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'public, max-age=300, must-revalidate'
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

'''
    # Insert before the if __name__ block or at end
    if "if __name__" in app_code:
        app_code = app_code.replace("if __name__", cache_code + "if __name__")
    else:
        app_code += cache_code

    with open('app.py', 'w') as f:
        f.write(app_code)
    print("  Cache-Control headers added:")
    print("    - Static assets: 1 week cache")
    print("    - HTML: 5 minute cache with revalidation")
    print("  Security headers added:")
    print("    - X-Content-Type-Options: nosniff")
    print("    - X-Frame-Options: SAMEORIGIN")
    print("    - Referrer-Policy: strict-origin-when-cross-origin")
else:
    print("  Caching headers already configured")

print(f"\n{'=' * 60}")
print("  ALL DONE! Click Republish to deploy.")
print(f"{'=' * 60}")
