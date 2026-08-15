---
name: skillparity
description: >-
  Detects the current agent runtime and machine, picks the matching PLX skills install plane (company bootstrap, operator laptop sync, or Cursor Cloud lock), and executes it. Use when the user says skillparity, skill parity, sync skills, bootstrap company skills, or wants Cursor, Claude, Cloud, Hermes, or Grok on the same catalog.
disable-model-invocation: true
---

# skillparity

Bring this runtime onto the same `petralabx/skills` catalog as the other PLX agent surfaces. Detect, choose one plane, execute. Do not ask first.

## Planes

| Plane | When | Command |
|---|---|---|
| `cloud-lock` | Cursor Cloud (`/agent/repos` or `CLOUD_AGENT_*`) | `agentic-swarm/scripts/install-cloud-agent-skills.sh` |
| `operator-sync` | Operator workstation (Vince laptop, Hermes, Grok, or `agentic-swarm` present) | Copy `skills/*` to `~/.cursor`, `~/.claude`, `~/.grok`, `~/.agents`, `~/.hermes` |
| `company-bootstrap` | Contributor laptop (Cursor or Claude, no operator signals) | `PLX_MC/scripts/bootstrap-company-skills.ps1` or `.sh` |

Company bootstrap follows the **PLX_MC pin** (`config/skills-catalog.json`). Operator sync follows the **skills checkout** used as source. Cloud lock follows `config/cloud-agent-skills-lock.json` (petralabx/skills wins collisions).

## Do this

1. Run the bundled script from this skill directory (foreground, absolute cwd):

```bash
python skills/skillparity/scripts/run.py
```

On Windows, `py -3` is fine. `--detect-only` prints the plan and stops.

2. Read the JSON summary. If `blockers` is non-empty, stop and report them. Do not invent a fourth install path.
3. If the script already applied the plane, report the canary lines (`skillparity`, `grill-with-docs`) and tell the user to **start a new agent session**. Skills load at session start only.
4. Never switch, stash, reset, or delete another worktree. Never run `scripts/distribute-to-repos.sh` unless the user explicitly asks (that opens consumer-repo PRs).
5. MCP `mc_install_skills` / `mc_sync_skills` are helpers for the pinned catalog. They do not replace this script, and they will not serve skills newer than the PLX_MC `pinTag`.

## Decision rules (script source of truth)

The script encodes these rules. Do not override them unless a blocker says the chosen plane is impossible and a fallback is listed.

1. Cloud VM → `cloud-lock`.
2. Else operator workstation → `operator-sync`.
3. Else → `company-bootstrap`.

Operator signals: home user `vince`, `~/agentic-swarm`, `~/.hermes`, or `~/.grok`.

## Source checkout rules

- Prefer the `petralabx/skills` tree that contains this skill. That tree must be a git worktree whose `origin` is `petralabx/skills`.
- An installed copy under `~/.cursor/skills` (or the other home skill dirs) is not a checkout. An empty origin slug is not a source. Fall through to the candidate paths. Prefer a candidate that still contains `skillparity`, then one on `main`.
- If the containing tree is a dirty or non-`main` clone, do **not** `git pull` or switch it. Sync from it if it is a valid source, or from a dedicated `skills-parity-sync` worktree created off `origin/main`.
- `~/plx-cursor-skills` is only valid when `origin` is `petralabx/skills`. The historical `taylorvalton/plx-cursor-skills` remote is not a source.
- Refuse to apply when `source/skills` is a home skill dest. That copy would delete the dest while reading it.

## After

Print:

- runtime, machine, plane, reason
- source repo path + HEAD
- PLX_MC pin if readable
- which home skill dirs were written
- whether `skillparity` and `grill-with-docs` exist in each dest
- "Start a new session to load the skills."
