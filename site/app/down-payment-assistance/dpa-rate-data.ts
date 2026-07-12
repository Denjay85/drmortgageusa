export const dpaRateSource =
  "https://www.ehousingplus.com/homeownership/florida-housing-finance-corporation/program-highlights/";

export type DpaRateEntry = {
  label: string;
  detail?: string;
  rate: string;
};

export type DpaRateGroup = {
  id: string;
  label: string;
  assistance: string;
  fico: string;
  status?: string;
  entries: DpaRateEntry[];
};

export type DpaRateSnapshot = {
  asOf: string;
  notice: string;
  source: string;
  groups: DpaRateGroup[];
};

export const fallbackDpaRateSnapshot: DpaRateSnapshot = {
  asOf: "July 10, 2026",
  notice: "Hometown Heroes 2026 is anticipated to become available July 13, 2026.",
  source: dpaRateSource,
  groups: [
    {
      id: "standard-bond",
      label: "Standard Bond",
      assistance: "FL Assist $10,000 or FL HLP $12,500",
      fico: "640 minimum program score",
      entries: [
        { label: "FHA, VA, or USDA-RD", rate: "6.750%" },
        { label: "Fannie Mae HFA Preferred", rate: "7.500%" },
        { label: "Freddie Mac HFA Advantage", rate: "7.250%" },
      ],
    },
    {
      id: "standard-tba",
      label: "Standard TBA",
      assistance: "FL Assist $10,000 or FL HLP $12,500",
      fico: "640 minimum program score",
      entries: [
        { label: "FHA, VA, or USDA-RD", rate: "7.125%" },
        { label: "Freddie Mac HFA Advantage", detail: "At or below 80% AMI", rate: "7.375%" },
        { label: "Freddie Mac HFA Advantage", detail: "Over 80% AMI", rate: "7.500%" },
      ],
    },
    {
      id: "plus-tba",
      label: "PLUS TBA",
      assistance: "Forgivable assistance based on total loan amount",
      fico: "640 minimum program score",
      entries: [
        { label: "3% DPA", detail: "At or below 80% AMI", rate: "7.250%" },
        { label: "4% DPA", detail: "At or below 80% AMI", rate: "7.500%" },
        { label: "5% DPA", detail: "At or below 80% AMI", rate: "7.875%" },
        { label: "3% DPA", detail: "Over 80% AMI", rate: "7.375%" },
        { label: "4% DPA", detail: "Over 80% AMI", rate: "7.625%" },
        { label: "5% DPA", detail: "Over 80% AMI", rate: "N/A" },
      ],
    },
    {
      id: "heroes-bond",
      label: "Hometown Heroes Bond",
      assistance: "5% of the first mortgage, up to $35,000",
      fico: "640 minimum program score",
      status: "Expected to open July 13",
      entries: [
        { label: "FHA, VA, or USDA-RD", rate: "6.000%" },
        { label: "Fannie Mae HFA Preferred", rate: "7.000%" },
        { label: "Freddie Mac HFA Advantage", rate: "6.500%" },
      ],
    },
    {
      id: "heroes-tba",
      label: "Hometown Heroes TBA",
      assistance: "5% of the first mortgage, up to $35,000",
      fico: "640 minimum program score",
      status: "Expected to open July 13",
      entries: [
        { label: "FHA, VA, or USDA-RD", rate: "6.375%" },
        { label: "Freddie Mac HFA Advantage", detail: "At or below 80% AMI", rate: "6.625%" },
        { label: "Freddie Mac HFA Advantage", detail: "Over 80% AMI", rate: "6.750%" },
      ],
    },
  ],
};

function decodeHtml(value: string) {
  return value
    .replace(/<br\s*\/?\s*>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&nbsp;|&#160;/gi, " ")
    .replace(/&#038;/gi, "&")
    .replace(/\s+/g, " ")
    .trim();
}

function readCell(html: string, id: string) {
  const match = html.match(new RegExp(`data-cell-id=["']${id}["'][^>]*>([\\s\\S]*?)<\\/t[dh]>`, "i"));
  return match ? decodeHtml(match[1]) : "";
}

export function parseDpaRatePage(html: string): DpaRateSnapshot {
  const fallback = fallbackDpaRateSnapshot;
  const cells = (id: string) => readCell(html, id);
  const dateMatch = cells("A1").match(/(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}/);
  const rate = (id: string, fallbackRate: string) => cells(id).match(/(?:\d+\.\d+%|n\/a)/i)?.[0] || fallbackRate;

  if (!dateMatch || !cells("G5")) throw new Error("The current Florida Housing rate table could not be parsed");

  return {
    asOf: dateMatch[0],
    notice: cells("A2") || fallback.notice,
    source: dpaRateSource,
    groups: [
      {
        ...fallback.groups[0],
        entries: fallback.groups[0].entries.map((entry, index) => ({
          ...entry,
          rate: rate(["G5", "G6", "G7"][index], entry.rate),
        })),
      },
      {
        ...fallback.groups[1],
        entries: fallback.groups[1].entries.map((entry, index) => ({
          ...entry,
          rate: rate(["G10", "G11", "G12"][index], entry.rate),
        })),
      },
      {
        ...fallback.groups[2],
        entries: fallback.groups[2].entries.map((entry, index) => ({
          ...entry,
          rate: rate(["G15", "G16", "G17", "G18", "G19", "G20"][index], entry.rate),
        })),
      },
      {
        ...fallback.groups[3],
        entries: fallback.groups[3].entries.map((entry, index) => ({
          ...entry,
          rate: rate(["G23", "G24", "G25"][index], entry.rate),
        })),
      },
      {
        ...fallback.groups[4],
        entries: fallback.groups[4].entries.map((entry, index) => ({
          ...entry,
          rate: rate(["G28", "G29", "G30"][index], entry.rate),
        })),
      },
    ],
  };
}
