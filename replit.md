# DrMortgageUSA - Mortgage Sales Funnel

## Overview

DrMortgageUSA is a responsive single-page sales funnel designed to convert visitors into qualified mortgage leads. The application features a 60-second quiz system that segments users into targeted pathways (first-time buyers, veterans, credit improvement) and captures leads through personalized forms.

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

The project is designed for static hosting deployment:
- **Hosting Options**: Any static file hosting service (Netlify, Vercel, GitHub Pages, AWS S3)
- **Build Process**: No build step required - direct HTML serving
- **Performance**: CDN-based external resources for fast loading
- **Scalability**: Static nature allows for global CDN distribution

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

## Contact Information

- **Name**: Dennis Ross
- **Phone**: 850-346-8514
- **Brand**: DrMortgageUSA
- **NMLS**: #2018381
- **License**: Florida Only

## User Preferences

Preferred communication style: Simple, everyday language.