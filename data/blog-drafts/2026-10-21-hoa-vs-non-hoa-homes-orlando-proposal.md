# Blog pre-release proof, October 21, 2026

Status: Local gates passed; commit, deployment and live verification pending.
Title: HOA vs Non-HOA Homes in Orlando: What to Check
Slug: hoa-vs-non-hoa-homes-orlando
URL: https://drmortgageusa.com/blog/hoa-vs-non-hoa-homes-orlando
Queue item: 69. What Orlando buyers should check when comparing HOA and non-HOA homes.
Authorization: Dennis's bounded August 19, 2026 blog standing authorization, confirmed by current task and docs/hermes-ai-operating-layer-index.md. One new article only.
Dedicated checkout: /Users/gordbot/.hermes/workspace/drmortgageusa-blog-publisher
Branch: automation/blog-index-publisher
Preflight: clean tree; fetched origin main; HEAD and origin/main both 2a585dc43235bf30001cfb0d5e247ef936334be7.

## Source log
Both authoritative pages parsed in the current run on October 21, 2026.
1. CFPB, Are condo/co-op fees or homeowners' association dues included in my monthly mortgage payment? https://www.consumerfinance.gov/ask-cfpb/are-condoco-op-fees-or-homeowners-association-dues-included-in-my-monthly-mortgage-payment-en-1945/ . Reviewed September 11, 2024. Supports usual direct association billing separate from servicer payment. No dues ranges copied.
2. Fannie Mae B3-6-03, Monthly Housing Expense for the Subject Property. https://selling-guide.fanniemae.com/sel/b3-6-03/monthly-housing-expense-subject-property . Topic December 16, 2020; guide published October 7, 2026. Supports association dues in applicable monthly qualifying expense and principal-residence DTI. Claims expressly limited to Fannie Mae loans.
Other content is explicitly framed as Dennis's comparison checklist and questions, not legal requirements or association-document entitlements. No legal, tax, insurance coverage, pricing, or program-availability claims.

## Compliance and deterministic checks
158-character meta description; 68-character title including suffix. Canonical, matching OG/Twitter, BlogPosting JSON-LD, Dennis Ross personal canonical identifier and NMLS 2018381, organization canonical identifier https://myhome1st.com/#organization and company NMLS 1418 preserved. Home1st Lending spelling follows current business brain. Brand and lender remain distinct. Two existing internal article targets, contact CTA, changing-guidelines and non-guarantee disclosure. No em/en dashes, rates, APR, payment illustrations, down-payment figures, fabricated statistics or guarantees.
Source HTML SHA-256: ebafa816bfec19c8a7fb851bc4db5458e0912584d9bc0098cd50c9aa3fed9255
Initial internal-link validation rejected a guessed filename before any article write. Resolved against the actual repository filename and reran successfully.

## Tests
Command from dedicated publisher checkout: PYTHONDONTWRITEBYTECODE=1 uv run --no-project --python 3.11 --with-requirements requirements.txt python -B -m unittest discover -s tests -p 'test_*.py'
Result: exit 0; 110 tests run, 12 skipped, OK, 1.670 seconds. Skips are retained, not represented as tested coverage. Expected mocked service-failure messages and pre-existing resource warnings appeared in passing tests.
Log: /Users/gordbot/.hermes/cache/scratch/blog-2026-10-21-tests.log
Generator: python3 update_blog.py; exit 0. git diff --check: exit 0. Post-test inspection found only the intended generated index/sitemap and new article/draft; no dependency/lockfile mutation.

## Allowed release files
- blog_posts/hoa-vs-non-hoa-homes-orlando.html
- blog_posts/index.html
- sitemap.xml
- data/blog-drafts/2026-10-21-hoa-vs-non-hoa-homes-orlando.html
- data/blog-drafts/2026-10-21-hoa-vs-non-hoa-homes-orlando-proposal.md
- data/blog-automation.md

Final commit, remote equality, live article/archive/API/sitemap readback and optional indexing results will be added to the workspace companion after execution. The repository proof is the immutable pre-release receipt, avoiding a self-referential commit or a second production commit.
