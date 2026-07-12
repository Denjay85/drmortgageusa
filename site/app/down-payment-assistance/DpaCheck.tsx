"use client";

import { useState } from "react";
import { submitLead } from "../lead-client";

export default function DpaCheck() {
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  if (submitted) {
    return (
      <div className="success-message" role="status">
        <strong>Your DPA starting factors were sent.</strong>
        <span>Dennis can now review the county, ownership, income, and household details against current program rules.</span>
        <button className="button button-navy" type="button" onClick={() => setSubmitted(false)}>Review another scenario</button>
      </div>
    );
  }

  return (
    <form className="dpa-check-form" onSubmit={async (event) => {
      event.preventDefault();
      setSubmitting(true);
      setError("");
      const form = new FormData(event.currentTarget);
      try {
        await submitLead({
          firstName: String(form.get("firstName") || ""),
          email: String(form.get("email") || ""),
          phone: String(form.get("phone") || ""),
          segment: "Down payment assistance review",
          county: String(form.get("county") || ""),
          recentOwnership: String(form.get("recentOwnership") || ""),
          householdIncome: String(form.get("householdIncome") || ""),
          householdSize: String(form.get("householdSize") || ""),
          message: String(form.get("message") || ""),
          emailConsent: form.get("emailConsent") === "on",
          callConsent: form.get("callConsent") === "on",
          smsConsent: form.get("smsConsent") === "on",
          source: "redesign-dpa-review",
        });
        setSubmitted(true);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "The request could not be submitted.");
      } finally {
        setSubmitting(false);
      }
    }}>
      <div className="field-grid">
        <label className="field">
          <span>Where are you planning to buy?</span>
          <select name="county" required defaultValue="">
            <option value="" disabled>Select a county</option>
            <option>Orange County</option>
            <option>Osceola County</option>
            <option>Seminole County</option>
            <option>Lake County</option>
            <option>Another Florida county</option>
            <option>Not sure yet</option>
          </select>
        </label>
        <label className="field">
          <span>Have you owned a home in the last three years?</span>
          <select name="recentOwnership" required defaultValue="">
            <option value="" disabled>Select one</option>
            <option>No</option>
            <option>Yes</option>
            <option>Not sure</option>
          </select>
        </label>
        <label className="field">
          <span>Approximate household income</span>
          <select name="householdIncome" required defaultValue="">
            <option value="" disabled>Select a range</option>
            <option>Under $60,000</option>
            <option>$60,000–$90,000</option>
            <option>$90,000–$120,000</option>
            <option>$120,000–$150,000</option>
            <option>Over $150,000</option>
            <option>Not sure</option>
          </select>
        </label>
        <label className="field">
          <span>Household size</span>
          <select name="householdSize" required defaultValue="">
            <option value="" disabled>Select one</option>
            <option>1</option><option>2</option><option>3</option><option>4</option><option>5+</option>
          </select>
        </label>
      </div>
      <label className="field">
        <span>Anything important about the scenario?</span>
        <textarea name="message" placeholder="Veteran status, occupation, target timing, available savings, or a program you heard about..." />
      </label>
      <div className="field-grid">
        <label className="field"><span>First name</span><input name="firstName" type="text" autoComplete="given-name" required /></label>
        <label className="field"><span>Email</span><input name="email" type="email" autoComplete="email" required /></label>
      </div>
      <label className="field"><span>Phone <small>(optional)</small></span><input name="phone" type="tel" autoComplete="tel" /></label>
      <label className="checkbox-field"><input type="checkbox" name="emailConsent" required /><span>Email my DPA review and allow Dennis to reply by email. I acknowledge the Privacy Policy.</span></label>
      <label className="checkbox-field"><input type="checkbox" name="callConsent" /><span>Optional: Dennis may call me about this request.</span></label>
      <label className="checkbox-field"><input type="checkbox" name="smsConsent" /><span>Optional: Dennis may text me about this request. Message and data rates may apply. Reply STOP to opt out.</span></label>
      {error ? <p className="form-error" role="alert">{error} You can also call 850-346-8514.</p> : null}
      <button className="button button-gold" type="submit" disabled={submitting}>{submitting ? "Sending..." : "Send my DPA starting factors"}</button>
      <p className="form-note">This is an educational starting review, not a commitment to lend or a determination of eligibility. Consent is not a condition of obtaining services.</p>
    </form>
  );
}
