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

Evidence hygiene (independent-verify will deduct below 8 if these fail):

- Do not point UC-01 at `RESULTS.json`. Write a dedicated happy-path
  proof that lists each ID and its per-case file.
- Do not reuse one HTML fetch as proof for four rows. Separate GET +
  file per case.
- EX-18 must probe live launch hrefs and the live Teams allowlist
  bundle. An unconfigured card is not that check. There is no write
  API for `Project.customFields` Teams links.
- UI/UX PASS rows need a screenshot as well as API/HTML proof.
- Party-filter PASS must show the filtered ID sets differ.
- Sourcing vendors come from `GET /api/mrp/sourcing-requests/vendors`
  (Prisma `Supplier`). Do not use `/api/mrp/suppliers/search` (FM
  replica ids fail "active approved Supplier").
- Sample RECEIVED/ACCEPTED updates must send `sampleId` from the
  REQUESTED row. Linked product id is `linked_product_id`.
- BCOM-28-mock: live `/outlook-pin` is VITE live mode. Without Outlook,
  only the office-context error is reachable. Score honest BLOCKED; do
  not PASS from a source grep of the five pane states.

## 4. Mail and MIME

If a pack sends mail, From must be the approved ops path
(`plx-graph-mail` / `email-theme`). Prefer a draft or an internal-only
recipient (`cos@` / `vince@`). Never email a real vendor. Never POST
message body / HTML / MIME / attachment bytes to a PLX API.

## 5. Teams and Outlook

Do not file "in-portal Teams chat missing" as a bug unless the pack
says chat exists. Outlook live pin may be BLOCKED until tenant NAA.
The hosted `/outlook-pin` build on staging is live-mode; the five
mock pane states are not a live-alias PASS.
