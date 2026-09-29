#!/usr/bin/env python3
"""Read-only crawl and identity audit. Synthetic requests do not prove AI inclusion."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.error
import urllib.request
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

ORIGIN = "https://drmortgageusa.com"
PERSON_ID = ORIGIN + "/about#dennis-ross"
BRAND_ID = ORIGIN + "/#brand"
EMPLOYER_ID = "https://myhome1st.com/#organization"
EXPERIENCE = "https://www.experience.com/reviews/dennis-14873595"
GOOGLE_MAPS = "https://www.google.com/maps?cid=3829412552217676351"
REQUIRED_LINKS = {
    EXPERIENCE, GOOGLE_MAPS, "https://myhome1st.com/dennis/",
    "https://www.nmlsconsumeraccess.org/EntityDetails.aspx/INDIVIDUAL/2018381",
    "https://www.bing.com/maps?ss=ypid.YN215EB5A5FBD32023",
    "https://linktr.ee/dr.mortgageusa",
}
PRIORITY_PATHS = ("/", "/about", "/va-loans-orlando",
                  "/blog/va-loan-guide-florida-veterans-2026")
ENTITY_PATHS = {"/", "/about", "/blog", "/va-loans-orlando",
                "/orlando-mortgage-broker", "/first-time-homebuyer-orlando",
                "/refinance-florida", "/heloc-orlando"}
# Tokens are simulated from this audit host, not sent from verified crawler IPs.
BOT_AGENTS = (
    "Googlebot", "bingbot", "OAI-SearchBot", "ChatGPT-User", "GPTBot",
    "ClaudeBot", "Claude-User", "Claude-SearchBot", "PerplexityBot",
    "Perplexity-User", "Applebot", "Amazonbot", "Amzn-SearchBot", "Amzn-User",
)
POLICY_TOKENS = ("Google-Extended", "Applebot-Extended")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonicals = []
        self.directives = []
        self.links = []
        self.text = []
        self.json_blocks = []
        self.script = None
        self.hidden = 0
        self.in_title = False
        self.title = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonicals.append(attrs.get("href", ""))
        if tag == "meta":
            name = attrs.get("name", "").lower()
            if name in {"robots", *(x.lower() for x in BOT_AGENTS)}:
                self.directives.append((name, attrs.get("content", "")))
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag in ("script", "style"):
            self.hidden += 1
        if tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self.script = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.script is not None:
            self.json_blocks.append("".join(self.script))
            self.script = None
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.script is not None:
            self.script.append(data)
        if not self.hidden:
            self.text.append(data)


def fetch(url, agent="DrMortgageUSA-Discoverability-Audit/2.0"):
    request = urllib.request.Request(
        url, headers={"User-Agent": agent, "Cache-Control": "no-cache"})
    try:
        response = urllib.request.urlopen(request, timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    except Exception as error:
        return dict(url=url, final_url=url, status=0, content_type="",
                    x_robots="", body="", error=str(error))
    with response:
        return dict(url=url, final_url=response.geturl(), status=response.code,
                    content_type=response.headers.get("Content-Type", ""),
                    x_robots=", ".join(response.headers.get_all("X-Robots-Tag", [])),
                    body=response.read().decode("utf-8", errors="replace"))


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def blocked(value):
    return bool(re.search(r"\b(noindex|none|nofollow)\b", value, re.I))


def field(value, key):
    return value.get(key) if isinstance(value, dict) else None


def inspect_page(result, origin=ORIGIN):
    issues = []
    body = result["body"]
    page = Page()
    page.feed(body)
    path = result["url"].removeprefix(origin)
    if result["status"] != 200:
        issues.append(f"HTTP {result['status']}: {result.get('error', '')}")
    if result["final_url"].rstrip("/") != result["url"].rstrip("/"):
        issues.append("unexpected redirect")
    if "text/html" not in result["content_type"].lower():
        issues.append("expected text/html")
    if len(page.canonicals) != 1 or page.canonicals[0].rstrip("/") != (ORIGIN + path).rstrip("/"):
        issues.append("missing, duplicate, or mismatched canonical")
    if blocked(result["x_robots"]) or any(blocked(v) for _, v in page.directives):
        issues.append("blocking robots directive")
    all_nodes = []
    for block in page.json_blocks:
        try:
            all_nodes.extend(nodes(json.loads(block)))
        except (ValueError, TypeError) as error:
            issues.append(f"invalid JSON-LD: {error}")
    visible = " ".join(" ".join(page.text).split())
    title = "".join(page.title).strip()
    if not title or len(title) > 69:
        issues.append("missing title or title exceeds repository limit of 69 characters")
    for number in ("2018381", "1418"):
        if not re.search(r"\b" + number + r"\b", visible):
            issues.append("missing visible NMLS " + number)
    if "463950" in body:
        issues.append("unrelated NMLS 463950")
    if "zillow.com/lender-profile/dennis0564" in body:
        issues.append("excluded legacy Zillow identity")
    expects_entity = path in ENTITY_PATHS or path.startswith("/blog/")
    people = [n for n in all_nodes if n.get("@type") == "Person"
              and n.get("@id") == PERSON_ID and "sameAs" in n]
    if expects_entity and not people:
        issues.append("missing canonical Dennis Person")
    for person in people:
        links = person.get("sameAs", [])
        missing = REQUIRED_LINKS - {x for x in links if isinstance(x, str)} if isinstance(links, list) else REQUIRED_LINKS
        if missing:
            issues.append("missing Person identity links: " + ", ".join(sorted(missing)))
        if str(field(person.get("identifier"), "value")) != "2018381":
            issues.append("incorrect Dennis NMLS association")
        if field(person.get("worksFor"), "@id") != EMPLOYER_ID:
            issues.append("incorrect Dennis employer association")
        if field(person.get("brand"), "@id") != BRAND_ID:
            issues.append("incorrect Dennis brand association")
    if expects_entity:
        brands = [n for n in all_nodes if n.get("@id") == BRAND_ID and "name" in n]
        employers = [n for n in all_nodes if n.get("@id") == EMPLOYER_ID and "name" in n]
        if not brands or any(n.get("@type") != "Brand" or
                             field(n.get("owner"), "@id") != PERSON_ID for n in brands):
            issues.append("missing or incorrect Dennis-owned Brand")
        if not employers or any(n.get("@type") != "Organization" or
                                str(field(n.get("identifier"), "value")) != "1418"
                                for n in employers):
            issues.append("missing or incorrect Home 1st NMLS association")
    if path in ("/about", "/va-loans-orlando") and EXPERIENCE not in page.links:
        issues.append("missing visible Experience verification link")
    if path == "/about":
        for phrase in ("VA home loan guidance across Greater Orlando",
                       "not a separate lender or mortgage company", "not Dr. Mortgage, LLC"):
            if phrase not in visible:
                issues.append("missing visible About identity statement: " + phrase)
    return dict(url=result["url"], status=result["status"],
                canonical=page.canonicals, experience_link=EXPERIENCE in body,
                person_entities=len(people), issues=issues)


def resource_issues(result, expected_type):
    issues = []
    if result["status"] != 200:
        issues.append(f"HTTP {result['status']}")
    if result["content_type"].split(";")[0].strip().lower() != expected_type:
        issues.append("wrong content type")
    if blocked(result["x_robots"]):
        issues.append("blocking X-Robots-Tag")
    return issues


def audit(origin=ORIGIN):
    resources = {}
    for path, mime in (("/robots.txt", "text/plain"), ("/sitemap.xml", "application/xml"),
                       ("/llms.txt", "text/plain")):
        result = fetch(origin + path)
        resources[path] = dict(status=result["status"], content_type=result["content_type"],
                               issues=resource_issues(result, mime), body=result["body"])
    robot = RobotFileParser()
    robot.parse(resources["/robots.txt"]["body"].splitlines())
    if ORIGIN + "/sitemap.xml" not in resources["/robots.txt"]["body"]:
        resources["/robots.txt"]["issues"].append("missing sitemap declaration")
    llms = resources["/llms.txt"]
    for expected in (EXPERIENCE, "2018381", "1418", GOOGLE_MAPS, "not a separate lender",
                     "does not refer to Dr. Mortgage, LLC"):
        if expected not in llms["body"]:
            llms["issues"].append("missing identity fact: " + expected)
    if "463950" in llms["body"] or "zillow.com/lender-profile/dennis0564" in llms["body"]:
        llms["issues"].append("excluded identity data")
    try:
        root = ET.fromstring(resources["/sitemap.xml"]["body"])
        urls = [n.text.strip() for n in root.findall("{*}url/{*}loc") if n.text]
    except ET.ParseError:
        urls = []
        resources["/sitemap.xml"]["issues"].append("malformed XML")
    if not urls or len(set(urls)) != len(urls):
        resources["/sitemap.xml"]["issues"].append("empty or duplicate URL inventory")
    if any(not u.startswith(ORIGIN + "/") for u in urls):
        resources["/sitemap.xml"]["issues"].append("unexpected sitemap host")
    # Never follow untrusted sitemap URLs to unrelated hosts.
    safe_urls = [origin + u[len(ORIGIN):] for u in urls if u.startswith(ORIGIN + "/")]
    with ThreadPoolExecutor(max_workers=6) as pool:
        pages = [inspect_page(r, origin) for r in pool.map(fetch, safe_urls)]
    for p in pages:
        if not robot.can_fetch("Googlebot", p["url"]):
            p["issues"].append("robots.txt blocks Googlebot")
    pairs = [(agent, path) for agent in BOT_AGENTS for path in PRIORITY_PATHS]

    def check_pair(pair):
        agent, path = pair
        checked = inspect_page(fetch(origin + path, agent), origin)
        if not robot.can_fetch(agent, origin + path):
            checked["issues"].append("robots.txt disallows token")
        return dict(agent=agent, path=path, **checked)

    with ThreadPoolExecutor(max_workers=4) as pool:
        checks = list(pool.map(check_pair, pairs))
    policies = [
        dict(token=token, path=path, allowed=robot.can_fetch(token, origin + path))
        for token in POLICY_TOKENS for path in PRIORITY_PATHS
    ]
    for resource in resources.values():
        resource.pop("body")
    clean = (not any(r["issues"] for r in resources.values()) and
             not any(p["issues"] for p in pages) and
             not any(c["issues"] for c in checks) and all(p["allowed"] for p in policies))
    return dict(
        timestamp=datetime.now(timezone.utc).isoformat(), clean=clean,
        measurement="synthetic_http_and_public_identity; not actual crawler visits or AI inclusion",
        resources=resources, sitemap_urls=len(urls), pages=pages,
        synthetic_requests=checks, robots_policy_tokens=policies,
        visibility_status="not_measured_by_this_script",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=ORIGIN)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.base_url.rstrip("/"))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(
        timestamp=result["timestamp"], clean=result["clean"], resources=result["resources"],
        sitemap_urls=result["sitemap_urls"],
        page_failures=[p for p in result["pages"] if p["issues"]],
        synthetic_requests=len(result["synthetic_requests"]),
        synthetic_failures=[c for c in result["synthetic_requests"] if c["issues"]],
        robots_policy_tokens=result["robots_policy_tokens"],
        visibility_status=result["visibility_status"],
    ), indent=2))
    return 0 if result["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
