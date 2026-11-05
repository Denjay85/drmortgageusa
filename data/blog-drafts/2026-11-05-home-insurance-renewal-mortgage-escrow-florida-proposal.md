# Publication proof: Florida Home Insurance Renewal and Escrow

Run: 2026-11-05T18:11:50-05:00
Queue: 74, Home insurance renewal and mortgage escrow in Florida, what to review before switching.
Authorization: bounded blog standing exception 2026-08-19, confirmed in current job and operating-layer index.
Preflight: dedicated publisher branch automation/blog-index-publisher, clean tree, fetched HEAD equals origin/main c2723d0c7c128ba046442fbd954c07642dbde9ed, ff-only already up to date.
No complete staged draft for topic found. Created one new article, not a replacement publication.
Canonical: https://drmortgageusa.com/blog/home-insurance-renewal-mortgage-escrow-florida
Article SHA-256: c81a08dd22de14ed3430c1bbf0d2c39624d6b7bf9483b38b5a8ec1edd7f186cd
Title length including suffix: 63. Meta description length: 157.

## Source log
Current web retrieval November 5, 2026: all four official pages parsed. Retrieval date is not a publication date.
1. PARSED: CFPB, What is an escrow or impound account?, https://www.consumerfinance.gov/ask-cfpb/what-is-an-escrow-or-impound-account-en-140/
2. PARSED: Florida DFS, Tips for Shopping for Homeowners Insurance, https://www.myfloridacfo.com/Division/ICA/ShoppingforInsurance/Tips
3. PARSED: CFPB, Force-placed homeowners insurance, https://www.consumerfinance.gov/ask-cfpb/what-can-i-do-if-my-mortgage-lender-servicer-is-charging-me-for-force-placed-homeowners-insurance-en-219/
4. PARSED: CFPB, Problems with escrow accounts, https://www.consumerfinance.gov/ask-cfpb/what-should-i-do-if-im-having-problems-with-my-escrow-or-impound-account-en-2082/

CFPB escrow overview reviewed September 11, 2024. Force-placed FAQ reviewed September 4, 2020; current page parsed today. Escrow-problems FAQ reviewed April 3, 2024. Florida DFS current online consumer education, no publication date asserted. No rate, insurance price, legal deadline, statute interpretation, eligibility or program limit claim.

## Compliance review
PASS, internal editorial screen, not formal legal/company approval. Mortgage process education, not insurance advice or placement. Coverage decisions routed to licensed agent. No guaranteed savings/payment change, fabricated numbers, rate/APR or numeric repayment trigger terms. Process checklists explicitly recommendations, not universal servicing rules. Refund handling is a question, not a claim of entitlement. Home1st Lending, LLC canonical organization preserved, separate from DrMortgageUSA brand; Dennis Ross NMLS 2018381, company NMLS 1418 from current template. Direct non-guaranteed contact CTA. No em/en dashes or prohibited company spelling.

## Release gates
PASS, same dedicated checkout. Python: `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'`, exit 0, 118 tests, 12 skipped. Node: `node --test tests/*.test.cjs`, exit 0, 64 tests, zero skipped. Site: `npm test` from site/, build plus 18 tests, exit 0, zero skipped. Root package.json has only a placeholder failing npm test, so real suites invoked explicitly. Test logs in matching workspace draft paths. Mock offline/error-path messages are test fixtures, not external operations.
Deterministic article gate PASS: metadata, 157-character description, 63-character title, canonical/social tags, BlogPosting JSON, identity, source anchors, internal target existence, dates, disclosure/CTA, draft equality, source HTTP 200 readbacks, generated archive/sitemap inclusion, banned punctuation/spellings, SHA-256 and exact allowed scope. `git diff --check` exit 0.
Site build rewrote only previously clean tracked site/dist/client files and created new hashed bundles. Restored only these proven same-run test outputs to their exact pre-test HEAD state and removed only those test-created untracked bundles. No dependency or lockfile mutation. Post-test diff contains only approved article/index/sitemap/draft/proof files. No commit or push yet.
Allowed scope: new article, generated index/sitemap, matching repository draft HTML/proof, data/blog-automation.md. No unrelated files.
Pre-release snapshot. Final workspace companion will record commit, live proof and indexing without a self-referential proof commit.
