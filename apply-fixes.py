#!/usr/bin/env python3
"""
Dr.MortgageUSA - Site Optimization Patcher
==========================================
Fixes applied:
  1. OG/Twitter social sharing images (broken reference)
  2. Removes unverifiable aggregateRating schema
  3. Fixes BreadcrumbList schema (removes hash anchors)
  4. Reorders quiz (name/email moves from step 2 to step 4)
  5. Updates JavaScript handlers for new quiz order

HOW TO RUN:
  1. Upload this file to your Replit project root (same folder as index.html)
  2. Open the Shell tab in Replit
  3. Run: python3 apply-fixes.py
  4. Delete this file after running
  5. Deploy your site
"""

import re
import sys
import os


def main():
    filename = 'index.html'

    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found.")
        print("Make sure this script is in the same folder as index.html.")
        sys.exit(1)

    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html
    fixes_applied = 0

    # =================================================================
    # FIX 1: OG/Twitter Image Reference
    # Your OG tags reference dennis-ross-headshot.png which doesn't exist.
    # Your actual image is dennis-ross.png. This breaks social sharing.
    # =================================================================
    old_img = 'https://drmortgageusa.com/dennis-ross-headshot.png'
    new_img = 'https://drmortgageusa.com/dennis-ross.png'
    count = html.count(old_img)
    if count > 0:
        html = html.replace(old_img, new_img)
        print(f"[OK] Fixed {count} OG/Twitter image references")
        fixes_applied += 1
    else:
        print("[SKIP] OG image references already correct or not found")

    # =================================================================
    # FIX 2: Remove aggregateRating from FinancialService Schema
    # Claims 127 reviews with 4.9 rating. If Google can't verify this
    # from a third-party source, they may penalize you.
    # =================================================================
    if '"aggregateRating"' in html:
        html = re.sub(
            r',\s*"aggregateRating"\s*:\s*\{[^}]+\}',
            '',
            html,
            flags=re.DOTALL
        )
        print("[OK] Removed unverifiable aggregateRating schema")
        fixes_applied += 1
    else:
        print("[SKIP] aggregateRating already removed or not found")

    # =================================================================
    # FIX 3: Fix BreadcrumbList Schema
    # Hash anchors (#quiz, #calculator) are not real pages.
    # Google ignores or flags these. Keep only real URLs.
    # =================================================================
    old_breadcrumb_marker = '"https://drmortgageusa.com/#quiz"'
    if old_breadcrumb_marker in html:
        # Find the full BreadcrumbList script block and replace it
        html = re.sub(
            r'(<script type="application/ld\+json">\s*\{\s*"@context":\s*"https://schema\.org",\s*"@type":\s*"BreadcrumbList",\s*"itemListElement":\s*\[).*?(\]\s*\}\s*</script>)',
            r'''<script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": "https://drmortgageusa.com"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Apply Now",
                "item": "https://home1st.my1003app.com/2018381/register"
            }
        ]
    }
    </script>''',
            html,
            flags=re.DOTALL
        )
        print("[OK] Fixed BreadcrumbList schema (removed hash anchors)")
        fixes_applied += 1
    else:
        print("[SKIP] BreadcrumbList already fixed or not found")

    # =================================================================
    # FIX 4: Reorder Quiz Steps
    # Original: 1-Price, 2-Name/Email, 3-Buyer, 4-Down, 5-Timeline
    # New:      1-Price, 2-Buyer, 3-Down, 4-Name/Email, 5-Timeline
    #
    # Moving name/email to step 4 means users answer 3 easy questions
    # before giving personal info. This increases completion rates.
    # =================================================================

    # Find the quiz form content boundaries
    form_start_tag = '<form id="quizForm" onsubmit="return false;">'
    form_start_pos = html.find(form_start_tag)

    if form_start_pos == -1:
        print("[SKIP] Quiz form not found")
    else:
        form_content_start = form_start_pos + len(form_start_tag)
        form_end_pos = html.find('</form>', form_content_start)

        if form_end_pos == -1:
            print("[SKIP] Quiz form end not found")
        else:
            form_content = html[form_content_start:form_end_pos]

            # Split form content into step blocks using comment markers
            parts = re.split(r'(<!-- Step \d+ )', form_content)

            # parts structure:
            # [0] = whitespace before first step
            # [1] = '<!-- Step 1 '
            # [2] = '- Price Range...-->\n<div...'
            # [3] = '<!-- Step 2 '
            # [4] = '- Email Capture...-->\n<div...'
            # etc.

            if len(parts) >= 11:  # 1 preamble + 5 pairs of (marker, content)
                preamble = parts[0]

                # Reconstruct full step blocks (marker + content)
                step_blocks = []
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        step_blocks.append(parts[i] + parts[i + 1])

                if len(step_blocks) == 5:
                    # Reorder: 0(Price), 2(Buyer), 3(Down), 1(Name/Email), 4(Timeline)
                    new_order = [
                        step_blocks[0],  # Price stays step 1
                        step_blocks[2],  # Buyer Type becomes step 2
                        step_blocks[3],  # Down Payment becomes step 3
                        step_blocks[1],  # Name/Email becomes step 4
                        step_blocks[4],  # Timeline stays step 5
                    ]

                    # New step descriptions
                    descriptions = [
                        'Price Range & Location (Better Qualification)',
                        'Buyer Type Selection',
                        'Down Payment Reality Check',
                        'Name & Email Capture',
                        'Urgency & Timeline',
                    ]

                    for i in range(len(new_order)):
                        block = new_order[i]
                        num = i + 1

                        # Update comment
                        block = re.sub(
                            r'<!-- Step \d+ - .*?-->',
                            f'<!-- Step {num} - {descriptions[i]} -->',
                            block,
                            count=1
                        )

                        # Update data-step attribute
                        block = re.sub(
                            r'data-step="\d+"',
                            f'data-step="{num}"',
                            block,
                            count=1
                        )

                        new_order[i] = block

                    # Remove step3-greeting id from buyer type (now step 2)
                    # since name hasn't been collected yet at this point
                    new_order[1] = new_order[1].replace(
                        'id="step3-greeting" ', ''
                    )

                    # Update name/email heading (now step 4)
                    new_order[3] = new_order[3].replace(
                        "Great! What's your first name?",
                        "Almost there! What's your first name?"
                    )
                    new_order[3] = new_order[3].replace(
                        'Continue - Almost Done!',
                        'See My Results!'
                    )

                    # Add id to timeline heading (step 5) for personalization
                    new_order[4] = new_order[4].replace(
                        '<h2 class="text-2xl font-bold mb-2 text-navy">When do you want to move?</h2>',
                        '<h2 id="step5-greeting" class="text-2xl font-bold mb-2 text-navy">When do you want to move?</h2>'
                    )

                    # Reconstruct form content
                    new_form_content = preamble + ''.join(new_order)

                    # Replace in the full HTML
                    html = (
                        html[:form_content_start]
                        + new_form_content
                        + html[form_end_pos:]
                    )

                    print("[OK] Reordered quiz steps (name/email moved to step 4)")
                    fixes_applied += 1
                else:
                    print(f"[WARN] Expected 5 quiz steps, found {len(step_blocks)}")
            else:
                print(f"[WARN] Could not split quiz into expected parts")

    # =================================================================
    # FIX 5: Update JavaScript Handlers for New Quiz Order
    # =================================================================

    js_fixes = 0

    # 5a: Update nextBtn selector (name/email is now step 4, not step 2)
    old_selector = """const step2Btn = document.querySelector("div[data-step='2'] .nextBtn");"""
    new_selector = """const step4Btn = document.querySelector("div[data-step='4'] .nextBtn");"""
    if old_selector in html:
        html = html.replace(old_selector, new_selector)
        js_fixes += 1

    # 5b: Update step2Btn variable references
    if 'if (step2Btn)' in html:
        html = html.replace('if (step2Btn) {', 'if (step4Btn) {')
        js_fixes += 1

    if 'step2Btn.addEventListener' in html:
        html = html.replace('step2Btn.addEventListener', 'step4Btn.addEventListener')
        js_fixes += 1

    # 5c: Update step3-greeting personalization to step5-greeting
    # and change current = 2 to current = 4 in the nextBtn handler
    old_personalization = (
        '      // Personalize Step 3 greeting\n'
        '      const step3Greeting = document.getElementById("step3-greeting");\n'
        '      if (step3Greeting) {\n'
        '        step3Greeting.textContent = `Thanks ${quizAnswers.firstName}! Which best describes you?`;\n'
        '      }\n'
        '      \n'
        '      current = 2;\n'
        '      showStep(current);'
    )
    new_personalization = (
        '      // Personalize Step 5 greeting\n'
        '      const step5Greeting = document.getElementById("step5-greeting");\n'
        '      if (step5Greeting && quizAnswers.firstName) {\n'
        '        step5Greeting.textContent = "Almost done " + quizAnswers.firstName + "! When do you want to move?";\n'
        '      }\n'
        '      \n'
        '      current = 4;\n'
        '      showStep(current);'
    )
    if old_personalization in html:
        html = html.replace(old_personalization, new_personalization)
        js_fixes += 1
    else:
        # Try with different whitespace
        old_p2 = '// Personalize Step 3 greeting'
        if old_p2 in html:
            # Use regex for more flexible whitespace matching
            html = re.sub(
                r'// Personalize Step 3 greeting\s+'
                r'const step3Greeting = document\.getElementById\("step3-greeting"\);\s+'
                r'if \(step3Greeting\) \{\s+'
                r'step3Greeting\.textContent = `Thanks \$\{quizAnswers\.firstName\}! Which best describes you\?`;\s+'
                r'\}\s+'
                r'current = 2;\s+'
                r'showStep\(current\);',
                '// Personalize Step 5 greeting\n'
                '      const step5Greeting = document.getElementById("step5-greeting");\n'
                '      if (step5Greeting && quizAnswers.firstName) {\n'
                '        step5Greeting.textContent = "Almost done " + quizAnswers.firstName + "! When do you want to move?";\n'
                '      }\n'
                '      \n'
                '      current = 4;\n'
                '      showStep(current);',
                html
            )
            js_fixes += 1

    # 5d: Update buyerBtn handler: current = 3 -> current = 2
    old_buyer = 'quizAnswers.buyerType = btn.dataset.buyer;\n      current = 3;'
    new_buyer = 'quizAnswers.buyerType = btn.dataset.buyer;\n      current = 2;'
    if old_buyer in html:
        html = html.replace(old_buyer, new_buyer)
        js_fixes += 1
    else:
        # Try regex for flexible whitespace
        html = re.sub(
            r'(quizAnswers\.buyerType = btn\.dataset\.buyer;\s+)current = 3;',
            r'\1current = 2;',
            html
        )
        js_fixes += 1

    # 5e: Update downBtn handler: current = 4 -> current = 3
    old_down = 'quizAnswers.downPayment = btn.dataset.down;\n      current = 4;'
    new_down = 'quizAnswers.downPayment = btn.dataset.down;\n      current = 3;'
    if old_down in html:
        html = html.replace(old_down, new_down)
        js_fixes += 1
    else:
        html = re.sub(
            r'(quizAnswers\.downPayment = btn\.dataset\.down;\s+)current = 4;',
            r'\1current = 3;',
            html
        )
        js_fixes += 1

    # 5f: Update JS comments for step order
    html = html.replace(
        '// Step 2: Name and Email Capture',
        '// Step 4: Name and Email Capture'
    )
    html = html.replace(
        '// Step 3: Buyer Type Selection',
        '// Step 2: Buyer Type Selection'
    )
    html = html.replace(
        '// Step 4: Down Payment Selection',
        '// Step 3: Down Payment Selection'
    )

    if js_fixes > 0:
        print(f"[OK] Updated {js_fixes} JavaScript handler references")
        fixes_applied += 1
    else:
        print("[WARN] Could not find expected JS patterns to update")

    # =================================================================
    # SAVE RESULTS
    # =================================================================

    if fixes_applied == 0:
        print("\nNo fixes were applied. The file may already be patched.")
        sys.exit(0)

    # Create backup
    backup_name = 'index.html.backup'
    with open(backup_name, 'w', encoding='utf-8') as f:
        f.write(original)
    print(f"\n[OK] Backup saved as {backup_name}")

    # Write fixed file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    # =================================================================
    # CREATE sitemap.xml (so Google can find your site)
    # =================================================================
    from datetime import date
    today = date.today().isoformat()

    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://drmortgageusa.com/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
