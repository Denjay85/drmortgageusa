"use client";

import { useState } from "react";
import { submitLead } from "../lead-client";

export default function ContactForm() {
  const [sent, setSent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  if (sent) {
    return (
      <div className="success-message contact-success" role="status">
        <strong>Your request is on its way to Dennis.</strong>
        <span>Your contact preferences and the details you provided were included with the request.</span>
        <button className="button button-navy" type="button" onClick={() => setSent(false)}>View the form again</button>
      </div>
    );
  }

  return (
    <form className="form-card" onSubmit={async (event) => {
      event.preventDefault();
      setSubmitting(true);
      setError("");
      const form = new FormData(event.currentTarget);
      try {
        await submitLead({
          firstName: String(form.get("firstName") || ""),
          lastName: String(form.get("lastName") || ""),
          email: String(form.get("email") || ""),
          phone: String(form.get("phone") || ""),
          segment: String(form.get("topic") || "General mortgage question"),
          message: String(form.get("message") || ""),
          emailConsent: form.get("emailConsent") === "on",
          callConsent: form.get("callConsent") === "on",
          smsConsent: form.get("smsConsent") === "on",
          source: "redesign-contact",
        });
        setSent(true);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "The request could not be submitted.");
      } finally {
        setSubmitting(false);
      }
    }}>
      <div className="field-grid">
        <label className="field"><span>First name</span><input type="text" name="firstName" autoComplete="given-name" required /></label>
        <label className="field"><span>Last name</span><input type="text" name="lastName" autoComplete="family-name" /></label>
      </div>
      <label className="field"><span>Email</span><input type="email" name="email" autoComplete="email" required /></label>
      <label className="field"><span>Phone <small>(optional)</small></span><input type="tel" name="phone" autoComplete="tel" /></label>
      <label className="field"><span>What would you like help with?</span><select name="topic" defaultValue=""><option value="" disabled>Select a topic</option><option>A question not answered in the FAQ</option><option>Buying a home</option><option>VA financing</option><option>Refinance or home equity</option><option>Self-employed or investor financing</option><option>Understanding my next step</option></select></label>
      <label className="field"><span>What should Dennis know?</span><textarea name="message" placeholder="Keep this high level. Do not include SSNs, account numbers, or sensitive documents." /></label>
      <label className="checkbox-field"><input type="checkbox" name="emailConsent" required /><span>I agree to receive a reply by email about this request and acknowledge the Privacy Policy.</span></label>
      <label className="checkbox-field"><input type="checkbox" name="callConsent" /><span>Optional: Dennis may call me about this request. This is separate from email permission.</span></label>
      <label className="checkbox-field"><input type="checkbox" name="smsConsent" /><span>Optional: Dennis may text me about this request. Message and data rates may apply. Reply STOP to opt out.</span></label>
      {error ? <p className="form-error" role="alert">{error} You can also call 850-346-8514.</p> : null}
      <button className="button button-gold" type="submit" disabled={submitting}>{submitting ? "Sending..." : "Request the conversation"}</button>
      <p className="form-note">Consent is not a condition of obtaining services.</p>
    </form>
  );
}
