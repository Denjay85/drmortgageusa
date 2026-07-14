"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { faqCategories, faqItems } from "./data";

export default function FaqLibrary() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All questions");

  const filteredItems = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return faqItems.filter((item) => {
      const categoryMatches = category === "All questions" || item.category === category;
      const queryMatches = !normalized || `${item.question} ${item.answer} ${item.category}`.toLowerCase().includes(normalized);
      return categoryMatches && queryMatches;
    });
  }, [category, query]);

  return (
    <div className="faq-library">
      <div className="faq-search-panel">
        <label className="faq-search-field">
          <span>Search mortgage questions</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try credit, VA, closing costs, HELOC…"
          />
        </label>
        <p aria-live="polite">
          <strong>{filteredItems.length}</strong> {filteredItems.length === 1 ? "answer" : "answers"} shown
        </p>
      </div>

      <div className="faq-category-filter" aria-label="Filter FAQ categories">
        {["All questions", ...faqCategories].map((item) => (
          <button
            type="button"
            className={category === item ? "active" : ""}
            aria-pressed={category === item}
            onClick={() => setCategory(item)}
            key={item}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="faq-library-layout">
        <div className="faq-results">
          {filteredItems.length ? filteredItems.map((item) => (
            <details className="faq-item" id={item.id} data-faq-id={item.id} key={item.id}>
              <summary>
                <span>
                  <small>{item.category}</small>
                  <strong>{item.question}</strong>
                </span>
                <i aria-hidden="true" />
              </summary>
              <div className="faq-answer">
                <p>{item.answer}</p>
                {item.links?.length ? (
                  <div className="faq-answer-links">
                    {item.links.map((link) => (
                      <Link href={link.href} key={link.label}>{link.label} <span aria-hidden="true">→</span></Link>
                    ))}
                  </div>
                ) : null}
              </div>
            </details>
          )) : (
            <div className="faq-empty">
              <span>?</span>
              <h2>No matching answer yet.</h2>
              <p>Try a shorter search, choose another category, or send the question directly to Dennis.</p>
              <button type="button" className="button button-navy" onClick={() => { setQuery(""); setCategory("All questions"); }}>
                Clear the search
              </button>
            </div>
          )}
        </div>

        <aside className="faq-help-card">
          <p className="eyebrow">Still unsure?</p>
          <h2>Bring Dennis the question you could not answer here.</h2>
          <p>Keep it high-level. Sensitive financial documents and personal identifiers belong only in the secure application.</p>
          <Link className="button button-gold" href="/contact">Ask Dennis</Link>
          <a className="faq-help-phone" href="tel:+18503468514">850-346-8514</a>
          <div>
            <strong>How these answers are maintained</strong>
            <span>Plain-language education, reviewed July 10, 2026. Actual eligibility, pricing, and documentation depend on the complete file and current guidelines.</span>
          </div>
          <nav aria-label="Official consumer references">
            <a href="https://www.consumerfinance.gov/owning-a-home/">CFPB home-loan resources</a>
            <a href="https://www.hud.gov/hud-partners/single-family-insurance">HUD FHA resources</a>
            <a href="https://www.va.gov/housing-assistance/home-loans/">VA home-loan resources</a>
            <a href="https://www.rd.usda.gov/programs-services/single-family-housing-programs">USDA housing resources</a>
          </nav>
        </aside>
      </div>
    </div>
  );
}
