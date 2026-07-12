import type { Metadata } from "next";
import Link from "next/link";
import { PageHero, PageShell } from "../site-components";

export const metadata: Metadata = {
  title: "Policies and Disclosures",
  alternates: { canonical: "/legal" },
  description: "Privacy, terms, communications, accessibility, licensing, and mortgage disclosures for DR. Mortgage USA.",
};

export default function LegalPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Policies & disclosures"
        title="The important information should be easy to find."
        body="Review the website terms, communications terms, accessibility commitment, licensing information, and the current privacy policy."
      />
      <section className="section">
        <div className="shell legal-content">
          <section id="privacy">
            <p className="eyebrow">Privacy</p>
            <h2>Privacy Policy</h2>
            <p>The privacy policy explains the contact and loan inquiry information collected through the site, how it is used, service-provider sharing, advertising measurement, cookies, retention, consumer choices, and contact procedures.</p>
            <p><Link className="text-link" href="/privacy">Read the current Privacy Policy <span>→</span></Link></p>
          </section>
          <section id="terms">
            <p className="eyebrow">Website use</p>
            <h2>Terms of Use</h2>
            <p>This website provides general educational information and planning estimates. It does not provide a loan approval, prequalification, commitment to lend, rate lock, legal advice, tax advice, or financial advice. Programs, rates, fees, guidelines, and availability may change. External sites are governed by their own terms and privacy practices.</p>
          </section>
          <section id="sms">
            <p className="eyebrow">Communications</p>
            <h2>Call and SMS Terms</h2>
            <p>When you separately opt in to calls or text messages, message frequency may vary and message or data rates may apply. Reply STOP to opt out of texts and HELP for help. Communications consent is not a condition of obtaining services. Email, call, and text preferences are recorded separately when the form provides those choices.</p>
          </section>
          <section id="accessibility">
            <p className="eyebrow">Inclusive access</p>
            <h2>Accessibility Statement</h2>
            <p>DR. Mortgage USA intends for the website to be usable with keyboards, screen readers, text scaling, reduced motion, and common assistive technologies. To report a barrier or request information in another format, call 850-346-8514 or email dennis@drmortgageusa.com.</p>
          </section>
          <section id="licensing">
            <p className="eyebrow">Licensing & mortgage disclosures</p>
            <h2>Licensing and Disclosures</h2>
            <p>Dennis Ross, Mortgage Loan Originator, NMLS #2018381. Licensed in Florida. Powered by Home 1st Lending, LLC, NMLS #1418. Equal Housing Opportunity.</p>
            <p>All loans are subject to credit and property approval. Not all applicants will qualify. Programs, interest rates, fees, pricing, and availability are subject to change without notice. Calculator and rate examples are educational estimates and are not an offer, approval, prequalification, commitment to lend, or rate lock.</p>
            <p><a className="text-link" href="https://www.nmlsconsumeraccess.org/EntityDetails.aspx/COMPANY/1418">View Home 1st Lending in NMLS Consumer Access <span>→</span></a></p>
          </section>
        </div>
      </section>
    </PageShell>
  );
}
