# Rate index to payment handoff

Approved by Dennis in the current session: "Yes, fix and deploy it".

## Behavior

The homepage's five Mortgage News Daily cards now link to `/tools?rateIndex=<allowlisted-id>#<calculator>`. The calculator fetches the same verified `/api/rates?source=mnd-daily-v2` feed as the homepage. No hardcoded daily rate, URL-supplied numeric rate, or user-entered quote is treated as a verified index.

- Conventional 30-year: purchase payment, 30 years.
- Conventional 15-year: purchase payment, 15 years.
- FHA 30-year: dedicated FHA calculator, 30 years.
- VA 30-year: dedicated VA purchase calculator, 30 years.
- Jumbo 30-year: purchase-payment model with the Jumbo index, 30 years. The UI explicitly says Jumbo loan limits and lender-specific underwriting are not modeled.

The selected rate is an editable starting assumption. The calculator identifies the index, its actual source date, and that it is not a quote, APR, or offer to lend. An edit made while source loading is in progress takes precedence. The explicit index selection takes precedence over a saved scenario's old rate, without discarding its home price and down payment. Manual calculator selection clears the rate-index selector while preserving unrelated attribution query parameters.

Unavailable, invalid, incomplete, undated, or out-of-range feed data never becomes an index assumption. A 15-second timeout exits loading and explains that remaining calculator values are editable assumptions, not current source pricing.

## Verification

- `node --test tests/rate-model.test.mjs`: five program/term mappings, allowlisting, malformed/unverified/undated rates, and future source snapshots.
- `npm run lint`.
- `NEXT_PUBLIC_INDEXABLE=true npm test`: production build and rendered site regressions plus the rate model tests.
- Focused TypeScript validation of `LiveRatesPanel.tsx`, `rate-model.ts`, and `tools/MortgageStudio.tsx`.
- Local and production browser verification must click every homepage card, compare displayed index with calculator input, verify matching term/mode, test manual editing, saved-scenario priority, failure behavior, and mobile layout.

No lead form, borrower record, email, CRM write, or underwriting formula is changed by this release. Roll back the scoped PR if production browser proof fails. Keep release evidence outside the public asset directory.
