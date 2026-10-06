# Blog Automation — DrMortgageUSA

## Schedule
Research, write, compliance-check, publish, and verify one new blog article
every 3 days. Dennis granted standing autonomy for this bounded DrMortgageUSA
blog pipeline on 2026-08-19. No per-article approval is required.

## Scheduled Publish Process
1. Fetch and fast-forward the dedicated publisher checkout to `origin/main`; fail closed on divergence or uncommitted changes.
2. Write the complete article to `data/blog-drafts/<date>-<slug>.html` and stage the release in `blog_posts/<slug>.html`.
3. Write a companion proof record to `data/blog-drafts/<date>-<slug>-proposal.md` with title, slug, sources, compliance notes, changed files, commit, live URL, and final SHA-256.
4. Validate title (at most 69 characters including the ` | Dr.MortgageUSA Blog` suffix), meta description, canonical URL, OG tags, JSON-LD, author, NMLS 2018381, internal links, disclosure, banned spellings, and punctuation.
5. Rebuild the blog index and sitemap, run the complete repository test suite and article-specific deterministic checks, then commit and push only the expected article/index/sitemap/queue files.
6. Verify `HEAD == origin/main`, the public article returns HTTP 200 with the expected title, `/api/blog` contains the article without a stale public-cache response, and the rendered `/blog` visibly lists the article before marking the queue item published. Because `/blog` is client-rendered, raw HTML from curl is not archive proof. Prefer an isolated Playwright browser DOM readback and require one visible article card with the exact title plus exact article link. On the current rendered archive, scope to the `article` element containing the exact href, verify its `h2` text and link visibility separately; the link text itself is only `Read the full article` and is not the title. Do not use Chrome `--dump-dom` as the primary observer because the process can hang without flushing usable DOM. If any browser process hangs after a valid DOM capture, terminate it only after the captured DOM passes both checks.
7. Submit supported indexing notifications only after live readback succeeds. Never change CRM, ManyChat, ads, email, DMs, or unrelated production systems.

## Recovery Publish Process
If a prior run staged a complete draft but failed before publication:
1. Fast-forward the dedicated publisher checkout to `origin/main`.
2. Copy the approved draft into `blog_posts/<slug>.html` and update the index and sitemap.
3. Run repository tests and article-specific compliance checks. Repair test defects before release; never publish around a red suite.
4. Show the final diff and publish only the approved files.
5. Verify the remote commit, public article URL, and live blog archive before claiming publication.
6. Load Google credentials from the configured local keyring/shell environment. Never store keyring passwords or OAuth tokens in this file.

## SEO Requirements (every post)
- Title tag: `<title>Topic | Dr.MortgageUSA Blog</title>`
- Meta description: 150-160 chars, includes target keyword + Orlando/Florida
- Canonical URL: `https://drmortgageusa.com/blog/<slug>`
- OG tags: type=article, title, description, url, site_name
- Twitter card: summary_large_image
- Author: Dennis Ross
- H1 matches title, H2s for sections
- Internal links to other blog posts where relevant
- CTA at bottom linking to contact/apply
- NMLS 2018381 in footer
- Schema.org Article structured data (JSON-LD)

