import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell, SectionHeading } from "../site-components";

export const metadata: Metadata = {
  title: "Meet Dennis Ross",
  description: "Meet Dennis Ross, Navy veteran, Florida mortgage broker, and the person behind DR. Mortgage USA.",
};

export default function AboutPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Meet Dennis Ross"
        title="Mortgage guidance shaped by service, social work, and calm under pressure."
        body="Dennis is a Navy veteran and Florida mortgage broker who helps people understand the decision instead of simply completing the paperwork."
      >
        <Link className="button button-gold" href="/contact">Talk with Dennis</Link>
        <Link className="button button-outline-light" href="/get-started">Build my plan first</Link>
      </PageHero>

      <section className="section">
        <div className="shell about-intro-grid">
          <div className="about-portrait">
            <div className="about-photo-frame">
              <img src="/media/dennis.webp" alt="Dennis Ross, DR. Mortgage USA" width="900" height="900" />
            </div>
            <div className="about-portrait-caption">
              <strong>Dennis Ross</strong>
              <span>Navy Veteran · Mortgage Broker · NMLS #2018381</span>
            </div>
          </div>
          <div className="about-copy">
            <p className="eyebrow">The person behind the brand</p>
            <h2>Clear answers matter most when the decision feels heavy.</h2>
            <p>Dennis served five years on active duty with two combat deployments and continues to serve in the Navy Reserve, totaling fifteen years of military service.</p>
            <p>After active duty, he earned a master’s degree in social work and built a career helping people navigate major life decisions. He entered the mortgage industry in 2020 with the same mindset: stay disciplined, stay accurate, and help people remain calm when the pressure is real.</p>
            <p>Today his focus is Florida first-time buyers, veterans, single buyers, self-employed borrowers, and investors who want to understand their choices without being pushed into a generic bank product.</p>
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
            <article className="info-card"><span>01</span><h3>You see the complete payment.</h3><p>Principal, interest, taxes, insurance, HOA, mortgage insurance, and cash-to-close assumptions are discussed early.</p></article>
            <article className="info-card"><span>02</span><h3>You compare real options.</h3><p>As a wholesale broker, Dennis can compare multiple lender paths instead of forcing every file into one menu.</p></article>
            <article className="info-card"><span>03</span><h3>You get plain-language follow-up.</h3><p>The conversation becomes a clear recap with decisions, missing information, and the next action.</p></article>
            <article className="info-card"><span>04</span><h3>You choose when to move forward.</h3><p>Education can start without a credit check. Sensitive information moves only through the secure application when you are ready.</p></article>
          </div>
        </div>
      </section>
      <FinalCTA title="Start with a small conversation. Build trust from there." />
    </PageShell>
  );
}
