"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import RateWatchMini from "./RateWatchMini";

type RateItem = { label: string; rate: string; href: string };

const rateLinks = [
  { label: "Conventional 30-year", href: "/tools#purchase" },
  { label: "Conventional 15-year", href: "/tools#purchase" },
  { label: "FHA 30-year", href: "/tools#fha" },
  { label: "VA 30-year", href: "/tools#va-purchase" },
  { label: "Jumbo 30-year", href: "/tools#purchase" },
];

type RatePayload = {
  status?: "verified" | "unavailable";
  verified?: boolean;
  rates?: Record<string, string>;
  asOf?: string;
  source?: { name?: string; url?: string };
};

export default function LiveRatesPanel() {
  const [rates, setRates] = useState<RateItem[]>([]);
  const [asOf, setAsOf] = useState("");
  const [status, setStatus] = useState<"loading" | "verified" | "unavailable">("loading");
  const [sourceUrl, setSourceUrl] = useState("https://www.mortgagenewsdaily.com/mortgage-rates");

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/rates?source=mnd-daily-v2", {
      signal: controller.signal,
      cache: "no-store",
    })
      .then((response) => {
        if (!response.ok) throw new Error("Rate source request failed");
        return response.json() as Promise<RatePayload>;
      })
      .then((payload) => {
        if (!payload.verified || payload.status !== "verified" || !payload.rates || !payload.asOf) {
          setStatus("unavailable");
          return;
        }
        const verifiedRates = rateLinks.flatMap((item) => {
          const rate = payload.rates?.[item.label];
          return rate ? [{ ...item, rate }] : [];
        });
        if (verifiedRates.length !== rateLinks.length) {
          setStatus("unavailable");
          return;
        }
        setRates(verifiedRates);
        setAsOf(payload.asOf);
        if (payload.source?.url) setSourceUrl(payload.source.url);
        setStatus("verified");
      })
      .catch(() => setStatus("unavailable"));
    return () => controller.abort();
  }, []);

  return (
    <div className="hero-rates-panel anchor-target" id="rates">
      <div className="hero-rates-heading">
        <div>
          <p className="hero-rates-title">Today&apos;s national mortgage rate index</p>
          {status === "verified" ? (
            <span>
              <a href={sourceUrl} target="_blank" rel="noopener noreferrer">Mortgage News Daily</a>
              {" · as of "}{asOf}
            </span>
          ) : status === "loading" ? (
            <span>Checking Mortgage News Daily...</span>
          ) : (
            <span>Current MND index temporarily unavailable</span>
          )}
        </div>
        <div className="hero-rates-actions">
          <Link className="hero-actual-rate" href="/contact">
            Check a rate for my situation <span aria-hidden="true">→</span>
          </Link>
          <RateWatchMini />
        </div>
      </div>
      {status === "verified" ? (
        <div className="hero-rate-grid" aria-label="Mortgage News Daily national rate index">
          {rates.map((item) => (
            <Link href={item.href} key={item.label}>
              <span>{item.label}</span>
              <strong>{item.rate}</strong>
              <small>Model a payment <b aria-hidden="true">→</b></small>
            </Link>
          ))}
        </div>
      ) : (
        <div className={`hero-rate-status hero-rate-status-${status}`} role="status">
          <strong>{status === "loading" ? "Verifying today's index" : "We will not guess at today's rates"}</strong>
          <span>
            {status === "loading"
              ? "Checking the dated daily index before showing any numbers."
              : "Mortgage News Daily is not returning a complete, current index right now. Ask Dennis for pricing based on your situation."}
          </span>
        </div>
      )}
      <p className="hero-rates-disclosure">
        National daily index data from Mortgage News Daily. This is not DR. Mortgage USA pricing,
        a rate quote, APR, or an offer to lend. Your available rate depends on credit, loan program,
        property, down payment, points, and current market conditions.
      </p>
    </div>
  );
}
