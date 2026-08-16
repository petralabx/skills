---
id: cos-close-ticket
title: COS Close ticket
sop: docs/UAT-SOP-Customer-Portal.md#72
module_readme: docs/modules/agents/README.md
happy_path:
  - CS-27
  - COS-CLOSE-01
  - COS-CLOSE-02
  - COS-CLOSE-03
skip: []
viewport_surfaces:
  - route: /mrp/project-development
    viewports: [desktop, tablet, mobile]
spatial_cases:
  - CS-27
  - COS-CLOSE-01
api_paths:
  - /api/agents/chief-of-staff/chat
---

# Pack — COS Close ticket (TASK-1051)

Projected from live UAT-SOP §72 CS-26/CS-27 and §73 COS-PATH-A-04 /
COS-CLOSE-01..03 / COS-RECENTS-02 / COS-FINALIZE-01, plus the agents
module contract for `PATCH /api/agents/[agentId]/threads/[threadId]`
`{ action: "close" }`. Do not invent extra SOP IDs.

Host: `https://staging.plxcustomer.io` only. Require deploy SHA
`e2e11e1ed1984c07337771c2ba15913f4e6b5d70` (PR #677) or a later
staging SHA that contains that merge. Live app reads `plx-postgres-uat`.

Program (do not invent features):

- Chief of Staff seal + panel on any authenticated MRP page
  (prefer `/mrp/formulations`)
- Close means stop this **chat draft**. It does not delete a filed
  Feedback row.
- **Close ticket** lives in thread chrome next to **Start new ticket**.
- **Dismiss** lives on the Home / UAT unfinished-draft card.
- Close must: stop voice and dictation; mark gold Triple-T
  `ACTIVE`/`READY` as `ABANDONED`; set `AgentThread.status` to
  `ARCHIVED`; clear last-thread resume; return to Home with no
  unfinished card.
- Recents may still list the row as **Closed**. It must not
  auto-resume or keep asking for a clip.
- **Start new ticket** still leaves an unfinished draft in Recents
  (CS-26 / COS-PATH-A-04). That is a pass, not a close defect.
- Call it a ticket only when a Feedback row exists; until then it is
  a draft. Copy tightening is not a FAIL unless the SOP expected
  result is missing.
- Do not change Hasitha Path A/B/C attach or finalize. Do not flip
  `NEXT_PUBLIC_COS_ASSISTANT_UI`. Do not set
  `COS_SUGGEST_NAVIGATE_ENABLED=0` on shared staging.

Fixture: staff-owned Path A draft created in this run (UAT-prefixed
composer text). Prefer an existing filed ticket the agent account
owns for COS-CLOSE-03. Do not delete Feedback. Do not mutate another
operator's threads.

## Cases

| ID | Name | Expected |
|---|---|---|
| CS-26 | Unfinished draft vs Start new ticket | Leave a Medium+ Path A draft without a clip. Close and reopen COS. Panel stays on the menu with an **Unfinished ticket** card (**Continue draft** / **Start new ticket**). **Start new ticket** opens a clean intake thread; the old draft remains under Recents. Reopening COS does not trap you back into the old thread |
| CS-27 | Close ticket / Dismiss stops the draft | Leave a Medium+ Path A draft without a clip. From Home choose **Dismiss**, or open the draft and choose **Close ticket**. Voice and dictation stop. The unfinished card is gone. Recents may still list the row as **Closed**. Reopening COS does not auto-resume or ask for a clip. A filed `/uat` ticket (if one existed) is still listed |
| COS-RECENTS-02 | Offer unfinished Path A after Clips | Start Medium+ Path A until the Path A control appears. Close the COS panel. Reopen the seal without clicking Recents. Panel stays on the menu with an **Unfinished ticket** card, or the same offer on the UAT tab. **Continue draft** restores Path A Attach / Open Clips |
| COS-PATH-A-04 | Start new ticket leaves draft in Recents | With an unfinished Path A draft, choose **Start new ticket** (Home card or thread chrome). Describe a different issue and send. Close and reopen COS. A new thread starts. The prior unfinished draft remains under Recents. Reopening COS offers the old draft but does not force-open it |
| COS-CLOSE-01 | Close ticket from thread chrome | Open an unfinished Path A draft. Choose **Close ticket** next to **Start new ticket**. Panel returns to Home. The unfinished card is gone. Recents may show the row as **Closed**. Reopen does not auto-resume or ask for a clip |
| COS-CLOSE-02 | Dismiss unfinished card | With the Home or UAT **Unfinished ticket** card visible, choose **Dismiss**. Same as COS-CLOSE-01. **Start new ticket** on that card still leaves the draft in Recents (COS-PATH-A-04) |
| COS-CLOSE-03 | Filed Feedback stays listed | File a ticket (COS-FINALIZE-01) or use an existing owned filed row. Then close any leftover draft and open `/uat` or COS → UAT. The filed Feedback row is still listed. Close never deletes a ticket |
| COS-FINALIZE-01 | Affirmation creates Feedback row | Precondition for COS-CLOSE-03 when no owned filed row exists. Complete Medium+ intake until ready. Reply **yes**. A new row appears under Your UAT tickets / My tickets. Conversation is FINALIZED with a non-null `feedbackId` |

## Dimensions

### Use-cases

| ID | Check |
|---|---|
| UC-01 | Happy path CS-27, COS-CLOSE-01, COS-CLOSE-02, COS-CLOSE-03 |
| UC-02 | CS-26 / COS-PATH-A-04 still hold after Close exists: Start new does not close the old draft |
| UC-03 | COS-RECENTS-02 still offers an open Path A draft (not a closed one) |

### Edge-cases

| ID | Check |
|---|---|
| EX-01 | Double **Close ticket** / **Dismiss** — idempotent 200; no 500; still no unfinished card |
| EX-02 | `PATCH` with `{ action: "delete" }` or missing action — 400; thread stays open |
| EX-03 | Close an `ACTIVE` Path A draft — gold becomes `ABANDONED`; mirror `ARCHIVED`; `feedbackId` stays null |
| EX-04 | Close a `READY` draft — gold becomes `ABANDONED`; no Feedback row created |
| EX-05 | Close after COS-FINALIZE-01 — gold stays `FINALIZED`; `feedbackId` unchanged; `/uat` still lists the ticket |
| EX-06 | Send on a closed thread — chat 409 / closed banner; no new Path A card |
| EX-07 | Resume a Closed Recents row — read transcript is allowed; Path A attach card stays hidden; banner says the draft is closed |
| EX-08 | Close while Voice Path A is listening / transcribing — mic stops; no leftover Transcribing state |
| EX-09 | Close while Voice Path B session is Listening — session tears down; no further turns land on the closed thread |
| EX-10 | Close does not attach, clear, or rewrite `clipUrl` / screenshot on another open draft |
| EX-11 | Owner scope: another user's thread id returns 404; no status change |
| EX-12 | Closed draft is excluded from unfinished-offer selection even if Recents still shows it |
| EX-13 | Hard refresh after Dismiss — unfinished card stays gone; last-thread resume does not reopen it |

### Workflow-loop E2E

| ID | Check |
|---|---|
| WL-01 | Open Path A draft → panel close → reopen → unfinished card → **Close ticket** → Home clean → Recents Closed → reopen COS still clean |
| WL-02 | Open Path A draft → **Start new ticket** → old draft still offered → **Dismiss** → offer gone → Recents Closed |
| WL-03 | Finalize a ticket → leftover draft close → `/uat` still lists the filed row → COS UAT tab still lists it |

### Speed

Classes from `references/SPEED-BUDGET.md`. Do not invent a number.

| ID | Metric | Class |
|---|---|---|
| SP-01 | Close ticket round trip (click to Home with no unfinished card) | Write (2000 ms, max of 5 warm) |
| SP-02 | Recents refresh after close shows Closed | Chrome (candidate — score BLOCKED, reason `chrome budget is candidate`) |

### UI/UX

| ID | Check |
|---|---|
| UX-01 | **Close ticket** is visible in thread chrome next to **Start new ticket** and does not scroll away (CS-23 chrome) |
| UX-02 | **Dismiss** is visible on the unfinished card with **Continue draft** and **Start new ticket** |
| UX-03 | Closed Recents meta says **Closed**, not **Path A — attach clip** |
| UX-04 | After close, no Path A "Open Clips" / attach loop on Home |
| UX-05 | Validation / close errors are inline; no raw 500 page |
| UX-VP-desktop | Required when the named PR stamps `Surface-change: yes`. Close ticket chrome at 1440 x 900 |
| UX-VP-tablet | Same at 834 x 1112 |
| UX-VP-mobile | Same at 390 x 844. Seal must not cover Close ticket / Dismiss |

### API

| ID | Class |
|---|---|
| API-AUTH | Required when `Api-change: yes`. Close / chat without cookie is 401 |
| API-CONTRACT | STAFF close payload is documented JSON |
| API-ERROR | Invalid close returns JSON, not HTML 500 |

### Security

| ID | Class |
|---|---|
| SEC-HOST | Required when `Security-change: yes`. Host is staging |
| SEC-AUTHN | No session → 401 |
| SEC-AUTHZ | Cannot close another owner's thread |
| SEC-SECRETS | Evidence has no secret |
| SEC-ISOLATION | Other-owner thread is 403/404, or BLOCKED `no isolation fixture` |
