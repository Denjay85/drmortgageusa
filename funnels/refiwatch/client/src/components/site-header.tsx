import { useState } from "react";
import { Link, useLocation } from "wouter";
import logoPath from "@assets/IG DR Logo 2_1759405525636.png";

export function SiteHeader() {
  const [location] = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navLinks = [
    { href: "/", label: "Home" },
    { href: "/about", label: "About" },
    { href: "/learn", label: "Learn more" },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-white/30 bg-white/60 backdrop-blur-md shadow-sm">
      <div className="mx-auto max-w-7xl px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img 
            src={logoPath} 
            alt="Dr Mortgage USA" 
            className="h-12 w-12 rounded-full object-cover border-2 border-primary"
          />
          <div className="leading-tight">
            <p className="text-xs uppercase tracking-widest text-muted-foreground font-medium">Dr.MortgageUSA</p>
            <h1 className="font-semibold text-sm">Mortgage Rate Watcher and Refinance Prep</h1>
          </div>
        </div>
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
          {navLinks.map((link) => (
            <Link 
              key={link.href}
              href={link.href} 
              className={`hover:text-primary transition-colors ${location === link.href ? 'text-primary' : 'text-muted-foreground'}`}
              data-testid={`nav-${link.label.toLowerCase().replace(/\s+/g, '-')}`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
        
        {/* Mobile Menu Button */}
        <button 
          className="md:hidden p-2 rounded-lg hover:bg-muted transition-colors" 
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle menu"
          data-testid="mobile-menu"
        >
          {isMobileMenuOpen ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          )}
        </button>
      </div>
      
      {/* Mobile Navigation Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-white/30 bg-white/95 backdrop-blur-md">
          <nav className="flex flex-col py-2">
            {navLinks.map((link) => (
              <Link 
                key={link.href}
                href={link.href} 
                className={`px-6 py-3 text-sm font-medium hover:bg-muted transition-colors ${location === link.href ? 'text-primary bg-primary/5' : 'text-muted-foreground'}`}
                onClick={() => setIsMobileMenuOpen(false)}
                data-testid={`mobile-nav-${link.label.toLowerCase().replace(/\s+/g, '-')}`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
