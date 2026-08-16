---
id: cos-p3-retrieve
title: COS Phase 3 retrieve grounding
sop: docs/UAT-SOP-Customer-Portal.md#83
module_readme: docs/modules/agents/README.md
happy_path:
  - CTX-NAV-01
  - CTX-NAV-09
  - CTX-NAV-04
  - KH-04
  - KH-11
skip:
  - CTX-NAV-07
viewport_surfaces:
  - route: /mrp/project-development
    viewports: [desktop, tablet, mobile]
  - route: /admin/knowledge
    viewports: [desktop, tablet, mobile]
spatial_cases:
  - CTX-NAV-04
  - KH-11
  - EX-05
api_paths:
  - /api/agents/chief-of-staff/chat
  - /api/admin/knowledge/articles
---

# Pack — COS Phase 3 retrieve grounding (TASK-1049 / PR #676)

Projected from live UAT-SOP **§83** (CTX-NAV-01..09) and **§27B** (KH-04,
KH-05, KH-11). Agents module contract: default COS seed stays
`readPolicy: "namespace"` / `writePolicy: "none"`; empty retrieve must
not invent citations; intake, tickets, and `suggestNavigate` still run.
Do not invent extra SOP IDs.

Host: `https://staging.plxcustomer.io` only. Require deploy SHA
`8c71f6edc3a16d24fb9215dc7b1276a013edc71b` (PR #676) or a later
staging SHA that contains that merge. Live app reads `plx-postgres-uat`.
No Prisma migration in this slice.

Program (do not invent features):

- Chief of Staff seal + panel on any authenticated MRP page. SOP names
  `/mrp/formulations` **or another known MRP route**. Prefer
  `/mrp/project-development` if formulations 404s for STAFF.
- Typed Send is the retrieve call site. Finalize / lookup / evidence
  paths skip retrieve.
- Default COS namespace does **not** include Hub how-tos. Asking a
  company-graph fact COS should not know must still get a reply, with
  no invented how-to id and no Hub citation that was not retrieved
  (CTX-NAV-09).
- Page-context answers still name the current area (CTX-NAV-01).
- `suggestNavigate` still offers confirm-before-navigate (CTX-NAV-04).
- Hub Ask at `/admin/knowledge` is a **negative** check: this PR must
  not change KH-04 / KH-11. Click a seed hit; **The page** still shows
  full markdown, not title + id + snippet.
- Do not special-case `chief-of-staff` in retrieve. Do not bump COS
  `readPolicy` to `global`. Do not start D5 / `KH_*`.
- Do not set `COS_SUGGEST_NAVIGATE_ENABLED=0` on shared staging
  (CTX-NAV-07 is skip).
- Mission Control Ask (`mc.plxcustomer.io/?screen=brain-ask`) is
  **out of this harness**. Wrong host.

Fixture: staff-owned COS thread created in this run. Use a phrasing
question, not finalize / lookup / evidence. Do not file a UAT ticket
unless CTX-NAV-09 ticket-lookup proof needs an existing owned row.
Do not mutate another operator's threads.

## Cases

| ID | Name | Expected |
|---|---|---|
| CTX-NAV-01 | Typed page context | Open `/mrp/formulations` (or another known MRP route). Open COS. Type **What is this page / module?** and Send. Reply names the current area / route. It does not invent a record id |
| CTX-NAV-02 | Voice Path A shares pageContext | On the same route, Voice Path A: dictate the same question, review, then Send. Transcript does not auto-send. After Send, the answer matches CTX-NAV-01. Still one chat turn. N/A if voice flag off |
| CTX-NAV-03 | Voice Path B shares pageContext | Opt into Voice Path B. Speak the same question as one final. One final becomes one `chat.ask`. Answer matches CTX-NAV-01. COS replies stay text-only. N/A if voice flag off |
| CTX-NAV-04 | Confirm-before-navigate | Ask **take me to purchase orders**. Confirm. Main view opens `/mrp/purchase-orders`. Thread does not add a second user turn |
| CTX-NAV-05 | Cancel does not navigate | Repeat CTX-NAV-04 on a different starting route. Cancel. Route does not change. Card disappears. Thread stays intact |
| CTX-NAV-06 | Role miss is visible | As STAFF ask **take me to admin agents**. No working navigation target. An error / notice is visible. The thread does not break |
| CTX-NAV-08 | Voice + confirm is not a turn | After a Voice Path B final that offers navigate, Confirm. Navigation happens. No extra `chat.ask`. N/A if voice flag off |
| CTX-NAV-09 | Retrieve grounding, no invented citations | As STAFF, on a route with no matching COS namespace how-to, ask a company-graph fact COS should not know. Chat still answers. It does not invent a how-to id or cite a Hub article that was not retrieved. Ticket lookup and suggestNavigate still work |
| KH-04 | Ask — in corpus | On `/admin/knowledge` Ask, search a term from a known guide title (e.g. `receiving`). Matching seed hits returned |
| KH-05 | Ask — abstain + gap | Search `qzxqzxqzx`. Abstain message. Do not use `zz-no-such-topic-973` |
| KH-11 | Ask — open full article | On Ask, search an in-corpus term (KH-04). Click a seed hit. **The page** shows title, provenance chips, and full markdown (not title + id + snippet). Search results stay visible |

## Dimensions

### Use-cases

| ID | Check |
|---|---|
| UC-01 | Happy path CTX-NAV-01, CTX-NAV-09, CTX-NAV-04 |
| UC-02 | Hub negative: KH-04 then KH-11 still open full markdown |
| UC-03 | After CTX-NAV-09, ticket lookup and suggestNavigate still work (same expected result as CTX-NAV-09) |

### Edge-cases

| ID | Check |
|---|---|
| EX-01 | Nonsense / out-of-namespace question still streams a reply (CTX-NAV-09). No invented Hub how-to id |
| EX-02 | Invalid `pageContext` object is ignored; the turn still runs (module contract) |
| EX-03 | Finalize / lookup / evidence phrasing is skipped for retrieve (module contract). A lookup turn does not attach retrieve hits |
| EX-04 | KH-05 abstain `qzxqzxqzx` still abstains after this deploy |
| EX-05 | STAFF Hub Ask KH-11 close returns to search; results remain |
| EX-06 | No `if (slug === "chief-of-staff")` behavior: retrieve uses `knowledgeReadAllowed` only |

### Workflow-loop E2E

| ID | Check |
|---|---|
| WL-01 | Open MRP page → COS → CTX-NAV-01 → CTX-NAV-09 on the same thread → reply still has no invented citation → CTX-NAV-04 confirm navigates |
| WL-02 | Hub Ask KH-04 → KH-11 open **The page** → close → search still listed |
| WL-03 | CTX-NAV-05 cancel after a retrieve turn: route unchanged; thread intact |

### Speed

Classes from `references/SPEED-BUDGET.md`. Do not invent a number.

| ID | Metric | Class | Clock |
|---|---|---|---|
| SP-01 | COS typed Send to first SSE `delta` | Stream (2000 ms, max of 5 warm) | `POST /api/agents/chief-of-staff/chat` start to first parsed `data:` frame with `type=delta`. Not time-to-complete reply. |
| SP-02 | Hub Ask click to **The page** body | Fetch (1000 ms, max of 5 warm) | Pack allows API stand-in: `GET /api/admin/knowledge/articles?id=guide:prod-receiving` start to JSON with `markdown` longer than 280 chars. A fast GET does not replace KH-11 UI proof. |

### UI/UX

| ID | Check |
|---|---|
| UX-01 | COS seal / panel still opens on the chosen MRP route (CS-01 / CS-03 chrome from §72 as precondition, not a new ID) |
| UX-02 | CTX-NAV-09 reply has no fake how-to chip or invented article title |
| UX-03 | Hub **The page** is full markdown with provenance chips, not a snippet card |
| UX-04 | Validation / chat errors are inline; no raw 500 page |
| UX-VP-desktop | Required when the named PR stamps `Surface-change: yes`. Primary surfaces at 1440 x 900 |
| UX-VP-tablet | Same surfaces at 834 x 1112. No hover-only primary action |
| UX-VP-mobile | Same surfaces at 390 x 844. Seal must not cover Close article / Confirm |

### API

Required when the named PR stamps `Api-change: yes`. Latency uses Stream / Fetch.

| ID | Class |
|---|---|
| API-AUTH | No cookie → 401 on chat and Hub article |
| API-CONTRACT | STAFF 200. Documented fields. No FM table. No invented Hub id |
| API-ERROR | Invalid or forbidden call returns JSON, not HTML 500 |

### Security

Required when the named PR stamps `Security-change: yes`. Defensive only.

| ID | Class |
|---|---|
| SEC-HOST | proof.host is staging.plxcustomer.io |
| SEC-AUTHN | Staff API without session is 401 |
| SEC-AUTHZ | STAFF denied on an ADMIN-only action, or no working admin navigate |
| SEC-SECRETS | Evidence has no password, token, or DB URL |
| SEC-ISOLATION | Other-customer record is 403/404, or BLOCKED `no isolation fixture` |
