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
- **Interactive Quiz**: 3-question JavaScript-driven segmentation, including a specialized path for real estate investors with various financing options.
- **Dynamic Segment Panels**: Targeted content and lead capture forms for different user segments.
- **Lead Capture**: Zapier webhook integration for form submissions, including detailed user data and segment tracking.
- **Social Proof**: Embedded video testimonials and client stories.
- **Mortgage Calculator**: Native multi-tab calculator (Purchase, Affordability, Refinance) with Chart.js donut chart visualization.
- **SEO Optimization**: Extensive meta tags, Open Graph, Twitter Cards, and multiple schema markups (FinancialService, LocalBusiness, FAQPage, BreadcrumbList) for improved search visibility. Includes `robots.txt` and `sitemap.xml`.
- **Compliance**: NMLS #2018381, Florida-only licensing, DOD disclaimer.
- **Deployment**: Optimized for static site deployment with Python-based servers (e.g., `serve-static.py`, `main.py`) and Node.js alternatives, featuring automatic port detection, CORS support, and robust error handling.

## External Dependencies
- **TailwindCSS CDN**: `cdn.tailwindcss.com`
- **Google Fonts**: `fonts.googleapis.com`, `fonts.gstatic.com`
- **AOS Library**: `unpkg.com`
- **Zapier**: For webhook integration and lead processing.
- **Chart.js**: For mortgage calculator visualizations.
- **Google Analytics 4 (GA4)**, **Meta Pixel**, **TikTok Pixel**: Placeholders for analytics integration.