# AGENTS.md — petralabx/skills

Canonical home for shared Cursor / Claude Agent Skills (`skills/<name>/SKILL.md`),
published through `manifest.json`. This repo has **no application server** — it is a
catalog plus validation/sync tooling. Cross-repo governance is in PLX Mission Control;
repo-specific workflow is in `CONTRIBUTING.md` and `docs/GOVERNANCE.md`.

## Mission Control handshake (Claude Code and every agent)

<!-- plx-mc:handshake:start -->
Generated from PLX_MC [`config/governance-contract.yaml`](https://github.com/petralabx/PLX_MC/blob/main/config/governance-contract.yaml) by `scripts/generate-governance-surfaces.py --fleet`. Do not edit this block: change the contract and regenerate.

Before the first edit or any PR on `petralabx/skills`:

1. Search projects, buckets and TASK-* first (mc_search_tasks: branch, title, runId). Create a task only on a real miss, with mc_create_task in BKT-INFRA. Never create a task to escape incomplete evidence on a live checkout.
2. Check out with mc_checkout_task, passing repo `petralabx/skills`, your own `runtime/lane` as agent, and your branch. Confirm the returned taskId and that actor.repo is `petralabx/skills`. Copy prBodyLine exactly.
3. Never invent a dsp_* id, never write `MC-Checkout: pending`, and never push with --no-verify. Without the MC tools, check out over HTTP: `COMPLIANCE_CAPTURE=1 MC_REPO=petralabx/skills MC_TASK_ID=TASK-N node scripts/compliance-checkout.mjs`. If that fails too, stop and ask CoS or CIP to paste the prBodyLine.
4. End every commit with Agent, On-Behalf-Of and MC-Checkout as its last three lines. Name the TASK id in the PR title or branch.
5. Save evidence with mc_save_evidence before you open the PR, and put the MC-Checkout line in the PR body when you open it.
6. After you fix a PR body, re-run the failed compliance job. Never push an empty commit, and never close and reopen a PR, to restart a check.
7. After the last commit, call mc_complete_task with verificationCommands, rollback and the PR link. Then move the task's stage, or say why you cannot.
8. Mark a green PR ready and stop: only CIP's merge-queue session arms auto-merge or merges, with a merge commit into `main`. A PR that touches money, migrations or workflows, or reverts merged work, needs a signed MC merge approval of its exact head (mc_request_approval, merge scope).

- A plan that adds a project, or two or more buckets, goes through a draft: mc_save_draft, then mc_submit_draft. Its author accepts it in Mission Control.
<!-- plx-mc:handshake:end -->

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
