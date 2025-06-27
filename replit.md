# DrMortgageUSA - Mortgage Services Website

## Overview

DrMortgageUSA is a static website for a mortgage services company that positions itself as a trusted mortgage partner. The project is built using HTML and TailwindCSS with a focus on modern design and user experience.

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

## Changelog

- June 27, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.