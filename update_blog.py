#!/usr/bin/env python3
"""
update_blog.py — Auto-update blog index and sitemap when new posts are added.

Run this any time a new blog post HTML file is added to blog_posts/.
It reads the metadata from each post and rebuilds:
  - blog_posts/index.html (the visible blog listing page)
  - sitemap.xml (submitted to Google Search Console)

Usage:
    python3 update_blog.py
    python3 update_blog.py --dry-run   (preview changes without writing)
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
BLOG_DIR = BASE_DIR / "blog_posts"
SITEMAP_PATH = BASE_DIR / "sitemap.xml"
INDEX_PATH = BLOG_DIR / "index.html"
BASE_URL = "https://drmortgageusa.com"

DRY_RUN = "--dry-run" in sys.argv

def extract_meta(filepath):
    """Pull title, description, and date from an HTML blog post file."""
    content = filepath.read_text(encoding="utf-8")

    title = ""
    m = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
    if m:
        title = m.group(1).strip()
        # Strip " | Dr.MortgageUSA" suffix if present
        title = re.sub(r'\s*\|.*$', '', title).strip()

    desc = ""
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
    if m:
        desc = m.group(1).strip()

    date = ""
    # Look for published date in meta or time tags
    m = re.search(r'<meta\s+(?:name|property)=["\'](?:article:published_time|date)["\']\s+content=["\']([\d-]+)', content, re.IGNORECASE)
    if m:
        date = m.group(1)[:10]
    if not date:
        m = re.search(r'<time[^>]*datetime=["\']([\d-]+)["\']', content, re.IGNORECASE)
        if m:
            date = m.group(1)[:10]
    if not date:
        # Fall back to file modification date
        date = datetime.fromtimestamp(filepath.stat().st_mtime).strftime("%Y-%m-%d")

    return title, desc, date

def format_date_display(date_str):
    """Convert 2026-02-22 to February 22, 2026."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%B %d, %Y").replace(" 0", " ")
    except Exception:
        return date_str

def get_posts():
    """Scan blog_posts/ and return sorted list of post metadata."""
    posts = []
    for f in sorted(BLOG_DIR.glob("*.html")):
        if f.name == "index.html":
            continue
        slug = f.stem
        title, desc, date = extract_meta(f)
        if not title:
            print(f"  WARNING: No title found in {f.name} — skipping")
            continue
        posts.append({
            "slug": slug,
            "filename": f.name,
            "title": title,
            "desc": desc,
            "date": date,
            "date_display": format_date_display(date),
            "url": f"{BASE_URL}/blog/{slug}",
        })

    # Sort newest first
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts

def build_index(posts):
    """Rebuild the blog index HTML."""
    cards = ""
    for p in posts:
        cards += f"""
            <a href="/blog/{p['slug']}" class="block bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
                <div class="p-6">
                    <time class="text-sm text-gold font-semibold">{p['date_display']}</time>
                    <h2 class="text-xl font-bold text-gray-900 mt-2 mb-3">{p['title']}</h2>
                    <p class="text-gray-600 text-sm leading-relaxed">{p['desc']}</p>
                    <span class="inline-block mt-4 text-gold font-semibold text-sm">Read More &rarr;</span>
                </div>
            </a>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mortgage Blog | Dr.MortgageUSA - Dennis Ross</title>
    <meta name="description" content="Florida mortgage tips, guides, and advice from Dennis Ross, Navy veteran and licensed mortgage broker. Learn about VA loans, FHA, conventional, and more.">
    <link rel="canonical" href="https://drmortgageusa.com/blog">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .bg-navy {{ background-color: #1a1a2e; }}
        .text-gold {{ color: #D4AF37; }}
        .bg-gold {{ background-color: #D4AF37; }}
    </style>
</head>
<body class="bg-gray-50">
    <nav class="bg-navy text-white py-4 sticky top-0 z-50">
        <div class="container mx-auto px-4 flex items-center justify-between">
            <a href="/" class="text-xl font-bold">Dr.MortgageUSA</a>
            <div class="flex items-center gap-6">
                <a href="/" class="text-gray-300 hover:text-white transition-colors">Home</a>
                <a href="/#rates" class="text-gray-300 hover:text-white transition-colors">Rates</a>
                <a href="/#faq" class="text-gray-300 hover:text-white transition-colors">FAQ</a>
                <a href="tel:+18503468514" class="bg-gold text-navy font-bold py-2 px-5 rounded-full text-sm hover:scale-105 transition-transform">Call Now</a>
            </div>
        </div>
    </nav>

    <div class="py-16">
        <div class="container mx-auto px-4 max-w-4xl">
            <div class="text-center mb-12">
                <h1 class="font-bold text-3xl md:text-4xl text-gray-900 mb-4">Mortgage Tips &amp; Guides</h1>
                <p class="text-gray-600 text-lg">Straight talk about mortgages in Florida. No jargon, no fluff.</p>
            </div>
            <div class="grid gap-6">{cards}
            </div>
        </div>
    </div>

    <footer class="bg-navy text-gray-400 py-8 mt-12">
        <div class="container mx-auto px-4 text-center text-sm">
            <p>Dennis Ross | NMLS #2018381 | Powered by Home1st Lending, LLC NMLS #1418</p>
            <p class="mt-2">Licensed in Florida | Equal Housing Lender</p>
        </div>
    </footer>
</body>
</html>"""
    return html

def build_sitemap(posts):
    """Rebuild sitemap.xml with all pages."""
    today = datetime.now().strftime("%Y-%m-%d")
    urls = f"""  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{BASE_URL}/blog</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>"""

    for p in posts:
        urls += f"""
  <url>
    <loc>{p['url']}</loc>
    <lastmod>{p['date']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""

def main():
    print(f"Scanning {BLOG_DIR} for posts...")
    posts = get_posts()
    print(f"Found {len(posts)} posts:")
    for p in posts:
        print(f"  [{p['date']}] {p['title'][:60]}")

    index_html = build_index(posts)
    sitemap_xml = build_sitemap(posts)

    if DRY_RUN:
        print("\n--- DRY RUN: no files written ---")
        print(f"Would write {len(index_html)} chars to {INDEX_PATH}")
        print(f"Would write {len(sitemap_xml)} chars to {SITEMAP_PATH}")
        return

    INDEX_PATH.write_text(index_html, encoding="utf-8")
    SITEMAP_PATH.write_text(sitemap_xml, encoding="utf-8")
    print(f"\nWrote blog index: {INDEX_PATH}")
    print(f"Wrote sitemap:    {SITEMAP_PATH}")
    print(f"\nNext steps:")
    print("  git add blog_posts/index.html sitemap.xml")
    print('  git commit -m "Add new blog post + update index/sitemap"')
    print("  git push origin main")
    print("\nGoogle will re-crawl the sitemap within 24-48 hours.")

if __name__ == "__main__":
    main()
