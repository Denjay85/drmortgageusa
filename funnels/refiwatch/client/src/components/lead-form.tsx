import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { insertLeadSchema, type InsertLead } from "@shared/schema";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { CalendlyModal } from "./calendly-modal.tsx";
import { trackLead } from "@/lib/tracking";

export function LeadForm() {
  const [showCalendly, setShowCalendly] = useState(false);
  const { toast } = useToast();

  const form = useForm<InsertLead>({
    resolver: zodResolver(insertLeadSchema),
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      yearBought: undefined,
      savingsGoal: undefined,
      currentRate: "",
      consent: false,
      source: "rate-watch",
    },
  });

  const submitLeadMutation = useMutation({
    mutationFn: async (data: InsertLead) => {
      const payload: InsertLead = {
        ...data,
        utmData: JSON.stringify(getUTM()),
      };
      
      const response = await apiRequest("POST", "/api/refiwatch/lead", payload);
      return response.json();
    },
    onSuccess: (data) => {
      trackLead({
        eventId: data?.event_id,
        contentName: "refiwatch_lead_form",
        currentRate: form.getValues("currentRate"),
      });
      toast({
        title: "Success!",
        description: "Your submission has been received. We'll be in touch soon!",
      });
      form.reset();
      setShowCalendly(true);
    },
    onError: (error: any) => {
      toast({
        title: "Submission failed",
        description: error.message || "Please try again or contact us at (850) 346-8514",
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data: InsertLead) => {
    submitLeadMutation.mutate(data);
  };

  return (
    <>
      <section id="form-section" className="bg-card border border-border rounded-3xl p-6 md:p-8 shadow-sm">
        <h3 className="text-2xl font-bold">Get rate alerts for your exact mortgage</h3>
        <p className="text-muted-foreground mt-2 text-sm">
          Fill this out once. I track rates for you and email you when it may save you money.
        </p>
        
        <form onSubmit={form.handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <div>
            <Label htmlFor="name">Full name *</Label>
            <Input
              id="name"
              {...form.register("name")}
              placeholder="John Smith"
              className="mt-1.5"
              data-testid="input-name"
            />
            {form.formState.errors.name && (
              <p className="text-sm text-destructive mt-1">{form.formState.errors.name.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="email">Email *</Label>
            <Input
              id="email"
              type="email"
              {...form.register("email")}
              placeholder="john@example.com"
              className="mt-1.5"
              data-testid="input-email"
            />
            {form.formState.errors.email && (
              <p className="text-sm text-destructive mt-1">{form.formState.errors.email.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="currentRate">Current interest rate (or best guess) *</Label>
            <Input
              id="currentRate"
              {...form.register("currentRate")}
              placeholder="e.g. 6.5%"
              className="mt-1.5"
              data-testid="input-current-rate"
            />
            <p className="text-xs text-muted-foreground mt-1">Your best estimate is fine.</p>
            {form.formState.errors.currentRate && (
              <p className="text-sm text-destructive mt-1">{form.formState.errors.currentRate.message}</p>
            )}
          </div>

          <div className="flex items-start gap-3 p-4 rounded-lg bg-muted/50 border border-border">
            <Checkbox
              id="consent"
              {...form.register("consent")}
              onCheckedChange={(checked) => form.setValue("consent", !!checked)}
              className="mt-0.5"
              data-testid="checkbox-consent"
            />
            <Label htmlFor="consent" className="text-xs text-muted-foreground leading-relaxed">
              By submitting, you agree that I may contact you by phone, text, or email. Msg and data rates may apply. You may opt out at any time. *
            </Label>
          </div>
          
          {form.formState.errors.consent && (
            <p className="text-sm text-destructive">{form.formState.errors.consent.message}</p>
          )}

          <Button 
            type="submit" 
            disabled={submitLeadMutation.isPending}
            className="w-full"
            data-testid="button-submit"
          >
            {submitLeadMutation.isPending ? (
              <>
                <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin mr-2" />
                Submitting...
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"/>
                </svg>
                Start tracking my rate
              </>
            )}
          </Button>
        </form>
      </section>

      <CalendlyModal isOpen={showCalendly} onClose={() => setShowCalendly(false)} />
    </>
  );
}

function getUTM() {
  const params = new URLSearchParams(window.location.search);
  return {
    utm_source: params.get('utm_source') || '',
    utm_medium: params.get('utm_medium') || '',
    utm_campaign: params.get('utm_campaign') || '',
    utm_term: params.get('utm_term') || '',
    utm_content: params.get('utm_content') || '',
    fbclid: params.get('fbclid') || '',
  };
}