## Topic Queue (in order)
1. ✅ HELOC vs home equity loan Florida 2026 (published 2026-03-09)
2. ✅ How to qualify for a mortgage with 1099 income Florida (published 2026-03-10)
3. ✅ VA loan assumability guide Florida 2026 (published 2026-03-12)
4. ✅ What happens at a mortgage closing in Florida (published 2026-03-15)
5. ✅ How much house can I afford in Orlando 2026 (published 2026-03-18)
6. ✅ Mortgage preapproval vs prequalification Florida (published 2026-03-18)
7. ✅ Closing costs in Florida explained 2026 (published 2026-03-21)
8. ✅ VA funding fee guide 2026 (who pays, exemptions, how it works) (published 2026-03-24)
9. ✅ Debt-to-income ratio explained for Florida homebuyers (published 2026-03-30)
10. ✅ Refinancing out of FHA to conventional in Florida (published 2026-04-07)
11. ✅ HOA and condo financing in Florida (warrantable vs non-warrantable) (published 2026-04-11)
12. ✅ How property taxes work in Florida for new homebuyers (published 2026-04-14)
13. ✅ Florida homestead exemption guide for new homeowners (published 2026-04-17)
14. ✅ Investment property loans in Florida 2026 (published 2026-04-22)
15. ✅ Credit repair strategy for buying a home in Florida (published 2026-04-24)
16. ✅ VA minimum property requirements in Florida 2026 (published 2026-05-03)
17. ✅ VA termite inspection requirements Florida 2026 (published 2026-05-06)
18. ✅ VA loan occupancy requirements Florida 2026 (published 2026-05-09)
19. ✅ Florida down payment assistance programs explained for 2026 (published 2026-02-26, existing post found)
20. ✅ Why your pre-approval amount is not your real homebuying budget (published 2026-05-22)
21. ✅ How seller credits work in Florida, closing costs, rate buydowns, and cash to close (published 2026-03-03, existing post found)
22. ✅ VA loan seller concessions in Florida, what veterans can and cannot use them for (published 2026-05-24)
23. ✅ How to compare mortgage quotes, APR, points, lender credits, and fees (published 2026-05-27)
24. ✅ What Florida buyers should know before waiving inspections or repairs (published 2026-05-30)
25. ✅ How Florida homeowners insurance can affect your mortgage approval (published 2026-06-02)
26. ✅ New construction builder incentives in Orlando, what buyers should check first (published 2026-06-05)
27. ✅ VA appraisal repairs in Florida, what veterans should know before closing (published 2026-06-08)
28. ✅ Florida escrow shortage after buying a home, why payments jump (published 2026-06-11)
29. ✅ Orlando move-up buyer strategy, keeping cash without overbuying (published 2026-06-14)
30. ✅ VA residual income explained for Florida veterans (published 2026-06-17)
31. ✅ Condo financing red flags in Florida, warrantable vs non-warrantable updates (published 2026-06-20)
32. ✅ Rate buydown vs price reduction, which helps Florida buyers more (published 2026-06-23)
33. ✅ Florida self-employed borrower documentation checklist (published 2026-06-26)
34. ✅ Florida mortgage gift funds rules for homebuyers (published 2026-06-29)
35. ✅ Florida bank statement mortgage loans for self-employed borrowers (published 2026-07-02)
36. ✅ Orlando FHA 203k renovation loan basics for buyers (published 2026-07-08)
37. ✅ Florida manufactured home mortgage rules buyers should know (published 2026-07-11)
38. ✅ Buying a Florida home after divorce, mortgage approval checklist (published 2026-07-14)
39. ✅ Orlando short-term rental financing basics for investors (published 2026-07-17)
40. ✅ Florida mortgage reserves explained for buyers and investors (published 2026-07-20)
41. ✅ Florida mortgage rate lock guide for Orlando buyers (published 2026-07-23)
42. ✅ Florida co-borrower vs cosigner mortgage differences for homebuyers (published 2026-07-26)
43. ✅ Orlando appraisal gap options when the home value comes in low (published 2026-07-29)
44. ✅ Buying a Florida home with student loan debt (published 2026-08-01)
45. ✅ Florida cash-out refinance closing cost checklist (published 2026-08-04)
46. ✅ Employment changes before mortgage closing in Florida (published 2026-08-07)
47. ✅ Mortgage recast vs refinance in Florida, which option fits your payment goal (published 2026-08-10)
48. ✅ Florida title insurance and lender title policy basics for homebuyers (published 2026-08-13)
49. ✅ Temporary 2-1 buydown basics for Orlando and Florida homebuyers (published 2026-08-19)
50. ✅ DSCR loans explained for Florida real estate investors (published 2026-08-19)
51. ✅ Asset depletion mortgage basics for Florida retirees (published 2026-08-22)
52. ✅ Florida bridge loan basics for move-up homebuyers (published 2026-08-25)
53. ✅ Condo special assessments and mortgage approval in Florida (published 2026-08-28)
54. ✅ FHA condo single-unit approval basics for Florida homebuyers (published 2026-08-31)
55. ✅ VA-approved condos in Florida, how veterans can check a project (published 2026-09-03)
56. ✅ Florida condo questionnaire explained for mortgage buyers (published 2026-09-06)
57. ✅ Buying a Florida condo with pending litigation (published 2026-09-09)
58. ✅ Florida condo master insurance deductibles and mortgage approval (published 2026-09-12)
59. ✅ Florida condo rental restrictions for second-home and investment financing (published 2026-09-15)
60. ✅ Conditional approval vs clear to close in Florida, what buyers need to know (published 2026-09-18)
61. ✅ Mortgage underwriting letters of explanation for Florida homebuyers (published 2026-09-21)
62. ✅ How large bank deposits affect mortgage approval in Florida (published 2026-09-27)
63. ✅ Florida homebuyer final walkthrough and mortgage closing checklist (published 2026-09-30)
64. ✅ Home equity loan vs cash-out refinance for Florida homeowners (published 2026-10-03)
65. ✅ Orlando homebuyers guide to appraisal reconsideration of value (published 2026-10-06)

## Queue Continuity Rule
If every topic in the queue is marked published, generate six SEO topics from current content gaps, Scout/Scribe reports, borrower questions, and the DrMortgageUSA content calendar, append them to the queue, and continue autonomous publication. Verify substantive mortgage claims against authoritative sources.

## Google Indexing Strategy
- Ordinary blog articles are not eligible for the Google Indexing API. Do not run `scripts/google-index-submit.sh` for BlogPosting pages; Google's official supported scope is JobPosting or BroadcastEvent embedded in VideoObject. Use the published sitemap and only supported existing notification scripts.
- IndexNow submission to Bing/Yandex (step 7 above) - key: e5b56c17491147a0b68601ac76defa13
- robots.txt already allows all crawling
- Google Search Console verified under dhustle85@gmail.com (personal account, NOT work email)
- Google Indexing API authorized under dhustle85@gmail.com via gog CLI (--client drmortgageusa)
- Structured data (JSON-LD Article schema) on every post
- Internal linking between related posts improves crawl depth
- Do not use the deprecated Google sitemap-ping endpoint or substitute the unsupported Indexing API for blog articles.
- Never embed the GOG keyring password in documentation or scheduled prompts. Load it from the configured local shell/keyring only during an approved publish run.

## Writing Standards
- Match Dennis's voice: direct, educational, no fluff
- No em dashes, no cliches, no filler
- Real numbers and program names, not vague generalizations
- Orlando/Central Florida focus where applicable
- Always note that guidelines can change and to consult a loan officer
- NMLS 2018381 disclosure
