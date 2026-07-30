# AGENTS.md — petralabx/skills

Canonical home for shared Cursor / Claude Agent Skills (`skills/<name>/SKILL.md`),
published through `manifest.json`. This repo has **no application server** — it is a
catalog plus validation/sync tooling. Cross-repo governance is in PLX Mission Control;
repo-specific workflow is in `CONTRIBUTING.md` and `docs/GOVERNANCE.md`.

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
