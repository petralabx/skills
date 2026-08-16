# Company UX viewport gate

Canonical for every `deployed-pr-e2e` pack. A PR declares a surface
change. The skill reads that stamp and incorporates the viewport pass.
The skill does not infer a surface change from SOP prose.

Adopted 2026-08-16.

## Viewports (do not invent a fourth)

| Name | Size | Source |
|---|---|---|
| desktop | 1440 x 900 | `plx-portal-agent-access` ui-gate |
| tablet | 834 x 1112 | ui-gate (not design-system 768) |
| mobile | 390 x 844 | ui-gate |

## Classes

| Class | Gate | Status |
|---|---|---|
| Viewport-desktop | Primary task completable. No clipped primary action. | Adopted |
| Viewport-tablet | Same. No hover-only primary action. | Adopted |
| Viewport-mobile | Same. Rail collapsed. Task completable with a thumb. | Adopted for customer / COS. Staff MRP only when the PR or pack requires it. |
| Touch | Fail under 24 px (WCAG 2.2 AA). 44 px is a candidate goal. | Mixed |
| A11y | axe serious/critical FAIL. Brand contrast uses the ui-gate baseline. | Adopted in ui-gate |
| Error chrome | Inline error. No raw 500. | Already UX-04 |

## When the three-width pass runs

Run desktop + tablet + mobile **once per declared surface**, not on
every SOP case.

Triggers (any one is enough):

1. The named PR stamp is `Surface-change: yes`
2. The PR has label `surface-change`
3. A pack case is tagged spatial (seal, sheet, Confirm, Close, swipe)
4. This run has not yet proved a pack `viewport_surfaces` entry that
   the stamp or pack marked required

Skip three widths on API, citation, and Stream/Fetch clock rows.

## PR stamp (produce)

Every portal PR that changes chrome, layout, CSS, or a shared
component must include this block. Paste it after `## Test plan`.
Do not invent a `dsp_` prefix here.

```text
## Surface change
- Surface-change: yes
- Surfaces: /mrp/project-development, /admin/knowledge
- Viewports: desktop, tablet, mobile
```

If the PR does not change a surface:

```text
## Surface change
- Surface-change: no
```

`Surfaces` is a comma list of routes. Empty `Surfaces` on `yes` means
use the pack `viewport_surfaces` list. `Viewports` defaults to all
three. Optional GitHub label: `surface-change`.

Missing stamp on a **named** PR is a STOP. Do not guess `yes`. Ask
the operator to add the block, then re-parse.

## Skill read (consume)

```bash
node scripts/parse-surface-change.mjs --pr 676
node scripts/parse-surface-change.mjs --body-file pr-body.md
```

Write the JSON into RESULTS as `surfaceChange`. If `declared` is
true, the run must include these UI/UX rows (one per required
viewport, covering every listed surface):

| ID | Viewport |
|---|---|
| UX-VP-desktop | 1440 x 900 |
| UX-VP-tablet | 834 x 1112 |
| UX-VP-mobile | 390 x 844 |

PASS needs a screenshot per surface at that width. A fast API clock
does not PASS a clipped button.

## Pack frontmatter

```yaml
viewport_surfaces:
  - route: /mrp/project-development
    viewports: [desktop, tablet, mobile]
spatial_cases:
  - CTX-NAV-04
  - KH-11
```
