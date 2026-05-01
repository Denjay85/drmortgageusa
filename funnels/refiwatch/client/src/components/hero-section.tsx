import { Link } from "wouter";

export function HeroSection() {
  const scrollToForm = () => {
    const formElement = document.getElementById('form-section');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section className="mt-8 md:mt-12">
      <div className="rounded-3xl bg-white/95 backdrop-blur-sm p-6 md:p-10 border border-border shadow-lg">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 text-accent text-xs font-semibold mb-4">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
              </svg>
              Free Rate Monitoring
            </div>
            <h2 className="text-3xl md:text-5xl font-bold leading-tight tracking-tight">
              Stop guessing refinance timing. Get an email the moment it makes sense.
            </h2>
            <p className="mt-4 text-muted-foreground text-base md:text-lg leading-relaxed">
              News is slow. Markets move fast. One missed day can cost you thousands over your mortgage life. Rate Watch tracks your exact loan, not the market average, and alerts you when to act.
            </p>
            <div className="mt-6 flex flex-wrap items-center gap-3">
              <button 
                onClick={scrollToForm}
                className="inline-flex items-center justify-center px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors shadow-sm"
                data-testid="hero-start-free"
              >
                Start free
              </button>
              <Link 
                href="/learn" 
                className="inline-flex items-center justify-center px-6 py-3 rounded-lg border border-border bg-card hover:bg-muted transition-colors font-medium"
                data-testid="hero-how-it-works"
              >
                How it works
              </Link>
            </div>
            <p className="mt-4 text-xs text-muted-foreground flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
              No spam. One-click unsubscribe.
            </p>
          </div>
          <div className="bg-card border border-border rounded-2xl p-4 md:p-6 shadow-lg">
            <div className="rounded-xl bg-gradient-to-br from-accent/5 to-accent/10 border border-accent/20 p-5">
              <p className="text-sm text-muted-foreground font-medium">Average monthly savings when trigger hits</p>
              <p className="text-4xl md:text-5xl font-bold mt-2 bg-gradient-to-br from-accent to-accent/70 bg-clip-text text-transparent">$275</p>
              <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"/>
                </svg>
                Client sample
              </p>
            </div>
            <div className="grid grid-cols-3 gap-3 mt-4">
              <div className="rounded-lg bg-muted border border-border p-3 text-center">
                <p className="text-xs text-muted-foreground font-medium">Active watchers</p>
                <p className="font-bold text-xl mt-1.5">1,274</p>
              </div>
              <div className="rounded-lg bg-muted border border-border p-3 text-center">
                <p className="text-xs text-muted-foreground font-medium">Avg alert lead time</p>
                <p className="font-bold text-xl mt-1.5">3 days</p>
              </div>
              <div className="rounded-lg bg-muted border border-border p-3 text-center">
                <p className="text-xs text-muted-foreground font-medium">Refi close time</p>
                <p className="font-bold text-xl mt-1.5">21 days</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
