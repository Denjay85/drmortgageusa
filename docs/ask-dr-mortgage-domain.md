# Ask Dr. Mortgage, same-domain release

## Scope

Dennis approved fixing the blog's Ask Dr. Mortgage destination and repository access. The public tool is now a native page at `/ask-dr-mortgage`, not a redirect or iframe. Both blog buttons and all three example-question links use internal paths. Existing CRM, ad, lead and ManyChat integrations are unchanged.

## Hosting boundary

- Interface and assets: built from `site/app/ask-dr-mortgage/` and served by the existing Flask/Render website.
- Answer service: the existing Dennis guide-backed API. `ask_mortgage.py` bridges only library, search, conversation, ask, feedback and article-click events under `/api/ask-dr-mortgage/`.
- This does not migrate the original answer-service database or owner research desk. Existing retention/deletion behavior stays with that service; the privacy page explains this. Do not decommission that service while the bridge is in use.
- No visitor browser request or link goes to the old host. No iframe, open proxy, LLM provider change or new credential is introduced.

## Safety

- Only the tool's `dm_conversation` cookie crosses the backend boundary. It is host-only, Secure, HttpOnly, SameSite=Lax and scoped to `/api/ask-dr-mortgage` for seven days.
- Main-site authentication, bearer headers and visitor IP headers are never forwarded.
- Owner research/review/sync endpoints are deliberately not exposed through the public bridge.
- Cross-site mutations, oversized questions/body/history, arbitrary URLs and unexpected upstream HTML/redirects fail closed.
- Question and conversation responses are no-store. API responses are noindex.
- Ask calls time out below the existing Gunicorn worker timeout. Errors do not echo private questions, cookies or upstream infrastructure details.

## Verification

Run:

```
ENABLE_RATE_UPDATER=0 python -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/lead-forms.test.cjs tests/lead-context.test.cjs tests/tracking-events.test.cjs tests/lead-client.test.cjs
cd site
npm run lint
NEXT_PUBLIC_INDEXABLE=true npm test
```

The CI workflow also runs the new bridge security tests.

Full `tsc --noEmit` encounters existing missing Cloudflare Worker type declarations in `db/index.ts` and `worker/index.ts`; the release does not change those files. The frontend lint, build and rendered tests are the project's canonical checks. Do not report the full type-check as passing.

## Live acceptance gates

1. All five blog links are internal and work, including query-string prefill.
2. The page stays on drmortgageusa.com while an actual synthetic question gets a guide-backed answer.
3. Source article links stay on the main website.
4. Follow-ups, feedback, guide search and cookie-backed refresh/resume work.
5. Delete a synthetic conversation, confirm the tool cookie is cleared, and confirm refresh shows no deleted turns.
6. Test narrow mobile rendering and no horizontal overflow.
7. Check main homepage, blog archive and an existing article after deployment.

## Rollback

Revert the release commit through the normal repository/Render deploy. The original answer-service deployment and data have not been changed, so prior service availability is retained. Do not reset unrelated work or force-push.
