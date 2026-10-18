# Blog publication pre-release proof: 2026-10-18

Status: STAGED, NOT YET PUBLISHED. Remote and live readback pending.
Title: Buying Before Your Florida Home Sells
Slug: buying-florida-home-current-home-listed-not-sold
Planned URL: https://drmortgageusa.com/blog/buying-florida-home-current-home-listed-not-sold
Source article SHA-256: 709f210b7f17452b4c9237ad5179a4a30f04b9bb64e53bf0562b98393d84c151
Preflight HEAD: 9ae7625903187360d1ab06afd91e417a9c890cdf
Branch: automation/blog-index-publisher
Authorization: Dennis's bounded blog standing authorization dated 2026-08-19, confirmed by current task and docs/hermes-ai-operating-layer-index.md. One article only. No unrelated systems changed.
Queue: exact next unchecked item 68, Buying a Florida home while your current home is listed but not sold. Mark only after local gates pass.

## Source log
All sources accessed October 18, 2026 in isolated Google Chrome, HTTP 200, parsed. Browser snapshots in /Users/gordbot/.hermes/cache/scratch/blog-2026-10-18-source-[1-3].txt. Source-check receipt: blog-2026-10-18-sources.json.
1. https://selling-guide.fanniemae.com/sel/b3-6-06/qualifying-impact-other-real-estate-owned . Topic September 2, 2026; guide published October 7, 2026. Read current principal residence pending sale, both PITIA treatment and executed-contract/cleared-financing-contingencies exception. Claims expressly scoped to Fannie Mae loans.
2. https://selling-guide.fanniemae.com/sel/b3-4.3-10/anticipated-sales-proceeds . Topic February 23, 2016; guide published October 7, 2026. Read anticipated sale proceeds, actual proceeds documentation and existing-home settlement statement before or simultaneously with purchase settlement. No proceeds formula, tax or 1031 advice included.
3. https://www.consumerfinance.gov/owning-a-home/prepare/ . Modified May 21, 2026. Read preparation, budget and loan paperwork recommendations. Overlap budgeting explicitly framed as Dennis's recommendation, not a program rule.

## Compliance review
Trigger-term compliance: PASS, no triggering number used. No rate, APR, advertised payment/down-payment figure, fabricated statistic, eligibility guarantee or legal/tax interpretation. Contract rights referred to agent/Florida attorney. No HELOC/bridge product availability or approval claim. General education, changing-guidelines notice, individual loan-officer review and no-guarantee disclosure included. Dennis Ross NMLS 2018381 retained; DrMortgageUSA educational Brand distinct from Home 1st Lending, LLC NMLS 1418, organization https://myhome1st.com/#organization.

## Test-environment recovery
Default terminal python3 is /usr/bin/python3 (3.9): full workspace suite had 279 tests, one error in mocked Reddit HTTPError close behavior. Hermes venv Python 3.11.14 lacked PIL: 10 failures and one error. No unrelated code or infrastructure was changed. Isolated uv dependency environment with Python 3.11, Pillow and Playwright reran the exact full suite: 279 tests, OK, exit 0. Log: /Users/gordbot/.hermes/cache/scratch/blog-2026-10-18-tests-isolated.txt. Test dependencies are ephemeral, not production changes. Final post-generation run: 279 tests, OK, exit 0, 62.794 seconds. Log: /Users/gordbot/.hermes/cache/scratch/blog-2026-10-18-tests-final.txt. Deterministic article validation PASS: 156-character description, 59-character title, canonical/OG/Twitter/BlogPosting schema, Dennis/Home 1st identities, three existing internal targets, disclosure, no banned punctuation or numeric pricing triggers, byte-identical draft/install, SHA-256, index/sitemap presence and allowed scope. Generated total: 81 articles, one new article. git diff --check PASS. Validator receipt: /Users/gordbot/.hermes/cache/scratch/blog-2026-10-18-validation.json. Repository queue marked only after these local gates passed; workspace queue awaits live proof.

## Expected commit scope
- blog_posts/buying-florida-home-current-home-listed-not-sold.html
- blog_posts/index.html
- sitemap.xml
- data/blog-drafts/2026-10-18-buying-florida-home-current-home-listed-not-sold.html
- data/blog-drafts/2026-10-18-buying-florida-home-current-home-listed-not-sold-proposal.md
- data/blog-automation.md

Final publication commit, final tests, remote equality, live article/archive/API/sitemap proof and optional indexing outcome will be added to the workspace companion only after execution. The repository keeps its immutable pre-release proof to avoid a self-referential commit hash or a second production commit.
