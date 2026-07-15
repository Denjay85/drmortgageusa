"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  dpaRateSource,
  fallbackDpaRateSnapshot,
  type DpaRateSnapshot,
} from "./dpa-rate-data";

export default function DpaRateTracker() {
  const [snapshot, setSnapshot] = useState<DpaRateSnapshot>(fallbackDpaRateSnapshot);
  const [activeId, setActiveId] = useState(fallbackDpaRateSnapshot.groups[0].id);
  const [live, setLive] = useState(false);
  const active = snapshot.groups.find((group) => group.id === activeId) || snapshot.groups[0];

  useEffect(() => {
    const controller = new AbortController();
    let mounted = true;

    fetch("/api/dpa-rates", { signal: controller.signal })
      .then((response) => response.json() as Promise<{ snapshot?: DpaRateSnapshot; live?: boolean }>)
      .then((payload) => {
        if (!mounted || !payload.snapshot?.groups.length) return;
        setSnapshot(payload.snapshot);
        setLive(Boolean(payload.live));
      })
      .catch(() => undefined);

    return () => {
      mounted = false;
      controller.abort();
    };
  }, []);

  return (
    <div className="dpa-rate-board" data-interaction="dpa-rate-board">
      <div className="dpa-rate-board-heading">
        <div>
          <p className="eyebrow">Daily program pricing</p>
          <h2>Today&apos;s Florida Housing DPA rate snapshot.</h2>
          <p>Compare the first-mortgage lock rates attached to major statewide assistance paths. Then compare the complete payment and assistance terms.</p>
        </div>
        <div className="dpa-rate-source-status">
          <span className={live ? "is-live" : ""} aria-hidden="true" />
          <div>
            <strong>{live ? "Official source connected" : "Last verified snapshot"}</strong>
            <small>Posted {snapshot.asOf}</small>
          </div>
        </div>
      </div>

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
              {active.status ? <strong>{active.status}</strong> : <strong>Currently posted</strong>}
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
            <Link className="button button-gold button-small" href="#dpa-check">Check my DPA starting factors</Link>
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
        <strong>Current program note</strong>
        <span>{snapshot.notice}</span>
      </div>
      <p className="dpa-rate-disclosure">
        Program lock rates are not ordinary retail rate quotes and do not guarantee eligibility, approval, funds, or a lock. Rates may change during the day. Income, purchase price, property, first-time-buyer rules, loan type, participating lender requirements, and available funding still apply. County programs may not publish one daily first-mortgage rate.
      </p>
    </div>
  );
}
