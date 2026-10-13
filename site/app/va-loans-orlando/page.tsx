import type { Metadata } from "next";
import { Eyebrow, PageHero, PageShell, SectionHeading, secureApplicationUrl } from "../site-components";
import VaReviewForm from "./VaReviewForm";
import content from "./content.json";

// Generated from scripts/generate_service_pages.py; keep the fallback in sync.
const { page, schema, faqSchema } = content;
const canonical = `https://drmortgageusa.com/${page.slug}`;

export const metadata: Metadata = {
  title: { absolute: page.title },
  description: page.description,
  alternates: { canonical },
  openGraph: {
    title: page.title, description: page.description, url: canonical,
    type: "website", siteName: "DR. Mortgage USA",
    images: [{ url: "https://drmortgageusa.com/dennis-ross-headshot.png", width: 1000, height: 1000, alt: "Dennis Ross, Navy veteran and Florida mortgage broker" }],
  },
  twitter: {
    card: "summary_large_image", title: page.title, description: page.description,
    images: ["https://drmortgageusa.com/dennis-ross-headshot.png"],
  },
};

const guides = [
  ["VA loan credit score requirements in Florida", "/blog/va-loan-credit-score-requirements-florida-2026"],
  ["VA termite inspection requirements in Florida", "/blog/va-termite-inspection-requirements-florida-2026"],
  ["How to check a Florida condo for VA financing", "/blog/va-approved-condos-florida-check-project"],
  ["VA occupancy requirements and common exceptions", "/blog/va-loan-occupancy-requirements-florida-2026"],
  ["VA seller concessions for Florida homebuyers", "/blog/va-loan-seller-concessions-florida"],
  ["VA minimum property requirements in Florida", "/blog/va-minimum-property-requirements-florida-2026"],
  ["Complete Florida VA loan guide for veterans", "/blog/va-loan-guide-florida-veterans-2026"],
];

export default function VaLoansPage() {
  return (
    <PageShell>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema).replace(/</g, "\\u003c") }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema).replace(/</g, "\\u003c") }} />
      <PageHero eyebrow={page.eyebrow} title={page.hero_title} body={page.hero_lead}>
        <a className="button button-gold" href={page.primary_cta[1]}>{page.primary_cta[0]}</a>
        <a className="button button-outline-light" href={page.secondary_cta[1]}>{page.secondary_cta[0]}</a>
        <a className="va-hero-guide" href={page.support_cta[1]}>{page.support_cta[0]} <span aria-hidden="true">→</span></a>
      </PageHero>

      <section className="trust-strip" aria-label="VA loan benefits">
        <div className="shell trust-strip-grid va-benefit-grid">
          {page.hero_stats.map(([title, body]) => <div key={title}><strong>{title}</strong><span>{body}</span></div>)}
        </div>
      </section>

      <section className="section section-cream">
        <div className="shell contact-grid">
          <VaReviewForm heading={page.form_heading} description={page.form_text} />
          <aside className="contact-aside">
            <Eyebrow>Veteran to veteran</Eyebrow>
            <h2>{page.trust_heading}</h2>
            {page.trust_points.map(([title, body]) => <div className="contact-option" key={title}><strong>{title}</strong><p>{body}</p></div>)}
            <a className="text-link va-profile-link" href="/about">Meet Dennis <span aria-hidden="true">→</span></a>
          </aside>
        </div>
      </section>

      <section className="content-section">
        <div className="shell">
          {page.sections.map((section) => <article className="option-row" key={section.title}>
            <div><Eyebrow>Build your VA plan</Eyebrow><h2>{section.title}</h2></div>
            <div className="option-row-copy"><p>{section.body}</p><ul className="check-list">{section.items.map((item) => <li key={item}>{item}</li>)}</ul></div>
          </article>)}
        </div>
      </section>

      <section className="section section-cream">
        <div className="shell">
          <SectionHeading eyebrow="A clearer path" title="What happens next" />
          <div className="process-grid va-process-grid">
            {page.process_points.map(([number, title, body]) => <article key={number}><span>{number.padStart(2, "0")}</span><h3>{title}</h3><p>{body}</p></article>)}
          </div>
        </div>
      </section>

      <section className="section" id="greater-orlando-va-service-area">
        <div className="shell content-grid-two va-resources">
          <article className="info-card">
            <Eyebrow>Local guidance</Eyebrow>
            <h2>VA loan guidance across Greater Orlando</h2>
            <p>Dennis works from Lake Mary and serves veterans, active-duty service members, and eligible military families throughout the Greater Orlando area.</p>
            <ul className="check-list">{page.local_service_areas.map((area) => <li key={area}>{area}</li>)}</ul>
          </article>
          <article className="info-card">
            <Eyebrow>Know your sources</Eyebrow>
            <h2>Official VA and licensing sources</h2>
            <p>Use VA.gov for benefit rules and Dennis for help applying those rules to your documented loan scenario.</p>
            <ul className="va-resource-links">{page.official_resources.map(([label, href]) => <li key={href}><a href={href}>{label}</a></li>)}</ul>
            <p>Before you take VA advice from anyone, verify who you are talking to. You can confirm <a href="https://www.nmlsconsumeraccess.org/EntityDetails.aspx/INDIVIDUAL/2018381">Dennis Ross, NMLS 2018381</a>, view his <a href="https://myhome1st.com/dennis/">official Home 1st Lending profile</a>, or <a href="https://www.google.com/maps?cid=3829412552217676351">read client reviews on Google</a>.</p>
            <p>You can also view <a href="https://www.experience.com/reviews/dennis-14873595">Dennis&apos;s Experience.com profile</a>, which lists his VA Home Loan services and links to customer reviews.</p>
          </article>
        </div>
      </section>

      <section className="section section-cream" id="orlando-va-loan-guides">
        <div className="shell">
          <SectionHeading eyebrow="Keep learning" title="VA loan guides for Orlando and Florida buyers" body="Use these plain-language guides to answer the questions that most often affect a VA pre-approval, property review, contract, or closing plan." />
          <ul className="va-guide-grid">{guides.map(([label, href]) => <li key={href}><a href={href}>{label}<span aria-hidden="true">→</span></a></li>)}</ul>
          <p className="form-note">These guides provide general education. Dennis can help apply the rules to a documented scenario for a Greater Orlando or Florida property.</p>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <SectionHeading eyebrow="Your VA questions" title="Frequently asked questions" />
          <div className="va-faq-list">{page.faqs.map(([question, answer]) => <details className="faq-item" key={question}><summary><strong>{question}</strong><i aria-hidden="true" /></summary><div className="va-faq-answer"><p>{answer}</p></div></details>)}</div>
        </div>
      </section>

      <section className="final-cta">
        <div className="shell final-cta-inner">
          <div><Eyebrow>Your next move</Eyebrow><h2>Ready for the next step?</h2><p>{page.cta_text}</p></div>
          <div className="final-cta-actions">
            <a className="button button-gold" href="#request-review">Request a review</a>
            <a className="button button-outline-light" href="tel:+18503468514">Call Dennis</a>
            <a className="va-secure-link" href={secureApplicationUrl}>Open the secure mortgage application <span aria-hidden="true">→</span></a>
          </div>
        </div>
      </section>
    </PageShell>
  );
}
