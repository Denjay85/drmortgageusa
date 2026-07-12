"use client";

import { useState } from "react";
import { submitLead } from "./lead-client";

export default function RateWatchMini() {
  const [saved, setSaved] = useState(false);
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
              <strong>Your Rate Watch request was sent.</strong>
              <p>Dennis can review the threshold you selected and follow up with current pricing context.</p>
            </div>
          </div>
        ) : (
          <form
            onSubmit={async (event) => {
              event.preventDefault();
              setSubmitting(true);
              setError("");
              const form = new FormData(event.currentTarget);
              try {
                await submitLead({
                  email: String(form.get("email") || ""),
                  segment: "Mortgage rate watch",
                  threshold: String(form.get("threshold") || ""),
                  emailConsent: true,
                  source: "redesign-rate-watch",
                });
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
              <input type="email" name="email" placeholder="you@example.com" required />
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
