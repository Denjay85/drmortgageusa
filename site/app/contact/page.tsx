import type { Metadata } from "next";
import Link from "next/link";
import { PageHero, PageShell, secureApplicationUrl } from "../site-components";
import ContactForm from "./ContactForm";

export const metadata: Metadata = {
  title: "Contact Dennis Ross",
  alternates: { canonical: "/contact" },
  description: "Request a mortgage conversation with Dennis Ross or continue to the secure application.",
};

export default function ContactPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Talk with Dennis"
        title="Tell me what you are trying to figure out."
        body="Use this short form for a general mortgage question or planning conversation. Please keep Social Security numbers, bank details, and other sensitive information inside the secure application."
      />
      <section className="section">
        <div className="shell contact-grid">
          <ContactForm />
          <aside className="contact-aside">
            <p className="eyebrow">Choose what feels easiest</p>
            <h2>Call, organize the basics, or go straight to the application.</h2>
            <div className="contact-option"><span>Call</span><strong><a href="tel:+18503468514">850-346-8514</a></strong><p>Best when the question is easier to explain than type.</p></div>
            <div className="contact-option"><span>Build a plan</span><strong><Link href="/get-started">60-second path finder</Link></strong><p>Best when you want to organize the basics before talking.</p></div>
            <div className="contact-option"><span>Apply securely</span><strong><a href={secureApplicationUrl}>Open the application</a></strong><p>Best when you are ready to provide income, assets, employment, and credit information.</p></div>
          </aside>
        </div>
      </section>
    </PageShell>
  );
}
