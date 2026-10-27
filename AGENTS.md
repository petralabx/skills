# AGENTS.md — petralabx/skills

Canonical home for shared Cursor / Claude Agent Skills (`skills/<name>/SKILL.md`),
published through `manifest.json`. This repo has **no application server** — it is a
catalog plus validation/sync tooling. Cross-repo governance is in PLX Mission Control;
repo-specific workflow is in `CONTRIBUTING.md` and `docs/GOVERNANCE.md`.

## Mission Control handshake (Claude Code and every agent)

Before first edit or any PR_CREATE on `petralabx/skills`:

1. **Search** projects, buckets and TASK-* first (`mc_search_tasks` / `mc_suggest_work`: branch, title, runId). Reuse a matching open TASK.
2. **Create only on a real miss**: `mc_create_task` in the registry default bucket (`BKT-INFRA`, from PLX_MC `config/tracked-repos-registry.json`; do not hardcode another prod bucket). Create a project/bucket only if it is truly missing. Never create a TASK to escape incomplete evidence on a live checkout.
3. **Checkout**: `mc_checkout_task { taskId, repo: "petralabx/skills" }` on PLX-MC-Hub. Confirm `taskId` matches and `actor.repo` is `petralabx/skills`. Copy `prBodyLine` exactly. HTTP fallback when Hub MCP tools are missing:
   `COMPLIANCE_CAPTURE=1 MC_REPO=petralabx/skills MC_TASK_ID=TASK-N node scripts/compliance-checkout.mjs` (reads `MC_BASE_URL`, `MC_MCP_API_KEY`, `MC_OPERATOR_EMAIL`, `MC_ACCOUNTABLE` from the environment; never echo the key).
4. **Stamp at PR open**: put the `MC-Checkout: dsp_…` line in the body at `gh pr create` time. A body edit does not start the compliance gate, but every run reads the live body (PLX_MC#438). Never invent a `dsp_*`, never write `MC-Checkout: pending`, never `--no-verify`, never an empty commit or push, and never a close and reopen, to re-trigger CI. If the body must change after open, edit it and re-run the failed `compliance` job.
5. **Last commit → `mc_complete_task`** (summary + verificationCommands + rollback) **→ freeze**. Anyone with write access then lands the green PR with a merge commit; never squash, never bypass. A PR that touches money, migrations or workflows lands only with a signed MC merge approval of its exact head (Vince, 2026-10-25, TASK-3901). Next slice = new branch from the integration branch.
6. If Hub MCP and the HTTP fallback both fail: stop; CoS/CIP paste `prBodyLine`.

## Workstream protocol

Sessions are disposable. What the next session or a teammate needs lives in
[`docs/workstreams/`](docs/workstreams/README.md) and travels with the code (Vince, 2026-10-26, TASK-3953).

- One workstream per branch and worktree. Flag any edit outside your workstream's scope before you make it. A one-PR change needs no workstream.
- At session start, read your workstream's note, `docs/workstreams/<slug>.md`. The index in `docs/workstreams/README.md` maps branches to slugs.
- Before you end a session, and after any significant decision, update that note in the same branch (`/handoff` in Claude Code and Cursor; `/resume-workstream` picks it up).
- Change the index row (owner, branch, status, dependencies) only when a workstream opens, closes or changes status.
- SharePoint `Agent Handoffs/` stays the system of record for durable handoffs. The note is the agents' working copy; when they disagree, SharePoint wins.

## Cursor Cloud specific instructions

> For future Cloud Agents. The startup update script installs the Python validator
> dependencies (`jsonschema`, `pyyaml`); everything below is durable run/gotcha context.

### What "running" this repo means

There is no web app or long-running service. The two core, testable flows are:

- **Validate** (the CI gate): `python3 scripts/validate-manifest.py` — validates
  `manifest.json` against `schemas/manifest.schema.json` and the `skills/` tree, and
  enforces that each skill's description is byte-identical between its `SKILL.md`
  frontmatter and `manifest.json`. Exit 0 = pass. This mirrors the `CI` workflow
  (`.github/workflows/validate-manifest.yml`).
- **Sync/activate**: `bash scripts/sync-skills.sh` — copies every `skills/<name>` into
  `~/.cursor/skills/<name>` and `~/.claude/skills/<name>` (idempotent). It first runs
  `git pull --ff-only` and prints `git pull skipped` if that fails (offline/detached),
  which is expected and non-fatal.

### Gotchas

- Only `python3` exists on the VM (there is no bare `python`). Invoke scripts with
  `python3`. (CI uses `python` on `setup-python`; locally use `python3`.)
- `validate-manifest.py` runs release-hygiene checks that diff the working tree against
  `origin/main`. On a shallow/partial checkout with no `origin/main` it prints
  `note: no origin/main ref — skipping release hygiene checks` and continues — the
  schema/frontmatter validation still runs.
- Editing any `skills/**` file or the catalog **requires bumping `manifest.version`**
  in `manifest.json`, and a version already tagged `v<version>` cannot be reused — the
  validator fails otherwise (consumers pin by version).
- Keep a skill's `description` identical in `SKILL.md` frontmatter and `manifest.json`;
  never copy a YAML block-scalar marker (`>-`, `|`) into the JSON. The validator blocks
  both drift and bare-marker descriptions.
- `scripts/distribute-to-repos.sh` pushes branches to consumer repos — do not run it as
  part of routine setup/testing (`--dry-run` is safe to inspect).
