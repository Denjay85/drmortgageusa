import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { Link } from "wouter";
import logoPath from "@assets/IG DR Logo 2_1759405525636.png";

export default function About() {
  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      
      <main className="flex-1 py-12 md:py-16">
        <div className="mx-auto max-w-4xl px-4">
          
          {/* Hero Section */}
          <section className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 md:p-12 shadow-lg border border-border mb-8">
            <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">
              <img 
                src={logoPath} 
                alt="Dennis Ross - Dr. Mortgage USA" 
                className="w-32 h-32 md:w-40 md:h-40 rounded-full object-cover border-4 border-primary shadow-lg"
                data-testid="img-dennis-ross"
              />
              <div className="text-center md:text-left">
                <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-2" data-testid="text-page-title">
                  About Dr. Mortgage USA
                </h1>
                <p className="text-xl text-primary font-semibold mb-4">Dennis Ross</p>
                <div className="flex flex-wrap justify-center md:justify-start gap-3">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-100 text-blue-800 text-sm font-medium">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                    </svg>
                    Navy Veteran
                  </span>
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-green-100 text-green-800 text-sm font-medium">
                    15 Years of Service
                  </span>
                </div>
              </div>
            </div>
          </section>
          
          {/* Main Bio */}
          <section className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 md:p-10 shadow-lg border border-border mb-8">
            <p className="text-lg text-foreground leading-relaxed mb-6" data-testid="text-bio">
              I'm Dennis Ross. Most people know me as Dr. Mortgage USA. I'm a Navy veteran with fifteen years of service, five years active duty with two combat deployments, and ten years in the reserves. That background shapes how I run my refinance business. <strong>Precision. Clarity. No surprises.</strong>
            </p>
          </section>

          {/* Service Cards */}
          <div className="grid gap-6 md:grid-cols-2 mb-8">
            
            {/* Refinance with Confidence */}
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 md:p-8 shadow-lg border border-border">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                </svg>
              </div>
              <h2 className="text-xl font-bold text-foreground mb-3">Refinance with confidence</h2>
              <p className="text-muted-foreground leading-relaxed">
                You want a lower payment, a better rate, or access to your equity. My job is to show you every option in plain language and help you decide what makes financial sense right now. No pressure. Just straight answers.
              </p>
            </div>
            
            {/* 79 Lenders */}
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 md:p-8 shadow-lg border border-border">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
              </div>
              <h2 className="text-xl font-bold text-foreground mb-3">I shop 79 lenders for you</h2>
              <p className="text-muted-foreground leading-relaxed">
                Rates change fast. Programs change fast. I compare options from 79 lenders in real time so you never leave money on the table. FHA, VA, conventional, cash out, streamline, second homes, or investment properties. You get the structure that fits your goals.
              </p>
            </div>
            
            {/* Understand Every Number */}
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 md:p-8 shadow-lg border border-border">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                </svg>
              </div>
              <h2 className="text-xl font-bold text-foreground mb-3">You will understand every number</h2>
              <p className="text-muted-foreground leading-relaxed">
                We review everything on Zoom. I break down your payment, your savings, your costs, and your breakeven point. You see exactly where every dollar goes so you can make a smart call. I follow up with clear emails that take the guesswork out of the process.
              </p>
            </div>
            
            {/* My Mission */}
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 md:p-8 shadow-lg border border-border">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"/>
                </svg>
              </div>
              <h2 className="text-xl font-bold text-foreground mb-3">My mission</h2>
              <p className="text-muted-foreground leading-relaxed">
                I bring the same integrity and discipline from my Navy career into every refinance I handle. I help homeowners across Florida and families relocating to Florida turn their equity into real financial strength and build long term stability without stress.
              </p>
            </div>
          </div>
          
          {/* CTA Section */}
          <section className="bg-white/95 backdrop-blur-sm border border-border rounded-2xl p-8 text-center shadow-lg">
            <h2 className="text-2xl font-bold text-foreground mb-3">Ready to get started?</h2>
            <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
              Join my Rate Watch list and I'll monitor the market for you. When rates hit your savings goal, you'll be the first to know.
            </p>
            <a 
              href="/#form-section"
              className="inline-flex items-center justify-center px-8 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors shadow-sm"
              data-testid="button-get-started"
            >
              Sign up for Rate Watch
            </a>
          </section>
          
        </div>
      </main>
      
      <SiteFooter />
    </div>
  );
}
