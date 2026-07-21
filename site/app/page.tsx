import type { Metadata } from "next";
import Image from "next/image";
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
    "Get clear, personal Florida mortgage guidance from Navy veteran and mortgage broker Dennis Ross. Compare payments, loan options, and next steps before you apply.",
};

const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://drmortgageusa.com/#organization",
  name: "DR. Mortgage USA",
  alternateName: "Dennis Ross Mortgage Broker",
  url: "https://drmortgageusa.com/",
  description:
    "Florida mortgage guidance for buyers, homeowners, veterans, self-employed borrowers, and investors.",
  logo: {
    "@type": "ImageObject",
    url: "https://drmortgageusa.com/media/logo.webp",
    contentUrl: "https://drmortgageusa.com/media/logo.webp",
    width: 192,
    height: 158,
  },
  image: "https://drmortgageusa.com/media/dennis.webp",
  telephone: "+1-850-346-8514",
  sameAs: ["https://www.instagram.com/dr.mortgageusa"],
  areaServed: {
    "@type": "State",
    name: "Florida",
  },
  founder: {
    "@id": "https://drmortgageusa.com/about#dennis-ross",
  },
};

export default function Home() {
  return (
    <PageShell>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
      />
      <section className="home-hero">
        <div className="shell home-hero-grid">
          <div className="home-hero-copy">
            <div className="hero-editorial-meta" aria-label="Independent Florida mortgage guidance">
              <span>Independent guidance</span>
              <span>Florida · Est. 2020</span>
            </div>
            <Eyebrow>Florida mortgage guidance · straight answers first</Eyebrow>
            <h1>Let&apos;s make the mortgage make sense before you make a move.</h1>
            <p className="hero-lede">
              I&apos;m Dennis Ross. I help Florida buyers and homeowners understand
              the payment, the cash, and the choices before they commit to a loan.
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
            <Image
              src="/media/dennis.webp"
              alt="Dennis Ross, Florida mortgage broker and Navy veteran"
              width={720}
              height={720}
              priority
              unoptimized
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
            <Eyebrow>Start with your real budget</Eyebrow>
            <h2>What can you comfortably pay each month?</h2>
            <p>
              A loan approval tells you what may be possible. It does not tell you
              what will still feel comfortable after groceries, daycare, travel,
              savings, and everything else life brings.
            </p>
            <ul className="check-list">
              <li>Put in the taxes and insurance that match the home you are considering.</li>
              <li>See how different down payments change both your payment and cash needed.</li>
              <li>Save your numbers, or send them to me and I will help you check the assumptions.</li>
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
            <Eyebrow>Why people call me</Eyebrow>
            <blockquote>
              “You should understand every number, every tradeoff, and every next
              step before you feel pressured to move.”
            </blockquote>
            <p>
              I spent fifteen years serving in the Navy and built my first career
              in social work. Both taught me how to listen, stay calm, and explain
              hard decisions clearly. You will get a direct conversation, a
              plain-language recap, and options built around your actual life.
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
            title="You do not have to figure it all out before we talk."
            body="Start with the question on your mind. We will build the next step from there."
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
              title="If borrowers keep asking it, I write about it."
              body="The blog is where I answer the real Florida mortgage questions I hear every week, including VA, FHA, self-employed income, insurance, equity, and what to do next."
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
            <h2>Ask the question you are worried might sound basic.</h2>
            <p>
              You are not supposed to know all of this already. Start with a quick
              answer here, then reach out if your situation needs a closer look.
            </p>
            <div className="home-faq-actions">
              <Link className="button button-navy" href="/faq">Search every answer</Link>
              <Link className="text-link" href="/contact">Ask Dennis directly <span>→</span></Link>
            </div>
            <div className="home-faq-note">
              <strong>Straight answers, no blanket promises.</strong>
              <span>I will tell you what is generally true and what still depends on your actual file.</span>
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
            <h2>Ready to skip the planning and apply?</h2>
            <p>Use the secure application when you are ready to share income, assets, employment, and credit information.</p>
          </div>
          <a className="button button-navy" href={secureApplicationUrl}>Open secure application</a>
        </div>
      </section>

      <FinalCTA />
    </PageShell>
  );
}
