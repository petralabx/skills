# Deployed-PR E2E — Reference

## 1. Host and proof

Canonical host is `https://staging.plxcustomer.io`. The skill script
`scripts/assert-exact-staging-deploy.mjs` queries the Vercel alias and
writes a proof object:

```json
{
  "ok": true,
  "host": "https://staging.plxcustomer.io",
  "sha": "<40 hex>",
  "deploymentId": "dpl_...",
  "aliasCheckedAt": "<ISO-8601>"
}
```

Wrong host, missing Vercel token, or pin mismatch is a STOP. Do not
fall back to `assert-staging-deploy-safe.mjs` as the matrix.

In the portal repo, `scripts/persona-qa/assert-exact-staging-deploy.mjs`
is a stricter pin-first helper used by Persona QA. This skill's script
is **resolve-then-record** (optional pin). Do not treat Persona QA as
the matrix.

## 2. Fixture

Prefer an existing sandbox / UAT-prefixed PD project. Record
`projectId`, project number, customer. Do not mutate a live customer
flagship project. If none is safe, create the smallest staff-owned
test project and say so.

## 3. Evidence layout

```text
artifacts/deployed-pr-e2e/<yyyy-mm-dd>/
  RESULTS.md
  RESULTS.json
  proof.json
  <case-id>-*.png
```

`RESULTS.json` rows must include `id`, `result`, `url`, `evidence`,
`notes`. PASS requires a non-empty `evidence` path or `httpProof`.

Speed rows follow [references/SPEED-BUDGET.md](references/SPEED-BUDGET.md).
Packs name a class. Record the deploy SHA next to timings. The UAT
statistic is max of 5 warm runs after one discarded warmup.

Viewport rows follow [references/UX-VIEWPORT.md](references/UX-VIEWPORT.md).
If a PR is named, parse harness stamps first. Missing `Surface-change:`
is a STOP. `yes` incorporates UX-VP-desktop / tablet / mobile.
`Api-change: yes` incorporates API-AUTH / CONTRACT / ERROR
([API-CONTRACT.md](references/API-CONTRACT.md)).
`Security-change: yes` incorporates SEC-*
([SECURITY.md](references/SECURITY.md)). Defensive only.
Do not infer a change from SOP prose.

## 4. Mail and MIME

If a pack sends mail, From must be the approved ops path
(`plx-graph-mail` / `email-theme`). Prefer a draft or an internal-only
recipient (`cos@` / `vince@`). Never email a real vendor. Never POST
message body / HTML / MIME / attachment bytes to a PLX API.

## 5. Teams and Outlook

Do not file "in-portal Teams chat missing" as a bug unless the pack
says chat exists. Outlook live pin may be BLOCKED until tenant NAA;
mock path is an honest BLOCKED/PASS per the pack, not a product FAIL.
