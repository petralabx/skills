---
id: bom-comms
title: BOM + Comms
sop: docs/UAT-SOP-Customer-Portal.md#81
happy_path:
  - BCOM-01
  - BCOM-03
  - BCOM-11
  - BCOM-15
  - BCOM-17
  - BCOM-21
  - BCOM-27
  - BCOM-28-mock
skip:
  - BCOM-29
  - BCOM-30
---

# Pack — BOM + Comms (MRP-M-142 / 143 / 144)

Projected from live UAT-SOP section 81. Do not use the 2026-08-13 prompt
as the case list. BCOM-16 is a **file upload** (`RECORD_DRAWING` is 400).
BCOM-08 APPROVED reopen `409` is **expected** (version-only path).

Program (do not invent features):

- Assembly BOM: `/mrp/costing/assembly-bom?projectId=`
- Sourcing: `/mrp/sourcing-requests`
- Comms: `/mrp/project-development/[id]?section=comms` — pin is a
  reference row (no email body in PLX)
- Teams: Overview card with trusted `channelDeepLink` only. No in-portal
  chat. Do not file "chat missing" as a bug.
- Outlook: `apps/outlook-pin-to-project` mock unless NAA is proven live.

## Cases

| ID | Name | Expected |
|---|---|---|
| BCOM-01 | Open editor from PD | Lands on assembly-bom with project context |
| BCOM-02 | Template create | DRAFT v1 with layers seeded |
| BCOM-03 | Add component | Persists after refresh |
| BCOM-04 | Needs sourcing | Flag saved; request action available |
| BCOM-05 | Save draft | Status stays DRAFT |
| BCOM-06 | Request review | Status IN_REVIEW |
| BCOM-07 | Approve | Status APPROVED |
| BCOM-08 | New version from APPROVED | Prior OBSOLETE; new DRAFT. POST reopen on APPROVED is 409 |
| BCOM-09 | New version | Version increments |
| BCOM-10 | Pack-Out history on DRAFT | Updates; blocked if active sourcing on replaced lines |
| BCOM-11 | Create sourcing request | OPEN on /mrp/sourcing-requests |
| BCOM-12 | Save brief | BRIEF_READY |
| BCOM-13 | Mark brief sent | BRIEF_SENT |
| BCOM-14 | Vendor response | VENDOR_RESPONDED |
| BCOM-15 | Link without drawing | Blocked |
| BCOM-16 | Upload drawing | File to SharePoint; no URL paste; RECORD_DRAWING is 400 |
| BCOM-17 | Link with sample RECEIVED only | Blocked until ACCEPTED |
| BCOM-18 | Accept sample + link gold Product | LINKED; productId set; needsSourcing cleared |
| BCOM-19 | Vendor package >=2 same supplier | One email; lines BRIEF_SENT; independently completable. Internal recipient only |
| BCOM-20 | Condensed path if configured | Gates still hold |
| BCOM-21 | Comms timeline default | Timeline selected; chronological |
| BCOM-22 | Manual note | Appears in timeline |
| BCOM-23 | Pin / unpin | Toggles; undo on unpin |
| BCOM-24 | Pinned reference row | Subject, party, Outlook + SharePoint links; no body |
| BCOM-25 | Party filter | CUSTOMER vs VENDOR vs both |
| BCOM-26 | Teams card linked | Trusted teams host only; new tab |
| BCOM-27 | Teams card unconfigured | Channel not linked; link to Comms; no error toast |
| BCOM-28-mock | Outlook add-in mock | Entry, loading, success, error, already-pinned at task-pane width |
| BCOM-29 | Mint gold SKU | SKIP until MRP-M-148 ships |
| BCOM-30 | Mint blocked without gates | SKIP until MRP-M-148 ships |

## Dimensions

### Use-cases

| ID | Check |
|---|---|
| UC-01 | Happy path BCOM-01, 03, 11, 15, 17, 21, 27, 28-mock |
| UC-02 | Refresh after every persist (no client-only lie) |

### Edge-cases

| ID | Check |
|---|---|
| EX-01 | Double-click SAVE DRAFT / REQUEST REVIEW — idempotent |
| EX-02 | Empty / negative qty / missing uom — validation, no 500 |
| EX-03 | Pack-Out apply on APPROVED — blocked |
| EX-04 | Pack-Out apply with active sourcing on replaced lines — blocked with message |
| EX-05 | Hard refresh mid-IN_REVIEW — still IN_REVIEW |
| EX-06 | Bogus projectId deep-link — graceful, no Application error |
| EX-07 | CUSTOMER or unauthenticated cannot open editor (403/redirect) |
| EX-08 | http drawing URL — rejected (upload path; RECORD_DRAWING 400) |
| EX-09 | Huge or empty upload — explicit error, no 500 |
| EX-10 | Re-link after LINKED — gate or explicit refuse |
| EX-11 | Cancelled request cannot be linked |
| EX-12 | Package mixed suppliers — refused |
| EX-13 | Package with fewer than 2 lines — refused |
| EX-14 | Double-send same package — no second blast |
| EX-15 | POST pinned-communications with body/html/mime — rejected / ignored |
| EX-16 | Duplicate graphMessageId — idempotent |
| EX-17 | Invalid partyType / missing graphMessageId — 400 |
| EX-18 | Evil Teams link (http or non-Teams host) — not a clickable launch |

### Workflow-loop E2E

| ID | Check |
|---|---|
| WL-01 | DRAFT to IN_REVIEW to APPROVED to new DRAFT version |
| WL-02 | needsSourcing to BRIEF_READY to drawing+accepted sample to LINKED |
| WL-03 | Two BRIEF_READY same supplier to one package send (internal only) |
| WL-04 | Note, pin two, unpin one, refresh — one pin remains |

### Speed

| ID | Budget |
|---|---|
| SP-01 | Assembly BOM editor interactive after open | no budget declared — score BLOCKED unless the pack is later amended with a number |
| SP-02 | Sourcing detail save-brief round trip | no budget declared |

### UI/UX

| ID | Check |
|---|---|
| UX-01 | Empty comms timeline is calm, not a crash |
| UX-02 | Validation messages name the field; no raw 500 page |
| UX-03 | Teams unconfigured card has no error toast |
| UX-04 | No in-portal Teams compose or presence (correct) |
