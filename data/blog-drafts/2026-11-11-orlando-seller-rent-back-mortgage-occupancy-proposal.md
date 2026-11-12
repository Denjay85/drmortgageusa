# Recovery publication proof: Orlando Seller Rent-Back and Mortgage Occupancy

Execution: 0742175acae24704aaf17a07fc1d2f5c. Current run: 2026-11-11T18:58:42.229452-05:00.
Bounded August 19, 2026 blog authorization confirmed in current job and operating-layer index.
Clean dedicated branch automation/blog-index-publisher; fetched HEAD == origin/main == 0a5998cd72561743b78ac40fd012e9b467d3cce5; ff-only already up to date.
Queue item 75 selected, still unchecked. Complete draft from earlier November 11 run retained byte-for-byte.
Prior failed proof preserved in matching -1855-prior-proof.md. Earlier run failed stale-clock DPA test; remote now contains separate test fix 0a5998cd72561743b78ac40fd012e9b467d3cce5. No test/production code changes in this publication run.
Article SHA-256: d21fa70b552d5546d864168794813504eb6e0eb6cf726e4a44b61f3d8bf8df98.
Canonical: https://drmortgageusa.com/blog/orlando-seller-rent-back-mortgage-occupancy

## Sources revalidated this execution
Fannie Mae B2-1.1-01 Occupancy Types, https://selling-guide.fanniemae.com/sel/b2-1.1-01/occupancy-types, HTTP 200 parsed, November 4, 2026 page date. Exact primary residence 60-day/one-year terms and exceptions rechecked.
The Florida Bar Buying a Home, https://www.floridabar.org/public/consumer/pamphlet006/, HTTP 200 isolated Chrome parsed. Possession/occupancy agreement/insurance checklist rechecked. September 2022 revision explicitly preserved, not presented as a new law.
Matching -1855-sources.json contains source excerpts from this execution. Sources retrieved in this execution with direct requests and isolated real Chrome; source excerpts preserved.

## Editorial compliance
PASS internal screen, not formal legal approval. General mortgage planning, no lease form/legal opinion. Legal questions referred to buyer's own attorney, insurance to licensed agent. No guaranteed eligibility/funding/outcomes, rate/APR/down payment/payment claims, invented statistics, em/en dashes, or prohibited lender spelling. Dennis Ross NMLS 2018381 and distinct DrMortgageUSA brand/Home1st Lending, LLC employer preserved. Fannie Mae rule not generalized to every loan or interpreted as permission for a rent-back. VA section makes review recommendations only. Disclosure and direct non-guaranteed CTA present.

## Release status
All local release gates PASS. Article staged, queue item 75 marked published November 11 after local gates as requested. Commit/push pending; not yet a live publication claim.
Final workspace companion will record exact commit, changed files, tests, live readback and indexing. Repository companion will retain pre-push proof without self-referential commit claims.

## Same-run prepush gates
PASS in dedicated publisher checkout. Python command: `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_*.py`, exit 0, 120 tests, 12 skipped. Root Node: `node --test tests/*.test.cjs`, exit 0, 64 tests, zero skipped. Site: `npm test` in site/, full build plus 18 tests, exit 0, zero skipped. Mock error-path output is test output, not live CRM/ManyChat actions. Existing installed dependencies used; no lockfile changes. Site build test-only mutations restored after proven pre-test HEAD hashes; 45 tracked generated outputs and 12 same-run untracked outputs handled, no unrelated changes retained.
Deterministic checks PASS: 69-character title, 159-character description, metadata/canonical/OG/Twitter, BlogPosting valid JSON and identity/date checks, NMLS 2018381, Home1st Lending, LLC, internal link target existence, source anchors, disclosure/non-guaranteed CTA, punctuation/spelling, exact draft byte equality, index/sitemap inclusion, exact scope, SHA-256. `git diff --check` passed. Current draft SHA-256 d21fa70b552d5546d864168794813504eb6e0eb6cf726e4a44b61f3d8bf8df98.

Exact allowed release files:
- blog_posts/orlando-seller-rent-back-mortgage-occupancy.html
- blog_posts/index.html
- sitemap.xml
- data/blog-drafts/2026-11-11-orlando-seller-rent-back-mortgage-occupancy.html
- data/blog-drafts/2026-11-11-orlando-seller-rent-back-mortgage-occupancy-proposal.md
- data/blog-automation.md
