# Company API contract

Canonical for every `deployed-pr-e2e` pack. Packs name paths.
They do not invent a latency number. Latency reuses
[SPEED-BUDGET.md](SPEED-BUDGET.md) (Stream / Fetch / Write).

Adopted 2026-08-16.

## Gate

| Rule | Value |
|---|---|
| Host | `https://staging.plxcustomer.io` only |
| Actor | STAFF session unless the row is Auth |
| Fail | Wrong status, missing documented field, HTML 500, or FM-table leak |
| Kind | Single-user UAT. Not a load test. Not production p75. |
| Proof | Status + JSON keys in `httpProof`. Record the deploy SHA. |

Do not run every SOP case against every route. The PR stamp or the
pack `api_paths` list names the paths.

## Classes

| Class | Gate | Status |
|---|---|---|
| Auth | No cookie → 401. Wrong role → 403. STAFF on a staff path → 200 | Adopted |
| Contract | Documented fields present. No FM replica table in the payload. No invented Hub id | Adopted |
| Error | JSON error object with a message. No HTML 500 page | Adopted |
| Latency | Use Stream / Fetch / Write from the speed table | Adopted (do not add a fourth millisecond) |

## PR stamp

```text
- Api-change: yes
- APIs: /api/agents/chief-of-staff/chat, /api/admin/knowledge/articles
```

`no` when the PR does not change a staff API. Empty `APIs` on `yes`
means use the pack `api_paths` list. Missing `Api-change:` on a named
PR is a STOP (same as Surface-change).

Optional label: `api-change`.

## Required rows when `Api-change: yes`

| ID | Class |
|---|---|
| API-AUTH | Auth on each listed path |
| API-CONTRACT | Contract on each listed path (STAFF) |
| API-ERROR | Error: one invalid or forbidden call returns JSON, not HTML |

A fast GET does not PASS a missing field. A 200 with an FM table name
in the payload is FAIL.

## Pack frontmatter

```yaml
api_paths:
  - /api/agents/chief-of-staff/chat
  - /api/admin/knowledge/articles
```
