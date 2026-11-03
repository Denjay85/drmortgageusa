"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  dpaRateSource,
  type DpaRateSnapshot,
} from "./dpa-rate-data";

export default function DpaRateTracker() {
  const [snapshot, setSnapshot] = useState<DpaRateSnapshot | null>(null);
  const [activeId, setActiveId] = useState("standard-bond");
  const [live, setLive] = useState(false);
  const [loading, setLoading] = useState(true);
  const [syncedAt, setSyncedAt] = useState<string | null>(null);
  const active = snapshot?.groups.find((group) => group.id === activeId) || snapshot?.groups[0];

  useEffect(() => {
    const controller = new AbortController();
    let mounted = true;

    let timer: ReturnType<typeof setTimeout>;
    async function refresh() {
      let delay = 300_000;
      try {
        const response = await fetch("/api/dpa-rates", { signal: controller.signal, cache: "no-store" });
        if (!response.ok) throw new Error("Rate source unavailable");
        const payload = await response.json() as { snapshot?: DpaRateSnapshot; live?: boolean; stale?: boolean; refreshing?: boolean; syncedAt?: string };
        if (!mounted) return;
        const date = Date.parse(payload.snapshot?.asOf || "");
        const expired = !Number.isFinite(date) || Date.now() - date > 5 * 86_400_000;
        setSnapshot(!payload.stale && !expired && payload.snapshot?.groups.length ? payload.snapshot : null);
        setLive(Boolean(payload.live));
        setSyncedAt(payload.syncedAt || null);
        if (payload.refreshing) delay = 5_000;
      } catch {
        if (mounted) {
          setLive(false);
          setSnapshot(null);
        }
        delay = 60_000;
      } finally {
        if (mounted) {
          setLoading(false);
          timer = setTimeout(refresh, delay);
        }
      }
    }
    void refresh();

    return () => {
      mounted = false;
      controller.abort();
      clearTimeout(timer);
    };
  }, []);

  return (
    <div className="dpa-rate-board" data-interaction="dpa-rate-board">
      <div className="dpa-rate-board-heading">
        <div>
          <p className="eyebrow">Florida program rate sheet</p>
          <h2>Compare Florida&apos;s latest verified assistance program rates.</h2>
          <p>The assistance gets the attention, but the first-mortgage rate affects the payment. Click through the programs, then let me help you compare the full cost.</p>
        </div>
        <div className="dpa-rate-source-status">
          <span className={live ? "is-live" : ""} aria-hidden="true" />
          <div>
            <strong>{loading ? "Checking the official rate sheet" : live ? "Official source verified" : snapshot ? "Last verified sheet; refresh pending" : "Current rates temporarily unavailable"}</strong>
            {snapshot ? <small>Rate sheet dated {snapshot.asOf}</small> : <small>Check the official source or contact Dennis for current pricing.</small>}
            {syncedAt && snapshot ? <small>Checked {new Date(syncedAt).toLocaleString("en-US", { timeZone: "America/New_York", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })} ET</small> : null}
          </div>
        </div>
      </div>

      {snapshot && active ? <>
      <div className="dpa-rate-layout">
        <div className="dpa-rate-tabs" role="tablist" aria-label="Choose a DPA rate program">
          {snapshot.groups.map((group, index) => (
            <button
              type="button"
              role="tab"
              aria-selected={active.id === group.id}
              aria-controls="dpa-rate-panel"
              className={active.id === group.id ? "active" : ""}
              onClick={() => setActiveId(group.id)}
              key={group.id}
            >
              <span>0{index + 1}</span>
              <strong>{group.label}</strong>
              <i aria-hidden="true">→</i>
            </button>
          ))}
        </div>

        <div className="dpa-rate-panel" id="dpa-rate-panel" role="tabpanel" key={active.id}>
          <div className="dpa-rate-panel-top">
            <div>
              <p className="eyebrow">{active.label}</p>
              <h3>{active.assistance}</h3>
            </div>
            <div className="dpa-rate-program-meta">
              <span>{active.fico}</span>
              {active.status ? <strong>{active.status}</strong> : <strong>Posted {snapshot.asOf}</strong>}
            </div>
          </div>

          <div className="dpa-rate-entry-grid">
            {active.entries.map((entry, index) => (
              <article key={`${entry.label}-${entry.detail || index}`}>
                <div>
                  <span>{entry.label}</span>
                  {entry.detail ? <small>{entry.detail}</small> : null}
                </div>
                <strong>{entry.rate}</strong>
              </article>
            ))}
          </div>

          <div className="dpa-rate-actions">
            <Link className="button button-gold button-small" href="#dpa-check">Have Dennis check my options</Link>
            <a className="button button-outline-light button-small" href={dpaRateSource}>Open official rate source</a>
          </div>
        </div>
      </div>

      {snapshot.heroesFunding ? (
        <div className="dpa-rate-notice dpa-heroes-funding" role="status">
          <strong>Hometown Heroes funding</strong>
          <span>{snapshot.heroesFunding}</span>
        </div>
      ) : null}

      <div className="dpa-rate-notice">
        <strong>Rate-sheet program note</strong>
        <span>{snapshot.notice}</span>
      </div>
      </> : <div className="dpa-rate-notice" role="status">
        <strong>{loading ? "Loading verified rates" : "Please confirm current rates"}</strong>
        <a href={dpaRateSource}>View the official Florida Housing rate sheet</a>
      </div>}
      <p className="dpa-rate-disclosure">
        Program lock rates are not ordinary retail rate quotes and do not guarantee eligibility, approval, funds, or a lock. Rates may change during the day. Income, purchase price, property, first-time-buyer rules, loan type, participating lender requirements, and available funding still apply. County programs may not publish one daily first-mortgage rate.
      </p>
    </div>
  );
}
