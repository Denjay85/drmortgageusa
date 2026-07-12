import type { Metadata } from "next";
import Link from "next/link";
import {
  Eyebrow,
  FinalCTA,
  PageShell,
  SectionHeading,
  secureApplicationUrl,
} from "./site-components";
import { blogPosts } from "./blog/posts";
import LatestBlogPosts from "./blog/LatestBlogPosts";
import { featuredFaqs } from "./faq/data";
import LiveRatesPanel from "./LiveRatesPanel";
import MortgageFlightDeck from "./MortgageFlightDeck";
import ClientMotionWall from "./ClientMotionWall";
import PremiumProcess from "./PremiumProcess";
import MortgagePathwaySection from "./MortgagePathwaySection";

export const metadata: Metadata = {
  title: "Florida Mortgage Guidance",
  alternates: { canonical: "/" },
  description:
    "Compare Florida mortgage paths, understand your payment, and get a clear next step with Navy veteran and mortgage broker Dennis Ross.",
};

export default function Home() {
  return (
    <PageShell>
      <section className="home-hero">
        <div className="shell home-hero-grid">
          <div className="home-hero-copy">
            <div className="hero-editorial-meta" aria-label="Independent Florida mortgage guidance">
              <span>Independent guidance</span>
              <span>Florida · Est. 2020</span>
            </div>
            <Eyebrow>Florida mortgage guidance · without the runaround</Eyebrow>
            <h1>Understand the numbers before you make the move.</h1>
            <p className="hero-lede">
              Dennis Ross helps Florida buyers compare mortgage paths, build a
              realistic payment, and know what comes next before a full application.
            </p>
            <div className="hero-actions">
              <Link className="button button-gold" href="/get-started">
                Build my mortgage plan
              </Link>
              <Link className="button button-outline-light" href="/tools">
                Run the numbers
              </Link>
            </div>
            <a
              className="hero-application-jump"
              href={secureApplicationUrl}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Open the secure mortgage application in a new tab"
            >
              <span className="hero-application-icon" aria-hidden="true">↗</span>
              <span>
                <small>Ready to apply now?</small>
                <strong>Open the secure application</strong>
              </span>
              <b aria-hidden="true">→</b>
            </a>
            <div className="hero-microcopy">
              <span>No credit check to start</span>
              <span>About 60 seconds</span>
              <span>Reviewed by a real loan officer</span>
            </div>
          </div>

          <div className="hero-portrait" aria-label="Dennis Ross, DR. Mortgage USA">
            <img
              src="/media/dennis.webp"
              alt="Dennis Ross, Florida mortgage broker and Navy veteran"
              width="720"
              height="720"
            />
            <div className="portrait-card portrait-card-top">
              <strong>Hundreds</strong>
              <span>Florida families served</span>
            </div>
            <div className="portrait-card portrait-card-bottom">
              <span className="portrait-card-kicker">Your guide</span>
              <strong>Dennis Ross</strong>
              <span>Navy Veteran · NMLS #2018381</span>
            </div>
          </div>

          <LiveRatesPanel />
        </div>
      </section>

      <section className="trust-strip" aria-label="Licensing and service highlights">
        <div className="shell trust-strip-grid">
          <div><strong>Florida</strong><span>Statewide service</span></div>
          <div><strong>VA · FHA · Conventional</strong><span>Plus specialty options</span></div>
          <div><strong>Human review</strong><span>No generic call center</span></div>
          <div><strong>Home 1st Lending</strong><span>Company NMLS #1418</span></div>
        </div>
      </section>

      <section className="section flight-deck-section">
        <div className="shell">
          <MortgageFlightDeck />
        </div>
      </section>

      <MortgagePathwaySection />

      <section className="depth-strip" aria-label="Popular mortgage resources">
        <div className="shell depth-grid">
          <Link href="/blog" className="depth-card">
            <span className="depth-card-icon">?</span>
            <div><small>Have a specific question?</small><strong>Search the mortgage blog</strong></div>
            <b aria-hidden="true">→</b>
          </Link>
          <Link href="/dpa" className="depth-card">
            <span className="depth-card-icon">DP</span>
            <div><small>Need help with cash to close?</small><strong>Explore DPA options</strong></div>
            <b aria-hidden="true">→</b>
          </Link>
          <Link href="/heloc-calculator" className="depth-card">
            <span className="depth-card-icon">EQ</span>
            <div><small>Thinking about home equity?</small><strong>Open the HELOC calculator</strong></div>
            <b aria-hidden="true">→</b>
          </Link>
        </div>
      </section>

      <section className="section section-cream">
        <div className="shell calculator-feature">
          <div className="calculator-copy">
            <Eyebrow>Start with the payment</Eyebrow>
            <h2>A comfortable budget is more useful than a maximum approval.</h2>
            <p>
              See principal, interest, taxes, insurance, HOA, and estimated
              mortgage insurance together. Then decide whether the payment fits
              your actual life.
            </p>
            <ul className="check-list">
              <li>Use editable taxes and insurance instead of a generic national average.</li>
              <li>Compare down-payment choices side by side.</li>
              <li>Save your scenario or ask Dennis to review it.</li>
            </ul>
            <div className="calculator-feature-actions">
              <Link className="button button-navy" href="/tools#purchase">Purchase payment</Link>
              <Link className="button button-outline-navy" href="/heloc-calculator">HELOC calculator</Link>
            </div>
          </div>
          <div className="payment-preview" aria-label="Example monthly payment breakdown">
            <div className="payment-preview-top">
              <span>Illustrative monthly payment</span>
              <strong>$3,236</strong>
              <small>$400,000 home · 5% down · sample assumptions</small>
            </div>
            <div className="payment-bar" aria-hidden="true">
              <span style={{ width: "72%" }} />
              <span style={{ width: "12%" }} />
              <span style={{ width: "9%" }} />
              <span style={{ width: "7%" }} />
            </div>
            <dl>
              <div><dt>Principal & interest</dt><dd>$2,528</dd></div>
              <div><dt>Property taxes</dt><dd>$400</dd></div>
              <div><dt>Home insurance</dt><dd>$150</dd></div>
              <div><dt>Estimated PMI</dt><dd>$158</dd></div>
            </dl>
            <p className="fine-print">Educational example only. Not a quote, approval, or offer to lend.</p>
          </div>
        </div>
      </section>

      <section className="section story-section">
        <div className="shell story-grid">
          <ClientMotionWall />
          <div className="story-copy">
            <Eyebrow>Why clients call Dennis</Eyebrow>
            <blockquote>
              “You should understand every number, every tradeoff, and every next
              step before you feel pressured to move.”
            </blockquote>
            <p>
              Dennis brings the discipline of fifteen years of Navy service and
              the calm of a trained social worker to a process that can otherwise
              feel confusing. You get a direct conversation, a plain-language
              recap, and options shaped around your file.
            </p>
            <div className="story-actions">
              <Link className="text-link" href="/about">Meet Dennis <span>→</span></Link>
              <a className="text-link" href="https://www.google.com/search?q=Dennis+Ross+Mortgage+Reviews">Read Google reviews <span>→</span></a>
            </div>
          </div>
        </div>
      </section>

      <section className="section process-section">
        <div className="shell">
          <SectionHeading
            eyebrow="A calmer process"
            title="From curious to confident in three steps."
            body="Start small. Share more only when the next step makes sense."
            align="center"
          />
          <PremiumProcess />
        </div>
      </section>

      <section className="section resource-section">
        <div className="shell">
          <div className="resource-heading-row">
            <SectionHeading
              eyebrow="Useful, not generic"
              title="The blog turns real questions into useful next steps."
              body="Dennis is continually publishing Florida-specific answers about VA, FHA, self-employed income, insurance, equity, and the decisions buyers face right now."
            />
            <Link className="text-link" href="/blog">Search the blog <span>→</span></Link>
          </div>
          <LatestBlogPosts initialPosts={blogPosts.slice(0, 3)} />
        </div>
      </section>

      <section className="section section-cream home-faq-section" id="faq">
        <div className="shell home-faq-layout">
          <div className="home-faq-intro">
            <Eyebrow>Questions before the call</Eyebrow>
            <h2>Get the concern out of the way, then decide what deserves a closer look.</h2>
            <p>
              These are the questions most likely to stop a borrower from taking
              the next step. The full library goes deeper without turning the
              homepage into a mortgage textbook.
            </p>
            <div className="home-faq-actions">
              <Link className="button button-navy" href="/faq">Search every answer</Link>
              <Link className="text-link" href="/contact">Ask Dennis directly <span>→</span></Link>
            </div>
            <div className="home-faq-note">
              <strong>No blanket promises.</strong>
              <span>Answers explain the framework and show what still depends on the actual file.</span>
            </div>
          </div>

          <div className="home-faq-list">
            {featuredFaqs.map((item, index) => (
              <details className="home-faq-item" data-faq-id={item.id} open={index === 0} key={item.id}>
                <summary>
                  <span>{item.question}</span>
                  <i aria-hidden="true" />
                </summary>
                <div>
                  <p>{item.answer}</p>
                  {item.links?.length ? (
                    <nav aria-label={`Next steps for ${item.question}`}>
                      {item.links.map((link) => (
                        <Link href={link.href} key={link.label}>{link.label} <span aria-hidden="true">→</span></Link>
                      ))}
                    </nav>
                  ) : null}
                </div>
              </details>
            ))}
          </div>
        </div>
      </section>

      <section className="section apply-band">
        <div className="shell apply-band-inner">
          <div>
            <Eyebrow>Already know what you need?</Eyebrow>
            <h2>Move directly to the secure application.</h2>
            <p>Use this path when you are ready to share income, assets, employment, and credit information.</p>
          </div>
          <a className="button button-navy" href={secureApplicationUrl}>Open secure application</a>
        </div>
      </section>

      <FinalCTA />
    </PageShell>
  );
}
