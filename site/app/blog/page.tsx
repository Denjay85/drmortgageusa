import type { Metadata } from "next";
import { FinalCTA, PageHero, PageShell, SectionHeading } from "../site-components";
import { blogCollectionSchema } from "../entity-schema";
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
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(blogCollectionSchema) }}
      />
      <PageHero
        eyebrow="The DR. Mortgage USA blog"
        title="Start with the question already on your mind."
        body="I write about the real questions Florida buyers, veterans, homeowners, and self-employed borrowers bring to me. Search the library the same way you would ask the question."
      >
        <a className="button button-gold" href="https://ask-dr-mortgage.denjay85.chatgpt.site/">Ask Dr. Mortgage</a>
        <a className="button button-outline-light" href="#blog-library">Browse the complete archive</a>
      </PageHero>

      <section className="section blog-ask-section" aria-labelledby="ask-dr-mortgage-title">
        <div className="shell">
          <div className="blog-ask-panel">
            <div className="blog-ask-copy">
              <p className="eyebrow">Ask it in your own words</p>
              <h2 id="ask-dr-mortgage-title">A question is a good place to start.</h2>
              <p>Something your lender said. Money for closing. Using your VA benefit again. Ask Dr. Mortgage looks through my articles for an answer and takes you to the part that explains it.</p>
              <a className="button button-gold" href="https://ask-dr-mortgage.denjay85.chatgpt.site/">Ask your question <span aria-hidden="true">→</span></a>
              <p className="blog-ask-note">Answers from my guides, not a live chat with me. Need to talk through your situation? <a href="tel:+18503468514">Call Dennis.</a></p>
            </div>
            <div className="blog-ask-examples">
              <p>Try a question</p>
              {[
                "What is an IRRRL?",
                "Can my parents help with my down payment?",
                "Can I use my VA loan a second time?",
              ].map((question) => (
                <a key={question} href={`https://ask-dr-mortgage.denjay85.chatgpt.site/?question=${encodeURIComponent(question)}`}>
                  <span>{question}</span><span aria-hidden="true">↗</span>
                </a>
              ))}
              <small>Read the answer. Open the guide. Ask what comes next.</small>
            </div>
          </div>
        </div>
      </section>

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
