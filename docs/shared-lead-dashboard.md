# Shared lead dashboard

The private `/admin/dashboard` and `/admin/mission-control` views read the same saved records as `GET /api/mission-control/leads`. Website, ManyChat keyword, and RefiWatch records remain in their existing tables; the read model combines them without duplicating or resending leads.

The API requires `Authorization: Bearer <read-only token>`. Set `MISSION_CONTROL_LEADS_TOKEN` to an independent secret, or derive the token as hex HMAC-SHA256 with the existing `MANYCHAT_WEBHOOK_SECRET` as the key and the literal string `mission-control-leads:v1` as the message. Mission Control stores only this scoped token in its server environment as `DRMORTGAGE_LEADS_TOKEN`. It never receives the webhook secret. The token does not authorize admin routes or webhook writes. Rotate the explicit token or source secret to revoke access.

Query parameters: `search`, `segment`, `source`, `channel` (`website`, `manychat`, `refiwatch`), `status` (`sent`, `pending`), `messages=1`, and `page` (50 records per page). Responses and private admin pages are `private, no-store`. Every refresh reads the source database; no synchronization cache can drift from the website. ManyChat records show “Not routed through Zapier,” because this webhook saves leads and does not send messages or forward to a CRM. RefiWatch delivery attempt history is not available in its old schema.

## ManyChat flow capture

In each lead-generating Instagram automation, configure a POST External Request to `https://drmortgageusa.com/api/manychat/enroll`. Use `Content-Type: application/json` and `X-Webhook-Secret` with the existing secret. Legacy `secret` in the JSON body is supported but is never saved.

Map the actual ManyChat fields using its variable picker, and enable Encode to JSON for text values. Send the first request after the contact opts in, then another after captured replies/contact details become available. Required: `subscriber_id`. Map `keyword` explicitly (legacy default is `5DAYS`). Recommended fields:

- `name`, `ig_username`, `email`, `phone`
- `message`: the captured reply/custom user field; not a hardcoded prompt
- `answers` or `custom_fields`: captured structured answers
- `campaign`, `flow_id`, `flow_name`, `post_id`, `ad_id`, `event_id`
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`
- `emailConsent`, `callConsent`, `smsConsent` only if actually collected

An ordinary Send Message asking someone to reply does not itself map that reply to this webhook. Add a ManyChat Data Collection step and save the answer to a custom user field before sending it. Existing free-form inbox conversations cannot be recovered from fields the webhook never received.

The webhook upserts on subscriber + keyword, preserving existing contact details when omitted in later requests. The same person using different keywords receives separate records. A database failure returns 503 and never falsely reports successful enrollment. Repeated deliveries of the same subscriber/keyword do not create additional leads. The `processed` flag is the existing downstream follow-up status, not proof that a particular message was delivered.

Official ManyChat instructions: https://help.manychat.com/hc/en-us/articles/14281285374364-Dev-Tools-External-request
