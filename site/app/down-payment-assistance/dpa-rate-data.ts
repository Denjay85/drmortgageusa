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
  heroesFunding?: string;
  source: string;
  groups: DpaRateGroup[];
};

export const fallbackDpaRateSnapshot: DpaRateSnapshot = {
  asOf: "July 15, 2026",
  notice: "Over $45 Million Available in Hometown Heroes 2026 DPA. You may not switch an existing reservation to HTH.",
  heroesFunding: "Over $45 Million Available in Hometown Heroes 2026 DPA",
  source: dpaRateSource,
  groups: [
    {
      id: "standard-bond",
      label: "Standard Bond",
      assistance: "FL Assist $10,000 or FL HLP $12,500",
      fico: "640 minimum program score",
      entries: [
        { label: "FHA, VA, or USDA-RD", rate: "7.000%" },
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
        { label: "Freddie Mac HFA Advantage", detail: "At or below 80% AMI", rate: "7.250%" },
        { label: "Freddie Mac HFA Advantage", detail: "Over 80% AMI", rate: "7.375%" },
      ],
    },
    {
      id: "plus-tba",
      label: "PLUS TBA",
      assistance: "Forgivable assistance based on total loan amount",
      fico: "640 minimum program score",
      entries: [
        { label: "3% DPA", detail: "At or below 80% AMI", rate: "7.125%" },
        { label: "4% DPA", detail: "At or below 80% AMI", rate: "7.375%" },
        { label: "5% DPA", detail: "At or below 80% AMI", rate: "7.750%" },
        { label: "3% DPA", detail: "Over 80% AMI", rate: "7.250%" },
        { label: "4% DPA", detail: "Over 80% AMI", rate: "7.500%" },
        { label: "5% DPA", detail: "Over 80% AMI", rate: "7.875%" },
      ],
    },
    {
      id: "heroes-bond",
      label: "Hometown Heroes Bond",
      assistance: "5% of the first mortgage, up to $35,000",
      fico: "640 minimum program score",
      status: "Available",
      entries: [
        { label: "FHA, VA, or USDA-RD", rate: "6.250%" },
        { label: "Fannie Mae HFA Preferred", rate: "6.750%" },
        { label: "Freddie Mac HFA Advantage", rate: "6.500%" },
      ],
    },
    {
      id: "heroes-tba",
      label: "Hometown Heroes TBA",
      assistance: "5% of the first mortgage, up to $35,000",
      fico: "640 minimum program score",
      status: "Available",
      entries: [
        { label: "FHA, VA, or USDA-RD", rate: "6.500%" },
        { label: "Freddie Mac HFA Advantage", detail: "At or below 80% AMI", rate: "6.625%" },
        { label: "Freddie Mac HFA Advantage", detail: "Over 80% AMI", rate: "6.750%" },
      ],
    },
  ],
};

const sectionSpecs: Array<[string, string, number[]]> = [
  ["heroes-bond", "2026 HOMETOWN HEROES PROGRAM - BOND", [2, 3, 4]],
  ["heroes-tba", "2026 HOMETOWN HEROES PROGRAM - TBA", [2, 3, 4]],
  ["standard-bond", "STANDARD BOND", [2, 3, 4]],
  ["standard-tba", "STANDARD TBA", [2, 3, 4]],
  ["plus-tba", "PLUS TBA", [2, 3, 4, 5, 6, 7]],
];

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

function sourceCells(html: string) {
  const cells = new Map<string, string>();
  const regex = /data-cell-id=["']([A-Z]+\d+)["'][^>]*>([\s\S]*?)<\/t[dh]>/gi;
  for (const match of html.matchAll(regex)) cells.set(match[1].toUpperCase(), decodeHtml(match[2]));
  return cells;
}

function sectionRow(cells: Map<string, string>, heading: string) {
  for (const [cell, value] of cells) {
    if (cell.startsWith("A") && value.toUpperCase() === heading) return Number(cell.match(/\d+$/)?.[0]);
  }
  throw new Error(`The current Florida Housing rate table is missing ${heading}`);
}

function rate(cells: Map<string, string>, row: number) {
  const value = cells.get(`G${row}`) || "";
  const match = value.match(/(?:\d+\.\d+%|n\/a)/i);
  if (!match) throw new Error(`The current Florida Housing rate table is missing G${row}`);
  return match[0].toUpperCase();
}

export function parseDpaRatePage(html: string): DpaRateSnapshot {
  const cells = sourceCells(html);
  const dateMatch = (cells.get("A1") || "").match(/(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}/);
  if (!dateMatch) throw new Error("The current Florida Housing rate-sheet date could not be parsed");

  const groups = fallbackDpaRateSnapshot.groups.map((group) => ({ ...group, entries: group.entries.map((entry) => ({ ...entry })) }));
  const byId = new Map(groups.map((group) => [group.id, group]));
  for (const [id, heading, offsets] of sectionSpecs) {
    const group = byId.get(id);
    if (!group || offsets.length !== group.entries.length) throw new Error(`Unexpected offering shape for ${heading}`);
    const row = sectionRow(cells, heading);
    group.entries.forEach((entry, index) => { entry.rate = rate(cells, row + offsets[index]); });
    const fico = cells.get(`D${row + 2}`);
    const assistance = cells.get(`E${row + 2}`);
    if (fico) group.fico = `${fico} minimum program score`;
    if (assistance && id !== "plus-tba") group.assistance = assistance.replace("(Max ", "(max ");
  }

  const heroesFunding = cells.get("A2") || fallbackDpaRateSnapshot.heroesFunding;
  return {
    asOf: dateMatch[0],
    notice: heroesFunding || fallbackDpaRateSnapshot.notice,
    heroesFunding,
    source: dpaRateSource,
    groups,
  };
}
