# Pack schema

A pack is a markdown file under `packs/<id>.md` with YAML frontmatter.

```yaml
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
```

Required frontmatter: `id`, `sop` (or `module_readme`), `happy_path` (non-empty).

Required body sections (each must list at least one row id):

- `## Cases` — SOP / module test IDs
- `## Dimensions` with `### Use-cases`, `### Edge-cases`, `### Workflow-loop E2E`, `### Speed`, `### UI/UX`

Speed rows must declare a budget or state `BLOCKED` reason `no budget declared`.
Do not invent numeric budgets.

If the live SOP disagrees with a pack case, report a pack defect and follow
the SOP. Do not FAIL the product for pack drift.
