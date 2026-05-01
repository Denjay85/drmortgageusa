import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { Link } from "wouter";
import { CalendlyModal } from "@/components/calendly-modal";
import { useState } from "react";

export default function LearnMore() {
  const [isCalendlyOpen, setIsCalendlyOpen] = useState(false);
  
  const scrollToForm = () => {
    window.location.href = "/#form-section";
  };

  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      
      <main className="flex-1 mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-lg p-6 md:p-10 border border-border">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-sm text-muted-foreground mb-8">
            <Link href="/" className="hover:text-primary transition-colors">Home</Link>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"/>
            </svg>
            <span className="text-foreground font-medium">Learn more</span>
          </nav>
          
          <section className="prose prose-slate max-w-none">
            {/* Hero */}
            <h1 className="text-3xl font-bold text-foreground">What RefiWatch Does For You</h1>
            <p className="text-muted-foreground mt-4 text-lg">
              RefiWatch is a free tracking service for your current mortgage. You tell me your basic loan details. I watch rates for you and email you when it may make sense to refinance.
            </p>

            {/* The Problem */}
            <h2 className="text-2xl font-semibold mt-10 text-foreground">The problem</h2>
            <p className="text-muted-foreground mt-4">
              Most homeowners guess about refinancing. They see a headline rate. They hear a friend talk about a refi. Then they wonder if they missed something.
            </p>
            <p className="text-muted-foreground mt-3">
              Sometimes a refinance saves you real money. Sometimes it does not. You should not have to guess which one it is.
            </p>

            {/* What RefiWatch Is */}
            <h2 className="text-2xl font-semibold mt-10 text-foreground">What RefiWatch is</h2>
            <p className="text-muted-foreground mt-4">
              RefiWatch tracks your exact mortgage in the background. You enter your loan details one time. I monitor rates and costs for you.
            </p>
            <p className="text-muted-foreground mt-3">
              When the numbers may work in your favor, I send you a simple email. No credit pull. No spam. No pressure.
            </p>

            {/* What You Share */}
            <h2 className="text-2xl font-semibold mt-10 text-foreground">What you share</h2>
            <p className="text-muted-foreground mt-4">To set up tracking, I ask for:</p>
            <div className="bg-card border border-border rounded-lg p-6 mt-4">
              <ul className="space-y-2 text-muted-foreground list-none pl-0">
                <li className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                  <span>Your name</span>
                </li>
                <li className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                  <span>Your email</span>
                </li>
                <li className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                  <span>Your current interest rate</span>
                </li>
                <li className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                  <span>A few basic details about your loan amount and term</span>
                </li>
              </ul>
              <p className="text-sm text-muted-foreground mt-4">Your best estimate is fine if you do not know every number.</p>
            </div>

            {/* What I Do With It */}
            <h2 className="text-2xl font-semibold mt-10 text-foreground">What I do with it</h2>
            <p className="text-muted-foreground mt-4">
              I use your info to check how a future refinance may look. The model checks:
            </p>
            <div className="bg-card border border-border rounded-lg p-6 mt-4">
              <ul className="space-y-2 text-muted-foreground list-none pl-0">
                <li className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-accent mt-2 flex-shrink-0"></div>
                  <span>How much your payment may drop</span>
                </li>
                <li className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-accent mt-2 flex-shrink-0"></div>
                  <span>How long it may take to recover closing costs</span>
                </li>
                <li className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-accent mt-2 flex-shrink-0"></div>
                  <span>Whether a shorter term may make sense for you</span>
                </li>
              </ul>
            </div>
            <p className="text-muted-foreground mt-4">
              If the math is weak, you will not get a refi alert from me. If the math looks good, you get a clear email that explains it in normal language.
            </p>

            {/* When Your Refi Window Opens */}
            <h2 className="text-2xl font-semibold mt-10 text-foreground">When your refi window opens</h2>
            <p className="text-muted-foreground mt-4">
              When I see a strong opportunity, I email you details like:
            </p>
            <div className="bg-card border border-border rounded-lg p-6 mt-4">
              <ul className="space-y-2 text-muted-foreground list-none pl-0">
                <li className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-accent mt-2 flex-shrink-0"></div>
                  <span>Your estimated new payment</span>
                </li>
                <li className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-accent mt-2 flex-shrink-0"></div>
                  <span>Rough costs to refinance</span>
                </li>
                <li className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-accent mt-2 flex-shrink-0"></div>
                  <span>About how much you may save over time</span>
                </li>
              </ul>
            </div>
            <p className="text-muted-foreground mt-4">
              You decide what to do. If you want to move forward, we talk and I walk you through full options as your loan officer. If you do not, you can stay on watch or unsubscribe with one click.
            </p>

            {/* What This Is Not */}
            <h2 className="text-2xl font-semibold mt-10 text-foreground">What this is not</h2>
            <div className="bg-card border border-border rounded-lg p-6 mt-4">
              <ul className="space-y-2 text-muted-foreground list-none pl-0">
                <li className="flex gap-3">
                  <svg className="w-5 h-5 text-destructive mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                  <span>Not a rate sheet blast</span>
                </li>
                <li className="flex gap-3">
                  <svg className="w-5 h-5 text-destructive mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                  <span>Not a high pressure sales funnel</span>
                </li>
                <li className="flex gap-3">
                  <svg className="w-5 h-5 text-destructive mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                  <span>Does not require a phone number to join</span>
                </li>
                <li className="flex gap-3">
                  <svg className="w-5 h-5 text-destructive mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                  <span>Does not require a hard credit pull to join</span>
                </li>
              </ul>
            </div>
            <p className="text-muted-foreground mt-4">
              It is a simple way to stop guessing and know when a refinance may be worth your time.
            </p>

            {/* CTA */}
            <div className="mt-10 p-6 rounded-xl bg-primary/5 border border-primary/20">
              <p className="font-medium text-foreground text-lg">Ready to start tracking?</p>
              <div className="mt-4 flex flex-wrap gap-3">
                <button 
                  onClick={scrollToForm}
                  className="inline-flex items-center justify-center px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors shadow-sm"
                  data-testid="button-join-now"
                >
                  Join now
                </button>
                <button 
                  onClick={() => setIsCalendlyOpen(true)}
                  className="inline-flex items-center justify-center px-6 py-3 rounded-lg border border-border bg-card hover:bg-muted transition-colors font-medium"
                  data-testid="button-book-call"
                >
                  Book a call
                </button>
              </div>
            </div>
          </section>
        </div>
      </main>
      
      <CalendlyModal isOpen={isCalendlyOpen} onClose={() => setIsCalendlyOpen(false)} />
      <SiteFooter />
    </div>
  );
}
