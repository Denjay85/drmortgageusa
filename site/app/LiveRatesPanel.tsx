"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import RateWatchMini from "./RateWatchMini";

type RateItem = { label: string; rate: string; href: string };

const fallbackRates: RateItem[] = [
  { label: "Conventional 30-year", rate: "6.65%", href: "/tools#purchase" },
  { label: "Conventional 15-year", rate: "6.20%", href: "/tools#purchase" },
  { label: "FHA 30-year", rate: "6.23%", href: "/tools#fha" },
  { label: "VA 30-year", rate: "6.25%", href: "/tools#va-purchase" },
  { label: "USDA 30-year", rate: "6.18%", href: "/tools#purchase" },
  { label: "Jumbo 30-year", rate: "6.82%", href: "/tools#purchase" },
];

export default function LiveRatesPanel() {
  const [rates, setRates] = useState(fallbackRates);
  const [reviewed, setReviewed] = useState("July 10, 2026");

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/rates", { signal: controller.signal })
      .then((response) => response.json() as Promise<{ rates?: Record<string, string>; reviewed?: string }>)
      .then((payload) => {
        if (!payload.rates) return;
        setRates((current) => current.map((item) => ({
          ...item,
          rate: payload.rates?.[item.label] || item.rate,
        })));
        if (payload.reviewed) setReviewed(payload.reviewed);
      })
      .catch(() => undefined);
    return () => controller.abort();
  }, []);

  return (
    <div className="hero-rates-panel anchor-target" id="rates">
      <div className="hero-rates-heading">
        <div>
          <p className="hero-rates-title">Today&apos;s mortgage rate ranges</p>
          <span>A quick market snapshot · reviewed {reviewed}</span>
        </div>
        <div className="hero-rates-actions">
          <Link className="hero-actual-rate" href="/contact">
            Check a rate for my situation <span aria-hidden="true">→</span>
          </Link>
          <RateWatchMini />
        </div>
      </div>
      <div className="hero-rate-grid" aria-label="Illustrative mortgage rate ranges">
        {rates.map((item) => (
          <Link href={item.href} key={item.label}>
            <span>{item.label}</span>
            <strong>{item.rate}</strong>
            <small>See the payment <b aria-hidden="true">→</b></small>
          </Link>
        ))}
      </div>
      <p className="hero-rates-disclosure">
        Sample ranges only. These are not live pricing, a rate quote, APR, or an offer to lend.
        Your rate depends on credit, loan program, property, down payment, points, and market conditions.
      </p>
    </div>
  );
}
