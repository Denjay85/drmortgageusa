import { Link } from "wouter";
import profileImagePath from "@assets/IG DR Logo 2_1759405525636.png";

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-border bg-white/95 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Main Footer Content */}
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div className="flex items-start gap-4">
              <img 
                src={profileImagePath} 
                alt="Dennis Ross - Your Trusted Mortgage Expert" 
                className="w-auto h-24 object-contain flex-shrink-0"
              />
              <div className="flex flex-col justify-center space-y-2">
                <div>
                  <p className="font-semibold text-foreground">Dennis Ross</p>
                  <p className="text-sm text-muted-foreground">Your Trusted Mortgage Expert</p>
                  <p className="text-sm font-medium text-foreground mt-1">NMLS #2018381</p>
                </div>
                <p className="text-xs text-muted-foreground pt-2 border-t border-border">
                  Powered by Home1st Lending, LLC NMLS #1418
                </p>
              </div>
            </div>
            <div className="flex items-center gap-6 text-sm">
              <Link href="/learn" className="text-primary hover:underline font-medium" data-testid="footer-learn">
                Learn more
              </Link>
              <a href="https://drmortgageusa.com/" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline font-medium" data-testid="footer-fullsite">
                Full site
              </a>
            </div>
          </div>

          {/* Compliance Disclaimers */}
          <div className="border-t border-border pt-6 space-y-4">
            <div className="text-xs text-muted-foreground leading-relaxed space-y-3">
              <p>
                <strong>NMLS Consumer Access:</strong> Visit{" "}
                <a 
                  href="https://www.nmlsconsumeraccess.org" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-primary hover:underline"
                >
                  www.nmlsconsumeraccess.org
                </a>{" "}
                for company and individual licensing information.
              </p>
              
              <p>
                <strong>Equal Housing Opportunity:</strong> We do business in accordance with the Federal Fair Housing Law. Under the Federal Fair Housing Act, it is illegal to discriminate on the basis of race, color, national origin, religion, sex, handicap, or familial status.
              </p>
              
              <p>
                <strong>Department of Defense Disclaimer:</strong> This is not an offer to enter into an agreement. Not all customers will qualify. Information, rates, and programs are subject to change without notice. All products are subject to credit and property approval. Other restrictions and limitations may apply.
              </p>
            </div>

            {/* Legal Links */}
            <div className="flex flex-wrap items-center gap-4 text-xs pt-2">
              <a href="/privacy" className="text-primary hover:underline font-medium" data-testid="footer-privacy">
                Privacy Policy
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
