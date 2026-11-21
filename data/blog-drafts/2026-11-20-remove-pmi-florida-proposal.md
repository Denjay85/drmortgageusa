# Prepush publication proof: How to Remove PMI in Florida

Date: 2026-11-20. Authorization: August 19, 2026 standing exception in the operating-layer index, limited to the dedicated DrMortgageUSA site publisher. Checkout automation/blog-index-publisher clean at entry, fetched main, fast-forward was a no-op, base `bae7d38bbedb47c4a189d76cd809b4ad86ca814d`.

- Title tag: How to Remove PMI in Florida | Dr.MortgageUSA Blog (50 characters).
- Canonical: https://drmortgageusa.com/blog/remove-pmi-florida
- Description: 155 characters.
- Draft and site article SHA-256: `5f1bfc4c0bc0b0cede32e76c3ffac789624fe125ba316f60309203a6529a7e8d`.
- Changed file allowlist: `blog_posts/remove-pmi-florida.html`, `blog_posts/index.html`, `sitemap.xml`, `data/blog-drafts/2026-11-20-remove-pmi-florida.html`, `data/blog-drafts/2026-11-20-remove-pmi-florida-proposal.md`, `data/blog-automation.md`.

## Sources and editorial review

- [CFPB, What is PMI?](https://www.consumerfinance.gov/ask-cfpb/what-is-private-mortgage-insurance-en-122/), parsed November 20. Reviewed November 9, 2026. Supports lender protection and the monthly premium on page 1 of the Closing Disclosure.
- [CFPB, When can I remove PMI?](https://www.consumerfinance.gov/ask-cfpb/when-can-i-remove-private-mortgage-insurance-pmi-from-my-loan-en-202/), parsed November 20. Reviewed August 28, 2026. Supports the original-value definitions, 80 percent request, 78 percent scheduled termination, current-payment requirement, midpoint and differing investor standards. No investor-specific appraisal or eligibility criteria asserted.
- [U.S. Code, 12 USC 4902](https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid:USC-prelim-title12-section4902), parsed November 20. Displayed laws in effect September 27, 2026. Confirms written request, current status, payment history, valuation and lien evidence, current-status termination, midpoint and high-risk exceptions.
- November 20 Scout and Scribe, content calendar and current article inventory informed queue continuity after 77 completed topics. No Reddit anecdote, market rate or third-party estimate presented as fact. Five new queue items remain unchecked after topic 78.
- Internal compliance screen PASS, not formal legal approval. The 80 and 78 percent figures are verified statutory principal-balance thresholds, not advertised rates, down payments or payment amounts. No advertised rate, repayment duration, payment example, guarantee or individualized legal/tax advice. Dennis Ross NMLS 2018381 and Home1st Lending, LLC NMLS 1418 distinct from DrMortgageUSA. CTA and separate servicing directions checked.

## Local gates

- `python3 update_blog.py`: 92 posts, index and sitemap rebuilt.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: dedicated checkout, exit 0, 120 discovered, 108 passed and 12 skipped.
- `node --test tests/*.test.cjs`: exit 0, 64 passed, 0 skipped.
- `npm --prefix site test`: exit 0, build plus 18 passed, 0 skipped. Only build-created site/dist changes restored from the demonstrated clean pretest baseline. No lockfile changes.
- 28 deterministic checks PASS, including schema, identity, copy hash, links, sitemap/index, punctuation, and prequeue scope. Git whitespace check PASS. Queue date staged only after local checks; workspace queue will be marked only after production readback.

This tracked proof is the immutable prepush snapshot. The matching workspace companion records the final Git SHA, exact live readback and indexing outcome without a second commit.
