export type LeadPayload = Record<string, string | boolean | number | null | undefined> & {
  firstName?: string;
  email?: string;
  phone?: string;
  segment: string;
  source: string;
};

type TrackingApi = {
  createEventId?: (prefix: string) => string;
  getOrCreateFbp?: () => string;
  getOrCreateFbc?: () => string;
  trackLeadSubmit?: (details: Record<string, string>) => void;
};

declare global {
  interface Window {
    DrMortgageTracking?: TrackingApi;
  }
}

function createFallbackEventId(prefix: string) {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

export async function submitLead(payload: LeadPayload) {
  const tracking = window.DrMortgageTracking;
  const eventId = tracking?.createEventId?.("lead_submit") || createFallbackEventId("lead_submit");
  const body = {
    ...payload,
    eventId,
    fbp: tracking?.getOrCreateFbp?.() || "",
    fbc: tracking?.getOrCreateFbc?.() || "",
    pageUrl: window.location.href,
    referrer: document.referrer,
  };

  const response = await fetch("/api/quiz-submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const result = await response.json().catch(() => null) as { errors?: string[]; error?: string } | null;
    throw new Error(result?.errors?.join(" ") || result?.error || "The request could not be submitted.");
  }

  tracking?.trackLeadSubmit?.({
    eventId,
    content_name: payload.segment,
    content_category: payload.source,
    source: payload.source,
  });

  return response.json();
}
