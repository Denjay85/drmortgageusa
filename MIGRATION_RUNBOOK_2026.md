# DR. Mortgage USA 2026 Migration Runbook

## Migration architecture

The redesigned site is stored in `site/` and exported to `site/dist/client/`.
The existing Flask application remains the production host and backend.

This preserves the current operational systems:

- Render hosting and PostgreSQL
- Cloudflare DNS, TLS, and proxying
- Zapier lead handoff to Bonzo
- Meta Pixel and Meta Conversions API
- Google Ads application, phone, and lead conversions
- ManyChat webhook and sequence endpoints
- RefiWatch lead endpoint
- Automated mortgage and DPA rate updates
- Existing blog publishing workflow
- Existing application URL
- Existing service and blog URLs

## Lead flow

1. A visitor submits Contact, Build My Plan, DPA review, or Rate Watch.
2. The browser creates one event ID and sends it with the scenario and consent choices.
3. Flask validates the submission.
4. PostgreSQL stores the contact, source, consent choices, event ID, and full JSON payload.
5. Flask forwards the same payload to the configured Zapier catch hook.
6. Zapier sends the mapped lead into Bonzo.
7. The browser fires the Meta Lead event with the event ID.
8. Flask sends the matching Meta CAPI Lead event with the same event ID.
9. Meta can deduplicate the browser and server events.

If Zapier is temporarily unavailable, PostgreSQL still stores the lead and marks it for delivery. `/admin/integrations` reports readiness and the queued lead count without exposing credentials. After `ZAPIER_WEBHOOK_URL` is configured, an authenticated `POST` to `/admin/retry-zapier` replays queued website leads and records each delivery attempt.

## Required Render secrets

Set or rotate these values in the Render service before staging a production-like form test:

- `ADMIN_PASSWORD`
- `ZAPIER_WEBHOOK_URL`
- `MANYCHAT_API_KEY`
- `MANYCHAT_WEBHOOK_SECRET`
- `META_CONVERSIONS_API_TOKEN`
- `META_TEST_EVENT_CODE` during testing only
- `GA_MEASUREMENT_ID` if GA4 is used
- `GTM_CONTAINER_ID` if Google Tag Manager is used

These values must remain in Render. They must not be committed to GitHub.

The website can operate while `ZAPIER_WEBHOOK_URL` is missing. Leads remain visible in the protected admin dashboard and can be replayed after the Bonzo workflow is restored. ManyChat endpoints remain unavailable until both ManyChat values are rotated and configured.

## Bonzo integration validation

On July 13, 2026, the replacement Zapier catch hook accepted a labeled synthetic website lead and returned HTTP 200 with a Zapier success receipt. The payload included the same contact, mortgage scenario, source, event ID, and channel consent fields sent by the redesigned forms. No real borrower information was used.

The hook is stored as the masked `ZAPIER_WEBHOOK_URL` secret on the production Render service using Save only. It will become active when the migration branch is deployed. Saving the secret did not restart the current production service.

Before launch, Gabi or another Bonzo administrator must confirm that the labeled test record is visible in Zapier and finish the Zapier to Bonzo field mapping. Then run one end-to-end synthetic submission and verify these exact outcomes:

- Zapier receives the website payload.
- Bonzo creates or updates the expected test contact.
- The source and mortgage scenario fields remain attached.
- Email, call, and SMS consent remain separate.
- A duplicate submission with the same test contact follows the intended Bonzo update rule.
- Failed Zapier delivery leaves the lead queued in PostgreSQL for authenticated replay.

Do not replay queued production leads until the Bonzo workflow is active and a Bonzo administrator confirms the destination and duplicate-handling rules.

## Staging checklist

- Deploy `migration/2026-redesign` as a separate Render preview service.
- Render sets `IS_PULL_REQUEST=true` on the temporary preview instance.
- Preview mode blocks database access, Zapier delivery, Meta CAPI, Meta Pixel, and Google Ads.
- Preview form submissions return a test success response without persisting or forwarding contact information.
- Keep staging pages set to `noindex, nofollow`.
- Confirm all calculator inputs work on desktop and mobile.
- Confirm all 49 current blog cards load from `/api/blog`.
- Confirm every existing blog article URL returns 200.
- Confirm the DPA tracker reads the official source or the verified fallback.
- Confirm Build My Plan keeps purchase questions out of refinance and home equity flows.
- Confirm the application shortcut opens the secure 1003 URL.
- Confirm the preview tracking script does not load Meta or Google advertising scripts.

Production-like delivery tests happen only after the preview interface is approved. Use a dedicated Zapier test hook and Meta Test Events before the final production cutover. Confirm one labeled lead reaches Bonzo, Google Ads or GTM receives the expected conversion, and Meta shows deduplicated browser and server Lead events.

## SEO checklist

- Build the final export with `NEXT_PUBLIC_INDEXABLE=true`.
- Confirm canonical URLs use `https://drmortgageusa.com`.
- Confirm `robots.txt` references the production sitemap.
- Confirm the sitemap contains redesigned routes, service pages, and every blog article.
- Keep the current service and blog paths unchanged.
- Submit the updated sitemap in Google Search Console after launch.
- Monitor 404s, indexed pages, Core Web Vitals, and search traffic after launch.

## Cutover

No DNS change is required when the redesign is deployed through the existing Render service.

1. Merge the approved migration branch into `main`.
2. Build and commit the final indexable static export.
3. Verify required Render secrets.
4. Deploy from `main`.
5. Run the smoke tests against the public domain.
6. Submit one labeled test lead and verify Postgres, Zapier, Bonzo, Meta, and Google Ads.
7. Remove the Meta test event code after validation.

## Rollback

The live site is unchanged until the migration branch is merged and deployed.
If the production smoke test fails, use Render to roll back to the previous successful deploy.
The previous Flask HTML remains in the repository and is used automatically if the redesign export is absent.