'''
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print("[OK] Created sitemap.xml")

    # =================================================================
    # CREATE robots.txt (tells search engines where to look)
    # =================================================================
    robots = '''User-agent: *
Allow: /

Sitemap: https://drmortgageusa.com/sitemap.xml

# Dr.MortgageUSA - Florida Mortgage Broker
# Dennis Ross NMLS #2018381
'''
    with open('robots.txt', 'w', encoding='utf-8') as f:
        f.write(robots)
    print("[OK] Created robots.txt")

    print(f"\n{'=' * 55}")
    print(f"  ALL DONE! {fixes_applied} fixes + 2 new files created!")
    print(f"{'=' * 55}")
    print()
    print("Changes made:")
    print("  1. Fixed OG/Twitter social sharing images")
    print("  2. Removed unverifiable aggregateRating schema")
    print("  3. Fixed BreadcrumbList (removed hash anchors)")
    print("  4. Reordered quiz (name/email now step 4)")
    print("  5. Updated JavaScript handlers for new flow")
    print("  6. Created sitemap.xml")
    print("  7. Created robots.txt")
    print()
    print("NEXT STEPS:")
    print("  1. Click Deploy in Replit")
    print("  2. Go to search.google.com/search-console")
    print("  3. Add drmortgageusa.com and verify with HTML tag method")
    print("  4. Submit your sitemap URL: https://drmortgageusa.com/sitemap.xml")
    print()
    print("You can delete apply-fixes.py after running it.")
    print(f"Original index.html backed up to: {backup_name}")


if __name__ == '__main__':
    main()
