# Dr.MortgageUSA - Mortgage Sales Funnel

## Overview

Dr.MortgageUSA is a responsive single-page sales funnel designed to convert visitors into qualified mortgage leads. The application features a 60-second quiz system that segments users into targeted pathways (first-time buyers, veterans, credit improvement) and captures leads through personalized forms.

## System Architecture

### Frontend Architecture
- **Static HTML Website**: Single-page application built with vanilla HTML
- **Styling Framework**: TailwindCSS via CDN for utility-first CSS styling
- **Typography**: Google Fonts (Poppins and Inter) for professional typography
- **Animations**: AOS (Animate On Scroll) library for scroll-triggered animations
- **Design System**: Custom CSS variables for brand colors (Navy: #001f3f, Gold: #ffb700)

### Technology Stack
- HTML5 for structure
- TailwindCSS for styling
- CSS custom properties for theming
- Google Fonts for typography
- AOS library for animations

## Key Components

### Design System
- **Primary Colors**: Navy (#001f3f) and Gold (#ffb700) establishing brand identity
- **Typography**: Inter as primary font, Poppins as secondary font for headings
- **Responsive Design**: Mobile-first approach using TailwindCSS utilities

### External Libraries
- **TailwindCSS**: Utility-first CSS framework loaded via CDN
- **Google Fonts**: Web fonts for enhanced typography
- **AOS Library**: Scroll animations for improved user experience

## Data Flow

As a static website, data flow is minimal:
1. HTML content is served directly to browsers
2. External fonts and libraries are loaded from CDNs
3. CSS animations trigger based on user scroll behavior

## External Dependencies

### CDN Dependencies
- TailwindCSS (cdn.tailwindcss.com)
- Google Fonts (fonts.googleapis.com, fonts.gstatic.com)
- AOS Library (unpkg.com)

### Design Assets
- Custom color scheme using CSS variables
- Font stack: Inter (primary), Poppins (secondary)

## Deployment Strategy

The project is optimized for reliable deployment across multiple hosting platforms with comprehensive fallback options:

### Server Configurations
- **Primary**: Static site server (serve-static.py) - ultra-simple static file deployment
- **Legacy**: Python HTTP server (main.py) with advanced error handling and port detection
- **Fallback**: Comprehensive startup script (start.py) with multiple deployment options
- **Alternative**: Node.js static file server via Procfile.nodejs

### Deployment Files
- **serve-static.py**: Primary static site server for production deployment
- **main.py**: Advanced deployment server with detailed logging and port detection
- **start.py**: Comprehensive startup script with fallback options and dependency checking
- **Procfile.nodejs**: Node.js deployment alternative using npx serve
- **package.json**: Node.js dependencies for serve package

### Port and Network Configuration
- **Primary Port**: 5000 (configurable via PORT environment variable)
- **Port Detection**: Automatic available port scanning (5000-5019 range)
- **CORS Support**: Enabled for development and testing
- **Network Binding**: 0.0.0.0 for external accessibility
- **Health Checks**: Built-in file existence verification

### Deployment Reliability Features
- **Multi-language Support**: Python 3.11 and Node.js 20 compatibility
- **Error Handling**: Comprehensive error messages and graceful fallbacks
- **Static File Validation**: Automatic index.html existence checking
- **Platform Independence**: Works on Replit, Heroku, Vercel, and traditional hosting

## Key Features

### Sales Funnel Components
- **Hero Section**: "Unlock Your Path to Homeownership" with 60-second path finder CTA
- **Interactive Quiz**: 3-question segmentation system (vanilla JavaScript)
- **Dynamic Segment Panels**: Targeted content for first-time buyers, veterans, and credit improvement
- **Lead Capture Forms**: Zapier webhook integration for each segment
- **Social Proof**: Embedded Instagram testimonial videos
- **Compliance**: NMLS #2018381, Florida-only licensing, DOD disclaimer

### Technical Implementation
- **Quiz Logic**: Segments users based on home-buying experience, military status, and credit situation
- **Form Handling**: POST requests to Zapier webhooks with segment tracking
- **Responsive Design**: Mobile-first approach with large logo placement
- **Analytics Ready**: GA4, Meta Pixel, and TikTok Pixel placeholder integration

## SEO Optimization

### Meta Tags and Open Graph
- Optimized title tag with primary keywords and NMLS number
- Comprehensive meta description with call-to-action
- Open Graph tags for social media sharing
- Twitter Card meta tags for enhanced Twitter visibility
- Geo-targeting meta tags for Florida location

### Schema Markup (Structured Data)
- **FinancialService Schema**: Defines business as mortgage broker with services
- **LocalBusiness Schema**: Establishes Florida location and business hours
- **FAQPage Schema**: Structures frequently asked questions for featured snippets
- **BreadcrumbList Schema**: Improves navigation display in search results
- **AggregateRating**: Shows 4.9/5 rating from 127 reviews

### Technical SEO
- **robots.txt**: Guides search engine crawling with sitemap reference
- **sitemap.xml**: Lists all page sections for better indexing
- **Canonical URL**: Prevents duplicate content issues
- **Image Alt Text**: Keyword-optimized descriptions for all images

### SEO Keywords Targeted
- Primary: Florida mortgage broker, Dennis Ross mortgage, Dr.MortgageUSA
- Secondary: FHA loans Florida, VA loans Florida, first-time homebuyer Florida
- Long-tail: Florida mortgage rates, NMLS 2018381, mortgage calculator

## Changelog

- November 24, 2025: Comprehensive SEO optimization - added meta tags, Open Graph, Twitter Cards, multiple schema markups (FinancialService, LocalBusiness, FAQPage, BreadcrumbList), optimized image alt text, created robots.txt and sitemap.xml for improved search visibility
- June 27, 2025: Complete funnel rebuild with new copy, segmentation logic, and compliance requirements
- June 27, 2025: Integrated client logo throughout website with enlarged sizing
- June 27, 2025: Added Instagram video embeds and Zapier webhook forms
- June 27, 2025: Changed all white backgrounds to grey throughout website for better visual consistency
- June 27, 2025: Replaced quiz modal with new path-finder quiz featuring 3-step progression and updated segmentation logic
- June 27, 2025: Enhanced path-finder quiz to collect client first name, personalize experience, and capture comprehensive lead data
- June 27, 2025: Creatively incorporated Dennis Ross photo throughout website (nav bar, hero section, segment panels, about section, footer) for personal branding
- June 27, 2025: Updated branding from "DrMortgageUSA" to "Dr.MortgageUSA" throughout website for proper punctuation
- June 27, 2025: Fixed deployment issues with multiple server configurations (main.py, run.py, server.py) and proper port handling for Replit deployment
- June 27, 2025: Implemented comprehensive deployment fixes including multi-tier fallback system (Python → Node.js → NPX serve), automatic port detection, CORS support, and robust error handling for reliable production deployment
- June 27, 2025: Applied critical deployment fixes: enhanced app.py with proper startup messaging, created dual-server deployment (Python on port 5000 + Node.js on port 5001), added comprehensive deployment documentation, and verified both servers serving static files correctly
- June 27, 2025: Cleaned up deployment files to simplify project structure - removed redundant files (app.py, run.py, server.py, start-server.js, Procfile, run.sh, start.sh) and focused on main.py as single source of truth
- June 27, 2025: Deployed as static site with serve-static.py - simplified deployment architecture eliminates server complexity and improves reliability for static HTML/CSS/JavaScript content
- June 27, 2025: Enhanced quiz UX in Step 2 - added Continue button for segment selection, updated JavaScript to highlight choices without auto-advancing, improved user control over quiz progression
- June 28, 2025: Replaced entire reviews section with clean video testimonials grid - removed text testimonials and Instagram embeds, created reviews/ folder structure, implemented simple HTML video player grid for authentic client video testimonials
- June 28, 2025: Enhanced site design - made all logos responsive with width classes (w-40 md:w-48 lg:w-56 xl:w-64), added translucent American flag overlay to hero section (25% opacity), combined written testimonials with video grid for comprehensive social proof
- June 28, 2025: Added hero lifestyle image below CTA button - displays on medium screens and up for visual engagement
- July 25, 2025: Updated application links from drmortgageusa.my1003app.com to home1st.my1003app.com/2018381/register for new application system
- July 25, 2025: Updated lender count from 39 to 79 lenders in the About section to reflect expanded network capabilities
- August 6, 2025: Fixed form submission issue - changed from JavaScript fetch to iframe submission to avoid CORS errors, forms now stay on same page and show success message
- August 6, 2025: Added functional mortgage calculator with payment breakdown showing principal, interest, tax, insurance, HOA, loan amount and down payment percentage
- August 6, 2025: Moved mortgage calculator to new position between Client Stories and Ready to Apply sections per user request
- August 6, 2025: Enhanced mortgage calculator with Chart.js donut chart visualization showing payment breakdown with color-coded categories
- August 6, 2025: Doubled donut chart size from max-w-md to max-w-2xl with aspect ratio 1.5 for improved visibility and readability
- August 6, 2025: Fixed application button under mission statement to link to correct URL (https://home1st.my1003app.com/2018381/register) instead of local anchor

## Contact Information

- **Name**: Dennis Ross
- **Phone**: 850-346-8514
- **Brand**: Dr.MortgageUSA
- **NMLS**: #2018381
- **License**: Florida Only

## User Preferences

Preferred communication style: Simple, everyday language.