"use client";

import { useState } from "react";
import { submitLead } from "./lead-client";

export default function RateWatchMini() {
  const [saved, setSaved] = useState(false);
  const [preview, setPreview] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  return (
    <details className="hero-rate-watch">
      <summary>Create Rate Watch</summary>
      <div className="hero-rate-watch-popover">
        {saved ? (
          <div className="hero-rate-watch-success" role="status">
            <span aria-hidden="true">✓</span>
            <div>
              <strong>{preview ? "Preview test complete." : "Your Rate Watch request was received."}</strong>
              <p>{preview ? "No lead was saved or sent." : "Dennis can review the threshold you selected and follow up with current pricing context."}</p>
            </div>
          </div>
        ) : (
          <form
            onSubmit={async (event) => {
              event.preventDefault();
              if (submitting) return;
              setSubmitting(true);
              setError("");
              const form = new FormData(event.currentTarget);
              try {
                const result = await submitLead({
                  email: String(form.get("email") || ""),
                  segment: "Mortgage rate watch",
                  threshold: String(form.get("threshold") || ""),
                  emailConsent: form.get("emailConsent") === "on",
                  source: "redesign-rate-watch",
                });
                setPreview(result.preview === true);
                setSaved(true);
              } catch (caught) {
                setError(caught instanceof Error ? caught.message : "The request could not be submitted.");
              } finally {
                setSubmitting(false);
              }
            }}
          >
            <div>
              <strong>What rate would get your attention?</strong>
              <p>Choose a threshold and Dennis can follow up with current pricing context.</p>
            </div>
            <label>
              <span>Email address</span>
              <input type="email" name="email" autoComplete="email" placeholder="you@example.com" required />
            </label>
            <label>
              <span>Notify me when</span>
              <select name="threshold" defaultValue="6.00% or lower">
                <option>6.25% or lower</option>
                <option>6.00% or lower</option>
                <option>5.75% or lower</option>
                <option>5.50% or lower</option>
              </select>
            </label>
            <label className="checkbox-field"><input type="checkbox" name="emailConsent" required /><span>Email me about this rate-watch request. I acknowledge the <a href="/privacy">Privacy Policy</a>.</span></label>
            {error ? <small className="form-error" role="alert">{error}</small> : null}
            <button className="button button-gold button-small" type="submit" disabled={submitting}>
              {submitting ? "Sending..." : "Create my alert"}
            </button>
            <small>Educational rate monitoring only. This is not a rate quote or lock.</small>
          </form>
        )}
      </div>
    </details>
  );
}
