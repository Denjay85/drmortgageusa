import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";
import ScenarioDock from "./ScenarioDock";
import SiteAtmosphere from "./SiteAtmosphere";

export const secureApplicationUrl =
  "https://home1st.my1003app.com/2018381/register";

export function Header() {
  return (
    <>
      <div className="topline">
        <div className="shell topline-inner">
          <span>Florida mortgage guidance, built around your numbers.</span>
          <span className="topline-proof">NMLS #2018381 · Navy Veteran · Orlando, FL</span>
        </div>
      </div>
      <header className="site-header">
        <div className="shell header-inner">
          <Link href="/" className="brand" aria-label="DR. Mortgage USA home">
            <span className="brand-mark" aria-hidden="true">
              <Image src="/media/logo.webp" alt="" width={48} height={48} priority unoptimized />
            </span>
            <span>
              <strong>DR. Mortgage USA</strong>
              <small>Dennis Ross · Mortgage Broker</small>
            </span>
          </Link>

          <nav className="desktop-nav" aria-label="Primary navigation">
            <Link href="/mortgage-options">Mortgage options</Link>
            <Link className="nav-dpa" href="/dpa">DPA programs</Link>
            <Link href="/#rates">Today&apos;s rates</Link>
            <Link href="/tools">Tools</Link>
            <Link href="/resources">Resources</Link>
            <Link href="/blog">Blog</Link>
            <Link href="/faq">FAQ</Link>
            <Link href="/about">About Dennis</Link>
          </nav>

          <div className="header-actions">
            <a className="header-phone" href="tel:+18503468514" aria-label="Call Dennis at 850-346-8514">
              <small>Call Dennis</small>
              <strong>(850) 346-8514</strong>
            </a>
            <Link className="button button-gold button-small" href="/get-started">
              Build my plan
            </Link>
          </div>

          <details className="mobile-menu">
            <summary aria-label="Open navigation">Menu</summary>
            <nav aria-label="Mobile navigation">
              <Link href="/mortgage-options">Mortgage options</Link>
              <Link className="nav-dpa" href="/dpa">DPA programs</Link>
              <Link href="/#rates">Today&apos;s rates</Link>
              <Link href="/tools">Tools & calculators</Link>
              <Link href="/resources">Resources</Link>
              <Link href="/blog">Blog</Link>
              <Link href="/faq">Mortgage FAQ</Link>
              <Link href="/about">About Dennis</Link>
              <Link href="/contact">Book a conversation</Link>
              <Link className="button button-gold" href="/get-started">Build my plan</Link>
            </nav>
          </details>
        </div>
      </header>
    </>
  );
}

export function Footer() {
  return (
    <footer className="site-footer">
      <div className="shell footer-grid">
        <div className="footer-brand">
          <Link href="/" className="brand brand-light">
            <span className="brand-mark" aria-hidden="true">
              <Image src="/media/logo.webp" alt="" width={56} height={56} unoptimized />
            </span>
            <span>
              <strong>DR. Mortgage USA</strong>
              <small>Clear numbers. Human guidance.</small>
            </span>
          </Link>
          <p>
            Mortgage guidance for Florida buyers, homeowners, veterans, and
            investors without the call-center runaround.
          </p>
          <a className="footer-phone" href="tel:+18503468514">850-346-8514</a>
        </div>

        <div>
          <h2>Explore</h2>
          <Link href="/mortgage-options">Mortgage options</Link>
          <Link href="/#rates">Today&apos;s rates</Link>
          <Link href="/tools">Calculators & tools</Link>
          <Link href="/resources">Guides & updates</Link>
          <Link href="/dpa">Down payment assistance</Link>
          <Link href="/blog">Mortgage blog</Link>
          <Link href="/faq">Mortgage FAQ</Link>
          <Link href="/about">Meet Dennis</Link>
        </div>

        <div>
          <h2>Next step</h2>
          <Link href="/get-started">Build my mortgage plan</Link>
          <Link href="/contact">Book a conversation</Link>
          <a href={secureApplicationUrl}>Secure application</a>
          <a href="https://www.instagram.com/dr.mortgageusa">Instagram</a>
        </div>

        <div>
          <h2>Important</h2>
          <Link href="/legal#privacy">Privacy</Link>
          <Link href="/legal#terms">Terms</Link>
          <Link href="/legal#sms">SMS terms</Link>
          <Link href="/legal#accessibility">Accessibility</Link>
          <Link href="/legal#licensing">Licensing & disclosures</Link>
        </div>
      </div>

      <div className="shell footer-disclosure">
        <p>
          Dennis Ross, Mortgage Loan Originator, NMLS #2018381. Licensed in
          Florida. Powered by Home 1st Lending, LLC, NMLS #1418. Equal Housing
          Opportunity. All loans are subject to credit and property approval.
          Programs, rates, and availability may change without notice.
        </p>
        <p>© 2026 DR. Mortgage USA. All rights reserved.</p>
      </div>
    </footer>
  );
}

export function PageShell({ children }: { children: ReactNode }) {
  return (
    <>
      <SiteAtmosphere />
      <Header />
      <main>{children}</main>
      <Footer />
      <ScenarioDock />
      <div className="mobile-actions" aria-label="Quick actions">
        <a className="button button-outline-light" href="tel:+18503468514">Call Dennis</a>
        <Link className="button button-gold" href="/get-started">Build my plan</Link>
      </div>
    </>
  );
}

export function Eyebrow({ children }: { children: ReactNode }) {
  return <p className="eyebrow">{children}</p>;
}

export function SectionHeading({
  eyebrow,
  title,
  body,
  align = "left",
}: {
  eyebrow: string;
  title: string;
  body?: string;
  align?: "left" | "center";
}) {
  return (
    <div className={`section-heading ${align === "center" ? "section-heading-center" : ""}`}>
      <Eyebrow>{eyebrow}</Eyebrow>
      <h2>{title}</h2>
      {body ? <p>{body}</p> : null}
    </div>
  );
}

export function IconBadge({ children }: { children: ReactNode }) {
  return <span className="icon-badge" aria-hidden="true">{children}</span>;
}

export function PageHero({
  eyebrow,
  title,
  body,
  children,
}: {
  eyebrow: string;
  title: string;
  body: string;
  children?: ReactNode;
}) {
  return (
    <section className="page-hero">
      <div className="shell page-hero-inner">
        <Eyebrow>{eyebrow}</Eyebrow>
        <h1>{title}</h1>
        <p>{body}</p>
        {children ? <div className="hero-actions">{children}</div> : null}
      </div>
    </section>
  );
}

export function FinalCTA({
  title = "Know the path before you fill out the application.",
  body = "Answer a few simple questions and get a clearer next step without a credit check.",
}: {
  title?: string;
  body?: string;
}) {
  return (
    <section className="final-cta">
      <div className="shell final-cta-inner">
        <div>
          <Eyebrow>Your next move</Eyebrow>
          <h2>{title}</h2>
          <p>{body}</p>
        </div>
        <div className="final-cta-actions">
          <Link className="button button-gold" href="/get-started">Build my mortgage plan</Link>
          <Link className="button button-outline-light" href="/contact">Book a conversation</Link>
        </div>
      </div>
    </section>
  );
}
