// The URL carries only an allowlisted index selector. Rates and source dates
// are always read from the same verified feed used by the homepage.
export const rateModelIndexes = [
  { id: "conventional-30", label: "Conventional 30-year", mode: "purchase", years: 30 },
  { id: "conventional-15", label: "Conventional 15-year", mode: "purchase", years: 15 },
  { id: "fha-30", label: "FHA 30-year", mode: "fha", years: 30 },
  { id: "va-30", label: "VA 30-year", mode: "va-purchase", years: 30 },
  { id: "jumbo-30", label: "Jumbo 30-year", mode: "purchase", years: 30 },
] as const;

export type RateModelIndex = (typeof rateModelIndexes)[number];
export type IndexAssumption = RateModelIndex & { rate: number; asOf: string };

export function modelPaymentHref(index: RateModelIndex) {
  return `/tools?rateIndex=${index.id}#${index.mode}`;
}

export function readRateIndexSelection(search: string): RateModelIndex | null {
  const id = new URLSearchParams(search).get("rateIndex");
  return rateModelIndexes.find((index) => index.id === id) ?? null;
}

export function resolveIndexAssumption(index: RateModelIndex, payload: unknown): IndexAssumption | null {
  if (!payload || typeof payload !== "object") return null;
  const data = payload as Record<string, unknown>;
  if (data.verified !== true || data.status !== "verified") return null;
  if (typeof data.asOf !== "string" || !data.asOf.trim() || data.asOf.length > 80 || !Number.isFinite(Date.parse(data.asOf))) return null;
  if (!data.rates || typeof data.rates !== "object") return null;
  const raw = (data.rates as Record<string, unknown>)[index.label];
  if (typeof raw !== "string" || !/^\d{1,2}(?:\.\d{1,3})?%$/.test(raw)) return null;
  const rate = Number(raw.slice(0, -1));
  if (!Number.isFinite(rate) || rate <= 0 || rate >= 30) return null;
  return { ...index, rate, asOf: data.asOf };
}
