import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell, SectionHeading } from "../site-components";
import BlogLibrary from "./BlogLibrary";
import { blogPosts } from "./posts";

export const metadata: Metadata = {
  title: "Florida Mortgage Blog",
  description: "Search recent Florida mortgage answers from Dennis Ross, including VA, FHA, self-employed, homebuying, and homeowner guidance.",
};

export default function BlogPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="The DR. Mortgage USA blog"
        title="Start with the question already on your mind."
        body="Plain-language mortgage answers for Florida buyers, veterans, homeowners, and self-employed borrowers, organized so the useful article is easier to find."
      >
        <a className="button button-gold" href="#blog-library">Browse the complete archive</a>
        <Link className="button button-outline-light" href="/tools">Run the numbers</Link>
      </PageHero>

      <section className="section blog-library-section anchor-target" id="blog-library">
        <div className="shell">
          <SectionHeading
            eyebrow="Live mortgage library"
            title="Browse by topic or search the way you would ask the question."
            body="The library connects to the current DR. Mortgage USA blog and keeps a complete local fallback, so every article since February remains visible."
          />
          <BlogLibrary initialPosts={blogPosts} />
        </div>
      </section>
      <FinalCTA title="Still not sure which article fits? Start with your scenario instead." />
    </PageShell>
  );
}
