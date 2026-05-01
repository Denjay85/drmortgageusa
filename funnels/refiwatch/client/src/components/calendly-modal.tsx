import { useEffect, useState, useRef } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { trackContact } from "@/lib/tracking";

interface CalendlyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CalendlyModal({ isOpen, onClose }: CalendlyModalProps) {
  const [isLoading, setIsLoading] = useState(true);
  const embedRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) {
      setIsLoading(true);
      return;
    }

    if (typeof window === "undefined") return;
    trackContact("refiwatch_calendly_open");

    // Load Calendly CSS
    const existingStylesheet = document.querySelector('link[href*="calendly.com"]');
    if (!existingStylesheet) {
      const link = document.createElement("link");
      link.href = "https://assets.calendly.com/assets/external/widget.css";
      link.rel = "stylesheet";
      document.head.appendChild(link);
    }

    // Load Calendly script if not already loaded
    const existingScript = document.querySelector('script[src*="calendly.com"]');
    if (!existingScript) {
      const script = document.createElement("script");
      script.src = "https://assets.calendly.com/assets/external/widget.js";
      script.async = true;
      document.head.appendChild(script);
    }

    // Initialize Calendly widget when modal opens
    const initCalendly = () => {
      if (window.Calendly && embedRef.current) {
        embedRef.current.innerHTML = "";
        
        window.Calendly.initInlineWidget({
          url: "https://calendly.com/dennis-ross-myhome1st/30min",
          parentElement: embedRef.current,
          prefill: {},
          utm: {}
        });
        
        // Give Calendly a moment to render before hiding loading
        setTimeout(() => setIsLoading(false), 500);
      }
    };

    if (window.Calendly) {
      initCalendly();
    } else {
      const checkCalendly = setInterval(() => {
        if (window.Calendly) {
          clearInterval(checkCalendly);
          initCalendly();
        }
      }, 100);

      return () => clearInterval(checkCalendly);
    }
  }, [isOpen]);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl w-full max-h-[90vh] overflow-hidden p-0 bg-white" data-testid="calendly-modal">
        <DialogHeader className="p-6 pb-2 bg-white border-b">
          <DialogTitle>Schedule Your Consultation</DialogTitle>
          <p className="text-sm text-muted-foreground">Pick a time that works for you</p>
        </DialogHeader>
        
        <div className="relative overflow-y-auto bg-white" style={{ height: "650px" }}>
          {isLoading && (
            <div className="absolute inset-0 z-10 bg-white flex items-center justify-center">
              <div className="text-center">
                <svg className="w-16 h-16 mx-auto text-muted-foreground mb-4 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <p className="text-muted-foreground font-medium">Loading Calendly...</p>
              </div>
            </div>
          )}
          
          <div 
            ref={embedRef}
            className="w-full h-full bg-white"
            style={{ minHeight: "650px" }}
            data-testid="calendly-embed"
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}

declare global {
  interface Window {
    Calendly: any;
  }
}
