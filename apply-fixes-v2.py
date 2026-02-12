#!/usr/bin/env python3
"""
Dr.MortgageUSA - Site Optimization Patcher v2
==============================================
Round 2 fixes:
  1. Add alt text to family-photo.png (SEO)
  2. Add privacy assurance text below quiz email field (Conversion)
  3. Add progress indicator to quiz steps (UX)
  4. Improve text contrast in "What sets me apart" section (Accessibility)
  5. Boost loan option card visibility (UX)
  6. Add phone number to sticky nav (Conversion)
  7. Style Instagram follow card on-brand (Branding)
  8. Strengthen CTA below calculator (Conversion)

HOW TO RUN:
  1. Upload this file to your Replit project root
  2. Open the Shell tab
  3. Run: python3 apply-fixes-v2.py
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
    # FIX 1: Add alt text to family-photo.png
    # Missing alt text hurts SEO. Google needs to know what the image is.
    # =================================================================
    old_family = '<img src="assets/family-photo.png" loading="lazy"'
    new_family = '<img src="assets/family-photo.png" loading="lazy" alt="Dennis Ross and family in Florida"'
    if old_family in html:
        html = html.replace(old_family, new_family)
        print("[OK] Added alt text to family-photo.png")
        fixes_applied += 1
    else:
        print("[SKIP] family-photo alt text already set or tag not found")

    # =================================================================
    # FIX 2: Add privacy assurance text near quiz email field
    # People hesitate to give their email. A small privacy note
    # reduces friction and increases quiz completion.
    # =================================================================
    # The email input is in quiz step 4 (name/email capture step)
    old_email_btn = 'See My Results!</button>'
    new_email_btn = ('See My Results!</button>\n'
                     '                    <p class="text-xs text-gray-400 mt-2 text-center">'
                     '<svg class="inline w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">'
                     '<path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/>'
                     '</svg>'
                     'Your info is private. No spam, ever.</p>')
    if old_email_btn in html:
        html = html.replace(old_email_btn, new_email_btn, 1)
        print("[OK] Added privacy assurance text below quiz email button")
        fixes_applied += 1
    else:
        print("[SKIP] Quiz email button text not found")

    # =================================================================
    # FIX 3: Add progress indicator to quiz
    # Users need to know how far along they are. A simple step counter
    # reduces abandonment.
    # =================================================================
    # Add a progress bar div right after the form tag opens
    old_form_tag = '<form id="quizForm" onsubmit="return false;">'
    progress_html = '''<form id="quizForm" onsubmit="return false;">
                <!-- Quiz Progress Bar -->
                <div id="quiz-progress" class="mb-6 px-4">
                    <div class="flex justify-between mb-1">
                        <span id="progress-text" class="text-xs font-medium text-gold">Step 1 of 5</span>
                        <span id="progress-percent" class="text-xs font-medium text-gray-400">20%</span>
                    </div>
                    <div class="w-full bg-gray-700 rounded-full h-2">
                        <div id="progress-bar" class="bg-gradient-to-r from-gold to-yellow-500 h-2 rounded-full transition-all duration-500 ease-out" style="width: 20%"></div>
                    </div>
                </div>'''
    if old_form_tag in html and 'quiz-progress' not in html:
        html = html.replace(old_form_tag, progress_html, 1)
        print("[OK] Added progress indicator to quiz")
        fixes_applied += 1
    else:
        print("[SKIP] Quiz progress bar already exists or form tag not found")

    # Add JS to update the progress bar when steps change
    progress_js = '''
    // Update quiz progress bar
    function updateQuizProgress(step) {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        const progressPercent = document.getElementById('progress-percent');
        if (progressBar && progressText && progressPercent) {
            const percent = Math.round((step / 5) * 100);
            progressBar.style.width = percent + '%';
            progressText.textContent = 'Step ' + step + ' of 5';
            progressPercent.textContent = percent + '%';
        }
    }
'''
    # Insert the progress JS function before the showStep function
    if 'updateQuizProgress' not in html and 'function showStep' in html:
        html = html.replace(
            'function showStep',
            progress_js + '    function showStep'
        )
        # Also add updateQuizProgress calls inside showStep
        old_show = 'function showStep(n) {'
        new_show = 'function showStep(n) {\n        updateQuizProgress(n + 1);'
        if old_show in html:
            html = html.replace(old_show, new_show, 1)
        print("[OK] Added progress bar JavaScript")
        fixes_applied += 1
    else:
        print("[SKIP] Progress JS already exists or showStep not found")

    # =================================================================
    # FIX 4: Improve text contrast in "What sets me apart" section
    # The gold text on whatever background is hard to read.
    # Change heading to white and make sure paragraph text is readable.
    # =================================================================
    old_heading = 'class="font-poppins font-bold text-2xl text-gold mb-6 text-center">What sets me apart:</h3>'
    new_heading = 'class="font-poppins font-bold text-2xl text-white mb-6 text-center">What sets me apart:</h3>'
    if old_heading in html:
        html = html.replace(old_heading, new_heading)
        print("[OK] Improved 'What sets me apart' heading contrast (gold -> white)")
        fixes_applied += 1
    else:
        print("[SKIP] 'What sets me apart' heading not found or already fixed")

    # Also improve the paragraph text in that section from text-gray-700 to text-gray-200
    # These are inside the border-gold divs
    old_p_class = 'border-l-4 border-gold pl-6">\n                    <h4 class="font-semibold text-lg text-navy'
    new_p_class = 'border-l-4 border-gold pl-6">\n                    <h4 class="font-semibold text-lg text-white'
    count = html.count(old_p_class)
    if count > 0:
        html = html.replace(old_p_class, new_p_class)
        # Also fix the paragraph text color
        # Look for text-gray-700 paragraphs inside these specific divs
        html = re.sub(
            r'(border-l-4 border-gold pl-6">\s+<h4 class="font-semibold text-lg text-white[^"]*">[^<]+</h4>\s+<p class=")text-gray-700(")',
            r'\1text-gray-300\2',
            html
        )
        print(f"[OK] Improved {count} 'What sets me apart' card text contrast")
        fixes_applied += 1
    else:
        print("[SKIP] 'What sets me apart' card text already fixed or not found")

    # =================================================================
    # FIX 5: Boost loan option card visibility
    # Cards use bg-white/10 which is nearly invisible.
    # Increase opacity and add a subtle glow effect.
    # =================================================================
    old_loan_card = 'bg-white/10 backdrop-blur rounded-xl p-6 border border-gold/30 hover:border-gold transition-colors'
    new_loan_card = 'bg-white/15 backdrop-blur rounded-xl p-6 border border-gold/50 hover:border-gold hover:bg-white/20 transition-all duration-300 shadow-lg shadow-gold/5'
    count = html.count(old_loan_card)
    if count > 0:
        html = html.replace(old_loan_card, new_loan_card)
        print(f"[OK] Boosted visibility on {count} loan option cards")
        fixes_applied += 1
    else:
        print("[SKIP] Loan option cards already fixed or pattern not found")

    # =================================================================
    # FIX 6: Add phone number to sticky nav
    # Making the phone number visible in the nav means people can
    # call you from any scroll position. Huge for mobile.
    # =================================================================
    # Find the nav tag and add a phone link before the headshot
    old_nav_phone = '<a href="tel:8503468514" class="cursor-pointer hover:opacity-80 transition-opacity" title="Call Dennis Ross">'
    if old_nav_phone in html:
        # Check if we already added a phone text
        if 'nav-phone-text' not in html:
            new_nav_phone = ('<a href="tel:8503468514" class="cursor-pointer hover:opacity-80 transition-opacity flex items-center gap-2" title="Call Dennis Ross">\n'
                           '                    <span id="nav-phone-text" class="hidden md:inline text-sm font-medium text-gold">(850) 346-8514</span>')
            html = html.replace(old_nav_phone, new_nav_phone, 1)
            print("[OK] Added phone number text to sticky nav")
            fixes_applied += 1
        else:
            print("[SKIP] Phone number already in nav")
    else:
        print("[SKIP] Nav phone link not found")

    # =================================================================
    # FIX 7: Style Instagram follow card on-brand
    # Make the Instagram section match your navy/gold brand colors
    # =================================================================
    old_ig_comment = '<!-- Instagram Follow Card -->'
    if old_ig_comment in html:
        # Find the Instagram card section and update its styling
        # The card is around line 3007-3025
        html = re.sub(
            r'<!-- Instagram Follow Card -->\s*<a href="https://www\.instagram\.com/dr\.mortgageusa" target="_blank"[^>]*>',
            ('<!-- Instagram Follow Card -->\n'
             '                    <a href="https://www.instagram.com/dr.mortgageusa" target="_blank" '
             'class="block bg-gradient-to-r from-navy to-navy-dark rounded-xl p-5 border border-gold/30 '
             'hover:border-gold hover:shadow-lg hover:shadow-gold/10 transition-all duration-300 text-center">'),
            html
        )
        print("[OK] Styled Instagram follow card on-brand")
        fixes_applied += 1
    else:
        print("[SKIP] Instagram Follow Card not found")

    # =================================================================
    # FIX 8: Add stronger CTA after calculator results
    # After someone uses the calculator, they're engaged.
    # Give them a clear next step.
    # =================================================================
    old_cta_comment = '<!-- Call to Action below calculator -->'
    if old_cta_comment in html:
        # Check what's there currently and see if we need to enhance it
        cta_pos = html.find(old_cta_comment)
        # Check if there's already a good CTA
        next_200 = html[cta_pos:cta_pos+500]
        if 'Get Your Free Quote' not in next_200:
            new_cta = '''<!-- Call to Action below calculator -->
                <div class="mt-8 p-6 bg-gradient-to-r from-navy to-navy-dark rounded-xl border border-gold/30 text-center">
                    <h3 class="text-xl font-bold text-white mb-2">Like what you see?</h3>
                    <p class="text-gray-300 mb-4">Get your personalized rate in under 5 minutes. No credit check required to start.</p>
                    <a href="https://home1st.my1003app.com/2018381/register" target="_blank" class="inline-block bg-gradient-to-r from-gold to-yellow-600 hover:from-yellow-600 hover:to-gold text-navy font-bold py-3 px-8 rounded-lg shadow-xl transition-all duration-300 hover:scale-105">
                        Get Your Free Quote
                    </a>
                    <p class="text-xs text-gray-400 mt-3">NMLS #2018381 | No obligation</p>
                </div>'''
            # Replace just the comment with the full CTA block
            html = html.replace(old_cta_comment, new_cta, 1)
            print("[OK] Added strong CTA below calculator")
            fixes_applied += 1
        else:
            print("[SKIP] Calculator CTA already enhanced")
    else:
        print("[SKIP] Calculator CTA comment not found")

    # =================================================================
    # SAVE RESULTS
    # =================================================================

    if fixes_applied == 0:
        print("\nNo fixes were applied. The file may already be patched.")
        sys.exit(0)

    # Create backup
    backup_name = 'index.html.backup-v2'
    with open(backup_name, 'w', encoding='utf-8') as f:
        f.write(original)
    print(f"\n[OK] Backup saved as {backup_name}")

    # Write fixed file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n{'=' * 55}")
    print(f"  ALL DONE! {fixes_applied} fixes applied!")
    print(f"{'=' * 55}")
    print()
    print("Changes made:")
    print("  1. Added alt text to family-photo.png")
    print("  2. Added privacy text below quiz email button")
    print("  3. Added progress bar to quiz steps")
    print("  4. Improved 'What sets me apart' text contrast")
    print("  5. Boosted loan option card visibility")
    print("  6. Added phone number to sticky nav")
    print("  7. Styled Instagram card on-brand")
    print("  8. Added CTA below calculator results")
    print()
    print("NEXT: Click Republish in Replit")
    print(f"Original backed up to: {backup_name}")


if __name__ == '__main__':
    main()
