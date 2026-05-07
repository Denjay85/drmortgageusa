# Google Ads Conversion Tracking Deployment, 2026-05-07

## Account

- Google Ads account: `123-887-8598`
- Google tag ID: `AW-18055212874`
- Campaign remains unpublished.

## Conversion actions

| Site event | Google Ads conversion action | Category | Env var | Value |
| --- | --- | --- | --- | --- |
| Secure application click | Apply click | Request quote | `GOOGLE_ADS_APPLY_CONVERSION_LABEL` | `ZoE7CPuPg6kcEMresqFD` |
| Phone link click | Phone click | Contact | `GOOGLE_ADS_PHONE_CONVERSION_LABEL` | `pIxfCP6Pg6kcEMresqFD` |
| Successful lead form submit | Submit lead form | Submit lead form | `GOOGLE_ADS_LEAD_FORM_CONVERSION_LABEL` | `90H9CJrk-agcEMresqFD` |

Base tag env var:

```bash
GOOGLE_ADS_ID=AW-18055212874
```

## Deployment env vars

These are already added to `render.yaml` for Render Blueprint deploys:

```bash
GOOGLE_ADS_ID=AW-18055212874
GOOGLE_ADS_APPLY_CONVERSION_LABEL=ZoE7CPuPg6kcEMresqFD
GOOGLE_ADS_PHONE_CONVERSION_LABEL=pIxfCP6Pg6kcEMresqFD
GOOGLE_ADS_LEAD_FORM_CONVERSION_LABEL=90H9CJrk-agcEMresqFD
```

If deploying outside Render, set the same four environment variables in that host before restart.

## Implementation notes

- `/site-tracking.js` loads Google Ads through `GOOGLE_ADS_ID` only when configured.
- Existing Meta Pixel and Meta CAPI paths are preserved.
- `GTM_CONTAINER_ID` still takes precedence if a GTM container is later configured.
- Lead conversion events fire only after `/api/quiz-submit` returns a successful response.
- Click events are bound to:
  - `a[href*="my1003app.com"]` for application clicks
  - `a[href^="tel:"]` for phone clicks
- GTM-ready dataLayer events are pushed:
  - `dr_apply_click`
  - `dr_phone_click`
  - `dr_lead_form_submit`
  - `dr_secondary_landing_view`

## Pre-launch verification

After deployment, verify with Google Tag Assistant before publishing the campaign:

1. Open `https://drmortgageusa.com/` in Tag Assistant.
2. Confirm Google tag `AW-18055212874` loads.
3. Click a secure application link and confirm conversion send_to includes `AW-18055212874/ZoE7CPuPg6kcEMresqFD`.
4. Click a phone link and confirm conversion send_to includes `AW-18055212874/pIxfCP6Pg6kcEMresqFD`.
5. Submit a test lead through the quiz or lead form and confirm conversion send_to includes `AW-18055212874/90H9CJrk-agcEMresqFD` only after the API succeeds.
6. Confirm no conversion fires on page load except the base Google tag config.
7. Return to Google Ads Diagnostics and confirm tag activity changes from misconfigured/inactive after Google receives traffic.

## Launch guardrail

Do not click `Publish campaign` until conversion tracking is verified and Dennis gives explicit launch confirmation.
