import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { HeroSection } from "@/components/hero-section";
import { LeadForm } from "@/components/lead-form";
import { Link } from "wouter";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      
      <main className="flex-1 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pb-20">
        <HeroSection />
        
        {/* Two Column Layout: Form + Proof */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-10">
          <LeadForm />
          
          {/* Proof Card */}
          <section className="bg-card border border-border rounded-3xl p-6 md:p-8 shadow-sm">
            <h3 className="text-2xl font-bold">Why this works</h3>
            <ul className="mt-4 space-y-4">
              <li className="flex gap-3 items-start">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-accent/20 flex items-center justify-center mt-0.5">
                  <svg className="w-4 h-4 text-accent" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                  </svg>
                </div>
                <p className="text-muted-foreground text-sm leading-relaxed">We track your loan terms, balance, and payment target, not broad averages.</p>
              </li>
              <li className="flex gap-3 items-start">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-accent/20 flex items-center justify-center mt-0.5">
                  <svg className="w-4 h-4 text-accent" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                  </svg>
                </div>
                <p className="text-muted-foreground text-sm leading-relaxed">Alerts fire on math, not headlines. No hype.</p>
              </li>
              <li className="flex gap-3 items-start">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-accent/20 flex items-center justify-center mt-0.5">
                  <svg className="w-4 h-4 text-accent" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                  </svg>
                </div>
                <p className="text-muted-foreground text-sm leading-relaxed">You see clear savings and breakeven before you decide.</p>
              </li>
              <li className="flex gap-3 items-start">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-accent/20 flex items-center justify-center mt-0.5">
                  <svg className="w-4 h-4 text-accent" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                  </svg>
                </div>
                <p className="text-muted-foreground text-sm leading-relaxed">When rates dip, you get to the front of the line.</p>
              </li>
            </ul>
            <Link href="/learn" className="mt-6 inline-flex items-center gap-2 text-primary hover:underline text-sm font-medium" data-testid="link-learn-more">
              Learn more 
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"/>
              </svg>
            </Link>
          </section>
        </div>
        
        {/* Benefits Section */}
        <section className="mt-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-card border border-border rounded-2xl p-6 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <h4 className="font-semibold text-lg">Timing edge</h4>
              <p className="text-sm text-muted-foreground mt-2 leading-relaxed">Headlines lag. Your alert hits early so you can act while pricing holds.</p>
            </div>
            <div className="bg-card border border-border rounded-2xl p-6 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                </svg>
              </div>
              <h4 className="font-semibold text-lg">Simple math</h4>
              <p className="text-sm text-muted-foreground mt-2 leading-relaxed">We show payment change, breakeven months, and total interest saved.</p>
            </div>
            <div className="bg-card border border-border rounded-2xl p-6 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <h4 className="font-semibold text-lg">No pressure</h4>
              <p className="text-sm text-muted-foreground mt-2 leading-relaxed">If the numbers are weak, we say so. You stay put until it pays.</p>
            </div>
          </div>
        </section>
        
        {/* FAQ Section */}
        <section id="faq" className="mt-12">
          <div className="bg-card border border-border rounded-2xl p-6 md:p-8">
            <h3 className="text-2xl font-bold">Refinance FAQs</h3>
            <p className="text-muted-foreground mt-2">Short answers first. If you are unsure, start the 60 second refi check and I will run the numbers for you.</p>
            <div className="mt-6 divide-y divide-border">
              <details className="py-4 group">
                <summary className="cursor-pointer flex items-center justify-between font-medium hover:text-primary transition-colors">
                  <span>How does RefiWatch work?</span>
                  <svg className="w-5 h-5 text-muted-foreground group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </summary>
                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">You give your current loan details. I track the market and notify you when a refinance may save you money.</p>
              </details>
              <details className="py-4 group">
                <summary className="cursor-pointer flex items-center justify-between font-medium hover:text-primary transition-colors">
                  <span>Who is this for?</span>
                  <svg className="w-5 h-5 text-muted-foreground group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </summary>
                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">Homeowners who want someone to watch the market for them. If you pay a mortgage and plan to stay put, this may fit you.</p>
              </details>
              <details className="py-4 group">
                <summary className="cursor-pointer flex items-center justify-between font-medium hover:text-primary transition-colors">
                  <span>Do you pull my credit to sign up?</span>
                  <svg className="w-5 h-5 text-muted-foreground group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </summary>
                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">No. Your credit has nothing to do with joining RefiWatch. I do not run your credit to add you to the system.</p>
              </details>
              <details className="py-4 group">
                <summary className="cursor-pointer flex items-center justify-between font-medium hover:text-primary transition-colors">
                  <span>When does it make sense to refinance?</span>
                  <svg className="w-5 h-5 text-muted-foreground group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </summary>
                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">It may make sense when your new payment drops enough to beat the cost of the refi. I flag it only when the numbers look good.</p>
              </details>
              <details className="py-4 group">
                <summary className="cursor-pointer flex items-center justify-between font-medium hover:text-primary transition-colors">
                  <span>What does RefiWatch cost?</span>
                  <svg className="w-5 h-5 text-muted-foreground group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </summary>
                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">Nothing. Joining is free. If you later choose to refinance with me, the lender pays me.</p>
              </details>
              <details className="py-4 group">
                <summary className="cursor-pointer flex items-center justify-between font-medium hover:text-primary transition-colors">
                  <span>What happens when my refi window opens?</span>
                  <svg className="w-5 h-5 text-muted-foreground group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </summary>
                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">You get a simple update showing possible savings and payment options. You decide if you want to move forward.</p>
              </details>
              <details className="py-4 group">
                <summary className="cursor-pointer flex items-center justify-between font-medium hover:text-primary transition-colors">
                  <span>Can I leave RefiWatch if I change my mind?</span>
                  <svg className="w-5 h-5 text-muted-foreground group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </summary>
                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">Yes. You can unsubscribe any time with one click.</p>
              </details>
            </div>
          </div>
        </section>
        
        {/* Final CTA */}
        <section className="mt-12">
          <div className="rounded-2xl border border-border bg-white/95 backdrop-blur-sm shadow-lg p-8 text-center">
            <h3 className="text-2xl md:text-3xl font-bold">Find out first when your refinance window opens</h3>
            <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
              <button 
                onClick={() => document.getElementById('form-section')?.scrollIntoView({ behavior: 'smooth' })}
                className="inline-flex items-center justify-center px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors shadow-sm"
                data-testid="cta-join-free"
              >
                Join free
              </button>
              <Link href="/learn" className="inline-flex items-center justify-center px-6 py-3 rounded-lg border border-border bg-card hover:bg-muted transition-colors font-medium" data-testid="cta-learn-more">
                Learn more
              </Link>
            </div>
          </div>
        </section>
      </main>
      
      <SiteFooter />
    </div>
  );
}
