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
- **Primary**: Python HTTP server (main.py) with optimized error handling and port detection
- **Backup Servers**: Multiple fallback configurations (run.py, server.py)
- **Node.js Alternative**: Custom Node.js static file server (start-server.js)
- **NPX Serve**: Package-based static file serving via npm serve package

### Deployment Files
- **Procfile**: Multi-tier fallback deployment command: `python main.py || node start-server.js || npx serve -s . -l $PORT`
- **package.json**: Auto-generated with serve dependency for Node.js fallback
- **start.sh**: Comprehensive startup script with dependency checking and error reporting
- **start-server.js**: Custom Node.js HTTP server with MIME type support and CORS headers

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

## Changelog

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
- June 27, 2025: Replaced website with simplified, cleaner version - removed Instagram embeds, streamlined quiz logic, updated form actions to https://drmortgageusa.my1003app.com, and improved overall performance

## Contact Information

- **Name**: Dennis Ross
- **Phone**: 850-346-8514
- **Brand**: Dr.MortgageUSA
- **NMLS**: #2018381
- **License**: Florida Only

## User Preferences

Preferred communication style: Simple, everyday language.