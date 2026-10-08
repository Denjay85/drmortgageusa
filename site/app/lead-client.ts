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
    DrMortgageLeadContext?: { get: () => Record<string, string> };
  }
}

function createFallbackEventId(prefix: string) {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

export async function submitLead(payload: LeadPayload) {
  if ((payload.callConsent === true || payload.smsConsent === true) && !String(payload.phone || "").trim()) {
    throw new Error("Please add a phone number for calls or texts, or leave those permissions unchecked.");
  }
  const tracking = window.DrMortgageTracking;
  const eventId = createFallbackEventId("lead_submit");
  const optionalValue = (read: () => string | undefined) => {
    try { return read() || ""; } catch { return ""; }
  };
  let attribution: Record<string, string> = {};
  try { attribution = window.DrMortgageLeadContext?.get() || {}; } catch { /* Optional measurement. */ }
  const body = {
    ...attribution,
    ...payload,
    eventId,
    fbp: optionalValue(() => tracking?.getOrCreateFbp?.()),
    fbc: optionalValue(() => tracking?.getOrCreateFbc?.()),
    pageUrl: window.location.origin + window.location.pathname,
  };

  const response = await fetch("/api/quiz-submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const result = await response.json().catch(() => null) as {
    success?: boolean; preview?: boolean; lead_id?: number; event_id?: string; errors?: string[];
  } | null;
  if (!response.ok || result?.success !== true || (result.preview !== true && !result.lead_id)) {
    const validation = response.status === 400 && Array.isArray(result?.errors)
      ? result.errors.join(" ") : "We could not confirm delivery. Please call 850-346-8514 before sending again.";
    throw new Error(validation);
  }

  if (result.preview !== true) {
    try {
      tracking?.trackLeadSubmit?.({
        eventId: result.event_id || eventId,
        content_name: payload.segment,
        content_category: payload.source,
        source: payload.source,
      });
    } catch { /* Tracking cannot turn an already saved lead into a failed form. */ }
  }

  return result;
}
