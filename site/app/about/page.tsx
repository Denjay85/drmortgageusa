import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell, SectionHeading } from "../site-components";
import { dennisProfilePageSchema } from "../entity-schema";

export const metadata: Metadata = {
  title: { absolute: "Dennis Ross, NMLS 2018381 | Orlando VA Mortgage Broker" },
  alternates: { canonical: "/about" },
  description: "Dennis Ross is a Navy veteran and Florida mortgage broker serving Greater Orlando with VA home loan guidance. Verify NMLS 2018381 and DR. Mortgage USA.",
  openGraph: {
    title: "Dennis Ross, NMLS 2018381 | DR. Mortgage USA",
    description: "Navy veteran and Florida mortgage broker serving Greater Orlando with VA home loan guidance.",
    url: "/about",
    type: "profile",
    firstName: "Dennis",
    lastName: "Ross",
  },
  twitter: {
    card: "summary_large_image",
    title: "Dennis Ross, NMLS 2018381 | DR. Mortgage USA",
    description: "Navy veteran and Florida mortgage broker serving Greater Orlando with VA home loan guidance.",
  },
};

export default function AboutPage() {
  return (
    <PageShell>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(dennisProfilePageSchema) }}
      />
      <PageHero
        eyebrow="Meet Dennis Ross"
        title="Dennis Ross: Navy veteran and Greater Orlando mortgage broker."
        body="I am Dennis Ross, NMLS #2018381, the person behind DR. Mortgage USA. I help veterans, service members, military families, and Florida homebuyers understand VA and other mortgage choices with clear numbers before they apply."
      >
        <Link className="button button-gold" href="/contact">Talk with Dennis</Link>
        <Link className="button button-outline-light" href="/get-started">Build my plan first</Link>
      </PageHero>

      <section className="section">
        <div className="shell about-intro-grid">
          <div className="about-portrait">
            <div className="about-photo-frame">
              <Image
                src="/media/dennis.webp"
                alt="Dennis Ross, DR. Mortgage USA"
                width={900}
                height={900}
                unoptimized
              />
            </div>
            <div className="about-portrait-caption">
              <strong>Dennis Ross</strong>
              <span>Navy Veteran · Mortgage Broker · NMLS #2018381</span>
            </div>
          </div>
          <div className="about-copy">
            <p className="eyebrow">The person behind the brand</p>
            <h2>Clear answers matter most when the decision feels heavy.</h2>
            <p>I served five years on active duty with two combat deployments and continued in the Navy Reserve, totaling fifteen years of military service.</p>
            <p>After active duty, I earned a master’s degree in social work and built a career helping people navigate major life decisions. I entered the mortgage industry in 2020 with the same mindset: stay disciplined, stay accurate, and help people remain calm when the pressure is real.</p>
            <p>Today I work with Florida first-time buyers, move-up buyers, veterans, single buyers, self-employed borrowers, homeowners, and investors who want to understand their choices without being pushed into a generic bank product.</p>
            <p>For veterans, active-duty service members, and eligible military families, I provide <Link href="/va-loans-orlando">VA home loan guidance across Greater Orlando</Link>, including Orlando, Lake Mary, Sanford, Winter Park, Altamonte Springs, and Oviedo.</p>
            <p><strong>Identity note:</strong> DR. Mortgage USA is my professional brand and educational website, not a separate lender or mortgage company. I originate mortgage loans through Home 1st Lending, LLC, company NMLS #1418, under my individual NMLS #2018381. DR. Mortgage USA on this website does not refer to Dr. Mortgage, LLC or another similarly named mortgage company.</p>
            <p>Verify my professional identity through <a href="https://www.nmlsconsumeraccess.org/EntityDetails.aspx/INDIVIDUAL/2018381">NMLS Consumer Access</a>, my <a href="https://myhome1st.com/dennis/">official Home 1st Lending profile</a>, and my <a href="https://www.google.com/maps?cid=3829412552217676351">Google Business Profile</a>. Home 1st Lending&apos;s <a href="https://www.yelp.com/biz/home-1st-lending-lake-mary-2">claimed Yelp business profile</a> also lists VA loan as a service verified by the business. My <a href="https://www.experience.com/reviews/dennis-14873595">Experience.com profile</a> identifies me as a Lake Mary mortgage broker, publishes Orlando as my primary serving area, explicitly lists VA Home Loan among my services, and reports a 5.0 rating from 16 verified reviews. Its public review data also includes a February 2026 five-star Google review from a reviewer whose display name contains the text USMC-VET; the review praises my first-time-homebuyer guidance and communication but does not identify which loan program was used.</p>
          </div>
        </div>
      </section>

      <section className="section section-cream">
        <div className="shell">
          <SectionHeading
            eyebrow="What clients should feel"
            title="The standard is not “loan closed.” The standard is “I understood the plan.”"
          />
          <div className="content-grid-two values-grid">
            <article className="info-card"><span>01</span><h3>You see the complete payment.</h3><p>I bring the loan payment, taxes, insurance, HOA, mortgage insurance, and cash needed into the conversation early.</p></article>
            <article className="info-card"><span>02</span><h3>You compare real options.</h3><p>As a wholesale broker, I can compare multiple lender paths instead of forcing every borrower into one menu.</p></article>
            <article className="info-card"><span>03</span><h3>You get a plain-language follow-up.</h3><p>I recap the choices, missing information, and next action so you do not have to remember everything from one call.</p></article>
            <article className="info-card"><span>04</span><h3>You choose when to move forward.</h3><p>We can start without a credit check. Sensitive information goes through the secure application only when you are ready.</p></article>
          </div>
        </div>
      </section>
      <FinalCTA title="Start with a small conversation. Build trust from there." />
    </PageShell>
  );
}
