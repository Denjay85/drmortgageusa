"use client";

import { useEffect, useMemo, useState } from "react";
import { blogPosts, type BlogPost } from "./posts";

const categories = ["All", "Buying", "VA loans", "Self-employed", "Market strategy", "Homeownership"] as const;

function monthLabel(date: string) {
  const parsed = new Date(date);
  return Number.isNaN(parsed.getTime())
    ? date
    : new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric" }).format(parsed);
}

export default function BlogLibrary({ initialPosts = blogPosts }: { initialPosts?: BlogPost[] }) {
  const [posts, setPosts] = useState(initialPosts);
  const [syncStatus, setSyncStatus] = useState<"checking" | "live" | "fallback">("checking");
  const [category, setCategory] = useState<(typeof categories)[number]>("All");
  const [month, setMonth] = useState("All dates");
  const [query, setQuery] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    fetch("/api/blog", { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("Live archive unavailable");
        return response.json() as Promise<{ posts?: BlogPost[] }>;
      })
      .then((payload) => {
        if (!active || !payload.posts?.length) return;
        setPosts(payload.posts);
        setSyncStatus("live");
      })
      .catch((error: unknown) => {
        if (!active || (error instanceof DOMException && error.name === "AbortError")) return;
        setSyncStatus("fallback");
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, []);

  const months = useMemo(() => Array.from(new Set(posts.map((post) => monthLabel(post.date)))), [posts]);

  const visiblePosts = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    const terms = normalized.split(/\s+/).filter(Boolean);
    return posts.filter((post) => {
      const categoryMatch = category === "All" || post.category === category;
      const monthMatch = month === "All dates" || monthLabel(post.date) === month;
      const haystack = `${post.title} ${post.description} ${post.category}`.toLowerCase();
      const words = haystack.split(/[^a-z0-9]+/).filter(Boolean);
      const searchMatch = !terms.length || terms.every((term) =>
        term.length <= 3 ? words.includes(term) : haystack.includes(term)
      );
      return categoryMatch && monthMatch && searchMatch;
    });
  }, [category, month, posts, query]);

  return (
    <>
      <div className="blog-live-bar" aria-live="polite">
        <div>
          <span className={`blog-live-dot ${syncStatus}`} aria-hidden="true" />
          <span>
            <strong>{syncStatus === "live" ? "Live archive connected" : syncStatus === "fallback" ? "Complete archive cached" : "Checking the live archive"}</strong>
            <small>{posts.length} articles available from the current DR. Mortgage USA blog</small>
          </span>
        </div>
        <b>Publishing since February 2026</b>
      </div>

      <div className="blog-controls" aria-label="Filter the blog library">
        <div className="blog-search-row">
          <label className="blog-search">
            <span>Search the library</span>
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Try VA, condo, insurance..."
            />
          </label>
          <label className="blog-month-filter">
            <span>Browse by month</span>
            <select value={month} onChange={(event) => setMonth(event.target.value)}>
              <option>All dates</option>
              {months.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
        </div>
        <div className="blog-filters" aria-label="Blog topics">
          {categories.map((item) => (
            <button
              className={category === item ? "active" : ""}
              key={item}
              type="button"
              aria-pressed={category === item}
              onClick={() => setCategory(item)}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      <p className="blog-result-count" aria-live="polite">
        Showing {visiblePosts.length} of {posts.length} {visiblePosts.length === 1 ? "article" : "articles"}
      </p>

      <div className="blog-grid">
        {visiblePosts.map((post) => (
          <article className="blog-card" key={post.url}>
            <div className="blog-card-meta">
              <span>{post.category}</span>
              <time>{post.date}</time>
            </div>
            <h2>{post.title}</h2>
            <p>{post.description}</p>
            <a className="resource-read" href={post.url}>
              Read the full article <span aria-hidden="true">→</span>
            </a>
          </article>
        ))}
      </div>

      {!visiblePosts.length ? (
        <div className="blog-empty">
          <h2>No exact match yet.</h2>
          <p>Try a broader phrase, choose another month, or reset the topic filter.</p>
          <button className="button button-navy" type="button" onClick={() => { setQuery(""); setCategory("All"); setMonth("All dates"); }}>Reset the library</button>
        </div>
      ) : null}
    </>
  );
}
