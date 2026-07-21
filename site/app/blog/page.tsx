import type { Metadata } from "next";
import Link from "next/link";
import { FinalCTA, PageHero, PageShell, SectionHeading } from "../site-components";
import BlogLibrary from "./BlogLibrary";
import { blogPosts } from "./posts";

export const metadata: Metadata = {
  title: "Florida Mortgage Blog",
  alternates: { canonical: "/blog" },
  description: "Search recent Florida mortgage answers from Dennis Ross, including VA, FHA, self-employed, homebuying, and homeowner guidance.",
};

export default function BlogPage() {
  return (
    <PageShell>
      <PageHero
        eyebrow="The DR. Mortgage USA blog"
        title="Start with the question already on your mind."
        body="I write about the real questions Florida buyers, veterans, homeowners, and self-employed borrowers bring to me. Search the library the same way you would ask the question."
      >
        <a className="button button-gold" href="#blog-library">Browse the complete archive</a>
        <Link className="button button-outline-light" href="/tools">Run the numbers</Link>
      </PageHero>

      <section className="section blog-library-section anchor-target" id="blog-library">
        <div className="shell">
          <SectionHeading
            eyebrow="Live mortgage library"
            title="Browse by topic or search the way you would ask the question."
            body="Every article I have published since February is here, including the newest posts from the live DR. Mortgage USA blog."
          />
          <BlogLibrary initialPosts={blogPosts} />
        </div>
      </section>
      <FinalCTA title="Still not sure which article fits? Start with your scenario instead." />
    </PageShell>
  );
}
