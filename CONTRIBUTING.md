# Contributing to petralabx/skills

Version: 1.0  
Effective: 2026-07-06  
Owner: PLX Repo Maintainers

> **Governance is centralized in PLX Mission Control.** This file covers
> **repo-specific** workflow only. Cross-repo rules are mandatory:
>
> | Topic | Canonical source |
> |-------|------------------|
> | Agent pillars, PR discipline, evidence | [`taylorvalton/PLX_MC/config/governance-contract.yaml`](https://github.com/taylorvalton/PLX_MC/blob/main/config/governance-contract.yaml) |
> | Compliance gate, `MC-Checkout`, risk tiers | [`taylorvalton/PLX_MC/docs/COLLABORATOR-SOP.md`](https://github.com/taylorvalton/PLX_MC/blob/main/docs/COLLABORATOR-SOP.md) |
> | Onboarding checklist | [`taylorvalton/PLX_MC/docs/runbooks/REPO-ONBOARDING.md`](https://github.com/taylorvalton/PLX_MC/blob/main/docs/runbooks/REPO-ONBOARDING.md) |
>
> See also: `docs/GOVERNANCE.md` in this repo.

---

## 1. Integration branch

| Branch | Role |
|--------|------|
| **`main`** | All feature work merges here via PR |


**Rules**

1. **Never push directly to the integration branch.** Open a PR.
2. Every PR runs the **PLX MC Compliance Gate** (`.github/workflows/plx-mc-compliance.yml`).
3. Agent-driven PRs must include `MC-Checkout: dsp_…` in the body (see COLLABORATOR-SOP).
4. Non-docs PRs need a `## Rollback Plan` section.

---

## 2. Branch naming

| Pattern | Use for |
|---------|---------|
| `feat/<area>-<slug>` | New capability |
| `fix/<area>-<slug>` | Bug fix |
| `chore/<area>-<slug>` | Tooling, deps |
| `docs/<area>-<slug>` | Documentation |
| `ci/<area>-<slug>` | GitHub Actions |

---

## 3. Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) with scope. Include
Mission Control milestone IDs when applicable (`MRP-M-*`, `ERP-M-*`, etc.).

---

## 4. PR template

```markdown
## Summary
(what and why)

## Mission Control
- Milestone: … / n/a
- MC-Checkout: dsp_…   ← required for agent/task work

## Test plan
- [ ] (repo validation commands)

## Rollback Plan
(how to revert)
```

---

## 5. Validation before merge

Run this before every PR that touches `manifest.json` or any `skills/*/SKILL.md`:

```bash
python -m pip install jsonschema pyyaml   # once
python scripts/validate-manifest.py
```

It validates `manifest.json` against `schemas/manifest.schema.json` and checks it
against the `skills/` tree: frontmatter parses as YAML, ids match directories,
no skill directory is missing from the catalog, and **every description is
byte-identical between `SKILL.md` frontmatter and `manifest.json`**.

It also enforces two release rules: **changing the catalog or any skill requires
bumping `manifest.version`**, and **a version that already has a `v<version>` tag
cannot be reused**. Consumers pin by version, so an unbumped change is invisible
to them, and moving a released tag would silently change what everyone pinned to
it receives.

For project-scoped Cursor copies, prove the parity checker itself and then compare
the live consumer branches:

```bash
python scripts/check-consumer-parity.py --selftest
scripts/distribute-to-repos.sh --check --repos plx-customer-portal,PLX_MC
```

The first command must report a known-bad `RED exit=1` followed by
`GREEN exit=0`. The second command clones each configured integration branch and
compares every package skill byte-for-byte with its `.cursor/skills/` copy. Run
the distributor without `--check` to create/update consumer branches, then rerun
the live check after those PRs merge.

GitHub checks on every PR: **Validate manifest and skill frontmatter** (`CI`),
**compliance**, **drift**, and the routing metadata suggestion job.

### Releases are tagged, not stamped

On merge to `main`, the **Release tag** workflow tags the commit `v<version>`
from `manifest.json`. Do not add a `gitRef` field to the manifest — the schema
rejects it. A file cannot name the commit that contains it, because the sha does
not exist until the commit is made, so such a stamp is stale by construction and
every version bump ships one that lags. At one point the stamp named a 39-skill
commit while the release served 69. Consumers resolve provenance from the ref
they fetched; the tag is the human-readable release marker.

### Why descriptions must match exactly

A skill's description lives in two places, read by different consumers:

| Location | Read by |
|----------|---------|
| `SKILL.md` frontmatter | the Cursor / Claude agent picker |
| `manifest.json` entry | the PLX MC skills directory (`mc_list_skills`) |

If they diverge, the same skill advertises different trigger conditions depending
on which surface an agent sees, so it gets applied inconsistently. Treat the
frontmatter as the source and copy the **folded** text into `manifest.json`.

Never copy a YAML block-scalar marker (`>-`, `|`) into the JSON. Seven
descriptions were once reduced to the literal two-character string `">-"` this
way, and one skill lost 797 characters of guidance. When a description contains
`": "`, quote it or use a `>-` block — an unquoted `": "` makes YAML read the
value as a nested mapping and the frontmatter fails to parse, which empties the
description in the picker.


---

## 6. Repo-specific notes

Skill ids must match `manifest.json`. No secrets in `skills/`. Catalog: PLX_MC `config/skills-catalog.json`.

---

## 7. Operator setup

Repo secrets: `PLX_MC_BASE_URL`, `COMPLIANCE_CI_TOKEN`.  
Repo variable: `COMPLIANCE_MODE` (`soft` → `hard` when ready).  
Enable branch protection on `main` — require PR + checks.

### Routing metadata (suggestion)

`.github/workflows/mc-routing-metadata.yml` submits pull-request metadata to MC `/api/routing/propose` via OIDC when org/repo variable `PLX_MC_ROUTING_METADATA_ENABLED=1`. It does not check out or execute PR code. Contract: `.github/plx-mc-routing-manifest.json`. Mode is suggestion (safe deep link in the Actions job summary; no candidate dump). Confirmation and fuzzy auto-link stay off. Rollback: set `PLX_MC_ROUTING_METADATA_ENABLED=0` (repo override); compliance gate remains enforced.

### Welcome to Mission Control

Colleague get-started: https://mc.plxcustomer.io/welcome  
Guide: https://github.com/petralabx/PLX_MC/blob/main/docs/runbooks/mc-for-colleagues.md

On PRs in this repo, the MC routing job may show an **Open Mission Control** suggestion link in the Actions summary. Confirmation and fuzzy auto-link remain off.
