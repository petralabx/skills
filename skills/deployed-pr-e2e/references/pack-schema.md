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
viewport_surfaces:
  - route: /mrp/costing/assembly-bom
    viewports: [desktop, tablet, mobile]
spatial_cases:
  - BCOM-01
---
```

Required frontmatter: `id`, `sop` (or `module_readme`), `happy_path` (non-empty).
Optional: `viewport_surfaces`, `spatial_cases`, `api_paths`.
See [UX-VIEWPORT.md](UX-VIEWPORT.md), [API-CONTRACT.md](API-CONTRACT.md),
[SECURITY.md](SECURITY.md), [MATURITY.md](MATURITY.md).

Required body sections (each must list at least one row id):

- `## Cases` — SOP / module test IDs
- `## Dimensions` with `### Use-cases`, `### Edge-cases`, `### Workflow-loop E2E`, `### Speed`, `### UI/UX`

Speed rows name a class from [SPEED-BUDGET.md](SPEED-BUDGET.md).
They do not invent a number. Chrome is a candidate: score BLOCKED
with reason `chrome budget is candidate`. `no budget declared` is
valid only when no class fits — stop and ask.

Viewport rows follow [UX-VIEWPORT.md](UX-VIEWPORT.md). A named PR
must stamp `Surface-change: yes|no`. The skill reads that stamp. It
does not infer a surface change from SOP prose.

API rows follow [API-CONTRACT.md](API-CONTRACT.md). Security rows
follow [SECURITY.md](SECURITY.md). Stamps: `Api-change:` and
`Security-change:`. Absent Api/Security stamps mean `no` (compat
with PRs that only have Surface-change). Do not invent latency
numbers. Do not write exploits.

If the live SOP disagrees with a pack case, report a pack defect and follow
the SOP. Do not FAIL the product for pack drift.
