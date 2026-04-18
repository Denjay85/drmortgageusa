# Dr. Mortgage USA - Design Guidelines

## Design Approach
**Patriotic Professional Hybrid**: Combining American flag imagery with clean, modern financial service design. Drawing inspiration from military/veteran service organizations (USAA credibility) + modern fintech clarity (Better.com, Rocket Mortgage). The flag background creates emotional connection while white opacity panels maintain professional readability.

## Typography
- **Primary**: Inter or Manrope (Google Fonts) - clean, modern, highly readable
- **Headers**: 600-700 weight, sizes: Hero 4xl-6xl, Section 3xl-4xl, Card 2xl
- **Body**: 400-500 weight, sizes: lg for primary content, base for secondary
- **Accent Numbers**: 700 weight for rates and stats (trust signals)

## Layout System
**Spacing Primitives**: Tailwind units of 4, 6, 8, 12, 16, 20
- Section padding: py-16 md:py-20 lg:py-24
- Card spacing: p-6 md:p-8
- Element gaps: gap-4 for tight groups, gap-8 for section content, gap-12 between major sections

**Container Strategy**: max-w-7xl with px-6 md:px-8 for content sections

## Component Library

**Content Panels**: White background with 85-90% opacity, rounded corners (rounded-xl), subtle shadow (shadow-lg), backdrop-blur-sm for depth against flag

**Buttons on Hero Image**: 
- Background: bg-white/20 with backdrop-blur-md
- Text: white with font-semibold
- Size: px-8 py-4, text-lg
- Border: border-2 border-white/40

**Rate Cards**: 
- 3-column grid on desktop (grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
- Each card: white opacity panel with large rate number (text-5xl font-bold), loan type, APR details
- Update timestamp badge in corner

**Trust Elements**:
- VA logo, Navy insignia placement
- "Licensed in X states" badge
- Years of service callout
- Customer review count with stars

**Forms**: 
- Refinance calculator with clean input fields
- Contact form: 2-column on desktop (name/email | phone/loan amount)
- White inputs with subtle borders, focus states with blue accent

**Stats Bar**: 4-column metrics grid - Loans closed, Total saved, Average savings, 5-star reviews

## Images

**Hero Section**: 
- Full-width American flag background (subtle waving flag, professional photography - not clipart)
- Overlay: gradient from transparent to semi-transparent blue at bottom
- Position: Professional headshot of Dennis Ross in Navy/business attire - placed right side, circular frame with white border

**Trust Section**:
- Navy service photo or insignia (authentic, high-quality)
- Certification badges/logos

**No large hero image** - the American flag IS the background treatment throughout, with hero content overlaid.

## Page Structure

1. **Hero**: Full viewport with flag background, headline "Serving Those Who Served" + veteran-focused value prop, CTA buttons (Check Rates + Calculate Savings), Dennis Ross headshot
2. **Live Rate Board**: White opacity panel, 3-4 current rates with loan types, last updated timestamp, "Rates updated daily" badge
3. **Veteran Benefits**: 3-column feature grid - VA Loans expertise, Military discount, Deployment flexibility
4. **Stats Bar**: 4 metrics across in white panels
5. **Why Dennis**: 2-column - left: Navy service story + credentials, right: professional photo/insignia
6. **Refinance Calculator**: Interactive tool in prominent white panel
7. **Testimonials**: 2-column veteran client reviews with ranks/service branches
8. **CTA Section**: Strong final push with contact form + phone number prominence
9. **Footer**: Trust badges, licenses, equal housing, contact info

**Color Notes** (for engineer): Blues from American flag palette - navy #003366 for primary, lighter blues for accents, red #B22234 sparingly for urgency elements, white for text on flag backgrounds.