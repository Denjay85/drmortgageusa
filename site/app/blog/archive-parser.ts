import type { BlogPost, BlogCategory } from "./posts";

export const liveBlogUrl = "https://drmortgageusa.com/blog";

function decodeHtml(value: string) {
  return value
    .replaceAll(String.fromCodePoint(0x2014), ",")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&nbsp;/g, " ")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&#(\d+);/g, (_, code: string) => String.fromCodePoint(Number(code)))
    .replace(/&#x([0-9a-f]+);/gi, (_, code: string) => String.fromCodePoint(Number.parseInt(code, 16)))
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function categorizePost(title: string, description: string): BlogCategory {
  const text = `${title} ${description}`.toLowerCase();
  if (/\bva\b|veteran|irr?rl|surviving spouse/.test(text)) return "VA loans";
  if (/self-employed|1099|bank statement|contractor income/.test(text)) return "Self-employed";
  if (/heloc|home equity|escrow|homestead|property tax|homeowners insurance/.test(text)) return "Homeownership";
  if (/market|buydown|price reduction|builder incentive|seller concession|investment property|refinanc/.test(text)) return "Market strategy";
  return "Buying";
}

export function parseBlogArchive(html: string): BlogPost[] {
  const posts: BlogPost[] = [];
  const cardPattern = /<a\s+href="(\/blog\/[^"]+)"[^>]*>[\s\S]*?<time[^>]*>([\s\S]*?)<\/time>[\s\S]*?<h2[^>]*>([\s\S]*?)<\/h2>[\s\S]*?<p[^>]*>([\s\S]*?)<\/p>[\s\S]*?<\/a>/gi;

  for (const match of html.matchAll(cardPattern)) {
    const date = decodeHtml(match[2]);
    const title = decodeHtml(match[3]);
    const description = decodeHtml(match[4]);
    posts.push({
      title,
      description,
      date,
      category: categorizePost(title, description),
      url: `https://drmortgageusa.com${match[1]}`,
    });
  }

  return posts;
}
