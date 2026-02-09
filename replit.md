# Dr.MortgageUSA - Mortgage Sales Funnel

## Overview
Dr.MortgageUSA is a responsive single-page sales funnel designed to convert visitors into qualified mortgage leads. It features a 60-second quiz system that segments users into targeted pathways (first-time buyers, veterans, credit improvement, real estate investors) and captures leads through personalized forms. The project aims to provide an efficient and engaging platform for mortgage lead generation, leveraging interactive elements and robust SEO.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture
### Frontend
- **Framework**: Vanilla HTML for a static single-page application.
- **Styling**: TailwindCSS via CDN for utility-first approach; custom CSS variables for branding (Navy: #001f3f, Gold: #ffb700).
- **Typography**: Google Fonts (Poppins for headings, Inter for body text).
- **Animations**: AOS (Animate On Scroll) library.
- **Responsiveness**: Mobile-first design using TailwindCSS.

### Core Features
- **Interactive Quiz**: 5-step JavaScript-driven segmentation with early email capture, including specialized paths for first-time buyers, veterans, credit improvement, and real estate investors.
- **Dynamic Segment Panels**: Targeted content and lead capture forms for different user segments.
- **Lead Capture**: Dual storage - PostgreSQL database for internal management AND Zapier webhook forwarding for automation.
- **Admin Dashboard**: Password-protected dashboard at `/admin` to view and manage quiz lead submissions with search and filter functionality.
- **Social Proof**: Embedded video testimonials and client stories.
- **Mortgage Calculator**: Comprehensive 8-tab calculator suite (Purchase, Affordability, Refinance, Rent vs Buy, VA Purchase, VA Refinance, DSCR, Fix & Flip) with Chart.js donut chart visualization. VA calculators include automatic funding fee calculation. DSCR calculator includes color-coded ratio indicator.
- **SEO Optimization**: Extensive meta tags, Open Graph, Twitter Cards, and multiple schema markups (FinancialService, LocalBusiness, FAQPage, BreadcrumbList) for improved search visibility. Includes `robots.txt` and `sitemap.xml`.
- **Compliance**: NMLS #2018381, Florida-only licensing, DOD disclaimer.
- **Deployment**: Flask-based server (app.py) with PostgreSQL database integration, session-based authentication, and robust error handling.

### Backend (Flask)
- **app.py**: Main Flask application handling static file serving, quiz submission API, and admin dashboard.
- **Routes**:
  - `/`: Main website
  - `/api/quiz-submit`: POST endpoint for quiz submissions (stores in DB + forwards to Zapier)
  - `/admin`: Password-protected admin login
  - `/admin/dashboard`: Lead management dashboard with search and segment filtering
- **Security**: 
  - ADMIN_PASSWORD environment variable required (no fallbacks)
  - Constant-time password comparison to prevent timing attacks
  - Secure session management

## External Dependencies
- **TailwindCSS CDN**: `cdn.tailwindcss.com`
- **Google Fonts**: `fonts.googleapis.com`, `fonts.gstatic.com`
- **AOS Library**: `unpkg.com`
- **Zapier**: For webhook integration and lead processing.
- **Chart.js**: For mortgage calculator visualizations.
- **Google Analytics 4 (GA4)**, **Meta Pixel**, **TikTok Pixel**: Placeholders for analytics integration.