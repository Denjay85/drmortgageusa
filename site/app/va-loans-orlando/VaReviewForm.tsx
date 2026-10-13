"use client";

import { useEffect, useRef, useState } from "react";
import { submitLead } from "../lead-client";

export default function VaReviewForm({ heading, description }: { heading: string; description: string }) {
  const pending = useRef(false);
  const success = useRef<HTMLDivElement>(null);
  const [sent, setSent] = useState(false);
  const [preview, setPreview] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (sent) success.current?.focus();
  }, [sent]);

  return (
    <div className="form-card va-review-card anchor-target" id="request-review" tabIndex={-1} aria-labelledby="review-heading">
      <p className="eyebrow">Start with a conversation</p>
      <h2 id="review-heading">{heading}</h2>
      <p className="va-form-intro">{description}</p>
      {sent ? (
        <div className="success-message contact-success" role="status" tabIndex={-1} ref={success}>
          <strong>{preview ? "Preview test complete." : "Your request was received."}</strong>
          <span>{preview ? "No lead was saved or sent." : "Dennis will follow up using the contact preferences you selected."}</span>
          <a className="button button-navy" href="tel:+18503468514">Call Dennis</a>
        </div>
      ) : (
        <form method="post" action="/request-review" aria-label="Orlando VA loan review" aria-busy={submitting} onSubmit={async (event) => {
          event.preventDefault();
          if (pending.current) return;
          pending.current = true;
          setSubmitting(true);
          setError("");
          const form = new FormData(event.currentTarget);
          try {
            const result = await submitLead({
              firstName: String(form.get("firstName") || ""),
              email: String(form.get("email") || ""),
              phone: String(form.get("phone") || ""),
              timeline: String(form.get("timeline") || ""),
              source: "service-page-va-loans-orlando",
              segment: "veteran",
              emailConsent: form.get("emailConsent") === "on",
              callConsent: form.get("callConsent") === "on",
              smsConsent: form.get("smsConsent") === "on",
            });
            setPreview(result.preview === true);
            setSent(true);
          } catch (caught) {
            setError(caught instanceof Error ? caught.message : "We could not confirm delivery. Please call 850-346-8514.");
          } finally {
            pending.current = false;
            setSubmitting(false);
          }
        }}>
          <div className="field-grid">
            <label className="field"><span>First name</span><input type="text" name="firstName" autoComplete="given-name" required /></label>
            <label className="field"><span>Email</span><input type="email" name="email" autoComplete="email" required /></label>
          </div>
          <div className="field-grid">
            <label className="field"><span>Phone <small>(optional)</small></span><input type="tel" name="phone" autoComplete="tel" /></label>
            <label className="field"><span>Timeline <small>(optional)</small></span><select name="timeline" defaultValue="">
              <option value="">Select a timeline</option>
              <option value="asap">ASAP</option>
              <option value="0-30">Within 30 days</option>
              <option value="1-3 months">1-3 months</option>
              <option value="3-6 months">3-6 months</option>
              <option value="6+ months">6+ months</option>
            </select></label>
          </div>
          <input type="hidden" name="source" value="service-page-va-loans-orlando" />
          <input type="hidden" name="segment" value="veteran" />
          <label className="checkbox-field"><input type="checkbox" name="emailConsent" required /><span>I agree to receive a reply by email about this request and acknowledge the <a href="/privacy">Privacy Policy</a>.</span></label>
          <label className="checkbox-field"><input type="checkbox" name="callConsent" /><span>Optional: Dennis may call me about this request.</span></label>
          <label className="checkbox-field"><input type="checkbox" name="smsConsent" /><span>Optional: Dennis may text me about this request. Message and data rates may apply. Reply STOP to opt out.</span></label>
          {error ? <p className="form-error" role="alert">{error}</p> : null}
          <button className="button button-gold" type="submit" disabled={submitting}>{submitting ? "Sending..." : "Request my VA review"}</button>
          <p className="form-note">This requests a conversation, not a loan approval or completed application. Consent is not a condition of obtaining services. You can also <a href="tel:+18503468514">call 850-346-8514</a>.</p>
        </form>
      )}
    </div>
  );
}
