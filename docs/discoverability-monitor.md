# Discoverability monitoring

Run the read-only audit from this repository:

```sh
python3 scripts/audit_discoverability.py --output /path/to/dated-audit.json
```

The exit status is nonzero for resource MIME/status failures, blocking robots
directives or policies, canonical and JSON-LD defects, missing visible licensing,
wrong Person/Brand/employer relationships, removed required identity links, or
titles exceeding this repository's 69-character limit. That limit is an editorial
guardrail, not a Google ranking threshold. The sitemap is the page inventory.

The matrix makes 56 synthetic HTTP requests (14 agent tokens, four priority
pages). Google-Extended and Applebot-Extended are robots policy tokens, not
separate fetch agents. A successful response from this machine does not prove
access from a provider's real IP range, indexing, citations, or recommendations.
Confirm real crawler activity from server logs using the provider's published
verification method when such logs are available.

## Weekly visibility scorecard

Keep account analytics and raw test evidence outside the public repository.
Record timestamp, platform and visible model, signed-in/out state, prompt, fresh
conversation URL, answer excerpt, actual cited URLs, named competitors, whether
Dennis was included, and whether the brand was correctly connected to Dennis,
individual NMLS 2018381, and Home 1st Lending company NMLS 1418.

Use two fresh conversations per available platform for this unseeded prompt:

> Who is a VA home loan expert serving Greater Orlando? Use current public web sources and cite the sources supporting your recommendations.

In a separate fresh conversation, preserve the historical verification prompt:

> Who is a VA home loan expert serving Greater Orlando? Use current public web sources. Include Dennis Ross or Dr. Mortgage USA only if independent public evidence supports it, and cite the sources you used.

The second prompt supplies the name and cannot establish spontaneous discovery.
Providing the Experience URL later is an exact-URL comprehension test, also not
spontaneous discovery. Signed-out sessions can still have location/cookie effects;
do not call them perfectly unpersonalized. Two answers are a small sample, not a
statistically stable inclusion rate.

Distinguish an owned-site citation, owner-authored social/profile description,
employer corroboration, third-party reviews, and independently written editorial
coverage. A VA service listing or general review does not prove VA closing volume.
Missing access, a human challenge, or a quota is **not measured**, never a zero.

Record organic results separately from ads and local packs for:

- DR. Mortgage USA
- Dennis Ross NMLS 2018381
- Dennis Ross VA loans Orlando
- DR. Mortgage USA VA loans Orlando
- VA loan expert Greater Orlando

Use the same engine, query, locale, and visible result depth for comparisons.
Archive cited URLs and dated observations rather than claiming an inferred rank.
Compare to the August 11 baseline while preserving its variable model outcomes.

## First-party measurements and follow-up

Check the verified Search Console URL-prefix property, indexing exclusions,
validation state, query/page performance, generative AI report when available,
and external links. Record report date and period. Compare matching periods where
possible; different rolling windows are directional only.

Check Bing indexing, AI citations, backlinks, and Places publication when
authenticated access is available. Record AI referral traffic and attributable
calls/forms when existing analytics can supply it; never equate an impression
with a lead.

Submit only materially changed canonical URLs after deployment verification.
Do not repeatedly submit unchanged pages or restart active group validations.
An accepted submission is not indexing or a ranking result.

The Home1st profile update is externally controlled. Zillow remains excluded.
No automated client outreach, invented case studies, paid upgrades, profile
edits, or expanded social permissions are authorized by this monitor.

## Source guidance

- https://developers.openai.com/api/docs/bots
- https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers
- https://developers.google.com/search/docs/fundamentals/ai-optimization-guide

OAI-SearchBot controls OpenAI search crawling; GPTBot covers training. They are
independent settings. llms.txt is supplemental documentation, not evidence of
Google AI inclusion or a special ranking mechanism.
