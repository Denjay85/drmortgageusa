# Overview

This is a lead generation and management web application for DrMortgageUSA's "Rate Watch" service. The application allows homeowners to sign up for mortgage rate monitoring and receive email notifications when refinancing becomes financially beneficial. It features a public-facing lead capture form and an administrative dashboard for managing submitted leads.

The application is built as a full-stack TypeScript project with a React frontend and Express backend, using PostgreSQL for data persistence.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture

**Framework & Routing**: React 18+ with Wouter for client-side routing. The application uses a multi-page structure with three main routes:
- Home page (`/`) - Lead capture form with hero section
- Learn More page (`/learn`) - Educational content about the Rate Watch service
- Admin page (`/admin`) - Lead management dashboard

**UI Framework**: Shadcn/ui component library built on Radix UI primitives with Tailwind CSS for styling. The design system uses CSS variables for theming with a "new-york" style configuration.

**State Management**: TanStack Query (React Query) for server state management with custom query client configuration. Form state is managed using React Hook Form with Zod validation.

**Styling Approach**: Tailwind CSS with custom design tokens defined in CSS variables. The theme supports light/dark modes and uses a neutral base color scheme with blue primary and green accent colors.

## Backend Architecture

**Server Framework**: Express.js with TypeScript, running in ESM module mode. The server handles both API routes and serves the Vite-built frontend in production.

**Development Setup**: Vite dev server integrated with Express using middleware mode, providing HMR (Hot Module Replacement) and development tooling through Replit-specific plugins.

**API Design**: RESTful API with the following endpoints:
- `POST /api/leads` - Create new lead submissions
- `GET /api/leads` - Retrieve leads with filtering, pagination, and search capabilities
- Additional CRUD operations for lead management (update status, delete)

**Data Layer**: Storage abstraction interface (`IStorage`) with in-memory implementation (`MemStorage`). This allows for easy swapping to database-backed storage without changing business logic.

## Data Storage

**Database**: PostgreSQL via Neon serverless driver (`@neondatabase/serverless`). The application is configured for Postgres but currently uses an in-memory storage fallback.

**ORM**: Drizzle ORM for type-safe database operations with schema defined in `shared/schema.ts`. The schema includes:
- `leads` table with fields for contact information, loan details, savings goals, UTM tracking, and status management
- Validation schemas using Drizzle-Zod for runtime type checking

**Session Management**: Prepared for connect-pg-simple for PostgreSQL-backed sessions, though not yet fully implemented.

## Authentication & Authorization

Currently, the application does not implement authentication. The admin dashboard is publicly accessible. This is a known limitation that should be addressed before production deployment.

## Email Notifications

**Service**: Resend API for transactional emails (configuration present but requires API key setup)

**Functionality**: Automated email notifications sent when new leads are submitted, containing lead details formatted as HTML emails. Email failures are logged but don't prevent lead submission from succeeding.

## External Dependencies

**Third-Party Services**:
- **Calendly**: Widget integration for scheduling consultations (embedded in modal)
- **Resend**: Email delivery service for lead notifications
- **Neon Database**: Serverless PostgreSQL hosting
- **Zapier/Formspree**: Optional webhook endpoints for form submissions (referenced in attached assets)

**Key NPM Packages**:
- `@tanstack/react-query` - Server state management
- `react-hook-form` + `@hookform/resolvers` - Form handling and validation
- `zod` + `drizzle-zod` - Runtime validation and schema definition
- `wouter` - Lightweight client-side routing
- `date-fns` - Date formatting and manipulation
- `nanoid` - Unique ID generation
- Radix UI components - Accessible UI primitives
- `class-variance-authority` + `clsx` + `tailwind-merge` - Styling utilities

**Development Tools**:
- Vite - Build tool and dev server
- TypeScript - Type safety across the stack
- Drizzle Kit - Database migration tooling
- esbuild - Server bundling for production

**Replit Integration**:
- `@replit/vite-plugin-runtime-error-modal` - Development error handling
- `@replit/vite-plugin-cartographer` - Code navigation
- `@replit/vite-plugin-dev-banner` - Development banner

## Build & Deployment

**Development**: `npm run dev` starts the Express server with integrated Vite dev server on port 5000

**Production Build**: 
1. `vite build` - Builds client to `dist/public`
2. `esbuild` - Bundles server to `dist/index.js`

**Environment Variables Required**:
- `DATABASE_URL` - PostgreSQL connection string
- `RESEND_API_KEY` - Email service API key (optional)
- `ADMIN_EMAIL` - Recipient for lead notifications
- `FROM_EMAIL` - Sender address for emails