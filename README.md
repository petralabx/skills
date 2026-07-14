# Petra-Lab-X Skills

Canonical home for shared **Cursor / Claude Agent Skills** used across Petra-Lab-X
projects. This repo is the **source of truth**; skills become active by syncing
them into your local skill directories.

## Skills

- **report-export** — Convert a Markdown/HTML report into a shareable **PDF + Word**
  (`.docx`), with optional OneDrive/SharePoint sharing. No LaTeX (uses headless
  Edge/Chrome for PDF, pandoc for Word).
- **brief-to-quote** — Turn a customer/product brief into a costed PLX **price quote**
  (real raw-material costs from the database, market research for gaps, bulk **$/kg**
  + per-unit model, reformulations) plus an interactive canvas and PDF/Word report.
- **uat-feedback-batch-fix** — Diagnose/fix one UAT Feedback session batch → one staging PR → retest email from `cos@`.
- **uat-weekly-batch-loop** — Weekly orchestrator for UAT session batches (Verified-only done + brain_ingest closeout).
- **staging-dual-db-migrate** — Apply gold/Prisma migrations to **both** staging and UAT DBs.
- **plx-graph-mail** — Graph app-only mail (default From `cos@petrasoap.com`; canonical staging URL only).
- **worktree-open-session** — New portal worktree + bootstrap + Cursor window + PASTE-FIRST/KICKOFF.

See `manifest.json` for the full published catalog (`plx-engineering-core`).


## Activate for Cursor Cloud `/` picker (project-scoped)

Cursor Cloud's `/` menu enumerates skills committed under **`.cursor/skills/`
in the repo the session launches against** — not `~/.cursor/skills`.

To seed the `plx-engineering-core` pack into consumer repos:

```bash
bash scripts/distribute-to-repos.sh          # push branches
bash scripts/distribute-to-repos.sh --dry-run
```

Then open/merge PRs (or use `gh pr create`). Canonical source stays this repo;
consumers hold a committed snapshot.

Skip `agentic-swarm` (already carries a richer local skill set) and this repo.

## Activate (sync into your machine)

Local Cursor/Claude sessions also discover skills from `~/.cursor/skills/` and `~/.claude/skills/`. Cloud `/` picker still needs project `.cursor/skills/` (see above).
Clone this repo once, then run the sync (idempotent — re-run any time to update):

Windows (PowerShell):

    git clone https://github.com/Petra-Lab-X/skills.git $HOME/petra-lab-x-skills
    & $HOME/petra-lab-x-skills/scripts/sync-skills.ps1

macOS / Linux:

    git clone https://github.com/Petra-Lab-X/skills.git ~/petra-lab-x-skills
    bash ~/petra-lab-x-skills/scripts/sync-skills.sh

The sync `git pull`s the latest and copies each `skills/<name>` into both
`~/.cursor/skills/<name>` and `~/.claude/skills/<name>`.

## Contributing

Add or edit a skill under `skills/<name>/SKILL.md` (+ optional `reference.md`,
`scripts/`, `assets/`), open a PR, and re-run the sync after merge. Keep
**app-specific** skills in their app repo; this repo is for **cross-project** skills.


